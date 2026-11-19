from h import *
dm = json.load(open('demo.json')); u = dm['u']; trail = json.load(open('trail.json'))['trail']
c = Aba()
c.ir(f'{B}/booth/single-ballot-verify.pt-BR.html?election_url=/helios/elections/{u}', 3)
c.js("document.querySelector('textarea[name=audit_trail]').value=%s" % json.dumps(trail))
c.clique('Verificar'); time.sleep(6)
t = re.sub(r'\s+', ' ', c.texto()); p(t[-260:])
c.js("window.scrollTo(0, 99999)"); time.sleep(0.5)
foto(c, 'verificador-cedula', 1100, 900, cheia=True)
c.fechar()

a = alice('francisca@exemplo.org')
time.sleep(10)
a.ir(f'{B}/helios/elections/{u}/compute_tally', 1)
a.clique('calcular a apuração cifrada'); a.esperar_carregar(); time.sleep(4)
for _ in range(30):
    time.sleep(3)
    a.ir(f'{B}/helios/elections/{u}/view', 0.3)
    if 'Próximo passo: apuradores' in a.vis(0, 3000):
        break
p(re.search(r'Próximo passo: [^.]{0,80}', a.vis(0, 3000)))
a.fechar()

b = Aba()
b.ir(dm['link'], 2)
dec = re.search(r'(/\S*decrypt-and-prove)', b.js("[...document.querySelectorAll('a')].map(x=>x.getAttribute('href')).join(' ')")).group(1)
foto(b, 'apurador-painel-apuracao', 1100, 560)
b.ir(B + dec, 3)
foto(b, 'decifragem-1', 1100, 800, cheia=True)
b.js("document.querySelector('#sk_textarea').value=%s" % json.dumps(dm['sk']))
b.clique('Gerar a decifragem'); time.sleep(10)
foto(b, 'decifragem', 1100, 800, cheia=True)
ok = b.clique('Enviar os fatores'); b.esperar_carregar(); time.sleep(4)
p('enviou', ok, b.vis(60, 200))
foto(b, 'decifragem-pronto', 1100, 560)
b.fechar()
