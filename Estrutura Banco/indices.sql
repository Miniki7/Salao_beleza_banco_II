-- #######################################################################
-- ÍNDICES
-- #######################################################################
-- Justificativa: as colunas abaixo são muito usadas em buscas (WHERE/ILIKE),
-- em ordenações e principalmente nos JOINs por chave estrangeira. Índices
-- nessas colunas aceleram pesquisas e relatórios. (As PKs e a coluna cpf
-- UNIQUE já são indexadas automaticamente pelo PostgreSQL.)

-- Buscas por nome (campos de pesquisa das telas)
CREATE INDEX IF NOT EXISTS idx_cliente_nome      ON cliente(nome);
CREATE INDEX IF NOT EXISTS idx_funcionario_nome  ON funcionario(nome);
CREATE INDEX IF NOT EXISTS idx_produto_nome      ON produto(nome);
CREATE INDEX IF NOT EXISTS idx_servico_nome      ON servico(nome);

-- Chaves estrangeiras (aceleram JOINs e relatórios)
CREATE INDEX IF NOT EXISTS idx_agendamento_cliente     ON agendamento(idcliente);
CREATE INDEX IF NOT EXISTS idx_agendamento_funcionario ON agendamento(idfuncionario);
CREATE INDEX IF NOT EXISTS idx_agendamento_datahora    ON agendamento(datahora);
CREATE INDEX IF NOT EXISTS idx_venda_cliente           ON venda_produto(idcliente);
CREATE INDEX IF NOT EXISTS idx_venda_funcionario       ON venda_produto(idfuncionario);
CREATE INDEX IF NOT EXISTS idx_item_venda_venda        ON item_venda(idvenda);
CREATE INDEX IF NOT EXISTS idx_item_venda_produto      ON item_venda(idproduto);
CREATE INDEX IF NOT EXISTS idx_pagamento_agendamento   ON pagamento(idagendamento);