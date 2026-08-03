import os
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app import models  # noqa: F401 — registra todos os models no Base.metadata
from app.database import Base, get_db
from app.enums import PapelUsuario
from app.main import app
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.models.vendedor import Vendedor
from app.security import hash_senha

DATABASE_URL = os.getenv("DATABASE_URL")
# mesma conexão, trocando só o nome do banco no fim: daetec -> daetec_test
TEST_DATABASE_URL = DATABASE_URL.rsplit("/", 1)[0] + "/daetec_test"


@pytest.fixture(scope="session")
def engine():
    # CREATE DATABASE não roda em transação: conexão em AUTOCOMMIT.
    # Conecta no banco de dev só pra criar o de teste, se ainda não existir.
    admin = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        existe = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'daetec_test'")
        ).scalar()
        if not existe:
            conn.execute(text("CREATE DATABASE daetec_test"))
    admin.dispose()

    eng = create_engine(TEST_DATABASE_URL)
    # drop antes de create: o banco de teste sobrevive entre execuções e
    # create_all NÃO altera tabela existente. Sem isso, model com coluna nova
    # roda contra schema velho e quebra com "column does not exist".
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine):
    """Cada teste roda numa transação desfeita no fim: banco sempre limpo."""
    conexao = engine.connect()
    transacao = conexao.begin()
    # create_savepoint: commit() da app vira SAVEPOINT, não commit real —
    # então o rollback abaixo desfaz tudo, inclusive o "commitado".
    sessao = Session(bind=conexao, join_transaction_mode="create_savepoint")
    yield sessao
    sessao.close()
    transacao.rollback()
    conexao.close()


@pytest.fixture
def client(db_session):
    """TestClient com o get_db trocado pelal)."""

    def get_db_de_teste():
        yield db_session

    app.dependency_overrides[get_db] = get_db_de_teste
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def usuario_admin(db_session):
    usuario = Usuario(
        username="admin_teste",
        email="admin_teste@daetec.com",
        senha_hash=hash_senha("Senhaforte1"),
        papel=PapelUsuario.ADMIN,
    )
    db_session.add(usuario)
    db_session.commit()
    return usuario


@pytest.fixture
def usuario_comum(db_session):
    usuario = Usuario(
        username="comum_teste",
        email="comum_teste@daetec.com",
        senha_hash=hash_senha("Senhaforte1"),
        papel=PapelUsuario.COMUM,
    )
    db_session.add(usuario)
    db_session.commit()
    return usuario


def _login(client, username):
    resp = client.post("/login", data={"username": username, "password": "Senhaforte1"})
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
def client_admin(client, usuario_admin):
    return _login(client, "admin_teste")


@pytest.fixture
def client_comum(client, usuario_comum):
    return _login(client, "comum_teste")


@pytest.fixture
def vendedor(db_session):
    v = Vendedor(nome="JOAO")
    db_session.add(v)
    db_session.commit()
    return v


@pytest.fixture
def produto(db_session, vendedor):
    """Todo produto tem dono — por isso depende do vendedor."""
    p = Produto(nome="BATATA", preco=Decimal("5.00"), vendedor_id=vendedor.id)
    db_session.add(p)
    db_session.commit()
    return p


@pytest.fixture
def cliente(db_session):
    c = Cliente(nome="MARIA")
    db_session.add(c)
    db_session.commit()
    return c
