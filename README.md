# keeper-1password-migration

Dependencies: keepercommander, secure_delete

TODO: 
 - Shared folders (hoo boy)
 - TOTP migration

Tentative plan:
 - convert into a Flask application
 - Workflow:
   - login with keeper credentials (email & master password) (with checkbox "I confirm I don't have 2FA enabled")
   - health check (no credit cards, no totp)
   - migration (done using "provisioning admin" user of 1P)

```
 /index.html
     
     1.  login form 
     2. POST /login 
         username, password
     
     3. endpoint returns 401 if not ok or 200 with HASH
     
     4. page shows textbox auto-scrolling to bottom with results of /console/HASH, refreshes every 500ms, check for end-token  \*\*CLEAR\*\* to show "migrate" button.
     
     5. migrate button clicked:
     
     6. POST /migrate
         username, password
     
     7. endpoint returns 200 with hash
     
     8. page shows textbox auto-scrolling to bottom with results of /console/HASH, refreshes every 500ms, check for end-token  \*\*DONE\*\*   or something
     
     endpoints in Flask:
     /login & /migrate
        both validate input then launches process with keeper creds as arguments, that logs into keeper, and echoes stdout to a text file named HASH
        return hash which is text file of stdout
     /console/HASH
        pipes the text file straight to the response, plaintext
        
        
      'unhappy' flows:
        -> error happens because of API bug or migratio bug -> just retry.
        -> thread gets stuck -> restart the container eventually
```
Environment variables & defaults

```text
KEEPER_SERVER       https://keepersecurity.eu/api/v2/
OP_SERVER           my.1password.com
OP_EXE              D:\\1password\\op.exe
TMPDIR or TMP
```

