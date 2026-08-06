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
    venda_id: Mapped[int] = mapped_column(ForeignKey("vendas.id"))
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    vendedor_id: Mapped[int] = mapped_column(ForeignKey("vendedores.id"))
    quantidade: Mapped[int]
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    venda: Mapped["Venda"] = relationship(back_populates="itens")
    # joined: N:1, o JOIN só acrescenta colunas na mesma linha — e a resposta
    # da conta precisa dos dois nomes em todo item
    produto: Mapped["Produto"] = relationship(lazy="joined")
    vendedor: Mapped["Vendedor"] = relationship(back_populates="itens", lazy="joined")
