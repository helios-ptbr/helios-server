# Guia de estilo da tradução pt-BR

Vale para todo texto traduzido: telas, cabine, e-mails e mensagens.
Os termos técnicos ficam no glossário (`docs/glossario.md`, issue #4).

## Tratamento

- Use **você**. Nunca "o senhor/a senhora" e nunca "tu".
- Fale direto com a pessoa: "Você precisa selecionar..." e não "É necessário selecionar...".
  Em avisos e passos, a forma impessoal é aceita se ficar mais curta e clara.

## Gênero

- Evite palavras que marcam gênero para a pessoa que lê.
  - "Quando tudo estiver certo" e não "Quando estiver satisfeito(a)".
  - "O sistema vai orientar você a..." e não "Você será orientado(a) a...".
- Para papéis e cargos, use **"pessoa" + adjetivo ou substantivo**, que concorda com "pessoa":

  | Em vez de | Use |
  |---|---|
  | eleitor | pessoa eleitora |
  | candidato | pessoa candidata |
  | administrador | pessoa administradora |
  | usuário | pessoa usuária |
  | curador (trustee) | pessoa curadora |
  | os eleitores | as pessoas eleitoras |
  | todos | todas as pessoas |

- Se "pessoa + papel" ficar pesado, reescreva a frase. Exemplos: "quem vota", "quem administra", "quem se candidata".
- Evite o masculino genérico ("os eleitores", "todos"). Não use "(a)", "@", "x" ou "e" para neutralizar.
- Use as formas acima no glossário (`docs/glossario.md`). Se o papel não estiver lá, pergunte.

## Tom

- Claro, curto e neutro. É uma votação: nada de gíria, humor ou exclamação.
- Frases na voz ativa. Um assunto por frase.
- Nos avisos de erro, diga o que houve e o que fazer.

## Termos

- Um termo em inglês tem **uma** tradução em todo o sistema. Veja o glossário.
- Não traduza nomes próprios: Helios, Heliosvoting, nomes de arquivos, URLs e e-mails.
- Traduza o botão e o texto que o cita do mesmo jeito. Exemplo: o botão "voltar à votação" e o texto que diz "voltar à votação".

## Escrita

- Acentos e cedilha sempre. Siga o Acordo Ortográfico em vigor.
- Aspas duplas retas (`"`) nos textos do código. Não use aspas curvas.
- Reticências são três pontos (`...`), como no original.
- Datas: `dd/mm/aaaa`. Horas: `14:30`. Veja a issue de localização.
- Não deixe espaço antes de `:`, `;`, `?`, `!`.
- Mantenha as variáveis exatamente como estão: `%(nome)s`, `{nome}`, `{$T.x}`.
  Os testes falham se elas mudarem.
- Mantenha as tags HTML e as quebras `\n` do original.

## Em dúvida

Abra uma issue com a etiqueta `traducao` e escreva as duas opções.
A decisão vira uma linha aqui ou no glossário.
