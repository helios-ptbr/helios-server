"""Eleição de demonstração para as capturas de apurador, auditoria e verificadores (parte 1: criar e gerar a chave)."""
from h import *

SHORT = 'clube-demo'
TITULO = 'Eleição de Demonstração do Clube'
CSV = "password,joao,joao@exemplo.org,João da Silva\n"
a = alice('francisca@exemplo.org')
a.ir(B + '/helios/elections/new', 1)
preencher(a, {'short_name': SHORT, 'name': TITULO, 'description': 'Eleição só para as capturas dos manuais.', 'help_email': 'ajuda@exemplo.org'})
a.clique('Próximo'); a.esperar_carregar(); time.sleep(2)
u = uuid_de(a, SHORT)
p('eleição', u)
a.ir(f'{B}/helios/elections/{u}/questions', 2)
preencher(a, {'question': 'Quais autores vamos ler no próximo semestre?', 'min': '0', 'max': '2',
              'answer_1': 'Machado de Assis', 'answer_2': 'Graciliano Ramos', 'answer_3': 'Cora Coralina', 'answer_4': 'Clarice Lispector'})
a.clique('Adicionar a questão'); time.sleep(3)
a.ir(f'{B}/helios/elections/{u}/voters/upload', 0.5)
a.js("""(async()=>{const t=document.querySelector('input[name=csrf_token]').value;const fd=new FormData();fd.append('csrf_token',t);
 fd.append('voters_file',new Blob([%s],{type:'text/csv'}),'eleitores.csv');
 const r=await fetch(location.href,{method:'POST',body:fd,credentials:'same-origin'});const h=await r.text();document.open();document.write(h);document.close();})()""" % json.dumps(CSV))
time.sleep(3)
a.clique('Sim, pode seguir'); a.esperar_carregar(); time.sleep(6)
r = post(a, f'/helios/elections/{u}/trustees/view', f'/helios/elections/{u}/trustees/new', {'name': 'Paulo', 'email': 'paulo@exemplo.org'})
p('apurador', r[0])
a.ir(f'{B}/helios/elections/{u}/trustees/view', 1)
tu = re.findall(r'trustees/([0-9a-f-]{36})/sendurl', a.js('document.documentElement.outerHTML'))[0]
r = post(a, f'/helios/elections/{u}/trustees/view', f'/helios/elections/{u}/trustees/{tu}/sendurl')
p('sendurl', r[0])
time.sleep(6)
a.fechar()
d = json.load(urllib.request.urlopen('http://localhost:8025/api/v1/messages?limit=200'))
link = None
for m in d['messages']:
    if m['To'][0]['Address'] == 'paulo@exemplo.org':
        t = json.load(urllib.request.urlopen('http://localhost:8025/api/v1/message/' + m['ID']))['Text']
        if SHORT in t:
            link = re.search(r'https://\S+', t).group(0); break
p('link', link)

b = Aba()
b.ir(link, 2)
foto(b, 'apurador-painel-antes', 1100, 560)
kg = re.search(r'-> (/[^ ]*keygenerator)', b.js("[...document.querySelectorAll('a')].map(x=>x.textContent.trim()+' -> '+x.getAttribute('href')).join(' | ')")).group(1)
b.ir(B + kg, 3)
foto(b, 'gerar-chave', 1100, 700)
b.clique('Gerar as chaves'); time.sleep(8)
b.clique('Mostrar a minha chave'); time.sleep(1)
sk = b.js("document.querySelector('#sk_content').value || document.querySelector('#sk_content').textContent")
foto(b, 'chave-secreta', 1100, 800)
b.clique('ok, já guardei'); time.sleep(1)
b.clique('Enviar a sua chave pública'); b.esperar_carregar(); time.sleep(2)
foto(b, 'apurador-painel', 1100, 560)
p(b.vis(60, 200))
b.fechar()
json.dump({'u': u, 'link': link, 'sk': sk}, open('demo.json', 'w'))
