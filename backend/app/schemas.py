"""
Schemas (Pydantic v2) com as validações de entrada da API.

Garantem as "melhorias" pedidas no trabalho:
  * não gravar informações vazias (nome, marca, etc.)
  * não permitir preço/quantidade/estoque zero ou negativo
  * domínios de status válidos
As validações de existência de FK (cliente/produto que não existem) são
feitas nas rotas, consultando o banco.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, field_validator

STATUS_FUNCIONARIO = ["Ativo", "Inativo"]
STATUS_AGENDAMENTO = ["Agendado", "Confirmado", "Concluído", "Cancelado"]
FORMAS_PAGAMENTO = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito",
                    "Pix", "Transferência", "Outro"]


def _nao_vazio(v: str, campo: str) -> str:
    if v is None or str(v).strip() == "":
        raise ValueError(f"O campo '{campo}' é obrigatório e não pode ficar vazio.")
    return str(v).strip()


# ─────────────────────────── Cliente ───────────────────────────
class ClienteBase(BaseModel):
    nome: str
    email: Optional[str] = None
    senha: str
    cpf: Optional[int] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    datanascimento: Optional[date] = None

    @field_validator("nome")
    @classmethod
    def _v_nome(cls, v): return _nao_vazio(v, "Nome")

    @field_validator("senha")
    @classmethod
    def _v_senha(cls, v): return _nao_vazio(v, "Senha")

    @field_validator("cpf")
    @classmethod
    def _v_cpf(cls, v):
        if v is None:
            return v
        if v <= 0 or len(str(v)) > 11:
            raise ValueError("CPF inválido (informe apenas os 11 dígitos).")
        return v


class ClienteIn(ClienteBase):
    pass


# ─────────────────────────── Funcionário ───────────────────────────
class FuncionarioIn(BaseModel):
    nome: str
    email: Optional[str] = None
    senha: str
    cpf: Optional[int] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    datanascimento: Optional[date] = None
    status: str = "Ativo"

    @field_validator("nome")
    @classmethod
    def _v_nome(cls, v): return _nao_vazio(v, "Nome")

    @field_validator("senha")
    @classmethod
    def _v_senha(cls, v): return _nao_vazio(v, "Senha")

    @field_validator("status")
    @classmethod
    def _v_status(cls, v):
        if v not in STATUS_FUNCIONARIO:
            raise ValueError(f"Status deve ser um de: {', '.join(STATUS_FUNCIONARIO)}.")
        return v

    @field_validator("cpf")
    @classmethod
    def _v_cpf(cls, v):
        if v is None:
            return v
        if v <= 0 or len(str(v)) > 11:
            raise ValueError("CPF inválido (informe apenas os 11 dígitos).")
        return v


# ─────────────────────────── Produto ───────────────────────────
class ProdutoIn(BaseModel):
    nome: str
    marca: Optional[str] = None
    observacao: Optional[str] = None
    preco: Decimal
    estoque: int = 0
    estoque_minimo: int = 10

    @field_validator("nome")
    @classmethod
    def _v_nome(cls, v): return _nao_vazio(v, "Nome")

    @field_validator("preco")
    @classmethod
    def _v_preco(cls, v):
        if v is None or v <= 0:
            raise ValueError("O preço deve ser maior que zero.")
        return v

    @field_validator("estoque", "estoque_minimo")
    @classmethod
    def _v_estoque(cls, v):
        if v is None or v < 0:
            raise ValueError("Estoque não pode ser negativo.")
        return v


# ─────────────────────────── Serviço ───────────────────────────
class ServicoIn(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: Decimal
    tempoestimado: Optional[int] = None

    @field_validator("nome")
    @classmethod
    def _v_nome(cls, v): return _nao_vazio(v, "Nome")

    @field_validator("preco")
    @classmethod
    def _v_preco(cls, v):
        if v is None or v <= 0:
            raise ValueError("O preço deve ser maior que zero.")
        return v

    @field_validator("tempoestimado")
    @classmethod
    def _v_tempo(cls, v):
        if v is not None and v <= 0:
            raise ValueError("O tempo estimado deve ser maior que zero.")
        return v


# ─────────────────────────── Agendamento ───────────────────────────
class ServicoDoAgendamento(BaseModel):
    idservico: int
    precototal: Decimal

    @field_validator("precototal")
    @classmethod
    def _v_preco(cls, v):
        if v is None or v <= 0:
            raise ValueError("O preço do serviço deve ser maior que zero.")
        return v


class AgendamentoIn(BaseModel):
    idcliente: int
    idfuncionario: int
    datahora: datetime
    status: str = "Agendado"
    observacao: Optional[str] = None
    servicos: List[ServicoDoAgendamento]

    @field_validator("status")
    @classmethod
    def _v_status(cls, v):
        if v not in STATUS_AGENDAMENTO:
            raise ValueError(f"Status deve ser um de: {', '.join(STATUS_AGENDAMENTO)}.")
        return v

    @field_validator("servicos")
    @classmethod
    def _v_servicos(cls, v):
        if not v:
            raise ValueError("Selecione pelo menos um serviço.")
        return v


# ─────────────────────────── Venda ───────────────────────────
class ItemDaVenda(BaseModel):
    idproduto: int
    quantidade: int

    @field_validator("quantidade")
    @classmethod
    def _v_qtd(cls, v):
        if v is None or v <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        return v


class VendaIn(BaseModel):
    idcliente: int
    idfuncionario: int
    itens: List[ItemDaVenda]

    @field_validator("itens")
    @classmethod
    def _v_itens(cls, v):
        if not v:
            raise ValueError("Adicione pelo menos um produto à venda.")
        return v


# ─────────────────────────── Pagamento ───────────────────────────
class PagamentoIn(BaseModel):
    idagendamento: Optional[int] = None
    formapag: str
    valortotal: Decimal
    observacao: Optional[str] = None

    @field_validator("formapag")
    @classmethod
    def _v_forma(cls, v): return _nao_vazio(v, "Forma de pagamento")

    @field_validator("valortotal")
    @classmethod
    def _v_valor(cls, v):
        if v is None or v <= 0:
            raise ValueError("O valor total deve ser maior que zero.")
        return v
