-- #######################################################################
-- VIEWS
-- #######################################################################
-- Justificativa geral: as consultas de relatório do sistema (agenda do dia,
-- gasto por cliente e faturamento por funcionário) envolvem vários JOINs e
-- agregações. Encapsulá-las em VIEWS evita repetir SQL complexo no backend,
-- centraliza a regra de negócio e simplifica a leitura/manutenção.

-- 1) Agenda completa: junta cliente, funcionário e os serviços (N:M) de cada agendamento, já com o valor total dos serviços.
CREATE OR REPLACE VIEW vw_agenda_completa AS
SELECT
    a.id                          AS id_agendamento,
    c.nome                        AS cliente,
    f.nome                        AS funcionario,
    a.datahora                    AS data_hora,
    a.status,
    a.observacao,
    STRING_AGG(s.nome, ', ')      AS servicos,
    COALESCE(SUM(ags.precototal), 0) AS valor_total_servicos
FROM agendamento a
JOIN cliente     c   ON c.id = a.idcliente
JOIN funcionario f   ON f.id = a.idfuncionario
LEFT JOIN agendamento_servico ags ON ags.idagendamento = a.id
LEFT JOIN servico             s   ON s.id = ags.idservico
GROUP BY a.id, c.nome, f.nome, a.datahora, a.status, a.observacao
ORDER BY a.datahora;


-- 2) Total gasto por cliente: soma o que cada cliente gastou em produtos (vendas) e em serviços (agendamentos), consolidando num só lugar.
CREATE OR REPLACE VIEW vw_total_gasto_cliente AS
SELECT
    c.id,
    c.nome,
    COALESCE(p.qtd_produtos, 0)    AS quantidade_produtos,
    COALESCE(s.qtd_servicos, 0)    AS quantidade_servicos,
    COALESCE(p.valor_produtos, 0)  AS valor_produtos,
    COALESCE(s.valor_servicos, 0)  AS valor_servicos,
    COALESCE(p.valor_produtos, 0) +
    COALESCE(s.valor_servicos, 0)  AS valor_total_gasto
FROM cliente c
LEFT JOIN (
    SELECT vp.idcliente,
           SUM(iv.quantidade) AS qtd_produtos,
           SUM(iv.precototal) AS valor_produtos
    FROM venda_produto vp
    INNER JOIN item_venda iv ON iv.idvenda = vp.id
    GROUP BY vp.idcliente
) p ON p.idcliente = c.id
LEFT JOIN (
    SELECT a.idcliente,
           COUNT(*)            AS qtd_servicos,
           SUM(ags.precototal) AS valor_servicos
    FROM agendamento a
    INNER JOIN agendamento_servico ags ON ags.idagendamento = a.id
    GROUP BY a.idcliente
) s ON s.idcliente = c.id
ORDER BY valor_total_gasto DESC;


-- 3) Resumo de vendas/atendimentos por funcionário (faturamento gerado).
CREATE OR REPLACE VIEW vw_resumo_vendas_funcionario AS
SELECT
    f.id,
    f.nome,
    COALESCE(v.total_vendas, 0)        AS total_vendas_produtos,
    COALESCE(v.valor_vendas, 0)        AS valor_total_vendas,
    COALESCE(a.total_agendamentos, 0)  AS total_atendimentos,
    COALESCE(a.valor_servicos, 0)      AS valor_servicos_realizados,
    COALESCE(v.valor_vendas, 0) +
    COALESCE(a.valor_servicos, 0)      AS faturamento_total_funcionario
FROM funcionario f
LEFT JOIN (
    SELECT vp.idfuncionario,
           COUNT(*)           AS total_vendas,
           SUM(iv.precototal) AS valor_vendas
    FROM venda_produto vp
    INNER JOIN item_venda iv ON iv.idvenda = vp.id
    GROUP BY vp.idfuncionario
) v ON v.idfuncionario = f.id
LEFT JOIN (
    SELECT a.idfuncionario,
           COUNT(*)            AS total_agendamentos,
           SUM(ags.precototal) AS valor_servicos
    FROM agendamento a
    INNER JOIN agendamento_servico ags ON ags.idagendamento = a.id
    GROUP BY a.idfuncionario
) a ON a.idfuncionario = f.id
ORDER BY faturamento_total_funcionario DESC;