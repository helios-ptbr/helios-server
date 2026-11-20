# Helios com Docker Compose

Uma instância completa e isolada: banco, aplicação, processador de tarefas e HTTPS.
Cada pasta com o seu `.env` é uma instância. Dá para rodar várias ao mesmo tempo no mesmo computador.

## O que sobe

| Serviço | O que faz |
|---|---|
| `db` | Postgres 16, com volume nomeado `pgdata` |
| `migrate` | roda as migrações do banco e sai |
| `web` | o Helios (gunicorn), em português do Brasil |
| `worker` | processa as tarefas em segundo plano: e-mails, apuração, envio de listas de eleitores |
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
   ./docker/gerar-env.sh producao eleicoes.exemplo.br
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
- **Permissão da chave**: o `caddy` roda sem capabilities (`cap_drop: ALL`), então não lê uma `privkey.pem` com modo `600` que seja de outro usuário (o caso comum, quando você copia o arquivo com a sua conta). O log mostra `open /certificados/privkey.pem: permission denied` e o HTTPS não sobe. Deixe o dono como `root` (`sudo chown root privkey.pem`) ou use `chmod 644 privkey.pem`. Em um servidor com mais de um usuário, prefira o `chown`, porque o `644` deixa a chave legível para todos.
- **Sem arquivos**: o Caddy usa um certificado autoassinado (`tls internal`). Serve para teste e laboratório.
- O log do `caddy` diz qual dos dois foi usado: `docker compose logs caddy | grep helios`.

## Trocar a logo da página inicial

1. Copie a imagem para `personalizacao/`, por exemplo `logo.png` (png, svg, jpg, gif e webp).
2. No `.env`: `MAIN_LOGO_URL=/personalizacao/logo.png`
3. `docker compose up -d`

A logo do rodapé funciona igual, com `FOOTER_LOGO_URL`. Esses arquivos não entram na imagem.

## Página de privacidade

A página `/privacy` vem com um texto padrão, que manda a pessoa ao regramento da unidade. Para pôr o nome da instituição, o contato, o encarregado, a base legal e o prazo de retenção, preencha as variáveis `PRIVACY_*` no `.env` e rode `docker compose up -d`. Detalhes em `docs/privacidade.md`.

## E-mail

- Desenvolvimento: deixe `EMAIL_HOST` e `EMAIL_PORT` vazios no `.env` e use `--profile dev`.
- Produção: preencha `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` e `DEFAULT_FROM_NAME`.
- Sem o `worker` no ar, nenhum e-mail sai.

## Criar pessoas administradoras

O Helios não tem `/admin` do Django. Quem cria eleições entra pelo login por senha (`/auth/password/login`), e a conta nasce por este comando:

```
docker compose exec web python manage.py criar_administrador maria --nome "Maria Silva" --email maria@exemplo.br
```

- A senha é pedida no terminal (mínimo de 8 caracteres).
- Em script, passe a senha por variável, sem deixá-la no histórico: `docker compose exec -e HELIOS_SENHA='...' web python manage.py criar_administrador maria`.
- `--redefinir-senha` troca a senha de um login que já existe.
- `--site` marca a pessoa como administradora do site (páginas de estatísticas e busca de usuários).
- Em produção (`DEBUG=0`) com só o login por senha ligado, `/auth/` já leva direto a essa tela.
- O Helios guarda a senha desse login em texto no banco. Use uma senha que não seja usada em outro lugar.

## Operação

| Tarefa | Comando |
|---|---|
| Ver o estado | `docker compose ps` |
| Ver os logs | `docker compose logs -f web worker` |
| Atualizar o código | `git pull` e `docker compose up -d --build` (as migrações rodam sozinhas) |
| Parar, mantendo os dados | `docker compose down` |
| Backup do banco | `docker compose exec db pg_dump -U helios helios > helios.sql` |
| Restaurar (em banco vazio) | `docker compose exec -T db psql -U helios helios < helios.sql` |
| **Apagar tudo, inclusive o banco** | `docker compose down -v` |

O `down -v` apaga os volumes `pgdata` e `caddy_data`. Faça o backup antes.

Se você subiu com `--profile dev`, use `docker compose --profile dev down` (e `--profile dev down -v`). Sem o perfil, o `down` deixa o `mailpit` no ar e a rede `back` fica em uso.

Para restaurar, o banco precisa estar vazio (por exemplo, depois de um `down -v` e um `up -d db`). Em um banco que já tem as tabelas, o `psql` mostra erros de "já existe".

## Tarefas presas e tempo limite

**Tarefas presas (requeue).** A apuração e os e-mails rodam no `worker`. Enquanto uma tarefa roda, o banco a marca como
`RUNNING`. Se o `worker` morre no meio (falta de memória, queda do servidor, reinício que passa do `stop_grace_period` de 5
minutos), a tarefa fica `RUNNING` para sempre e a eleição parece parada na apuração.

Por isso o `worker` roda `python manage.py requeue_stuck_tasks --older-than 0` ao subir. O comando devolve à fila as
tarefas `RUNNING` e a apuração recomeça do zero, com o mesmo resultado. Ele **não refaz** `voters_email` nem `voters_notify`,
para não mandar o e-mail aos eleitores de novo.

**Isso só funciona com um único `worker`.** Com dois ou mais, um `worker` que sobe refaria a tarefa que o outro está
rodando. Não aumente o número de `worker` sem trocar esse comando (por exemplo, para `--older-than 120`, que só mexe em tarefa
rodando há mais de duas horas). Para rodar o comando na mão: `docker compose exec worker python manage.py requeue_stuck_tasks --dry-run`.

**Tempo limite do `web` (`GUNICORN_TIMEOUT`).** O gunicorn mata a requisição que passa de 30 segundos. Aqui o padrão é
**120 segundos**, e o `.env` pode mudar isso com `GUNICORN_TIMEOUT`. Ele cobre as ações pesadas que rodam dentro da página, como
combinar as decifragens de uma eleição grande.

**Processos do `web` (`WEB_WORKERS`).** É o número de processos do gunicorn dentro do `web`. Não tem relação com o contêiner `worker` de tarefas, e mudar esse número não afeta o requeue acima. Está comentado no `.env.example`. Quando fica vazio, o padrão é 4.

## CSV grande de eleitores

Medido neste compose (Docker, PostgreSQL 16, 1 `web`, 4 processos do gunicorn, 1 `worker`, senhas do Helios):

| Eleitores | Tamanho do CSV | Envio | Processamento no `worker` | Pico do `web` | Pico do `worker` |
|---:|---:|---:|---:|---:|---:|
| 10.000 | 0,5 MB | 0,1 s | 29 s | 238 MiB | 71 MiB |
| 100.000 | 5,3 MB | 0,4 s | 480 s (8 min) | 280 MiB | 144 MiB |
| 1.000.000 | 56 MB | 3,1 s (só o envio, não confirmei) | não medido | 948 MiB | não medido |

- **O envio não é o gargalo.** O arquivo vai inteiro para o banco (56 MB em 3 s). O `web` gasta cerca de 12 vezes o tamanho do arquivo em memória durante o envio (leitura e prévia). Um CSV de 500 MB pediria uns 6 GiB no `web`.
- **O processamento é o gargalo.** O `worker` leva 2,9 ms por eleitor com 10 mil e 4,8 ms com 100 mil (cada senha é gerada e cada eleitor é gravado). Um milhão de eleitores passaria de uma hora e meia, **bem acima dos 5 minutos de `stop_grace_period`**: se o `worker` reiniciar nesse tempo, o requeue refaz a tarefa.
- O Caddy não limita o tamanho do corpo da requisição, e o Django não limita o tamanho do arquivo. Ainda não pusemos um teto: o limite fica a cargo da memória do `web` e do `/tmp`.

## Segurança

- O `.env` guarda os segredos e não vai para o git (`chmod 600` pelo `gerar-env.sh`). Guarde uma cópia em lugar seguro: perder a `SECRET_KEY` ou a `EMAIL_OPTOUT_SECRET` quebra links já enviados.
- `DEBUG=1` liga o "Dev Login", que entra sem senha. Só em desenvolvimento.
- `HSTS=1` faz o navegador exigir HTTPS neste site por um ano. Só com certificado definitivo.
- Em produção, publique só as portas do `caddy`. O banco e o `web` ficam na rede interna.

**Endurecimento dos contêineres (já no `docker-compose.yml`).**
- `web`, `worker` e `migrate` rodam com o sistema de arquivos **somente leitura** (`read_only`), sem nenhuma capability (`cap_drop: ALL`) e com `no-new-privileges`. O app nunca escreve em disco, porque os arquivos enviados vão para o banco. Só o `/tmp`, em memória, aceita escrita.
- O usuário da imagem é o `10001:10001` (número fixo), o que permite `runAsNonRoot` no Kubernetes.
- Há duas redes: `back` (banco, `migrate`, `web`, `worker` e `mailpit`) e `front` (`caddy` e `web`). O `caddy` não alcança o banco.
- O `caddy` perde todas as capabilities, menos `NET_BIND_SERVICE` (abrir as portas 80 e 443).
- As imagens de terceiros têm versão fixa (`postgres:16.16-alpine`, `caddy:2.11.9-alpine`, `mailpit:v1.34.0`). **Atualizar é uma decisão sua**: troque o número no compose e rode `docker compose pull && docker compose up -d`. Acompanhe os avisos de segurança dessas três imagens.
- O `.pyc` já vem pronto na imagem (`PYTHONDONTWRITEBYTECODE=1`), então a partida não fica mais lenta.

**O `/tmp` em memória e os envios grandes (`UPLOAD_TMP_SIZE`).** O Django guarda em arquivo temporário o envio acima de 2,5 MiB, como o CSV de eleitores. Esse arquivo vai para o `/tmp` em memória do `web`, que tem 1 GiB por padrão. O valor sai do `.env` (`UPLOAD_TMP_SIZE`) e conta na memória do contêiner. Um CSV maior que esse espaço falha no envio.

## Como a imagem é feita

O `Dockerfile` tem dois estágios. O primeiro compila o `python-ldap`, instala as dependências e compila as traduções (`compilemessages`). O segundo copia o resultado para uma imagem enxuta, sem compilador e sem `gettext`, rodando como usuário sem privilégios. O Fly.io continua funcionando com o mesmo `Dockerfile`.
