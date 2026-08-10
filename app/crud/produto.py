from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.produto import Produto
from app.models.vendedor import Vendedor
from app.schemas.produto import ProdutoCreate


def _exigir_vendedor(db: Session, vendedor_id: int) -> None:
    if db.get(Vendedor, vendedor_id) is None:
        raise ValueError(f"Vendedor {vendedor_id} não existe")


def criar_produto(db: Session, dados: ProdutoCreate) -> Produto:
    _exigir_vendedor(db, dados.vendedor_id)
    produto = Produto(
        nome=dados.nome,
        preco=dados.preco,
        vendedor_id=dados.vendedor_id,
        estoque=dados.estoque,
    )
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def listar_produtos(db: Session) -> list[Produto]:
    return list(db.scalars(select(Produto)).all())


def obter_produto(db: Session, produto_id: int) -> Produto | None:
    return db.get(Produto, produto_id)


def atualizar_produto(db: Session, produto: Produto, dados: ProdutoCreate) -> Produto:
    _exigir_vendedor(db, dados.vendedor_id)
    produto.nome = dados.nome
    produto.preco = dados.preco
    produto.vendedor_id = dados.vendedor_id
    produto.estoque = dados.estoque
    db.commit()
    db.refresh(produto)
    return produto


def deletar_produto(db: Session, produto: Produto) -> None:
    db.delete(produto)
    db.commit()
