from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.enums import FormaPagamento


class ItemVendaCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)


class VendaCreate(BaseModel):
    forma_pagamento: FormaPagamento | None = None
    cliente_id: int | None = None
    itens: list[ItemVendaCreate] = Field(min_length=1)


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
    forma_pagamento: FormaPagamento | None
    cliente_id: int | None
    paga_em: datetime | None
    cancelada_em: datetime | None
    itens: list[ItemVendaRead]
    registrado_por_id: int

    model_config = {"from_attributes": True}


class ContaRead(BaseModel):
    cliente_id: int
    total: Decimal
    vendas: list[VendaRead]

    model_config = {"from_attributes": True}


class FecharConta(BaseModel):
    forma_pagamento: FormaPagamento
