'''

Does a one-shot migration from Keeper Enterprise into 1Password

Does not do credit cards

Environment variables & defaults

Used in integration with web interface:

KEEPER_1P_OPERATION      
KEEPER_1P_PASSWORD
KEEPER_1P_USERNAME
KEEPER_1P_PROVISIONING_PASSWORD     should be set globally (base64 encoded)
KEEPER_1P_PROVISIONING_SECRETKEY    should be set globally (base64 encoded)
KEEPER_1P_PROVISIONING_USER         should be set globally (base64 encoded)
KEEPER_1P_OP_EXE                    should be set globally


With defaults:

KEEPER_SERVER       https://keepersecurity.eu/api/v2/
OP_SERVER           my.1password.com
KEEPER_1P_OP_EXE    D:\\1password\\op.exe
TMPDIR or TMP       /tmp

'''

from secure_delete import secure_delete
from keepercommander import api
from keepercommander.commands.folder import FolderListCommand 
from keepercommander.commands.record import RecordDownloadAttachmentCommand 
from keepercommander.params import KeeperParams
from keepercommander.subfolder import UserFolderNode
from subprocess import run, Popen, PIPE
from base64 import b64decode, b64encode

import getpass, json, os, re, subprocess

KEEPER_SERVER = os.getenv("KEEPER_API_URL", default="https://keepersecurity.eu/api/v2/")
OP_SERVER = os.getenv("ONEPASS_SERVER", default="msfocb.1password.eu")

TMPDIR = os.path.join(os.getenv("TMP", os.getenv("TMPDIR", "/tmp")), "keepermigration", "downloads")

OP_EXE = os.getenv("KEEPER_1P_OP_EXE", default="D:\\1password\\op.exe")
OP_CONFIG_DIR = os.getenv("KEEPER_1P_OP_CONFIG_DIR")

MIGRATE_SHARED = True

kp_params = KeeperParams()

credentials = {}

def process_folder_record(keeper_user, our_parents, record_uid) :

    r = api.get_record(kp_params, record_uid)

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

        if(r.custom_fields or r.totp):
            oneP["sections"].append(
                {
                    "title": "Custom fields",
                    "fields": []
                }
            )

            if(r.totp) : 
            
                oneP["sections"][0]["fields"].append({
                    "k": "concealed",
                    "n": "TOTP_"+str(name),
                    "t": "one-time password",
                    "v": r.totp
                })
                
                name += 1

            for custom_field in r.custom_fields:
                oneP["sections"][0]["fields"].append({
                    "k": "string",
                    "n": str(name),
                    "t": custom_field["name"],
                    "v": custom_field["value"]
                })
                
                name += 1
   
        # ! important ! non-breaking spaces mess things up!
        credentials[r.record_uid] = {"json": oneP, "title": r.title.replace("\xa0", " ")}
        
        if r.login_url : credentials[r.record_uid]["url"] = r.login_url

        if(r.attachments) :

            dir = os.path.sep.join([TMPDIR, keeper_user, r.record_uid])

            if not os.path.exists(dir): 
                os.makedirs(dir)

            os.chdir(dir)

            dl = RecordDownloadAttachmentCommand()

            kwargs = {'record': r.record_uid}

            dl.execute(kp_params, **kwargs)

            credentials[r.record_uid]["docs"] = dir

    if our_parents : 
        if not "tags" in credentials[r.record_uid] :
            credentials[r.record_uid]["tags"] = []
        credentials[r.record_uid]["tags"].append("/".join(our_parents ))


def process_folder_records(keeper_user, our_parents, folder_uid) :

    if not folder_uid in kp_params.subfolder_record_cache:
        return

    for record_uid in kp_params.subfolder_record_cache[folder_uid]:
        process_folder_record(keeper_user, our_parents, record_uid)

def process_folder(keeper_user, folder_uid, parents=[]) :

    folder = kp_params.folder_cache[folder_uid];

    if(folder.type != "user_folder" and not MIGRATE_SHARED) :
        return
    
    our_parents = parents.copy()

    our_parents.append(folder.name)

    print("Processing "+folder.name)
    
    process_folder_records(keeper_user, our_parents, folder_uid)
    
    for subfolder in folder.subfolders: 
      process_folder(keeper_user, subfolder, our_parents )

def exec_op(args, input_stdin=None, proc_timeout=15) :

    if OP_CONFIG_DIR : args.extend(["--config", OP_CONFIG_DIR])

    proc = Popen(args, 
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True)
    
    if(input_stdin) : input_stdin += "\n"
    
    try:
        outs, errs = proc.communicate(input=input_stdin, timeout=proc_timeout)
    except TimeoutExpired:
        raise Exception("Timeout on "+str(args)+", timeout="+timeout)

    #prints that to stderr and I wish they wouldn't
    if(errs):
        errs = errs.replace("Using configuration at non-standard location \""+OP_CONFIG_DIR+"\"", "").strip()
        if(errs != ""):
            raise Exception("Error on executing "+str(args)+": "+errs)
    
    return outs.strip()

def check_keeper_account_login(keeper_user, keeper_password) :

    try:
    
        print("Trying to log into your account...")
        print("If you see text asking for a 6-digit code, go back to Keeper")
        print("and disable two-factor authentication, then try again")
    
        kp_params.login_v3 = False
        kp_params.user = keeper_user
        kp_params.password = keeper_password
        kp_params.server = KEEPER_SERVER
        kp_params.debug = True

        api.sync_down(kp_params)
        
        print("Great! Ready to go...")
        print("***ALL_CLEAR***")
        
    except:
        print("*************************************")
        print("!! Could not log into your account !!")
        print("*************************************")
        print()
        print("Please make sure that you typed your email address and master password correctly.")
        print()
        print("If this still happens please contact IT support (Dr. Watson) ASAP.")
        print()
        print("***NO_LOGIN***")

def migrate_keeper_1password_cmdline():
    
    print('Keeper -> 1Password migration tool (all shared folders into private vault)')
    
    migrate_keeper_user_to_1password(
        keeper_user       = input("Keeper user: "),
        keeper_password   = getpass.getpass("Keeper password: "),
        op_user           = input("1Password user: "),
        op_key            = getpass.getpass("1Password secret key: "),
        op_pass           = getpass.getpass("1Password password: ")
    )

def migrate_keeper_user_to_1password(keeper_user, keeper_password, op_user, op_pass, op_key, op_user_to_migrate=None) :

    print("Retrieving keeper logins for "+keeper_user+"...")

    kp_params.login_v3 = False
    kp_params.user = keeper_user
    kp_params.password = keeper_password
    kp_params.server = KEEPER_SERVER
    kp_params.debug = True

    api.sync_down(kp_params)
   
    for uid, folder in kp_params.folder_cache.items() :
        if(folder.parent_uid == None):
            process_folder(keeper_user, uid)

    ##these ones are in the root folder only
    for record_uid in (record_uid for record_uid in kp_params.record_cache if record_uid not in credentials) :
        process_folder_record(keeper_user, [], record_uid)
    
    print(str(len(credentials)) +" Passwords to migrate.")

    print("Logging into 1Password (as provisioning user)...")
    
    shorthand = re.sub('[^a-zA-Z0-9]', '', op_user)
    
    token = exec_op(args=[OP_EXE, "signin", OP_SERVER, op_user, op_key, "--raw", "--shorthand="+shorthand], input_stdin=op_pass)

    current_items_args = [OP_EXE, "list", "items", "Login", "--session", token]
    
    vault_uid=None
    
    if op_user != op_user_to_migrate :
    
        try:
            
            exec_op(args=[OP_EXE, "get", "user", op_user_to_migrate, "--session", token])
        
        except:
            
            #user doesn't exist, so create them in 1P
            
            user_name = op_user_to_migrate[0:op_user_to_migrate.index("@")]
             
            exec_op(args=[OP_EXE, "create", "user", op_user_to_migrate, user_name, "--session", token])
        
            print("***USER_CREATED***")
        
        #print("Getting private vault ID for target user("+op_user_to_migrate+")...")
    
        vaults = json.loads(exec_op(args=[OP_EXE, "list", "vaults", "--user="+op_user_to_migrate, "--session", token]))
        
        vault = next((vault for vault in vaults if "Private Vault" in vault["name"]), None)
        
        if vault: vault_uid = vault["uuid"]
        
        #print("Private vault ID = "+str(vault_uid))

    if(vault_uid) : current_items_args.extend(["--vault", vault_uid])
    
    current_items = json.loads(exec_op(args=current_items_args))
    
    def already_imported(login, pword) :
        return login["overview"]["title"] == pword["title"] \
          and ("tags" in pword and "tags" in login["overview"] and pword["tags"][0] in login["overview"]["tags"]) \
          and (
                   ("url" not in login["overview"] and "url" not in pword)
               or  ("url" in login["overview"] and "url" in pword \
                    and pword["url"] == login["overview"]["url"])
              )

    for uid, pword in credentials.items():
        
        if next((login for login in current_items if already_imported(login, pword)), None):
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
                
                if("tags" in pword): upload_args.extend(["--tags", ",".join(pword["tags"])]);

                if(vault_uid): upload_args.extend(["--vault", vault_uid])
                
                uploaded_file = exec_op(args=upload_args)
                
                attachments["fields"].append(
                    {
                        "k": "reference",
                        "t": file_name,
                        "n": str(name),
                        "v": json.loads(uploaded_file)["uuid"]
                    }
                )
                
                name += 1
                
        encoded_entry = exec_op(args=[OP_EXE, "encode", "--session", token], input_stdin=json.dumps(to_encode))
        
        create_args = [OP_EXE, "create", "item", "Login", encoded_entry, "--session", token, "--title", pword["title"]];
        
        if("url" in pword): create_args.extend(["--url", pword["url"]]);
        
        if("tags" in pword): create_args.extend(["--tags", ",".join(pword["tags"])]);
        
        if(vault_uid): create_args.extend(["--vault", vault_uid])
        
        try:
            result = exec_op(args=create_args)
        except Exception as failure: 
            print("*** ERROR: Can't save "+pword["title"]+", err="+str(failure))
           
        
    print("***ACCOUNT_MIGRATED***")

def confirm_1password_user(keeper_user, keeper_password, op_user, op_pass, op_key, op_user_to_migrate) :

    if not op_user_to_migrate : op_user_to_migrate = op_user

    print("Just checking your (Keeper) username and password...")

    kp_params.login_v3 = False
    kp_params.user = keeper_user
    kp_params.password = keeper_password
    kp_params.server = KEEPER_SERVER
    kp_params.debug = True

    api.sync_down(kp_params)

    print("Logging into 1Password (as provisioning user)...")
    
    shorthand = re.sub('[^a-zA-Z0-9]', '', op_user)

    token = exec_op(args=[OP_EXE, "signin", OP_SERVER, op_user, op_key, "--raw", "--shorthand="+shorthand], input_stdin=op_pass)

    print("Finalizing your account...")

    exec_op(args=[OP_EXE, "confirm", op_user_to_migrate, "--session", token])

    print("Finished!")

    print("***DONE***")

def decode_env(var_name) : 
    return b64decode(os.getenv(var_name)).decode("UTF-8")

def main() :

    if( not os.getenv("KEEPER_1P_OPERATION")) : 
        migrate_keeper_1password_cmdline()
        return

    operation = decode_env("KEEPER_1P_OPERATION")

    if(operation == "login_health") :

        check_keeper_account_login(
            keeper_user          = decode_env("KEEPER_1P_USERNAME"),
            keeper_password      = decode_env("KEEPER_1P_PASSWORD")
        )
        
    elif(operation == "migrate_launch") :

        migrate_keeper_user_to_1password(
            keeper_user          = decode_env("KEEPER_1P_USERNAME"),
            keeper_password      = decode_env("KEEPER_1P_PASSWORD"),
            op_user              = decode_env("KEEPER_1P_PROVISIONING_USER"),
            op_key               = decode_env("KEEPER_1P_PROVISIONING_SECRETKEY"),
            op_pass              = decode_env("KEEPER_1P_PROVISIONING_PASSWORD"),
            op_user_to_migrate   = decode_env("KEEPER_1P_USERNAME")           
        )

    elif(operation == "confirm_user") :

        confirm_1password_user(
            keeper_user          = decode_env("KEEPER_1P_USERNAME"),
            keeper_password      = decode_env("KEEPER_1P_PASSWORD"),
            op_user              = decode_env("KEEPER_1P_PROVISIONING_USER"),
            op_key               = decode_env("KEEPER_1P_PROVISIONING_SECRETKEY"),
            op_pass              = decode_env("KEEPER_1P_PROVISIONING_PASSWORD"),
            op_user_to_migrate   = decode_env("KEEPER_1P_USERNAME")
        )


if __name__ == "__main__" :
    main()

