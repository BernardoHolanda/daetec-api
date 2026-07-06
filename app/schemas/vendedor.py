from pydantic import BaseModel


class VendedorBase(BaseModel):
    nome: str


class VendedorCreate(VendedorBase):
    pass


class VendedorRead(VendedorBase):
    id: int

    model_config = {"from_attributes": True}