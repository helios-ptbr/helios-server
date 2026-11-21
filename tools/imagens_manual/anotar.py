#!/usr/bin/env python3
"""Recorta e marca as capturas de tela dos manuais.

Entrada: as capturas brutas (as que os `passo*.py` geram), por nome de arquivo.
Saída: as imagens finais de `docs/images/manual/pt-BR/` e de `docs/pt-BR/<papel>/imagens/`.

O que faz com cada captura:
  1. tira a barra de menu do alto e a barra "sessão iniciada" de baixo;
  2. corta o branco que sobra, com margem de 14 px, e põe uma borda cinza;
  3. deixa todas com a mesma largura (1013 px);
  4. desenha um círculo numerado e um contorno vermelho em cada elemento de MARCAS.

As caixas de MARCAS estão em pixels da captura bruta: (x0, y0, x1, y1, número) e, se quiser, uma letra
que diz onde fica o círculo do número: 'e' (à esquerda, o padrão), 'a' (acima), 'b' (abaixo) ou 'd' (à direita).
Se uma tela mudar, rode os `passo*.py`, ajuste as caixas aqui e rode este script.

Uso, da raiz do repositório:
    python3 tools/imagens_manual/anotar.py PASTA_DAS_CAPTURAS_BRUTAS
    python3 tools/imagens_manual/anotar.py PASTA_DAS_CAPTURAS_BRUTAS --so freeze.png
    python3 tools/imagens_manual/anotar.py PASTA_DAS_CAPTURAS_BRUTAS --legendas   # e as legendas dos manuais
Precisa do Pillow (`pip install pillow`).
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LARGURA_UTIL = 985   # largura do recorte, em pixels
MARGEM = 14          # margem em volta do recorte
RAIO = 13           # raio do círculo numerado
VERMELHO = (214, 40, 40)
CINZA = (170, 170, 170)

# captura bruta -> arquivos finais (relativos a docs/)
DESTINOS = {
    'admin-home.png': ['images/manual/pt-BR/admin-home.png', 'pt-BR/gestor/imagens/admin-home.png'],
    'admins.png': ['images/manual/pt-BR/admins.png', 'pt-BR/gestor/imagens/admins.png'],
    'booth-question.png': ['images/manual/pt-BR/booth-question.png', 'pt-BR/eleitor/imagens/cabine-questao.png'],
    'booth-review.png': ['images/manual/pt-BR/booth-review.png', 'pt-BR/eleitor/imagens/cabine-revisao.png'],
    'booth-start.png': ['images/manual/pt-BR/booth-start.png', 'pt-BR/eleitor/imagens/cabine-inicio.png'],
    'cast-done.png': ['images/manual/pt-BR/cast-done.png', 'pt-BR/eleitor/imagens/voto-depositado.png'],
    'cast-login.png': ['images/manual/pt-BR/cast-login.png', 'pt-BR/eleitor/imagens/depositar-login.png'],
    'compute-tally.png': ['images/manual/pt-BR/compute-tally.png', 'pt-BR/gestor/imagens/compute-tally.png'],
    'election-open.png': ['images/manual/pt-BR/election-open.png', 'pt-BR/gestor/imagens/election-open.png'],
    'email-voters.png': ['images/manual/pt-BR/email-voters.png', 'pt-BR/gestor/imagens/email-voters.png'],
    'freeze.png': ['images/manual/pt-BR/freeze.png', 'pt-BR/gestor/imagens/freeze.png'],
    'new-election.png': ['images/manual/pt-BR/new-election.png', 'pt-BR/gestor/imagens/new-election.png'],
    'question-form.png': ['images/manual/pt-BR/question-form.png', 'pt-BR/gestor/imagens/question-form.png'],
    'questions.png': ['images/manual/pt-BR/questions.png'],
    'release.png': ['images/manual/pt-BR/release.png', 'pt-BR/gestor/imagens/release.png'],
    'results-admin.png': ['images/manual/pt-BR/results-admin.png', 'pt-BR/gestor/imagens/results-admin.png'],
    'results-public.png': ['images/manual/pt-BR/results-public.png', 'pt-BR/gestor/imagens/results-public.png'],
    'tracking-center.png': ['images/manual/pt-BR/tracking-center.png', 'pt-BR/eleitor/imagens/rastreamento.png'],
    'trustees.png': ['images/manual/pt-BR/trustees.png'],
    'voters-confirm.png': ['images/manual/pt-BR/voters-confirm.png', 'pt-BR/gestor/imagens/voters-confirm.png'],
    'voters-empty.png': ['images/manual/pt-BR/voters-empty.png', 'pt-BR/gestor/imagens/voters-empty.png'],
    'voters-list.png': ['images/manual/pt-BR/voters-list.png', 'pt-BR/gestor/imagens/voters-list.png'],
    'apurador-painel.png': ['pt-BR/apurador/imagens/apurador-painel.png'],
    'chave-secreta.png': ['pt-BR/apurador/imagens/chave-secreta.png'],
    'decifragem.png': ['pt-BR/apurador/imagens/decifragem.png'],
    'email-apurador.png': ['pt-BR/apurador/imagens/email-apurador.png'],
    'cabine-anular.png': ['pt-BR/eleitor/imagens/cabine-anular.png'],
    'cedula-auditada.png': ['pt-BR/eleitor/imagens/cedula-auditada.png'],
    'cedulas-auditadas.png': ['pt-BR/eleitor/imagens/cedulas-auditadas.png', 'pt-BR/fiscal/imagens/cedulas-auditadas.png'],
    'email-eleitor.png': ['pt-BR/eleitor/imagens/email-eleitor.png'],
    'verificador-cedula.png': ['pt-BR/fiscal/imagens/verificador-cedula.png'],
    'verificador-eleicao-inicio.png': ['pt-BR/fiscal/imagens/verificador-eleicao-inicio.png'],
    'verificador-eleicao.png': ['pt-BR/fiscal/imagens/verificador-eleicao.png'],
}

# captura bruta -> lista de (x0, y0, x1, y1, número), em pixels da captura bruta
MARCAS = {
    'admin-home.png': [(807, 267, 912, 297, 1)],
    'new-election.png': [(242, 152, 1011, 180, 1), (242, 738, 1011, 767, 2), (242, 812, 1011, 841, 3),
                         (74, 904, 209, 947, 4)],
    'question-form.png': [(73, 228, 1013, 260, 1), (175, 274, 267, 293, 2, 'b'), (73, 360, 1013, 642, 3),
                          (74, 658, 323, 700, 4), (695, 274, 742, 293, 5, 'b'), (74, 723, 274, 765, 6)],
    'questions.png': [(73, 124, 186, 153, 1), (73, 309, 100, 334, 2), (73, 437, 1013, 1033, 3)],
    'voters-empty.png': [(65, 204, 390, 248, 1), (66, 426, 292, 468, 2)],
    'voters-confirm.png': [(65, 240, 538, 418, 1), (273, 440, 450, 482, 2, 'd')],
    'voters-list.png': [(74, 426, 299, 468, 1), (74, 571, 326, 614, 2), (82, 749, 162, 883, 3)],
    'email-voters.png': [(73, 196, 687, 218, 1), (83, 287, 1003, 691, 2), (342, 831, 1011, 889, 3),
                         (342, 918, 642, 937, 4), (74, 985, 170, 1028, 5)],
    'trustees.png': [(73, 318, 251, 338, 1), (459, 364, 580, 383, 2, 'd'), (327, 398, 832, 421, 3, 'd')],
    'admins.png': [(65, 170, 350, 191, 1), (287, 375, 346, 393, 2, 'd')],
    'freeze.png': [(74, 261, 243, 303, 1), (250, 261, 451, 303, 2, 'b')],
    'election-open.png': [(135, 299, 935, 328, 1), (65, 367, 440, 392, 2)],
    'compute-tally.png': [(74, 288, 333, 330, 1), (340, 288, 445, 330, 2, 'b')],
    'results-admin.png': [(73, 367, 364, 392, 1), (73, 504, 1013, 905, 2)],
    'release.png': [(65, 244, 528, 262, 1), (66, 293, 259, 335, 2)],
    'results-public.png': [(73, 272, 294, 311, 1), (73, 339, 1013, 696, 2), (73, 711, 1013, 739, 3)],
    'tracking-center.png': [(65, 293, 221, 313, 1), (73, 361, 1013, 518, 2)],
    'cast-login.png': [(73, 218, 479, 252, 1), (84, 303, 562, 413, 2), (85, 435, 370, 477, 3),
                       (84, 527, 471, 545, 4)],
    'cast-done.png': [(65, 248, 633, 277, 1), (65, 330, 181, 348, 2, 'b')],
    'booth-start.png': [(496, 357, 604, 399, 1)],
    'booth-question.png': [(70, 287, 1030, 448, 1), (290, 457, 810, 500, 2), (75, 523, 207, 565, 3)],
    'booth-review.png': [(70, 244, 1030, 413, 1), (70, 428, 887, 453, 2), (75, 473, 366, 515, 3),
                         (70, 536, 432, 576, 4)],
    'cabine-anular.png': [(75, 399, 366, 441, 1), (86, 634, 299, 676, 2)],
    'cedula-auditada.png': [(70, 418, 734, 664, 1), (75, 799, 288, 841, 2), (316, 809, 653, 838, 3)],
    'cedulas-auditadas.png': [(602, 417, 793, 437, 1, 'd'), (514, 513, 541, 531, 2, 'd')],
    'apurador-painel.png': [(391, 222, 773, 243, 1, 'd'), (160, 250, 426, 268, 2, 'd'), (80, 321, 845, 340, 3)],
    'chave-secreta.png': [(81, 396, 453, 460, 1), (80, 603, 1020, 799, 2)],
    'decifragem.png': [(80, 198, 693, 268, 1), (80, 778, 1020, 1127, 2), (81, 1143, 462, 1185, 3)],
    'email-apurador.png': [(129, 122, 573, 140, 1), (24, 388, 686, 404, 2, 'd')],
    'email-eleitor.png': [(8, 368, 457, 383, 1, 'd'), (8, 430, 181, 465, 2, 'd'), (8, 510, 1037, 527, 3, 'd')],
    'verificador-cedula.png': [(329, 201, 754, 231, 1, 'd'), (70, 282, 734, 454, 2), (70, 478, 161, 520, 3),
                               (70, 736, 406, 753, 4)],
    'verificador-eleicao-inicio.png': [(389, 92, 814, 122, 1), (536, 122, 666, 143, 2)],
    'verificador-eleicao.png': [(131, 22, 591, 156, 1), (131, 843, 513, 929, 2)],
}

# captura bruta -> legenda que vai sob a imagem nos manuais (um item por marca, na mesma ordem)
LEGENDAS = {
    'admin-home.png': '(1) **criar eleição**.',
    'new-election.png': '(1) **Nome curto**. (2) **Início da votação**, opcional. (3) **Fim da votação**, opcional. (4) **Próximo**.',
    'question-form.png': '(1) Texto da questão. (2) **Escolha entre _X_ e _Y_ opções**. (3) Opções de resposta. (4) **Adicionar mais 5 opções**. (5) **Ordem aleatória**. (6) **Adicionar a questão**.',
    'questions.png': '(1) **editar** e **×**, que editam e removem a questão. (2) **↑**, que sobe a questão. (3) Formulário de uma nova questão.',
    'voters-empty.png': '(1) **Quem pode votar?** (2) **enviar eleitores em lote**.',
    'voters-confirm.png': '(1) As primeiras linhas do arquivo enviado. (2) **Sim, pode seguir**.',
    'voters-list.png': '(1) **enviar eleitores em lote**. (2) **remover todos os eleitores**. (3) **[x]**, que remove um eleitor.',
    'email-voters.png': '(1) Modelos. (2) Prévia do e-mail. (3) **Corpo da mensagem**. (4) **Enviar para**. (5) **Enviar**.',
    'trustees.png': '(1) **adicionar um apurador**. (2) **enviar o acesso**. (3) Impressão digital da chave pública.',
    'admins.png': '(1) **adicionar uma pessoa administradora**. (2) **remover**.',
    'freeze.png': '(1) **Congelar a urna**. (2) **NÃO congelar ainda**.',
    'election-open.png': '(1) Menu da eleição. (2) **Próximo passo**.',
    'compute-tally.png': '(1) **calcular a apuração cifrada!** (2) **desistir**.',
    'results-admin.png': '(1) **Próximo passo**: liberar o resultado. (2) Apuração, visível só para quem administra.',
    'release.png': '(1) Aviso por e-mail aos eleitores. (2) **liberar o resultado!**',
    'results-public.png': '(1) Aviso de eleição concluída. (2) Apuração. (3) **Informações de auditoria**.',
    'tracking-center.png': '(1) Número de votos depositados. (2) Código de rastreamento de cada cédula.',
    'cast-login.png': '(1) Código de rastreamento da sua cédula. (2) **ID do eleitor** e **Senha**. (3) **autenticar & depositar a cédula**. (4) **Esqueceu a senha?**',
    'cast-done.png': '(1) Código de rastreamento da sua cédula. (2) **lista de eleitores**.',
    'booth-start.png': '(1) **Iniciar**.',
    'booth-question.png': '(1) Opções marcadas. (2) Aviso de máximo de opções. (3) **Próximo**.',
    'booth-review.png': '(1) Resumo da cédula. (2) Código de rastreamento. (3) **Prosseguir para o login**. (4) **Anular e auditar**.',
    'cabine-anular.png': '(1) **Prosseguir para o login**. (2) **Anular e auditar**.',
    'cedula-auditada.png': '(1) Dados da cédula auditada. (2) **voltar à votação**. (3) **publicar cédula auditada no centro de rastreamento**.',
    'cedulas-auditadas.png': '(1) **verificador de cédula única**. (2) **ver**.',
    'apurador-painel.png': '(1) Impressão digital da chave pública. (2) **verificar se tem a chave secreta certa**. (3) Aviso para guardar o e-mail.',
    'chave-secreta.png': '(1) **Mostrar a minha chave secreta**. (2) Chave secreta, que aparece uma vez.',
    'decifragem.png': '(1) Impressões digitais da chave pública e da apuração cifrada. (2) Decifragem parcial. (3) **Enviar os fatores de decifragem ao servidor**.',
    'email-apurador.png': '(1) Assunto. (2) Link do painel do apurador.',
    'email-eleitor.png': '(1) Endereço da eleição. (2) **ID do eleitor** e **Senha**. (3) Impressão digital da eleição.',
    'verificador-cedula.png': '(1) Endereço da eleição. (2) Cédula auditada. (3) **Verificar**. (4) Resultado da verificação.',
    'verificador-eleicao-inicio.png': '(1) Endereço da eleição. (2) **iniciar a verificação**.',
    'verificador-eleicao.png': '(1) Contagens e fatores de decifragem de cada apurador. (2) Resultado final.',
}
PREFIXO_LEGENDA = '*Na imagem:'


def _media(p):
    return sum(p[:3]) // 3


def _limites_verticais(im):
    """Devolve (topo, fim): a faixa da captura sem a barra de menu e sem a barra de baixo."""
    w, h = im.size
    topo = 0
    if _media(im.getpixel((1, 2))) < 40:  # barra de menu escura
        topo = 2
        while topo < h and _media(im.getpixel((1, topo))) < 40:
            topo += 1
    fim = h
    if _media(im.getpixel((1, h - 3))) in range(215, 226):  # barra cinza "sessão iniciada"
        fim = h - 3
        while fim > 0 and _media(im.getpixel((1, fim - 1))) in range(215, 226):
            fim -= 1
        while fim > 0 and _media(im.getpixel((1, fim - 1))) < 120:  # linha de borda
            fim -= 1
    return topo, fim


def _caixa_do_conteudo(im, topo, fim):
    """Menor caixa (x0, y0, x1, y1) com algo que não é branco, dentro da faixa topo..fim.

    Nas páginas com barra de menu, ignora os 20 px da direita: a barra de rolagem do navegador, que
    aparece em algumas capturas, vai de cima a baixo e faria o recorte incluir todo o branco."""
    direita = im.size[0] - 20 if topo > 0 else im.size[0]
    faixa = im.crop((0, topo, direita, fim)).convert('L').point(lambda v: 0 if v > 244 else 255)
    caixa = faixa.getbbox()
    if not caixa:
        return (0, topo, im.size[0], fim)
    return (caixa[0], caixa[1] + topo, caixa[2], caixa[3] + topo)


def _fonte(tam):
    for caminho in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                    '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(caminho):
            return ImageFont.truetype(caminho, tam)
    return ImageFont.load_default()


def _lado(m):
    return m[5] if len(m) > 5 else 'e'


def processar(bruta, marcas):
    im = Image.open(bruta).convert('RGB')
    w, _ = im.size
    topo, fim = _limites_verticais(im)
    cx0, cy0, cx1, cy1 = _caixa_do_conteudo(im, topo, fim)
    for m in marcas:  # as marcas (e o círculo do número) também entram no recorte
        lado = _lado(m)
        cx0 = min(cx0, m[0] - (RAIO * 2 + 8 if lado == 'e' else 8))
        cx1 = max(cx1, m[2] + (RAIO * 2 + 10 if lado == 'd' else 8))
        cy0 = min(cy0, m[1] - (RAIO * 2 + 18 if lado == 'a' else 8))
        cy1 = max(cy1, m[3] + (RAIO * 2 + 18 if lado == 'b' else 8))
    y0 = max(topo, cy0 - MARGEM)
    y1 = min(fim, cy1 + MARGEM)
    if cx1 - cx0 <= LARGURA_UTIL:
        x0 = max(0, min(w - LARGURA_UTIL, cx0))
        x1 = x0 + LARGURA_UTIL
        escala = 1.0
    else:
        # a tela é mais larga que o recorte (a cabine, o Mailpit): reduz para caber
        x0, x1 = max(0, cx0), min(w, cx1)
        escala = LARGURA_UTIL / (x1 - x0)
    corte = im.crop((x0, y0, x1, y1))
    if escala != 1.0:
        corte = corte.resize((LARGURA_UTIL, round(corte.size[1] * escala)), Image.LANCZOS)
    cw, ch = corte.size
    saida = Image.new('RGB', (cw + 2 * MARGEM, ch + 2 * MARGEM), (255, 255, 255))
    saida.paste(corte, (MARGEM, MARGEM))
    d = ImageDraw.Draw(saida)
    d.rectangle((MARGEM - 1, MARGEM - 1, MARGEM + cw, MARGEM + ch), outline=CINZA, width=2)
    fonte = _fonte(17)

    def ponto(x, y):
        return ((x - x0) * escala + MARGEM, (y - y0) * escala + MARGEM)

    for m in marcas:
        n = m[4]
        lado = _lado(m)
        px0, py0 = ponto(m[0], m[1])
        px1, py1 = ponto(m[2], m[3])
        d.rounded_rectangle((px0 - 4, py0 - 4, px1 + 4, py1 + 4), radius=8, outline=VERMELHO, width=3)
        meio = min(py0 + RAIO + 2, (py0 + py1) / 2)
        if lado == 'e':
            cx, cy = px0 - 4 - RAIO - 3, meio
        elif lado == 'd':
            cx, cy = px1 + 4 + RAIO + 3, meio
        elif lado == 'b':
            cx, cy = px0 + 4, py1 + 4 + RAIO + 3
        else:
            cx, cy = px0 + 4, py0 - 4 - RAIO - 3
        d.ellipse((cx - RAIO, cy - RAIO, cx + RAIO, cy + RAIO), fill=VERMELHO, outline='white', width=2)
        d.text((cx, cy), str(n), fill='white', font=fonte, anchor='mm')
    return saida


def escrever_legendas():
    """Põe (ou troca) a legenda "Na imagem: (1) ... (2) ..." sob cada imagem citada nos manuais."""
    import glob
    import re
    por_destino = {}
    for n, lista in DESTINOS.items():
        for rel in lista:
            por_destino[os.path.normpath(os.path.join(RAIZ, 'docs', rel))] = n
    alterados = 0
    for md in sorted(glob.glob(os.path.join(RAIZ, 'docs', '**', '*.md'), recursive=True)):
        linhas = open(md, encoding='utf-8').read().split('\n')
        mudou = False
        i = 0
        while i < len(linhas):
            m = re.match(r'^!\[[^\]]*\]\(([^)\s]+\.png)\)\s*$', linhas[i])
            i += 1
            if not m:
                continue
            alvo = os.path.normpath(os.path.join(os.path.dirname(md), m.group(1)))
            nome = por_destino.get(alvo)
            if not nome or nome not in LEGENDAS or not MARCAS.get(nome):
                continue
            nova = '%s %s*' % (PREFIXO_LEGENDA, LEGENDAS[nome])
            if i + 1 < len(linhas) and linhas[i] == '' and linhas[i + 1].startswith(PREFIXO_LEGENDA):
                if linhas[i + 1] != nova:
                    linhas[i + 1] = nova
                    mudou = True
            else:
                linhas[i:i] = ['', nova]
                mudou = True
        if mudou:
            open(md, 'w', encoding='utf-8').write('\n'.join(linhas))
            alterados += 1
            print('legendas em', os.path.relpath(md, RAIZ))
    return alterados


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('entrada', help='pasta com as capturas brutas')
    ap.add_argument('--so', action='append', help='refaz só esta captura (pode repetir)')
    ap.add_argument('--saida', help='grava aqui, com o nome da captura, em vez de nas pastas de docs/')
    ap.add_argument('--legendas', action='store_true', help='também escreve as legendas nos manuais (docs/**/*.md)')
    a = ap.parse_args()
    nomes = a.so or sorted(DESTINOS)
    faltam = [n for n in nomes if not os.path.exists(os.path.join(a.entrada, n))]
    if faltam:
        sys.exit('faltam capturas em %s: %s' % (a.entrada, ', '.join(faltam)))
    for n in nomes:
        img = processar(os.path.join(a.entrada, n), MARCAS.get(n, []))
        if a.saida:
            os.makedirs(a.saida, exist_ok=True)
            img.save(os.path.join(a.saida, n), optimize=True)
        else:
            for rel in DESTINOS[n]:
                img.save(os.path.join(RAIZ, 'docs', rel), optimize=True)
        print('%-30s -> %dx%d' % (n, img.size[0], img.size[1]))
    if a.legendas:
        escrever_legendas()


if __name__ == '__main__':
    main()
