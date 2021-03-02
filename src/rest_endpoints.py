'''
Created on 17 mars 2020

$python -m pip install --upgrade pip
$pip install flask

$set FLASK_APP=rest_endpoints.py
$flask run
'''

import os, re, time, subprocess
from cryptography.hazmat.primitives import hashes
from base64 import b64decode, b64encode

from flask import Flask, Response, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

#need to stop sprays and dictionary attacks
limiter = Limiter(
    app,
    key_func=get_remote_address
)

#see https://emailregex.com/
EMAIL_REGEX=re.compile("""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")

HASH_REGEX=re.compile("[A-Za-z0-9]{64}");

HASH_NOK_PASSWORD=re.compile("[\x00-\x1F]+");

TMPDIR = os.path.join(os.getenv("TMP", os.getenv("TMPDIR", "/tmp")), "keepermigration", "io")

if not os.path.exists(TMPDIR): os.makedirs(TMPDIR)

SHELL = os.getenv("KEEPER_1P_PASSWORD_SHELL");
PYTHON = os.getenv("KEEPER_1P_PASSWORD_PYTHON");

TEST_MODE = False

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

def get_hash(inputs):

    inputs.extend([time.time(), os.urandom(32)])

    digest = hashes.Hash(hashes.SHA256())

    for input in inputs : digest.update(str(input).encode("UTF-8"))
   
    return digest.finalize().hex().strip()

def is_valid(username, password) :
    
    if not username or not EMAIL_REGEX.match(username.lower()) :
        return False
    
    # only blocking on control characters, the rest will be b64-encoded 
    # before being passed as password env variable anyway, 

    if not password or HASH_NOK_PASSWORD.match(password) :
        return False;
    
    return True

def launch_process(username, password, operation) : 

    output_file = get_hash([username, password, operation])

    env_vars = {
        "KEEPER_1P_PROVISIONING_USER"       : os.getenv("KEEPER_1P_PROVISIONING_USER"),
        "KEEPER_1P_PROVISIONING_PASSWORD"   : os.getenv("KEEPER_1P_PROVISIONING_PASSWORD"),
        "KEEPER_1P_PROVISIONING_SECRETKEY"  : os.getenv("KEEPER_1P_PROVISIONING_SECRETKEY"),
        "KEEPER_1P_OP_EXE"                  : os.getenv("KEEPER_1P_OP_EXE"),
        "KEEPER_1P_OP_CONFIG_DIR"           : os.getenv("KEEPER_1P_OP_CONFIG_DIR"),
        "KEEPER_1P_USERNAME"                : b64encode(username.encode("UTF-8")),
        "KEEPER_1P_PASSWORD"                : b64encode(password.encode("UTF-8")),
        "KEEPER_1P_OPERATION"               : b64encode(operation.encode("UTF-8")),
        "OP_DEVICE"                         : os.getenv("OP_DEVICE")
    }
    
    #print("env_vars="+str(env_vars))
    
    script = "./migrate_account.py"
    
    if TEST_MODE : script = "./fake_migration.py"
    
    subprocess.Popen(args=[SHELL, "-c", "nohup "+PYTHON+" -u "+script+" > "+os.path.join(TMPDIR,output_file)], env=env_vars)
    
    return output_file;

@app.route('/login', methods=['POST'])
@limiter.limit("50 per hour")
def login_health():

    username=request.form.get('username')
    password=request.form.get('password')
    
    if not is_valid(username, password) :
        return Response("", status=400)

    output_file_hash = launch_process(username, password, "login_health")

    return Response(output_file_hash, status=200)

@app.route('/migrate', methods=['POST'])
@limiter.limit("50 per hour")
def migrate_launch():

    username=request.form.get('username')
    password=request.form.get('password')

    if not is_valid(username, password) :
        return Response("", status=400)

    output_file_hash = launch_process(username, password, "migrate_launch")
    
    return Response(output_file_hash, status=200)

@app.route('/finish', methods=['POST'])
@limiter.limit("50 per hour")
def confirm_user():

    username=request.form.get('username')
    password=request.form.get('password')

    if not is_valid(username, password) :
        return Response("", status=400)

    output_file_hash = launch_process(username, password, "confirm_user")
    
    return Response(output_file_hash, status=200)

@app.route('/console/<consolehash>', methods=['GET'])
def get_console_output(consolehash):

    if not HASH_REGEX.match(consolehash) : return Response("", status=400)
    
    file_path = os.path.join(TMPDIR, consolehash)

    if not os.path.exists(file_path): 
        return Response("", status=404)
    
    with open(file_path, "r") as file:
        file_contents = file.read()
    
    return Response(file_contents, 200)
    

