from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vendedor import Vendedor
from app.schemas.vendedor import VendedorCreate


def criar_vendedor(db: Session, dados: VendedorCreate) -> Vendedor:
    vendedor = Vendedor(nome=dados.nome)
    db.add(vendedor)
    db.commit()
    db.refresh(vendedor)
    return vendedor


def listar_vendedores(db: Session) -> list[Vendedor]:
    return list(db.scalars(select(Vendedor)).all())


def obter_vendedor(db: Session, vendedor_id: int) -> Vendedor | None:
    return db.get(Vendedor, vendedor_id)


def atualizar_vendedor(
    db: Session, vendedor: Vendedor, dados: VendedorCreate
) -> Vendedor:
    vendedor.nome = dados.nome
    db.commit()
    db.refresh(vendedor)
    return vendedor
