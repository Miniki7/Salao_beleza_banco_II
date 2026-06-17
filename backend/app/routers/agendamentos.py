from fastapi import APIRouter, HTTPException

from .. import database as db
from ..helpers import garantir_existe, buscar_ou_404
from ..schemas import AgendamentoIn

router = APIRouter(prefix="/api/agendamentos", tags=["agendamentos"])


@router.get("")
def listar(busca: str = ""):
    # Usa a VIEW vw_agenda_completa (cliente + funcionário + serviços agregados)
    if busca:
        return db.fetch_all(
            "SELECT * FROM vw_agenda_completa "
            "WHERE cliente ILIKE %s OR funcionario ILIKE %s",
            (f"%{busca}%", f"%{busca}%"),
        )
    return db.fetch_all("SELECT * FROM vw_agenda_completa")


@router.get("/{id_}")
def obter(id_: int):
    ag = buscar_ou_404("agendamento", id_, "Agendamento")
    servicos = db.fetch_all(
        "SELECT idservico, precototal FROM agendamento_servico WHERE idagendamento=%s",
        (id_,),
    )
    ag["servicos"] = servicos
    return ag


def _validar_refs(a: AgendamentoIn):
    garantir_existe("cliente", a.idcliente, "Cliente")
    garantir_existe("funcionario", a.idfuncionario, "Funcionário")
    for s in a.servicos:
        garantir_existe("servico", s.idservico, "Serviço")


@router.post("", status_code=201)
def criar(a: AgendamentoIn):
    _validar_refs(a)
    with db.get_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO agendamento (idcliente,idfuncionario,datahora,status,observacao) "
            "VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (a.idcliente, a.idfuncionario, a.datahora, a.status, a.observacao),
        )
        ag_id = cur.fetchone()["id"]
        for s in a.servicos:
            cur.execute(
                "INSERT INTO agendamento_servico (idagendamento,idservico,precototal) "
                "VALUES (%s,%s,%s)",
                (ag_id, s.idservico, s.precototal),
            )
    return {"id": ag_id}


@router.put("/{id_}")
def atualizar(id_: int, a: AgendamentoIn):
    buscar_ou_404("agendamento", id_, "Agendamento")
    _validar_refs(a)
    with db.get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE agendamento SET idcliente=%s,idfuncionario=%s,datahora=%s,"
            "status=%s,observacao=%s WHERE id=%s",
            (a.idcliente, a.idfuncionario, a.datahora, a.status, a.observacao, id_),
        )
        cur.execute("DELETE FROM agendamento_servico WHERE idagendamento=%s", (id_,))
        for s in a.servicos:
            cur.execute(
                "INSERT INTO agendamento_servico (idagendamento,idservico,precototal) "
                "VALUES (%s,%s,%s)",
                (id_, s.idservico, s.precototal),
            )
    return {"ok": True}


@router.delete("/{id_}")
def excluir(id_: int):
    buscar_ou_404("agendamento", id_, "Agendamento")
    try:
        db.execute("DELETE FROM agendamento WHERE id=%s", (id_,))
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir: há pagamentos vinculados a este agendamento.",
        )
    return {"ok": True}
