from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routers import produtos, vendedores, vendas, clientes, relatorio

app = FastAPI(title="DAETEC API")
app.include_router(produtos.router)
app.include_router(vendedores.router)
app.include_router(vendas.router)
app.include_router(clientes.router)
app.include_router(relatorio.router)

@app.get("/")
def raiz():
    return {"mensagem": "Olá mundo — DATEC API esta no ar!"}

@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"db": "ok"}
