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
