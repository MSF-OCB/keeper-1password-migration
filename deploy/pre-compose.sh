#! /usr/bin/env nix-shell
#! nix-shell -i bash --packages docker-compose

echo "Pulling latest image from ${MSFOCB_DEPLOY_DIR}..."

docker-compose --verbose --project-directory "${MSFOCB_DEPLOY_DIR}" --no-ansi --file "${MSFOCB_DEPLOY_DIR}/docker-compose.yml" pull keeper_1password_migration

echo "Done."

