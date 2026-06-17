from fastapi import APIRouter, HTTPException

from .. import database as db
from ..helpers import garantir_existe, buscar_ou_404
from ..schemas import VendaIn

router = APIRouter(prefix="/api/vendas", tags=["vendas"])

LISTA_SQL = """
    SELECT vp.id, c.nome AS cliente, f.nome AS funcionario, vp.datavenda,
           COALESCE(SUM(iv.precototal), 0) AS total,
           COALESCE(SUM(iv.quantidade), 0) AS itens
    FROM venda_produto vp
    JOIN cliente c     ON c.id = vp.idcliente
    JOIN funcionario f ON f.id = vp.idfuncionario
    LEFT JOIN item_venda iv ON iv.idvenda = vp.id
    {where}
    GROUP BY vp.id, c.nome, f.nome, vp.datavenda
    ORDER BY vp.datavenda DESC
"""


@router.get("")
def listar(busca: str = ""):
    if busca:
        return db.fetch_all(
            LISTA_SQL.format(where="WHERE c.nome ILIKE %s OR f.nome ILIKE %s"),
            (f"%{busca}%", f"%{busca}%"),
        )
    return db.fetch_all(LISTA_SQL.format(where=""))


@router.get("/{id_}")
def obter(id_: int):
    venda = buscar_ou_404("venda_produto", id_, "Venda")
    itens = db.fetch_all(
        "SELECT iv.id, p.nome AS produto, iv.quantidade, iv.precototal, "
        "(iv.precototal / iv.quantidade) AS preco_unitario "
        "FROM item_venda iv JOIN produto p ON p.id = iv.idproduto "
        "WHERE iv.idvenda=%s",
        (id_,),
    )
    venda["itens"] = itens
    return venda


@router.post("", status_code=201)
def criar(v: VendaIn):
    garantir_existe("cliente", v.idcliente, "Cliente")
    garantir_existe("funcionario", v.idfuncionario, "Funcionário")

    # Valida produtos e estoque ANTES de gravar
    preparados = []
    for item in v.itens:
        prod = db.fetch_one(
            "SELECT id, nome, preco, estoque FROM produto WHERE id=%s",
            (item.idproduto,),
        )
        if not prod:
            raise HTTPException(400, f"Produto (ID {item.idproduto}) não existe.")
        if item.quantidade > prod["estoque"]:
            raise HTTPException(
                400,
                f"Estoque insuficiente de '{prod['nome']}' "
                f"(disponível: {prod['estoque']}).",
            )
        preparados.append((item.idproduto, item.quantidade, prod["preco"] * item.quantidade))

    with db.get_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO venda_produto (idcliente,idfuncionario) VALUES (%s,%s) RETURNING id",
            (v.idcliente, v.idfuncionario),
        )
        venda_id = cur.fetchone()["id"]
        for idproduto, qtd, total in preparados:
            # O trigger trg_baixar_estoque dá baixa no estoque automaticamente
            cur.execute(
                "INSERT INTO item_venda (idvenda,idproduto,quantidade,precototal) "
                "VALUES (%s,%s,%s,%s)",
                (venda_id, idproduto, qtd, total),
            )
    return {"id": venda_id}


@router.delete("/{id_}")
def excluir(id_: int):
    buscar_ou_404("venda_produto", id_, "Venda")
    # item_venda tem ON DELETE CASCADE; devolvemos o estoque manualmente
    with db.get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE produto p SET estoque = p.estoque + iv.quantidade "
            "FROM item_venda iv WHERE iv.idvenda=%s AND p.id = iv.idproduto",
            (id_,),
        )
        cur.execute("DELETE FROM venda_produto WHERE id=%s", (id_,))
    return {"ok": True}
