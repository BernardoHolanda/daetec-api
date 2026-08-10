from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.vendedor import Vendedor


class Produto(Base):
    __tablename__ = "produtos"

    # o banco é a última linha: duas vendas simultâneas do último item não passam
    __table_args__ = (
        CheckConstraint("estoque >= 0", name="produtos_estoque_nao_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    vendedor_id: Mapped[int] = mapped_column(ForeignKey("vendedores.id"))
    # NULL = estoque não controlado (vende à vontade); 0 = esgotado
    estoque: Mapped[int | None] = mapped_column(default=None)

    vendedor: Mapped["Vendedor"] = relationship(lazy="joined")
