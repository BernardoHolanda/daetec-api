from decimal import Decimal


def test_comum_nao_ve_relatorio(client_comum):
    resp = client_comum.get("/relatorio")
    assert resp.status_code == 403


def test_relatorio_soma_venda_do_dia(client_admin, produto, vendedor):
    client_admin.post(
        "/vendas",
        json={
            "forma_pagamento": "dinheiro",
            "itens": [{"produto_id": produto.id, "quantidade": 2}],
        },
    )
    resp = client_admin.get("/relatorio")
    assert resp.status_code == 200
    vendedores = resp.json()["vendedores"]
    assert len(vendedores) == 1
    assert vendedores[0]["vendedor_id"] == vendedor.id
    assert Decimal(vendedores[0]["recebido_total"]) == Decimal("10")  # 2 × 5
