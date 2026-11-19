# Documentação do Helios em português

Estes manuais são do fork `helios-ptbr`. Eles são nossos: os arquivos do Ben Adida em `docs/` ficam como estão.

Escolha o seu papel na eleição.

| Papel | O que faz | Manuais |
|---|---|---|
| Gestor da eleição | Cria a eleição, as questões e a lista de eleitores, e libera o resultado | [gestor/](gestor/README.md) |
| Eleitor | Vota, deposita a cédula e confere o voto | [eleitor/](eleitor/README.md) |
| Apurador | Guarda uma parte da chave e a usa na apuração | [apurador/](apurador/README.md) |
| Fiscal | Verifica que a eleição foi honesta, sem precisar de senha | [fiscal/](fiscal/README.md) |

## Antes de começar

- O Helios **não tem quórum**. Se há 5 apuradores, os 5 precisam decifrar. Se um perder a chave, o resultado não abre.
- O Helios **não tem voto branco nem nulo** como opção própria. Veja [gestor/02-questoes.md](gestor/02-questoes.md).
- Palavras como "urna", "congelar" e "cédula" estão em [../glossario.md](../glossario.md).

## Outros documentos

- [Manual do usuário](manual-do-usuario.md) (visão geral, em um arquivo só)
- [Como o Helios funciona](como-o-helios-funciona.md)
