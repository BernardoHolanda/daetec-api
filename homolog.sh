#!/usr/bin/env bash
# Roda qualquer comando do container `api` apontado para o branch homolog do Neon.
#
#   ./homolog.sh alembic upgrade head
#   ./homolog.sh python seed.py
#   ./homolog.sh python -m pytest        # NÃO faça isso: a suíte dá drop_all
#
# set -e: aborta no primeiro erro, em vez de seguir com o passo seguinte
# set -u: variável não definida vira erro, não string vazia silenciosa
set -euo pipefail

cd "$(dirname "$0")"

URL=$(grep '^DATABASE_URL_HOMOLOG=' .env | cut -d= -f2- || true)
if [ -z "$URL" ]; then
  echo "erro: DATABASE_URL_HOMOLOG não está no .env" >&2
  exit 1
fi

# mostra o host antes de rodar: o erro caro aqui é achar que está no homolog
# e estar na produção, e host errado é a única evidência que aparece a tempo
HOST=$(printf '%s' "$URL" | sed -E 's|.*@([^/]+)/.*|\1|')
echo ">> alvo: $HOST"

exec docker compose exec -T -e DATABASE_URL="$URL" api "$@"
