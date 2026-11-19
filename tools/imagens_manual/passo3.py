"""Exemplo do tutorial (parte 3): congelar, e-mail, votos na cabine."""
from h import *

SHORT = 'clube-leitura-2026'
TITULO = 'Eleição do Clube de Leitura 2026'
u = json.load(open('manual.json'))['u']
VOTOS = [('joao', ['Machado de Assis', 'Clarice Lispector'], ['Sim']), ('jose', ['Machado de Assis', 'Cora Coralina'], ['Sim']),
         ('ana', ['Machado de Assis'], ['Não']), ('maria', ['Cora Coralina', 'Graciliano Ramos'], ['Sim'])]

a = alice('francisca@exemplo.org')
a.ir(f'{B}/helios/elections/{u}/freeze', 1)
foto(a, 'freeze')
a.clique('Congelar')
a.esperar_carregar()
time.sleep(3)
a.ir(f'{B}/helios/elections/{u}/view', 1)
p('após congelar:', a.vis(100, 360))
foto(a, 'election-open')
a.ir(f'{B}/helios/elections/{u}/voters/email', 1)
preencher(a, {'subject': TITULO, 'body': 'A votação está aberta até sexta-feira, às 17h.'})
foto(a, 'email-voters', cheia=True)
a.clique('Enviar')
a.esperar_carregar()
time.sleep(7)
s = senhas(SHORT)
p('senhas:', list(s))
json.dump(s, open('senhas.json', 'w'))
a.fechar()


def marcar(a, rotulos):
    return a.js("""(()=>{const want=%s;let n=0;for(const l of document.querySelectorAll('label')){const t=l.textContent.trim();if(want.includes(t)){(l.control||document.getElementById(l.htmlFor)||l.querySelector('input')).click();n++}}return n})()""" % json.dumps(rotulos))


for i, (login, q1, q2) in enumerate(VOTOS):
    b = Aba()
    primeiro = (i == 0)
    b.ir(f'{B}/helios/e/{SHORT}/vote', 4)
    if primeiro:
        foto(b, 'booth-start', 1100, 800)
    b.clique('Iniciar')
    time.sleep(2)
    p(login, 'q1', marcar(b, q1))
    if primeiro:
        foto(b, 'booth-question', 1100, 800)
    b.clique('Próximo')
    time.sleep(2)
    p(login, 'q2', marcar(b, q2))
    b.clique('Prosseguir') or b.clique('Próximo')
    time.sleep(2)
    p(login, 'revisão?', 'Revise' in b.texto())
    if primeiro:
        foto(b, 'booth-review', 1100, 800)
    b.clique('Prosseguir para o login')
    time.sleep(8)
    b.js(f"document.querySelector('#id_voter_id').value={json.dumps(login)};document.querySelector('#id_password').value={json.dumps(s[login])}")
    if primeiro:
        foto(b, 'cast-login')
    b.js("document.querySelector('input[type=submit],button[type=submit]').click()")
    b.esperar_carregar()
    time.sleep(3)
    p(login, b.url().split('/')[-1])
    if primeiro:
        foto(b, 'cast-done')
    b.fechar()
