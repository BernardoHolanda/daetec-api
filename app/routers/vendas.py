from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from app.crud import venda as crud_venda
from app.dependencies import DbSession, UsuarioLogado, exigir_admin, get_current_user
from app.schemas.venda import VendaCreate, VendaRead

router = APIRouter(
    prefix="/vendas", tags=["vendas"], dependencies=[Depends(get_current_user)]
)


@router.post("", response_model=VendaRead, status_code=201)
def criar(dados: VendaCreate, db: DbSession, usuario: UsuarioLogado):
    """Registra uma venda. Com `cliente_id` ela nasce fiada; sem ele, já paga."""
    try:
        return crud_venda.criar_venda(db, dados, registrado_por_id=usuario.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[VendaRead])
def listar(
    db: DbSession,
    usuario: UsuarioLogado,
    minhas: bool = False,
    inicio: date | None = None,
    fim: date | None = None,
    incluir_canceladas: bool = False,
):
    """Vendas por data de registro. Sem escopo, devolve todas."""
    return crud_venda.listar_vendas(
        db,
        registrado_por_id=usuario.id if minhas else None,
        inicio=inicio,
        fim=fim,
        incluir_canceladas=incluir_canceladas,
    )


@router.get("/{venda_id}", response_model=VendaRead)
def obter(venda_id: int, db: DbSession):
    """Uma venda pelo id."""
    venda = crud_venda.obter_venda(db, venda_id)
    if venda is None:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return venda


@router.delete(
    "/{venda_id}", response_model=VendaRead, dependencies=[Depends(exigir_admin)]
)
def cancelar(venda_id: int, db: DbSession):
    """Cancela a venda e devolve a mercadoria ao estoque. Exige admin."""
    venda = crud_venda.obter_venda(db, venda_id)
    if venda is None:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return crud_venda.cancelar_venda(db, venda)
