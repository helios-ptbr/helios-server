# Como atualizar com o código do Ben Adida

Este repositório é um fork não oficial. Não enviamos PRs de tradução para o
`benadida/helios-server`. Tudo fica aqui.

## Remotos

| Remoto | Repositório |
|---|---|
| `origin` | `helios-ptbr/helios-server` (nosso) |
| `upstream` | `benadida/helios-server` (do Ben) |

Se faltar o `upstream`:

```
git remote add upstream git@github.com:benadida/helios-server.git
```

## Branches

| Branch | O que tem | Quem mexe |
|---|---|---|
| `master` | Cópia exata do `upstream/master` | Só `fetch` e `merge --ff-only` |
| `ptbr` | `master` + as traduções | Nós |
| `tr/<assunto>` | Trabalho pequeno, volta para `ptbr` por PR | Nós |

Nunca faça commit direto no `master`.

## Passo a passo

1. Atualize o `master`:

```
git fetch upstream
git switch master
git merge --ff-only upstream/master
git push origin master
```

2. Traga as mudanças para o `ptbr`:

```
git switch ptbr
git merge master
```

3. Se houver conflito, resolva à mão, depois `git add` e `git commit`.
   Use `merge`, não `rebase`: várias pessoas usam o `ptbr`, e o `rebase`
   reescreve o histórico.

4. Confira as traduções (ferramentas em `tools/`):

```
python3 -m unittest tools.test_booth_i18n
```

5. Envie:

```
git push origin ptbr
```

## Se o `--ff-only` falhar

Alguém fez commit no `master`. Ele deve ser igual ao `upstream/master`.
Pare e avise o grupo antes de mexer.
