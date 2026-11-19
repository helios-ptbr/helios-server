#!/usr/bin/env python3
"""Roda um cenário: gera a eleição, mede `antes` e `depois` e anexa ao CSV.

  python3 tools/carga/medir.py '{"n":1000,"q":3,"opcoes":5}' [--decifrar] [--manter]

Os parâmetros são os de gerar.py (sem `nome`). Um cenário já no CSV é pulado.
O CSV fica em tools/carga/resultados/medidas.csv, uma linha por (cenário, variante).
"""
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIR = os.path.join(RAIZ, "tools", "carga")
CSV = os.path.join(DIR, "resultados", "medidas.csv")
COMPOSE = ["docker", "compose", "--profile", "dev"]
SERVICOS = ("web", "worker", "db")
CAMPOS = ["cenario", "variante", "n", "q", "opcoes", "min", "max", "rand", "apuradores", "admins",
          "rss_base_mib", "rss_pico_mib", "wall_s", "cpu_s", "tally_sha1",
          "web_mem_pico_mib", "worker_mem_pico_mib", "db_mem_pico_mib",
          "web_cpu_pico_pct", "db_cpu_pico_pct", "mem_livre_min_mib",
          "db_bytes", "castvote_bytes", "voter_bytes", "gerar_total_s", "gerar_cifrar_s",
          "gerar_gravar_s", "compute_tally_s", "decifrar_por_apurador_s", "obs"]


def sh(args, entrada=None, env=None):
    return subprocess.run(args, cwd=RAIZ, input=entrada, capture_output=True, text=True, env=env)


def exec_web(script, var, valor):
    with open(os.path.join(DIR, script)) as f:
        corpo = f.read()
    r = sh(COMPOSE + ["exec", "-T", "-e", "%s=%s" % (var, json.dumps(valor)), "web",
                      "python", "manage.py", "shell"], entrada=corpo)
    return r.stdout + r.stderr


def mib(txt):
    m = re.match(r"([\d.]+)\s*([KMG]i?B)", txt)
    v, u = float(m.group(1)), m.group(2)
    return v * {"KiB": 1 / 1024, "MiB": 1, "GiB": 1024, "KB": 1 / 1024, "MB": 1, "GB": 1024}[u]


class Amostrador(threading.Thread):
    """docker stats a cada ~1 s; guarda o pico de memória e de CPU por serviço."""

    def __init__(self):
        super().__init__(daemon=True)
        self.parar = False
        self.pico = {s: [0.0, 0.0] for s in SERVICOS}
        self.livre_min = 1e9

    def run(self):
        while not self.parar:
            r = sh(["docker", "stats", "--no-stream", "--format", "{{json .}}"])
            for linha in r.stdout.splitlines():
                try:
                    d = json.loads(linha)
                except ValueError:
                    continue
                for s in SERVICOS:
                    if d["Name"].endswith("-%s-1" % s):
                        m = mib(d["MemUsage"].split("/")[0].strip())
                        c = float(d["CPUPerc"].rstrip("%"))
                        self.pico[s][0] = max(self.pico[s][0], m)
                        self.pico[s][1] = max(self.pico[s][1], c)
            with open("/proc/meminfo") as f:
                mi = dict(l.split(":") for l in f.read().splitlines())
            self.livre_min = min(self.livre_min, int(mi["MemAvailable"].split()[0]) / 1024)


def tamanhos():
    q = ("select pg_database_size(current_database()), pg_total_relation_size('helios_castvote'),"
         " pg_total_relation_size('helios_voter')")
    r = sh(COMPOSE + ["exec", "-T", "db", "sh", "-c",
                      'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "%s"' % q])
    try:
        return [int(x) for x in r.stdout.strip().split("|")]
    except ValueError:
        return [None, None, None]


def ja_feito(cenario):
    if not os.path.exists(CSV):
        return False
    with open(CSV) as f:
        return any(l["cenario"] == cenario for l in csv.DictReader(f))


def achar(saida, marca):
    for l in saida.splitlines():
        if l.startswith(marca):
            return json.loads(l[len(marca):])
    return None


def main():
    params = json.loads(sys.argv[1])
    opcoes_cli = sys.argv[2:]
    cenario = params.pop("cenario", None) or hashlib.sha1(
        json.dumps(params, sort_keys=True).encode()).hexdigest()[:10]
    if ja_feito(cenario):
        print("PULADO", cenario)
        return
    nome = "carga-" + cenario
    params["nome"] = nome
    os.makedirs(os.path.dirname(CSV), exist_ok=True)

    exec_web("variante.py", "CARGA_V", {"nome": nome, "variante": "apagar"})  # sobra de execução interrompida
    g = achar(exec_web("gerar.py", "CARGA", params), "CARGA_OK ")
    if not g:
        print("ERRO ao gerar", cenario)
        sys.exit(1)
    db, cv, vt = tamanhos()
    novo = not os.path.exists(CSV)
    linhas = []
    variantes = ["antes", "depois"] + (["decifrar"] if "--decifrar" in opcoes_cli else [])
    for variante in variantes:
        a = Amostrador()
        a.start()
        time.sleep(1.5)
        out = exec_web("variante.py", "CARGA_V", {"nome": nome, "variante": variante})
        time.sleep(1.5)
        a.parar = True
        a.join(timeout=10)
        v = achar(out, "VAR_OK ")
        obs = "" if v else out[-300:].replace("\n", " ")
        v = v or {}
        linhas.append({
            "cenario": cenario, "variante": variante, "n": g["n"], "q": g["q"],
            "opcoes": "-".join(map(str, g["opcoes"])), "min": params.get("min", 0),
            "max": params.get("max", 1), "rand": params.get("rand", False),
            "apuradores": g["apuradores"], "admins": g["admins"],
            "rss_base_mib": v.get("rss_base_mib"), "rss_pico_mib": v.get("rss_pico_mib"),
            "wall_s": v.get("wall_s"), "cpu_s": v.get("cpu_s"), "tally_sha1": v.get("tally_sha1"),
            "web_mem_pico_mib": round(a.pico["web"][0], 1), "worker_mem_pico_mib": round(a.pico["worker"][0], 1),
            "db_mem_pico_mib": round(a.pico["db"][0], 1), "web_cpu_pico_pct": a.pico["web"][1],
            "db_cpu_pico_pct": a.pico["db"][1], "mem_livre_min_mib": round(a.livre_min),
            "db_bytes": db, "castvote_bytes": cv, "voter_bytes": vt,
            "gerar_total_s": round(g["seg"]["total"], 1),
            "gerar_cifrar_s": round(sum(x for k, x in g["seg"].items() if k.startswith("cifrar")), 1),
            "gerar_gravar_s": round(g["seg"]["gravar_cedulas"], 1),
            "compute_tally_s": v.get("compute_tally_s"),
            "decifrar_por_apurador_s": v.get("decifrar_por_apurador_s"), "obs": obs})
    if "--manter" not in opcoes_cli:
        exec_web("variante.py", "CARGA_V", {"nome": nome, "variante": "apagar"})
    with open(CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        w.writerows(linhas)
    for l in linhas:
        print(cenario, l["variante"], "pico_MiB", l["rss_pico_mib"], "wall_s", l["wall_s"],
              "sha", (l["tally_sha1"] or "")[:8])
    if len({l["tally_sha1"] for l in linhas if l["variante"] in ("antes", "depois")}) > 1:
        print("ALERTA: resultado diferente entre antes e depois")


if __name__ == "__main__":
    main()
