"""Teste de CSV grande: envia N eleitores pelo navegador (Caddy -> web -> worker) e mede tempo e memória. Uso: python3 passo7.py N"""
import subprocess, threading, sys
from h import *

N = int(sys.argv[1])
SHORT = 'csv-%d' % N
amostras = {}
parar = False


def mem():
    while not parar:
        out = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{.Name}} {{.MemUsage}}'], capture_output=True, text=True, cwd='/home/rolim/du/dev/github/helios-server').stdout
        for l in out.splitlines():
            nome, uso = l.split()[0], l.split()[1]
            v = float(re.sub('[A-Za-z]+', '', uso)); un = re.sub('[0-9.]+', '', uso)
            mib = v * {'KiB': 1/1024, 'MiB': 1, 'GiB': 1024, 'B': 1/1048576}.get(un, 1)
            amostras[nome] = max(amostras.get(nome, 0), mib)


t = threading.Thread(target=mem, daemon=True); t.start()
a = alice('francisca@exemplo.org')
a.ir(B + '/helios/elections/new', 1)
preencher(a, {'short_name': SHORT, 'name': 'CSV %d' % N, 'description': 'teste de CSV grande', 'help_email': 'ajuda@exemplo.org'})
a.clique('Próximo'); a.esperar_carregar(); time.sleep(2)
u = uuid_de(a, SHORT)
a.ir(f'{B}/helios/elections/{u}/voters/upload', 0.5)
t0 = time.time()
r = a.js("""(async()=>{const n=%d;const linhas=new Array(n);for(let i=0;i<n;i++)linhas[i]='password,v'+i+',v'+i+'@exemplo.org,Eleitor Numero '+i;
 const csv=linhas.join('\\n')+'\\n';const t=document.querySelector('input[name=csrf_token]').value;const fd=new FormData();fd.append('csrf_token',t);
 fd.append('voters_file',new Blob([csv],{type:'text/csv'}),'eleitores.csv');
 const t0=performance.now();const r=await fetch(location.href,{method:'POST',body:fd,credentials:'same-origin'});const h=await r.text();
 document.open();document.write(h);document.close();return JSON.stringify([r.status,csv.length,Math.round(performance.now()-t0)])})()""" % N)
p('envio (status, bytes, ms):', r)
time.sleep(2)
t1 = time.time()
import os
if os.environ.get('SEM_CONFIRMAR'):
    p('sem confirmar (só o envio)'); parar = True; time.sleep(2); p('pico de memória (MiB):', {k.replace('helios-carga-', ''): round(v) for k, v in amostras.items() if 'web' in k or 'worker' in k or 'db' in k}); a.fechar(); sys.exit()
ok = a.clique('Sim, pode seguir')
a.esperar_carregar()
p('confirmou:', ok, 'em %.1f s' % (time.time() - t1))
fim = None
for _ in range(600):
    time.sleep(2)
    o = subprocess.run(['docker', 'compose', 'exec', '-T', 'db', 'psql', '-U', 'helios', '-d', 'helios', '-Atc',
                        "select processing_finished_at is not null, num_voters, extract(epoch from (processing_finished_at-processing_started_at)) from helios_voterfile order by id desc limit 1"],
                       capture_output=True, text=True, cwd='/home/rolim/du/dev/github/helios-server').stdout.strip()
    if o.startswith('t'):
        fim = o; break
p('processamento:', fim, 'total %.0f s desde o envio' % (time.time() - t0))
parar = True; time.sleep(2)
p('pico de memória (MiB):', {k.replace('helios-carga-', ''): round(v) for k, v in amostras.items() if 'web' in k or 'worker' in k or 'db' in k})
a.fechar()
