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
- #21 varredura de telas: feita para eleição e site, e as páginas longas já estão traduzidas (seção 12). Falta só cobrir login, opt-out e telas da pessoa curadora na varredura.
- #23 plurais feitos (seção 12). Separador de milhar: mantido sem (decisão do usuário).
- #23 resto da rodada de localização (números, plurais, ordenação).
- Teste real da pessoa curadora externa (chave secreta e decifragem) e do opt-out no navegador: não feitos.

## 12. Páginas longas e plurais (issues #21 e #23)

- `/about`, `/faq`, `/privacy` e `/docs` têm um template por idioma: `server_ui/templates/<nome>.pt-BR.html`. Motivo: são textos longos, e marcar com `{% trans %}` geraria conflito de merge com o Ben. O `server_ui/view_utils.py` (`render_template`) procura `<nome>.<idioma>.html` e, se não achar, usa o original. Em inglês nada muda.
- Cada página traduzida mostra o aviso "Tradução não oficial" (`server_ui/templates/aviso_traducao.html`), com link para o fork, para o Helios de Ben Adida e para a versão original em inglês (`vote.heliosvoting.org/<página>`).
- `/docs` aponta para a tradução do manual e de "Como o Helios funciona" (`docs/pt-BR/manual-do-usuario.md` e `docs/pt-BR/como-o-helios-funciona.md`), cada uma com link para o original em inglês. A arquitetura segue só em inglês. As imagens do manual estão na interface em inglês.
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
