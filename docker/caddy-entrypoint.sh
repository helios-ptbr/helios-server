#!/bin/sh
# Escolhe o certificado: os arquivos da pasta certificados/ ou, sem eles, um autoassinado.
set -eu

CERT=/certificados/fullchain.pem
KEY=/certificados/privkey.pem

if [ -f "$CERT" ] && [ -f "$KEY" ]; then
    export TLS_DIRECTIVE="tls $CERT $KEY"
    echo "[helios] usando o certificado de /certificados (fullchain.pem e privkey.pem)"
else
    export TLS_DIRECTIVE="tls internal"
    echo "[helios] sem certificado em /certificados: usando certificado autoassinado (tls internal)"
fi

# 443 é a porta padrão do HTTPS; qualquer outra precisa aparecer no endereço do redirecionamento
if [ "${HTTPS_PORT:-443}" = "443" ]; then
    export HTTPS_PUBLIC_PORT_SUFFIX=""
else
    export HTTPS_PUBLIC_PORT_SUFFIX=":${HTTPS_PORT}"
fi

exec caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
