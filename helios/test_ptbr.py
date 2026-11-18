"""Testes de tradução pt-BR (fork helios-ptbr). Não alteram os testes do upstream.

Precisam do catálogo compilado: `python manage.py compilemessages`.
Rodam com qualquer settings: ligam o LocaleMiddleware e o pt-BR só dentro do teste.
"""
import os

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from django_webtest import WebTest

from helios import models
from helios_auth import models as auth_models

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MO = os.path.join(ROOT, 'locale', 'pt_BR', 'LC_MESSAGES', 'django.mo')
LOCALE_MW = 'django.middleware.locale.LocaleMiddleware'
SESSION_MW = 'django.contrib.sessions.middleware.SessionMiddleware'


def ptbr_middleware():
    mw = [m for m in settings.MIDDLEWARE if m != LOCALE_MW]
    mw.insert(mw.index(SESSION_MW) + 1, LOCALE_MW)
    return mw


import unittest  # noqa: E402


@unittest.skipUnless(os.path.exists(MO), "rode compilemessages antes (django.mo não existe)")
class PtBrRenderTests(WebTest):
    fixtures = ['users.json', 'election.json']
    allow_database_queries = True

    def setUp(self):
        self.election = models.Election.objects.all()[0]
        self.url = reverse('election@view', args=[self.election.uuid])

    def get(self, lang):
        with override_settings(MIDDLEWARE=ptbr_middleware(), LOCALE_PATHS=[os.path.join(ROOT, 'locale')]):
            return self.client.get(self.url, HTTP_ACCEPT_LANGUAGE=lang)

    def test_election_view_in_portuguese(self):
        r = self.get('pt-br')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Informações de auditoria')
        self.assertContains(r, 'lang="pt-br"')
        self.assertNotContains(r, 'Audit Info')

    def test_election_view_stays_in_english_by_default(self):
        r = self.get('en')
        self.assertContains(r, 'Audit Info')
        self.assertNotContains(r, 'Informações de auditoria')


@unittest.skipUnless(os.path.exists(MO), "rode compilemessages antes (django.mo não existe)")
class PtBrAdminPagesTests(WebTest):
    fixtures = ['users.json', 'election.json']
    allow_database_queries = True

    def setUp(self):
        self.election = models.Election.objects.all()[0]
        user = auth_models.User.objects.get(user_id='ben@adida.net', user_type='google')
        # não faça requisição aqui: o client guarda a lista de middlewares da primeira requisição
        session = self.client.session
        session['user'] = {'type': user.user_type, 'user_id': user.user_id}
        session.save()

    def get(self, url, lang='pt-br'):
        with override_settings(MIDDLEWARE=ptbr_middleware(), LOCALE_PATHS=[os.path.join(ROOT, 'locale')]):
            return self.client.get(url, HTTP_ACCEPT_LANGUAGE=lang)

    def test_new_election_page(self):
        r = self.get(reverse('elections@new'))
        self.assertContains(r, 'Criar uma nova eleição')
        self.assertNotContains(r, 'Create a New Election')
        self.assertContains(r, 'Nome curto')
        self.assertContains(r, 'Início da votação')
        self.assertContains(r, '>Consulta<')
        self.assertNotContains(r, 'Short name')

    def test_new_election_page_in_english(self):
        r = self.get(reverse('elections@new'), lang='en')
        self.assertContains(r, 'Create a New Election')
        self.assertContains(r, 'Short name')

    def test_freeze_page(self):
        r = self.get(reverse('election@freeze', args=[self.election.uuid]))
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, 'Freeze Ballot')
        self.assertContains(r, 'Congelar a urna')

    def test_trustees_page(self):
        r = self.get(reverse('election@trustees@view', args=[self.election.uuid]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Pessoas curadoras')
        self.assertNotContains(r, 'Trustees are responsible')

    def test_trustees_page_in_english(self):
        r = self.get(reverse('election@trustees@view', args=[self.election.uuid]), lang='en')
        self.assertContains(r, 'Trustees are responsible')

    def test_voters_list_page(self):
        r = self.get(reverse('election@voters@list-pretty', args=[self.election.uuid]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Pessoas eleitoras e centro de rastreamento de cédulas')
        self.assertContains(r, 'Quem pode votar?')
        self.assertNotContains(r, 'Who can vote?')

    def test_voters_list_page_in_english(self):
        r = self.get(reverse('election@voters@list-pretty', args=[self.election.uuid]), lang='en')
        self.assertContains(r, 'Who can vote?')

    def test_admins_page(self):
        r = self.get(reverse('election@admins', args=[self.election.uuid]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Pessoas administradoras')
        self.assertContains(r, 'adicionar uma pessoa administradora')
        self.assertNotContains(r, 'add an administrator')

    def test_admin_add_error_in_portuguese(self):
        url = reverse('election@admins@add', args=[self.election.uuid])
        with override_settings(MIDDLEWARE=ptbr_middleware(), LOCALE_PATHS=[os.path.join(ROOT, 'locale')]):
            self.client.get(url, HTTP_ACCEPT_LANGUAGE='pt-br')  # cria o csrf_token na sessão
            r = self.client.post(url,
                                 {'email': '', 'csrf_token': self.client.session['csrf_token']},
                                 HTTP_ACCEPT_LANGUAGE='pt-br')
        self.assertContains(r, 'Digite um endereço de e-mail.')

    def test_nocookies_page(self):
        r = self.get(reverse('cookie@no') + '?continue_url=/helios/elections/x')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Cookies são necessários no Helios')
        self.assertNotContains(r, 'Cookies are Required for Helios')


@unittest.skipUnless(os.path.exists(MO), "rode compilemessages antes (django.mo não existe)")
class PtBrEmailTests(WebTest):
    """Os e-mails saem do worker, sem requisição: o idioma vem de LANGUAGE_CODE."""

    def render(self, template, lang):
        from django.template import Context, loader
        from django.utils import translation

        class Obj:
            pass

        voter = Obj()
        voter.name, voter.voter_type, voter.voter_login_id = 'Maria', 'password', 'maria'
        voter.voter_password, voter.vote_hash, voter.alias = 'abc', 'HASH', 'V12'
        election = Obj()
        election.name, election.use_voter_aliases, election.hash = 'Eleição "X"', True, 'FP'
        voter.election = election
        ctx = dict(voter=voter, election=election, custom_message='Oi', custom_subject='Assunto',
                   election_vote_url='http://x/vote', election_url='http://x/e',
                   unsubscribe_url='http://x/out')
        with override_settings(LOCALE_PATHS=[os.path.join(ROOT, 'locale')]), translation.override(lang):
            return loader.get_template(template).template.render(Context(ctx, autoescape=False))

    def test_vote_email_in_portuguese(self):
        body = self.render('email/vote_body.txt', 'pt-br')
        self.assertIn('Olá, Maria,', body)
        self.assertIn('Seu login: maria', body)
        self.assertIn('Para deixar de receber todos os e-mails do Helios', body)
        self.assertNotIn('Dear ', body)

    def test_vote_email_in_english_is_unchanged(self):
        body = self.render('email/vote_body.txt', 'en')
        self.assertIn('Dear Maria,', body)
        self.assertIn('Your voter ID: maria', body)

    def test_email_subjects_keep_quotes_unescaped(self):
        subj = self.render('email/password_resend_subject.txt', 'pt-br')
        self.assertEqual(subj.strip(), 'Suas credenciais de votação para Eleição "X"')


@unittest.skipUnless(os.path.exists(MO), "rode compilemessages antes (django.mo não existe)")
class PtBrOptOutTests(WebTest):
    def get(self, url, lang):
        with override_settings(MIDDLEWARE=ptbr_middleware(), LOCALE_PATHS=[os.path.join(ROOT, 'locale')]):
            return self.client.get(url, HTTP_ACCEPT_LANGUAGE=lang)

    def test_optout_form_in_portuguese(self):
        r = self.get(reverse('optout_form'), 'pt-br')
        self.assertContains(r, 'Deixar de receber e-mails do Helios')
        self.assertContains(r, 'Endereço de e-mail:')
        self.assertNotContains(r, 'Opt Out of Helios Emails')

    def test_optin_form_in_portuguese(self):
        r = self.get(reverse('optin_form'), 'pt-br')
        self.assertContains(r, 'Voltar a receber e-mails do Helios')

    def test_optout_form_in_english_is_unchanged(self):
        r = self.get(reverse('optout_form'), 'en')
        self.assertContains(r, 'Opt Out of Helios Emails')


@unittest.skipUnless(os.path.exists(MO), "rode compilemessages antes (django.mo não existe)")
class PtBrTrusteePagesTests(WebTest):
    """As telas da pessoa curadora têm JavaScript com textos: o Django traduz tudo no servidor."""
    fixtures = ['users.json', 'election.json']
    allow_database_queries = True

    def render(self, name, lang):
        from django.test import RequestFactory
        from django.contrib.sessions.backends.db import SessionStore
        from django.utils import translation
        from helios.view_utils import render_template

        election = models.Election.objects.all()[0]
        trustee, _ = models.Trustee.objects.get_or_create(
            election=election, email='fulana@example.com',
            defaults={'uuid': 'trustee-teste', 'name': 'Fulana', 'public_key_hash': 'HASH'})
        request = RequestFactory().get('/x')
        request.session = SessionStore()
        request.session['csrf_token'] = 'tok'
        with override_settings(LOCALE_PATHS=[os.path.join(ROOT, 'locale')]), translation.override(lang):
            return render_template(request, name, {'election': election, 'trustee': trustee}).content.decode()

    def test_check_sk_page_in_portuguese(self):
        html = self.render('trustee_check_sk', 'pt-br')
        self.assertIn('a sua chave secreta confere!', html)
        self.assertIn('Ops, a sua chave está errada.', html)
        self.assertNotIn('your secret key matches!', html)

    def test_decrypt_page_in_portuguese_and_english(self):
        self.assertIn('PRIMEIRO PASSO: digite a sua chave secreta', self.render('trustee_decrypt_and_prove', 'pt-br'))
        self.assertIn('FIRST STEP: enter your secret key', self.render('trustee_decrypt_and_prove', 'en'))


@unittest.skipUnless(os.path.exists(MO), "rode compilemessages antes (django.mo não existe)")
class PtBrVoterFileMessagesTests(WebTest):
    def test_voter_file_errors_in_portuguese(self):
        from django.utils import translation
        from helios import models as m
        with override_settings(LOCALE_PATHS=[os.path.join(ROOT, 'locale')]), translation.override('pt-br'):
            f = m.VoterFile()
            f.voter_file_content = "xyz,maria,maria@example.com,Maria"
            with self.assertRaises(Exception) as ctx:
                list(f.itervoters())
        self.assertIn("tipo de pessoa eleitora inválido 'xyz'", str(ctx.exception))
