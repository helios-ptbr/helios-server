#!/bin/sh
# Cria o .env de uma instância, com segredos novos.
#
#   ./docker/gerar-env.sh NOME SITE_HOST [PORTA_HTTPS] [PORTA_HTTP]
#
# Exemplos:
#   ./docker/gerar-env.sh teste localhost 8443 8080
#   ./docker/gerar-env.sh cetae eleicoes.exemplo.br
#
# NOME vira o COMPOSE_PROJECT_NAME (letras minúsculas, números, - e _).
set -eu

cd "$(dirname "$0")/.."

if [ "$#" -lt 2 ]; then
    echo "uso: $0 NOME SITE_HOST [PORTA_HTTPS] [PORTA_HTTP]" >&2
    exit 1
fi

NOME="$1"
HOST="$2"
HTTPS_PORT="${3:-443}"
HTTP_PORT="${4:-80}"

case "$NOME" in
    *[!a-z0-9_-]*|"") echo "NOME deve ter só letras minúsculas, números, - e _" >&2; exit 1 ;;
esac

if [ -e .env ]; then
    echo ".env já existe. Apague ou renomeie antes (ele guarda os segredos desta instância)." >&2
    exit 1
fi

if [ "$HTTPS_PORT" = "443" ]; then
    URL="https://$HOST"
else
    URL="https://$HOST:$HTTPS_PORT"
fi

# hex não tem caracteres que atrapalhem a URL do banco nem o .env
PG="$(openssl rand -hex 16)"
SK="$(openssl rand -hex 32)"
OPT="$(openssl rand -hex 32)"

sed \
    -e "s|^COMPOSE_PROJECT_NAME=.*|COMPOSE_PROJECT_NAME=helios-$NOME|" \
    -e "s|^SITE_HOST=.*|SITE_HOST=$HOST|" \
    -e "s|^HTTP_PORT=.*|HTTP_PORT=$HTTP_PORT|" \
    -e "s|^HTTPS_PORT=.*|HTTPS_PORT=$HTTPS_PORT|" \
    -e "s|^URL_HOST=.*|URL_HOST=$URL|" \
    -e "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$PG|" \
    -e "s|^SECRET_KEY=.*|SECRET_KEY=$SK|" \
    -e "s|^EMAIL_OPTOUT_SECRET=.*|EMAIL_OPTOUT_SECRET=$OPT|" \
    .env.example > .env
chmod 600 .env

echo "Criei o .env da instância helios-$NOME ($URL)."
echo "Revise o e-mail e a aparência no .env, e suba com:"
echo "  docker compose up -d --build            # produção"
echo "  docker compose --profile dev up -d --build   # desenvolvimento, com Mailpit"
