from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import usuario as crud_usuario
from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioRead
from app.dependencies import get_current_user, exigir_admin
from app.models.usuario import Usuario

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("", response_model=UsuarioRead, status_code=201, dependencies=[Depends(exigir_admin)])
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return crud_usuario.criar_usuario(db, dados)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[UsuarioRead], dependencies=[Depends(exigir_admin)])
def listar_usuarios(db: Session = Depends(get_db)):
    return crud_usuario.listar_usuarios(db)


@router.get("/me", response_model=UsuarioRead)
def usuario_atual(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioRead, dependencies=[Depends(exigir_admin)])
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = crud_usuario.obter_usuario(db, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario
