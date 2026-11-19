# Página de privacidade (`/privacy`)

A página `/privacy` descreve o que o Helios faz com os dados de quem vota e de quem administra. O texto é do projeto
helios-ptbr, baseado na página do Helios original, e foi conferido com o código.

Este repositório não pertence a nenhuma instituição. Por isso, os pontos que dependem de **quem opera a instância**
ficam em aberto, e cada instituição preenche os seus. Sem preencher, a página diz que **as regras são as do regramento
da unidade responsável por esta instância**.

## O que dá para preencher

No `.env` (ou no ambiente), em texto simples e sem HTML. Todas são opcionais.

| Variável | O que é | Se ficar vazia, a página diz |
|---|---|---|
| `PRIVACY_CONTROLADOR` | Nome da unidade que opera a instância (a controladora dos dados) | "uma unidade (a instituição que a coloca no ar)" |
| `PRIVACY_CONTATO_EMAIL` | Contato para dúvidas e pedidos sobre dados | o `HELP_EMAIL_ADDRESS`; sem ele, "o endereço indicado pela unidade" |
| `PRIVACY_ENCARREGADO` | Nome do encarregado pelo tratamento de dados pessoais (LGPD, art. 41) | "a pessoa indicada pelo regramento da unidade" |
| `PRIVACY_ENCARREGADO_EMAIL` | E-mail do encarregado | (some) |
| `PRIVACY_BASE_LEGAL` | Base legal do tratamento, entre as do art. 7º da LGPD | "a definida no regramento da unidade responsável" |
| `PRIVACY_RETENCAO` | Por quanto tempo os dados ficam | "pelo prazo definido no regramento da unidade responsável" |
| `PRIVACY_REGRAS_URL` | Endereço do regramento da unidade (política de privacidade ou norma interna) | (não mostra o link) |

Exemplo:

```
PRIVACY_CONTROLADOR=Universidade Exemplo
PRIVACY_CONTATO_EMAIL=privacidade@exemplo.br
PRIVACY_ENCARREGADO=Maria da Silva
PRIVACY_ENCARREGADO_EMAIL=encarregado@exemplo.br
PRIVACY_BASE_LEGAL=execução de políticas públicas (LGPD, art. 7º, III)
PRIVACY_RETENCAO=cinco anos depois do fim da eleição
PRIVACY_REGRAS_URL=https://exemplo.br/politica-de-privacidade
```

Depois de mudar o `.env`, rode `docker compose up -d` para o `web` ler os valores novos.

## O que a página diz sobre o sistema (e vale para qualquer instância)

- **Dados guardados:** nome, e-mail, ID do eleitor, senha de votação, cédula cifrada, código de rastreamento, hora do voto,
  IP e hora de cada cédula depositada, a conta de quem administra e o e-mail de quem saiu da lista de e-mails.
  A tabela da página diz para que serve cada um e quem pode vê-lo.
- **A senha de votação fica guardada no banco, e não só um resumo dela**, para que o sistema possa reenviá-la. O mesmo vale para
  a senha da conta de quem administra. Quem opera a instância deve proteger o servidor, o banco e os backups.
- **O IP de cada cédula** fica no banco e não aparece nas telas.
- **O Helios não grava log de acesso.** O servidor web (o Caddy do `docker-compose.yml`, um Apache ou outro) pode gravar, e
  isso depende da instalação. Se a sua grava, diga isso no regramento da unidade.
- **Sem rastreadores:** não há anúncios, botões de redes sociais nem cookies de rastreamento. Os cookies são os da sessão e os
  de proteção dos formulários.

## O que não decidimos

A página não é aconselhamento jurídico. O projeto não escolhe a base legal, o prazo de retenção, o encarregado, as regras de
compartilhamento nem as respostas a pedidos de titulares. Isso é de quem opera a instância. Por isso as variáveis acima existem,
e o texto padrão manda a pessoa ao regramento da unidade.

Antes de colocar uma instância no ar para eleições reais, vale que a unidade:

1. preencha as variáveis acima (ou confirme que o texto padrão serve);
2. confira se o que a página diz (e o que o sistema guarda) combina com o regramento dela;
3. defina como atende os pedidos do art. 18 da LGPD, já que a eleição precisa manter parte dos dados para a auditoria.

## Onde mexer no código

- Texto: `server_ui/templates/privacy.pt-BR.html`. O original em inglês (`privacy.html`) continua o do Ben.
- Variáveis: `settings_ptbr.py` (`PRIVACY_*`).
- Testes: `helios/test_ptbr.py` (`test_pagina_de_privacidade_*`).
