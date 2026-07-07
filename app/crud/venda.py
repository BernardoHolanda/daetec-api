from sqlalchemy import select
from sqlalchemy.orm import Session

from datetime import datetime, timezone

from app.models.produto import Produto
from app.models.venda import Venda
from app.models.item_venda import ItemVenda
from app.schemas.venda import VendaCreate


def criar_venda(db: Session, dados: VendaCreate) -> Venda:
    venda = Venda()

    for item in dados.itens:
        produto = db.get(Produto, item.produto_id)
        if produto is None:
            raise ValueError(f"Produto {item.produto_id} não existe")

        venda.itens.append(
            ItemVenda(
                produto_id=item.produto_id,
                vendedor_id=item.vendedor_id,
                quantidade=item.quantidade,
                preco_unitario=produto.preco,
            )
        )

    db.add(venda)
    db.commit()
    db.refresh(venda)
    return venda


def listar_vendas(db: Session) -> list[Venda]:
    return list(db.scalars(select(Venda).where(Venda.cancelada_em.is_(None))).all())


def obter_venda(db: Session, venda_id: int) -> Venda | None:
    return db.get(Venda, venda_id)


def cancelar_venda(db: Session, venda: Venda) -> Venda:
    venda.cancelada_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(venda)
    return venda
