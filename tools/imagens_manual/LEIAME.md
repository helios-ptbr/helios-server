# Imagens do manual

Scripts que refazem as imagens de `docs/images/manual/pt-BR/` com a eleição de exemplo do manual
("Eleição do Clube de Leitura 2026"). Não fazem parte do Helios nem dos testes.

## O que precisa
- Instância Docker no ar com `DEBUG=1`, `AUTH_ENABLED_SYSTEMS=password` e
  `WELCOME_MESSAGE=Bem-vindo ao Helios, eleições online seguras.` no `.env` (portas 8443 e 8025 do Mailpit).
- Chrome aberto com `--remote-debugging-port=9222`. Os scripts abrem só abas novas, em contexto isolado.
- `pip install websocket-client`.
- As contas de quem administra, criadas com o comando `criar_administrador` (senha `alice-senha-1` nos scripts, é de teste):

```
for u in "francisca@exemplo.org|Francisca" "francisca-inicio@exemplo.org|Francisca" "luiz@exemplo.org|Luiz"; do
  docker compose exec -T -e HELIOS_SENHA='alice-senha-1' web python manage.py criar_administrador "${u%%|*}" --nome "${u##*|}"
done
```
- Se já existir uma eleição `clube-leitura-2026`, troque o nome curto dela antes (o Helios não repete).

## Ordem
Rode da pasta `tools/imagens_manual`:

1. `python3 passo1.py`: página inicial, nova eleição, questões, eleitores, apuradores e administradores.
2. `python3 passo2.py`: cada pessoa dos apuradores gera a chave e envia a chave pública (guarda as chaves secretas em `chaves_secretas.json`, que **não** deve ir para o git).
3. `python3 passo3.py`: congela, envia o e-mail e vota na cabine com os quatro eleitores.
4. `python3 passo4.py`: apuração, decifragem pelos apuradores, resultado e páginas públicas.

Cada passo leva de 1 a 2 minutos. Os arquivos `manual.json`, `trustees.json`, `links_apuradores.json`, `senhas.json` e
`chaves_secretas.json` ficam na pasta de onde você rodar (não os versione).

Os textos que os scripts clicam ("Adicionar a questão", "Próximo", "Congelar", "Enviar") são os da interface em pt-BR.
Se um deles mudar, o script para com um erro.

## Capturas dos manuais por papel (`docs/pt-BR/<papel>/imagens/`)

Rode depois dos passos 1 a 4, com `OUT_DIR=/caminho/da/pasta` para escolher onde as imagens caem (sem isso, elas vão para
`docs/images/manual/pt-BR/`). Depois, copie cada imagem para a pasta do papel e use o Pillow para recortar a
`verificador-eleicao.png` (a página é longa).

5. `python3 passo5.py`: e-mails no Mailpit em tema claro (`mp-theme=light`) e o verificador da eleição inteira.
6. `python3 passo6a.py`, `passo6b.py` e `passo6c.py`: uma eleição de demonstração (`clube-demo`) com um apurador, para as
   telas de gerar a chave, de auditoria na cabine (anular e auditar, publicar), de cédulas auditadas, do verificador de
   cédula única e da decifragem. O `demo.json` e o `trail.json` guardam a chave secreta de teste e a cédula auditada: não os versione.

## Recorte e marcas numeradas (`anotar.py`)

Os passos acima geram **capturas brutas** (a tela inteira, com menu e rodapé). As imagens que entram nos manuais são
as capturas já recortadas, com todas na mesma largura (1013 px) e com círculos numerados nos elementos que o texto cita.
Quem faz isso é o `anotar.py`.

Junte as 33 capturas brutas em uma pasta (os nomes são os das chaves de `DESTINOS` no `anotar.py`, por exemplo
`freeze.png`, `booth-review.png`, `email-eleitor.png`) e rode, da raiz do repositório:

```
python3 tools/imagens_manual/anotar.py PASTA_DAS_CAPTURAS_BRUTAS --legendas
```

- Ele grava cada imagem nos dois lugares em que ela aparece (`docs/images/manual/pt-BR/` e `docs/pt-BR/<papel>/imagens/`).
- `--so freeze.png` refaz só uma. `--saida PASTA` grava fora do repositório, para conferir antes.
- `--legendas` escreve, sob cada imagem dos manuais, a linha "Na imagem: (1) ... (2) ...", a partir de `LEGENDAS`.
- As caixas das marcas (`MARCAS`) estão em pixels da captura bruta. Se uma tela mudar de lugar, ajuste a caixa,
  confira com `--saida` e rode de novo. O `anotar.py` precisa do Pillow (`pip install pillow`).
- Ao mudar uma marca, mude também a legenda dela em `LEGENDAS`: o número de itens deve ser o mesmo.
- As capturas brutas não vão para o git (os `passo*.py` as refazem).

## Capa do README (`capa.py`)

A imagem do topo do `README.md` (`docs/images/capa.png`) tem a logo do Helios e duas capturas **sem marcas**: a cabine
(`booth-question.png`) e o resultado público (`results-public.png`). Para refazer:

```
python3 tools/imagens_manual/capa.py PASTA_DAS_CAPTURAS_BRUTAS
```
