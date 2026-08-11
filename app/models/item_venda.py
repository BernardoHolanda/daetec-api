from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.produto import Produto
    from app.models.venda import Venda
    from app.models.vendedor import Vendedor


class ItemVenda(Base):
    __tablename__ = "itens_venda"

    id: Mapped[int] = mapped_column(primary_key=True)
    # o selectin de Venda.itens roda "WHERE venda_id IN (...)" a cada venda carregada
    venda_id: Mapped[int] = mapped_column(ForeignKey("vendas.id"), index=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), index=True)
    vendedor_id: Mapped[int] = mapped_column(ForeignKey("vendedores.id"), index=True)
    quantidade: Mapped[int]
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    venda: Mapped["Venda"] = relationship(back_populates="itens")
    # joined: N:1, o JOIN só acrescenta colunas na mesma linha — e a resposta
    # da conta precisa dos dois nomes em todo item
    produto: Mapped["Produto"] = relationship(lazy="joined")
    vendedor: Mapped["Vendedor"] = relationship(back_populates="itens", lazy="joined")
