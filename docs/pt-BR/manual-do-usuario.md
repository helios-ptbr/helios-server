# Manual do Helios

> **Tradução não oficial.** Este texto vem do fork
> [helios-ptbr/helios-server](https://github.com/helios-ptbr/helios-server),
> que traduz o Helios para o português do Brasil. Ele não foi escrito nem
> revisado por Ben Adida. Em caso de dúvida, vale o original em inglês:
> [User Manual](../user-manual.md)
> ([no repositório de Ben Adida](https://github.com/benadida/helios-server/blob/master/docs/user-manual.md)).

Este guia percorre uma eleição inteira: criar a eleição, incluir pessoas
eleitoras, abri-la, votar e publicar o resultado. A última parte é um guia para
quem vota.

As imagens vêm de uma eleição de teste, "Riverside Club Board Election 2026",
com três pessoas eleitoras. **As imagens estão na interface em inglês**, e os
nomes de botões e campos no texto seguem a interface em português. Seu servidor
pode oferecer outras opções de login.

## Parte 1: Administrar uma eleição

### 1. Entre

Entre no seu servidor Helios. Depois do login, a página inicial mostra
**criar eleição**, além das eleições que você administra e das que você votou.

![Página inicial depois do login](../images/manual/admin-home.png)

### 2. Crie a eleição

Clique em **criar eleição** e preencha o formulário:

- **Nome curto:** uma palavra, sem espaços. Ele passa a fazer parte do endereço
  da eleição, por exemplo `/helios/e/diretoria-2026`.
- **Nome** e **Descrição:** o que as pessoas eleitoras vão ver.
- **Tipo:** Eleição ou Consulta.
- **Usar apelidos de pessoas eleitoras:** mostra as pessoas como "V12" e
  assim por diante no centro de rastreamento de cédulas público, no lugar dos
  nomes.
- **Ordem aleatória das opções:** mostra as opções em ordem aleatória para cada
  pessoa eleitora.
- **Privada?:** só as pessoas eleitoras da sua lista podem ver a eleição.
- **E-mail de ajuda:** para onde as pessoas eleitoras podem pedir ajuda.
- **Início da votação / Fim da votação:** opcionais. Você digita o horário do
  fuso do seu navegador, e o Helios converte para UTC. Deixe em branco para
  abrir a votação assim que você congelar a urna (passo 6) e encerrá-la você
  mesma ou você mesmo.

Clique em **Próximo**. Você chega à página da eleição, que sempre mostra o
**Próximo passo**.

![Formulário da nova eleição](../images/manual/new-election.png)

### 3. Inclua as perguntas

Clique em **perguntas**. Em cada pergunta, digite o texto, quantas opções a
pessoa pode escolher ("Seleção: 0 a 2") e as opções. Clique em **Adicionar a
pergunta**.

![Incluindo uma pergunta](../images/manual/question-form.png)

Você pode editar, remover e reordenar as perguntas até congelar a eleição.

![A cédula pronta](../images/manual/questions.png)

### 4. Inclua as pessoas eleitoras

Clique em **pessoas eleitoras e cédulas**. Primeiro escolha quem pode votar
(isso não muda depois do congelamento):

- **qualquer pessoa pode votar:** qualquer pessoa que entrar pode votar.
- **só as pessoas eleitoras listadas abaixo podem votar:** só as pessoas que
  você enviar.

![Página das pessoas eleitoras](../images/manual/voters-empty.png)

Para incluir pessoas eleitoras, clique em **enviar pessoas eleitoras em lote**
e envie um arquivo CSV, com uma pessoa por linha. A maioria das eleições usa
senhas do Helios:

```
password,dana,dana@example.org,Dana Lee
password,sam,sam@example.org,Sam Ortiz
password,priya,priya@example.org,Priya Shah
```

Os campos são: `password`, um login que você escolhe, o e-mail da pessoa e o
nome dela. O Helios cria uma senha para cada pessoa e a envia por e-mail no
passo 7. Para usar uma conta de login externa, escreva o tipo de login e o
nome de usuário, por exemplo `github,benadida`.

Confira a prévia e clique em **Sim, pode seguir**.

![Conferindo o envio](../images/manual/voters-confirm.png)

As pessoas eleitoras agora aparecem na lista. Você pode enviar mais arquivos e
remover pessoas até calcular a apuração, mesmo com a votação aberta.

![A lista de pessoas eleitoras](../images/manual/voters-list.png)

### 5. Pessoas curadoras (opcional)

As pessoas curadoras guardam as chaves que decifram o resultado. Por padrão, o
Helios é a única pessoa curadora e cuida disso por você, então você pode pular
este passo.

![Página das pessoas curadoras](../images/manual/trustees.png)

Para ter mais proteção, inclua pessoas curadoras em **adicionar uma pessoa
curadora** (nome e e-mail) e clique em **enviar o acesso** para mandar a cada
uma o seu link. Cada pessoa curadora abre o link, clica em **configurar a sua
chave**, gera uma chave, guarda o arquivo da chave secreta em um lugar seguro e
envia a chave pública. Você também pode remover a pessoa curadora do Helios,
para que ninguém consiga decifrar o resultado sem as suas pessoas curadoras.

Você só consegue congelar a eleição quando todas as pessoas curadoras tiverem
enviado a chave pública. Decifrar o resultado exige todas elas: se uma perder
a chave secreta, o resultado não pode ser decifrado.

### 6. Congele a eleição

Quando a cédula e as pessoas curadoras estiverem prontas, clique em **congelar
a urna e abrir a eleição** em Próximo passo e depois em **Congelar a urna**.

Depois do congelamento, as perguntas, as opções e as pessoas curadoras não
mudam mais. Você ainda pode mudar a lista de pessoas eleitoras. A votação abre
na hora, ou no horário de início que você definiu.

![Congelando a urna](../images/manual/freeze.png)

![A eleição está aberta](../images/manual/election-open.png)

### 7. Envie e-mail às pessoas eleitoras

Na página **pessoas eleitoras e cédulas**, clique em **enviar e-mail às pessoas
eleitoras**. O modelo **Hora de votar** envia a cada pessoa o link de votação
e, para quem usa senha, o login e a senha.

A caixa do topo é uma prévia. O Helios preenche os dados de cada pessoa nos
campos mostrados entre sinais de menor e maior. Para acrescentar um texto seu,
escreva-o em **Corpo da mensagem**: ele aparece no lugar de `<BODY>`. Não cole
a prévia ali. Escolha quem recebe e clique em **Enviar**.

![Enviando e-mail às pessoas eleitoras](../images/manual/email-voters.png)

Depois, você pode usar a mesma página para lembrar só as pessoas que ainda não
votaram.

### 8. Enquanto a votação está aberta

A página **pessoas eleitoras e cédulas** mostra quantos votos foram enviados e
o código de rastreamento de cada pessoa. Se você definiu um horário de fim,
pode **prorrogar a votação** até calcular a apuração.

### 9. Encerre a votação e calcule a apuração

Quando quiser parar a votação, clique em **calcular a apuração cifrada** em
Próximo passo e depois em **calcular a apuração cifrada!**. Isso encerra a
votação: ninguém mais consegue enviar cédula.

![Calculando a apuração](../images/manual/compute-tally.png)

O Helios soma as cédulas cifradas sem decifrar nenhuma. Se o Helios é pessoa
curadora, ele decifra a sua parte automaticamente. As outras pessoas curadoras
agora abrem o seu link, clicam em decifrar com a sua chave, digitam a chave
secreta e enviam a decifragem parcial.

### 10. Calcule e libere o resultado

Quando todas as pessoas curadoras tiverem decifrado, clique em **calcular os
resultados** em Próximo passo e depois em **calcular a apuração!**. O
resultado agora aparece só para você.

![O resultado, antes de liberar](../images/manual/results-admin.png)

Confira e clique em **liberar o resultado**. Deixe a caixa marcada para enviar
e-mail às pessoas eleitoras e clique em **liberar o resultado!**.

![Liberando o resultado](../images/manual/release.png)

Agora todas as pessoas veem o resultado na página da eleição.

![O resultado publicado](../images/manual/results-public.png)

## Parte 2: Guia para quem vota

### 1. Seu e-mail

Você recebe um e-mail como este (o texto abaixo é o do modelo em inglês; no
servidor em português, ele vem em português):

```
Dear Dana Lee,

Voting is open until Friday at 5pm.

Election URL (click to begin voting):
https://vote.example.org/helios/e/club-board-2026/vote

Your voter ID: dana
Your password: usyWtLo2yW
```

Guarde o e-mail: você vai precisar do login e da senha para enviar a cédula.
Algumas eleições pedem que você entre com uma conta, como Google ou GitHub.

### 2. Preencha a cédula

Clique no link do e-mail. A cabine de votação abre. Clique em **Iniciar**.

![A cabine de votação](../images/manual/booth-start.png)

Marque as respostas de cada pergunta e clique em **Próximo** (**Prosseguir**
depois da última pergunta). A cabine diz quantas opções você pode escolher.

![Escolhendo as opções](../images/manual/booth-question.png)

### 3. Revise e cifre

A cabine mostra as suas escolhas. Clique em **[alterar]** para corrigir uma
pergunta.

Em seguida, o navegador cifra a cédula e mostra o seu **código de
rastreamento**, um código longo como `Ag/lQORWPk...`. Anote-o ou deixe a
página aberta. Clique em **Prosseguir para o login**.

![Revisando a cédula](../images/manual/booth-review.png)

**Anular e auditar** é opcional. Com isso você confere se a cabine cifrou as
suas escolhas corretamente, mas essa cédula é descartada e você começa de novo.
A auditoria mostra as suas escolhas, e, se você publicar a cédula auditada,
qualquer pessoa pode vê-las.

### 4. Envie a cédula

A sua cédula ainda não foi enviada. Digite o login e a senha do e-mail e
clique em **autenticar & enviar a cédula**.

![Entrando para enviar](../images/manual/cast-login.png)

Perdeu a senha? Clique em **Esqueceu a senha? Clique aqui para receber de
novo.**

Se você entrou com uma conta, clique em **ENVIAR esta cédula**.

### 5. Pronto

Você vê **Voto enviado com sucesso!** e o seu código de rastreamento. O Helios
também envia o código por e-mail.

![Cédula enviada](../images/manual/cast-done.png)

### 6. Confira a sua cédula

Abra a página da eleição e clique em **pessoas eleitoras e cédulas**. Em alguns
minutos, o seu código de rastreamento aparece ao lado do seu nome (ou do seu
apelido). Se ele for igual ao que você anotou, a sua cédula foi registrada como
você a enviou.

![Centro de rastreamento de cédulas](../images/manual/tracking-center.png)

### Votar de novo

Você pode votar de novo enquanto a votação estiver aberta. Só vale a sua
última cédula.

### Ver o resultado

Quando quem administra libera o resultado, ele aparece na página da eleição, e
você pode receber um e-mail.
