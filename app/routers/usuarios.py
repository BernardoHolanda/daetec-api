from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import usuario as crud_usuario
from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioRead

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("", response_model=UsuarioRead)
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    return crud_usuario.criar_usuario(db, dados)


@router.get("", response_model=list[UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db)):
    return crud_usuario.listar_usuarios(db)


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = crud_usuario.obter_usuario(db, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario
