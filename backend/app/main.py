"""
API do Sistema de Gestão de Clínica Estética (FastAPI + PostgreSQL).

Sobe a API REST (/api/...) e serve o frontend estático (HTML/CSS/JS).
Execute a partir da pasta backend/:

    uvicorn app.main:app --reload
"""
import os

import psycopg2
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import database as db
from .routers import (
    clientes, funcionarios, produtos, servicos,
    agendamentos, vendas, pagamentos, dashboard,
)

app = FastAPI(title="Clínica Estética – API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Rotas da API ───────────────────────────────────────────────
for r in (clientes, funcionarios, produtos, servicos,
          agendamentos, vendas, pagamentos, dashboard):
    app.include_router(r.router)


@app.get("/api/health")
def health():
    ok, msg = db.test_connection()
    return {"banco_ok": ok, "mensagem": msg}


# ─── Tratamento de erros (mensagens amigáveis em PT-BR) ─────────
@app.exception_handler(RequestValidationError)
async def validacao_handler(request: Request, exc: RequestValidationError):
    erros = []
    for e in exc.errors():
        campo = e.get("loc", ["?"])[-1]
        msg = e.get("msg", "valor inválido")
        msg = msg.replace("Value error, ", "")
        erros.append(f"{campo}: {msg}")
    return JSONResponse(status_code=422, content={"detail": " | ".join(erros)})


@app.exception_handler(psycopg2.Error)
async def db_handler(request: Request, exc: psycopg2.Error):
    mensagem = "Erro no banco de dados."
    if isinstance(exc, psycopg2.errors.UniqueViolation):
        mensagem = "Registro duplicado (ex.: CPF já cadastrado)."
    elif isinstance(exc, psycopg2.errors.ForeignKeyViolation):
        mensagem = "Operação inválida: existe um registro relacionado (em uso) ou a referência não existe."
    elif isinstance(exc, psycopg2.errors.CheckViolation):
        mensagem = "Dados inválidos: violam uma regra do banco (valor negativo/zero ou vazio)."
    elif isinstance(exc, psycopg2.OperationalError):
        mensagem = "Não foi possível conectar ao banco. Verifique o arquivo backend/.env."
    return JSONResponse(status_code=400, content={"detail": mensagem})


# ─── Frontend estático ──────────────────────────────────────────
FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend"
)
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
