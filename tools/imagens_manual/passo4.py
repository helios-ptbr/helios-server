"""Exemplo do tutorial (parte 4): apuração, decifragem pela curadoria, resultado, páginas públicas."""
from h import *

SHORT = 'clube-leitura-2026'
u = json.load(open('manual.json'))['u']
links = json.load(open('links_curadoria.json'))
chaves = json.load(open('chaves_secretas.json'))

a = alice('francisca@exemplo.org')
time.sleep(12)  # o worker verifica as cédulas
a.ir(f'{B}/helios/elections/{u}/compute_tally', 1)
foto(a, 'compute-tally')
a.clique('calcular a apuração cifrada')
a.esperar_carregar()
time.sleep(4)
for _ in range(40):
    time.sleep(3)
    a.ir(f'{B}/helios/elections/{u}/view', 0.3)
    if 'curadoria' in a.vis(0, 3000) and 'Próximo passo: curadoria' in a.vis(0, 3000):
        break
p('próximo:', re.search(r'Próximo passo: [^.]{0,80}', a.vis(0, 3000)).group(0))
a.fechar()

for email, link in links.items():
    b = Aba()
    b.ir(link, 2)
    dec = re.search(r'(/\S*decrypt-and-prove)', b.js("[...document.querySelectorAll('a')].map(x=>x.getAttribute('href')).join(' ')")).group(1)
    b.ir(B + dec, 3)
    b.js("document.querySelector('#sk_textarea').value=%s" % json.dumps(chaves[email]))
    b.clique('Gerar a decifragem')
    time.sleep(10)
    ok = b.clique('Enviar os fatores')
    b.esperar_carregar()
    time.sleep(4)
    p(email, 'enviou:', ok, '| diálogos', b.dialogos, '| erros JS', len([m for m in b.log if m['method'] == 'Runtime.exceptionThrown']))
    b.fechar()

a = alice('francisca@exemplo.org')
a.ir(f'{B}/helios/elections/{u}/view', 1)
p('antes de combinar:', re.search(r'Próximo passo: [^.]{0,90}', a.vis(0, 3000)).group(0))
r = post(a, f'/helios/elections/{u}/view', f'/helios/elections/{u}/combine_decryptions')
p('combinar', r[0])
a.ir(f'{B}/helios/elections/{u}/view', 1)
p('resultado:', re.search(r'Apuração.*', a.vis(0, 3000)).group(0)[:300])
foto(a, 'results-admin', cheia=True)
a.ir(f'{B}/helios/elections/{u}/release_result', 1)
foto(a, 'release')
a.clique('Liberar')
a.esperar_carregar()
time.sleep(3)
a.fechar()

b = Aba()
b.ir(f'{B}/helios/e/{SHORT}', 2)
p('público:', b.vis(60, 200))
foto(b, 'results-public')
b.ir(f'{B}/helios/elections/{u}/voters/list', 1)
foto(b, 'tracking-center')
b.fechar()
