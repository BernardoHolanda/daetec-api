from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import venda as crud_venda
from app.database import get_db
from app.schemas.venda import VendaCreate, VendaRead

router = APIRouter(prefix="/vendas", tags=["vendas"])


@router.post("", response_model=VendaRead, status_code=201)
def criar(dados: VendaCreate, db: Session = Depends(get_db)):
    try:
        return crud_venda.criar_venda(db, dados)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[VendaRead])
def listar(db: Session = Depends(get_db)):
    return crud_venda.listar_vendas(db)


@router.get("/{venda_id}", response_model=VendaRead)
def obter(venda_id: int, db: Session = Depends(get_db)):
    venda = crud_venda.obter_venda(db, venda_id)
    if venda is None:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return venda


@router.delete("/{venda_id}", response_model=VendaRead)
def cancelar(venda_id: int, db: Session = Depends(get_db)):
    venda = crud_venda.obter_venda(db, venda_id)
    if venda is None:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return crud_venda.cancelar_venda(db, venda)
