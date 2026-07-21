from decimal import Decimal

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
