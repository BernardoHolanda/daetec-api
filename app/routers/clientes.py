from fastapi import APIRouter, Depends, HTTPException

from app.crud import cliente as crud_cliente
from app.crud import venda as crud_venda
from app.dependencies import DbSession, exigir_admin, get_current_user
from app.schemas.cliente import ClienteCreate, ClienteRead
from app.schemas.venda import ContaRead, FecharConta

router = APIRouter(
    prefix="/clientes", tags=["clientes"], dependencies=[Depends(get_current_user)]
)


@router.post("", response_model=ClienteRead, status_code=201)
def criar(dados: ClienteCreate, db: DbSession):
    return crud_cliente.criar_cliente(db, dados)


@router.get("", response_model=list[ClienteRead])
def listar(db: DbSession):
    return crud_cliente.listar_clientes(db)


@router.get("/{cliente_id}", response_model=ClienteRead)
def obter(cliente_id: int, db: DbSession):
    cliente = crud_cliente.obter_cliente(db, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente


@router.put(
    "/{cliente_id}", response_model=ClienteRead, dependencies=[Depends(exigir_admin)]
)
def atualizar(cliente_id: int, dados: ClienteCreate, db: DbSession):
    cliente = crud_cliente.obter_cliente(db, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return crud_cliente.atualizar_cliente(db, cliente, dados)


@router.delete("/{cliente_id}", status_code=204, dependencies=[Depends(exigir_admin)])
def deletar(cliente_id: int, db: DbSession):
    cliente = crud_cliente.obter_cliente(db, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    crud_cliente.deletar_cliente(db, cliente)


@router.get("/{cliente_id}/conta", response_model=ContaRead)
def conta(cliente_id: int, db: DbSession):
    cliente = crud_cliente.obter_cliente(db, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    vendas = crud_venda.listar_conta(db, cliente_id)
    total = crud_venda.total_das_vendas(vendas)
    return ContaRead(
        cliente_id=cliente_id, nome=cliente.nome, total=total, vendas=vendas
    )


@router.post("/{cliente_id}/conta/fechar", response_model=ContaRead)
def fechar(cliente_id: int, dados: FecharConta, db: DbSession):
    cliente = crud_cliente.obter_cliente(db, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    try:
        vendas = crud_venda.fechar_conta(db, cliente_id, dados.forma_pagamento)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    total = crud_venda.total_das_vendas(vendas)
    return ContaRead(
        cliente_id=cliente_id, nome=cliente.nome, total=total, vendas=vendas
    )
