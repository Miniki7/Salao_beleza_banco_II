from fastapi import APIRouter

from .. import database as db
from ..helpers import garantir_existe, buscar_ou_404
from ..schemas import PagamentoIn

router = APIRouter(prefix="/api/pagamentos", tags=["pagamentos"])

LISTA_SQL = """
    SELECT p.id, p.idagendamento, c.nome AS cliente,
           p.formapag, p.valortotal, p.observacao, p.datahora
    FROM pagamento p
    LEFT JOIN agendamento a ON a.id = p.idagendamento
    LEFT JOIN cliente c     ON c.id = a.idcliente
    {where}
    ORDER BY p.datahora DESC
"""


@router.get("")
def listar(busca: str = ""):
    if busca:
        return db.fetch_all(
            LISTA_SQL.format(where="WHERE p.formapag ILIKE %s OR c.nome ILIKE %s"),
            (f"%{busca}%", f"%{busca}%"),
        )
    return db.fetch_all(LISTA_SQL.format(where=""))


@router.get("/{id_}")
def obter(id_: int):
    return buscar_ou_404("pagamento", id_, "Pagamento")


@router.post("", status_code=201)
def criar(p: PagamentoIn):
    if p.idagendamento is not None:
        garantir_existe("agendamento", p.idagendamento, "Agendamento")
    return db.execute(
        "INSERT INTO pagamento (idagendamento,formapag,valortotal,observacao) "
        "VALUES (%s,%s,%s,%s) RETURNING id",
        (p.idagendamento, p.formapag, p.valortotal, p.observacao),
        returning=True,
    )


@router.put("/{id_}")
def atualizar(id_: int, p: PagamentoIn):
    buscar_ou_404("pagamento", id_, "Pagamento")
    if p.idagendamento is not None:
        garantir_existe("agendamento", p.idagendamento, "Agendamento")
    db.execute(
        "UPDATE pagamento SET idagendamento=%s,formapag=%s,valortotal=%s,observacao=%s "
        "WHERE id=%s",
        (p.idagendamento, p.formapag, p.valortotal, p.observacao, id_),
    )
    return {"ok": True}


@router.delete("/{id_}")
def excluir(id_: int):
    buscar_ou_404("pagamento", id_, "Pagamento")
    db.execute("DELETE FROM pagamento WHERE id=%s", (id_,))
    return {"ok": True}
