from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.crud import usuario as crud_usuario
from app.database import get_db
from app.enums import PapelUsuario
from app.models.usuario import Usuario
from app.security import JWT_ALGORITHM, JWT_SECRET

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

DbSession = Annotated[Session, Depends(get_db)]
TokenBearer = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(token: TokenBearer, db: DbSession) -> Usuario:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise credenciais_invalidas

    username = payload.get("sub")
    if username is None:
        raise credenciais_invalidas

    usuario = crud_usuario.buscar_por_username(db, username)
    if usuario is None:
        raise credenciais_invalidas

    return usuario


UsuarioLogado = Annotated[Usuario, Depends(get_current_user)]


def exigir_admin(usuario: UsuarioLogado) -> Usuario:
    if usuario.papel != PapelUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requer papel de administrador",
        )
    return usuario
