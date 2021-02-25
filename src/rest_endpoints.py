'''
Created on 17 mars 2020

$python -m pip install --upgrade pip
$pip install flask

$set FLASK_APP=rest_endpoints.py
$flask run
'''

import os, re, time
from flask import Flask, Response, request, render_template
from cryptography.hazmat.primitives import hashes
from base64 import b64decode, b64encode

app = Flask(__name__)

EMAIL_REGEX=re.compile("""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")

HASH_REGEX=re.compile("[A-Za-z0-9]{128}");

TMPDIR = os.getenv("TMP", os.getenv("TMPDIR"))

MIGRATION_IO_DIR = os.paths.join(TMPDIR, "keepermigration", "io")

if not os.path.exists(MIGRATION_IO_DIR): MIGRATION_IO_DIR.mkdirs()

SHELL = os.getenv("KEEPER_1P_PASSWORD_SHELL");
PYTHON = os.getenv("KEEPER_1P_PASSWORD_PYTHON");

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

def get_hash(inputs):

   digest = hashes.Hash(hashes.SHA256())
   
   for(input in inputs) : digest.update(input)
   
   return digest.finalize().hex()

def validate(usename, password) :

    if not EMAIL_REGEX.match(email) return False

    #IMPORTANT TODO validate password to avoid injection of all stuff

def launch_process(username, password, operation, output_file) : 

    env_vars = {
        "KEEPER_1P_USERNAME": b64encode(username),
        "KEEPER_1P_PASSWORD": b64encode(password),
        "KEEPER_1P_OP": b64encode(operation)
    }

    subprocess.Popen([SHELL, "-c", "nohup "+PYTHON+" ./migrate_account.py > "+os.paths.join(MIGRATION_IO_DIR,output_file)], env_vars)

@app.route('/login', methods=['POST'])
def login_health():

    username=request.form.get('username')
    password=request.form.get('password')
    
    if not validate(username, password)
        return Response(hash, status=400)

    hash = get_hash([usename, password, time.current_milli_time(), os.getrandom(32), "login_health"])

    file_path = os.paths.join(MIGRATION_IO_DIR, hash)

    #launch "python migrate_accounts.py --option A --option B > "+file_path
    
    return Response(hash, status=200)

@app.route('/migrate', methods=['POST'])
def migrate_launch():

    username=request.form.get('username')
    password=request.form.get('password')

    if not validate(username, password)
        return Response(hash, status=400)

    hash = get_hash([usename, password, time.current_milli_time(), os.getrandom(32), "migrate_launch"])
    
    file_path = os.paths.join(MIGRATION_IO_DIR, hash)
    
    #launch "python migrate_accounts.py --option A --option B > "+file_path

    return Response(hash, status=200)

@app.route('/console/<consolehash>', methods=['GET'])
def get_console_ouptut(consolehash):

    if not HASH_REGEX.match(consolehash) return Response("", status=400)

    file_path = os.paths.join(MIGRATION_IO_DIR, consolehash)
    
    if not os.path.exists(file_path): return Response(hash, status=404)
    
    with open(file_path, "r") as file:
    	file_contents = file.read()
    
    return Response(file_contents, 200)
    

