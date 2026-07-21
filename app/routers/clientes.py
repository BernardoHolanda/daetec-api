from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from app.crud import venda as crud_venda
from app.schemas.venda import ContaRead, FecharConta
from app.crud import cliente as crud_cliente
from app.database import get_db
from app.dependencies import exigir_admin
from app.schemas.cliente import ClienteCreate, ClienteRead

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("", response_model=ClienteRead, status_code=201)
def criar(dados: ClienteCreate, db: Session = Depends(get_db)):
    return crud_cliente.criar_cliente(db, dados)


@router.get("", response_model=list[ClienteRead])
def listar(db: Session = Depends(get_db)):
    return crud_cliente.listar_clientes(db)


@router.get("/{cliente_id}", response_model=ClienteRead)
def obter(cliente_id: int, db: Session = Depends(get_db)):
    cliente = crud_cliente.obter_cliente(db, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente


@router.put("/{cliente_id}", response_model=ClienteRead, dependencies=[Depends(exigir_admin)])
def atualizar(cliente_id: int, dados: ClienteCreate, db: Session = Depends(get_db)):
    cliente = crud_cliente.obter_cliente(db, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return crud_cliente.atualizar_cliente(db, cliente, dados)


@router.get("/{cliente_id}/conta", response_model=ContaRead)
def conta(cliente_id: int, db: Session = Depends(get_db)):
    cliente = crud_cliente.obter_cliente(db, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    vendas = crud_venda.listar_conta(db, cliente_id)
    total = sum(
        (item.quantidade * item.preco_unitario for venda in vendas for item in venda.itens),
        Decimal("0"),
    )
    return ContaRead(cliente_id=cliente_id, total=total, vendas=vendas)


@router.post("/{cliente_id}/conta/fechar", response_model=ContaRead)
def fechar(cliente_id: int, dados: FecharConta, db: Session = Depends(get_db)):
    cliente = crud_cliente.obter_cliente(db, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    try:
        vendas = crud_venda.fechar_conta(db, cliente_id, dados.forma_pagamento)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    total = sum(
        (item.quantidade * item.preco_unitario for venda in vendas for item in venda.itens),
        Decimal("0"),
    )
    return ContaRead(cliente_id=cliente_id, total=total, vendas=vendas)
