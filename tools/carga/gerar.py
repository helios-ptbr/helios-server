"""Cria uma eleição de carga com cédulas. Rodar dentro do contêiner `web`:

  docker compose --profile dev exec -T -e CARGA='{"nome":"c1","n":1000}' web \
      python manage.py shell < tools/carga/gerar.py

Parâmetros (JSON em CARGA), todos opcionais menos `nome`:
  n            eleitores com cédula (10)
  q            número de questões (3)
  opcoes       opções por questão, número ou lista (5)
  min          mínimo de seleções, 0 ou 1 (0)
  max          máximo de seleções; None = igual ao número de opções (1)
  rand         randomize_answer_order da eleição (false). Só afeta a cabine, não a apuração.
  apuradores   número de apuradores (1, o do Helios; os demais têm chave gerada aqui)
  admins       número de administradores (1)
  distintas    cédulas distintas geradas (20); as demais repetem estas
Imprime uma linha JSON com tempos e o short_name.
"""
import json, os, time, uuid, datetime, random

from django.db import transaction
from helios import models, views
from helios.crypto import algs
from helios.workflows import homomorphic
from helios_auth.models import User

P = json.loads(os.environ["CARGA"])
nome = P["nome"]
n = P.get("n", 10)
q = P.get("q", 3)
opcoes = P.get("opcoes", 5)
mn = P.get("min", 0)
mx = P.get("max", 1)
rand = P.get("rand", False)
apuradores = P.get("apuradores", 1)
admins = P.get("admins", 1)
distintas = min(P.get("distintas", 20), n)
t0 = time.time()
seg = {}

if isinstance(opcoes, int):
    opcoes = [opcoes] * q


def usuario(i):
    u, _ = User.objects.get_or_create(
        user_type="password", user_id="carga-admin-%d" % i,
        defaults={"name": "Admin %d" % i, "info": {"password": "x"}, "admin_p": True})
    return u


users = [usuario(i) for i in range(max(admins, 1))]
questions = []
for i in range(q):
    k = opcoes[i]
    questions.append({
        "answer_urls": [None] * k, "answers": ["Opção %d.%d" % (i + 1, j + 1) for j in range(k)],
        "choice_type": "approval", "min": mn, "max": k if mx in (None, "todas") else mx,
        "question": "Questão %d" % (i + 1), "result_type": "absolute",
        "short_name": "Q%d" % (i + 1), "tally_type": "homomorphic"})

e = models.Election(
    admin=users[0], uuid=str(uuid.uuid4()), short_name=nome, name="Carga " + nome,
    description="carga", questions=questions, randomize_answer_order=rand,
    cast_url="https://localhost:8443/helios/elections/x/cast", use_voter_aliases=False,
    private_p=False)
e.save()
e.admins.set(users[1:])
seg["eleicao"] = time.time() - t0

# apuradores: o do Helios + (apuradores-1) com chave gerada aqui (como se fossem externos)
t1 = time.time()
e.generate_trustee(views.ELGAMAL_PARAMS)
for i in range(1, apuradores):
    kp = views.ELGAMAL_PARAMS.generate_keypair()
    t = models.Trustee(election=e, uuid=str(uuid.uuid4()), name="Apurador %d" % i,
                       email="apurador%d@exemplo.org" % i, public_key=kp.pk, secret_key=kp.sk)
    t.public_key_hash = models.datatypes.LDObject.instantiate(kp.pk, datatype="legacy/EGPublicKey").hash
    t.pok = kp.sk.prove_sk(algs.DLog_challenge_generator)
    t.save()
seg["apuradores"] = time.time() - t1

# eleitores (sem passar pelo CSV) e congelamento
t1 = time.time()
vs = []
for i in range(n):
    vs.append(models.Voter(election=e, uuid=str(uuid.uuid4()),
                           voter_login_id="v%d" % i, voter_password="senha%d" % i,
                           voter_name="Eleitor %d" % i, voter_email="v%d@exemplo.org" % i))
models.Voter.objects.bulk_create(vs, batch_size=1000)
seg["eleitores"] = time.time() - t1

t1 = time.time()
e.freeze()
seg["congelar"] = time.time() - t1
e = models.Election.objects.get(pk=e.pk)

# cédulas: `distintas` cifradas pelo código do Helios, repetidas até n
t1 = time.time()
rng = random.Random(42)
modelos = []
for _ in range(distintas):
    resp = []
    for i, k in enumerate(opcoes):
        top = questions[i]["max"]
        qtd = rng.randint(max(mn, 0), min(top, k))
        resp.append(sorted(rng.sample(range(k), qtd)))
    modelos.append(homomorphic.EncryptedVote.fromElectionAndAnswers(e, resp))
seg["cifrar_%d" % distintas] = time.time() - t1

t1 = time.time()
agora = datetime.datetime.utcnow()
voters = list(models.Voter.objects.filter(election=e).order_by("id"))
batch = []
for i, v in enumerate(voters):
    ev = modelos[i % len(modelos)]
    h = ev.hash
    v.vote = ev
    v.vote_hash = h
    v.cast_at = agora
    batch.append(models.CastVote(voter=v, vote=ev, vote_hash=h, vote_tinyhash=str(uuid.uuid4())[:20],
                                 cast_at=agora, verified_at=agora, cast_ip="127.0.0.1"))
models.Voter.objects.bulk_update(voters, ["vote", "vote_hash", "cast_at"], batch_size=500)
models.CastVote.objects.bulk_create(batch, batch_size=500)
seg["gravar_cedulas"] = time.time() - t1
seg["total"] = time.time() - t0
print("CARGA_OK " + json.dumps({"short_name": nome, "n": n, "q": q, "opcoes": opcoes,
                                "apuradores": apuradores, "admins": admins, "seg": seg}))
