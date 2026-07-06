from fastapi import APIRouter, Depends
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