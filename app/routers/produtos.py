from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import produto as crud_produto
from app.database import get_db
from app.dependencies import exigir_admin, get_current_user
from app.schemas.produto import ProdutoCreate, ProdutoRead

router = APIRouter(prefix="/produtos", tags=["produtos"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=ProdutoRead, status_code=201, dependencies=[Depends(exigir_admin)])
def criar(dados: ProdutoCreate, db: Session = Depends(get_db)):
    return crud_produto.criar_produto(db, dados)


@router.get("", response_model=list[ProdutoRead])
def listar(db: Session = Depends(get_db)):
    return crud_produto.listar_produtos(db)


@router.get("/{produto_id}", response_model=ProdutoRead)
def obter(produto_id: int, db: Session = Depends(get_db)):
    produto = crud_produto.obter_produto(db, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.put("/{produto_id}", response_model=ProdutoRead, dependencies=[Depends(exigir_admin)])
def atualizar(produto_id: int, dados: ProdutoCreate, db: Session = Depends(get_db)):
    produto = crud_produto.obter_produto(db, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return crud_produto.atualizar_produto(db, produto, dados)


@router.delete("/{produto_id}", status_code=204, dependencies=[Depends(exigir_admin)])
def deletar(produto_id: int, db: Session = Depends(get_db)):
    produto = crud_produto.obter_produto(db, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    crud_produto.deletar_produto(db, produto)
