from fastapi import APIRouter

from .. import database as db
from ..helpers import buscar_ou_404
from ..schemas import ProdutoIn

router = APIRouter(prefix="/api/produtos", tags=["produtos"])

COLS = "id, nome, marca, observacao, preco, estoque, estoque_minimo, datahora"


@router.get("")
def listar(busca: str = "", com_estoque: bool = False):
    where = []
    params = []
    if busca:
        where.append("(nome ILIKE %s OR marca ILIKE %s)")
        params += [f"%{busca}%", f"%{busca}%"]
    if com_estoque:
        where.append("estoque > 0")
    sql = f"SELECT {COLS} FROM produto"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY nome"
    return db.fetch_all(sql, tuple(params))


@router.get("/{id_}")
def obter(id_: int):
    return buscar_ou_404("produto", id_, "Produto")


@router.post("", status_code=201)
def criar(p: ProdutoIn):
    return db.execute(
        "INSERT INTO produto (nome,marca,observacao,preco,estoque,estoque_minimo) "
        "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
        (p.nome, p.marca, p.observacao, p.preco, p.estoque, p.estoque_minimo),
        returning=True,
    )


@router.put("/{id_}")
def atualizar(id_: int, p: ProdutoIn):
    buscar_ou_404("produto", id_, "Produto")
    db.execute(
        "UPDATE produto SET nome=%s,marca=%s,observacao=%s,preco=%s,"
        "estoque=%s,estoque_minimo=%s WHERE id=%s",
        (p.nome, p.marca, p.observacao, p.preco, p.estoque, p.estoque_minimo, id_),
    )
    return {"ok": True}


@router.delete("/{id_}")
def excluir(id_: int):
    buscar_ou_404("produto", id_, "Produto")
    db.execute("DELETE FROM produto WHERE id=%s", (id_,))
    return {"ok": True}
