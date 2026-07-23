from sqlalchemy import func, select
from sqlalchemy.orm import Session

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal


FUSO_MANAUS = timezone(timedelta(hours=-4))

from app.models.produto import Produto
from app.models.venda import Venda
from app.models.item_venda import ItemVenda
from app.models.cliente import Cliente
from app.models.vendedor import Vendedor
from app.schemas.venda import VendaCreate
from app.enums import FormaPagamento


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
        vendedor = db.get(Vendedor, item.vendedor_id)
        if vendedor is None:
            raise ValueError(f"Vendedor {item.vendedor_id} não existe")
        if produto is None:
            raise ValueError(f"Produto {item.produto_id} não existe")

        venda.itens.append(
            ItemVenda(
                produto_id = item.produto_id,
                vendedor_id = item.vendedor_id,
                quantidade = item.quantidade,
                preco_unitario = produto.preco,
            )
        )

    db.add(venda)
    db.commit()
    db.refresh(venda)
    return venda


def listar_vendas(db: Session) -> list[Venda]:
    return list(db.scalars(select(Venda).where(Venda.cancelada_em.is_(None))).all())


def obter_venda(db: Session, venda_id: int) -> Venda | None:
    return db.get(Venda, venda_id)


def cancelar_venda(db: Session, venda: Venda) -> Venda:
    venda.cancelada_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(venda)
    return venda


def listar_conta(db: Session, cliente_id: int) -> list[Venda]:
    return list(
        db.scalars(
            select(Venda).where(
                Venda.cliente_id == cliente_id,
                Venda.paga_em.is_(None),
                Venda.cancelada_em.is_(None),
            )
        ).all()
    )


def fechar_conta(db: Session, cliente_id: int, forma_pagamento: FormaPagamento) -> list[Venda]:
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


def recebido_por_vendedor(db: Session, dia: date) -> dict[int, dict[FormaPagamento, Decimal]]:
    inicio = datetime.combine(dia, time.min, tzinfo=FUSO_MANAUS)
    fim = datetime.combine(dia, time.max, tzinfo=FUSO_MANAUS)

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
        (item.quantidade * item.preco_unitario for venda in vendas for item in venda.itens),
        Decimal("0"),
    )
