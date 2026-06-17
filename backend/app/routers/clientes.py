from fastapi import APIRouter

from .. import database as db
from ..helpers import buscar_ou_404
from ..schemas import ClienteIn

router = APIRouter(prefix="/api/clientes", tags=["clientes"])

COLS = "id, nome, email, cpf, telefone, endereco, datanascimento, datacadastro"


@router.get("")
def listar(busca: str = ""):
    if busca:
        return db.fetch_all(
            f"SELECT {COLS} FROM cliente "
            "WHERE nome ILIKE %s OR CAST(cpf AS TEXT) ILIKE %s "
            "ORDER BY nome",
            (f"%{busca}%", f"%{busca}%"),
        )
    return db.fetch_all(f"SELECT {COLS} FROM cliente ORDER BY nome")


@router.get("/{id_}")
def obter(id_: int):
    return buscar_ou_404("cliente", id_, "Cliente")


@router.post("", status_code=201)
def criar(c: ClienteIn):
    return db.execute(
        "INSERT INTO cliente (nome,email,senha,cpf,telefone,endereco,datanascimento) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
        (c.nome, c.email, c.senha, c.cpf, c.telefone, c.endereco, c.datanascimento),
        returning=True,
    )


@router.put("/{id_}")
def atualizar(id_: int, c: ClienteIn):
    buscar_ou_404("cliente", id_, "Cliente")
    db.execute(
        "UPDATE cliente SET nome=%s,email=%s,senha=%s,cpf=%s,telefone=%s,"
        "endereco=%s,datanascimento=%s WHERE id=%s",
        (c.nome, c.email, c.senha, c.cpf, c.telefone, c.endereco, c.datanascimento, id_),
    )
    return {"ok": True}


@router.delete("/{id_}")
def excluir(id_: int):
    buscar_ou_404("cliente", id_, "Cliente")
    db.execute("DELETE FROM cliente WHERE id=%s", (id_,))
    return {"ok": True}
