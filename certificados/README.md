# Certificado HTTPS da instância

Para usar o seu certificado, ponha nesta pasta dois arquivos, com estes nomes:

- `fullchain.pem`: o certificado, com a cadeia completa.
- `privkey.pem`: a chave privada.

Depois: `docker compose up -d --force-recreate caddy`

Sem os dois arquivos, o Caddy usa um certificado **autoassinado** (`tls internal`).
O navegador mostra um aviso de segurança, e isso é esperado. Serve para teste e laboratório.

Os arquivos `.pem` desta pasta não vão para o git.
