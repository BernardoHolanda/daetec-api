from datetime import datetime
from decimal import Decimal

from app.crud.venda import FUSO_MANAUS
from app.models.venda import Venda


def _venda(client, produto_id):
    resp = client.post(
        "/vendas",
        json={
            "forma_pagamento": "pix",
            "itens": [{"produto_id": produto_id, "quantidade": 1}],
        },
    )
    return resp.json()["id"]


def test_comum_cria_venda_a_vista(client_comum, usuario_comum, produto, vendedor):
    resp = client_comum.post(
        "/vendas",
        json={
            "forma_pagamento": "dinheiro",
            "itens": [{"produto_id": produto.id, "quantidade": 2}],
        },
    )
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["registrado_por_id"] == usuario_comum.id
    assert corpo["forma_pagamento"] == "dinheiro"
    assert Decimal(corpo["itens"][0]["preco_unitario"]) == Decimal("5")
    # o dono não foi enviado pelo cliente: saiu do produto
    assert corpo["itens"][0]["vendedor_id"] == vendedor.id


def test_venda_a_vista_sem_forma_pagamento_400(client_comum, produto):
    resp = client_comum.post(
        "/vendas",
        json={"itens": [{"produto_id": produto.id, "quantidade": 1}]},
    )
    assert resp.status_code == 400


def test_venda_produto_inexistente_400(client_comum):
    resp = client_comum.post(
        "/vendas",
        json={
            "forma_pagamento": "pix",
            "itens": [{"produto_id": 999, "quantidade": 1}],
        },
    )
    assert resp.status_code == 400


def test_venda_sem_itens_422(client_comum):
    resp = client_comum.post("/vendas", json={"forma_pagamento": "pix", "itens": []})
    assert resp.status_code == 422


def test_venda_fiado_fica_sem_pagamento(client_comum, produto, cliente):
    resp = client_comum.post(
        "/vendas",
        json={
            "cliente_id": cliente.id,
            "itens": [{"produto_id": produto.id, "quantidade": 1}],
        },
    )
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["cliente_id"] == cliente.id
    assert corpo["paga_em"] is None
    assert corpo["forma_pagamento"] is None


def test_minhas_traz_so_as_vendas_do_usuario(
    client_comum, db_session, usuario_admin, produto
):
    minha = _venda(client_comum, produto.id)
    da_outra = _venda(client_comum, produto.id)
    db_session.get(Venda, da_outra).registrado_por_id = usuario_admin.id
    db_session.commit()

    assert len(client_comum.get("/vendas").json()) == 2

    minhas = client_comum.get("/vendas", params={"minhas": True}).json()
    assert [v["id"] for v in minhas] == [minha]


def test_filtro_por_dia(client_comum, db_session, produto):
    antiga = _venda(client_comum, produto.id)
    db_session.get(Venda, antiga).data_hora = datetime(
        2026, 1, 5, 10, tzinfo=FUSO_MANAUS
    )
    db_session.commit()
    recente = _venda(client_comum, produto.id)

    de_janeiro = client_comum.get("/vendas", params={"dia": "2026-01-05"}).json()

    assert [v["id"] for v in de_janeiro] == [antiga]
    assert recente not in [v["id"] for v in de_janeiro]


def test_dia_usa_o_fuso_de_manaus(client_comum, db_session, produto):
    """23:30 em Manaus é 03:30 UTC do dia seguinte — não pode vazar pro outro dia."""
    venda = _venda(client_comum, produto.id)
    db_session.get(Venda, venda).data_hora = datetime(
        2026, 3, 10, 23, 30, tzinfo=FUSO_MANAUS
    )
    db_session.commit()

    assert len(client_comum.get("/vendas", params={"dia": "2026-03-10"}).json()) == 1
    assert len(client_comum.get("/vendas", params={"dia": "2026-03-11"}).json()) == 0


def test_vendas_vem_da_mais_nova_pra_mais_antiga(client_comum, db_session, produto):
    antiga = _venda(client_comum, produto.id)
    db_session.get(Venda, antiga).data_hora = datetime(
        2026, 1, 5, 10, tzinfo=FUSO_MANAUS
    )
    db_session.commit()
    recente = _venda(client_comum, produto.id)

    assert [v["id"] for v in client_comum.get("/vendas").json()] == [recente, antiga]
