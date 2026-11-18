"""Escolhe a página da cabine de votação conforme o idioma ativo.

Para o idioma 'pt-br' do Django, usa heliosbooth/vote.pt-BR.html se ela existir
(veja tools/gen_booth_pages.py). Sem página do idioma, usa vote.html (inglês).
Fica fora do pacote helios para não depender do Django nos testes.
"""
import os
import re

_LANG_RE = re.compile(r'([a-z]{2,3})(?:-([a-z0-9]{2,8}))?')
_BOOTH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heliosbooth')
DEFAULT_PAGE = 'vote.html'


def page_for_language(lang, booth_dir=_BOOTH_DIR):
    """'pt-br' -> 'vote.pt-BR.html' (se o arquivo existir); senão 'vote.html'."""
    m = _LANG_RE.fullmatch((lang or '').lower().replace('_', '-'))
    if not m:
        return DEFAULT_PAGE
    code = m.group(1) + ('-' + m.group(2).upper() if m.group(2) else '')
    for candidate in (code, m.group(1)):
        name = 'vote.%s.html' % candidate
        if os.path.isfile(os.path.join(booth_dir, name)):
            return name
    return DEFAULT_PAGE


def booth_page():
    """Página da cabine para o idioma da requisição atual."""
    from django.utils import translation
    return page_for_language(translation.get_language())
