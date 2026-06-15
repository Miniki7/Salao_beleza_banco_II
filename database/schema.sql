-- ============================================
-- SISTEMA DE GERENCIAMENTO - SALÃO DE BELEZA
-- Schema PostgreSQL
-- ============================================

-- CLIENTES
CREATE TABLE IF NOT EXISTS cliente (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    senha VARCHAR(100),
    cpf VARCHAR(14) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    endereco TEXT,
    data_nascimento DATE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FUNCIONÁRIOS
CREATE TABLE IF NOT EXISTS funcionario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    senha VARCHAR(100),
    cpf VARCHAR(14) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    endereco TEXT,
    data_nascimento DATE,
    status VARCHAR(20) DEFAULT 'Ativo' CHECK (status IN ('Ativo', 'Inativo'))
);

-- PRODUTOS
CREATE TABLE IF NOT EXISTS produto (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    marca VARCHAR(100),
    observacao TEXT,
    preco NUMERIC(10,2) NOT NULL CHECK (preco > 0),
    estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    estoque_minimo INTEGER DEFAULT 5,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SERVIÇOS
CREATE TABLE IF NOT EXISTS servico (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco NUMERIC(10,2) NOT NULL CHECK (preco > 0),
    tempo_estimado INTEGER -- em minutos
);

-- AGENDAMENTOS
CREATE TABLE IF NOT EXISTS agendamento (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES cliente(id),
    funcionario_id INTEGER NOT NULL REFERENCES funcionario(id),
    data_hora TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'Agendado' CHECK (status IN ('Agendado', 'Concluído', 'Cancelado')),
    observacao TEXT
);

-- AGENDAMENTO x SERVIÇOS (N:N)
CREATE TABLE IF NOT EXISTS agendamento_servico (
    agendamento_id INTEGER NOT NULL REFERENCES agendamento(id) ON DELETE CASCADE,
    servico_id INTEGER NOT NULL REFERENCES servico(id),
    PRIMARY KEY (agendamento_id, servico_id)
);

-- VENDAS
CREATE TABLE IF NOT EXISTS venda (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES cliente(id),
    funcionario_id INTEGER NOT NULL REFERENCES funcionario(id),
    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Ativa' CHECK (status IN ('Ativa', 'Cancelada'))
);

-- ITENS DA VENDA (N:N)
CREATE TABLE IF NOT EXISTS item_venda (
    id SERIAL PRIMARY KEY,
    venda_id INTEGER NOT NULL REFERENCES venda(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produto(id),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(10,2) NOT NULL CHECK (preco_unitario > 0)
);

-- PAGAMENTOS
CREATE TABLE IF NOT EXISTS pagamento (
    id SERIAL PRIMARY KEY,
    agendamento_id INTEGER REFERENCES agendamento(id),
    forma_pagamento VARCHAR(50) NOT NULL,
    valor_total NUMERIC(10,2) NOT NULL CHECK (valor_total > 0),
    observacao TEXT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TRIGGERS
-- ============================================

-- 1. Baixa automática de estoque ao inserir item_venda
CREATE OR REPLACE FUNCTION fn_baixa_estoque()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE produto
    SET estoque = estoque - NEW.quantidade
    WHERE id = NEW.produto_id;

    IF (SELECT estoque FROM produto WHERE id = NEW.produto_id) < 0 THEN
        RAISE EXCEPTION 'Estoque insuficiente para o produto ID %', NEW.produto_id;
    END IF;

    -- Alerta de estoque baixo
    IF (SELECT estoque FROM produto WHERE id = NEW.produto_id) <=
       (SELECT estoque_minimo FROM produto WHERE id = NEW.produto_id) THEN
        RAISE NOTICE 'ALERTA: Produto ID % com estoque abaixo do mínimo!', NEW.produto_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_baixa_estoque ON item_venda;
CREATE TRIGGER trg_baixa_estoque
AFTER INSERT ON item_venda
FOR EACH ROW EXECUTE FUNCTION fn_baixa_estoque();

-- 2. Reajuste de estoque ao cancelar/reativar venda
CREATE OR REPLACE FUNCTION fn_reajuste_estoque_venda()
RETURNS TRIGGER AS $$
BEGIN
    -- Cancelando venda: devolve estoque
    IF NEW.status = 'Cancelada' AND OLD.status = 'Ativa' THEN
        UPDATE produto p
        SET estoque = estoque + iv.quantidade
        FROM item_venda iv
        WHERE iv.venda_id = NEW.id AND iv.produto_id = p.id;
    END IF;

    -- Reativando venda: reduz estoque novamente
    IF NEW.status = 'Ativa' AND OLD.status = 'Cancelada' THEN
        UPDATE produto p
        SET estoque = estoque - iv.quantidade
        FROM item_venda iv
        WHERE iv.venda_id = NEW.id AND iv.produto_id = p.id;

        IF EXISTS (SELECT 1 FROM produto WHERE estoque < 0) THEN
            RAISE EXCEPTION 'Estoque insuficiente para reativar a venda';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_reajuste_estoque ON venda;
CREATE TRIGGER trg_reajuste_estoque
AFTER UPDATE OF status ON venda
FOR EACH ROW EXECUTE FUNCTION fn_reajuste_estoque_venda();
