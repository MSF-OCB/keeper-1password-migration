# keeper-1password-migration

Dependencies for running src/migrate_account.py on the commandline: keepercommander, secure_delete

IMPORTANT: this tool cannot migrate credit cards! (There is no API to extract them from Keeper.)

TODO: 
 - Shared folders (hoo boy)

##Environment variables & their defaults for the command-line tool AND the docker version
```text
KEEPER_SERVER       https://keepersecurity.eu/api/v2/
OP_SERVER           msfocb.1password.eu
KEEPER_1P_OP_EXE    D:\\1password\\op.exe
TMPDIR or TMP       /tmp
```

##To run from the command line

```text
$python src/migrate_account.py
```

It will ask you the rest of the info and migrate 1 account.

##To run as a dockerised application for migrating multiple accounts

It will also create the new user, and confirm it at the end.

Add this file at `${MSFOCB_SECRETS_DIRECTORY}/keeper_1password_migration_variables.` This file is *extremely sensitive*.

```text
KEEPER_1P_PROVISIONING_PASSWORD=<base64 encoded password for 1Password provisioning user>
KEEPER_1P_PROVISIONING_SECRETKEY=<base64 encoded secret key for 1Password provisioning user>
KEEPER_1P_PROVISIONING_USER= <base64 encoded user for 1Password>
OP_DEVICE= <device ID for 1password account> (the first time you run the tool it will spit this out & tell you to run EXPORT - put it here instead
KEEPER_1P_OP_EXE=/op/op
KEEPER_1P_OP_CONFIG_DIR=/op/config
KEEPER_1P_PASSWORD_PYTHON=/usr/local/bin/python
KEEPER_1P_PASSWORD_SHELL=/bin/bash
```

The, after you run docker-compose up it will expose 8081, and if you have Traefik you can changfe the file yourself, then it will also expose it on the right domain. If you're running it locally you can replace `expose: 8081` with `ports: 8081:8081´.

