#!/usr/bin/env python3
"""Generate the translated booth pages from the original English files.

Usage: python3 tools/gen_booth_pages.py <lang> [--check]

For <lang> (e.g. pt_BR) it writes:
  heliosbooth/vote.<lang>.html          from heliosbooth/vote.html
  heliosbooth/templates/<lang>/*.html   from heliosbooth/templates/*.html

The original files are never changed. In each page, the text between tags and
between jTemplates {...} expressions is replaced when it matches a msgid of
locale/<lang>/LC_MESSAGES/booth_html.po (whitespace is normalized for the
match). Text with no translation stays in English. vote.<lang>.html also gets:
  - <html lang="<lang>">
  - one <script src="js/strings.<lang>.js"> tag before js/i18n.js
  - setTemplateURL("templates/<lang>/...") instead of templates/...
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import po2js  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BOOTH = ROOT / "heliosbooth"
LANG_RE = re.compile(r'^[A-Za-z]{2,3}([_-][A-Za-z0-9]{2,8})?$')
I18N_RE = re.compile(r'^(?P<ind>[ \t]*)<script[^>]*src="js/i18n\.js"[^>]*></script>[ \t]*$', re.M)
HTML_LANG_RE = re.compile(r'<html lang="en">')
TEMPLATE_URL = 'setTemplateURL("templates/'
# script/style/comments are kept whole; tags and jTemplates {...} split the text.
TOKEN_RE = re.compile(r'(<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->|<[^>]*>|\{[^{}]*\})', re.S)
# Text that is not translated on purpose.
IGNORE = {"java.com"}


def norm(text):
    return " ".join(text.split())


def has_words(text):
    return bool(re.search(r"[A-Za-z]{2}", re.sub(r"&\w+;", "", text)))


def segments(html):
    """Yield (index, part, normalized_text) for each translatable text segment."""
    parts = TOKEN_RE.split(html)
    for i in range(0, len(parts), 2):
        t = norm(parts[i])
        if t and has_words(t) and t not in IGNORE:
            yield i, parts[i], t


def build_table(entries):
    table = {}
    for msgid, msgstr, fuzzy in entries:
        if not msgid or not msgstr or fuzzy:
            continue
        for ch in "<{}":
            if ch in msgstr and ch not in msgid:
                raise ValueError("%r not allowed in translation of %r" % (ch, msgid))
        table[norm(msgid)] = msgstr.strip()
    return table


def translate_html(html, table):
    parts = TOKEN_RE.split(html)
    for i, part, t in segments(html):
        if t in table:
            lead = part[:len(part) - len(part.lstrip())]
            trail = part[len(part.rstrip()):]
            parts[i] = lead + table[t] + trail
    return "".join(parts)


def generate_template(source, table):
    return translate_html(source, table)


def generate_vote(source, lang, table):
    web = lang.replace("_", "-")
    if len(I18N_RE.findall(source)) != 1:
        raise ValueError("expected exactly one js/i18n.js <script> in vote.html")
    if len(HTML_LANG_RE.findall(source)) != 1:
        raise ValueError('expected exactly one <html lang="en"> in vote.html')
    if source.count(TEMPLATE_URL) < 1:
        raise ValueError("no setTemplateURL calls found in vote.html")
    out = translate_html(source, table)
    out = out.replace(TEMPLATE_URL, TEMPLATE_URL + web + "/")
    out = I18N_RE.sub(lambda m: '%s<script src="js/strings.%s.js"></script>\n%s' % (m.group("ind"), web, m.group(0)),
                      out, count=1)
    return HTML_LANG_RE.sub('<html lang="%s">' % web, out, count=1)


def po_path(lang):
    return ROOT / "locale" / lang / "LC_MESSAGES" / "booth_html.po"


def load_table(lang):
    p = po_path(lang)
    if not p.exists():
        return {}
    return build_table(po2js.parse_po(p.read_text(encoding="utf-8")))


def outputs(lang):
    """Return {path: content} for every generated file."""
    web = lang.replace("_", "-")
    table = load_table(lang)
    out = {BOOTH / ("vote.%s.html" % web):
           generate_vote((BOOTH / "vote.html").read_text(encoding="utf-8"), lang, table)}
    for t in sorted((BOOTH / "templates").glob("*.html")):
        out[BOOTH / "templates" / web / t.name] = generate_template(t.read_text(encoding="utf-8"), table)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lang")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if not LANG_RE.match(a.lang):
        ap.error("invalid language code: %r" % a.lang)
    files = outputs(a.lang)
    if a.check:
        bad = [p for p, c in files.items() if not p.exists() or p.read_text(encoding="utf-8") != c]
        for p in bad:
            print("out of date: %s" % p, file=sys.stderr)
        return 1 if bad else 0
    for p, c in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(c, encoding="utf-8")
        print("wrote %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
