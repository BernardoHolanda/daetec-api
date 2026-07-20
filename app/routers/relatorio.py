from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import venda as crud_venda
from app.crud import vendedor as crud_vendedor
from app.crud import cliente as crud_cliente
from app.database import get_db
from app.schemas.relatorio import RelatorioRead, VendedorRelatorioRead, DevedorRead

router = APIRouter(prefix="/relatorio", tags=["relatorio"])


@router.get("", response_model=RelatorioRead)
def relatorio(dia: date | None = None, db: Session = Depends(get_db)):
    if dia is None:
        dia = date.today()

    recebido = crud_venda.recebido_por_vendedor(db, dia)
    contas = crud_venda.contas_abertas_por_vendedor(db)

    nomes_vendedor = {v.id: v.nome for v in crud_vendedor.listar_vendedores(db)}
    nomes_cliente = {c.id: c.nome for c in crud_cliente.listar_clientes(db)}

    vendedor_ids = set(recebido) | set(contas)

    vendedores = []
    for vid in sorted(vendedor_ids):
        por_forma = recebido.get(vid, {})
        devedores_map = contas.get(vid, {})

        devedores = [
            DevedorRead(cliente_id=cid, nome=nomes_cliente[cid], valor=valor)
            for cid, valor in devedores_map.items()
        ]

        vendedores.append(
            VendedorRelatorioRead(
                vendedor_id=vid,
                nome=nomes_vendedor[vid],
                recebido_total=sum(por_forma.values(), Decimal("0")),
                recebido_por_forma=por_forma,
                conta_em_aberto=sum(devedores_map.values(), Decimal("0")),
                devedores=devedores,
            )
        )

    return RelatorioRead(data=dia, vendedores=vendedores)
