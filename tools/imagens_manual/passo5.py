"""Capturas extras para os manuais por papel (e-mails no Mailpit claro, apurador, verificador). Rode depois do passo4."""
from h import *

SHORT = 'clube-leitura-2026'
TITULO = 'Eleição do Clube de Leitura 2026'
u = json.load(open('manual.json'))['u']
links = json.load(open('links_apuradores.json'))
chaves = json.load(open('chaves_secretas.json'))
MP = 'http://localhost:8025'
d = json.load(urllib.request.urlopen(MP + '/api/v1/messages?limit=200'))


def msg(para, assunto, exato=False):
    for m in d['messages']:
        if m['To'][0]['Address'] == para and (m['Subject'] == assunto if exato else m['Subject'].startswith(assunto)):
            return m['ID']


def mail(nome, para, assunto, exato=False):
    a = Aba()
    a.ir(MP + '/', 1)
    a.js("localStorage.setItem('mp-theme','light')")
    a.ir(MP + '/view/' + msg(para, assunto, exato), 3)
    foto(a, nome, 1100, 760)
    a.fechar()


mail('email-eleitor', 'joao@exemplo.org', TITULO, True)
mail('email-apurador', 'paulo@exemplo.org', 'a sua página de apurador')

# verificador da eleição inteira
v = Aba()
v.ir(f'{B}/helios/e/{SHORT}', 2)
href = v.js("[...document.querySelectorAll('a')].map(x=>x.getAttribute('href')).find(h=>h&&h.indexOf('/verifier/')==0)")
p('verifier href', href)
v.ir(B + href, 2)
v.clique('iniciar a verificação')
time.sleep(25)
p(v.vis(0, 300), '...', v.vis(-250, 250) if False else '')
foto(v, 'verificador-eleicao', 1100, 800, cheia=True)  # a página é longa: recorte o começo e o fim com o Pillow
v.fechar()
