from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.crud import usuario as crud_usuario
from app.dependencies import DbSession
from app.schemas.usuario import Token
from app.security import criar_token, verificar_senha

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    dados: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
):
    usuario = crud_usuario.buscar_por_username(db, dados.username)
    if usuario is None or not verificar_senha(dados.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    token = criar_token(sub=usuario.username, papel=usuario.papel)
    return Token(access_token=token)
