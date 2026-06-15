import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Configuração de conexão – ajuste conforme seu ambiente
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "database": os.getenv("DB_NAME", "salaoBeleza"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456"),
}


def get_connection():
    """Retorna uma nova conexão com o banco de dados."""
    return psycopg2.connect(**DB_CONFIG)


def execute_query(query: str, params=None, fetch=False, fetch_one=False):
    """
    Executa uma query no banco.
    - fetch=True  → retorna todas as linhas
    - fetch_one=True → retorna somente a primeira linha
    - Caso contrário, apenas executa (INSERT/UPDATE/DELETE)
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch_one:
                result = cur.fetchone()
            elif fetch:
                result = cur.fetchall()
            else:
                result = None
            conn.commit()
            return result
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def init_database():
    """Cria as tabelas e triggers a partir do arquivo schema.sql."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()
        return True, "Banco de dados inicializado com sucesso!"
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        return False, str(e)
    finally:
        if conn:
            conn.close()


def test_connection():
    """Testa a conexão com o banco de dados."""
    try:
        conn = get_connection()
        conn.close()
        return True, "Conexão estabelecida com sucesso!"
    except psycopg2.Error as e:
        return False, str(e)
