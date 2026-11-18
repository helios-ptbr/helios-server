"""Cria (ou atualiza) uma pessoa administradora com login e senha.

Fork helios-ptbr: o Helios não tem tela para isso nem /admin do Django.
A pessoa entra em /auth/password/login e pode criar eleições.

Uso, no Docker:
    docker compose exec web python manage.py criar_administrador maria --nome "Maria Silva" --email maria@exemplo.br
A senha é pedida no terminal. Para scripts, use a variável HELIOS_SENHA (evita a senha no histórico).
"""
import getpass
import os

from django.core.management.base import BaseCommand, CommandError

from helios_auth.models import User


class Command(BaseCommand):
    help = "Cria uma pessoa administradora (login por senha) que pode criar eleições."

    def add_arguments(self, parser):
        parser.add_argument('login', help="login da pessoa, por exemplo maria")
        parser.add_argument('--nome', default=None, help="nome para mostrar (padrão: o login)")
        parser.add_argument('--email', default=None,
                            help="e-mail da pessoa; sem ele, o 'esqueci a senha' não funciona")
        parser.add_argument('--site', action='store_true',
                            help="marca também como administradora do site (admin_p: estatísticas e busca de usuários)")
        parser.add_argument('--redefinir-senha', action='store_true', dest='redefinir',
                            help="se o login já existe, troca a senha em vez de falhar")

    def _senha(self):
        senha = os.environ.get('HELIOS_SENHA')
        if senha:
            return senha
        senha = getpass.getpass("Senha: ")
        if senha != getpass.getpass("Senha (de novo): "):
            raise CommandError("as senhas não são iguais")
        return senha

    def handle(self, *args, **opts):
        login = opts['login'].strip()
        if not login or len(login) > 50 or any(c.isspace() for c in login):
            raise CommandError("o login precisa ter de 1 a 50 caracteres, sem espaços")

        existe = User.objects.filter(user_type='password', user_id=login).first()
        if existe and not opts['redefinir']:
            raise CommandError(f"o login '{login}' já existe; use --redefinir-senha para trocar a senha")

        senha = self._senha().strip()
        if len(senha) < 8:
            raise CommandError("use uma senha com pelo menos 8 caracteres")

        nome = opts['nome'] or (existe.name if existe else None) or login
        info = dict(existe.info) if existe and existe.info else {}
        info.update({'password': senha, 'name': nome})
        if opts['email']:
            info['email'] = opts['email']

        user = existe or User(user_type='password', user_id=login)
        user.name = nome
        user.info = info
        if opts['site']:
            user.admin_p = True
        user.save()

        acao = "senha trocada" if existe else "criada"
        self.stdout.write(self.style.SUCCESS(
            f"Pessoa administradora '{login}' {acao}. Ela entra em /auth/password/login."))
