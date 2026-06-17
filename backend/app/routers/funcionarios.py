from fastapi import APIRouter

from .. import database as db
from ..helpers import buscar_ou_404
from ..schemas import FuncionarioIn

router = APIRouter(prefix="/api/funcionarios", tags=["funcionarios"])

COLS = "id, nome, email, cpf, telefone, endereco, datanascimento, datacadastro, status"


@router.get("")
def listar(busca: str = "", apenas_ativos: bool = False):
    where = []
    params = []
    if busca:
        where.append("(nome ILIKE %s OR CAST(cpf AS TEXT) ILIKE %s)")
        params += [f"%{busca}%", f"%{busca}%"]
    if apenas_ativos:
        where.append("status = 'Ativo'")
    sql = f"SELECT {COLS} FROM funcionario"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY nome"
    return db.fetch_all(sql, tuple(params))


@router.get("/{id_}")
def obter(id_: int):
    return buscar_ou_404("funcionario", id_, "Funcionário")


@router.post("", status_code=201)
def criar(f: FuncionarioIn):
    return db.execute(
        "INSERT INTO funcionario (nome,email,senha,cpf,telefone,endereco,datanascimento,status) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
        (f.nome, f.email, f.senha, f.cpf, f.telefone, f.endereco, f.datanascimento, f.status),
        returning=True,
    )


@router.put("/{id_}")
def atualizar(id_: int, f: FuncionarioIn):
    buscar_ou_404("funcionario", id_, "Funcionário")
    db.execute(
        "UPDATE funcionario SET nome=%s,email=%s,senha=%s,cpf=%s,telefone=%s,"
        "endereco=%s,datanascimento=%s,status=%s WHERE id=%s",
        (f.nome, f.email, f.senha, f.cpf, f.telefone, f.endereco,
         f.datanascimento, f.status, id_),
    )
    return {"ok": True}


@router.delete("/{id_}")
def excluir(id_: int):
    buscar_ou_404("funcionario", id_, "Funcionário")
    db.execute("DELETE FROM funcionario WHERE id=%s", (id_,))
    return {"ok": True}
