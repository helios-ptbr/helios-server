"""Configurações do fork helios-ptbr: Helios em português do Brasil.

Uso:  DJANGO_SETTINGS_MODULE=settings_ptbr  (manage.py, wsgi, gunicorn)

Importa o settings.py do Ben Adida e só sobrescreve o que é de idioma, no mesmo
estilo do settings_ci.py. Assim o settings.py não muda e não gera conflito no merge.
"""
import os

from settings import *  # noqa: F401,F403
from settings import MIDDLEWARE, ROOT_PATH

# Idioma padrão. O LocaleMiddleware abaixo escolhe pelo cookie/sessão e pelo
# cabeçalho Accept-Language do navegador; sem correspondência, vale este.
LANGUAGE_CODE = 'pt-br'

LANGUAGES = [
    ('pt-br', 'Português (Brasil)'),
    ('en', 'English'),
]

# Os arquivos .po/.mo ficam em locale/<idioma>/LC_MESSAGES/.
LOCALE_PATHS = [os.path.join(ROOT_PATH, 'locale')]

# O LocaleMiddleware precisa vir depois do SessionMiddleware (ele lê o idioma da sessão).
_session = 'django.contrib.sessions.middleware.SessionMiddleware'
_locale = 'django.middleware.locale.LocaleMiddleware'
MIDDLEWARE = [m for m in MIDDLEWARE if m != _locale]
MIDDLEWARE.insert(MIDDLEWARE.index(_session) + 1, _locale)

# Mensagem da página inicial. Quem define WELCOME_MESSAGE no ambiente continua mandando;
# sem ela, o texto padrão do Ben ("This is the default message") sai em português.
if not os.environ.get('WELCOME_MESSAGE'):
    WELCOME_MESSAGE = 'Esta é a mensagem padrão. Defina a variável de ambiente WELCOME_MESSAGE para trocá-la.'

# Página /privacy: quem opera a instância preenche estas variáveis (veja docs/privacidade.md).
# Vazias, a página usa o texto padrão: as regras são as do regramento da unidade responsável.
def _privacy(var):
    # como o get_from_env do settings.py: nos testes, o ambiente não vale
    return '' if globals().get('TESTING') else os.environ.get(var, '')


_ajuda = globals().get('HELP_EMAIL_ADDRESS', '')
PRIVACY_CONTROLADOR = _privacy('PRIVACY_CONTROLADOR')            # nome da unidade (controladora dos dados)
# contato: sem valor, usa o HELP_EMAIL_ADDRESS (menos o do Ben, que não é de ninguém daqui)
PRIVACY_CONTATO_EMAIL = _privacy('PRIVACY_CONTATO_EMAIL') or ('' if _ajuda == 'help@heliosvoting.org' else _ajuda)
PRIVACY_ENCARREGADO = _privacy('PRIVACY_ENCARREGADO')            # nome do encarregado (LGPD, art. 41)
PRIVACY_ENCARREGADO_EMAIL = _privacy('PRIVACY_ENCARREGADO_EMAIL')
PRIVACY_BASE_LEGAL = _privacy('PRIVACY_BASE_LEGAL')              # base legal (LGPD, art. 7º)
PRIVACY_RETENCAO = _privacy('PRIVACY_RETENCAO')                  # por quanto tempo os dados ficam
PRIVACY_REGRAS_URL = _privacy('PRIVACY_REGRAS_URL')              # endereço do regramento da unidade
