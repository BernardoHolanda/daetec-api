from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import NomeNormalizado


class ProdutoBase(BaseModel):
    nome: NomeNormalizado
    preco: Decimal = Field(gt=0)


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoRead(ProdutoBase):
    id: int

    model_config = {"from_attributes": True}
