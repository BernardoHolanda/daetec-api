from pydantic import BaseModel, EmailStr

from app.schemas.common import SenhaForte
from app.enums import PapelUsuario


class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    papel: PapelUsuario


class UsuarioCreate(UsuarioBase):
    senha: SenhaForte


class UsuarioRead(UsuarioBase):
    id: int

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
