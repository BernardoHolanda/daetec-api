from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
