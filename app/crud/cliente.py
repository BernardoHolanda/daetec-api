from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate


def criar_cliente(db: Session, dados: ClienteCreate) -> Cliente:
    cliente = Cliente(nome=dados.nome)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def listar_clientes(db: Session) -> list[Cliente]:
    return list(db.scalars(select(Cliente)).all())


def obter_cliente(db: Session, cliente_id: int) -> Cliente | None:
    return db.get(Cliente, cliente_id)


def atualizar_cliente(db: Session, cliente: Cliente, dados: ClienteCreate) -> Cliente:
    cliente.nome = dados.nome
    db.commit()
    db.refresh(cliente)
    return cliente


def deletar_cliente(db: Session, cliente: Cliente) -> None:
    """Quem barra cliente com venda é a FK (NO ACTION): vira 409 no handler."""
    db.delete(cliente)
    db.commit()
