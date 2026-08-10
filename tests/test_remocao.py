"""Remoção nos três cadastros.

A regra é a mesma nos três: quem barra o registro em uso é a **foreign key**
(NO ACTION), não código de aplicação — o `IntegrityError` vira 409 no handler.
"""


def _venda_fiado(client, cliente_id, produto_id):
    return client.post(
        "/vendas",
        json={
            "cliente_id": cliente_id,
            "itens": [{"produto_id": produto_id, "quantidade": 1}],
        },
    )


def test_admin_remove_produto_sem_venda(client_admin, produto):
    resp = client_admin.delete(f"/produtos/{produto.id}")
    assert resp.status_code == 204
    assert client_admin.get("/produtos").json() == []


def test_nao_remove_produto_ja_vendido(client_admin, produto, cliente):
    _venda_fiado(client_admin, cliente.id, produto.id)
    resp = client_admin.delete(f"/produtos/{produto.id}")
    assert resp.status_code == 409
    # continua na listagem: o 409 recusou, não apagou pela metade
    assert len(client_admin.get("/produtos").json()) == 1


def test_admin_remove_vendedor_sem_produto(client_admin, vendedor):
    resp = client_admin.delete(f"/vendedores/{vendedor.id}")
    assert resp.status_code == 204
    assert client_admin.get("/vendedores").json() == []


def test_nao_remove_vendedor_com_produto(client_admin, produto):
    """A fixture `produto` já cria o vendedor e amarra os dois."""
    resp = client_admin.delete(f"/vendedores/{produto.vendedor_id}")
    assert resp.status_code == 409


def test_admin_remove_cliente_sem_venda(client_admin, cliente):
    resp = client_admin.delete(f"/clientes/{cliente.id}")
    assert resp.status_code == 204
    assert client_admin.get("/clientes").json() == []


def test_nao_remove_cliente_com_venda(client_admin, produto, cliente):
    _venda_fiado(client_admin, cliente.id, produto.id)
    resp = client_admin.delete(f"/clientes/{cliente.id}")
    assert resp.status_code == 409


def test_comum_nao_remove(client_comum, produto, cliente):
    assert client_comum.delete(f"/produtos/{produto.id}").status_code == 403
    assert client_comum.delete(f"/vendedores/{produto.vendedor_id}").status_code == 403
    assert client_comum.delete(f"/clientes/{cliente.id}").status_code == 403


def test_remover_inexistente_404(client_admin):
    assert client_admin.delete("/produtos/999").status_code == 404
    assert client_admin.delete("/vendedores/999").status_code == 404
    assert client_admin.delete("/clientes/999").status_code == 404
