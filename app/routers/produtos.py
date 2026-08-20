from fastapi import APIRouter, Depends, HTTPException

from app.crud import produto as crud_produto
from app.dependencies import DbSession, exigir_admin, get_current_user
from app.schemas.produto import ProdutoCreate, ProdutoRead

router = APIRouter(
    prefix="/produtos", tags=["produtos"], dependencies=[Depends(get_current_user)]
)


@router.post(
    "",
    response_model=ProdutoRead,
    status_code=201,
    dependencies=[Depends(exigir_admin)],
)
def criar(dados: ProdutoCreate, db: DbSession):
    """Cadastra um produto. Exige admin."""
    try:
        return crud_produto.criar_produto(db, dados)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[ProdutoRead])
def listar(db: DbSession):
    """Todos os produtos, com dono e estoque."""
    return crud_produto.listar_produtos(db)


@router.get("/{produto_id}", response_model=ProdutoRead)
def obter(produto_id: int, db: DbSession):
    """Um produto pelo id."""
    produto = crud_produto.obter_produto(db, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.put(
    "/{produto_id}", response_model=ProdutoRead, dependencies=[Depends(exigir_admin)]
)
def atualizar(produto_id: int, dados: ProdutoCreate, db: DbSession):
    """Substitui os dados do produto. Exige admin."""
    produto = crud_produto.obter_produto(db, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    try:
        return crud_produto.atualizar_produto(db, produto, dados)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{produto_id}", status_code=204, dependencies=[Depends(exigir_admin)])
def deletar(produto_id: int, db: DbSession):
    """Remove o produto. Recusa com 409 se ele já foi vendido."""
    produto = crud_produto.obter_produto(db, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    crud_produto.deletar_produto(db, produto)
