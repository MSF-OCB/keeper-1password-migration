'''

Does a one-shot migration from Keeper Enterprise into 1Password

Does not do TOTP, credit cards, or any shared folders (yet)

Environment variables & defaults

KEEPER_SERVER       https://keepersecurity.eu/api/v2/
OP_SERVER           my.1password.com
OP_EXE              D:\\1password\\op.exe
TMPDIR or TMP

'''

from secure_delete import secure_delete
from keepercommander import api
from keepercommander.commands.folder import FolderListCommand 
from keepercommander.commands.record import RecordDownloadAttachmentCommand 
from keepercommander.params import KeeperParams
from keepercommander.subfolder import UserFolderNode
from subprocess import run, Popen, PIPE

import getpass, json, os, re, subprocess

KEEPER_SERVER = os.getenv("KEEPER_API_URL", default="https://keepersecurity.eu/api/v2/")
OP_SERVER = os.getenv("ONEPASS_SERVER", default="msfocb.1password.eu")
TMPDIR = os.getenv("TMP", os.getenv("TMPDIR"))
OP_EXE = os.getenv("OP_EXE", default="D:\\1password\\op.exe")

MIGRATE_SHARED = True

kp_params = KeeperParams()

credentials = {}

def process_folder_record(op_user, our_parents, record_uid) :

    r = api.get_record(kp_params, record_uid)

    if(r.totp != None) : 
        print("******************************* HASTOTP, not done yet")
        print(str(r.totp))

    if not r.record_uid in credentials :
        oneP = {
            "fields": [
                {
                    "designation": "username",
                    "name": "username",
                    "type": "T",
                    "value": r.login
                },
                {
                    "designation": "password",
                    "name": "password",
                    "type": "P",
                    "value": r.password
                },
            ],
            "sections": []
        }

        if(r.notes): oneP["notesPlain"] = r.notes
        
        name = 1;

        if(r.custom_fields):
            oneP["sections"].append(
                {
                    "title": "Custom fields",
                    "fields": []
                }
            )

            for custom_field in r.custom_fields:
                oneP["sections"][0]["fields"].append({
                    "k": "string",
                    "n": str(name),
                    "t": custom_field["name"],
                    "v": custom_field["value"]
                })
                
                name += 1
   
        # ! important ! non-breaking spaces mess things up!
        credentials[r.record_uid] = {"json": oneP, "title": r.title.replace("\xa0", " "), "url": r.login_url, "tags": []}

    credentials[r.record_uid]["tags"].append("/".join(our_parents ))

    if(r.attachments) :

        dir = os.path.sep.join([TMPDIR, "onepassword-migration-downloads", op_user, r.record_uid])

        if not os.path.exists(dir): 
            os.makedirs(dir)

        os.chdir(dir)

        dl = RecordDownloadAttachmentCommand()

        kwargs = {'record': r.record_uid}

        dl.execute(kp_params, **kwargs)

        credentials[r.record_uid]["docs"] = dir


def process_folder_records(op_user, our_parents, folder_uid) :

    if not folder_uid in kp_params.subfolder_record_cache:
        return

    for record_uid in kp_params.subfolder_record_cache[folder_uid]:
        process_folder_record(op_user, our_parents, record_uid)

def process_folder(op_user, folder_uid, parents=[]) :

    folder = kp_params.folder_cache[folder_uid];

    if(folder.type != "user_folder" and not MIGRATE_SHARED) :
        return
    
    our_parents = parents.copy()

    our_parents.append(folder.name)

    print("Processing "+folder.name)
    
    process_folder_records(op_user, our_parents, folder_uid)
    
    for subfolder in folder.subfolders: 
      process_folder(op_user, subfolder, our_parents )

def exec_op(args, input_stdin=None, proc_timeout=15) :
    proc = Popen(args, 
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True)
    
    if(input_stdin) : input_stdin += "\n"
    
    try:
        outs, errs = proc.communicate(input=input_stdin, timeout=proc_timeout)
    except TimeoutExpired:
        raise Exception("Timeout on "+str(args)+", in="+input_stdin+", timeout="+timeout)

    if(errs != ""):
        raise Exception("Error on executing "+str(args)+": "+errs)
    
    return outs.strip()


def get_keeper_folders():    
    
    print('Keeper -> 1Password migration (command line 1-account POC)')

    kp_params.login_v3 = False
    kp_params.user = input("Keeper user: ")
    kp_params.password = getpass.getpass("Keeper password: ")
    kp_params.server = KEEPER_SERVER
    kp_params.debug = True
    
    op_user = input("1Password user: ")
    op_key = getpass.getpass("1Password secret key: ")
    op_pwd = getpass.getpass("1Password password: ")

    print("Retrieving keeper logins...")

    api.sync_down(kp_params)
   
    for uid, folder in kp_params.folder_cache.items() :
        if(folder.parent_uid == None):
            process_folder(op_user, uid)
    
    print(str(len(credentials)) +" Passwords to migrate.")

    print("Logging into 1Password...")

    token = exec_op([OP_EXE, "signin", OP_SERVER, op_user, op_key, "--raw", "--shorthand=cmdlinetool"], op_pwd)

    current_items = json.loads(exec_op([OP_EXE, "list", "items", "Login", "--session", token]))
    
    def matches(login, pword) :
        return login["overview"]["title"] == pword["title"] \
          and pword["tags"][0] in login["overview"]["tags"] \
          and (("url" in login["overview"] and pword["url"] == login["overview"]["url"]) or \
                ("url" not in login["overview"] and pword["url"]==""))

    for uid, pword in credentials.items():
        
        if next((login for login in current_items if matches(login, pword)), None):
            print("Already imported: "+pword["title"])
            continue

        print("Exporting \""+pword["title"]+"\"...")
        
        to_encode = pword["json"]
        
        if("docs" in pword):
            
            os.chdir(pword["docs"])

            attachments = {
                "fields": [],
                "name": "linked items",
                "title": "Related Items"
            }

            to_encode["sections"].append(attachments)
            
            name=99999
            
            for file_name in os.listdir(pword["docs"]) :
            
                upload_args = [OP_EXE, "create", "document", file_name, "--session", token]
                
                if(pword["tags"]): upload_args.extend(["--tags", ",".join(pword["tags"])]);            
                
                uploaded_file = exec_op(upload_args)
                
                attachments["fields"].append(
                    {
                        "k": "reference",
                        "t": file_name,
                        "n": str(name),
                        "v": json.loads(uploaded_file)["uuid"]
                    }
                )
                
                name += 1

        encoded_entry = exec_op([OP_EXE, "encode", "--session", token], json.dumps(to_encode))
        
        create_args = [OP_EXE, "create", "item", "Login", encoded_entry, "--session", token, "--title", pword["title"]];
        
        if(pword["url"]): create_args.extend(["--url", pword["url"]]);
        if(pword["tags"]): create_args.extend(["--tags", ",".join(pword["tags"])]);
        
        try:
            result = exec_op(create_args)
        except Exception as failure: 
            print("Cant save "+json.dumps(to_encode)+", err="+str(failure))
           
        
    print('Done.')

if __name__ == "__main__":
    get_keeper_folders()


