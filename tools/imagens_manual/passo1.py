"""Exemplo do tutorial (parte 1): clube de leitura, nomes brasileiros."""
from h import *

SHORT = 'clube-leitura-2026'
TITULO = 'Eleição do Clube de Leitura 2026'
CSV = ("password,joao,joao@exemplo.org,João da Silva\npassword,jose,jose@exemplo.org,José dos Santos\n"
       "password,ana,ana@exemplo.org,Ana Maria Souza\npassword,maria,maria@exemplo.org,Maria José Pereira\n")
CUR = [('Paulo', 'paulo@exemplo.org'), ('Gabriel', 'gabriel@exemplo.org'), ('Juliana', 'juliana@exemplo.org'), ('Antônia', 'antonia@exemplo.org')]

a = alice('francisca-inicio@exemplo.org')
a.ir(B + '/', 1)
foto(a, 'admin-home', 1100, 800)
a.fechar()

a = alice('francisca@exemplo.org')
a.ir(B + '/helios/elections/new', 1)
preencher(a, {'short_name': SHORT, 'name': TITULO,
              'description': 'Escolher as leituras do semestre e a compra de livros do clube.',
              'help_email': 'ajuda@exemplo.org'})
foto(a, 'new-election', cheia=True)
a.clique('Próximo')
a.esperar_carregar()
time.sleep(2)
u = uuid_de(a, SHORT)
p('eleição', u)
json.dump({'u': u}, open('manual.json', 'w'))

a.ir(f'{B}/helios/elections/{u}/questions', 2)
preencher(a, {'question': 'Quais autores vamos ler no próximo semestre?', 'min': '0', 'max': '2',
              'answer_1': 'Machado de Assis', 'answer_2': 'Graciliano Ramos', 'answer_3': 'Cora Coralina', 'answer_4': 'Clarice Lispector'})
foto(a, 'question-form', cheia=True)
a.clique('Adicionar a questão')
time.sleep(3)
a.ir(f'{B}/helios/elections/{u}/questions', 2)
preencher(a, {'question': 'Aprovar a compra de livros para a biblioteca do clube?', 'min': '0', 'max': '1', 'answer_1': 'Sim', 'answer_2': 'Não'})
a.clique('Adicionar a questão')
time.sleep(3)
a.ir(f'{B}/helios/elections/{u}/questions', 2)
p('questões:', re.findall(r'\d\. [^?]*\?', a.vis(0, 800)))
foto(a, 'questions', cheia=True)

a.ir(f'{B}/helios/elections/{u}/voters/list', 1)
foto(a, 'voters-empty')
a.ir(f'{B}/helios/elections/{u}/voters/upload', 0.5)
a.js("""(async()=>{const t=document.querySelector('input[name=csrf_token]').value;const fd=new FormData();fd.append('csrf_token',t);
 fd.append('voters_file',new Blob([%s],{type:'text/csv'}),'eleitores.csv');
 const r=await fetch(location.href,{method:'POST',body:fd,credentials:'same-origin'});const h=await r.text();document.open();document.write(h);document.close();})()""" % json.dumps(CSV))
time.sleep(3)
foto(a, 'voters-confirm')
p('confirmar:', a.clique('Sim, pode seguir') or a.clique('Sim'))
a.esperar_carregar()
time.sleep(8)
a.ir(f'{B}/helios/elections/{u}/voters/list', 1)
p('lista:', re.search(r'processamento concluído[^.]*', a.vis(0, 1500)))
foto(a, 'voters-list', cheia=True)

# apuradores: o Helios mais quatro pessoas
a.ir(f'{B}/helios/elections/{u}/trustees/view', 1)
foto(a, 'trustees-vazio', cheia=False)
for nome, email in CUR:
    r = post(a, f'/helios/elections/{u}/trustees/view', f'/helios/elections/{u}/trustees/new', {'name': nome, 'email': email})
    p('apuradores', nome, r[0])
a.ir(f'{B}/helios/elections/{u}/trustees/view', 1)
html = a.js('document.documentElement.outerHTML')
tus = re.findall(r'trustees/([0-9a-f-]{36})/sendurl', html)
p('trustees:', len(tus))
json.dump({'tus': tus}, open('trustees.json', 'w'))

# outro administrador
a.ir(f'{B}/helios/elections/{u}/admins/', 1)
foto(a, 'admins-antes')
r = post(a, f'/helios/elections/{u}/admins/add', f'/helios/elections/{u}/admins/add', {'email': 'luiz@exemplo.org'})
p('admin Luiz', r[0], re.sub(r'<[^>]+>', ' ', r[2])[:0])
a.ir(f'{B}/helios/elections/{u}/admins/', 1)
p('admins:', a.vis(0, 500))
foto(a, 'admins')
a.fechar()
