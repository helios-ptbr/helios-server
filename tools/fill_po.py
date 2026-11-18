#!/usr/bin/env python3
"""Preenche msgstr vazios de um .po a partir de um arquivo de traducoes.

Uso: python3 tools/fill_po.py locale/pt_BR/LC_MESSAGES/django.po traducoes.json
O JSON e um objeto {"msgid": "msgstr"}. So preenche entradas com msgstr vazio.
Entradas 'fuzzy' que recebem traducao perdem a marca. Falha se faltar ou sobrar placeholder.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import po2js  # noqa: E402


def quote(s):
    parts = s.split("\n")
    if len(parts) == 1:
        return json.dumps(s, ensure_ascii=False)
    lines = [json.dumps(p + "\n", ensure_ascii=False) for p in parts[:-1]]
    if parts[-1]:
        lines.append(json.dumps(parts[-1], ensure_ascii=False))
    return '""\n' + "\n".join(lines)


def main(po_path, json_path):
    po = Path(po_path)
    tr = json.loads(Path(json_path).read_text(encoding="utf-8"))
    blocks = po.read_text(encoding="utf-8").split("\n\n")
    out, used = [], set()
    for b in blocks:
        entries = po2js.parse_po(b + "\n")
        if len(entries) == 1 and entries[0][0] and entries[0][0] in tr and not entries[0][1]:
            msgid = entries[0][0]
            new = tr[msgid]
            if sorted(po2js.PLACEHOLDER_RE.findall(msgid)) != sorted(po2js.PLACEHOLDER_RE.findall(new)):
                raise SystemExit("placeholder diferente: %r" % msgid)
            head = [l for l in b.split("\n") if l.startswith("#") and "fuzzy" not in l]
            if any("fuzzy" in l for l in b.split("\n") if l.startswith("#,")):
                flags = [l for l in b.split("\n") if l.startswith("#,")]
                rest = [f.replace(", fuzzy", "").replace("fuzzy", "").strip() for f in flags]
                head = [l for l in head if not l.startswith("#,")] + [r for r in rest if r not in ("#,", "")]
            # reconstroi o bloco
            ctx = [l for l in b.split("\n") if l.startswith("#")]
            ctx = [l for l in ctx if not (l.startswith("#,") and "fuzzy" in l and l.replace("fuzzy", "").replace(",", "").replace("#", "").strip() == "")]
            id_start = next(i for i, l in enumerate(b.split("\n")) if l.startswith("msgid"))
            id_lines = []
            for l in b.split("\n")[id_start:]:
                if l.startswith("msgstr"):
                    break
                id_lines.append(l)
            out.append("\n".join(ctx + id_lines + ["msgstr " + quote(new)]))
            used.add(msgid)
        else:
            out.append(b)
    missing = [k for k in tr if k not in used]
    po.write_text("\n\n".join(out), encoding="utf-8")
    print("preenchidos: %d; no JSON mas sem entrada vazia: %d" % (len(used), len(missing)))
    for m in missing:
        print("  sem entrada:", m[:80])


if __name__ == "__main__":
    main(*sys.argv[1:3])
