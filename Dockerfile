# Base comum aos dois ambientes: tudo que produção precisa pra rodar.
FROM python:3.13-slim AS base

# --shell /bin/bash: sem isso o padrão é dash, sem histórico nem autocomplete
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser

WORKDIR /code

# requirements antes do resto: código muda toda hora, dependência quase nunca,
# e assim o cache do pip install sobrevive
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Estágio de desenvolvimento: git é 105 MB que só o Dev Container usa.
# O compose aponta pra cá com `target: dev`.
FROM base AS dev
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
USER appuser

# Último estágio = alvo padrão do build. O Cloud Run constrói sem passar target
# nenhum, então precisa ser este que fica por último.
FROM base AS producao
USER appuser
EXPOSE 8000
# Forma shell (sh -c) porque a forma exec não expande variável: o Cloud Run
# injeta a porta em $PORT, e o padrão 8000 mantém o local igual ao de antes.
CMD ["sh", "-c", "fastapi run app/main.py --host 0.0.0.0 --port ${PORT:-8000}"]
