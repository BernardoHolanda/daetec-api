from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate


def criar_produto(db: Session, dados: ProdutoCreate) -> Produto:
    produto = Produto(nome=dados.nome, preco=dados.preco)
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def listar_produtos(db: Session) -> list[Produto]:
    return list(db.scalars(select(Produto)).all())


def obter_produto(db: Session, produto_id: int) -> Produto | None:
    return db.get(Produto, produto_id)


def atualizar_produto(db: Session, produto: Produto, dados: ProdutoCreate) -> Produto:
    produto.nome = dados.nome
    produto.preco = dados.preco
    db.commit()
    db.refresh(produto)
    return produto


def deletar_produto(db: Session, produto: Produto) -> None:
    db.delete(produto)
    db.commit()
