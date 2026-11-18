import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_booth_pages
import po2js

ROOT = Path(__file__).resolve().parent.parent

PO = r'''
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"

#: a.js
msgid "Review"
msgstr "Revisar"

msgid "Hello %(name)s"
msgstr "Olá %(name)s"

#, fuzzy
msgid "Fuzzy one"
msgstr "Incerto"

msgid "Empty"
msgstr ""

msgid "Multi "
"line"
msgstr "Várias "
"linhas"

msgid "Say \"hi\""
msgstr "Diga \"oi\""

msgid "One item"
msgid_plural "Many items"
msgstr[0] "Um"
msgstr[1] "Vários"
'''


class Po2JsTest(unittest.TestCase):
    def strings(self, text=PO):
        return po2js.build_strings(po2js.parse_po(text))

    def test_basic_entries(self):
        s = self.strings()
        self.assertEqual(s["Review"], "Revisar")
        self.assertEqual(s["Hello %(name)s"], "Olá %(name)s")
        self.assertEqual(s["Multi line"], "Várias linhas")
        self.assertEqual(s['Say "hi"'], 'Diga "oi"')

    def test_skips_header_fuzzy_empty_plural(self):
        s = self.strings()
        for k in ("", "Fuzzy one", "Empty", "One item"):
            self.assertNotIn(k, s)

    def test_placeholder_mismatch_fails(self):
        bad = 'msgid "Hi %(name)s"\nmsgstr "Oi"\n'
        with self.assertRaises(po2js.PoError):
            self.strings(bad)
        bad2 = 'msgid "Hi %(name)s"\nmsgstr "Oi %(nome)s"\n'
        with self.assertRaises(po2js.PoError):
            self.strings(bad2)

    def test_output_is_data_only_and_deterministic(self):
        out = po2js.render(self.strings())
        self.assertEqual(out, po2js.render(self.strings()))
        body = re.search(r'^BOOTH_STRINGS = (.*);\n\Z', out, re.S | re.M).group(1)
        self.assertEqual(json.loads(body.replace("<\\/", "</")), self.strings())

    def test_script_close_is_escaped(self):
        out = po2js.render({"a": "x</script><script>alert(1)</script>"})
        self.assertNotIn("</script>", out)

    def test_cli_write_and_check(self):
        with tempfile.TemporaryDirectory() as d:
            po = Path(d) / "booth.po"
            out = Path(d) / "strings.pt-BR.js"
            po.write_text(PO, encoding="utf-8")
            args = ["pt_BR", "--po", str(po), "--out", str(out)]
            self.assertEqual(po2js.main(args), 0)
            self.assertEqual(po2js.main(args + ["--check"]), 0)
            out.write_text(out.read_text(encoding="utf-8") + "// x\n", encoding="utf-8")
            self.assertEqual(po2js.main(args + ["--check"]), 1)

    def test_invalid_lang_rejected(self):
        with self.assertRaises(SystemExit):
            po2js.main(["../etc", "--po", "x"])


class GenPagesTest(unittest.TestCase):
    def setUp(self):
        self.src = (ROOT / "heliosbooth" / "vote.html").read_text(encoding="utf-8")

    def test_only_expected_lines_change(self):
        out = gen_booth_pages.generate(self.src, "pt_BR")
        a, b = self.src.splitlines(), out.splitlines()
        added = [l.strip() for l in b if l not in a]
        self.assertEqual(sorted(added), sorted([
            '<html lang="pt-BR">',
            '<script src="js/strings.pt-BR.js"></script>',
        ]))
        self.assertEqual(len(b), len(a) + 1)

    def test_strings_loaded_before_i18n_before_bundle(self):
        out = gen_booth_pages.generate(self.src, "pt_BR")
        i = [out.index(x) for x in ("strings.pt-BR.js", "js/i18n.js", "helios-booth-compressed.js")]
        self.assertEqual(i, sorted(i))

    def test_committed_page_is_up_to_date(self):
        page = ROOT / "heliosbooth" / "vote.pt-BR.html"
        if page.exists():
            self.assertEqual(page.read_text(encoding="utf-8"),
                             gen_booth_pages.generate(self.src, "pt_BR"))


class I18nJsTest(unittest.TestCase):
    def test_no_url_or_dynamic_loading(self):
        js = (ROOT / "heliosbooth" / "js" / "i18n.js").read_text(encoding="utf-8")
        code = "\n".join(l for l in js.splitlines() if not l.strip().startswith("//"))
        for bad in ("location", "document.write", "eval", "innerHTML", "createElement", "XMLHttpRequest"):
            self.assertNotIn(bad, code)

    def test_T_behaviour_with_node(self):
        node = subprocess.run(["which", "node"], capture_output=True, text=True).stdout.strip()
        if not node:
            self.skipTest("node not installed")
        js = ROOT / "heliosbooth" / "js" / "i18n.js"
        script = ("var fs=require('fs');eval(fs.readFileSync(%s,'utf8')+';globalThis.T=T;globalThis.S=BOOTH_STRINGS');"
                  "S.Next='Próximo';"
                  "console.log([T('Next'),T('Missing'),T('hasOwnProperty'),T('__proto__')].join('|'))") % json.dumps(str(js))
        r = subprocess.run([node, "-e", script], capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "Próximo|Missing|hasOwnProperty|__proto__", r.stderr)


class RepoFilesTest(unittest.TestCase):
    PO = ROOT / "locale" / "pt_BR" / "LC_MESSAGES" / "booth.po"

    def test_T_calls_in_vote_html_match_po(self):
        src = (ROOT / "heliosbooth" / "vote.html").read_text(encoding="utf-8")
        ids = set()
        for m in re.finditer(r"""\bT\((?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")""", src):
            t = m.group(1) if m.group(1) is not None else m.group(2)
            ids.add(t.encode().decode("unicode_escape"))
        po = {e[0] for e in po2js.parse_po(self.PO.read_text(encoding="utf-8"))} - {""}
        self.assertEqual(ids, po)

    def test_all_po_entries_translated_and_valid(self):
        entries = po2js.parse_po(self.PO.read_text(encoding="utf-8"))
        for msgid, msgstr, fuzzy in entries:
            if msgid:
                self.assertTrue(msgstr and not fuzzy, msgid)
        po2js.build_strings(entries)  # raises on placeholder mismatch

    def test_strings_file_is_up_to_date(self):
        self.assertEqual(po2js.main(["pt_BR", "--check"]), 0)


if __name__ == "__main__":
    unittest.main()
