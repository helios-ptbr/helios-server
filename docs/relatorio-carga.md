# Relatório de carga da apuração: antes e depois do `iterator`

Data: 2026-11-19. Máquina: notebook com 20 CPUs e 31 GiB de memória, sem outros programas abertos. Docker Compose (perfil `dev`), PostgreSQL 16.

Dados brutos: `tools/carga/resultados/medidas.csv` (96 linhas, uma por cenário e variante). Plano: `tools/carga/PLANO.md`. Rotinas: `tools/carga/gerar.py`, `variante.py`, `medir.py` e `rodar_matriz.sh`.

## O que foi comparado

A soma cifrada da apuração (`Election.compute_tally`, em `helios/models.py`):

- **antes:** `for voter in self.voter_set.exclude(vote=None)`, como está no código do Ben. O Django carrega todos os eleitores e cédulas na memória.
- **depois:** o mesmo laço com `.iterator(chunk_size=500)`.

## Como foi medido

- Cada medida roda em **processo novo** dentro do contêiner `web`. O pico é o `ru_maxrss` do processo.
- A soma não grava nada no banco, para as duas variantes serem comparáveis. O SHA-1 do resultado foi comparado: **as duas variantes deram o mesmo resultado em todos os 48 cenários**.
- Também coletados: tempo de relógio e de CPU, pico de memória e de CPU de `web`, `worker` e `db` (`docker stats` a cada 1 s), memória livre mínima do notebook, tamanho do banco, da tabela de cédulas e da de eleitores, tempo de geração das cédulas e, nos cenários de apuradores, o tempo de `compute_tally` e da decifragem de cada apurador.
- As cédulas são geradas pelo código do Helios. Cada eleição tem **20 cédulas distintas repetidas** até o número de eleitores. O custo da soma depende do tamanho da cédula e do número de cédulas, não de elas serem distintas.
- Linha de base: 3 questões de 5 opções, mínimo 0, máximo 1, 1 apurador, 1 administrador, sem randomização.
- A matriz não é o produto cartesiano (daria milhares de execuções). Cada eixo varia sozinho, com os outros na linha de base.

## 1. Número de eleitores (3 questões, 5 opções)

| Eleitores | Antes (MiB) | Depois (MiB) | Tempo antes (s) | Tempo depois (s) | CPU antes (s) | CPU depois (s) |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 74 | 73 | 0,02 | 0,03 | 0,01 | 0,02 |
| 100 | 90 | 85 | 0,14 | 0,15 | 0,11 | 0,11 |
| 500 | 165 | 140 | 0,70 | 0,74 | 0,56 | 0,55 |
| 1.000 | 260 | 175 | 1,39 | 1,44 | 1,11 | 1,05 |
| 2.000 | 448 | 175 | 3,17 | 3,03 | 2,51 | 2,26 |
| 5.000 | 1.014 | 174 | 7,55 | 7,43 | 6,04 | 5,45 |
| 10.000 | 1.955 | 174 | 15,0 | 14,7 | 12,0 | 10,7 |
| 20.000 | 3.839 | 174 | 30,6 | 29,3 | 24,6 | 21,5 |
| 30.000 | 5.724 | 175 | 47,2 | 46,3 | 38,1 | 34,0 |
| 50.000 | 9.492 | 175 | 79,8 | 78,2 | 63,7 | 57,0 |

- **Antes:** a memória cresce linearmente, cerca de **0,19 MiB por eleitor** neste formato de cédula. Com 50.000 eleitores o pico foi 9,5 GiB.
- **Depois:** a memória fica **constante em 174 MiB** de 1.000 a 50.000 eleitores.
- **Tempo:** igual. A diferença entre as variantes (de -3% a +4%) está dentro da variação entre execuções. O teste de 10.000 eleitores com 11 questões feito antes (116 s contra 135 s) usou outro formato de cédula e não se repetiu aqui.
- **Parada pedida no objetivo:** não foi necessária. O maior pico do "antes", 9,5 GiB, deixou 14,8 GiB livres. Mais eleitores seguem a mesma reta: 100.000 eleitores dariam cerca de 19 GiB no "antes", e o "depois" continuaria em 174 MiB.

## 2. Número de questões (cada uma com 5 opções)

| Questões | 1.000 eleitores, antes | 1.000, depois | 10.000, antes | 10.000, depois | 10.000, tempo (s) |
|---:|---:|---:|---:|---:|---:|
| 1 | 135 | 106 | 713 | 106 | 5,3 |
| 2 | 197 | 141 | 1.334 | 141 | 10,5 |
| 3 | 260 | 175 | 1.955 | 175 | 15,8 |
| 4 | 322 | 208 | 2.576 | 209 | 22,4 |
| 5 | 383 | 243 | 3.197 | 243 | 26,5 |

Valores em MiB, a menos da última coluna. Cada questão acrescenta cerca de 620 MiB ao "antes" com 10.000 eleitores e cerca de 34 MiB ao "depois" (o lote de 500 cédulas). O tempo cresce linearmente com as questões.

## 3. Tipo de questão (3 questões, 1.000 eleitores)

| Mínimo | Máximo | Opções | Antes (MiB) | Depois (MiB) | Tempo (s) |
|---|---|---:|---:|---:|---:|
| 0 | todas | 2 | 173 | 127 | 0,82 |
| 0 | todas | 5 | 305 | 199 | 1,87 |
| 0 | todas | 18 | 874 | 514 | 6,6 |
| 1 | todas | 2 | 162 | 121 | 0,70 |
| 1 | todas | 5 | 293 | 193 | 1,63 |
| 1 | todas | 18 | 863 | 508 | 6,5 |

- O que pesa é o **número de opções**, porque cada opção leva uma prova na cédula. Com 18 opções por questão, a cédula é cerca de 3,5 vezes maior que com 5.
- Mínimo 0 ou 1 muda pouco, com um pico de 1% a 4% maior no mínimo 0 (cédulas diferentes, sorteadas pela mesma semente).
- Com cédulas grandes, o "depois" também sobe, porque o lote de 500 cédulas fica maior. Com 18 opções e 3 questões, **o lote de 500 usa cerca de 440 MiB**. Um `chunk_size` menor baixaria esse valor, com mais consultas ao banco. Ainda não medi isso.
- Máximo 1 (escolha única) não foi medido à parte. A linha de base já usa máximo 1.

## 4. Randomização

| Cenário | Antes (MiB) | Depois (MiB) | Tempo (s) |
|---|---:|---:|---:|
| Sem randomizar | 259 | 175 | 1,59 |
| `randomize_answer_order` ligado | 259 | 174 | 1,59 |

A randomização muda só a ordem das opções na cabine. **A apuração não muda.** O Helios guarda a randomização por eleição (`randomize_answer_order`). Não há opção por questão neste código, então o teste cobre a eleição inteira.

## 5. Apuradores (3 questões de 5 opções)

| Apuradores | `compute_tally`, 1.000 eleitores (s) | Decifragem por apurador (s) | `compute_tally`, 10.000 eleitores (s) | Decifragem por apurador (s) |
|---:|---:|---:|---:|---:|
| 1 | 1,58 | 0,11 | 15,65 | 0,14 |
| 2 | 1,60 | 0,11 a 0,12 | 15,68 | 0,11 a 0,13 |
| 3 | 1,58 | 0,13 | 15,66 | 0,11 |
| 5 | 1,58 | 0,11 | 15,47 | 0,13 |
| 10 | 1,58 | 0,10 a 0,13 | 15,65 | 0,10 a 0,11 |

- **Os apuradores não deixam a apuração mais lenta.** A decifragem leva cerca de 0,12 s por apurador, e não depende do número de eleitores nem de apuradores, porque ela age só sobre a soma já feita (uma por opção).
- Dez apuradores somam cerca de 1,2 s no total.
- Neste teste a decifragem roda no servidor (as chaves foram geradas aqui). Numa eleição real, a pessoa apuradora decifra **no navegador**, e o tempo dela não passa pelo servidor.
- O pico de memória do `compute_tally` é o do "antes" (1.955 MiB com 10.000 eleitores) em todos os casos.

## 6. Administradores

De 1 a 10 administradores, com 1.000 eleitores: pico de 259 MiB no "antes" e de 175 MiB no "depois", e tempo de 1,5 s a 1,6 s. **Não há efeito.** Administradores são só uma relação entre usuários e eleição, e a apuração não os lê.

## 7. Banco de dados, outros serviços e disco

- **Memória do `web`** durante a soma "antes": segue o pico do processo (9,7 GiB com 50.000 eleitores). No "depois", fica em 380 MiB a 470 MiB.
- **Memória do `db`:** de 82 MiB (banco vazio) a 255 MiB. O `db` não cresce com a soma, e sim com a quantidade de dados gerados.
- **Memória do `worker`:** não participou. A soma foi medida em processo próprio dentro do `web`. Na instância real a apuração roda no `worker`, e o consumo é o mesmo do processo medido.
- **CPU:** a soma usa um núcleo (cerca de 100%). O pico do `web` ficou em 100% do `docker stats`, em todos os cenários grandes. A variante "depois" gasta de 10% a 15% menos CPU que a "antes", com a mesma duração de relógio.
- **Tamanho dos dados:** a tabela de cédulas fica em cerca de 87 MiB com 1.000 eleitores (0,09 MiB por cédula, para 3 questões de 5 opções), 547 MiB com 10.000 e 1,1 GiB com 20.000. A de eleitores tem tamanho parecido, porque cada eleitor guarda a cédula também.
- **Memória do notebook:** com 50.000 eleitores no "antes", a memória livre mínima foi de 14,8 GiB (de 31 GiB). Nenhum cenário chegou perto do limite.
- **Cuidado com `db_bytes`:** a coluna do CSV mede o banco inteiro. Como cada cenário apaga a eleição no fim, o espaço fica reservado no PostgreSQL (sem `VACUUM FULL`), e o valor sobe de um cenário para o outro. Use `castvote_bytes` e `voter_bytes` para comparar tamanhos.

## 8. Limites deste teste

- As cédulas se repetem (20 distintas). Isso não afeta a soma, mas reduz o tamanho no disco, se o PostgreSQL comprimir os dados repetidos (TOAST).
- A soma foi medida sem gravar o resultado. A gravação do `encrypted_tally` e a verificação de cada cédula (4,5 s por cédula com 11 questões, medida em 2026-11-18) ficaram de fora. A verificação é o gargalo de tempo, e não a soma.
- A medida é de uma execução por cenário. Diferenças de tempo menores que 5% não são significativas.
- Memória de `chunk_size` diferente de 500: não medida.

## Conclusão

- Sem o `iterator`, a memória da apuração cresce com o número de eleitores e de questões: **9,5 GiB com 50.000 eleitores**, 3 questões de 5 opções.
- Com `.iterator(chunk_size=500)`, a memória fica **constante** (174 MiB nesse formato), o resultado é **idêntico** e o tempo é o mesmo.
- Apuradores e administradores não afetam a soma.
- O que ainda pesa depois da correção é o tamanho da cédula (opções por questão), pelo lote de 500.
