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
