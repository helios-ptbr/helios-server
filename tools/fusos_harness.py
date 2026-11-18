"""Roda timezone-display.js no Chromium sem tela, com o fuso do sistema trocado (variável TZ).

Uso nos testes: executar(fuso, casos) devolve, para cada caso, o que a página mostrou ao abrir
(UTC -> local) e o que enviaria ao servidor (local -> UTC).
"""
import html
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "helios" / "media" / "timezone-display.js"

PAGINA = """<!DOCTYPE html><html lang="%(lang)s"><head><meta charset="utf-8">
<script>window.HELIOS_TZ_TEXTS = {};</script></head><body>
<form id="f" action="#" onsubmit="return false"></form>
<span id="ts" data-utc-time="%(ts)s">%(ts)s</span>
<script>
var CASOS = %(casos)s;
var form = document.getElementById('f');
CASOS.forEach(function(c, i) {
  var inp = document.createElement('input');
  inp.type = 'datetime-local'; inp.name = 'campo' + i; inp.value = c.utc;
  form.appendChild(inp);
});
</script>
<script src="file://%(js)s"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  var out = {aberto: [], enviado: [], tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
             offset: new Date().getTimezoneOffset(), ts: document.getElementById('ts').textContent};
  var inputs = form.querySelectorAll('input[type=datetime-local]');
  Array.prototype.forEach.call(inputs, function(inp) { out.aberto.push(inp.value); });
  // a pessoa digita o horário local de cada caso (ou deixa o que veio) e envia
  CASOS.forEach(function(c, i) { if (c.digitado) { inputs[i].value = c.digitado; } });
  form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    var fd = new FormData(form);
    CASOS.forEach(function(c, i) { out.enviado.push(fd.get('campo' + i)); });
    var pre = document.createElement('pre'); pre.id = 'saida';
    pre.textContent = JSON.stringify(out);
    document.body.appendChild(pre);
  });
  form.dispatchEvent(new Event('submit', {cancelable: true}));
});
</script></body></html>
"""


def navegador():
    for nome in ("chromium", "google-chrome", "chromium-browser"):
        caminho = shutil.which(nome)
        if caminho:
            return caminho
    return None


def executar(fuso, casos, lang="pt-BR", ts="2026-12-01 12:00"):
    """casos: lista de {'utc': 'AAAA-MM-DDTHH:MM', 'digitado': 'AAAA-MM-DDTHH:MM' ou ausente}."""
    with tempfile.TemporaryDirectory() as d:
        arq = Path(d) / "p.html"
        arq.write_text(PAGINA % {"lang": lang, "ts": ts, "casos": json.dumps(casos), "js": JS})
        perfil = Path(d) / "perfil"
        env = dict(os.environ, TZ=fuso)
        r = subprocess.run(
            [navegador(), "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-extensions",
             "--no-first-run", "--user-data-dir=%s" % perfil, "--allow-file-access-from-files",
             "--virtual-time-budget=3000", "--dump-dom", "file://%s" % arq],
            env=env, capture_output=True, text=True, timeout=60)
    m = re.search(r'<pre id="saida">(.*?)</pre>', r.stdout, re.S)
    if not m:
        raise RuntimeError("sem saída da página (%s): %s" % (fuso, r.stderr[-500:]))
    return json.loads(html.unescape(m.group(1)))
