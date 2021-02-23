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


 /index.html
     login form 
     POST /login 
         username, password
     200 with hash
     console showing health check (credit cards? OTP?), refresh every 500ms, check for end-token
     health check txt ends with \*\*CLEAR\*\* or something
     new button
     POST /migrate
         username, password
     200 with hash
     console showing migration, refresh every 500ms, check for end-token
     
     /login & /migrate
        launches process that logs into keeper, echoes stdout to progress window
        return hash which is text dir of stdout
     /console/HASH
        pipes the text file straight to the response, plaintext

Environment variables & defaults

```text
KEEPER_SERVER       https://keepersecurity.eu/api/v2/
OP_SERVER           my.1password.com
OP_EXE              D:\\1password\\op.exe
TMPDIR or TMP
```

