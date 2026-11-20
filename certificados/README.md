# Certificado HTTPS da instância

Para usar o seu certificado, ponha nesta pasta dois arquivos, com estes nomes:

- `fullchain.pem`: o certificado, com a cadeia completa.
- `privkey.pem`: a chave privada.

O `privkey.pem` precisa ser legível pelo `root` do contêiner: deixe o dono como `root` (`sudo chown root privkey.pem`) ou use `chmod 644 privkey.pem`. Com modo `600` de outro usuário, o log do `caddy` diz `permission denied` e o HTTPS não sobe.

Depois: `docker compose up -d --force-recreate caddy`

Sem os dois arquivos, o Caddy usa um certificado **autoassinado** (`tls internal`).
O navegador mostra um aviso de segurança, e isso é esperado. Serve para teste e laboratório.

Os arquivos `.pem` desta pasta não vão para o git.
