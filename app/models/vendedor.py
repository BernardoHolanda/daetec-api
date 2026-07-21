from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.item_venda import ItemVenda


class Vendedor(Base):
    __tablename__ = "vendedores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)

    itens: Mapped[list["ItemVenda"]] = relationship(back_populates="vendedor")
