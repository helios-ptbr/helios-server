#!/bin/bash
# Percorre a matriz do PLANO.md. Retomável: medir.py pula cenário já no CSV.
cd "$(dirname "$0")/../.." || exit 1
M="python3 tools/carga/medir.py"
r() { $M "$@"; echo "FIM $1 $(date +%T)"; }
# 1. eixo N restante (extrapolação do 'antes': 30000 ~5,8 GiB, 50000 ~9,6 GiB; cabe nos 31 GiB)
for n in 30000 50000; do r "{\"cenario\":\"n$n\",\"n\":$n,\"q\":3,\"opcoes\":5}"; done
# 2. eixo Q (1 a 5), N=1000 e N=10000
for n in 1000 10000; do for q in 1 2 3 4 5; do
  r "{\"cenario\":\"q${q}_n$n\",\"n\":$n,\"q\":$q,\"opcoes\":5}"; done; done
# 3. tipo de questão (min 0/1, max 1/x; 2, 5, 18 opções), Q=3, N=1000
for mn in 0 1; do for mx in 1 todas; do for o in 2 5 18; do
  r "{\"cenario\":\"tipo_min${mn}_max${mx}_o${o}\",\"n\":1000,\"q\":3,\"opcoes\":$o,\"min\":$mn,\"max\":\"$mx\"}"; done; done; done
# 4. randomização (afeta só a cabine; confirma que não pesa na apuração)
r '{"cenario":"rand_nenhuma","n":1000,"q":3,"opcoes":5,"rand":false}'
r '{"cenario":"rand_eleicao","n":1000,"q":3,"opcoes":5,"rand":true}'
# 5. apuradores e administradores, com decifragem por apurador
for n in 1000 10000; do for a in 1 2 3 5 10; do
  r "{\"cenario\":\"apur${a}_n$n\",\"n\":$n,\"q\":3,\"opcoes\":5,\"apuradores\":$a}" --decifrar; done; done
for a in 1 2 3 5 10; do
  r "{\"cenario\":\"adm${a}_n1000\",\"n\":1000,\"q\":3,\"opcoes\":5,\"admins\":$a}"; done
echo MATRIZ_COMPLETA
