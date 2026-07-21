from pydantic import BaseModel

from app.schemas.common import NomeNormalizado


class VendedorBase(BaseModel):
    nome: NomeNormalizado


class VendedorCreate(VendedorBase):
    pass


class VendedorRead(VendedorBase):
    id: int

    model_config = {"from_attributes": True}
