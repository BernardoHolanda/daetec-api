from decimal import Decimal


def test_comum_cria_venda_a_vista(client_comum, usuario_comum, produto, vendedor):
    resp = client_comum.post(
        "/vendas",
        json={
            "forma_pagamento": "dinheiro",
            "itens": [
                {"produto_id": produto.id, "vendedor_id": vendedor.id, "quantidade": 2}
            ],
        },
    )
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["registrado_por_id"] == usuario_comum.id
    assert corpo["forma_pagamento"] == "dinheiro"
    assert Decimal(corpo["itens"][0]["preco_unitario"]) == Decimal("5")


def test_venda_a_vista_sem_forma_pagamento_400(client_comum, produto, vendedor):
    resp = client_comum.post(
        "/vendas",
        json={
            "itens": [
                {"produto_id": produto.id, "vendedor_id": vendedor.id, "quantidade": 1}
            ]
        },
    )
    assert resp.status_code == 400


def test_venda_produto_inexistente_400(client_comum, vendedor):
    resp = client_comum.post(
        "/vendas",
        json={
            "forma_pagamento": "pix",
            "itens": [
                {"produto_id": 999, "vendedor_id": vendedor.id, "quantidade": 1}
            ],
        },
    )
    assert resp.status_code == 400


def test_venda_sem_itens_422(client_comum):
    resp = client_comum.post("/vendas", json={"forma_pagamento": "pix", "itens": []})
    assert resp.status_code == 422


def test_venda_fiado_fica_sem_pagamento(client_comum, produto, vendedor, cliente):
    resp = client_comum.post(
        "/vendas",
        json={
            "cliente_id": cliente.id,
            "itens": [
                {"produto_id": produto.id, "vendedor_id": vendedor.id, "quantidade": 1}
            ],
        },
    )
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["cliente_id"] == cliente.id
    assert corpo["paga_em"] is None
    assert corpo["forma_pagamento"] is None
