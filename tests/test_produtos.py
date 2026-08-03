def test_comum_nao_cria_produto(client_comum, vendedor):
    resp = client_comum.post(
        "/produtos", json={"nome": "batata", "preco": 5, "vendedor_id": vendedor.id}
    )
    assert resp.status_code == 403


def test_admin_cria_produto(client_admin, vendedor):
    resp = client_admin.post(
        "/produtos", json={"nome": "batata", "preco": 5, "vendedor_id": vendedor.id}
    )
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["nome"] == "BATATA"  # normalização em MAIÚSCULA
    assert "id" in corpo
    assert corpo["vendedor"]["id"] == vendedor.id  # dono vem junto na leitura


def test_produto_criado_aparece_na_listagem(client_admin, vendedor):
    client_admin.post(
        "/produtos", json={"nome": "batata", "preco": 5, "vendedor_id": vendedor.id}
    )
    resp = client_admin.get("/produtos")
    assert resp.status_code == 200
    nomes = [p["nome"] for p in resp.json()]
    assert nomes == ["BATATA"]  # só um — isolamento entre testes funcionando


def test_admin_nao_cria_produto_preco_invalido(client_admin, vendedor):
    resp = client_admin.post(
        "/produtos", json={"nome": "batata", "preco": 0, "vendedor_id": vendedor.id}
    )
    assert resp.status_code == 422


def test_produto_sem_vendedor_422(client_admin):
    resp = client_admin.post("/produtos", json={"nome": "batata", "preco": 5})
    assert resp.status_code == 422


def test_produto_com_vendedor_inexistente_400(client_admin):
    resp = client_admin.post(
        "/produtos", json={"nome": "batata", "preco": 5, "vendedor_id": 999}
    )
    assert resp.status_code == 400


def test_nome_duplicado_retorna_409(client_admin, vendedor):
    corpo = {"nome": "batata", "preco": 5, "vendedor_id": vendedor.id}
    client_admin.post("/produtos", json=corpo)
    resp = client_admin.post("/produtos", json=corpo)
    assert resp.status_code == 409


def test_obter_produto_inexistente_404(client_admin):
    resp = client_admin.get("/produtos/999")
    assert resp.status_code == 404


def test_comum_lista_produtos(client_comum):
    resp = client_comum.get("/produtos")
    assert resp.status_code == 200
