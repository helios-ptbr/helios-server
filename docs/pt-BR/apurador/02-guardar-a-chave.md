# Apurador 2: Guardar a chave e o que acontece se ela se perder

## Como o Helios divide a chave

Cada apurador gera a sua própria chave. O Helios soma as chaves públicas e forma a **chave da eleição**. Para abrir o resultado, a decifragem precisa da parte de **cada** apurador.

**O Helios não usa quórum.** Ele não usa o método de dividir um segredo em partes em que bastam algumas (como "3 de 5"). Aqui, são todas ou nenhuma.

| Situação | O que acontece |
|---|---|
| 5 apuradores, os 5 decifram | O resultado abre |
| 5 apuradores, 4 decifram e 1 perdeu a chave | **O resultado não abre. Não há recuperação** |
| 5 apuradores, 4 decifram e 1 ainda não decifrou | O Helios espera. A eleição fica parada até a quinta decifragem |

O Helios confere isso na hora de combinar as decifragens. Se falta uma, o botão não aparece.

## O que guardar

- **A chave secreta.** É o texto longo que a tela mostrou ao gerar a chave. Guarde uma cópia em um gerenciador de senhas ou em um arquivo, em dois lugares diferentes.
- **O e-mail com o link do painel.** Sem ele, você não chega à página de decifragem.
- **A impressão digital da chave pública.** Ela serve para conferir, e não é segredo.

**Não guarde a chave** em um arquivo aberto na nuvem, em um e-mail sem proteção ou em uma conversa de mensagens.

## Antes de a eleição abrir

Peça a cada apurador para **conferir a chave** (veja o [manual 1](01-chave.md), seção 3). O gestor só deve congelar a eleição depois que todos conferiram. Depois de congelar, não dá para trocar um apurador.

## Se a chave se perder

Se a eleição ainda **não foi congelada**, o gestor remove o apurador e cria outro, que gera uma chave nova.

Se a eleição **já foi congelada**, não há saída dentro do Helios. O resultado não abre. As cédulas continuam guardadas e verificáveis, mas ninguém consegue contar. Quem decide o que fazer é a regra da instituição, por exemplo refazer a eleição.

## Como reduzir o risco

- Use **poucos apuradores**. Cada um a mais é mais um ponto de falha.
- Use o apurador do próprio Helios para parte da função. Ele guarda e usa a chave dele sozinho. Se o servidor é de confiança, um apurador do Helios mais um ou dois externos já dão ao grupo uma forma de fiscalizar.
- Ensaie. Peça a cada apurador para abrir o painel, conferir a chave e achar o e-mail, antes de congelar.

## Dúvidas comuns

**Posso ter só o apurador do Helios?** Pode. A decifragem fica automática. A desvantagem é que a confiança fica toda no servidor.

**Dá para trocar a chave depois do envio?** Não. Só removendo o apurador, antes de congelar.

**Um apurador pode decifrar por outro?** Não. Cada um usa a própria chave.

Voltar ao [índice do apurador](README.md).
