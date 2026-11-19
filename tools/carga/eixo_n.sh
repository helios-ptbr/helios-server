#!/bin/bash
# Eixo N (eleitores), linha de base: 3 questões de 5 opções, 1 apurador, 1 administrador.
cd "$(dirname "$0")/../.." || exit 1
for n in ${NS:-10 100 500 1000 2000 5000 10000 20000}; do
  python3 tools/carga/medir.py "{\"cenario\":\"n$n\",\"n\":$n,\"q\":3,\"opcoes\":5}"
  echo "FIM n=$n $(date +%T)"
done
