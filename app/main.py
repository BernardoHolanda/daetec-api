import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.database import engine
from app.routers import (
    auth,
    clientes,
    contas,
    produtos,
    relatorio,
    usuarios,
    vendas,
    vendedores,
)

app = FastAPI(title="DAETEC API")
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(produtos.router)
app.include_router(vendedores.router)
app.include_router(vendas.router)
app.include_router(clientes.router)
app.include_router(contas.router)
app.include_router(relatorio.router)
app.include_router(usuarios.router)
app.include_router(auth.router)


@app.get("/")
def raiz():
    return {"mensagem": "Olá mundo — DAETEC API está no ar!"}


@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"db": "ok"}


@app.exception_handler(IntegrityError)
def integrity_error_handler(request: Request, exc: IntegrityError):
    sqlstate = getattr(getattr(exc, "orig", None), "sqlstate", None)
    if sqlstate == "23503":  # foreign_key_violation
        detail = "Registro em uso por outro recurso — não é possível concluir."
    elif sqlstate == "23505":  # unique_violation
        detail = "Já existe um registro com esses dados."
    else:
        detail = "Violação de integridade dos dados."
    return JSONResponse(status_code=409, content={"detail": detail})
