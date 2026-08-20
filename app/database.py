import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# mesma regra do JWT_SECRET: falta de configuração obrigatória derruba no boot
DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    # o Neon suspende quando ocioso e mata as conexões que o pool guardou
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Uma sessão por request, fechada no fim."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # sessão que falhou no flush fica inutilizável até o rollback
        db.rollback()
        raise
    finally:
        db.close()
