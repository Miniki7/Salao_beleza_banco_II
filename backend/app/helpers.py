"""Funções utilitárias compartilhadas pelas rotas."""
from fastapi import HTTPException

from . import database as db


def garantir_existe(tabela: str, id_: int, nome_amigavel: str):
    """
    Garante que um registro referenciado existe (ex.: não gerar venda de
    cliente/produto inexistente). Lança 400 com mensagem clara se não existir.
    """
    row = db.fetch_one(f"SELECT 1 FROM {tabela} WHERE id = %s", (id_,))
    if not row:
        raise HTTPException(
            status_code=400,
            detail=f"{nome_amigavel} (ID {id_}) não existe.",
        )


def buscar_ou_404(tabela: str, id_: int, nome_amigavel: str):
    row = db.fetch_one(f"SELECT * FROM {tabela} WHERE id = %s", (id_,))
    if not row:
        raise HTTPException(status_code=404, detail=f"{nome_amigavel} não encontrado.")
    return row
