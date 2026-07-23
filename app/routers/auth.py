from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.crud import usuario as crud_usuario
from app.database import get_db
from app.schemas.usuario import Token
from app.security import criar_token, verificar_senha

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    dados: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario = crud_usuario.buscar_por_username(db, dados.username)
    if usuario is None or not verificar_senha(dados.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    token = criar_token(sub=usuario.username, papel=usuario.papel)
    return Token(access_token=token)
