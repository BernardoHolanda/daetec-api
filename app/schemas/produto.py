from decimal import Decimal

from pydantic import BaseModel


class ProdutoBase(BaseModel):
    nome: str
    preco: Decimal


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoRead(ProdutoBase):
    id: int

    model_config = {"from_attributes": True}