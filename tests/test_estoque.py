"""Baixa de estoque na venda.

Regra central: `estoque = None` é produto **não controlado** (vende à vontade);
`estoque = 0` é **esgotado**. Confundir os dois quebraria todo produto antigo.
"""

from decimal import Decimal

import pytest

from app.models.produto import Produto


@pytest.fixture
def produto_com_estoque(db_session, vendedor):
    p = Produto(
        nome="COXINHA", preco=Decimal("8.00"), vendedor_id=vendedor.id, estoque=3
    )
    db_session.add(p)
    db_session.commit()
    return p


def _vender(client, produto_id, qtd):
    return client.post(
        "/vendas",
        json={
            "forma_pagamento": "pix",
            "itens": [{"produto_id": produto_id, "quantidade": qtd}],
        },
    )


def test_venda_baixa_o_estoque(client_comum, client_admin, produto_com_estoque):
    assert _vender(client_comum, produto_com_estoque.id, 2).status_code == 201

    corpo = client_admin.get(f"/produtos/{produto_com_estoque.id}").json()
    assert corpo["estoque"] == 1


def test_nao_vende_mais_do_que_tem(client_comum, client_admin, produto_com_estoque):
    resp = _vender(client_comum, produto_com_estoque.id, 4)
    assert resp.status_code == 400
    assert "3 em estoque" in resp.json()["detail"]

    # recusou inteiro: nada de baixa parcial
    corpo = client_admin.get(f"/produtos/{produto_com_estoque.id}").json()
    assert corpo["estoque"] == 3


def test_vender_o_ultimo_zera_e_depois_trava(
    client_comum, client_admin, produto_com_estoque
):
    assert _vender(client_comum, produto_com_estoque.id, 3).status_code == 201
    assert (
        client_admin.get(f"/produtos/{produto_com_estoque.id}").json()["estoque"] == 0
    )
    # 0 é esgotado, não "não controlado"
    assert _vender(client_comum, produto_com_estoque.id, 1).status_code == 400


def test_produto_sem_estoque_informado_vende_a_vontade(
    client_comum, client_admin, produto
):
    """A fixture `produto` não informa estoque — é o caso dos cadastros antigos."""
    assert _vender(client_comum, produto.id, 999).status_code == 201
    assert client_admin.get(f"/produtos/{produto.id}").json()["estoque"] is None


def test_cancelar_devolve_ao_estoque(client_admin, produto_com_estoque):
    venda_id = _vender(client_admin, produto_com_estoque.id, 2).json()["id"]
    assert (
        client_admin.get(f"/produtos/{produto_com_estoque.id}").json()["estoque"] == 1
    )

    assert client_admin.delete(f"/vendas/{venda_id}").status_code == 200
    assert (
        client_admin.get(f"/produtos/{produto_com_estoque.id}").json()["estoque"] == 3
    )


def test_cancelar_duas_vezes_nao_devolve_em_dobro(client_admin, produto_com_estoque):
    venda_id = _vender(client_admin, produto_com_estoque.id, 2).json()["id"]
    client_admin.delete(f"/vendas/{venda_id}")
    client_admin.delete(f"/vendas/{venda_id}")

    corpo = client_admin.get(f"/produtos/{produto_com_estoque.id}").json()
    assert corpo["estoque"] == 3  # e não 5


def test_criar_produto_sem_estoque_e_opcional(client_admin, vendedor):
    resp = client_admin.post(
        "/produtos", json={"nome": "agua", "preco": 3, "vendedor_id": vendedor.id}
    )
    assert resp.status_code == 201
    assert resp.json()["estoque"] is None


def test_criar_produto_com_estoque_pela_api(client_admin, vendedor):
    """A fixture monta o Produto direto no banco; este passa pelo crud — que era onde faltava."""
    resp = client_admin.post(
        "/produtos",
        json={"nome": "agua", "preco": 3, "vendedor_id": vendedor.id, "estoque": 5},
    )
    assert resp.status_code == 201
    assert resp.json()["estoque"] == 5
    assert client_admin.get(f"/produtos/{resp.json()['id']}").json()["estoque"] == 5


def test_editar_produto_ajusta_o_estoque(client_admin, produto, vendedor):
    resp = client_admin.put(
        f"/produtos/{produto.id}",
        json={
            "nome": produto.nome,
            "preco": 5,
            "vendedor_id": vendedor.id,
            "estoque": 7,
        },
    )
    assert resp.status_code == 200
    assert client_admin.get(f"/produtos/{produto.id}").json()["estoque"] == 7


def test_estoque_negativo_recusado_na_entrada(client_admin, vendedor):
    resp = client_admin.post(
        "/produtos",
        json={"nome": "agua", "preco": 3, "vendedor_id": vendedor.id, "estoque": -1},
    )
    assert resp.status_code == 422


def test_venda_cancelada_some_da_lista_mas_volta_com_o_parametro(
    client_admin, produto, cliente
):
    venda_id = client_admin.post(
        "/vendas",
        json={
            "cliente_id": cliente.id,
            "itens": [{"produto_id": produto.id, "quantidade": 1}],
        },
    ).json()["id"]
    client_admin.delete(f"/vendas/{venda_id}")

    assert client_admin.get("/vendas").json() == []

    canceladas = client_admin.get("/vendas?incluir_canceladas=true").json()
    assert [v["id"] for v in canceladas] == [venda_id]
    assert canceladas[0]["cancelada_em"] is not None
