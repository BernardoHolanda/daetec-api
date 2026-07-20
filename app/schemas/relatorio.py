from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.enums import FormaPagamento


class DevedorRead(BaseModel):
    cliente_id: int
    nome: str
    valor: Decimal


class VendedorRelatorioRead(BaseModel):
    vendedor_id: int
    nome: str
    recebido_total: Decimal
    recebido_por_forma: dict[FormaPagamento, Decimal]
    conta_em_aberto: Decimal
    devedores: list[DevedorRead]


class RelatorioRead(BaseModel):
    data: date
    vendedores: list[VendedorRelatorioRead]
