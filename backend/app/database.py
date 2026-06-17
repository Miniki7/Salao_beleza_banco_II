"""
Camada de acesso ao banco de dados (PostgreSQL via psycopg2).

Lê as credenciais de variáveis de ambiente / arquivo .env e expõe
funções utilitárias para executar queries com segurança (parâmetros
sempre escapados, evitando SQL injection).
"""
import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carrega o .env que fica na pasta backend/
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "salaoBeleza"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456"),
}


def get_connection():
    """Abre uma nova conexão com o banco."""
    return psycopg2.connect(**DB_CONFIG)


@contextmanager
def get_cursor(commit: bool = False):
    """
    Context manager que entrega um cursor (RealDictCursor → linhas viram dict).
    Faz commit/rollback e fecha a conexão automaticamente.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_all(sql: str, params=None):
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def fetch_one(sql: str, params=None):
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def execute(sql: str, params=None, returning: bool = False):
    """Executa INSERT/UPDATE/DELETE. Se returning=True, retorna a 1ª linha."""
    with get_cursor(commit=True) as cur:
        cur.execute(sql, params)
        if returning:
            return cur.fetchone()
        return None


def test_connection():
    try:
        conn = get_connection()
        conn.close()
        return True, "Conexão estabelecida com sucesso!"
    except psycopg2.Error as e:
        return False, str(e)
