from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routers import produtos

app = FastAPI(title="DAETEC API")
app.include_router(produtos.router)

@app.get("/")
def raiz():
    return {"mensagem": "Olá mundo — DATEC API esta no ar, agora com host reload!"}

@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"db": "ok"}