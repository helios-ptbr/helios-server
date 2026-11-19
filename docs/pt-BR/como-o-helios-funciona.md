# Como o Helios funciona

> **Tradução não oficial.** Este texto vem do fork
> [helios-ptbr/helios-server](https://github.com/helios-ptbr/helios-server),
> que traduz o Helios para o português do Brasil. Ele não foi escrito nem
> revisado por Ben Adida. Em caso de dúvida, vale o original em inglês:
> [How Helios Works](../how-helios-works.md)
> ([no repositório de Ben Adida](https://github.com/benadida/helios-server/blob/master/docs/how-helios-works.md)).

O Helios é um sistema de votação online em que as cédulas são cifradas no
próprio dispositivo do eleitor, e em que qualquer pessoa autorizada a
ver uma eleição pode conferir se ela foi apurada corretamente. Esta página
explica o processo para quem administra a eleição, para quem vota e para as
pessoas curadoras. Para o projeto técnico, veja a
[Arquitetura](../architecture.md) (em inglês).

## Quem participa

- **Pessoas administradoras** criam a eleição, escrevem as questões, fornecem
  a lista de eleitores e fazem a apuração. Uma eleição pode ter mais de
  uma pessoa administradora.
- **Eleitores** depositam cédulas cifradas.
- **Pessoas curadoras** guardam as chaves necessárias para decifrar a apuração
  final. Por padrão, o próprio Helios é a única pessoa curadora. Quem
  administra pode incluir outras pessoas como curadoras.
- **Quem pode ver a eleição** pode conferir se cada cédula está bem formada e
  se o resultado corresponde às cédulas. Em uma eleição pública, isso vale
  para qualquer pessoa. Em uma eleição privada, para os eleitores,
  administradoras e curadoras.

## Os passos de uma eleição

1. **Preparação.** Quem administra cria a eleição, escreve as questões e as
   opções, inclui as pessoas curadoras, se houver, e envia a lista de eleitores. Cada questão pode permitir uma ou várias escolhas, com um mínimo
   e um máximo.
2. **Chaves das pessoas curadoras.** Cada pessoa curadora incluída gera um par
   de chaves no navegador e guarda a parte secreta. Só a parte pública é
   enviada ao Helios. Essas chaves públicas são combinadas na chave de cifragem
   da eleição.
3. **Congelamento.** Quem administra congela a eleição. A partir daí, as
   questões, as pessoas curadoras e a chave de cifragem não mudam mais. As
   eleitores ainda podem ser incluídos ou removidos até o início da
   apuração. A votação abre na hora marcada, ou na mesma hora, se não houver
   horário.
4. **Votação.** Os eleitores preenchem e depositam as cédulas (veja
   abaixo).
5. **Apuração.** Quando a votação termina, quem administra inicia a apuração.
   O Helios soma todas as cédulas cifradas sem decifrar nenhuma, e obtém um
   total cifrado para cada opção.
6. **Decifragem.** Cada pessoa curadora decifra a sua parte dos totais
   cifrados, com uma prova de que fez isso corretamente. A pessoa curadora do
   Helios faz isso automaticamente. As outras usam a chave secreta no
   navegador. Todas as pessoas curadoras precisam participar: sem isso, os
   totais não podem ser decifrados.
7. **Resultados.** Quem administra combina as partes das pessoas curadoras para
   obter as contagens e depois as libera. Também pode avisar os eleitores por e-mail quando o resultado sair.

## Votação

1. O eleitor abre a cabine de votação pela página da eleição e faz as
   suas escolhas.
2. A cabine cifra a cédula no dispositivo da pessoa e mostra um **código de
   rastreamento**, que é a impressão digital da cédula cifrada.
3. A pessoa pode **auditar** a cédula em vez de depositá-la. A cabine então revela
   como a cédula foi cifrada, e a pessoa (ou quem ela escolher) pode conferir
   se ela contém mesmo as suas escolhas. Uma cédula auditada nunca é contada, e
   a pessoa faz uma cédula nova para depositar. Se a pessoa publicar uma cédula
   auditada na lista pública, qualquer pessoa pode ver as escolhas dela. É
   assim que os eleitores conferem que a cabine não altera o voto: como
   ela não sabe de antemão quais cédulas serão auditadas, qualquer fraude corre
   o risco de ser descoberta.
4. A pessoa **deposita** a cédula e entra: com o ID do eleitor e a senha que o Helios
   mandou por e-mail, ou com a conta com que foi convidada (por exemplo,
   Google ou GitHub).
5. O Helios registra a cédula e confere as provas dela em segundo plano.
   Quando as conferências passam, a cédula vira a cédula contada da pessoa, e o
   Helios envia a ela o código de rastreamento por e-mail. O código aparece ao
   lado do nome da pessoa no centro de rastreamento de cédulas da eleição, para
   que ela confira que a cédula foi registrada.
6. **Votar de novo.** A pessoa pode depositar uma cédula nova a qualquer momento,
   enquanto a votação estiver aberta. Só vale a cédula mais recente que passou
   nas conferências.

## Privacidade

- De uma cédula depositada, o Helios recebe só a cédula cifrada, nunca as escolhas
  da pessoa. As cédulas auditadas são a exceção: elas revelam as escolhas, e
  publicar uma cédula auditada publica essas escolhas.
- As cédulas nunca são decifradas uma a uma. Só os totais combinados são
  decifrados.
- Decifrar qualquer coisa exige todas as pessoas curadoras. Quem consegue
  decifrar depende, portanto, de quem são as pessoas curadoras:
  - Se o Helios é a única pessoa curadora (o padrão), o servidor do Helios
    guarda a chave inteira, e quem opera o servidor poderia, em princípio,
    decifrar cédulas individuais.
  - Incluir pessoas curadoras independentes evita isso: nenhuma parte
    isolada, nem o Helios, consegue decifrar sem as outras.
- As eleições podem usar **apelidos para os eleitores**, de modo que a
  lista pública mostre `V1`, `V2`, ... no lugar dos nomes.
- Uma eleição **privada** só pode ser vista pelos seus eleitores,
  administradoras e curadoras.

## Verificar uma eleição

Qualquer pessoa que possa ver a eleição pode conferir:

- se o seu código de rastreamento aparece na lista de cédulas;
- se cada cédula da lista está bem formada: ela cifra uma escolha válida para
  cada questão, o que as provas dentro da cédula mostram sem revelar a
  escolha;
- se a chave de cada pessoa curadora é genuína e se a chave da eleição foi
  construída a partir delas;
- se os totais cifrados são o produto das cédulas da lista;
- se cada pessoa curadora decifrou os totais corretamente e se as contagens
  publicadas decorrem disso.

O Helios inclui uma página de verificação que faz todas essas conferências no
navegador. Também há um verificador de cédula única, para cédulas auditadas.
Como tudo o que se confere é publicado, programas de outras pessoas podem
fazer as mesmas conferências de forma independente.

## No que você ainda precisa confiar

As conferências acima mostram que as cédulas publicadas foram contadas
corretamente. Elas não cobrem tudo:

- **A lista de eleitores e os IDs.** O Helios decide quem pode
  votar: a lista enviada, mais quem puder se cadastrar, se o cadastro estiver
  aberto. Ele também confere que cada cédula vem de um eleitor com
  ID do eleitor. A lista de eleitores é publicada, mas os dados publicados, por
  si sós, não provam que cada cédula foi depositada pela pessoa a quem ela está
  atribuída.
- **O dispositivo e a cabine de votação.** A cifragem acontece no navegador da
  pessoa. A auditoria de cédulas é a proteção contra uma cabine ou um
  dispositivo que altere votos.
- **As pessoas curadoras.** O sigilo depende de as pessoas curadoras não se
  combinarem para decifrar cédulas individuais. Isso inclui o Helios, quando
  ele é uma pessoa curadora.
- **Coação.** Os eleitores podem ver e mostrar o próprio código de
  rastreamento e podem votar de novo, mas o Helios não tem nenhuma outra
  proteção contra pessoas pressionadas ou pagas para votar de certa forma.

## Resultados

Em cada questão, as opções com mais votos vencem, até o número de vagas que a
questão permite. Se houver empate na última vaga, nenhuma das opções empatadas
a ocupa: a vaga fica sem preenchimento, as opções empatadas são marcadas, e
quem administra decide o que fazer. Uma questão de escolha única pode, em vez
disso, exigir maioria absoluta: a opção vencedora precisa de mais da metade das
cédulas depositadas. Se isso não acontecer, não há vencedora.
