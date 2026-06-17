-- =======================================================================
-- Contrainsts de integridade e regras de negócio
-- =======================================================================

-- ---- Campos de texto obrigatórios não podem ser vazios -----------------
ALTER TABLE cliente      ADD CONSTRAINT ck_cliente_nome_nvazio      CHECK (length(trim(nome)) > 0);
ALTER TABLE funcionario  ADD CONSTRAINT ck_funcionario_nome_nvazio  CHECK (length(trim(nome)) > 0);
ALTER TABLE produto      ADD CONSTRAINT ck_produto_nome_nvazio      CHECK (length(trim(nome)) > 0);
ALTER TABLE servico      ADD CONSTRAINT ck_servico_nome_nvazio      CHECK (length(trim(nome)) > 0);

-- ---- Valores monetários e quantidades positivos ------------------------
ALTER TABLE produto   ADD CONSTRAINT ck_produto_preco_pos    CHECK (preco > 0);
ALTER TABLE produto   ADD CONSTRAINT ck_produto_estoque_npos CHECK (estoque >= 0);
ALTER TABLE servico   ADD CONSTRAINT ck_servico_preco_pos    CHECK (preco > 0);
ALTER TABLE servico   ADD CONSTRAINT ck_servico_tempo_pos    CHECK (tempoestimado IS NULL OR tempoestimado > 0);
ALTER TABLE pagamento ADD CONSTRAINT ck_pagamento_valor_pos  CHECK (valortotal > 0);
ALTER TABLE item_venda ADD CONSTRAINT ck_item_preco_pos      CHECK (precototal > 0);
-- (item_venda.quantidade > 0 já existe em tabelas.sql)

-- ---- Domínios de status (evita valores inválidos) ----------------------
ALTER TABLE funcionario ADD CONSTRAINT ck_funcionario_status
    CHECK (status IS NULL OR status IN ('Ativo', 'Inativo'));
ALTER TABLE agendamento ADD CONSTRAINT ck_agendamento_status
    CHECK (status IS NULL OR status IN ('Agendado', 'Confirmado', 'Concluído', 'Cancelado'));