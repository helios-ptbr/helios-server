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
        # menu da página da eleição (decisão de 2026-11-19)
        self.assertContains(r, 'eleitores e cédulas')
        self.assertContains(r, 'apuradores (')
        self.assertNotContains(r, 'curadoria (')
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

    def english_msgids(self):
        """Frases longas e sem variáveis do catálogo (msgid): não podem aparecer em pt-BR."""
        import re
        po = open(os.path.join(ROOT, 'locale', 'pt_BR', 'LC_MESSAGES', 'django.po'), encoding='utf-8').read()
        english = set()
        for block in po.split('\n\n')[1:]:
            parts = block.split('\nmsgid', 1)
            if len(parts) < 2 or 'msgctxt' in block:
                continue
            text = ''.join(re.findall(r'"(.*)"', parts[1].split('\nmsgstr')[0]))
            text = re.sub(r'<[^>]+>', '', text.replace('\\"', '"').replace('\\n', ' ')).strip()
            # só frases longas e sem variáveis: curtas como "Login" são iguais em inglês e português
            if len(text) >= 20 and '%(' not in text:
                english.add(' '.join(text.split()))
        return english

    def scan(self, urls):
        """Pede cada URL em pt-BR e confere que nenhum msgid em inglês aparece. Devolve quantas deram 200."""
        import re
        from html import unescape
        english = self.english_msgids()
        seen = 0
        for url in urls:
            r = self.get(url)
            if r.status_code != 200:
                continue
            seen += 1
            page = ' '.join(unescape(re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]+>', ' ', r.content.decode(), flags=re.S)).split())
            leaked = sorted(t for t in english if t in page)
            self.assertEqual(leaked, [], 'texto em inglês na tela %s' % url)
        return seen

    def test_no_english_catalog_text_in_election_pages(self):
        """Varre as telas da eleição em pt-BR: nenhum texto original (msgid) do catálogo pode aparecer."""
        paths = ['view', 'edit', 'extend', 'questions', 'voters/list', 'voters/email', 'voters/upload',
                 'trustees/view', 'admins/', 'audited-ballots/', 'freeze']
        base = '/helios/elections/%s/' % self.election.uuid
        self.assertGreaterEqual(self.scan([base + p for p in paths]), 6)

    def test_no_english_catalog_text_in_site_pages(self):
        """Varre as telas fora da eleição (início, páginas fixas, login, opt-out, estatísticas, listas)."""
        # /about, /docs, /faq e /privacy não usam {% trans %}: têm um template por idioma (test_static_pages_*).
        auth_models.User.objects.filter(user_id='ben@adida.net').update(admin_p=True)  # telas de estatísticas
        urls = ['/', '/auth/', '/auth/why',
                '/optout/', '/optout/success/', '/optin/', '/optin/success/',
                '/helios/elections/new', '/helios/elections/administered', '/helios/elections/voted',
                '/helios/stats/', '/helios/stats/elections', '/helios/stats/problem-elections',
                '/helios/stats/recent-votes', '/helios/stats/deleted-elections', '/helios/stats/user-search',
                '/helios/elections/%s/' % self.election.uuid + 'trustees/view',
                '/helios/elections/%s/' % self.election.uuid + 'voters/']
        self.assertGreaterEqual(self.scan(urls), 17)

    def test_no_english_catalog_text_in_login_and_voter_pages(self):
        """Login por senha, reenvio de credenciais, selo e eleições em que a pessoa votou (issue #21)."""
        base = '/helios/elections/%s/' % self.election.uuid
        urls = ['/auth/password/login', '/auth/password/forgot', '/helios/elections/voted',
                base + 'password_voter_resend', base + 'badge']
        self.assertGreaterEqual(self.scan(urls), 5)

    def test_no_english_catalog_text_in_trustee_pages(self):
        """O apurador entra pelo link do e-mail; varre início, gerador de chave, conferir chave e decifrar."""
        trustee, _ = models.Trustee.objects.get_or_create(
            election=self.election, email='fulana@example.com',
            defaults={'uuid': 'trustee-varredura', 'name': 'Fulana', 'secret': 'segredo', 'public_key_hash': 'HASH'})
        login = reverse('trustee@login', args=[self.election.short_name, trustee.email, trustee.secret])
        self.client.logout()
        self.get(login)  # grava a sessão do apurador
        base = '/helios/elections/%s/trustees/%s/' % (self.election.uuid, trustee.uuid)
        urls = [base + 'home', base + 'keygenerator', base + 'check-sk', base + 'decrypt-and-prove']
        self.assertGreaterEqual(self.scan(urls), 3)

    STATIC_PAGES = {'/about': ('Sobre o Helios Voting', 'About Helios Voting'),
                    '/docs': ('Documentação', 'Documentation'),
                    '/faq': ('Perguntas frequentes', 'What makes Helios different'),
                    '/privacy': ('Privacidade', 'built-in privacy')}

    def test_static_pages_in_portuguese(self):
        for url, (pt, en) in self.STATIC_PAGES.items():
            r = self.get(url)
            self.assertContains(r, pt, msg_prefix=url)
            # /privacy é texto próprio do fork (descreve este código), com o próprio aviso
            self.assertContains(r, 'Sobre este texto' if url == '/privacy' else 'Tradução não oficial', msg_prefix=url)
            self.assertContains(r, 'https://vote.heliosvoting.org' + url, msg_prefix=url)
            self.assertNotContains(r, en, msg_prefix=url)

    def test_pagina_de_privacidade_padrao(self):
        r = self.get('/privacy')
        # sem variáveis PRIVACY_*: as regras são as do regramento da unidade
        for t in ('regramento da unidade', 'Lei Geral de Proteção de Dados', 'Dados que ficam guardados',
                  'Os seus direitos', 'Encarregado pelo tratamento de dados pessoais', 'ID do eleitor e senha de votação',
                  'não só um resumo dela'):
            self.assertContains(r, t)
        # afirmações do texto antigo que o código não sustenta
        for t in ('Facebook', 'Twitter', 'Yahoo', '>help@heliosvoting.org</a>'):
            self.assertNotContains(r, t)

    def test_pagina_de_privacidade_preenchida(self):
        with override_settings(PRIVACY_CONTROLADOR='Universidade Exemplo', PRIVACY_CONTATO_EMAIL='privacidade@exemplo.br',
                               PRIVACY_ENCARREGADO='Maria da Silva', PRIVACY_ENCARREGADO_EMAIL='dpo@exemplo.br',
                               PRIVACY_BASE_LEGAL='execução de políticas públicas', PRIVACY_RETENCAO='cinco anos',
                               PRIVACY_REGRAS_URL='https://exemplo.br/regras'):
            r = self.get('/privacy')
        for t in ('<b>Universidade Exemplo</b>', 'mailto:privacidade@exemplo.br', 'Maria da Silva', 'mailto:dpo@exemplo.br',
                  'execução de políticas públicas', 'cinco anos', 'href="https://exemplo.br/regras"'):
            self.assertContains(r, t)

    def test_pagina_de_privacidade_escapa_html(self):
        with override_settings(PRIVACY_CONTROLADOR='<script>x</script>'):
            r = self.get('/privacy')
        self.assertNotContains(r, '<script>x</script>')
        self.assertContains(r, '&lt;script&gt;x&lt;/script&gt;')

    def test_pagina_traducao_e_link_no_topo(self):
        r = self.get('/translation')
        self.assertEqual(r.status_code, 200)
        for t in ('<h2>Tradução</h2>', 'github.com/shirlei/helios-server', 'github.com/labsec/helios-server',
                  'github.com/ifsc/helios-server', 'github.com/ufscar/helios-server', 'github.com/STI-UFMA/helios-server-main',
                  'eleitor, cédula, depositar, questão e ID do eleitor'):
            self.assertContains(r, t)
        self.assertContains(self.get('/'), '<a href="/translation">Tradução</a>')

    def test_pagina_traducao_em_ingles_sem_link_no_topo(self):
        r = self.get('/translation', lang='en')
        self.assertContains(r, '<h2>Translation</h2>')
        self.assertNotContains(self.get('/', lang='en'), 'href="/translation"')

    def test_static_pages_in_english_are_unchanged(self):
        for url, (pt, en) in self.STATIC_PAGES.items():
            r = self.get(url, 'en')
            self.assertContains(r, en, msg_prefix=url)
            self.assertNotContains(r, pt, msg_prefix=url)
            self.assertNotContains(r, 'Tradução não oficial', msg_prefix=url)

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
        self.assertContains(r, '&mdash; Apuradores')
        self.assertContains(r, 'Os apuradores são responsáveis')
        self.assertNotContains(r, 'Trustees are responsible')

    def test_trustees_page_in_english(self):
        r = self.get(reverse('election@trustees@view', args=[self.election.uuid]), lang='en')
        self.assertContains(r, 'Trustees are responsible')

    def test_voters_list_page(self):
        r = self.get(reverse('election@voters@list-pretty', args=[self.election.uuid]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Eleitores e centro de rastreamento de cédulas')
        self.assertContains(r, 'Quem pode votar?')
        self.assertNotContains(r, 'Who can vote?')

    def test_voters_list_page_in_english(self):
        r = self.get(reverse('election@voters@list-pretty', args=[self.election.uuid]), lang='en')
        self.assertContains(r, 'Who can vote?')

    def test_admins_page(self):
        r = self.get(reverse('election@admins', args=[self.election.uuid]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '&mdash; Administradores')
        self.assertNotContains(r, 'Pessoas administradoras de')
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
        self.assertIn('ID do eleitor: maria', body)
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
    """As telas do apurador têm JavaScript com textos: o Django traduz tudo no servidor."""
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

    def test_keygenerator_page_in_portuguese_and_english(self):
        from django.test import RequestFactory
        from django.contrib.sessions.backends.db import SessionStore
        from django.utils import translation
        from helios.view_utils import render_template

        election = models.Election.objects.all()[0]
        trustee, _ = models.Trustee.objects.get_or_create(
            election=election, email='fulana@example.com',
            defaults={'uuid': 'trustee-teste', 'name': 'Fulana', 'public_key_hash': 'HASH'})
        paginas = {}
        for lang in ('pt-br', 'en'):
            request = RequestFactory().get('/x')
            request.session = SessionStore()
            request.session['csrf_token'] = 'tok'
            with override_settings(LOCALE_PATHS=[os.path.join(ROOT, 'locale')]), translation.override(lang):
                paginas[lang] = render_template(request, 'election_keygenerator',
                                                {'election': election, 'trustee': trustee, 'eg_params_json': '{}'}).content.decode()
        self.assertIn('Gerar as chaves da eleição', paginas['pt-br'])
        self.assertIn('Apurador Fulana', paginas['pt-br'])
        self.assertNotIn('Generate Election Keys', paginas['pt-br'])
        self.assertIn('Generate Election Keys', paginas['en'])
        self.assertIn('Trustee Fulana', paginas['en'])

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
        self.assertIn("tipo de eleitor inválido 'xyz'", str(ctx.exception))


@unittest.skipUnless(os.path.exists(MO), "rode compilemessages antes (django.mo não existe)")
class PtBrTimezoneTextsTests(WebTest):
    def get(self, lang):
        with override_settings(MIDDLEWARE=ptbr_middleware(), LOCALE_PATHS=[os.path.join(ROOT, 'locale')]):
            return self.client.get('/', HTTP_ACCEPT_LANGUAGE=lang)

    def test_timezone_script_gets_portuguese_texts_and_language(self):
        r = self.get('pt-br')
        self.assertContains(r, 'Tempo Universal Coordenado')
        self.assertContains(r, 'lang="pt-br"')

    def test_timezone_balloon_text_in_portuguese(self):
        r = self.get('pt-br')
        self.assertContains(r, 'Mato Grosso')
        self.assertContains(r, 'ajuste o fuso do seu computador')

    def test_timezone_script_texts_in_english(self):
        r = self.get('en')
        self.assertContains(r, 'Universal Coordinated Time')
        self.assertNotContains(r, 'Tempo Universal Coordenado')


@unittest.skipUnless(os.path.exists(MO), "rode compilemessages antes (django.mo não existe)")
class PtBrPluralTests(WebTest):
    """Plurais do pt-BR: 0 e 1 usam o singular; 2 ou mais, o plural."""

    def render(self, template, lang='pt-br'):
        from django.template import Template, Context
        from django.utils import translation
        with override_settings(LOCALE_PATHS=[os.path.join(ROOT, 'locale')]), translation.override(lang):
            return Template('{% load i18n %}' + template).render(Context({}))

    def test_voters_singular_e_plural(self):
        t = '{% blocktranslate trimmed count n=N %}{{ n }} voter{% plural %}{{ n }} voters{% endblocktranslate %}'
        self.assertEqual(self.render(t.replace('N', '1')), '1 eleitor')
        self.assertEqual(self.render(t.replace('N', '0')), '0 eleitor')
        self.assertEqual(self.render(t.replace('N', '2')), '2 eleitores')
        self.assertEqual(self.render(t.replace('N', '1'), 'en'), '1 voter')
        self.assertEqual(self.render(t.replace('N', '2'), 'en'), '2 voters')

    def test_cast_votes_com_negrito(self):
        t = '{% blocktranslate count n=N %}<b>{{ n }}</b> cast vote.{% plural %}<b>{{ n }}</b> cast votes.{% endblocktranslate %}'
        self.assertEqual(self.render(t.replace('N', '1')), '<b>1</b> voto depositado.')
        self.assertEqual(self.render(t.replace('N', '3')), '<b>3</b> votos depositados.')


@unittest.skipUnless(os.path.exists(MO), "rode compilemessages antes (django.mo não existe)")
class PtBrBateriaDockerTests(WebTest):
    """Regressões achadas na bateria de testes do Docker (2026-11-18)."""

    def trad(self, texto, lang='pt-br'):
        from django.utils import translation
        with override_settings(LOCALE_PATHS=[os.path.join(ROOT, 'locale')]), translation.override(lang):
            return translation.gettext(texto)

    def test_textos_do_eleitor_dizem_id_do_eleitor(self):
        self.assertEqual(self.trad('Voter ID'), 'ID do eleitor')
        self.assertEqual(self.trad('Bad Username or Password'), 'Login ou senha incorretos.')
        self.assertIn('ID do eleitor', self.trad('Enter the voter ID you were assigned for this election'))

    def test_termos_decididos_em_2026_11_19(self):
        """eleitor, depositar a cédula, questão e ID do eleitor (e o resto do vocabulário fica como estava)."""
        self.assertEqual(self.trad('CAST this ballot'), 'DEPOSITAR esta cédula')
        self.assertEqual(self.trad('Vote Successfully Cast!'), 'Voto depositado com sucesso!')
        self.assertEqual(self.trad('Question #%(n)s') % {'n': 2}, 'Questão #2')
        self.assertEqual(self.trad('Voter ID'), 'ID do eleitor')
        # "Enviar" continua para o que não é depositar a cédula
        self.assertEqual(self.trad('Send To'), 'Enviar para')

    def test_mensagens_novas_em_portugues_e_ingles_intacto(self):
        self.assertEqual(self.trad('the voter file is empty'), 'o arquivo está vazio')
        self.assertEqual(self.trad('the voter file is empty', 'en'), 'the voter file is empty')
        msgid = 'An election with short name %(short_name)s already exists'
        self.assertEqual(self.trad(msgid) % {'short_name': 'x'}, 'Já existe uma eleição com o nome curto x')

    def test_email_de_voto_registrado(self):
        from django.template import Context, loader
        from django.utils import translation

        class Obj:
            pass

        voter, election, cast = Obj(), Obj(), Obj()
        voter.name, voter.alias = 'Maria', 'V12'
        election.name, election.use_voter_aliases = 'Eleição X', True
        cast.vote_hash = 'HASH'
        ctx = dict(voter=voter, election=election, cast_vote=cast, cast_vote_url='http://x/v/HASH')
        for lang, esperado in (('pt-br', 'Seu voto em Eleição X foi depositado.'),
                               ('en', 'You have successfully cast a vote in Eleição X.')):
            with override_settings(LOCALE_PATHS=[os.path.join(ROOT, 'locale')]), translation.override(lang):
                corpo = loader.get_template('email/cast_vote_body.txt').template.render(Context(ctx, autoescape=False))
            self.assertIn(esperado, corpo)


@unittest.skipUnless(os.path.exists(MO), "rode compilemessages antes (django.mo não existe)")
class PtBrAvisosPorEmailTests(WebTest):
    """E-mails de aviso para a administração e para o apurador (tasks.py e views.py)."""

    def trad(self, fn, *args, lang='pt-br'):
        from django.utils import translation
        with override_settings(LOCALE_PATHS=[os.path.join(ROOT, 'locale')]), translation.override(lang):
            return fn(*args)

    def test_avisos_em_portugues_e_ingles_intacto(self):
        from django.utils.translation import gettext, ngettext
        corpo = "\nThe encrypted tally for election %(election)s has been computed.\n\n--\nHelios\n"
        self.assertIn('A apuração cifrada da eleição X foi calculada.',
                      self.trad(gettext, corpo) % {'election': 'X'})
        self.assertIn('The encrypted tally for election X has been computed.',
                      self.trad(gettext, corpo, lang='en') % {'election': 'X'})
        self.assertEqual(self.trad(gettext, 'your trustee homepage for %(election)s') % {'election': 'X'},
                         'a sua página de apurador de X')

    def test_plural_de_pessoas_criadas(self):
        from django.utils.translation import ngettext
        um, varias = '1 voter has been created.', '%(n)d voters have been created.'
        self.assertEqual(self.trad(ngettext, um, varias, 1), '1 eleitor foi criado.')
        self.assertEqual(self.trad(ngettext, um, varias, 7) % {'n': 7}, '7 eleitores foram criados.')
        self.assertEqual(self.trad(ngettext, um, varias, 7, lang='en') % {'n': 7}, '7 voters have been created.')
