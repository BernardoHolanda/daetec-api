from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from app.security import hash_senha


def criar_usuario(db: Session, dados: UsuarioCreate) -> Usuario:
    usuario = Usuario(username=dados.username, senha_hash=hash_senha(dados.senha), papel=dados.papel)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def listar_usuarios(db: Session) -> list[Usuario]:
    return list(db.scalars(select(Usuario)).all())


def obter_usuario(db: Session, usuario_id: int) -> Usuario | None:
    return db.get(Usuario, usuario_id)


def buscar_por_username(db: Session, username: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.username == username))
