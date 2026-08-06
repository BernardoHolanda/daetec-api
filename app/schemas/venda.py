from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.enums import FormaPagamento
from app.schemas.produto import ProdutoResumo
from app.schemas.vendedor import VendedorRead


class ItemVendaCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)


class VendaCreate(BaseModel):
    forma_pagamento: FormaPagamento | None = None
    cliente_id: int | None = None
    itens: list[ItemVendaCreate] = Field(min_length=1)


class ItemVendaRead(BaseModel):
    id: int
    # objeto no lugar do id: a tela precisa do nome, e o id vem junto de graça
    produto: ProdutoResumo
    vendedor: VendedorRead
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
    nome: str
    total: Decimal
    vendas: list[VendaRead]

    model_config = {"from_attributes": True}


class FecharConta(BaseModel):
    forma_pagamento: FormaPagamento


class ContaAbertaRead(BaseModel):
    cliente_id: int
    nome: str
    total: Decimal
    consumos: int
    primeiro_consumo: datetime
    ultimo_consumo: datetime

    model_config = {"from_attributes": True}


class ContasAbertasRead(BaseModel):
    total: Decimal
    contas: list[ContaAbertaRead]
