def test_login_com_credenciais_validas(client, usuario_admin):
    resp = client.post(
        "/login", data={"username": "admin_teste", "password": "Senhaforte1"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_login_senha_errada(client, usuario_admin):
    resp = client.post(
        "/login", data={"username": "admin_teste", "password": "errada"}
    )
    assert resp.status_code == 401


def test_rota_protegida_sem_token(client):
    resp = client.get("/produtos")
    assert resp.status_code == 401


def test_rota_protegida_com_token(client_admin):
    resp = client_admin.get("/produtos")
    assert resp.status_code == 200
