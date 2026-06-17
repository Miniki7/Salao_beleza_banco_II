from fastapi import APIRouter

from .. import database as db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def resumo():
    contagens = db.fetch_one("""
        SELECT
            (SELECT COUNT(*) FROM cliente)        AS clientes,
            (SELECT COUNT(*) FROM funcionario)    AS funcionarios,
            (SELECT COUNT(*) FROM produto)        AS produtos,
            (SELECT COUNT(*) FROM servico)        AS servicos,
            (SELECT COUNT(*) FROM agendamento)    AS agendamentos,
            (SELECT COUNT(*) FROM venda_produto)  AS vendas
    """)
    # Produtos com estoque baixo
    alertas = db.fetch_all(
        "SELECT nome, estoque, estoque_minimo FROM produto "
        "WHERE estoque <= estoque_minimo ORDER BY estoque ASC"
    )
    # Top clientes (VIEW vw_total_gasto_cliente)
    top_clientes = db.fetch_all(
        "SELECT nome, valor_total_gasto FROM vw_total_gasto_cliente "
        "WHERE valor_total_gasto > 0 LIMIT 5"
    )
    # Faturamento por funcionário (VIEW vw_resumo_vendas_funcionario)
    faturamento = db.fetch_all(
        "SELECT nome, faturamento_total_funcionario FROM vw_resumo_vendas_funcionario "
        "WHERE faturamento_total_funcionario > 0 LIMIT 5"
    )
    return {
        "contagens": contagens,
        "alertas_estoque": alertas,
        "top_clientes": top_clientes,
        "faturamento_funcionarios": faturamento,
    }
