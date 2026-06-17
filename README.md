# Sistema de Gestão de Clínica Estética

Trabalho da disciplina **Banco de Dados II** — PostgreSQL.

Aplicação web com **CRUD** completo: backend em **Python + FastAPI** e frontend em
**HTML / CSS / JavaScript** (sem frameworks). O backend também serve o frontend.

---

## Estrutura do projeto

```
.
├── tabelas.sql          # Tabelas + INSERTs (esquema oficial)
├── objetos.sql          # 3 views, 1 trigger, 3 functions/procedures, índices
├── extras.sql           # (opcional) CHECKs de integridade no banco
├── requirements.txt
├── backend/
│   ├── .env.example     # modelo de credenciais (copie para .env)
│   └── app/
│       ├── main.py          # app FastAPI + tratamento de erros + serve o frontend
│       ├── database.py      # conexão PostgreSQL (psycopg2)
│       ├── schemas.py       # validações de entrada (Pydantic)
│       ├── helpers.py       # checagens de existência de FK
│       └── routers/         # uma rota por entidade + dashboard
└── frontend/
    ├── index.html
    ├── css/styles.css
    └── js/  (api.js, components.js, entities.js, app.js)
```

---

## Pré-requisitos
- Python 3.9+
- PostgreSQL 12+

## Como rodar

### 1) Banco de dados
Crie o banco e execute os scripts **nesta ordem** (o `objetos.sql` é obrigatório:
as views e o trigger são usados pela aplicação):

```sql
CREATE DATABASE "salaoBeleza";
```
```bash
psql -U postgres -d salaoBeleza -f tabelas.sql     # tabelas + dados
psql -U postgres -d salaoBeleza -f objetos.sql     # views, trigger, funcs, índices
psql -U postgres -d salaoBeleza -f extras.sql      # opcional (CHECKs no banco)
```
> Também é possível abrir cada arquivo no **Query Tool** do pgAdmin e executar.

### 2) Credenciais
Copie `backend/.env.example` para `backend/.env` e ajuste com os dados do seu
PostgreSQL (host, porta, banco, usuário e senha):

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=salaoBeleza
DB_USER=postgres
DB_PASSWORD=sua_senha
```
> O nome do banco pode conter espaços (ex.: `Salao de Beleza - Projeto Final`).

### 3) Dependências e execução

```bash
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload
```

Acesse:
- **Aplicação:** http://localhost:8000
- **Documentação da API (Swagger):** http://localhost:8000/docs

---

## Objetos do banco (Etapa 1) e justificativas

| Tipo | Objeto | Por que foi escolhido | Usado pela aplicação |
|------|--------|------------------------|----------------------|
| **View** | `vw_agenda_completa` | Junta cliente + funcionário + serviços (N:M) de cada agendamento; evita repetir JOINs complexos. | Sim — lista de Agendamentos |
| **View** | `vw_total_gasto_cliente` | Consolida gasto em produtos + serviços por cliente. | Sim — Início (Top Clientes) |
| **View** | `vw_resumo_vendas_funcionario` | Faturamento gerado por cada funcionário. | Sim — Início (Faturamento) |
| **Trigger** | `trg_baixar_estoque` | Baixa automática de estoque a cada item vendido + alerta de estoque baixo; garante consistência sem depender da aplicação. | Sim — dispara em toda venda |
| **Procedure** | `sp_registrar_venda` | Agrupa validações + criação de venda/itens numa transação. | Objeto demonstrável |
| **Function** | `fn_total_gasto_cliente` | Cálculo escalar reutilizável (total gasto por cliente). | Objeto demonstrável |
| **Function** | `fn_relatorio_faturamento` | Retorna tabela com faturamento (serviços/produtos) por período. | Objeto demonstrável |
| **Índices** | `idx_*` | Aceleram buscas por nome (ILIKE) e JOINs por chave estrangeira. | Sim |

> **Revisão feita:** a versão anterior do `objetos.sql` tinha **4 triggers**
> disparando no mesmo INSERT de `item_venda` (estoque debitado várias vezes) e um
> trigger referenciando uma coluna inexistente. Tudo foi consolidado em
> **1 único trigger** correto, e foram adicionados as functions/procedures e os índices.

---

## Regras de integridade implementadas (melhorias)

- Códigos sequenciais (`SERIAL`) e dados reais.
- **Não grava campos vazios** (nome, marca, forma de pagamento…).
- **Não aceita preço/quantidade/valor zero ou negativo**, nem estoque negativo.
- **Impede vendas/agendamentos de cliente, produto ou serviço inexistentes.**
- Estoque insuficiente bloqueia a venda.
- Listas e pesquisas organizadas; telas estruturadas com título, separadores e alinhamento.

As validações ficam no **backend** (FastAPI/Pydantic), com mensagens claras em
PT-BR. O `extras.sql` (opcional) reforça as mesmas regras com `CHECK` no banco,
como segunda camada de proteção.

---

## Telas (CRUD)

| Tela | Descrição |
|------|-----------|
| Início | Alertas de estoque, top clientes e faturamento por funcionário (a partir das views). |
| Clientes | CRUD completo com busca por nome/CPF. |
| Funcionários | CRUD com status (Ativo/Inativo). |
| Produtos | CRUD com preço, estoque e estoque mínimo. |
| Serviços | CRUD com preço e tempo estimado. |
| Agendamentos | CRUD com seleção de múltiplos serviços (N:M). |
| Vendas | Registro com itens; baixa de estoque automática via trigger. |
| Pagamentos | Registro vinculado (opcionalmente) a um agendamento. |

---

## Observações
- O esquema oficial é o `tabelas.sql`. Caso já exista um banco criado a partir de
  uma versão anterior, garanta que ele esteja alinhado a esse arquivo (ex.: a coluna
  `produto.estoque_minimo`) e rode o `objetos.sql` para criar/atualizar os objetos.
- As senhas de cliente/funcionário são gravadas em texto puro, conforme o esquema
  entregue (contexto acadêmico).
