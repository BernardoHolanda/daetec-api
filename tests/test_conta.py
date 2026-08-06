from decimal import Decimal


def _venda_fiado(client, cliente_id, produto_id, qtd):
    return client.post(
        "/vendas",
        json={
            "cliente_id": cliente_id,
            "itens": [{"produto_id": produto_id, "quantidade": qtd}],
        },
    )


def test_ciclo_do_fiado(client_comum, produto, cliente):
    # 1. abre uma conta com uma venda fiado de 3 × 5 = 15
    _venda_fiado(client_comum, cliente.id, produto.id, 3)

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


def test_contas_lista_devedores_do_maior_pro_menor(client_comum, produto, cliente):
    outro_id = client_comum.post("/clientes", json={"nome": "ANA"}).json()["id"]
    _venda_fiado(client_comum, cliente.id, produto.id, 3)  # 15
    _venda_fiado(client_comum, outro_id, produto.id, 1)  # 5

    corpo = client_comum.get("/contas").json()

    assert Decimal(corpo["total"]) == Decimal("20")
    assert [c["nome"] for c in corpo["contas"]] == ["MARIA", "ANA"]
    assert Decimal(corpo["contas"][0]["total"]) == Decimal("15")


def test_contas_soma_a_quantidade_dos_itens(
    client_comum, produto, outro_produto, cliente
):
    """3 + 2 numa venda e 1 em outra dão 6 consumos — não 2 vendas nem 3 linhas de item."""
    client_comum.post(
        "/vendas",
        json={
            "cliente_id": cliente.id,
            "itens": [
                {"produto_id": produto.id, "quantidade": 3},
                {"produto_id": outro_produto.id, "quantidade": 2},
            ],
        },
    )
    _venda_fiado(client_comum, cliente.id, produto.id, 1)

    conta = client_comum.get("/contas").json()["contas"][0]

    assert conta["consumos"] == 6
    assert Decimal(conta["total"]) == Decimal("26")  # 3×5 + 2×3 + 1×5
    assert conta["primeiro_consumo"] <= conta["ultimo_consumo"]


def test_contas_ignora_conta_ja_fechada(client_comum, produto, cliente):
    _venda_fiado(client_comum, cliente.id, produto.id, 2)
    client_comum.post(
        f"/clientes/{cliente.id}/conta/fechar", json={"forma_pagamento": "pix"}
    )

    corpo = client_comum.get("/contas").json()

    assert corpo["contas"] == []
    assert Decimal(corpo["total"]) == Decimal("0")


def test_conta_traz_os_nomes_que_a_tela_mostra(
    client_comum, produto, outro_produto, cliente, vendedor
):
    """A tela do detalhe não faz busca por id: nome de cliente, produto e vendedor vêm na resposta."""
    client_comum.post(
        "/vendas",
        json={
            "cliente_id": cliente.id,
            "itens": [
                {"produto_id": produto.id, "quantidade": 2},
                {"produto_id": outro_produto.id, "quantidade": 1},
            ],
        },
    )

    corpo = client_comum.get(f"/clientes/{cliente.id}/conta").json()

    assert corpo["nome"] == "MARIA"
    itens = corpo["vendas"][0]["itens"]
    assert [i["produto"]["nome"] for i in itens] == ["BATATA", "SUCO"]
    assert itens[0]["produto"]["id"] == produto.id
    assert itens[0]["vendedor"] == {"id": vendedor.id, "nome": "JOAO"}


def test_conta_vem_da_venda_mais_nova_pra_mais_antiga(client_comum, produto, cliente):
    primeira = _venda_fiado(client_comum, cliente.id, produto.id, 1).json()["id"]
    segunda = _venda_fiado(client_comum, cliente.id, produto.id, 1).json()["id"]

    corpo = client_comum.get(f"/clientes/{cliente.id}/conta").json()

    assert [v["id"] for v in corpo["vendas"]] == [segunda, primeira]
