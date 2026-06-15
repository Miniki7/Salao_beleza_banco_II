# 💄 Sistema de Gerenciamento – Salão de Beleza

Sistema desktop completo desenvolvido com **Python 3 + Tkinter + PostgreSQL**.

---

## 📁 Estrutura do Projeto

```
salao/
├── main.py                  ← Ponto de entrada / janela principal
├── requirements.txt
├── database/
│   ├── connection.py        ← Conexão e utilitários do banco
│   └── schema.sql           ← Tabelas e triggers PostgreSQL
├── modules/
│   ├── dashboard.py         ← Tela inicial com cards e resumos
│   ├── clientes.py
│   ├── funcionarios.py
│   ├── produtos.py
│   ├── servicos.py
│   ├── agendamentos.py      ← Com seleção múltipla de serviços (N:N)
│   ├── vendas.py            ← Com controle automático de estoque
│   └── pagamentos.py
└── utils/
    ├── constants.py         ← Paleta de cores, fontes, constantes
    └── widgets.py           ← Componentes reutilizáveis (botões, tabelas, etc.)
```

---

## ⚙️ Pré-requisitos

- Python 3.9+
- PostgreSQL 12+
- pip

---

## 🚀 Instalação e Execução

### 1. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 2. Criar o banco de dados no PostgreSQL

```sql
CREATE DATABASE salao_beleza;
```

### 3. Configurar credenciais

Edite o arquivo `database/connection.py`:

```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "salao_beleza",
    "user":     "postgres",
    "password": "SUA_SENHA_AQUI",
}
```

Ou use variáveis de ambiente:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=salao_beleza
export DB_USER=postgres
export DB_PASSWORD=SUA_SENHA
```

### 4. Executar o sistema

```bash
cd salao
python main.py
```

O sistema criará automaticamente todas as tabelas e triggers na primeira execução.

---

## 🗂️ Módulos

| Módulo         | Funcionalidades                                           |
|----------------|-----------------------------------------------------------|
| Dashboard      | Cards com totais, alertas de estoque, agendamentos hoje  |
| Clientes       | CRUD completo com busca por nome/CPF                     |
| Funcionários   | CRUD com controle de status (Ativo/Inativo)              |
| Produtos       | CRUD + alertas de estoque mínimo em destaque             |
| Serviços       | CRUD com preço e tempo estimado                          |
| Agendamentos   | CRUD com seleção múltipla de serviços (N:N)              |
| Vendas         | Registro com atualização automática de estoque (trigger) |
| Pagamentos     | Registro vinculado a agendamentos (opcional)             |

---

## ⚡ Triggers PostgreSQL

1. **Baixa de estoque** – ao inserir item na venda, o estoque é reduzido automaticamente
2. **Restauração de estoque** – ao cancelar uma venda, o estoque é devolvido
3. **Alerta de estoque baixo** – NOTICE no PostgreSQL quando estoque ≤ estoque_mínimo

---

## 🎨 Paleta de Cores

| Cor              | Hex       |
|------------------|-----------|
| Rosa principal   | `#E98688` |
| Verde suave      | `#CCEDCE` |
| Rosa claro       | `#FEB3C2` |
| Bege             | `#F8D3AD` |
| Azul suave       | `#AABDFF` |
| Texto            | `#4F4F4F` |
