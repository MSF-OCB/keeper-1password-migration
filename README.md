# keeper-1password-migration

Dependencies: keepercommander, secure_delete

TODO: 
 - Shared folders (hoo boy)
 - TOTP migration

Tentative plan:
 - convert into a Flask application
 - Workflow:
   - login with keeper credentials (with checkbox "I confirm I don't have 2FA enabled")
   - health check (no credit cards, no totp)
   - migration (done using "provisioning admin" user of 1P)


Environment variables & defaults

```text
KEEPER_SERVER       https://keepersecurity.eu/api/v2/
OP_SERVER           my.1password.com
OP_EXE              D:\\1password\\op.exe
TMPDIR or TMP
```

