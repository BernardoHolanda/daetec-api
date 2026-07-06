from fastapi import FastAPI
from sqlalchemy import text

from database import engine

app = FastAPI(title="DAETEC API")

@app.get("/")
def raiz():
    return {"mensagem": "Olá mundo — DATEC API esta no ar, agora com hot reload!"}

@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"db": "ok"}