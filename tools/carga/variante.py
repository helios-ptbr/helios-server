"""Mede uma variante da soma da apuração, em processo novo (dentro do `web`).
Env CARGA_V = {"nome": short_name, "variante": "antes"|"depois"|"decifrar"}
"antes" e "depois" não gravam nada no banco (a soma fica só em memória, a menos
que "salvar" seja verdadeiro), para as variantes serem comparáveis.
"""
import hashlib
import json
import os
import resource
import time

from helios import models

P = json.loads(os.environ["CARGA_V"])
if P["variante"] == "apagar":
    models.Election.objects.filter(short_name=P["nome"]).delete()
    print("VAR_OK " + json.dumps({"apagada": P["nome"]}))
    raise SystemExit
e = models.Election.objects.get(short_name=P["nome"])
KB = 1024.0
base = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / KB
c0, w0 = time.process_time(), time.time()
saida = {"nome": P["nome"], "variante": P["variante"], "rss_base_mib": round(base, 1)}

if P["variante"] == "apagar":
    e.delete()
    print("VAR_OK " + json.dumps({"apagada": P["nome"]}))
    raise SystemExit

if P["variante"] in ("antes", "depois"):
    tally = e.init_tally()
    qs = e.voter_set.exclude(vote=None)
    if P["variante"] == "depois":
        qs = qs.iterator(chunk_size=500)
    for v in qs:
        tally.add_vote(v.vote, verify_p=False)
    saida["tally_sha1"] = hashlib.sha1(
        json.dumps([[[int(c.alpha), int(c.beta)] for c in q] for q in tally.tally]).encode()).hexdigest()
    if P.get("salvar"):
        e.encrypted_tally = tally
        e.save()
elif P["variante"] == "decifrar":
    t = time.time()
    e.compute_tally()
    saida["compute_tally_s"] = round(time.time() - t, 2)
    tally = e.encrypted_tally
    tally.init_election(e)
    por = []
    for tr in e.trustee_set.exclude(secret_key=None):
        t = time.time()
        f, pr = tally.decryption_factors_and_proofs(tr.secret_key)
        tr.decryption_factors, tr.decryption_proofs = f, pr
        tr.save()
        por.append(round(time.time() - t, 2))
    saida["decifrar_por_apurador_s"] = por

saida["wall_s"] = round(time.time() - w0, 2)
saida["cpu_s"] = round(time.process_time() - c0, 2)
saida["rss_pico_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / KB, 1)
print("VAR_OK " + json.dumps(saida))
