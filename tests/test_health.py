def test_raiz_responde(client):
    resposta = client.get("/")
    assert resposta.status_code == 200
