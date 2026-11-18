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
| `helios/test_ptbr.py` | renderização em pt-BR e em inglês, e-mails, telas da curadoria, varredura que procura inglês nas telas da eleição |
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
- Previsto: o CI falhar se o `.po` estiver desatualizado ou com `msgid` sem tradução ou `fuzzy` (issues #18 a #21).

## 10. Achados no código do Ben (não alterados)

1. `helios/views.py`, perto da linha 344: `election.voting_has_started` sem `()`, então a condição é sempre verdadeira. Só afeta o texto de status ("Vote in" no lugar de "Register to vote in").
2. Texto de data com deslocamento (`...Z` ou `-03:00`) é guardado como horário da Califórnia (`TIME_ZONE=America/Los_Angeles`, `USE_TZ=False`): `14:00Z` vira 06:00. O navegador nunca envia isso. Só um pedido feito à mão cai nesse caso.

## 11. Pendências (issues abertas)

- #17 idioma do e-mail por eleição (hoje vem do `LANGUAGE_CODE`).
- #18 a #21 CI do `.po`, placeholders e varredura de todas as telas.
- #23 resto da rodada de localização (números, plurais, ordenação).
- #25 Dockerfile multi-stage e `docker-compose`.
- Teste real da pessoa curadora externa (chave secreta e decifragem) e do opt-out no navegador: não feitos.
