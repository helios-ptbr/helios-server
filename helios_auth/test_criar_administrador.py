import os
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from helios_auth.models import User


class CriarAdministradorTests(TestCase):
    def roda(self, *args, senha='senha-de-teste'):
        saida = StringIO()
        with mock.patch.dict(os.environ, {'HELIOS_SENHA': senha}):
            call_command('criar_administrador', *args, stdout=saida)
        return saida.getvalue()

    def test_cria_e_guarda_dados(self):
        self.roda('maria', '--nome', 'Maria Silva', '--email', 'maria@exemplo.br')
        u = User.objects.get(user_type='password', user_id='maria')
        self.assertEqual(u.name, 'Maria Silva')
        self.assertEqual(u.info['email'], 'maria@exemplo.br')
        self.assertEqual(u.info['password'], 'senha-de-teste')
        self.assertFalse(u.admin_p)
        self.assertTrue(u.can_create_election())

    def test_marca_administradora_do_site(self):
        self.roda('chefe', '--site')
        self.assertTrue(User.objects.get(user_id='chefe').admin_p)

    def test_login_repetido_falha_sem_redefinir(self):
        self.roda('ana')
        with self.assertRaises(CommandError):
            self.roda('ana', senha='outra-senha-1')
        self.roda('ana', '--redefinir-senha', senha='outra-senha-1')
        self.assertEqual(User.objects.get(user_id='ana').info['password'], 'outra-senha-1')

    def test_rejeita_login_com_espaco_e_senha_curta(self):
        with self.assertRaises(CommandError):
            self.roda('com espaco')
        with self.assertRaises(CommandError):
            self.roda('beto', senha='curta')

    def test_login_na_tela(self):
        self.roda('carla', senha='uma-senha-boa')
        import re
        pagina = self.client.get('/auth/password/login')
        token = re.search(r'name="csrf_token" value="([^"]+)"', pagina.content.decode()).group(1)
        r = self.client.post('/auth/password/login',
                             {'username': 'carla', 'password': 'uma-senha-boa', 'csrf_token': token})
        self.assertEqual(r.status_code, 302)
        r = self.client.post('/auth/password/login',
                             {'username': 'carla', 'password': 'errada', 'csrf_token': token})
        self.assertEqual(r.status_code, 200)
