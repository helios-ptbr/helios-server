#!/usr/bin/env python3
"""Acha texto visível nos templates do Django que ficou fora de {% translate %} e {% blocktranslate %}.

Uso: python3 tools/templates_sem_traducao.py [--todos]
Só biblioteca padrão. Sem --todos, mostra só os trechos com 2 palavras ou mais.
Ignora: tags HTML, {{ variáveis }}, {% tags %}, comentários, <script>, <style> e templates *.pt-BR.html.
Serve de apoio à varredura de telas (issue #21): o que sair aqui não aparece traduzido em nenhuma tela.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASTAS = ['helios/templates', 'helios_auth/templates', 'server_ui/templates', 'templates']
# o que fica em inglês de propósito (marca, valores de código, tela só para desenvolvimento)
ARQUIVOS_IGNORADOS = {
    'helios_auth/templates/auth/devlogin.html',   # só existe com DEBUG=1
    'server_ui/templates/about.html',             # tem about.pt-BR.html
    'server_ui/templates/aviso_traducao.html',    # já está em português
    'server_ui/templates/confirm.html',           # nenhuma view usa
    'server_ui/templates/done.html',              # nenhuma view usa
    'server_ui/templates/election_tallied.html',  # sombreado por helios/templates/election_tallied.html
}
TRECHOS_IGNORADOS = {
    'Helios Voting', '- Helios',
    'password, unique_id , email&gt, full name', 'github, username',
    'password,bobsmith,bob@acme.org,Bob Smith',   # exemplo de CSV: dados, não texto da tela
}
VALORES_DE_CODIGO = re.compile(r"^atributo: (?:'|https?://|send_email$|openreg$|closedreg$|limitedreg$)")
# atributos que a pessoa vê
ATRIBUTOS = re.compile(r'\b(?:title|alt|placeholder|value|aria-label)="([^"{}]*[A-Za-z]{3,}[^"{}]*)"')


def limpar(texto):
    texto = re.sub(r'\{#.*?#\}', ' ', texto, flags=re.S)
    texto = re.sub(r'<!--.*?-->', ' ', texto, flags=re.S)
    texto = re.sub(r'<(script|style)\b.*?</\1>', ' ', texto, flags=re.S | re.I)
    # blocos traduzidos: o conteúdo está no catálogo
    texto = re.sub(r'\{%\s*blocktrans(?:late)?\b.*?\{%\s*endblocktrans(?:late)?\s*%\}', ' ', texto, flags=re.S)
    texto = re.sub(r'\{%\s*(?:translate|trans)\b.*?%\}', ' ', texto, flags=re.S)
    texto = re.sub(r'\{%.*?%\}', ' ', texto, flags=re.S)
    texto = re.sub(r'\{\{.*?\}\}', ' ', texto, flags=re.S)
    return texto


def achados(caminho):
    bruto = caminho.read_text(encoding='utf-8')
    saida = []
    for m in ATRIBUTOS.finditer(re.sub(r'\{%.*?%\}|\{\{.*?\}\}', '', bruto, flags=re.S)):
        saida.append('atributo: ' + m.group(1).strip())
    texto = limpar(bruto)
    texto = re.sub(r'<[^>]+>', '\n', texto)
    for linha in texto.split('\n'):
        linha = re.sub(r'&\w+;', ' ', linha)
        linha = ' '.join(linha.split())
        palavras = re.findall(r"[A-Za-z][A-Za-z']{2,}", linha)
        if palavras and re.search(r'[A-Za-z]{3,}', linha):
            saida.append(linha)
    return saida


def main():
    todos = '--todos' in sys.argv
    total = 0
    for pasta in PASTAS:
        for arq in sorted((ROOT / pasta).rglob('*.html')):
            if '.pt-BR.' in arq.name or '/media/' in str(arq):
                continue
            if arq.with_name(arq.stem + '.pt-BR.html').exists():
                continue  # página fixa com um template por idioma
            if str(arq.relative_to(ROOT)) in ARQUIVOS_IGNORADOS:
                continue
            ach = [a for a in achados(arq)
                   if (todos or len(a.split()) >= 2) and a not in TRECHOS_IGNORADOS and not VALORES_DE_CODIGO.match(a)
                   and not a.startswith('iframe ')]
            if ach:
                total += len(ach)
                print(f'\n{arq.relative_to(ROOT)}')
                for a in ach:
                    print('   -', a[:150])
    print(f'\n{total} trechos')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
