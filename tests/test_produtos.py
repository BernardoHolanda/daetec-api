def test_comum_nao_cria_produto(client_comum):
    resp = client_comum.post("/produtos", json={"nome": "batata", "preco": 5})
    assert resp.status_code == 403


def test_admin_cria_produto(client_admin):
    resp = client_admin.post("/produtos", json={"nome": "batata", "preco": 5})
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["nome"] == "BATATA"  # normalização em MAIÚSCULA
    assert "id" in corpo


def test_produto_criado_aparece_na_listagem(client_admin):
    client_admin.post("/produtos", json={"nome": "batata", "preco": 5})
    resp = client_admin.get("/produtos")
    assert resp.status_code == 200
    nomes = [p["nome"] for p in resp.json()]
    assert nomes == ["BATATA"]  # só um — isolamento entre testes funcionando


def test_admin_nao_cria_produto_preco_invalido(client_admin):
    resp = client_admin.post("/produtos", json={"nome": "batata", "preco": 0})
    assert resp.status_code == 422


def test_nome_duplicado_retorna_409(client_admin):
    client_admin.post("/produtos", json={"nome": "batata", "preco": 5})
    resp = client_admin.post("/produtos", json={"nome": "batata", "preco": 5})
    assert resp.status_code == 409


def test_obter_produto_inexistente_404(client_admin):
    resp = client_admin.get("/produtos/999")
    assert resp.status_code == 404


def test_comum_lista_produtos(client_comum):
    resp = client_comum.get("/produtos")
    assert resp.status_code == 200
