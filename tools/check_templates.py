#!/usr/bin/env python3
"""Compila templates do Django para achar erro de sintaxe (sem banco de dados).

Uso: DJANGO_SETTINGS_MODULE=settings_ptbr uv run python tools/check_templates.py [arquivo.html ...]
Sem argumentos, confere todos os templates das apps (helios, helios_auth, server_ui) e templates/.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_ptbr")

import django  # noqa: E402

django.setup()
from django.template import engines  # noqa: E402

DIRS = ["helios/templates", "helios_auth/templates", "server_ui/templates", "templates"]


def main(argv):
    engine = engines["django"]
    if argv:
        files = [Path(a).resolve() for a in argv]
    else:
        files = [p for d in DIRS for p in sorted((ROOT / d).rglob("*.html"))]
    bad = 0
    for f in files:
        try:
            engine.from_string(f.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            bad += 1
            print("ERRO %s: %s" % (f.relative_to(ROOT), e))
    print("%d arquivo(s), %d com erro" % (len(files), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
