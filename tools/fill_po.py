#!/usr/bin/env python3
"""Preenche msgstr vazios de um .po a partir de um arquivo de traducoes.

Uso: python3 tools/fill_po.py locale/pt_BR/LC_MESSAGES/django.po traducoes.json
O JSON e um objeto {"msgid": "msgstr"}. So preenche entradas com msgstr vazio.
Entradas 'fuzzy' que recebem traducao perdem a marca. Falha se a traducao tiver placeholder que nao existe no original.
Placeholder do original que a traducao nao usa vira aviso (permitido).
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
        if len(entries) == 1 and entries[0][0] and entries[0][0] in tr and (not entries[0][1] or entries[0][2]):
            msgid = entries[0][0]
            new = tr[msgid]
            src_ph = po2js.PLACEHOLDER_RE.findall(msgid)
            dst_ph = po2js.PLACEHOLDER_RE.findall(new)
            extra = [x for x in dst_ph if x not in src_ph]
            if extra:
                raise SystemExit("placeholder que nao existe no original %s: %r" % (extra, msgid))
            for x in set(src_ph) - set(dst_ph):
                print("aviso: %s nao usado na traducao de %r" % (x, msgid[:60]))
            lines = b.split("\n")
            comments = []
            for l in lines:
                if not l.startswith("#"):
                    continue
                if l.startswith("#,"):
                    flags = [f.strip() for f in l[2:].split(",") if f.strip() and f.strip() != "fuzzy"]
                    if not flags:
                        continue
                    l = "#, " + ", ".join(flags)
                comments.append(l)
            id_start = next(i for i, l in enumerate(lines) if l.startswith("msgid"))
            id_lines = []
            for l in lines[id_start:]:
                if l.startswith("msgstr"):
                    break
                id_lines.append(l)
            out.append("\n".join(comments + id_lines + ["msgstr " + quote(new)]))
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
