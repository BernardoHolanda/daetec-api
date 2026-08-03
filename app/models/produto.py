from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.vendedor import Vendedor


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    vendedor_id: Mapped[int] = mapped_column(ForeignKey("vendedores.id"))

    vendedor: Mapped["Vendedor"] = relationship(lazy="joined")
