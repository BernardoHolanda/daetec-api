import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt


JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRA_MINUTOS = 60


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())


def criar_token(sub: str, papel: str) -> str:
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "papel": papel,
        "exp": agora + timedelta(minutes=TOKEN_EXPIRA_MINUTOS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
