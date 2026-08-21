from datetime import datetime, time, timedelta
from decimal import Decimal

from app.crud.venda import FUSO_MANAUS, hoje_manaus
from app.models.venda import Venda


def _recuar(db_session, venda_id: int, dias: int):
    """Joga a venda pra `dias` atrás. Meio-dia no fuso de Manaus pra não encostar na borda."""
    venda = db_session.get(Venda, venda_id)
    quando = datetime.combine(
        hoje_manaus() - timedelta(days=dias), time(12, 0), tzinfo=FUSO_MANAUS
    )
    venda.data_hora = quando
    # fiado em aberto continua aberto: recuar no tempo não é pagar
    if venda.paga_em is not None:
        venda.paga_em = quando
    db_session.commit()


def _vender(client, produto, quantidade=2):
    resp = client.post(
        "/vendas",
        json={
            "forma_pagamento": "dinheiro",
            "itens": [{"produto_id": produto.id, "quantidade": quantidade}],
        },
    )
    return resp.json()["id"]


def test_comum_nao_ve_relatorio(client_comum):
    resp = client_comum.get("/relatorio")
    assert resp.status_code == 403


def test_relatorio_soma_venda_do_dia(client_admin, produto, vendedor):
    _vender(client_admin, produto)

    resp = client_admin.get("/relatorio")
    assert resp.status_code == 200
    vendedores = resp.json()["vendedores"]
    assert len(vendedores) == 1
    assert vendedores[0]["vendedor_id"] == vendedor.id
    assert Decimal(vendedores[0]["recebido_total"]) == Decimal("10")  # 2 × 5


def test_relatorio_sem_escopo_e_hoje(client_admin):
    corpo = client_admin.get("/relatorio").json()
    hoje = hoje_manaus().isoformat()
    assert corpo["inicio"] == hoje
    assert corpo["fim"] == hoje


def test_escopo_de_varios_dias_soma_todos(client_admin, produto, db_session):
    _recuar(db_session, _vender(client_admin, produto), dias=3)
    _vender(client_admin, produto)

    hoje = hoje_manaus()
    corpo = client_admin.get(
        "/relatorio",
        params={
            "inicio": (hoje - timedelta(days=5)).isoformat(),
            "fim": hoje.isoformat(),
        },
    ).json()

    # as duas vendas caem no mesmo vendedor, então viram uma linha só de 20
    assert Decimal(corpo["vendedores"][0]["recebido_total"]) == Decimal("20")


def test_escopo_exclui_venda_de_fora(client_admin, produto, db_session):
    _recuar(db_session, _vender(client_admin, produto), dias=10)

    hoje = hoje_manaus()
    corpo = client_admin.get(
        "/relatorio",
        params={
            "inicio": (hoje - timedelta(days=2)).isoformat(),
            "fim": hoje.isoformat(),
        },
    ).json()

    assert corpo["vendedores"] == []


def test_escopo_invertido_desinverte(client_admin, produto, db_session):
    _recuar(db_session, _vender(client_admin, produto), dias=3)

    hoje = hoje_manaus()
    # fim antes do início: sem desinverter, o BETWEEN não pegaria nada
    corpo = client_admin.get(
        "/relatorio",
        params={
            "inicio": hoje.isoformat(),
            "fim": (hoje - timedelta(days=5)).isoformat(),
        },
    ).json()

    assert corpo["inicio"] < corpo["fim"]
    assert Decimal(corpo["vendedores"][0]["recebido_total"]) == Decimal("10")


def test_uma_ponta_so_vira_dia_unico(client_admin, produto, db_session):
    _recuar(db_session, _vender(client_admin, produto), dias=3)
    _vender(client_admin, produto)

    alvo = (hoje_manaus() - timedelta(days=3)).isoformat()
    corpo = client_admin.get("/relatorio", params={"inicio": alvo}).json()

    assert corpo["fim"] == alvo
    # só a venda recuada entra: a de hoje ficou fora
    assert Decimal(corpo["vendedores"][0]["recebido_total"]) == Decimal("10")


def test_fiado_acertado_muda_de_escopo(client_admin, produto, cliente, db_session):
    """Fiado conta pelo dia da venda enquanto aberto, e pelo dia do acerto depois."""
    resp = client_admin.post(
        "/vendas",
        json={
            "cliente_id": cliente.id,
            "itens": [{"produto_id": produto.id, "quantidade": 1}],
        },
    )
    _recuar(db_session, resp.json()["id"], dias=3)

    hoje = hoje_manaus().isoformat()
    antes = (hoje_manaus() - timedelta(days=3)).isoformat()

    def no_dia(dia):
        return client_admin.get("/vendas", params={"inicio": dia, "fim": dia}).json()

    # em aberto: aparece no dia da venda
    assert len(no_dia(antes)) == 1
    assert len(no_dia(hoje)) == 0

    client_admin.post(
        f"/clientes/{cliente.id}/conta/fechar", json={"forma_pagamento": "pix"}
    )

    # acertado hoje: saiu do dia da venda e entrou no de hoje
    assert len(no_dia(antes)) == 0
    assert len(no_dia(hoje)) == 1


def test_vendas_aceitam_escopo(client_admin, produto, db_session):
    _recuar(db_session, _vender(client_admin, produto), dias=3)
    _vender(client_admin, produto)

    hoje = hoje_manaus().isoformat()
    do_dia = client_admin.get("/vendas", params={"inicio": hoje, "fim": hoje}).json()
    assert len(do_dia) == 1

    tudo = client_admin.get("/vendas").json()
    assert len(tudo) == 2
