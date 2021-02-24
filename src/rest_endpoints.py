'''
Created on 17 mars 2020

$python -m pip install --upgrade pip
$pip install flask
$pip install keepercommander

$set FLASK_APP=rest_endpoints.py
$flask run
'''

import os, re, time
from flask import Flask, Response, request
from cryptography.hazmat.primitives import hashes

app = Flask(__name__)

EMAIL_REGEX=re.compile("""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")

HASH_REGEX=re.compile("[A-Za-z0-9]{128}");

TMPDIR = os.getenv("TMP", os.getenv("TMPDIR"))

@app.route("/")
def index():
  return "alive"

def get_hash(inputs):

   digest = hashes.Hash(hashes.SHA256())
   
   for(input in inputs) : digest.update(input)
   
   return digest.finalize().hex()

def validate(usename, password) :

    if not EMAIL_REGEX.match(email) return False

    #IMPORTANT TODO validate password to avoid injection of all stuff



@app.route('/login', methods=['POST'])
def login_health():

    username=request.form.get('username')
    password=request.form.get('password')
    
    if not validate(username, password)
        return Response(hash, status=400)

    hash = get_hash([usename, password, time.current_milli_time(), os.getrandom(32), "login_health"])

    #launch process with file

    #launch "python migrate_accounts.py --option A --option B > "+file_path
    
    return Response(hash, status=200)

@app.route('/migrate', methods=['POST'])
def migrate_launch():

    username=request.form.get('username')
    password=request.form.get('password')

    if not validate(username, password)
        return Response(hash, status=400)

    hash = get_hash([usename, password, time.current_milli_time(), os.getrandom(32), "login_health"])
    
    #launch process with file
    
    file_path = os.paths.join(TMPDIR, "keepermigration", consolehash)
    
    #launch "python migrate_accounts.py --option A --option B > "+file_path

    return Response(hash, status=200)

@app.route('/console/<consolehash>', methods=['GET'])
def get_console_ouptut(consolehash):

    if not HASH_REGEX.match(consolehash) return Response("", status=400)

    file_path = os.paths.join(TMPDIR, "keepermigration", consolehash)
    
    if not os.path.exists(file_path): return Response(hash, status=404)
    
    file_contents = 
    
    return Response(file_contents, 200)
    

