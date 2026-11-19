"""Testa o settings_ptbr.py sem precisar do Django instalado (usa um settings falso)."""
import importlib
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class SettingsPtbrTest(unittest.TestCase):
    def load(self, middleware):
        fake = types.ModuleType("settings")
        fake.ROOT_PATH = str(ROOT)
        fake.MIDDLEWARE = list(middleware)
        saved = {k: sys.modules.get(k) for k in ("settings", "settings_ptbr")}
        sys.modules["settings"] = fake
        sys.modules.pop("settings_ptbr", None)
        sys.path.insert(0, str(ROOT))
        try:
            return importlib.import_module("settings_ptbr")
        finally:
            sys.path.remove(str(ROOT))
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v

    BASE = [
        "django.middleware.security.SecurityMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ]

    def test_language_and_paths(self):
        s = self.load(self.BASE)
        self.assertEqual(s.LANGUAGE_CODE, "pt-br")
        self.assertIn("pt-br", [c for c, _ in s.LANGUAGES])
        self.assertEqual(s.LOCALE_PATHS, [str(ROOT / "locale")])

    def test_locale_middleware_after_session(self):
        m = self.load(self.BASE).MIDDLEWARE
        loc = m.index("django.middleware.locale.LocaleMiddleware")
        self.assertGreater(loc, m.index("django.contrib.sessions.middleware.SessionMiddleware"))
        self.assertLess(loc, m.index("django.contrib.auth.middleware.AuthenticationMiddleware"))
        self.assertEqual(m.count("django.middleware.locale.LocaleMiddleware"), 1)

    def test_original_middleware_list_not_lost(self):
        m = self.load(self.BASE).MIDDLEWARE
        for item in self.BASE:
            self.assertIn(item, m)


    def test_welcome_message_in_portuguese_unless_set_in_environment(self):
        import os
        old = os.environ.pop("WELCOME_MESSAGE", None)
        try:
            self.assertIn("mensagem padrão", self.load(self.BASE).WELCOME_MESSAGE)
            os.environ["WELCOME_MESSAGE"] = "Bem-vindas"
            self.assertFalse(hasattr(self.load(self.BASE), "WELCOME_MESSAGE"))  # o do ambiente vale, vindo do settings.py
        finally:
            os.environ.pop("WELCOME_MESSAGE", None)
            if old is not None:
                os.environ["WELCOME_MESSAGE"] = old

    def test_privacidade_vazia_por_padrao(self):
        s = self.load(self.BASE)
        for nome in ("CONTROLADOR", "ENCARREGADO", "ENCARREGADO_EMAIL", "BASE_LEGAL", "RETENCAO", "REGRAS_URL", "CONTATO_EMAIL"):
            self.assertEqual(getattr(s, "PRIVACY_" + nome), "")

    def test_privacidade_le_o_ambiente(self):
        import os
        os.environ["PRIVACY_CONTROLADOR"] = "Universidade Exemplo"
        os.environ["PRIVACY_RETENCAO"] = "cinco anos"
        try:
            s = self.load(self.BASE)
        finally:
            del os.environ["PRIVACY_CONTROLADOR"], os.environ["PRIVACY_RETENCAO"]
        self.assertEqual(s.PRIVACY_CONTROLADOR, "Universidade Exemplo")
        self.assertEqual(s.PRIVACY_RETENCAO, "cinco anos")


if __name__ == "__main__":
    unittest.main()
