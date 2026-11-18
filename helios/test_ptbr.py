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
