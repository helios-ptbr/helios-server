# Imagem do Helios (fork helios-ptbr). Também serve para o Fly.io e qualquer host Docker.
# O Heroku continua usando o Procfile e os buildpacks, e ignora este arquivo.
#
# Dois estágios:
#   build: compila o python-ldap, instala as dependências e compila as traduções (.mo).
#   final: só o Python, as bibliotecas de execução do LDAP, o .venv e o código.
#          Sem compilador e sem gettext.

# ---- build ---------------------------------------------------------------
FROM python:3.13-slim AS build

# python-ldap é compilado do código-fonte: precisa dos cabeçalhos LDAP/SASL e de um compilador.
# gettext traz o msgfmt, usado pelo compilemessages.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    gettext \
    libldap2-dev \
    libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /bin/uv

WORKDIR /app

# instala as dependências antes do código, para o cache não se perder a cada mudança
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

# o .mo não vai para o git: compila aqui. O compilemessages não usa banco de dados.
RUN DJANGO_SETTINGS_MODULE=settings_ptbr /app/.venv/bin/python manage.py compilemessages

# ---- final ---------------------------------------------------------------
FROM python:3.13-slim

# bibliotecas de execução do python-ldap (os pacotes -dev ficam só no estágio build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libldap2 \
    libsasl2-2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=build /app /app

# usa os executáveis do virtualenv direto; `uv run` sincronizaria de novo na partida.
# settings_ptbr: Helios em português do Brasil. Quem quiser em inglês usa o repositório do Ben.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=settings_ptbr \
    PORT=8080

# o Helios guarda os arquivos enviados no banco: o app nunca escreve em disco
RUN useradd --system --no-create-home helios
USER helios

EXPOSE 8080

# o fly.toml e o docker-compose.yml trocam este comando por processo; este roda o servidor web
CMD ["sh", "-c", "exec gunicorn wsgi:application -b 0.0.0.0:${PORT} -w 4"]
