from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.enums import FormaPagamento


class ItemVendaCreate(BaseModel):
    produto_id: int
    vendedor_id: int
    quantidade: int


class VendaCreate(BaseModel):
    forma_pagamento: FormaPagamento
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
    forma_pagamento: FormaPagamento
    cancelada_em: datetime | None
    itens: list[ItemVendaRead]

    model_config = {"from_attributes": True}
