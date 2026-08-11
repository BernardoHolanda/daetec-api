import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# mesma regra do JWT_SECRET: falta de configuração obrigatória derruba no boot
DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    # o Neon suspende quando ocioso, e o pool guarda conexões que morrem junto.
    # pre_ping testa cada uma antes de entregar e reconecta sozinho se caiu.
    pool_pre_ping=True,
    # descarta conexão parada há mais de 5 min em vez de descobrir na hora do uso
    pool_recycle=300,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # sessão que falhou no flush fica inutilizável até o rollback
        db.rollback()
        raise
    finally:
        db.close()
