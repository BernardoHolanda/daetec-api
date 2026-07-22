from decimal import Decimal


def _venda_fiado(client, cliente_id, produto_id, vendedor_id, qtd):
    return client.post(
        "/vendas",
        json={
            "cliente_id": cliente_id,
            "itens": [
                {"produto_id": produto_id, "vendedor_id": vendedor_id, "quantidade": qtd}
            ],
        },
    )


def test_ciclo_do_fiado(client_comum, produto, vendedor, cliente):
    # 1. abre uma conta com uma venda fiado de 3 × 5 = 15
    _venda_fiado(client_comum, cliente.id, produto.id, vendedor.id, 3)

    # 2. a conta mostra o total devido
    resp = client_comum.get(f"/clientes/{cliente.id}/conta")
    assert resp.status_code == 200
    assert Decimal(resp.json()["total"]) == Decimal("15")

    # 3. fecha a conta pagando no pix
    resp = client_comum.post(
        f"/clientes/{cliente.id}/conta/fechar", json={"forma_pagamento": "pix"}
    )
    assert resp.status_code == 200

    # 4. agora a conta está zerada
    resp = client_comum.get(f"/clientes/{cliente.id}/conta")
    assert Decimal(resp.json()["total"]) == Decimal("0")


def test_fechar_conta_vazia_400(client_comum, cliente):
    resp = client_comum.post(
        f"/clientes/{cliente.id}/conta/fechar", json={"forma_pagamento": "pix"}
    )
    assert resp.status_code == 400
