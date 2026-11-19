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
  | candidato | pessoa candidata |
  | administrador | pessoa administradora |
  | usuário | pessoa usuária |
  | curador (trustee) | pessoa curadora |
  | todos | todas as pessoas |

- **Exceção, decidida em 2026-11-19:** para quem vota, use **"eleitor" e "eleitores"** em todo lugar. **"Pessoa eleitora"** só onde o texto fala com quem lê e precisaria de "eleitor(a)" ("Você entrou como pessoa eleitora X"). O item do menu da eleição que leva à página dos trustees diz "curadoria", e o que leva à página dos administradores diz "administradores". Os outros papéis seguem a regra da tabela acima.

- Se "pessoa + papel" ficar pesado, reescreva a frase. Exemplos: "quem vota", "quem administra", "quem se candidata".
- Fora a exceção de "eleitor" acima, evite o masculino genérico ("todos"). Não use "(a)", "@", "x" ou "e" para neutralizar.
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
