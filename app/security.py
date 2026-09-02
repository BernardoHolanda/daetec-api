import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# environ[] e não getenv(): sem o segredo, morrer no boot em vez de no primeiro login
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRA_MINUTOS = 60
CABECALHO_TOKEN_NOVO = "X-Token-Renovado"


def hash_senha(senha: str) -> str:
    """Transformação só de ida: o salt vai embutido no próprio hash."""
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())


def criar_token(sub: str, papel: str) -> str:
    """JWT com `sub` (username) e `papel`, válido por `TOKEN_EXPIRA_MINUTOS`."""
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "papel": papel,
        "exp": agora + timedelta(minutes=TOKEN_EXPIRA_MINUTOS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def perto_de_expirar(payload: dict) -> bool:
    """Passou da metade da vida: hora de mandar um substituto junto da resposta."""
    expira_em = datetime.fromtimestamp(payload["exp"], timezone.utc)
    return expira_em - datetime.now(timezone.utc) < timedelta(
        minutes=TOKEN_EXPIRA_MINUTOS / 2
    )
