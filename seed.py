"""Seed inicial do banco.

Cria o usuário admin inicial, resolvendo o ovo-e-galinha: criar usuário
exige um admin logado, mas o primeiro admin não pode ser criado pela API.

Rodar:  docker compose exec api python seed.py

É idempotente — rodar várias vezes não duplica nada.
"""
import os

from sqlalchemy import select

from app.database import SessionLocal
from app.enums import PapelUsuario
from app.models.usuario import Usuario
from app.security import hash_senha


def criar_admin_inicial(db) -> None:
    username = os.getenv("ADMIN_USERNAME", "admin")
    senha = os.getenv("ADMIN_PASSWORD")
    email = os.getenv("ADMIN_EMAIL", "admin@daetec.com")

    if not senha:
        raise SystemExit("ADMIN_PASSWORD não definido no .env — abortando.")

    existente = db.scalar(select(Usuario).where(Usuario.username == username))
    if existente is not None:
        print(f"admin '{username}' já existe — nada a fazer.")
        return

    db.add(
        Usuario(
            username=username,
            email=email,
            senha_hash=hash_senha(senha),
            papel=PapelUsuario.ADMIN,
        )
    )
    db.commit()
    print(f"admin '{username}' criado.")


def main() -> None:
    db = SessionLocal()
    try:
        criar_admin_inicial(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
