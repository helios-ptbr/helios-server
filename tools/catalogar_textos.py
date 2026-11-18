#!/usr/bin/env python3
"""Cataloga textos visíveis ao usuário (em inglês) por dificuldade de tradução.

Saída: docs/catalogo-textos.csv (detalhe) e docs/catalogo-textos.md (resumo).
Uso: python3 tools/catalogar_textos.py   (na raiz do repositório)

Dificuldade:
  A (fácil)   texto puro em template: basta envolver com {% trans %}
  B (média)   template com variáveis/tags inline ({% blocktrans %}), ou string Python simples (gettext)
  C (difícil) JS, e-mails, Python com formatação/f-string/concatenação, plurais, texto montado em partes
"""
import ast
import csv
import os
import re
import sys
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = ["helios", "helios_auth", "server_ui", "heliosbooth", "heliosverifier", "templates"]
PULAR_ARQ = re.compile(r"(compressed|-test\.html$|\.min\.)", re.I)
INTERNOS = {"Exception", "ValueError", "SuspiciousOperation"}
PULAR_DIRS = {"migrations", "node_modules", ".git", "__pycache__", "foundation", "jscrypto",
              "crypto", "tests", "static", "docs", "selenium"}
# bibliotecas de terceiros (não traduzir)
LIBS_JS = re.compile(r"(jquery|foundation|underscore|bootstrap|jsbn|sjcl|sha1|sha2|bigint|"
                     r"class\.js|random\.js|combined|\.min\.js|json2|modernizr|fastclick|"
                     r"placeholder|zepto|jscrypto|\.map$)", re.I)
TAG = re.compile(r"<[^>]+>")
DJ_TAG = re.compile(r"\{%.*?%\}|\{#.*?#\}", re.S)
DJ_VAR = re.compile(r"\{\{.*?\}\}")
SCRIPT = re.compile(r"<script\b[^>]*>(.*?)</script>", re.S | re.I)
STYLE = re.compile(r"<style\b[^>]*>.*?</style>", re.S | re.I)
COMENT = re.compile(r"<!--.*?-->", re.S)
COMENT_DJ = re.compile(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", re.S)
INLINE = re.compile(r"[A-Za-z][^<>{}\n]*<(a|b|i|em|strong|span|code|u|br)\b", re.I)
PALAVRA = re.compile(r"[A-Za-z]{2,}")
LINHA_JS_STR = re.compile(r"""(["'])((?:(?!\1)[^\\\n]|\\.){6,})\1""")
JS_CONTEXTO = re.compile(r"(alert|confirm|prompt|\.html|\.text|innerHTML|\.val|error|message|title|label)", re.I)

linhas_csv = []  # arquivo, linha, tipo, dificuldade, texto


def registrar(arq, n, tipo, dif, texto):
    texto = " ".join(texto.split())
    if texto:
        linhas_csv.append((os.path.relpath(arq, RAIZ), n, tipo, dif, texto))


def eh_texto(s):
    s = s.strip()
    if s.startswith(("{", "}")) or "$T." in s:
        return False
    if len(s) < 3 or not PALAVRA.search(s):
        return False
    if re.fullmatch(r"[\w./#:\-]+", s) and " " not in s:  # id, url, classe
        return len(s) > 3 and s[0].isupper() and s.isalpha()
    return True


def varrer_template(caminho, email=False):
    with open(caminho, encoding="utf-8", errors="replace") as f:
        bruto = f.read()
    # remove blocos que não são texto visível, mantendo as quebras de linha
    def branco(m):
        return "\n" * m.group(0).count("\n")
    js_blocos = [(m.start(1), m.group(1)) for m in SCRIPT.finditer(bruto)]
    texto = COMENT_DJ.sub(branco, bruto)
    texto = SCRIPT.sub(branco, texto)
    texto = STYLE.sub(branco, texto)
    texto = COMENT.sub(branco, texto)
    for i, linha in enumerate(texto.split("\n"), 1):
        ja_trad = "{% trans" in linha or "{% blocktrans" in linha
        limpo = DJ_TAG.sub(" ", linha)
        tem_var = bool(DJ_VAR.search(limpo))
        limpo = DJ_VAR.sub(" ", limpo)
        limpo = TAG.sub(" ", limpo).replace("&nbsp;", " ").strip()
        if not eh_texto(limpo) or ja_trad:
            continue
        if email:
            dif = "C"
        elif tem_var or INLINE.search(linha):
            dif = "B"
        else:
            dif = "A"
        registrar(caminho, i, "email" if email else "template", dif, limpo)
        # atributos traduzíveis
    for m in re.finditer(r'\b(title|alt|placeholder|value)="([^"{}]*[A-Za-z]{3,}[^"{}]*)"', texto):
        v = m.group(2)
        if eh_texto(v) and " " in v.strip():
            n = texto.count("\n", 0, m.start()) + 1
            registrar(caminho, n, "template-atributo", "B", v)
    # JS embutido
    for inicio, js in js_blocos:
        base = bruto.count("\n", 0, inicio)
        varrer_js_texto(caminho, js, base)


def varrer_js_texto(caminho, js, base=0):
    for i, linha in enumerate(js.split("\n"), 1):
        s = linha.strip()
        if s.startswith("//") or s.startswith("*") or s.startswith("/*"):
            continue
        if not JS_CONTEXTO.search(s):
            continue
        for m in LINHA_JS_STR.finditer(s):
            v = m.group(2)
            if " " in v.strip() and PALAVRA.search(v) and not v.startswith(("http", "/", "#", ".")) \
                    and not re.search(r"[{};=]|function|return ", v):
                registrar(caminho, base + i, "js", "C", v)


def varrer_js(caminho):
    if LIBS_JS.search(caminho):
        return
    with open(caminho, encoding="utf-8", errors="replace") as f:
        varrer_js_texto(caminho, f.read())


class Visitante(ast.NodeVisitor):
    CHAMADAS_VISIVEIS = {"HttpResponse", "HttpResponseBadRequest", "HttpResponseNotFound",
                         "HttpResponseForbidden", "ValidationError", "Exception", "ValueError",
                         "PermissionDenied", "SuspiciousOperation", "CharField", "BooleanField",
                         "EmailField", "ChoiceField", "DateTimeField", "IntegerField", "Field",
                         "add_message", "error", "success", "warning", "info", "send_mail",
                         "EmailMessage", "render_template", "render_template_raw", "Http404"}
    IGNORAR_CHAMADAS = {"debug", "exception", "critical", "getLogger", "print", "get", "pop",
                        "getattr", "setattr", "hasattr", "reverse", "filter", "exclude", "order_by",
                        "values", "values_list", "annotate", "strftime", "strptime", "join",
                        "split", "startswith", "endswith", "replace", "format_map"}

    def __init__(self, caminho):
        self.caminho = caminho
        self.pilha = []

    def visit(self, no):
        self.pilha.append(no)
        super().visit(no)
        self.pilha.pop()

    def nome_chamada(self, c):
        f = c.func
        return f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")

    def contexto(self):
        for no in reversed(self.pilha[:-1]):
            if isinstance(no, ast.Call):
                return self.nome_chamada(no), no
            if isinstance(no, ast.keyword) and no.arg in ("label", "help_text", "error_messages"):
                return "kw:" + no.arg, no
        return None, None

    def eh_docstring(self, no):
        if len(self.pilha) < 3:
            return False
        pai = self.pilha[-2]
        avo = self.pilha[-3]
        return (isinstance(pai, ast.Expr) and
                isinstance(avo, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and
                avo.body and avo.body[0] is pai)

    def tratar(self, no, valor, composto):
        nome, _ = self.contexto()
        if nome is None or nome in self.IGNORAR_CHAMADAS:
            return
        visivel = nome in self.CHAMADAS_VISIVEIS or str(nome).startswith("kw:")
        if not visivel:
            return
        if not (" " in valor.strip() and PALAVRA.search(valor)):
            return
        pai = self.pilha[-2]
        formatado = composto or isinstance(pai, ast.BinOp) or \
            (isinstance(pai, ast.Attribute) and pai.attr == "format")
        tipo = "python-erro-interno" if nome in INTERNOS else "python"
        registrar(self.caminho, no.lineno, tipo, "C" if formatado else "B", valor)

    def visit_Constant(self, no):
        if isinstance(no.value, str) and not self.eh_docstring(no):
            self.tratar(no, no.value, False)

    def visit_JoinedStr(self, no):
        partes = [v.value for v in no.values if isinstance(v, ast.Constant) and isinstance(v.value, str)]
        if partes and not self.eh_docstring(no):
            self.tratar(no, "".join(partes) + " {…}", True)
        # não desce nos filhos para não duplicar


def varrer_python(caminho):
    with open(caminho, encoding="utf-8", errors="replace") as f:
        src = f.read()
    try:
        arvore = ast.parse(src)
    except SyntaxError:
        return
    Visitante(caminho).visit(arvore)


def andar():
    for app in APPS:
        base = os.path.join(RAIZ, app)
        if not os.path.isdir(base):
            continue
        for raiz, dirs, arqs in os.walk(base):
            dirs[:] = [d for d in dirs if d not in PULAR_DIRS]
            for a in arqs:
                if PULAR_ARQ.search(a):
                    continue
                p = os.path.join(raiz, a)
                if a.endswith((".html",)):
                    varrer_template(p)
                elif a.endswith(".txt") and "templates" in p:
                    varrer_template(p, email=True)
                elif a.endswith(".js"):
                    varrer_js(p)
                elif a.endswith(".py") and not a.startswith("test"):
                    varrer_python(p)


def escrever():
    docs = os.path.join(RAIZ, "docs")
    os.makedirs(docs, exist_ok=True)
    linhas_csv.sort(key=lambda r: (r[0], r[1]))
    with open(os.path.join(docs, "catalogo-textos.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["arquivo", "linha", "tipo", "dificuldade", "texto"])
        w.writerows(linhas_csv)

    por_arq = defaultdict(lambda: defaultdict(int))
    por_tipo = defaultdict(lambda: defaultdict(int))
    for arq, _, tipo, dif, _ in linhas_csv:
        por_arq[arq][dif] += 1
        por_tipo[tipo][dif] += 1
    total = len(linhas_csv)
    tot_dif = defaultdict(int)
    for r in linhas_csv:
        tot_dif[r[3]] += 1

    md = ["# Catálogo de textos a traduzir", "",
          "Gerado por `tools/catalogar_textos.py`. Detalhe linha a linha em `docs/catalogo-textos.csv`.", "",
          "Contagem por **ocorrência** (linha de texto), não por frase única. É uma estimativa: "
          "revisar à mão antes de fechar o escopo.", "",
          "## Dificuldade", "",
          "| Nível | Significado | Como traduzir |", "|---|---|---|",
          "| A | texto puro em template | `{% trans %}` |",
          "| B | template com variável ou tag inline; string Python simples | `{% blocktrans %}` / `gettext` |",
          "| C | JS, e-mail, Python com formatação ou montado em partes | caso a caso |", "",
          "## Total", "",
          f"| A | B | C | Total |", "|---:|---:|---:|---:|",
          f"| {tot_dif['A']} | {tot_dif['B']} | {tot_dif['C']} | {total} |", "",
          "## Por tipo", "", "| Tipo | A | B | C | Total |", "|---|---:|---:|---:|---:|"]
    for t, d in sorted(por_tipo.items()):
        md.append(f"| {t} | {d['A']} | {d['B']} | {d['C']} | {sum(d.values())} |")
    md += ["", "## Por arquivo (maiores primeiro)", "", "| Arquivo | A | B | C | Total |", "|---|---:|---:|---:|---:|"]
    for a, d in sorted(por_arq.items(), key=lambda kv: -sum(kv[1].values())):
        md.append(f"| `{a}` | {d['A']} | {d['B']} | {d['C']} | {sum(d.values())} |")
    with open(os.path.join(docs, "catalogo-textos.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"total={total} A={tot_dif['A']} B={tot_dif['B']} C={tot_dif['C']} arquivos={len(por_arq)}")


if __name__ == "__main__":
    andar()
    escrever()
