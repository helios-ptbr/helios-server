"""Falha se um template ganhar texto visível fora de {% translate %} ou {% blocktranslate %} (issue #21)."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TemplatesSemTraducaoTests(unittest.TestCase):
    def test_nenhum_texto_visivel_fora_do_catalogo(self):
        r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'templates_sem_traducao.py')],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, 'template com texto sem tradução:\n' + r.stdout)


if __name__ == '__main__':
    unittest.main()
