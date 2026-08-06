from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import NomeNormalizado
from app.schemas.vendedor import VendedorRead


class ProdutoBase(BaseModel):
    nome: NomeNormalizado
    preco: Decimal = Field(gt=0)


class ProdutoCreate(ProdutoBase):
    vendedor_id: int


class ProdutoRead(ProdutoBase):
    id: int
    vendedor: VendedorRead

    model_config = {"from_attributes": True}


class ProdutoResumo(BaseModel):
    """Produto dentro de outra resposta: sem o preço atual, que não é o da venda."""

    id: int
    nome: str

    model_config = {"from_attributes": True}
