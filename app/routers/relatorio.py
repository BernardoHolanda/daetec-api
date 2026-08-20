from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends

from app.crud import cliente as crud_cliente
from app.crud import venda as crud_venda
from app.crud import vendedor as crud_vendedor
from app.dependencies import DbSession, exigir_admin
from app.schemas.relatorio import DevedorRead, RelatorioRead, VendedorRelatorioRead

router = APIRouter(
    prefix="/relatorio", tags=["relatorio"], dependencies=[Depends(exigir_admin)]
)


@router.get("", response_model=RelatorioRead)
def relatorio(
    db: DbSession,
    inicio: date | None = None,
    fim: date | None = None,
):
    """Recebido por vendedor e forma no escopo, mais as contas em aberto.

    Sem `inicio` e `fim`, responde o dia de hoje no fuso de Manaus. O recebido conta
    por data de pagamento; a conta em aberto é saldo de agora, sem recorte de data.
    Exige admin.
    """
    inicio, fim = crud_venda.normalizar_escopo(inicio, fim)

    recebido = crud_venda.recebido_por_vendedor(db, inicio, fim)
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

    return RelatorioRead(inicio=inicio, fim=fim, vendedores=vendedores)
