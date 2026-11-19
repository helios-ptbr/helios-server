"""Apoio para refazer as imagens do manual: Chrome por CDP (porta 9222, aba nova em contexto isolado). Veja o LEIAME.md."""
import base64, json, os, re, time, urllib.request
from urllib.parse import urlencode

import websocket

B = 'https://localhost:8443'
CDP = 'http://127.0.0.1:9222'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'images', 'manual', 'pt-BR')


class Aba:
    def __init__(self):
        v = json.load(urllib.request.urlopen(CDP + '/json/version'))
        self.br = websocket.create_connection(v['webSocketDebuggerUrl'], timeout=90, suppress_origin=True)
        self._id = 0
        self.log = []
        self.dialogos = []
        r = self._br('Target.createBrowserContext', {'disposeOnDetach': True})
        self.ctx = r['browserContextId']
        r = self._br('Target.createTarget', {'url': 'about:blank', 'browserContextId': self.ctx})
        r = self._br('Target.attachToTarget', {'targetId': r['targetId'], 'flatten': True})
        self.sid = r['sessionId']
        for d in ('Page', 'Runtime', 'Network'):
            self.cmd(d + '.enable')
        self.cmd('Security.setIgnoreCertificateErrors', {'ignore': True})

    def _send(self, method, params, sid=None):
        self._id += 1
        m = {'id': self._id, 'method': method, 'params': params or {}}
        if sid:
            m['sessionId'] = sid
        self.br.send(json.dumps(m))
        return self._id

    def _wait(self, i):
        while True:
            m = json.loads(self.br.recv())
            if m.get('id') == i:
                if 'error' in m:
                    raise RuntimeError(str(m['error']))
                return m.get('result', {})
            mt = m.get('method', '')
            if mt in ('Runtime.exceptionThrown', 'Network.loadingFailed'):
                self.log.append(m)
            if mt == 'Page.javascriptDialogOpening':
                self.dialogos.append(m['params'].get('message'))
                self._send('Page.handleJavaScriptDialog', {'accept': True}, self.sid)

    def _br(self, method, params=None):
        return self._wait(self._send(method, params))

    def cmd(self, method, params=None):
        return self._wait(self._send(method, params, self.sid))

    def js(self, expr):
        r = self.cmd('Runtime.evaluate', {'expression': expr, 'returnByValue': True, 'awaitPromise': True})
        if 'exceptionDetails' in r:
            raise RuntimeError(str(r['exceptionDetails'])[:300])
        return r['result'].get('value')

    def esperar_carregar(self, t=30):
        fim = time.time() + t
        while time.time() < fim:
            try:
                if self.js('document.readyState') == 'complete':
                    return
            except RuntimeError:
                pass
            time.sleep(0.2)

    def ir(self, url, espera=1.0):
        self.cmd('Page.navigate', {'url': url})
        self.esperar_carregar()
        time.sleep(espera)

    def texto(self):
        return self.js('document.body.innerText')

    def vis(self, a=0, n=700):
        return re.sub(r'\s+', ' ', self.texto())[a:a + n]

    def url(self):
        return self.js('location.href')

    def clique(self, txt):
        return self.js("""(()=>{const t=%s;const e=[...document.querySelectorAll('input,button,a')].filter(x=>x.offsetParent&&((x.value||x.textContent||'').trim().toLowerCase().startsWith(t.toLowerCase())))[0];if(!e)return false;e.click();return true})()""" % json.dumps(txt))

    def fechar(self):
        try:
            self._br('Target.disposeBrowserContext', {'browserContextId': self.ctx})
        finally:
            self.br.close()


def fetch(a, url, method='GET', body=None):
    opts = {'method': method, 'credentials': 'same-origin'}
    if body is not None:
        opts['headers'] = {'Content-Type': 'application/x-www-form-urlencoded'}
        opts['body'] = body
    js = f"""(async()=>{{const r=await fetch({json.dumps(url)},{json.dumps(opts)});const t=await r.text();return JSON.stringify([r.status,r.url,t]);}})()"""
    return json.loads(a.js(js))


def uuid_de(a, short):
    st, url, _ = fetch(a, f'{B}/helios/e/{short}')
    return url.rstrip('/').split('/')[-2] if '/elections/' in url else None


def tok(a):
    return a.js("(window.CSRF_TOKEN)||document.querySelector('input[name=csrf_token]')?.value||''")


def post(a, pagina, caminho, dados=None):
    a.ir(B + pagina, 0.5)
    d = {'csrf_token': tok(a)}
    d.update(dados or {})
    return fetch(a, B + caminho, 'POST', urlencode(d))


def senhas(short):
    d = json.load(urllib.request.urlopen('http://localhost:8025/api/v1/messages?limit=200'))
    r = {}
    for m in d['messages']:
        t = json.load(urllib.request.urlopen('http://localhost:8025/api/v1/message/' + m['ID']))['Text']
        l = re.search(r'ID do eleitor: (\S+)\s+Sua senha: (\S+)', t)
        e = re.search(r'/e/([^/]+)/vote', t)
        if l and e and e.group(1) == short:
            r.setdefault(l.group(1), l.group(2))
    return r


def alice(login='alice'):
    a = Aba()
    a.ir(B + '/auth/password/login', 1)
    a.js("(()=>{const f=document.forms[0];f.username.value=%s;f.password.value='alice-senha-1';f.querySelector('[type=submit]').click()})()" % json.dumps(login))
    a.esperar_carregar()
    time.sleep(1.5)
    return a


def tamanho(a, w, h):
    a.cmd('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': False})
    time.sleep(0.4)


def foto(a, nome, w=1085, h=805, cheia=False):
    a.cmd('Emulation.setScrollbarsHidden', {'hidden': True})
    tamanho(a, w, h)
    if cheia:
        alt = a.js('Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)')
        tamanho(a, w, max(h, alt))
        time.sleep(0.4)
        alt2 = a.js('Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)')
        if alt2 > max(h, alt):
            tamanho(a, w, alt2)
    d = a.cmd('Page.captureScreenshot', {'format': 'png'})['data']
    open(f'{OUT}/{nome}.png', 'wb').write(base64.b64decode(d))
    a.cmd('Emulation.setScrollbarsHidden', {'hidden': False})
    tamanho(a, w, h)
    print('foto', nome, flush=True)


def preencher(a, campos):
    """Preenche o campo VISÍVEL de cada nome (a página de questões tem formulários de edição escondidos)."""
    a.js("""(()=>{const c=%s;for(const k in c){const l=[...document.querySelectorAll('[name="'+k+'"]')];const e=l.filter(x=>x.offsetParent)[0]||l[0];if(!e)continue;if(e.type=='checkbox')e.checked=!!c[k];else e.value=c[k];e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}})()""" % json.dumps(campos))


def p(*x):
    print(*x, flush=True)
