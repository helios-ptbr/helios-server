#!/usr/bin/env python3
"""Monta a imagem de capa do README (docs/images/capa.png).

Usa a logo do Helios (server_ui/media/logo.png) e duas capturas brutas, sem marcas:
a cabine (booth-question.png) e o resultado público (results-public.png).

Uso, da raiz do repositório:
    python3 tools/imagens_manual/capa.py PASTA_DAS_CAPTURAS_BRUTAS
Precisa do Pillow (`pip install pillow`).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import anotar  # noqa: E402,F401  (só para achar a raiz do repositório)

RAIZ = anotar.RAIZ
LARGURA = 1400
FUNDO = (255, 255, 255)
BORDA = (208, 215, 222)
TEXTO = (36, 41, 47)
CINZA = (87, 96, 106)
AZUL = (31, 136, 61)
LARGURA_CARTAO = 660
# captura bruta, região (x0, y0, x1, y1) em pixels da captura e legenda de cada cartão
CARTOES = [
    ('booth-question.png', (49, 20, 1051, 500), '1. Escolha na cabine de votação'),
    ('results-public.png', (60, 262, 1040, 742), '2. Qualquer pessoa confere o resultado'),
]


def fonte(tam, negrito=False):
    nome = 'DejaVuSans-Bold.ttf' if negrito else 'DejaVuSans.ttf'
    for pasta in ('/usr/share/fonts/truetype/dejavu/', '/usr/share/fonts/dejavu/'):
        if os.path.exists(pasta + nome):
            return ImageFont.truetype(pasta + nome, tam)
    return ImageFont.load_default()


def cartao(bruta, regiao):
    """Recorte limpo da captura (sem marcas), reduzido para LARGURA_CARTAO de largura."""
    img = Image.open(bruta).convert('RGB').crop(regiao)
    altura = round(img.size[1] * LARGURA_CARTAO / img.size[0])
    return img.resize((LARGURA_CARTAO, altura), Image.LANCZOS)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    entrada = sys.argv[1]
    logo = Image.open(os.path.join(RAIZ, 'server_ui', 'media', 'logo.png')).convert('RGBA')
    logo = logo.resize((round(logo.size[0] * 130 / logo.size[1]), 130), Image.LANCZOS)
    cartoes = [(cartao(os.path.join(entrada, n), r), t) for n, r, t in CARTOES]
    alt_cartao = max(c[0].size[1] for c in cartoes)
    altura = 40 + 130 + 24 + 40 + 36 + alt_cartao + 70 + 20
    capa = Image.new('RGB', (LARGURA, altura), FUNDO)
    d = ImageDraw.Draw(capa)
    capa.paste(logo, ((LARGURA - logo.size[0]) // 2, 40), logo)
    y = 40 + 130 + 24
    d.text((LARGURA // 2, y + 20), 'Eleições online verificáveis, em português do Brasil',
           fill=TEXTO, font=fonte(30, True), anchor='mm')
    y += 40 + 36
    folga = (LARGURA - len(cartoes) * LARGURA_CARTAO) // (len(cartoes) + 1)
    for i, (img, legenda) in enumerate(cartoes):
        x = folga + i * (LARGURA_CARTAO + folga)
        h = img.size[1]
        sombra = Image.new('RGBA', (LARGURA_CARTAO + 40, h + 40), (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rectangle((20, 24, 20 + LARGURA_CARTAO, 24 + h), fill=(0, 0, 0, 70))
        sombra = sombra.filter(ImageFilter.GaussianBlur(8))
        capa.paste(sombra, (x - 20, y - 20), sombra)
        capa.paste(img, (x, y))
        d.rectangle((x - 1, y - 1, x + LARGURA_CARTAO, y + h), outline=BORDA, width=2)
        d.text((x + LARGURA_CARTAO // 2, y + alt_cartao + 40), legenda, fill=CINZA, font=fonte(22, True), anchor='mm')
    d.rectangle((0, 0, LARGURA - 1, altura - 1), outline=BORDA, width=2)
    destino = os.path.join(RAIZ, 'docs', 'images', 'capa.png')
    capa.save(destino, optimize=True)
    print(destino, capa.size)


if __name__ == '__main__':
    main()
