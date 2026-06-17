from fastapi import APIRouter

from .. import database as db
from ..helpers import buscar_ou_404
from ..schemas import ServicoIn

router = APIRouter(prefix="/api/servicos", tags=["servicos"])

COLS = "id, nome, descricao, preco, tempoestimado"


@router.get("")
def listar(busca: str = ""):
    if busca:
        return db.fetch_all(
            f"SELECT {COLS} FROM servico WHERE nome ILIKE %s ORDER BY nome",
            (f"%{busca}%",),
        )
    return db.fetch_all(f"SELECT {COLS} FROM servico ORDER BY nome")


@router.get("/{id_}")
def obter(id_: int):
    return buscar_ou_404("servico", id_, "Serviço")


@router.post("", status_code=201)
def criar(s: ServicoIn):
    return db.execute(
        "INSERT INTO servico (nome,descricao,preco,tempoestimado) "
        "VALUES (%s,%s,%s,%s) RETURNING id",
        (s.nome, s.descricao, s.preco, s.tempoestimado),
        returning=True,
    )


@router.put("/{id_}")
def atualizar(id_: int, s: ServicoIn):
    buscar_ou_404("servico", id_, "Serviço")
    db.execute(
        "UPDATE servico SET nome=%s,descricao=%s,preco=%s,tempoestimado=%s WHERE id=%s",
        (s.nome, s.descricao, s.preco, s.tempoestimado, id_),
    )
    return {"ok": True}


@router.delete("/{id_}")
def excluir(id_: int):
    buscar_ou_404("servico", id_, "Serviço")
    db.execute("DELETE FROM servico WHERE id=%s", (id_,))
    return {"ok": True}
