from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session

from app.enums import FormaPagamento
from app.models.cliente import Cliente
from app.models.item_venda import ItemVenda
from app.models.produto import Produto
from app.models.venda import Venda
from app.schemas.venda import VendaCreate

FUSO_MANAUS = timezone(timedelta(hours=-4))


def criar_venda(db: Session, dados: VendaCreate, registrado_por_id: int) -> Venda:
    if dados.cliente_id is not None:
        cliente = db.get(Cliente, dados.cliente_id)
        if cliente is None:
            raise ValueError(f"Cliente {dados.cliente_id} não existe")
        forma_pagamento = None
        paga_em = None
    else:
        if dados.forma_pagamento is None:
            raise ValueError("Venda à vista exige forma_pagamento")
        forma_pagamento = dados.forma_pagamento
        paga_em = datetime.now(timezone.utc)

    venda = Venda(
        forma_pagamento=forma_pagamento,
        cliente_id=dados.cliente_id,
        paga_em=paga_em,
        registrado_por_id=registrado_por_id,
    )

    for item in dados.itens:
        produto = db.get(Produto, item.produto_id)
        if produto is None:
            raise ValueError(f"Produto {item.produto_id} não existe")

        # estoque None é produto não controlado — vende sem baixa nenhuma
        if produto.estoque is not None:
            if item.quantidade > produto.estoque:
                raise ValueError(f"{produto.nome}: só há {produto.estoque} em estoque")
            produto.estoque -= item.quantidade

        venda.itens.append(
            ItemVenda(
                produto_id=item.produto_id,
                # dono congelado no ato, pelo mesmo motivo do preço: se o produto
                # mudar de dono depois, a venda antiga continua creditada a quem vendeu
                vendedor_id=produto.vendedor_id,
                quantidade=item.quantidade,
                preco_unitario=produto.preco,
            )
        )

    db.add(venda)
    db.commit()
    db.refresh(venda)
    return venda


def _intervalo_do_dia(dia: date) -> tuple[datetime, datetime]:
    return (
        datetime.combine(dia, time.min, tzinfo=FUSO_MANAUS),
        datetime.combine(dia, time.max, tzinfo=FUSO_MANAUS),
    )


def listar_vendas(
    db: Session,
    registrado_por_id: int | None = None,
    dia: date | None = None,
) -> list[Venda]:
    consulta = select(Venda).where(Venda.cancelada_em.is_(None))

    if registrado_por_id is not None:
        consulta = consulta.where(Venda.registrado_por_id == registrado_por_id)

    if dia is not None:
        inicio, fim = _intervalo_do_dia(dia)
        consulta = consulta.where(Venda.data_hora.between(inicio, fim))

    return list(db.scalars(consulta.order_by(Venda.data_hora.desc())).all())


def obter_venda(db: Session, venda_id: int) -> Venda | None:
    return db.get(Venda, venda_id)


def cancelar_venda(db: Session, venda: Venda) -> Venda:
    # idempotente: cancelar de novo devolveria a mercadoria duas vezes
    if venda.cancelada_em is not None:
        return venda

    venda.cancelada_em = datetime.now(timezone.utc)

    # venda cancelada já sai de todos os totais; a mercadoria volta pra prateleira
    for item in venda.itens:
        produto = db.get(Produto, item.produto_id)
        if produto is not None and produto.estoque is not None:
            produto.estoque += item.quantidade

    db.commit()
    db.refresh(venda)
    return venda


def listar_conta(db: Session, cliente_id: int) -> list[Venda]:
    return list(
        db.scalars(
            select(Venda)
            .where(
                Venda.cliente_id == cliente_id,
                Venda.paga_em.is_(None),
                Venda.cancelada_em.is_(None),
            )
            # id como desempate: duas vendas no mesmo instante precisam de ordem estável
            .order_by(Venda.data_hora.desc(), Venda.id.desc())
        ).all()
    )


def contas_abertas(
    db: Session,
) -> list[Row[tuple[int, str, Decimal, int, datetime, datetime]]]:
    """Uma linha por cliente devedor, da maior dívida pra menor."""
    total = func.sum(ItemVenda.quantidade * ItemVenda.preco_unitario)

    return list(
        db.execute(
            select(
                Venda.cliente_id,
                Cliente.nome,
                total.label("total"),
                # consumo é item consumido: soma quantidade, não conta vendas
                func.sum(ItemVenda.quantidade).label("consumos"),
                func.min(Venda.data_hora).label("primeiro_consumo"),
                func.max(Venda.data_hora).label("ultimo_consumo"),
            )
            .join(ItemVenda, ItemVenda.venda_id == Venda.id)
            .join(Cliente, Cliente.id == Venda.cliente_id)
            .where(
                Venda.paga_em.is_(None),
                Venda.cliente_id.is_not(None),
                Venda.cancelada_em.is_(None),
            )
            .group_by(Venda.cliente_id, Cliente.nome)
            .order_by(total.desc())
        ).all()
    )


def fechar_conta(
    db: Session, cliente_id: int, forma_pagamento: FormaPagamento
) -> list[Venda]:
    vendas = listar_conta(db, cliente_id)
    if not vendas:
        raise ValueError("Cliente não tem conta em aberto")

    agora = datetime.now(timezone.utc)
    for venda in vendas:
        venda.paga_em = agora
        venda.forma_pagamento = forma_pagamento

    db.commit()
    for venda in vendas:
        db.refresh(venda)
    return vendas


def recebido_por_vendedor(
    db: Session, dia: date
) -> dict[int, dict[FormaPagamento, Decimal]]:
    inicio, fim = _intervalo_do_dia(dia)

    linhas = db.execute(
        select(
            ItemVenda.vendedor_id,
            Venda.forma_pagamento,
            func.sum(ItemVenda.quantidade * ItemVenda.preco_unitario),
        )
        .join(Venda, ItemVenda.venda_id == Venda.id)
        .where(
            Venda.paga_em >= inicio,
            Venda.paga_em <= fim,
            Venda.cancelada_em.is_(None),
        )
        .group_by(ItemVenda.vendedor_id, Venda.forma_pagamento)
    ).all()

    resultado: dict[int, dict[FormaPagamento, Decimal]] = {}
    for vendedor_id, forma, total in linhas:
        resultado.setdefault(vendedor_id, {})[forma] = total
    return resultado


def contas_abertas_por_vendedor(db: Session) -> dict[int, dict[int, Decimal]]:
    linhas = db.execute(
        select(
            ItemVenda.vendedor_id,
            Venda.cliente_id,
            func.sum(ItemVenda.quantidade * ItemVenda.preco_unitario),
        )
        .join(Venda, ItemVenda.venda_id == Venda.id)
        .where(
            Venda.paga_em.is_(None),
            Venda.cliente_id.is_not(None),
            Venda.cancelada_em.is_(None),
        )
        .group_by(ItemVenda.vendedor_id, Venda.cliente_id)
    ).all()

    resultado: dict[int, dict[int, Decimal]] = {}
    for vendedor_id, cliente_id, total in linhas:
        resultado.setdefault(vendedor_id, {})[cliente_id] = total
    return resultado


def hoje_manaus() -> date:
    """O 'hoje' no fuso de Manaus (não o do servidor, que é UTC)."""
    return datetime.now(FUSO_MANAUS).date()


def total_das_vendas(vendas: list[Venda]) -> Decimal:
    """Soma quantidade × preço de todos os itens de uma lista de vendas."""
    return sum(
        (
            item.quantidade * item.preco_unitario
            for venda in vendas
            for item in venda.itens
        ),
        Decimal("0"),
    )
