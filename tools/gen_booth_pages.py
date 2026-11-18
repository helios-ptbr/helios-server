#!/usr/bin/env python3
"""Generate heliosbooth/vote.<lang>.html from heliosbooth/vote.html.

Usage: python3 tools/gen_booth_pages.py <lang> [--check]

The page is a copy of vote.html with two fixed <script src> tags inserted
before the booth bundle, and the <html lang> changed. Nothing else changes.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOTH = ROOT / "heliosbooth"
LANG_RE = re.compile(r'^[A-Za-z]{2,3}([_-][A-Za-z0-9]{2,8})?$')
BUNDLE_RE = re.compile(r'^(?P<ind>[ \t]*)<script[^>]*src="js/\d+-helios-booth-compressed\.js"[^>]*></script>[ \t]*$', re.M)
HTML_LANG_RE = re.compile(r'<html lang="en">')


def generate(source, lang):
    web = lang.replace("_", "-")
    if len(BUNDLE_RE.findall(source)) != 1:
        raise ValueError("expected exactly one booth bundle <script> in vote.html")
    if len(HTML_LANG_RE.findall(source)) != 1:
        raise ValueError('expected exactly one <html lang="en"> in vote.html')
    tags = ('{ind}<script src="js/strings.%s.js"></script>\n'
            '{ind}<script src="js/i18n.js"></script>\n') % web

    def add(m):
        return tags.format(ind=m.group("ind")) + m.group(0)

    out = BUNDLE_RE.sub(add, source, count=1)
    return HTML_LANG_RE.sub('<html lang="%s">' % web, out, count=1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("lang")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if not LANG_RE.match(a.lang):
        ap.error("invalid language code: %r" % a.lang)
    web = a.lang.replace("_", "-")
    out_path = BOOTH / ("vote.%s.html" % web)
    content = generate((BOOTH / "vote.html").read_text(encoding="utf-8"), a.lang)
    if a.check:
        if not out_path.exists() or out_path.read_text(encoding="utf-8") != content:
            print("out of date: %s" % out_path, file=sys.stderr)
            return 1
        return 0
    out_path.write_text(content, encoding="utf-8")
    print("wrote %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
