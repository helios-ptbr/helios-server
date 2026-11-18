import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import booth_lang


class BoothLangTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.addCleanup(self.d.cleanup)
        for n in ("vote.html", "vote.pt-BR.html", "vote.es.html", "single-ballot-verify.html", "single-ballot-verify.pt-BR.html"):
            (Path(self.d.name) / n).write_text("x")

    def page(self, lang):
        return booth_lang.page_for_language(lang, self.d.name)

    def test_portuguese(self):
        self.assertEqual(self.page("pt-br"), "vote.pt-BR.html")
        self.assertEqual(self.page("pt_BR"), "vote.pt-BR.html")

    def test_falls_back_to_language_without_region(self):
        self.assertEqual(self.page("es-mx"), "vote.es.html")

    def test_english_and_unknown_use_default(self):
        for lang in ("en", "en-us", "fr", "", None, "de-ch"):
            self.assertEqual(self.page(lang), "vote.html", lang)

    def test_hostile_values_use_default(self):
        for lang in ("../../etc/passwd", "pt-br/../x", "pt-br\n", "pt br", "x" * 100):
            self.assertEqual(self.page(lang), "vote.html", lang)

    def test_real_booth_has_the_page(self):
        self.assertEqual(booth_lang.page_for_language("pt-br"), "vote.pt-BR.html")


    def test_verifier_page_follows_language(self):
        f = lambda lang: booth_lang.page_for_language(lang, self.d.name, base="single-ballot-verify")
        self.assertEqual(f("pt-br"), "single-ballot-verify.pt-BR.html")
        self.assertEqual(f("en"), "single-ballot-verify.html")
        self.assertEqual(f("es"), "single-ballot-verify.html")  # no es verifier page here


if __name__ == "__main__":
    unittest.main()
