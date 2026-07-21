from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import PapelUsuario


class Usuario(Base):
    __tablename__ = "usuarios"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    senha_hash: Mapped[str]
    papel: Mapped[PapelUsuario]
