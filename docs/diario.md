# Diário do projeto helios-ptbr

Registro das decisões da tradução pt-BR do Helios, com o motivo de cada uma.
Cada entrada diz o que foi decidido, por quê, e onde está no código.
Os commits seguem Conventional Commits em português (`git log ben-master..ptbr`).

Como atualizar: uma entrada nova por decisão, no fim do arquivo, com data, motivo e arquivos.

## 1. Estrutura dos repositórios e branches

- **Fork** `helios-ptbr/helios-server`, a partir de `benadida/helios-server`. Não há plano de enviar PR ao Ben.
- **`ben-master`** (antes `master`): espelho do repositório do Ben. Só recebe `fetch` e `merge --ff-only`.
- **`ptbr`**: branch padrão do GitHub e onde o trabalho acontece. Quem clona não precisa trocar de branch. PRs com `Closes #N` fecham as issues sozinhos.
- Motivo do nome `ben-master`: `upstream` já é o nome do remoto, e `git fetch upstream` junto de `git switch upstream` confunde.
- O aviso "N commits behind benadida:master" do GitHub é esperado e não é erro.
- Fluxo de atualização: `docs/atualizar-upstream.md`. Primeiro uso real: merge dos commits #566 e #567 do Ben, com 1 conflito em `helios/templates/new_trustee.html`, resolvido juntando o bloco novo dele com os nossos `translate`.

## 2. O `msgid` é o inglês original

- Nos templates e no Python, o texto marcado é o inglês do Ben. A tradução fica só no `locale/pt_BR/LC_MESSAGES/django.po`.
- Motivo: o inglês não muda, e o merge com o Ben fica simples (poucas linhas tocadas nos arquivos dele).
- Erro corrigido no caminho: uma rodada de e-mails tinha usado português como `msgid`. Foi refeita.
- Quando o mesmo texto precisa de duas traduções ("Login" botão x coluna), usa-se contexto do gettext (`msgctxt`).
- Texto com aspas escapadas dentro de `{% translate "..." %}` é cortado pelo `makemessages`. Usar `blocktranslate`.

## 3. Idioma e configuração

- `settings_ptbr.py` importa o `settings.py` do Ben e muda só o necessário: `LANGUAGE_CODE`, `LANGUAGES`, `LOCALE_PATHS`, `LocaleMiddleware` e a mensagem inicial (`WELCOME_MESSAGE`). O `settings.py` do Ben não é alterado.
- Rodar com `DJANGO_SETTINGS_MODULE=settings_ptbr`. Precisa de `manage.py compilemessages` (o `.mo` não vai para o git).
- No ambiente de teste local o `LocaleMiddleware` é retirado e o idioma vem do `LANGUAGE_CODE`, porque o worker não tem requisição.

## 4. Cabine de votação e verificadores

- A cabine (`heliosbooth`) é estática e não passa pelo Django.
- **Rejeitado**: um `i18n.js` que escolhe o idioma por `?lang=` e `document.write`. Motivo: a URL decidiria qual JavaScript carrega, o que abre margem a ataque.
- **Adotado**: uma página por idioma (`vote.pt-BR.html`), gerada no build, com tags `<script src>` fixas. Um `i18n.js` fixo só com `T()`, e um `strings.<idioma>.js` gerado do `.po`. Geradores: `booth_lang.py`, `tools/gen_booth_pages.py`, `tools/po2js.py`.
- O arquivo de textos é um `.js` de dados puros, carregado na abertura. A cabine já precisa de rede na abertura e no envio. JSON via `$.get` não funciona com `file://`. Todo texto do meio do fluxo (erros, confirmações) fica nesse arquivo.
- O mesmo desenho vale para o verificador de cédula única (`single-ballot-verify`) e o da eleição inteira (`heliosverifier/verify.html`). Os textos do Worker do verificador vão como dados (`BOOTH_STRINGS`).
- O `i18n.js` do verificador é cópia do da cabine. Um teste confere que as duas são idênticas.
- Aviso: `election_build.html` aponta para o modelo da lista de perguntas, mas não tem rota. Se alguém ligar essa página, ela precisa do objeto `I18N`.

## 5. JavaScript dentro das telas do Django

- Os textos de JavaScript passam pelo Django: a página monta um objeto (`I18N`, `HELIOS_TZ_TEXTS`) com os textos já traduzidos. Exemplo: `election_questions.html` e `question.html`.
- Textos que entram em strings JavaScript usam `escapejs`. Um apóstrofo na tradução não quebra a página.
- Valores enviados ao servidor continuam em inglês (`"result_type": "absolute"`), mesmo que a tela mostre "absoluto".
- O que sobrou em `helios/media` e `server_ui/media` é biblioteca de terceiros. Nada mais a traduzir (issue #15).

## 6. Vocabulário (ver também `docs/glossario.md` e `docs/estilo.md`)

- **Pessoa curadora** (trustee): mantido. "Fiscal" foi rejeitado: no Brasil, fiscal observa a votação; o trustee guarda parte da chave. "Fiscal" também se misturaria com "auditar".
- **Login** e **senha**: substituíram "nome de acesso" por serem as palavras que a pessoa eleitora vê na prática.
- Sem gênero: "recebeu convite" em vez de "foi convidada", "pessoa administradora", "pessoa usuária".
- "Dev Login" fica em inglês de propósito (só existe em desenvolvimento).
- Ficam em inglês de propósito: `Http404` (só em `DEBUG`), erros internos e as respostas `SUCCESS` e `FAILURE` da API.

## 7. Datas e fusos

- O banco e o servidor guardam e comparam tudo em UTC, sem fuso (`datetime.utcnow()`). Nada disso muda.
- **Decisão (issue #24)**: a pessoa digita a data no fuso do navegador. O navegador converte para UTC ao enviar. Foi escolhida a opção B (navegador) e rejeitada a A (servidor) porque a B só mexe em arquivos nossos e não gera conflito de merge com o Python do Ben.
- Implementação: `helios/media/timezone-display.js` (UTC para local ao abrir, local para UTC ao enviar, com campo escondido no envio), `timezone-display.css` (balão ⓘ ao lado de cada campo), e textos novos em `server_ui/templates/base.html` e no `.po`.
- Não existe fuso fixo no código e não há build. `compilemessages` só é preciso quando um texto muda.
- Balão ⓘ: fica no fim da linha do texto de ajuda (sem o `<br>` antes dele), e a caixa abre para a esquerda (`right: 0` no CSS), para não sair da tela. O campo vira bloco (`display: block`) para o texto de ajuda continuar na linha de baixo.
- O formato das datas segue o idioma da página (`<html lang>`).
- Sem JavaScript, o campo é lido como UTC.
- Se o fuso do computador estiver errado, o horário digitado fica errado. A linha "Este horário é: ... UTC / ... BRT" mostra isso antes do envio.
- O Brasil não usa horário de verão. Os testes não consideram isso.

## 8. Testes

| Arquivo | O que cobre |
|---|---|
| `helios/test_ptbr.py` | renderização em pt-BR e em inglês, e-mails, telas da curadoria, duas varreduras que procuram inglês: 11 telas da eleição e 17 telas do site (início, login, opt-out, estatísticas, listas) |
| `helios/test_po.py` | os 5 arquivos `.po`: sem entrada vazia ou "fuzzy" (#19), marcadores `%(x)s` e `%d` iguais no original e na tradução (#20), `django.po` em dia com o código via `makemessages` (#18), `msgfmt --check` |
| `helios/test_datas.py` | início, fim e limites da votação em 16 fusos do Brasil, prorrogação, formulário, Aragarças x Barra do Garças |
| `tools/test_fusos_navegador.py` | `timezone-display.js` no Chromium com cada fuso (variável `TZ`), pares criador x leitor |
| `tools/test_booth_*.py`, `tools/test_settings_ptbr.py` | geração das páginas da cabine e do verificador, `settings_ptbr` |

- Aragarças (GO, UTC-3, `America/Sao_Paulo`) e Barra do Garças (MT, UTC-4, `America/Cuiaba`) são vizinhas com 1 hora de diferença. Criada às 09:00 em Barra (13:00 UTC), a votação abre às 10:00 em Aragarças. O servidor decide só pelo UTC.
- Teste de ponta a ponta no Chrome (eleição completa em pt-BR, 3 pessoas eleitoras, apuração Azul 1, Verde 1, Vermelho 0): sem erros funcionais.
- E-mails testados com o Mailpit (container `helios-mail`, FOSS), que recebe o SMTP e não envia nada para fora.
- A mensagem `unload is not allowed` no console da cabine vem do código do Ben.

## 9. CI

- `.github/workflows/ci.yml` roda também na `ptbr`, instala `gettext`, roda `compilemessages` e os testes de `tools/`.
- **CI só manual** durante o trabalho pesado, para poupar minutos do Actions (a execução leva cerca de 3 min). Disparo: `gh workflow run CI -R helios-ptbr/helios-server --ref ptbr`. **Antes do Release**, devolver os gatilhos `push` e `pull_request` (estão comentados no `ci.yml`).
- `helios/test_po.py` faz o papel do CI do `.po` (issues #18 a #20): falha se o `.po` estiver desatualizado, com `msgid` sem tradução ou `fuzzy`, ou com marcadores diferentes. Ele roda o `makemessages` num subprocesso e devolve o `django.po` original no fim. Precisa do pacote `gettext` (sem ele, esses testes são pulados).
- Previsto: #21 (varredura de todas as rotas em busca de inglês).

## 9b. Docker (issue #25)

Guia: `docs/docker.md`. Decisões:
- **Uma imagem, uma pasta por instância.** Cada instância é uma pasta com o seu `.env`. O `COMPOSE_PROJECT_NAME` isola volumes, rede e contêineres, então várias rodam em paralelo no mesmo computador. Criado por `docker/gerar-env.sh NOME HOST [PORTA_HTTPS] [PORTA_HTTP]`.
- **Postgres dentro do compose**, com volume nomeado, mesmo em produção, para isolar cada sistema. O banco não é publicado fora da rede da instância.
- **Caddy** faz o HTTPS. Com `certificados/fullchain.pem` e `privkey.pem`, usa os arquivos. Sem eles, usa `tls internal` (autoassinado). A escolha é feita em `docker/caddy-entrypoint.sh`.
- **Mailpit** só no perfil `dev`. Em produção, `EMAIL_HOST` e afins vêm do `.env`.
- **`settings_ptbr` fixo na imagem.** Quem quiser o Helios em inglês usa o repositório do Ben.
- **O `Dockerfile` do Fly.io foi substituído** (multi-stage). O `fly.toml` não mudou. O merge com o Ben, se der conflito, fica para depois.
- **Segredos no `.env`** (fora do git). Docker secrets ficam para depois.
- **Logo trocável sem reconstruir**: a pasta `personalizacao/` é servida pelo Caddy em `/personalizacao/`, e `MAIN_LOGO_URL` aponta para o arquivo. Sem mexer no Python do Ben.
- O `db_worker` roda com `--no-reload` no contêiner.
- Testado: imagem de 318 MB, sem `gcc` e sem `msgfmt`, com `ldap` funcionando; HTTPS autoassinado e com certificado próprio; redirecionamento de HTTP; logo própria; app, fila no banco, worker e e-mail no Mailpit; dados mantidos após `down`.

## 10. Achados no código do Ben (não alterados)

1. `helios/views.py`, perto da linha 344: `election.voting_has_started` sem `()`, então a condição é sempre verdadeira. Só afeta o texto de status ("Vote in" no lugar de "Register to vote in").
2. Texto de data com deslocamento (`...Z` ou `-03:00`) é guardado como horário da Califórnia (`TIME_ZONE=America/Los_Angeles`, `USE_TZ=False`): `14:00Z` vira 06:00. O navegador nunca envia isso. Só um pedido feito à mão cai nesse caso.

## 11. Pendências (issues abertas)

- #17 idioma do e-mail por eleição (hoje vem do `LANGUAGE_CODE`).
- #21 varredura de telas: feita (seção 13). Cobre eleição, site, login, opt-out, pessoa curadora e uma ferramenta que acha texto fora do catálogo nos templates.
- #23 feita (seção 13): datas, plurais e números. Separador de milhar: mantido sem (decisão do usuário). Ordenação alfabética: fica como o banco ordena (não é tradução).
- Pessoa curadora externa: testada de ponta a ponta no navegador, com a decifragem pela chave dela (seção 14).
- O que falta para o Release está na seção 18 (fases A a G).

## 12. Páginas longas e plurais (issues #21 e #23)

- `/about`, `/faq`, `/privacy` e `/docs` têm um template por idioma: `server_ui/templates/<nome>.pt-BR.html`. Motivo: são textos longos, e marcar com `{% trans %}` geraria conflito de merge com o Ben. O `server_ui/view_utils.py` (`render_template`) procura `<nome>.<idioma>.html` e, se não achar, usa o original. Em inglês nada muda.
- Cada página traduzida mostra o aviso "Tradução não oficial" (`server_ui/templates/aviso_traducao.html`), com link para o fork, para o Helios de Ben Adida e para a versão original em inglês (`vote.heliosvoting.org/<página>`).
- `/docs` aponta para a tradução do manual e de "Como o Helios funciona" (`docs/pt-BR/manual-do-usuario.md` e `docs/pt-BR/como-o-helios-funciona.md`), cada uma com link para o original em inglês. A arquitetura segue só em inglês. As imagens do manual foram refeitas em português (seção 15).
- Separador de milhar: decidido manter sem separador (2603).
- A tradução de `/privacy` precisa de revisão de quem responde pela política de privacidade da instituição.
- Plurais: 8 textos que mostravam "1 voters" ou "voter(s)" passaram a usar `{% blocktranslate count %}` com singular e plural (bboard, stats, lista de pessoas eleitoras, confirmação de remoção). No pt-BR, 0 e 1 usam o singular. Em inglês só muda o caso n = 1 ("1 voter").
- Testes: `helios/test_ptbr.py` (páginas fixas em pt-BR e em inglês, plurais).

## Bateria Docker (2026-11-18)

- **Login padrão no Docker.** Sem `AUTH_ENABLED_SYSTEMS`, o Helios liga `ldap`, `google` e `facebook`, que não funcionam sem chaves. O `.env.example` agora traz `AUTH_ENABLED_SYSTEMS=password`. Com `DEBUG=1`, o `devlogin` entra por conta própria.
- **Rótulo do formulário de voto.** A tela de login da pessoa eleitora ainda dizia "ID da pessoa eleitora", mas o e-mail e o glossário usam "login". O `msgstr` de "Voter ID" passou a ser "Login". Achado na bateria Docker.
- **E-mail de confirmação de voto em inglês.** O e-mail enviado depois do voto (`server_ui/templates/email/cast_vote_body.txt` e o assunto em `server_ui/glue.py`) estava sem tradução ("Bateria 1 - vote cast"). Passou a usar `translate`/`blocktranslate` e `gettext`, com 5 textos novos no `django.po`. O `msgid` continua igual ao inglês original. Na tela de login da pessoa eleitora, "O seu ID e a sua senha" virou "O seu login e a sua senha".
- **Votos na bateria.** Maria votou duas vezes (Azul, depois Verde) e o segundo voto foi aceito. A cabine só deixa marcar 1 opção numa pergunta com máximo 1.
- **"ID" no login.** Mais dois textos do formulário de votação ainda diziam "ID": "ID ou senha incorretos" e "Digite o ID que você recebeu". Passaram a dizer "login". Senha errada, login inexistente, campos vazios e uma tentativa de injeção SQL no login foram barrados, sem erro 500.
- **Limites de seleção na cabine** (pergunta com mínimo 1 e máximo 2): com 0 opções, a cabine barra e mostra "Você precisa selecionar pelo menos 1 resposta(s)." Com 1 e 2 opções, passa para a revisão. O terceiro clique não marca a terceira opção. O voto em branco (mínimo 0) passa e vale.
- **Eleição completa `bateria-1` no Docker.** Votos: Maria votou duas vezes (a última, Verde, vale), Ana votou Vermelho e João votou em branco. Apuração: Azul 0, Verde 1, Vermelho 1, Açaí 0, correta. Fluxo: calcular a apuração, combinar as decifragens e liberar o resultado, tudo em pt-BR.
- **CSV de pessoas eleitoras (bateria 3).** Barrados com mensagem em pt-BR: e-mail inválido, tipo inválido, colunas erradas, só cabeçalho. Aceitos na pré-visualização: acentos, vírgula entre aspas, fim de linha CRLF, nome em branco (usa o e-mail), HTML no nome (aparece como texto, sem executar). **Achado corrigido:** arquivo vazio mostrava a mensagem interna do Django em inglês ("The 'voter_file' attribute has no file associated with it"). Agora mostra "o arquivo está vazio" (`helios/views.py`, +3 linhas). Falta ver o que o processamento faz com login repetido e login com espaço.
- **CSV, continuação.** Arquivo vazio: agora mostra "o arquivo está vazio" (conferido no Docker). Login repetido no mesmo arquivo: o Helios guarda só uma pessoa, a da última linha, sem avisar (comportamento do Ben, só registrado). Login com espaço ("com espaco"): aceito sem aviso. Arquivo grande: 20000 linhas (826 KB) processadas em cerca de 80 s pelo `worker`, e a lista abre em 1,3 s. O arquivo não tem limite de tamanho no Helios.
- **Formulário de criação (bateria).** Nome curto com espaço, acento, barra ou mais de 40 caracteres: barrado com mensagem em pt-BR. Nome curto vazio e nome vazio: barrados pelo navegador (campos obrigatórios). Nome com HTML: aceito e mostrado como texto. **Corrigido:** "An election with short name X already exists" aparecia em inglês (`helios/views.py`, 2 pontos); agora usa `gettext`. **Só registrado, é do Ben:** data de fim antes da data de início é aceita sem aviso, e e-mail de ajuda sem formato de e-mail também.
- **Django admin (bateria).** O Helios **não tem** `/admin` (responde 404; `django.contrib.admin` não está nos apps). O `createsuperuser` cria um usuário do Django que o Helios não usa. O Helios tem o seu próprio usuário (`helios_auth.User`): `admin_p` marca a administração do site, e qualquer pessoa autenticada pode criar eleições (o `can_create_election` dos sistemas `devlogin`, `password` e `ldap` devolve sempre verdadeiro). A pessoa sem login que tenta criar eleição vai para `/auth/`. Co-administradoras de uma eleição entram pela tela "pessoas administradoras" da eleição.
- **Criar administradora no Docker.** Não há tela. O jeito é um comando no contêiner: `docker compose exec web python manage.py shell -c "from helios_auth.auth_systems.password import create_user; create_user('login','senha','Nome')"`. Testado: o login em `/auth/password/login` funciona e a pessoa cria eleição. **Achados do Ben, só registrados:** a senha desse usuário fica em texto puro no banco (`info['password']`); o "esqueci a senha" manda a senha por e-mail em texto puro e falha sem a chave `email` (o `create_user` não grava e-mail); o login por senha não aparece na lista de `/auth/` quando há outros sistemas, só pelo endereço direto.
- **Login por senha em inglês. Corrigido** em `helios_auth/auth_systems/password.py`: rótulos "Username" e "Password" e as mensagens "Bad Username or Password" e "no such username" agora passam por `gettext`. O corpo do e-mail de "esqueci a senha" continua em inglês (é pouco usado e envia a senha em texto puro).
- **Janela de votação em tempo real (bateria-janela).** Eleição criada às 15:40 (America/Sao_Paulo) com início 15:41 e fim 15:43, digitados no fuso do navegador. A página mostra 18:41 UTC / 15:41 BRT. Antes do início: `/vote` mostra "ainda não está aberta". Dentro da janela (15:41:20): voto aceito. Cabine aberta antes do fim e envio às 15:43:13: o voto **não conta** (o banco manteve só o primeiro, `votos = 1` e o mesmo código de rastreamento), mas a pessoa volta à página inicial **sem nenhuma mensagem** (`helios/views.py`, `password_voter_login`, é do Ben). Depois do fim, `/vote` mostra "Esta eleição já foi apurada", texto do template `election_tallied` que o Ben usa para qualquer eleição encerrada, mesmo sem apuração. Só registrado.
- **Cabine offline (bateria).** Com a cabine carregada e a rede do Chrome desligada (CDP, modo offline): escolher opções, revisar e cifrar a cédula funcionam sem nenhum pedido de rede (0 pedidos). O único pedido é o `POST .../cast` do passo "Prosseguir para o login", que falha com `ERR_INTERNET_DISCONNECTED` e mostra a página de erro do Chrome. Voltando pelo histórico com a rede ligada, a cabine reaparece na revisão com a cédula guardada, e dá para tentar de novo. Confirma o que o Ben diz.
- **Plural da seleção.** "[1 seleções de um total possível de 1-2]" ficou "[1 seleção(ões) de um total possível de 1-2]" (`booth_html.po`, páginas geradas de novo). O molde do Ben não tem plural, então usei "seleção(ões)".
- **Segurança básica (bateria).** Sem login e com outra pessoa logada (`admin1`), numa eleição que não é dela: `edit`, `admins/`, `compute_tally`, `freeze` e `save_questions` (mesmo com token CSRF válido) respondem 403. `POST` sem token CSRF: 403. Eleição, e-mail curto, cédula e rota inexistentes: 404, sem erro 500. A tela de perguntas e a lista de pessoas eleitoras abrem para qualquer pessoa que saiba o UUID (o Ben deixa de propósito: "anyone can see the questions"; salvar exige ser administradora). Com `DEBUG=1`, o 404 mostra a página técnica do Django: em produção o `.env` deve ter `DEBUG=0`.
- **Opt-out e opt-in (bateria).** O link do rodapé do e-mail abre "Confirmar a saída da lista de e-mails" em pt-BR, com o endereço certo; confirmar mostra "Saída da lista concluída". Depois disso, o envio em lote da eleição (`bateria-2`) **pulou** o Beto e entregou só para a Ana (1 e-mail novo). A tela `/optin/` abre em pt-BR. Um e-mail de confirmação do opt-out não apareceu no Mailpit; as telas de pedido de opt-in/opt-out por e-mail ainda faltam.
- **Reenvio de senha da pessoa eleitora (bateria).** A tela `password_voter_resend` e o e-mail "Suas credenciais de votação para Bateria 1" saem em pt-BR, com login, senha e links certos. Login existente e inexistente recebem a mesma resposta (não revela quem está na lista), e só o existente recebe e-mail. A senha reenviada é a mesma (não gira). **Corrigido:** dois textos ainda diziam "ID" ("com esse ID", "Digite o seu ID abaixo"); agora dizem "login". Os textos "Nome ou ID do usuário" e "ID do usuário:" são das estatísticas do site e ficaram.
- **Persistência (bateria).** `docker compose --profile dev down` seguido de `up -d --build` (sem `-v`): 10 eleições, 20009 pessoas eleitoras, 5 votos e 2 usuários antes e depois, iguais. Os 3 volumes (`pgdata`, `caddy_data`, `caddy_config`) continuaram. A caixa do Mailpit esvazia, pois ele não tem volume (é só para teste).
- **Modo de produção, `DEBUG=0` (bateria).** Com um único sistema de login (`password`), `/auth/` vai direto para a tela de login por senha. O `devlogin` fica desligado (`/auth/start/devlogin` volta para `/auth/`). A página 404 usa o modelo do site, em pt-BR ("Não foi possível encontrar a página que você pediu."), sem a página técnica do Django. `/admin/` e UUID inválido: 404. Login por senha sem token CSRF: 400. A administradora `admin1` entrou e criou a eleição `prod-1`. Sem exceções de JavaScript. **Só registrado:** a página 404 sai com `lang="en"` no `<html>`, porque o `base.html` do Ben usa `LANGUAGE_CODE` e o tratador de 404 não o fornece. O `.env` de teste ficou com `DEBUG=0`; ponha `DEBUG=1` de volta se quiser o `devlogin`.
- **Fusos do Brasil no servidor real (bateria).** Para cada um dos 15 fusos do Brasil (Noronha, Belém, Fortaleza, Recife, Araguaina, Maceió, Bahia, São Paulo, Campo Grande, Cuiabá, Porto Velho, Boa Vista, Manaus, Eirunepé e Rio Branco), com o fuso do Chrome trocado por CDP (`Emulation.setTimezoneOverride`), criei uma eleição digitando 09:00 a 18:00 no formulário. O servidor guardou o UTC certo nos 15 casos (por exemplo 12:00-21:00 em UTC-3, 13:00-22:00 em UTC-4, 14:00-23:00 em UTC-5), e a tela de edição reabriu com 09:00 e 18:00 locais. Cruzado: eleição criada em Cuiabá (Barra do Garças) às 09:00 aparece em Aragarças (São Paulo) como 10:00 BRT, em Rio Branco como 08:00 ACT e em Noronha como 11:00. As eleições `tz-*` ficaram no banco de teste.
- **Testes locais depois da bateria.** Suíte do Helios em inglês: 402 testes OK (3 novos em `PtBrBateriaDockerTests`, `helios/test_ptbr.py`, cobrindo "login" no lugar de "ID", "o arquivo está vazio", o nome curto repetido e o e-mail de voto registrado). Testes das ferramentas (`tools.*`): 45 OK, 1 pulado (sem `node`).
- **E-mail de apuração liberada (bateria).** O formulário com `?template=result` mostra "Apuração liberada - <SUBJECT>" com os marcadores, e o e-mail enviado chega em pt-BR ("A apuração de Bateria 1 foi calculada e liberada", código de rastreamento, link de opt-out). Fim da bateria: 9 áreas cobertas, 11 correções nossas, achados do Ben só registrados.
- **Neutralidade de gênero relaxada (2026-11-18).** "Pessoas eleitoras" deixava rótulos e botões pesados. Nos rótulos, botões, listas e contagens passou a valer o masculino genérico ("Contatar os eleitores", "Baixar a lista de eleitores em CSV", "2 eleitores", "enviar e-mail aos eleitores"): 49 textos do `django.po`. As frases longas e explicativas e os textos do verificador mantêm "pessoa eleitora". Registrado no `docs/glossario.md`. Na cabine, "Envie sua cédula cifrada e se autentique para verificar sua elegibilidade" virou "Envie a sua cédula cifrada e entre com o seu login para confirmar que você pode votar", e "onde você fará login para validar sua elegibilidade para votar" virou "onde você entrará com o seu login para confirmar que pode votar".
- **Neutralidade de gênero: desfeita (2026-11-18).** Decidido manter "pessoa eleitora" em todo lugar, para o termo ser o mesmo em todas as telas. Voltaram "pessoa eleitora" e "pessoas eleitoras" nos 49 textos do `django.po`, nos testes e no glossário. A única mudança que ficou do commit anterior é a das frases da cabine ("Envie a sua cédula cifrada e entre com o seu login para confirmar que você pode votar"). O rótulo do CSV agora é "Baixar a lista de pessoas eleitoras em CSV".
- **Comando `criar_administrador` (2026-11-18).** Novo arquivo `helios_auth/management/commands/criar_administrador.py` (sem tocar em código do Ben). Cria a pessoa com login por senha, com nome, e-mail (para o "esqueci a senha" funcionar), `--site` (admin_p) e `--redefinir-senha`. A senha vem do terminal ou da variável `HELIOS_SENHA`; exige 8 caracteres ou mais e rejeita login com espaço. 5 testes novos em `helios_auth/test_criar_administrador.py` (suíte: 407 OK). Testado no Docker: criar, login repetido, senha curta. Documentado em `docs/docker.md`.

## Teste de carga no Docker (2026-11-18, instância `carga`)

Eleição `carga-1`: **10000 pessoas eleitoras** e **11 perguntas com 114 opções** no total (3, 4, 5, 6, 8, 10, 12, 14, 16, 18 e 18 opções; máximo de 1 a 18 seleções). Máquina com 20 CPUs e 31 GB. Sem limites de memória nos contêineres.

| Etapa | Tempo | Memória no pico |
|---|---|---|
| CSV de 10000 pessoas (556 KB): envio + processamento no `worker` | 31 s | `worker` 73 MiB, `db` 43 MiB |
| Congelar a urna | 1 s | sem impacto |
| Verificar **1 cédula** (11 perguntas, 114 opções) no `worker` | **4,5 s** | `worker` 72 MiB |
| Gerar 1 cédula (o que o navegador faz) | 2,7 s | |
| Apuração cifrada (`election_compute_tally`) com 10000 cédulas | **116 s** | **`worker` 15,5 GiB** (ficou em 11,4 GiB depois), `db` 2,3 GiB |
| Decifragem do Helios (`tally_helios_decrypt`) | 1 s | sem impacto |
| `combine_decryptions` (na requisição) e `release_result` | 0,2 s e 0,1 s | `web` 261 MiB |

O resultado saiu certo e a eleição foi concluída. As 10000 cédulas gravadas para o teste repetem 20 cédulas distintas (gerar 10000 levaria 7 h); o custo da apuração não depende disso.

**Achado 1, o mais grave: a apuração gasta 15,5 GiB.** `Election.compute_tally` (`helios/models.py`) faz `for voter in self.voter_set.exclude(vote=None)`. O Django carrega **todas** as pessoas eleitoras com as cédulas na memória antes de somar. Com `.iterator(chunk_size=...)` a memória fica quase constante. É uma linha no código do Ben. Com limite de memória de 1 GiB no `worker`, essa apuração seria morta por falta de memória e a tarefa ficaria `RUNNING` para sempre. É compatível com o problema que houve no servidor antigo.

**Achado 2: a verificação é serial e lenta.** Cada cédula leva 4,5 s no `worker`, e há um `worker` só. Dez mil cédulas levam cerca de 12,5 h de fila. A apuração só começa com 0 cédulas pendentes. Se muita gente votar perto do fim, a fila atrasa a apuração. Dá para ter mais de um `worker` com `docker compose up -d --scale worker=N`.

**Achado 3: a memória do `worker` não volta.** Depois da apuração ele ficou com 11,4 GiB. O Python não devolve a memória ao sistema. O `db_worker --max-tasks N` faz o processo sair depois de N tarefas, e o Docker o reinicia.

**Teste da correção (sem alterar o código).** Rodei a mesma soma da apuração dentro do contêiner `web`, na eleição `carga-1` (10000 cédulas), com `.iterator(chunk_size=500)`: 135 s, **pico de 923 MiB** (contra 15,5 GiB do `worker` sem o `iterator`). O resultado é **idêntico** ao `encrypted_tally` já salvo (`igual_ao_salvo=True`). Ou seja, a mudança de uma linha em `Election.compute_tally` corta a memória em cerca de 17 vezes e não muda o resultado. O arquivo `helios/models.py` não foi alterado: a mudança vai por PR, a partir da `ben-master`.

## 13. Varredura de telas e e-mails (issues #21 e #23, 2026-11-18)

Foco só em tradução; nenhuma funcionalidade mudou. O inglês continua igual (os `msgid` são o texto original).

**Como foi feito**
- `tools/templates_sem_traducao.py` (só biblioteca padrão) acha texto visível nos templates fora de `{% translate %}` e `{% blocktranslate %}`. Tem uma lista de exceções (marca, tela `devlogin`, exemplos de CSV, templates sem uso). `tools/test_templates_sem_traducao.py` falha se um template novo ganhar texto sem tradução.
- Rastreio no Docker em pt-BR, logado: 94 páginas (eleição nova, com perguntas e eleitores, concluída com 10000 cédulas, estatísticas, login, opt-out, páginas fixas), com dois detectores (palavras em inglês e `msgid` do catálogo que apareceu na tela). Sobraram só nomes próprios nas páginas `about` e `docs`.
- Testes novos em `helios/test_ptbr.py`: varredura das telas de login, reenvio de credenciais, selo e "eleições em que você votou"; varredura das telas da pessoa curadora (início, gerador de chave, conferir chave, decifrar) entrando pelo link do e-mail; página do gerador de chave em pt-BR e inglês; e-mails de aviso.

**Achados traduzidos**
- `elections_voted.html` ("Elections where you voted") estava inteira em inglês.
- `election_keygenerator.html`, a tela em que a pessoa curadora externa gera a chave, estava inteira em inglês (22 textos). Testei no navegador: gerar, mostrar a chave secreta, baixar, enviar a chave pública. Sem erro de JavaScript.
- `election_badge.html` ("powered by", "vote!").
- O "Subject:" da prévia do e-mail (`voters_email.html`).
- E-mails de aviso que estavam fixos em inglês: link da página da pessoa curadora (`trustee_send_url`), "pessoa curadora enviou a chave pública", "fez a decifragem parcial", "o seu voto foi removido", e os avisos para a administração em `tasks.py` (apuração cifrada calculada, Helios decifrou, arquivo de pessoas eleitoras processado, pessoas que saíram da lista). Plurais com `ngettext` ("1 linha ... não foi adicionada" / "N linhas ... não foram adicionadas"). O idioma do e-mail segue `LANGUAGE_CODE` (pt-BR no fork); escolher por eleição fica na #17.
- Erros de formulário em inglês: "No special characters allowed in the short name." e "Bad Username or Password" do LDAP.

**Deixado em inglês de propósito:** tela `devlogin`, textos que só aparecem com `DEBUG=1` (404 técnico do Django), mensagens de status para redes sociais (`status_update_message`, o Helios não as mostra), respostas `SUCCESS`/`FAILURE` da API, `LOGIN_MESSAGE` dos sistemas de login (nenhuma tela usa) e os templates `confirm.html`, `done.html` e `election_tallied.html` de `server_ui` (sem uso ou sombreados pelos de `helios`).

**#23.** Datas e fusos, plurais e números estão feitos. O separador de milhar fica sem (decisão de 2026-11-18) e a ordenação alfabética é a do banco: não é texto traduzido.

**#17 (idioma do e-mail por eleição) não entra agora.** Seria uma função nova (campo na eleição, migração e escolha na tela), e o foco é tradução.

## 14. Pessoa curadora externa de ponta a ponta (2026-11-19)

Teste no Chrome, no Docker (`DEBUG=1`, `AUTH_ENABLED_SYSTEMS=password`), na eleição `curadora-ext`: 1 pergunta com 3 opções, 3 pessoas eleitoras, o Helios e uma pessoa curadora externa (`curadora@example.com`).

| Etapa | Resultado |
|---|---|
| Adicionar a pessoa curadora e "enviar o acesso" | O e-mail chega em pt-BR, com o link da página dela |
| Gerar a chave, mostrar a chave secreta (2066 caracteres) e enviar a chave pública | OK. A impressão digital aparece na página dela e na da administração |
| Congelar, e-mail de votação e 3 votos pela cabine (Azul, Verde, Verde) | OK |
| Apuração cifrada | OK. A tela mostra "aguardando a apuração desta pessoa curadora" |
| Conferir a chave secreta | Chave certa: "a sua chave secreta confere!". Chave com 5 caracteres trocados: "Ops, a sua chave está errada." |
| Decifrar: passo 1 (no navegador) e passo 2 (enviar os fatores ao servidor) | OK, sem erro de JavaScript e sem janelas de aviso |
| Combinar as decifragens e liberar | Azul 1, Verde 2, Vermelho 0, que é o que foi votado. "Esta eleição está concluída." |

Os textos da tela de decifrar saíram todos em pt-BR, inclusive os dois passos e o aviso de deixar o navegador "offline" no primeiro passo. Nada novo para traduzir. A etapa de decifragem com chave externa, que faltava, está fechada.

## 15. Imagens do manual em português (2026-11-19)

As 20 imagens do manual passaram a ser capturas da interface em pt-BR, em `docs/images/manual/pt-BR/` (mesmos nomes e tamanhos das originais, que ficam em `docs/images/manual/` para o manual em inglês). O `docs/pt-BR/manual-do-usuario.md` aponta para elas.

- **Como foram feitas:** no Docker, no Chrome por CDP, com a mesma eleição do manual em inglês: "Eleição da Diretoria do Clube Riverside 2026", 2 perguntas (4 pessoas candidatas, de 0 a 2; orçamento Sim/Não), 3 pessoas eleitoras (Dana Lee, Sam Ortiz, Priya Shah) e a pessoa administradora "Alice Admin" (criada com `criar_administrador`). Os 3 votaram pela cabine e a apuração saiu Dana 2, Sam 1, Priya 2, Tom 0; Sim 2, Não 1, igual ao manual em inglês.
- **Cuidado ao refazer:** a página de perguntas tem formulários de edição escondidos; preencher o primeiro campo `question` da página preenche o formulário escondido. Preencha o campo visível.
- O e-mail de exemplo da Parte 2 passou a ser o texto real em português.
- Para refazer as imagens, a instância precisa de `WELCOME_MESSAGE=Bem-vindo ao Helios, eleições online seguras.` no `.env` (a mensagem padrão é outra).

## 16. Eleitor, curadoria e administradores (2026-11-19)

Decisão do usuário, ponto a ponto, depois de ver a lista completa do que mudaria. Antes valia "pessoa eleitora" em todo lugar (decisão de 2026-11-18); agora vale a regra abaixo.

| Onde | Termo |
|---|---|
| Menu da página da eleição | `perguntas (2) \| eleitores e cédulas \| curadoria (1) \| administradores` |
| Rótulos, botões, menus, listas, contagens e avisos curtos (45 textos do `django.po`) | eleitor, eleitores ("Contatar os eleitores", "3 eleitores", "enviar e-mail aos eleitores") |
| Verificador (7 textos do `verifier.po`) | "Eleitor #1", "lista de eleitores". A frase longa do login do verificador continua com "pessoa eleitora" |
| Frases explicativas do sistema (ajuda dos formulários, avisos, e-mails, 18 textos) | continua "pessoa eleitora" |
| Página que o link `curadoria` abre | "Curadoria" e "Curadoria de X". O resto das telas da pessoa curadora continua "pessoa curadora" |
| Documentos e páginas fixas (manual, "Como o Helios funciona", FAQ, privacidade, sobre, `docs/docker.md`, glossário, estilo) | eleitor, eleitores. "Pessoa curadora" e "pessoa administradora" continuam; os nomes de botões e links citados seguem a tela |
| "Pessoa administradora" | não mudou, fora o item do menu |

- **Junto dos botões:** as duas confirmações de remover eleitores ("Tem certeza de que quer remover TODOS os N eleitores?") mudaram, para combinar com o botão "remover todos os eleitores".
- **Arquivos gerados:** `heliosverifier/js/strings.pt-BR.js` foi refeito com `python3 tools/po2js.py pt_BR --po locale/pt_BR/LC_MESSAGES/verifier.po --out heliosverifier/js/strings.pt-BR.js`.
- **Testes:** `helios/test_ptbr.py` confere o menu ("eleitores e cédulas", "curadoria (") e as contagens ("1 eleitor", "2 eleitores").
- **Imagens do manual:** as 20 imagens foram refeitas com os novos nomes (mesma eleição da seção 15). O manual ganhou "Clique em **curadoria**" no passo 5.
- **Resolvido na Fase C (seção 18):** a página do item `administradores` agora se chama "Administradores de X".


## 17. Vocabulário dos outros projetos e página "Tradução" (2026-11-19)

**Varredura dos projetos em português.** Estudamos cinco repositórios: `shirlei/helios-server`, `labsec/helios-server`, `ifsc/helios-server`, `ufscar/helios-server` e `STI-UFMA/helios-server-main`. Resumo:
- É uma tradução só. O catálogo `django.po` (cerca de 580 textos) é o mesmo nos cinco, com no máximo 12 linhas diferentes (nomes das instituições e "Voter ID"). O `ufscar` é cópia idêntica do `shirlei`.
- A cabine, o verificador, os e-mails e as telas de ajuda foram escritos em português direto nos arquivos, sem o inglês original. O catálogo de cada projeto cobre 42% dos textos do nosso (os outros são do Helios mais novo).
- Todos partem do Helios antigo (Django 1.11, Celery). Trazem manuais em português (`ajuda`, `ajuda-gestor`, em mkdocs).
- Eles dizem "apuradores" para trustee. Nós mantivemos "pessoa curadora" e "curadoria".

**Termos adotados deles (decisão de 2026-11-19):** eleitor, cédula, depositar (a cédula), questão e ID do eleitor. O resto fica como estava (pessoa curadora, curadoria, administradores, congelar a urna, apuração, consulta e outros). Resumo do que mudou:
- **Depositar:** "enviar a cédula" virou "depositar a cédula" onde a palavra em inglês é "cast": botão "DEPOSITAR esta cédula", "autenticar & depositar a cédula", "Voto depositado com sucesso!", "voto depositado", "cédulas depositadas", o e-mail de confirmação ("Seu voto em X foi depositado") e a cabine. "Enviar" ficou para o que não é votar: e-mail, arquivo, o passo "(3) Enviar" da cabine.
- **Questão:** "pergunta" virou "questão" em todo lugar (menu `questões (2)`, "Questão #1", cabine, verificador, documentos). Só o título "Perguntas frequentes" (FAQ) ficou.
- **ID do eleitor:** o "login" de quem vota virou "ID do eleitor" (formulário de votação, coluna da lista de eleitores, e-mails, avisos, reenvio de credenciais, CSV). O "Login" de quem administra (tela de login por senha) continua "Login".
- **Eleitor no lugar de "pessoa eleitora":** agora em todos os textos do catálogo, da ajuda dos formulários, dos avisos, e-mails, verificador e documentos. "Pessoa eleitora" só ficou onde o texto fala com quem lê e precisaria de "eleitor(a)": "Você entrou como pessoa eleitora X", "que não é uma pessoa eleitora desta eleição" e, no verificador, "Você pode entrar como pessoa eleitora cadastrada".

**Página "Tradução".** Novo item no topo, ao lado de "Sobre o Helios" (só em português; em inglês o topo fica igual ao original). Endereço `/translation`; arquivos `server_ui/templates/translation.pt-BR.html` e `translation.html` (inglês, curto), rota em `server_ui/urls.py` e view em `server_ui/views.py`. A página conta o nosso trabalho (o que foi traduzido, como, vocabulário) e agradece aos cinco projetos acima, com link para cada um, ao Helios e ao Ben Adida. Testes em `helios/test_ptbr.py`.

**Imagens do manual** refeitas de novo (21 imagens), agora com o menu "questões / eleitores e cédulas / curadoria / administradores", "ID do eleitor", "depositar", a barra de cima com "Tradução" e sem barra de rolagem.

**Ficou aberto:** a página que o item `administradores` abre ainda se chama "Pessoas administradoras de X".

## 18. Fases que faltam (2026-11-19)

Lista para revisar com o usuário. A ordem é a de hoje, e cada fase pode mudar de lugar.

| Fase | O que é | Situação |
|---|---|---|
| A | **Imagens dos tutoriais.** Feita em parte: o exemplo agora usa nomes brasileiros (seção 19). O **formato** das imagens (capturas inteiras da tela) continua o mesmo, e o usuário pode pedir outro depois. | Em revisão |
| B | **Documentação do repositório.** O repositório quase não tem documentação própria. Decidir entre a wiki do GitHub (fica fora do código, sem PR) e `docs/` com GitHub Pages (entra em PR e acompanha o código). Os manuais `ajuda` e `ajuda-gestor` dos outros projetos em português (mkdocs, licença Apache-2.0) podem servir de base. | A decidir |
| C | **Termos.** Feita em 2026-11-19: a página do item `administradores` agora se chama "Administradores de X" (título e `<title>`). O resto dos textos de administração continua "pessoa administradora". "Apurador" (usado pelos outros projetos e pela UFU) foi considerado, e ficou "pessoa curadora" e "curadoria". | Feita |
| D | **Página `/privacy`.** Feita em 2026-11-19 (seção 20): texto próprio, conferido com o código, e configurável por quem opera a instância. As regras de proteção de dados seguem o regramento da unidade; o que não for preenchido fica no texto padrão. Não há revisão jurídica do projeto: cada instituição confere o que vale para ela. | Feita |
| E | **PR da correção da apuração (`iterator`)** para o Ben: Issue já aberta, falta a branch a partir da `ben-master`, o teste e a nova medição (923 MiB, antes 15,5 GiB). | A fazer |
| F | **Docker:** requeue das tarefas presas ao subir o `worker`, `GUNICORN_TIMEOUT`, `stop_grace_period` maior e limites de memória (estes só depois do PR da fase E). | A fazer |
| G | **Antes do Release:** religar o CI automático, atualizar as versões das actions e fazer o merge com o Ben (`docs/atualizar-upstream.md`). | Por último |

Itens do Helios que não são tradução e ficaram só registrados (código do Ben): envio depois do fim da votação sem aviso, data de fim antes do início aceita, login repetido ou com espaço no CSV, página 404 com `lang="en"` e a senha de quem administra guardada em texto. A #17 (idioma do e-mail por eleição) é função nova e fica para depois.

## 19. Exemplo do tutorial com nomes brasileiros (2026-11-19)

As 22 imagens de `docs/images/manual/pt-BR/` e o texto do `docs/pt-BR/manual-do-usuario.md` passaram a usar um exemplo brasileiro, no lugar do "Riverside Club" do manual em inglês.

| Parte | Exemplo |
|---|---|
| Eleição | "Eleição do Clube de Leitura 2026" (`clube-leitura-2026`), e-mail de ajuda `ajuda@exemplo.org` |
| Questão 1 (de 0 a 2 opções) | "Quais autores vamos ler no próximo semestre?": Machado de Assis, Graciliano Ramos, Cora Coralina, Clarice Lispector (só autores falecidos) |
| Questão 2 (Sim ou Não) | "Aprovar a compra de livros para a biblioteca do clube?" |
| Eleitores | João da Silva, José dos Santos, Ana Maria Souza, Maria José Pereira |
| Administração | Francisca (criou a eleição) e Luiz (outro administrador) |
| Curadoria | Helios, Paulo, Gabriel, Juliana e Antônia (as quatro geraram a chave e decifraram, de verdade) |
| Votos | João: Machado e Clarice, Sim. José: Machado e Cora, Sim. Ana: Machado, Não. Maria José: Graciliano e Cora, Sim |
| Resultado | Machado 3, Cora 2, Graciliano 1, Clarice 1; Sim 3, Não 1 |

- Novo: a imagem e uma seção "Outros administradores (opcional)" no manual, com a tela de administradores.
- A curadoria do exemplo tem quatro pessoas de verdade, então a apuração só termina depois que as quatro decifram.
- Os scripts que fazem as imagens ficam em `tools/imagens_manual/` (com `LEIAME.md`). Eles precisam de Chrome com CDP e da instância Docker; não rodam nos testes.
- Os e-mails do exemplo usam `exemplo.org`. O domínio não é um dos reservados para exemplos (`example.org` é), e só serve de ilustração.

## 20. Página de privacidade (2026-11-19, fase D)

A `/privacy` era a tradução do texto de heliosvoting.org, escrito como se "nós" fôssemos esse serviço. Conferimos cada frase com o código e achamos o que não batia:

| Texto antigo | Realidade |
|---|---|
| "Não usamos rastreadores, exceto botões de compartilhar do Facebook e do Twitter" | Não existe nenhum botão desses nas telas. Saiu. |
| "Para administrar, entre com Google, Facebook, Yahoo ou Twitter" | No Docker é login e senha, LDAP ou o que a instituição ligar. |
| "Envie um e-mail para nós" (`help@heliosvoting.org`) | Era o endereço do Helios do Ben. |
| "Os dados do voto (de onde, quando) podem ser fornecidos à administração" | Verdade em parte: o IP de cada cédula (`cast_ip`) fica no banco, mas nenhuma tela o mostra. |
| Sem menção | A senha de votação fica guardada no banco, e não só um resumo, para poder ser reenviada. O e-mail de quem saiu da lista também fica guardado. |
| "O Helios nunca tem acesso às suas credenciais nesses serviços" | Vale para Google e GitHub. No LDAP o Helios recebe usuário e senha só para conferir, e não os guarda (conferido em `ldapauth.py`). |

**O que mudou.** `server_ui/templates/privacy.pt-BR.html` foi reescrito, com: quem é a controladora e o contato; uma tabela do que fica guardado, para quê e quem vê; as seções para quem vota e para quem administra (já corrigidas); segurança; finalidade, base legal e prazo; e os direitos do art. 18 da LGPD. O original em inglês (`privacy.html`) não mudou.

**Configurável, sem decidir pelos outros.** O repositório não pertence a nenhuma instituição. Cada utilizador preenche, no `.env`, `PRIVACY_CONTROLADOR`, `PRIVACY_CONTATO_EMAIL`, `PRIVACY_ENCARREGADO`, `PRIVACY_ENCARREGADO_EMAIL`, `PRIVACY_BASE_LEGAL`, `PRIVACY_RETENCAO` e `PRIVACY_REGRAS_URL` (`settings_ptbr.py`, `.env.example`). Vazias, o texto padrão diz que as regras são as do regramento da unidade responsável. O contato cai no `HELP_EMAIL_ADDRESS` (menos o do Ben). Os valores são texto simples e saem escapados. Guia: `docs/privacidade.md`.

**Testes:** `helios/test_ptbr.py` (página padrão, página preenchida, HTML escapado, nada de Facebook, Twitter ou Yahoo) e `tools/test_settings_ptbr.py` (variáveis).

**Limite:** o texto descreve o sistema e não é aconselhamento jurídico. Base legal, prazo e encarregado ficam com quem opera.


## 21. Apuração em lotes (`iterator`) no `ptbr`

Decisão final: a correção foi enviada ao Ben como [PR #568](https://github.com/benadida/helios-server/pull/568). A `ptbr` **não** carrega a mudança: `Election.compute_tally` fica igual ao código do Ben (`ben-master`). Quando o PR for aceito, a correção volta pelo merge da `ben-master`, sem conflito. Até lá, a `ptbr` tem o consumo alto de memória na apuração.
- Os marcadores `HELIOS-PTBR-INICIO/FIM` e o teste `helios/test_apuracao.py` foram removidos.
- Medições antes e depois: `docs/relatorio-carga.md`. Com 50 mil eleitores o pico caiu de 9,5 GiB para 174 MiB, com resultado idêntico.


## 22. Manuais em `docs/pt-BR/` e troca para "apurador"

**Manuais novos.** A pasta `docs/pt-BR/` ganhou um `README.md` e uma pasta por papel: `gestor/`, `eleitor/`, `apurador/` e `fiscal/`, cada uma com o seu `README.md`. Os 15 estão escritos: 6 do gestor, 3 do apurador, 4 do eleitor e 2 do fiscal. As capturas ficam em `imagens/` de cada pasta (31 arquivos), feitas no Docker com o exemplo brasileiro, os e-mails no Mailpit em tema claro e as telas novas de apurador, auditoria e verificadores. Os scripts estão em `tools/imagens_manual/` (`passo5.py` e `passo6a` a `6c`). Achado: o link `/helios/elections/single_ballot_verifier` do Ben abre um template que não existe; o verificador de cédula única está em `/booth/single-ballot-verify.html` (e `.pt-BR.html`). Os arquivos do Ben em `docs/` ficam intactos, e o passo de conferir `docs/` na `ben-master` entrou em `docs/atualizar-upstream.md`.

**Fatos que os manuais registram.** O Helios não tem quórum: todos os apuradores precisam decifrar. Não tem voto branco nem nulo próprios: o branco é o "0 a n" sem marcar nada, e o nulo, se existir, é uma opção comum (A, B e Nulo numa questão 1 a 3 vale como voto para A, B e Nulo). Testado no Docker.

**Troca de termo (decisão de 2026-11-19).** "Pessoa curadora" e "curadoria" viraram "apurador" e "apuradores" em `django.po` (47 textos), `verifier.po` (5), páginas fixas (FAQ, privacidade, Tradução), manual, "Como o Helios funciona", glossário, guia de estilo, testes e scripts das imagens. O menu da eleição diz `apuradores (n)`, e a página dele, "Apuradores de X". Este diário não foi reescrito: as seções anteriores falam em "curadoria" porque era o termo da época. As imagens do manual antigo ainda mostram "curadoria" e serão refeitas na fase das capturas.


## 23. Fase F: requeue ao subir o `worker` e `GUNICORN_TIMEOUT`

**Problema.** Se o `worker` morre no meio de uma tarefa (falta de memória, queda, reinício além do `stop_grace_period` de 5 minutos), a tarefa fica `RUNNING` para sempre e a eleição parece parada na apuração. O comando `requeue_stuck_tasks` do Ben resolve, mas só na mão e só para tarefas com mais de 120 minutos.

**Mudanças (só no Docker, o código do Ben não mudou).**
- `docker-compose.yml`, `worker`: roda `requeue_stuck_tasks --older-than 0` antes do `db_worker`. **Só é seguro com um único `worker`**, e isso está dito no compose e em `docs/docker.md` (seção "Tarefas presas e tempo limite").
- `docker-compose.yml`, `web`: `--timeout ${GUNICORN_TIMEOUT:-120}` (o padrão do gunicorn é 30 s). Novo `GUNICORN_TIMEOUT` em `.env.example`.

**Teste no Docker.** Com uma tarefa `election_notify_admin` e uma `voters_email` marcadas como `RUNNING` no banco, o `worker` reiniciou e escreveu `not requeued: ... voters_email` e `requeued 1 tasks`. A `notify_admin` foi refeita com sucesso, e a `voters_email` ficou como estava. O processo do `web` sobe com `--timeout 120`.

**Não feito (de propósito).** Limites e reservas de memória: depois da correção do `iterator` (PR #568), com a issue de estudo. Também não medi o `combine_decryptions` numa eleição grande, e é por isso que o timeout subiu para 120 s sem a medição.


## 24. Endurecimento do Docker e teste de CSV grande

**Mudanças (itens 1 a 7 da análise).** `web`, `worker` e `migrate`: `read_only: true`, `tmpfs` em `/tmp` (`UPLOAD_TMP_SIZE`, 1 GiB), `cap_drop: ALL`, `no-new-privileges`. O `web` usa `--worker-tmp-dir /dev/shm`. A imagem usa `PYTHONDONTWRITEBYTECODE=1` (com `.pyc` prontos, via `--compile-bytecode` e `compileall`) e o usuário `10001:10001`. Redes `back` e `front`: o `caddy` só enxerga o `web`. O `caddy` só mantém `NET_BIND_SERVICE`. Versões fixas: `postgres:16.16-alpine`, `caddy:2.11.9-alpine`, `mailpit:v1.34.0`. A imagem passou de 318 MB para 341 MB (os `.pyc`).

**Teste no Docker.** Os contêineres sobem com `ReadonlyRootfs=true`, `CapEff=0` e `User=10001`. O `web` não grava em `/app` e grava em `/tmp`. O `caddy` alcança o `web` e não o banco. A eleição do manual rodou inteira (criar, questões, CSV de eleitores, apuradores com chave no navegador, congelar, e-mail, votos na cabine, apuração, decifragem, resultado) com o mesmo resultado de antes: Machado 3, Graciliano 1, Cora 2, Clarice 1; Sim 3, Não 1. Sem erros de leitura somente nos logs.

**CSV grande.** Tabela e leitura em `docs/docker.md` ("CSV grande de eleitores"). O gargalo é o processamento no `worker` (4,8 ms por eleitor com 100 mil, 8 min), não o envio nem a memória. `tools/imagens_manual/passo7.py` repete a medição.

**Ficou de fora, por decisão sua:** CSP, digest das imagens, segredos em arquivo, log de acesso, limite de tentativas de login, cabeçalhos e limites do Caddy (itens 8 e 9). Fica em aberto: o que acontece se o `worker` reinicia no meio do processamento de um CSV gigante (o requeue refaz a tarefa; não testei se os eleitores já gravados atrapalham).
