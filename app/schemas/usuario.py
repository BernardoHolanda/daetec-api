from pydantic import BaseModel

from app.enums import PapelUsuario


class UsuarioBase(BaseModel):
    username: str
    papel: PapelUsuario


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioRead(UsuarioBase):
    id: int

    model_config = {"from_attributes": True}
