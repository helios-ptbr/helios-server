# Catálogo de textos a traduzir

Gerado por `tools/catalogar_textos.py`. Detalhe linha a linha em `docs/catalogo-textos.csv`.

Contagem por **ocorrência** (linha de texto), não por frase única. É uma estimativa: revisar à mão antes de fechar o escopo.

## Dificuldade

| Nível | Significado | Como traduzir |
|---|---|---|
| A | texto puro em template | `{% trans %}` |
| B | template com variável ou tag inline; string Python simples | `{% blocktrans %}` / `gettext` |
| C | JS, e-mail, Python com formatação ou montado em partes | caso a caso |

## Total

| A | B | C | Total |
|---:|---:|---:|---:|
| 471 | 402 | 106 | 979 |

## Por tipo

| Tipo | A | B | C | Total |
|---|---:|---:|---:|---:|
| email | 0 | 0 | 53 | 53 |
| js | 0 | 0 | 28 | 28 |
| python | 0 | 91 | 17 | 108 |
| python-erro-interno | 0 | 28 | 8 | 36 |
| template | 471 | 257 | 0 | 728 |
| template-atributo | 0 | 26 | 0 | 26 |

## Por arquivo (maiores primeiro)

| Arquivo | A | B | C | Total |
|---|---:|---:|---:|---:|
| `helios/templates/election_view.html` | 33 | 42 | 0 | 75 |
| `helios/views.py` | 0 | 59 | 7 | 66 |
| `helios/templates/voters_list.html` | 18 | 16 | 0 | 34 |
| `helios/templates/trustee_decrypt_and_prove.html` | 11 | 15 | 1 | 27 |
| `server_ui/templates/privacy.html` | 23 | 4 | 0 | 27 |
| `helios/templates/stats_user_search.html` | 14 | 12 | 0 | 26 |
| `server_ui/templates/about.html` | 22 | 3 | 0 | 25 |
| `helios/forms.py` | 0 | 23 | 0 | 23 |
| `helios/media/static_templates/question.html` | 19 | 3 | 0 | 22 |
| `helios/templates/election_keygenerator.html` | 13 | 8 | 0 | 21 |
| `heliosbooth/vote.html` | 10 | 2 | 8 | 20 |
| `server_ui/templates/index.html` | 16 | 2 | 0 | 18 |
| `helios/templates/email/vote_body.txt` | 0 | 0 | 17 | 17 |
| `helios/templates/list_trustees.html` | 7 | 9 | 0 | 16 |
| `server_ui/templates/docs.html` | 14 | 1 | 0 | 15 |
| `helios/templates/election_cast_confirm.html` | 7 | 6 | 1 | 14 |
| `helios/templates/election_compute_tally.html` | 6 | 7 | 0 | 13 |
| `server_ui/templates/faq.html` | 12 | 1 | 0 | 13 |
| `helios/templates/stats.html` | 8 | 4 | 0 | 12 |
| `helios/templates/voters_upload.html` | 7 | 5 | 0 | 12 |
| `server_ui/templates/base.html` | 7 | 5 | 0 | 12 |
| `helios/templates/election_bboard.html` | 5 | 6 | 0 | 11 |
| `helios/templates/optout_confirm_form.html` | 10 | 1 | 0 | 11 |
| `heliosbooth/templates/audit.html` | 8 | 3 | 0 | 11 |
| `helios/templates/election_admins.html` | 7 | 3 | 0 | 10 |
| `helios/templates/election_new_2.html` | 6 | 3 | 1 | 10 |
| `helios/templates/optout_confirmed.html` | 9 | 1 | 0 | 10 |
| `helios/templates/trustee_home.html` | 4 | 6 | 0 | 10 |
| `helios/models.py` | 0 | 6 | 3 | 9 |
| `helios/templates/election_audited_ballots.html` | 3 | 6 | 0 | 9 |
| `helios/templates/election_freeze.html` | 4 | 5 | 0 | 9 |
| `helios/templates/election_questions.html` | 0 | 2 | 7 | 9 |
| `helios_auth/templates/perms_why.html` | 8 | 1 | 0 | 9 |
| `helios/templates/base.html` | 8 | 0 | 0 | 8 |
| `helios/templates/election_admin_add.html` | 3 | 5 | 0 | 8 |
| `helios/templates/email/result_body.txt` | 0 | 0 | 8 | 8 |
| `helios/templates/email/simple_body.txt` | 0 | 0 | 8 | 8 |
| `helios/templates/stats_deleted_elections.html` | 4 | 4 | 0 | 8 |
| `helios/templates/voters_email.html` | 4 | 4 | 0 | 8 |
| `helios/templates/voters_upload_confirm.html` | 5 | 3 | 0 | 8 |
| `helios_auth/templates/base.html` | 8 | 0 | 0 | 8 |
| `heliosbooth/single-ballot-verify.html` | 6 | 2 | 0 | 8 |
| `heliosbooth/templates/seal.html` | 7 | 1 | 0 | 8 |
| `heliosverifier/verify.html` | 4 | 1 | 3 | 8 |
| `helios/templates/_castconfirm_docast.html` | 4 | 3 | 0 | 7 |
| `helios/templates/_castconfirm_password.html` | 4 | 3 | 0 | 7 |
| `helios/templates/email/password_resend_body.txt` | 0 | 0 | 7 | 7 |
| `helios/templates/optout_not_opted_out.html` | 6 | 1 | 0 | 7 |
| `helios/templates/password_voter_resend.html` | 5 | 2 | 0 | 7 |
| `helios/templates/trustee_check_sk.html` | 3 | 2 | 2 | 7 |
| `heliosbooth/templates/submit.html` | 4 | 3 | 0 | 7 |
| `server_ui/templates/confirm.html` | 4 | 3 | 0 | 7 |
| `server_ui/templates/email/cast_vote_body.txt` | 0 | 0 | 7 | 7 |
| `helios/templates/cast_done.html` | 3 | 3 | 0 | 6 |
| `helios/templates/combine_decryptions.html` | 3 | 3 | 0 | 6 |
| `helios/templates/election_admin_remove.html` | 2 | 4 | 0 | 6 |
| `helios/templates/optout_form.html` | 6 | 0 | 0 | 6 |
| `helios/templates/stats_elections.html` | 3 | 3 | 0 | 6 |
| `helios/templates/voters_manage.html` | 4 | 2 | 0 | 6 |
| `helios/workflows/homomorphic.py` | 0 | 3 | 3 | 6 |
| `heliosbooth/templates/election.html` | 5 | 1 | 0 | 6 |
| `heliosbooth/templates/question.html` | 6 | 0 | 0 | 6 |
| `helios/templates/election_build.html` | 0 | 1 | 4 | 5 |
| `helios/templates/election_not_started.html` | 2 | 3 | 0 | 5 |
| `helios/templates/election_tallied.html` | 2 | 3 | 0 | 5 |
| `helios/templates/optout_success.html` | 5 | 0 | 0 | 5 |
| `helios/templates/password_voter_login.html` | 3 | 2 | 0 | 5 |
| `helios/templates/release_result.html` | 2 | 3 | 0 | 5 |
| `helios/templates/voters_eligibility.html` | 1 | 4 | 0 | 5 |
| `helios/templates/voters_search.html` | 2 | 3 | 0 | 5 |
| `helios_auth/auth_systems/google.py` | 0 | 5 | 0 | 5 |
| `helios_auth/templates/login_failed.html` | 4 | 1 | 0 | 5 |
| `helios/datatypes/__init__.py` | 0 | 1 | 3 | 4 |
| `helios/templates/election_register.html` | 1 | 3 | 0 | 4 |
| `helios/templates/nocookies.html` | 3 | 1 | 0 | 4 |
| `helios/templates/stats_problem_elections.html` | 3 | 1 | 0 | 4 |
| `helios/templates/stats_recent_votes.html` | 3 | 1 | 0 | 4 |
| `helios_auth/auth_systems/devlogin.py` | 0 | 3 | 1 | 4 |
| `helios_auth/templates/auth/devlogin.html` | 4 | 0 | 0 | 4 |
| `helios_auth/views.py` | 0 | 2 | 2 | 4 |
| `server_ui/templates/done.html` | 2 | 2 | 0 | 4 |
| `helios/templates/castvote.html` | 0 | 3 | 0 | 3 |
| `helios/templates/email/info_body.txt` | 0 | 0 | 3 | 3 |
| `helios_auth/auth_systems/gitlab.py` | 0 | 3 | 0 | 3 |
| `helios_auth/auth_systems/linkedin.py` | 0 | 3 | 0 | 3 |
| `helios_auth/auth_systems/password.py` | 0 | 2 | 1 | 3 |
| `helios_auth/templates/password/forgot.html` | 1 | 2 | 0 | 3 |
| `server_ui/templates/election_tallied.html` | 2 | 1 | 0 | 3 |
| `helios/tasks.py` | 0 | 0 | 2 | 2 |
| `helios/templates/election_badge.html` | 0 | 2 | 0 | 2 |
| `helios/templates/election_extend.html` | 0 | 2 | 0 | 2 |
| `helios/templates/election_new.html` | 1 | 1 | 0 | 2 |
| `helios/templates/elections_administered.html` | 0 | 2 | 0 | 2 |
| `helios/templates/new_trustee.html` | 0 | 2 | 0 | 2 |
| `helios_auth/auth_systems/github.py` | 0 | 2 | 0 | 2 |
| `helios_auth/security/__init__.py` | 0 | 2 | 0 | 2 |
| `helios_auth/security/oauth.py` | 0 | 0 | 2 | 2 |
| `helios_auth/templates/index.html` | 1 | 1 | 0 | 2 |
| `heliosbooth/templates/done.html` | 2 | 0 | 0 | 2 |
| `templates/404.html` | 2 | 0 | 0 | 2 |
| `templates/500.html` | 2 | 0 | 0 | 2 |
| `helios/datatypes/legacy.py` | 0 | 1 | 0 | 1 |
| `helios/security.py` | 0 | 1 | 0 | 1 |
| `helios/templates/election_edit.html` | 0 | 1 | 0 | 1 |
| `helios/templates/elections_voted.html` | 0 | 1 | 0 | 1 |
| `helios/templates/email/password_resend_subject.txt` | 0 | 0 | 1 | 1 |
| `helios/templates/email/result_subject.txt` | 0 | 0 | 1 | 1 |
| `helios/templates/notification/result.txt` | 0 | 0 | 1 | 1 |
| `helios/utils.py` | 0 | 1 | 0 | 1 |
| `helios/view_utils.py` | 0 | 0 | 1 | 1 |
| `helios_auth/auth_systems/openid/view_helpers.py` | 0 | 1 | 0 | 1 |
| `helios_auth/templates/login_box.html` | 0 | 1 | 0 | 1 |
| `helios_auth/templates/password/login.html` | 0 | 1 | 0 | 1 |
| `helios_auth/utils.py` | 0 | 1 | 0 | 1 |
| `heliosbooth/boothworker-single.js` | 0 | 0 | 1 | 1 |
| `heliosbooth/templates/footer.html` | 1 | 0 | 0 | 1 |
