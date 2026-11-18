# Helios com Docker Compose

Uma instância completa e isolada: banco, aplicação, processador de tarefas e HTTPS.
Cada pasta com o seu `.env` é uma instância. Dá para rodar várias ao mesmo tempo no mesmo computador.

## O que sobe

| Serviço | O que faz |
|---|---|
| `db` | Postgres 16, com volume nomeado `pgdata` |
| `migrate` | roda as migrações do banco e sai |
| `web` | o Helios (gunicorn), em português do Brasil |
| `worker` | processa as tarefas em segundo plano: e-mails, apuração, envio de listas de pessoas eleitoras |
| `caddy` | HTTPS na frente do `web`, e entrega a pasta `personalizacao/` |
| `mailpit` | só no perfil `dev`: recebe os e-mails em vez de enviá-los |

A imagem fixa `settings_ptbr`. Quem quiser o Helios em inglês usa o repositório do Ben.

## Primeira instância

1. Crie o `.env` com segredos novos. Exemplo de laboratório, nas portas 8443 e 8080:

   ```
   ./docker/gerar-env.sh teste localhost 8443 8080
   ```

   Exemplo de produção, nas portas 443 e 80:

   ```
   ./docker/gerar-env.sh cetae eleicoes.exemplo.br
   ```

2. Revise o `.env` (e-mail e aparência). O arquivo `.env.example` explica cada linha.
3. Suba:

   ```
   docker compose up -d --build
   ```

   Em desenvolvimento, com o Mailpit e o "Dev Login" (ponha `DEBUG=1` no `.env`):

   ```
   docker compose --profile dev up -d --build
   ```

4. Abra o endereço do `URL_HOST`. Com o certificado autoassinado, o navegador mostra um aviso, e isso é esperado.
5. Os e-mails de desenvolvimento ficam em `http://localhost:8025` (a porta é a `MAILPIT_PORT`).

## Várias instâncias em paralelo

1. Copie a pasta do projeto (ou clone de novo) para outro lugar.
2. Rode o `gerar-env.sh` com **outro nome** e **outras portas**:

   ```
   ./docker/gerar-env.sh outra localhost 9443 9080
   ```

3. Se as duas usam o perfil `dev`, ponha uma `MAILPIT_PORT` diferente no `.env` da segunda.

O nome vira o `COMPOSE_PROJECT_NAME`. Com ele, cada instância tem volumes (`helios-<nome>_pgdata`), rede e contêineres só seus. Nada é compartilhado, e o Postgres não é publicado fora da rede da instância.

## Certificado HTTPS

- **Seu certificado**: ponha `fullchain.pem` e `privkey.pem` na pasta `certificados/` e rode `docker compose up -d --force-recreate caddy`.
- **Sem arquivos**: o Caddy usa um certificado autoassinado (`tls internal`). Serve para teste e laboratório.
- O log do `caddy` diz qual dos dois foi usado: `docker compose logs caddy | grep helios`.

## Trocar a logo da página inicial

1. Copie a imagem para `personalizacao/`, por exemplo `logo.png` (png, svg, jpg, gif e webp).
2. No `.env`: `MAIN_LOGO_URL=/personalizacao/logo.png`
3. `docker compose up -d`

A logo do rodapé funciona igual, com `FOOTER_LOGO_URL`. Esses arquivos não entram na imagem.

## E-mail

- Desenvolvimento: deixe `EMAIL_HOST` e `EMAIL_PORT` vazios no `.env` e use `--profile dev`.
- Produção: preencha `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` e `DEFAULT_FROM_NAME`.
- Sem o `worker` no ar, nenhum e-mail sai.

## Operação

| Tarefa | Comando |
|---|---|
| Ver o estado | `docker compose ps` |
| Ver os logs | `docker compose logs -f web worker` |
| Atualizar o código | `git pull` e `docker compose up -d --build` (as migrações rodam sozinhas) |
| Parar, mantendo os dados | `docker compose down` |
| Backup do banco | `docker compose exec db pg_dump -U helios helios > helios.sql` |
| Restaurar | `docker compose exec -T db psql -U helios helios < helios.sql` |
| **Apagar tudo, inclusive o banco** | `docker compose down -v` |

O `down -v` apaga os volumes `pgdata` e `caddy_data`. Faça o backup antes.

## Segurança

- O `.env` guarda os segredos e não vai para o git (`chmod 600` pelo `gerar-env.sh`). Guarde uma cópia em lugar seguro: perder a `SECRET_KEY` ou a `EMAIL_OPTOUT_SECRET` quebra links já enviados.
- `DEBUG=1` liga o "Dev Login", que entra sem senha. Só em desenvolvimento.
- `HSTS=1` faz o navegador exigir HTTPS neste site por um ano. Só com certificado definitivo.
- Em produção, publique só as portas do `caddy`. O banco e o `web` ficam na rede interna.

## Como a imagem é feita

O `Dockerfile` tem dois estágios. O primeiro compila o `python-ldap`, instala as dependências e compila as traduções (`compilemessages`). O segundo copia o resultado para uma imagem enxuta, sem compilador e sem `gettext`, rodando como usuário sem privilégios. O Fly.io continua funcionando com o mesmo `Dockerfile`.
