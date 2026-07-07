from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ItemVendaCreate(BaseModel):
    produto_id: int
    vendedor_id: int
    quantidade: int


class VendaCreate(BaseModel):
    itens: list[ItemVendaCreate]


class ItemVendaRead(BaseModel):
    id: int
    produto_id: int
    vendedor_id: int
    quantidade: int
    preco_unitario: Decimal

    model_config = {"from_attributes": True}


class VendaRead(BaseModel):
    id: int
    data_hora: datetime
    cancelada_em: datetime | None
    itens: list[ItemVendaRead]

    model_config = {"from_attributes": True}
