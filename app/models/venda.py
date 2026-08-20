from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import FormaPagamento

if TYPE_CHECKING:
    from app.models.item_venda import ItemVenda


class Venda(Base):
    __tablename__ = "vendas"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # selectin, não joined: coleção com joined multiplica as linhas da venda.
    # order_by porque sem ele o banco devolve na ordem que quiser, e a tela lista item a item
    itens: Mapped[list["ItemVenda"]] = relationship(
        back_populates="venda", lazy="selectin", order_by="ItemVenda.id"
    )
    forma_pagamento: Mapped[FormaPagamento | None]

    # index: a conta do cliente filtra por aqui, e apagar cliente checa esta coluna
    cliente_id: Mapped[int | None] = mapped_column(
        ForeignKey("clientes.id"), index=True
    )
    paga_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    registrado_por_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), index=True
    )
