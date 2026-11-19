"""Demonstração, parte 2: congelar, e-mail, auditoria na cabine (publica a cédula auditada), voto de verdade e verificador."""
from h import *

SHORT = 'clube-demo'
TITULO = 'Eleição de Demonstração do Clube'
dm = json.load(open('demo.json'))
u = dm['u']

s = senhas(SHORT)


def marcar(a, rotulos):
    return a.js("""(()=>{const want=%s;let n=0;for(const l of document.querySelectorAll('label')){const t=l.textContent.trim();if(want.includes(t)){(l.control||document.getElementById(l.htmlFor)||l.querySelector('input')).click();n++}}return n})()""" % json.dumps(rotulos))


def preencher_cabine(b, escolhas):
    b.ir(f'{B}/helios/e/{SHORT}/vote', 4)
    b.clique('Iniciar'); time.sleep(2)
    marcar(b, escolhas)
    b.clique('Prosseguir') or b.clique('Próximo'); time.sleep(3)


# 1) auditoria
b = Aba()
preencher_cabine(b, ['Graciliano Ramos'])
p('revisão?', 'Revise' in b.texto())
foto(b, 'cabine-revisao-auditar', 1100, 800, cheia=True)
b.clique('Anular e auditar'); time.sleep(1)
foto(b, 'cabine-anular', 1100, 800, cheia=True)
b.js("[...document.querySelectorAll('a,button,input')].filter(x=>x.offsetParent&&(x.value||x.textContent).trim().startsWith('Anular e auditar')).pop().click()"); time.sleep(4)
p('auditoria:', b.vis(0, 200))
foto(b, 'cedula-auditada', 1100, 800, cheia=True)
trail = b.js("document.querySelector('#audit_trail').value")
json.dump({'trail': trail}, open('trail.json', 'w'))
p('trail', len(trail))
b.clique('publicar cédula auditada'); time.sleep(3)
p('diálogos', b.dialogos)
b.fechar()

# 2) voto de verdade
b = Aba()
preencher_cabine(b, ['Machado de Assis', 'Cora Coralina'])
b.clique('Prosseguir para o login'); time.sleep(8)
b.js(f"document.querySelector('#id_voter_id').value='joao';document.querySelector('#id_password').value={json.dumps(s['joao'])}")
b.js("document.querySelector('input[type=submit],button[type=submit]').click()")
b.esperar_carregar(); time.sleep(3)
p('voto:', b.url().split('/')[-1], b.vis(60, 120))
b.fechar()

# 3) página de cédulas auditadas e verificador de cédula única
c = Aba()
c.ir(f'{B}/helios/elections/{u}/audited-ballots/', 1)
p(c.vis(60, 300))
foto(c, 'cedulas-auditadas', 1100, 640)
c.ir(f'{B}/booth/single-ballot-verify.pt-BR.html?election_url=/helios/elections/{u}', 3)
c.js("document.querySelector('textarea[name=audit_trail]').value=%s" % json.dumps(trail))
foto(c, 'verificador-cedula-antes', 1100, 640)
c.clique('Verificar'); time.sleep(5)
p(c.vis(0, 300))
foto(c, 'verificador-cedula', 1100, 640)
c.fechar()
