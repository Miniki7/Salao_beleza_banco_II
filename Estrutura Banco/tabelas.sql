-- =======================================================================
-- TABELA DO BANCO DE DADOS
-- =======================================================================

-- Tabela: cliente
CREATE TABLE cliente (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    senha VARCHAR(100) NOT NULL,
    cpf NUMERIC(14) UNIQUE,
    telefone VARCHAR(20),
    endereco VARCHAR(100),
    datanascimento DATE,
    datacadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: funcionario
CREATE TABLE funcionario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    senha VARCHAR(100) NOT NULL,
    cpf NUMERIC(14) UNIQUE,
    telefone VARCHAR(20),
    endereco VARCHAR(100),
    datanascimento DATE,
    datacadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20)
);

-- Tabela: produto
CREATE TABLE produto (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    marca VARCHAR(100),
    observacao TEXT,
    preco NUMERIC(10,2) NOT NULL,
    estoque INT DEFAULT 0,
    estoque_minimo INT DEFAULT 10,
    datahora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: servico
CREATE TABLE servico (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco NUMERIC(10,2) NOT NULL,
    tempoestimado INT -- Representando minutos, conforme o modelo
);

-- Tabela: agendamento
CREATE TABLE agendamento (
    id SERIAL PRIMARY KEY,
    idcliente INT NOT NULL,
    idfuncionario INT NOT NULL,
    datahora TIMESTAMP NOT NULL,
    status VARCHAR(50),
    observacao TEXT,
    datacadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_agendamento_cliente FOREIGN KEY (idcliente) REFERENCES cliente(id) ON DELETE RESTRICT,
    CONSTRAINT fk_agendamento_funcionario FOREIGN KEY (idfuncionario) REFERENCES funcionario(id) ON DELETE RESTRICT
);

-- Tabela: venda_produto
CREATE TABLE venda_produto (
    id SERIAL PRIMARY KEY,
    idcliente INT NOT NULL,
    idfuncionario INT NOT NULL,
    datavenda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_venda_cliente FOREIGN KEY (idcliente) REFERENCES cliente(id),
    CONSTRAINT fk_venda_funcionario FOREIGN KEY (idfuncionario) REFERENCES funcionario(id)
);

-- Tabela: item_venda
CREATE TABLE item_venda (
    id SERIAL PRIMARY KEY,
    idvenda INT NOT NULL,
    idproduto INT NOT NULL,
    quantidade INT NOT NULL CHECK (quantidade > 0),
    precototal NUMERIC(10,2) NOT NULL,
    CONSTRAINT fk_item_venda_origem FOREIGN KEY (idvenda) REFERENCES venda_produto(id) ON DELETE CASCADE,
    CONSTRAINT fk_item_venda_produto FOREIGN KEY (idproduto) REFERENCES produto(id)
);

-- Tabela: pagamento
CREATE TABLE pagamento (
    id SERIAL PRIMARY KEY,
    idagendamento INT,
    formapag VARCHAR(50) NOT NULL,
    valortotal NUMERIC(10,2) NOT NULL,
    observacao TEXT,
    datahora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pagamento_agendamento FOREIGN KEY (idagendamento) REFERENCES agendamento(id)
);

-- Tabela: agendamento_servico
CREATE TABLE agendamento_servico (
    idagendamento INT NOT NULL,
    idservico INT NOT NULL,
    precototal NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (idagendamento, idservico), -- Chave primária composta para tabela N:M
    CONSTRAINT fk_agendamento_servico_agenda FOREIGN KEY (idagendamento) REFERENCES agendamento(id) ON DELETE CASCADE,
    CONSTRAINT fk_agendamento_servico_item FOREIGN KEY (idservico) REFERENCES servico(id)
);


