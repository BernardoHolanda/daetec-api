from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import FormaPagamento

if TYPE_CHECKING:
    from app.models.item_venda import ItemVenda


class Venda(Base):
    __tablename__ = "vendas"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_hora: Mapped[datetime] = mapped_column(server_default=func.now())

    itens: Mapped[list["ItemVenda"]] = relationship(back_populates="venda")
    forma_pagamento: Mapped[FormaPagamento | None]

    cliente_id: Mapped[int | None] = mapped_column(ForeignKey("clientes.id"))
    paga_em: Mapped[datetime | None]
    cancelada_em: Mapped[datetime | None]
