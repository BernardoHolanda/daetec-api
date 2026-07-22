from sqlalchemy import inspect


def test_schema_criado(engine):
    tabelas = inspect(engine).get_table_names()
    assert "usuarios" in tabelas
    assert "vendas" in tabelas
