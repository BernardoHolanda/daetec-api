from decimal import Decimal

from fastapi import APIRouter, Depends

from app.crud import venda as crud_venda
from app.dependencies import DbSession, get_current_user
from app.schemas.venda import ContaAbertaRead, ContasAbertasRead

router = APIRouter(
    prefix="/contas", tags=["contas"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=ContasAbertasRead)
def listar(db: DbSession):
    """Um resumo por cliente devedor, da maior dívida pra menor."""
    contas = [
        ContaAbertaRead.model_validate(linha) for linha in crud_venda.contas_abertas(db)
    ]
    return ContasAbertasRead(
        total=sum((conta.total for conta in contas), Decimal("0")),
        contas=contas,
    )
