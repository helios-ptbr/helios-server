"""Exemplo do tutorial (parte 2): cada pessoa da curadoria gera a chave e envia a chave pública."""
from h import *

u = json.load(open('manual.json'))['u']
tus = json.load(open('trustees.json'))['tus']
EMAILS = ['paulo@exemplo.org', 'gabriel@exemplo.org', 'juliana@exemplo.org', 'antonia@exemplo.org']

a = alice('francisca@exemplo.org')
for tu in tus:
    r = post(a, f'/helios/elections/{u}/trustees/view', f'/helios/elections/{u}/trustees/{tu}/sendurl')
    p('sendurl', tu[:8], r[0])
time.sleep(6)
a.fechar()

d = json.load(urllib.request.urlopen('http://localhost:8025/api/v1/messages?limit=100'))
links = {}
for m in d['messages']:
    para = m['To'][0]['Address']
    if para in EMAILS and para not in links:
        t = json.load(urllib.request.urlopen('http://localhost:8025/api/v1/message/' + m['ID']))['Text']
        if 'clube-leitura-2026' in t:
            links[para] = re.search(r'https://\S+', t).group(0)
p('links:', list(links))
json.dump(links, open('links_curadoria.json', 'w'))

chaves = {}
for email, link in links.items():
    b = Aba()
    b.ir(link, 2)
    kg = re.search(r'-> (/[^ ]*keygenerator)', b.js("[...document.querySelectorAll('a')].map(x=>x.textContent.trim()+' -> '+x.getAttribute('href')).join(' | ')")).group(1)
    b.ir(B + kg, 3)
    b.clique('Gerar as chaves')
    time.sleep(8)
    b.clique('Mostrar a minha chave')
    time.sleep(1)
    sk = b.js("document.querySelector('#sk_content').value || document.querySelector('#sk_content').textContent")
    chaves[email] = sk
    b.clique('ok, já guardei')
    time.sleep(1)
    b.clique('Enviar a sua chave pública')
    b.esperar_carregar()
    time.sleep(2)
    p(email, len(sk), 'caracteres;', b.url().split('/')[-1], '|', b.vis(60, 120))
    b.fechar()
json.dump(chaves, open('chaves_secretas.json', 'w'))

a = alice('francisca@exemplo.org')
a.ir(f'{B}/helios/elections/{u}/trustees/view', 1)
p(a.vis(60, 900))
foto(a, 'trustees', cheia=True)
a.fechar()
