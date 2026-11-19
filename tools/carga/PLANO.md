# Plano do teste de memória da apuração (antes e depois do `iterator`)

Objetivo: medir o consumo de `Election.compute_tally` sem e com `.iterator(chunk_size=500)`.
Registro: `docs/relatorio-carga.md` (relatório final) e `tools/carga/resultados/*.csv` (dados brutos).

## Como medir
- Cada medida roda em **processo novo** dentro do contêiner `web` (`manage.py shell`), para o pico (`ru_maxrss`) não vazar entre medidas.
- Variante `antes`: a soma como está no código do Ben. Variante `depois`: com `.iterator(chunk_size=500)`.
- As cédulas são geradas pelo código do Helios (`Voter`, `CastVote`) com **K cédulas distintas repetidas** para N eleitores. O custo da apuração depende do tamanho da cédula e de N, não de elas serem distintas. Gerar N cédulas distintas leva horas.
- Coletado por medida: pico RSS do processo, tempo de relógio, tempo de CPU (user+sys), `docker stats` (CPU e memória do `web`, `worker` e `db`) amostrado a cada 1 s, tamanho do banco (`pg_database_size`), tamanho da tabela de eleitores/cédulas, disco do volume, duração do `combine_decryptions`.
- Igualdade do resultado: `encrypted_tally` de `antes` e `depois` comparados.

## Matriz (não é o produto cartesiano, que daria milhares de execuções)
Linha de base: 3 questões, 1 curador (Helios), 1 administrador, sem randomização, N=1000.

| Eixo | Valores | Fixos |
|---|---|---|
| Eleitores N | 10, 100, 500, 1000, 2000, 5000, 10000, 20000, 30000, 50000 | base |
| Questões Q | 1 a 5 | N=1000 e N=10000 |
| Tipo de questão | mín 0 ou 1, máx 1 ou x; opções 2, 5, 18 | Q=3, N=1000 |
| Randomização | questões e respostas: nenhuma, só questões, só respostas, ambas | Q=3, N=1000 |
| Apuradores | 1, 2, 3, 5, 10 | N=1000 e N=10000 |
| Administradores | 1, 2, 3, 5, 10 | N=1000 |

Parada: quando a extrapolação (ajuste linear do pico por N) passar de ~80% dos 31 GiB, pula os N maiores no variante `antes`.
O variante `depois` roda até 50000 se a extrapolação couber.

## Ordem
1. `tools/carga/gerar.py`: cria eleição e cédulas por parâmetros.
2. `tools/carga/medir.py`: roda uma medida e anexa uma linha ao CSV.
3. `tools/carga/rodar_matriz.sh`: percorre a matriz, retomável (pula linhas já no CSV).
4. Relatório com tabelas e gráfico.
