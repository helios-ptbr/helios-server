# Glossário de termos

Uma tradução por termo, em todo o sistema. Siga também o `docs/estilo.md`.

Situação: **em uso** (já aparece nas traduções), **proposta** (sugestão para revisar) ou
**decidir** (precisa de uma decisão do grupo antes de traduzir).

## Pessoas

| Inglês | pt-BR | Situação | Observação |
|---|---|---|---|
| voter | eleitor, eleitores | em uso | Decidido em 2026-11-19. Vale em todo lugar: rótulos, botões, menus, listas, contagens, avisos, ajuda dos formulários, e-mails, verificador e documentos. **"Pessoa eleitora"** fica só onde o texto fala com quem lê e precisaria de "eleitor(a)": "Você entrou como pessoa eleitora X", "que não é uma pessoa eleitora desta eleição" e, no verificador, "Você pode entrar como pessoa eleitora cadastrada". Antes disso valia "pessoa eleitora" em todo lugar. |
| voter list | lista de eleitores | em uso | |
| election administrator, admin | pessoa administradora | em uso | Só o item do menu da página da eleição diz "administradores" (decidido em 2026-11-19). |
| trustee | pessoa curadora | em uso | Quem guarda parte da chave secreta e ajuda a abrir a apuração. Decidido em 2026-11-18. O item do menu da página da eleição e a página que ele abre dizem "curadoria" (2026-11-19); no resto fica "pessoa curadora". Descartado: "fiscal", porque no Brasil é quem observa a votação (fiscal de partido) e não guarda chave, e porque se confundiria com "auditar" e "cédulas auditadas". Outras opções vistas: custodiante da chave, pessoa fiduciária, pessoa guardiã. |
| candidate | pessoa candidata | proposta | O Helios chama a opção de "answer"; veja abaixo. |
| user | pessoa usuária | proposta | |

## Votação

| Inglês | pt-BR | Situação | Observação |
|---|---|---|---|
| election | eleição | em uso | Tipo "referendum" (campo `election_type`): **consulta**. Os dois são femininos, então "esta %(etype)s" e "%(etype)s privada" concordam. |
| question | questão | em uso | Decidido em 2026-11-19, como nos outros projetos em português do Helios. Só o título "Perguntas frequentes" (FAQ) fica como está. |
| answer, choice, option | opção | proposta | Em "selections out of possible", usamos "seleções". |
| ballot | cédula | em uso | |
| vote (noun) | voto | em uso | |
| to vote | votar | em uso | |
| to cast a ballot | depositar a cédula | em uso | Decidido em 2026-11-19, como nos outros projetos em português do Helios. O botão e os textos que o citam usam a mesma palavra ("DEPOSITAR esta cédula", "voto depositado", "cédulas depositadas"). "Enviar" fica para o que não é votar: enviar e-mail, enviar arquivo, "(3) Enviar" da cabine. |
| voting booth | cabine de votação | em uso | |
| ballot tracker, tracking number | código de rastreamento | em uso | Texto: "código de rastreamento da sua cédula". |
| tracking center | centro de rastreamento | em uso | |
| preview | prévia | em uso | |
| eligibility | elegibilidade | em uso | |
| to tally | apurar | em uso | "tally" (noun): apuração. |
| result | resultado | proposta | |
| freeze ballot | congelar a urna | em uso | Texto: "congelar a urna e abrir a eleição". Aqui "ballot" é o conjunto da votação (perguntas e lista de eleitores), não uma cédula. |
| ballot box | urna | proposta | O lugar onde ficam as cédulas cifradas. |
| opt out (of emails) | deixar de receber e-mails | proposta | Botão: "Não quero receber e-mails". |

## Criptografia e auditoria

| Inglês | pt-BR | Situação | Observação |
|---|---|---|---|
| to encrypt | cifrar | em uso | Substantivo: cifragem. Não alternar com "criptografar". |
| to decrypt | decifrar | proposta | Substantivo: decifragem. |
| public key | chave pública | proposta | |
| secret key, private key | chave secreta | proposta | |
| fingerprint | impressão digital | em uso | Texto: "Impressão digital da eleição". |
| to audit | auditar | em uso | |
| to spoil (a ballot) | anular | em uso | Botão: "Anular e auditar". |
| verifier | verificador | em uso | "verificador de cédulas". |
| proof | prova | proposta | |
| randomness | aleatoriedade | proposta | |

## Interface

| Inglês | pt-BR | Situação | Observação |
|---|---|---|---|
| Select / Review / Submit | Selecionar / Revisar / Enviar | em uso | Os três passos da cabine. |
| Proceed | Prosseguir | em uso | |
| Previous / Next | Anterior / Próximo | em uso | |
| back to voting | voltar à votação | em uso | |
| login, log in | login, fazer login | em uso | |
| voter ID | ID do eleitor | em uso | Decidido em 2026-11-19 (antes era "login"). Vale nos e-mails, na coluna da lista de eleitores, no formulário de votação e nos avisos. |
| username (administração) | login | em uso | Só a tela de login por senha de quem administra. |
| password | senha | em uso | |
| email | e-mail | em uso | Com hífen. |

## Não traduzir

Helios, Heliosvoting, nomes de arquivos, URLs, endereços de e-mail e variáveis
(`%(nome)s`, `{nome}`, `{$T.x}`).
