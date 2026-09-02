from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.security import CABECALHO_TOKEN_NOVO, JWT_ALGORITHM, JWT_SECRET


@pytest.mark.usefixtures("usuario_admin")
def test_login_com_credenciais_validas(client):
    resp = client.post(
        "/login", data={"username": "admin_teste", "password": "Senhaforte1"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.usefixtures("usuario_admin")
def test_login_senha_errada(client):
    resp = client.post("/login", data={"username": "admin_teste", "password": "errada"})
    assert resp.status_code == 401


def test_rota_protegida_sem_token(client):
    resp = client.get("/produtos")
    assert resp.status_code == 401


def test_rota_protegida_com_token(client_admin):
    resp = client_admin.get("/produtos")
    assert resp.status_code == 200


def test_token_novo_nao_vem_renovado(client_comum):
    """Token recém-emitido tem vida de sobra — renovar seria assinar à toa."""
    resp = client_comum.get("/produtos")
    assert CABECALHO_TOKEN_NOVO not in resp.headers


def test_token_na_reta_final_vem_renovado(client, usuario_comum):
    """E o substituto precisa servir de verdade, não só existir."""
    quase_vencido = jwt.encode(
        {
            "sub": usuario_comum.username,
            "papel": usuario_comum.papel,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    resp = client.get("/produtos", headers={"Authorization": f"Bearer {quase_vencido}"})
    assert resp.status_code == 200

    novo = resp.headers[CABECALHO_TOKEN_NOVO]
    seguinte = client.get("/produtos", headers={"Authorization": f"Bearer {novo}"})
    assert seguinte.status_code == 200
    # o substituto nasce inteiro: se herdasse o `exp` do antigo, a sessão morreria igual
    assert CABECALHO_TOKEN_NOVO not in seguinte.headers


def test_token_vencido_nao_renova_nada(client, usuario_comum):
    """Renovação é para quem ainda está dentro do prazo; vencido é 401, sem segunda chance."""
    vencido = jwt.encode(
        {
            "sub": usuario_comum.username,
            "papel": usuario_comum.papel,
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    resp = client.get("/produtos", headers={"Authorization": f"Bearer {vencido}"})
    assert resp.status_code == 401
    assert CABECALHO_TOKEN_NOVO not in resp.headers
