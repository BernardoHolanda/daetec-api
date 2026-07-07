from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import vendedor as crud_vendedor
from app.database import get_db
from app.schemas.vendedor import VendedorCreate, VendedorRead

router = APIRouter(prefix="/vendedores", tags=["vendedores"])


@router.post("", response_model=VendedorRead, status_code=201)
def criar(dados: VendedorCreate, db: Session = Depends(get_db)):
    return crud_vendedor.criar_vendedor(db, dados)


@router.get("", response_model=list[VendedorRead])
def listar(db: Session = Depends(get_db)):
    return crud_vendedor.listar_vendedores(db)


@router.get("/{vendedor_id}", response_model=VendedorRead)
def obter(vendedor_id: int, db: Session = Depends(get_db)):
    vendedor = crud_vendedor.obter_vendedor(db, vendedor_id)
    if vendedor is None:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado")
    return vendedor


@router.put("/{vendedor_id}", response_model=VendedorRead)
def atualizar(vendedor_id: int, dados: VendedorCreate, db: Session = Depends(get_db)):
    vendedor = crud_vendedor.obter_vendedor(db, vendedor_id)
    if vendedor is None:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado")
    return crud_vendedor.atualizar_vendedor(db, vendedor, dados)
