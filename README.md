# 💄 Sistema de Gestão de Clínica Estética

Trabalho da disciplina **Banco de Dados II** — PostgreSQL.

Sistema web com **CRUD** completo: backend em **Python + FastAPI** e frontend em
**HTML / CSS / JavaScript** (sem frameworks).

---

## 📁 Estrutura

```
.
├── tabelas.sql          ← Tabelas + INSERTs (esquema oficial)
├── objetos.sql          ← 3 views, 1 trigger, 3 functions/procedures, índices
├── extras.sql           ← (opcional) CHECKs de integridade no banco
├── requirements.txt
├── backend/
│   ├── .env.example     ← modelo de credenciais (copie para .env)
│   └── app/
│       ├── main.py          ← app FastAPI + tratamento de erros + serve o frontend
│       ├── database.py      ← conexão PostgreSQL (psycopg2)
│       ├── schemas.py       ← validações de entrada (Pydantic)
│       ├── helpers.py
│       └── routers/         ← uma rota por entidade + dashboard
└── frontend/
    ├── index.html
    ├── css/styles.css
    └── js/  (api.js, components.js, entities.js, app.js)
```

---

## ⚙️ Pré-requisitos
- Python 3.9+
- PostgreSQL 12+

## 🚀 Como rodar

### 1) Banco de dados
Crie o banco e execute os scripts **nesta ordem**:

```sql
CREATE DATABASE "salaoBeleza";
```
```bash
psql -U postgres -d salaoBeleza -f tabelas.sql
psql -U postgres -d salaoBeleza -f objetos.sql
psql -U postgres -d salaoBeleza -f extras.sql   # opcional
```

### 2) Credenciais
Copie `backend/.env.example` para `backend/.env` e ajuste:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=salaoBeleza
DB_USER=postgres
DB_PASSWORD=sua_senha
```

### 3) Dependências e execução

```bash
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload
```

Acesse:
- **Aplicação:** http://localhost:8000
- **API (docs Swagger):** http://localhost:8000/docs

---

## 🧱 Objetos do banco (Etapa 1) e justificativas

| Tipo | Objeto | Por que foi escolhido |
|------|--------|------------------------|
| **View** | `vw_agenda_completa` | Junta cliente + funcionário + serviços (N:M) de cada agendamento; evita repetir JOINs complexos. |
| **View** | `vw_total_gasto_cliente` | Consolida gasto em produtos + serviços por cliente (relatório). |
| **View** | `vw_resumo_vendas_funcionario` | Faturamento gerado por cada funcionário. |
| **Trigger** | `trg_baixar_estoque` | Dá baixa automática no estoque a cada item vendido e alerta estoque baixo — garante consistência sem depender da aplicação. |
| **Procedure** | `sp_registrar_venda` | Agrupa validações + criação de venda/itens numa única transação. |
| **Function** | `fn_total_gasto_cliente` | Cálculo escalar reutilizável (total gasto por cliente). |
| **Function** | `fn_relatorio_faturamento` | Retorna tabela com faturamento (serviços/produtos) por período. |
| **Índices** | `idx_*` | Aceleram buscas por nome (ILIKE) e JOINs por chave estrangeira. |

> Correção feita na revisão: a versão anterior tinha **4 triggers** disparando no
> mesmo INSERT de `item_venda` (estoque era debitado várias vezes). Consolidado em
> **1 único trigger**.

---

## ✅ Regras de integridade implementadas (melhorias)

- Códigos sequenciais (`SERIAL`) e dados reais.
- **Não grava campos vazios** (nome, marca, forma de pagamento…).
- **Não aceita preço/quantidade/valor zero ou negativo** nem estoque negativo.
- **Impede vendas/agendamentos de cliente, produto ou serviço inexistentes.**
- Estoque insuficiente bloqueia a venda.
- Listas e pesquisas organizadas, telas estruturadas (títulos, separadores, alinhamento).

As validações ficam no backend (mensagens amigáveis em PT-BR) e, opcionalmente,
reforçadas por `CHECK`/`FK` no banco (`extras.sql`).

---

## 🎨 Telas (CRUD)
Início (dashboard), Clientes, Funcionários, Produtos, Serviços, Agendamentos
(com múltiplos serviços), Vendas (com itens e baixa de estoque) e Pagamentos.
