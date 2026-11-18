"""Testes dos arquivos de tradução (.po) do fork helios-ptbr. Cobrem as issues #18, #19 e #20.

- #18: o django.po está em dia com o código (rodar makemessages não acha texto novo nem sobrando).
- #19: nenhuma entrada vazia ou "fuzzy".
- #20: os marcadores (%(nome)s, %s, %d, {0}) são os mesmos no original e na tradução.

Não alteram os testes do upstream.
"""
import ast
import os
import re
import shutil
import subprocess
import sys
import unittest
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALE = os.path.join(ROOT, 'locale', 'pt_BR', 'LC_MESSAGES')
DOMINIOS = ['django', 'booth', 'booth_html', 'verifier', 'verifier_html']


def ler_po(caminho):
    """Lê um .po e devolve a lista de entradas (sem o cabeçalho e sem as obsoletas)."""
    entradas = []
    atual = None
    campo = None
    flags = []

    def fechar():
        nonlocal atual
        if atual is not None and atual.get('id') is not None:
            entradas.append(atual)
        atual = None

    with open(caminho, encoding='utf-8') as f:
        linhas = f.read().split('\n')
    for linha in linhas:
        if linha.startswith('#~'):
            continue
        if linha.startswith('#,'):
            if atual is not None and 'id' in atual and campo is not None:
                fechar()
            flags = [x.strip() for x in linha[2:].split(',')]
            continue
        if linha.startswith('#'):
            if atual is not None and campo is not None and campo.startswith('str'):
                fechar()
                flags = []
            continue
        if not linha.strip():
            if atual is not None:
                fechar()
            campo = None
            flags = []
            continue
        m = re.match(r'^(msgctxt|msgid_plural|msgid|msgstr(?:\[\d+\])?)\s+(".*")\s*$', linha)
        if m:
            nome, texto = m.group(1), ast.literal_eval(m.group(2))
            if atual is None or (nome in ('msgctxt', 'msgid') and campo is not None and campo.startswith('str')):
                fechar()
                atual = {'ctxt': None, 'id': None, 'plural': None, 'str': {}, 'fuzzy': 'fuzzy' in flags}
            if nome == 'msgctxt':
                campo = 'ctxt'
                atual['ctxt'] = texto
            elif nome == 'msgid':
                campo = 'id'
                atual['id'] = texto
            elif nome == 'msgid_plural':
                campo = 'plural'
                atual['plural'] = texto
            else:
                idx = int(re.search(r'\[(\d+)\]', nome).group(1)) if '[' in nome else 0
                campo = 'str%d' % idx
                atual['str'][idx] = texto
            continue
        m = re.match(r'^(".*")\s*$', linha)
        if m and atual is not None and campo is not None:
            texto = ast.literal_eval(m.group(1))
            if campo in ('ctxt', 'id', 'plural'):
                atual[campo] += texto
            else:
                atual['str'][int(campo[3:])] += texto
    fechar()
    return [e for e in entradas if e['id'] != '']  # cabeçalho sai


MARCADOR = re.compile(r'%\([A-Za-z_][A-Za-z0-9_]*\)[sdifrx]|%[sdifrx]|\{[A-Za-z0-9_]*\}')


def marcadores(texto):
    # '%%(nome)s' é como o texto aparece depois do blocktranslate: conta como marcador.
    # Outros '%%' são só um '%' literal.
    texto = texto.replace('%%(', '%(').replace('%%', '')
    return Counter(MARCADOR.findall(texto))


class ArquivoPoTests(unittest.TestCase):

    def test_arquivos_existem_e_tem_entradas(self):
        for d in DOMINIOS:
            with self.subTest(dominio=d):
                self.assertGreater(len(ler_po(os.path.join(LOCALE, d + '.po'))), 0)

    def test_leitor_entende_plural_contexto_e_linhas_continuadas(self):
        import tempfile
        conteudo = (
            'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
            '#: a.py:1\n#, fuzzy\nmsgid "Um"\nmsgstr "Uno"\n\n'
            'msgctxt "col"\nmsgid "Login"\nmsgstr ""\n"Nome "\n"de acesso"\n\n'
            'msgid "%(n)d dia"\nmsgid_plural "%(n)d dias"\nmsgstr[0] "%(n)d dia"\nmsgstr[1] "%(n)d dias"\n')
        with tempfile.NamedTemporaryFile('w', suffix='.po', delete=False, encoding='utf-8') as f:
            f.write(conteudo)
        try:
            e = ler_po(f.name)
        finally:
            os.unlink(f.name)
        self.assertEqual(len(e), 3)
        self.assertTrue(e[0]['fuzzy'])
        self.assertEqual((e[1]['ctxt'], e[1]['str'][0]), ('col', 'Nome de acesso'))
        self.assertEqual((e[2]['plural'], e[2]['str'][1]), ('%(n)d dias', '%(n)d dias'))

    # ---- #19 -------------------------------------------------------------
    def test_sem_entrada_vazia_ou_fuzzy(self):
        for d in DOMINIOS:
            for e in ler_po(os.path.join(LOCALE, d + '.po')):
                with self.subTest(dominio=d, msgid=e['id'][:60]):
                    self.assertFalse(e['fuzzy'], 'entrada "fuzzy"')
                    self.assertTrue(e['str'], 'sem msgstr')
                    for idx, s in e['str'].items():
                        self.assertNotEqual(s.strip(), '', 'msgstr[%d] vazio' % idx)

    # ---- #20 -------------------------------------------------------------
    def test_marcadores_iguais_no_original_e_na_traducao(self):
        for d in DOMINIOS:
            for e in ler_po(os.path.join(LOCALE, d + '.po')):
                esperado = marcadores(e['id'])
                if e['plural'] is not None:
                    esperado_plural = marcadores(e['plural'])
                for idx, s in e['str'].items():
                    with self.subTest(dominio=d, msgid=e['id'][:60], idx=idx):
                        tem = marcadores(s)
                        if e['plural'] is not None:
                            # nomes iguais aos do plural; o singular pode omitir o número
                            nomes = set(esperado_plural)
                            self.assertTrue(set(tem) <= nomes, 'marcador desconhecido: %s' % (set(tem) - nomes))
                            if idx > 0 or len(e['str']) == 1:
                                self.assertEqual(tem, esperado_plural)
                        else:
                            self.assertEqual(tem, esperado)

    def test_msgfmt_aprova_o_django_po(self):
        msgfmt = shutil.which('msgfmt')
        if not msgfmt:
            self.skipTest('msgfmt não instalado (pacote gettext)')
        for d in DOMINIOS:
            with self.subTest(dominio=d):
                r = subprocess.run([msgfmt, '--check', '--check-format', '-o', os.devnull,
                                    os.path.join(LOCALE, d + '.po')], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)

    # ---- #18 -------------------------------------------------------------
    def test_django_po_esta_em_dia_com_o_codigo(self):
        if not shutil.which('xgettext'):
            self.skipTest('xgettext não instalado (pacote gettext)')
        po = os.path.join(LOCALE, 'django.po')
        copia = po + '.teste-bak'
        shutil.copy2(po, copia)
        try:
            antes = {(e['ctxt'], e['id'], e['plural']) for e in ler_po(po)}
            env = dict(os.environ, DJANGO_SETTINGS_MODULE='settings_ptbr')
            r = subprocess.run([sys.executable, 'manage.py', 'makemessages', '-l', 'pt_BR', '--no-obsolete',
                                '--no-location', '-i', '.venv', '-i', 'node_modules'],
                               cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
            self.assertEqual(r.returncode, 0, r.stderr[-800:])
            depois = {(e['ctxt'], e['id'], e['plural']) for e in ler_po(po)}
        finally:
            shutil.move(copia, po)  # devolve o arquivo original, aconteça o que acontecer
        novos = sorted(i[1][:70] for i in depois - antes)
        sobrando = sorted(i[1][:70] for i in antes - depois)
        self.assertEqual((novos, sobrando), ([], []),
                         'rode "python manage.py makemessages -l pt_BR" e traduza os textos novos; '
                         'apague os que sobraram')


if __name__ == '__main__':
    unittest.main()
