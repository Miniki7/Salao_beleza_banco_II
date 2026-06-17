-- #######################################################################
-- FUNCTIONS / PROCEDURES
-- #######################################################################

-- 1) PROCEDURE  sp_registrar_venda
-- Justificativa: registrar uma venda envolve VÁRIOS passos que precisam
-- acontecer juntos (validar cliente/funcionário/produto, conferir estoque,
-- criar a venda e o item). Uma PROCEDURE agrupa essa lógica numa única
-- transação e centraliza as validações no banco, impedindo vendas de
-- clientes/produtos inexistentes ou com quantidade inválida.
CREATE OR REPLACE PROCEDURE sp_registrar_venda(
    p_idcliente     INT,
    p_idfuncionario INT,
    p_idproduto     INT,
    p_quantidade    INT
)
LANGUAGE plpgsql AS
$$
DECLARE
    v_preco    NUMERIC(10,2);
    v_estoque  INT;
    v_idvenda  INT;
BEGIN
    IF p_quantidade IS NULL OR p_quantidade <= 0 THEN
        RAISE EXCEPTION 'Quantidade deve ser maior que zero.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM cliente WHERE id = p_idcliente) THEN
        RAISE EXCEPTION 'Cliente % não existe.', p_idcliente;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM funcionario WHERE id = p_idfuncionario) THEN
        RAISE EXCEPTION 'Funcionário % não existe.', p_idfuncionario;
    END IF;

    SELECT preco, estoque INTO v_preco, v_estoque
      FROM produto WHERE id = p_idproduto;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Produto % não existe.', p_idproduto;
    END IF;

    IF v_estoque < p_quantidade THEN
        RAISE EXCEPTION 'Estoque insuficiente (disponível: %).', v_estoque;
    END IF;

    -- Cria a venda e o item (o trigger trg_baixar_estoque cuida do estoque)
    INSERT INTO venda_produto (idcliente, idfuncionario)
    VALUES (p_idcliente, p_idfuncionario)
    RETURNING id INTO v_idvenda;

    INSERT INTO item_venda (idvenda, idproduto, quantidade, precototal)
    VALUES (v_idvenda, p_idproduto, p_quantidade, v_preco * p_quantidade);
END;
$$;

-- 2) FUNCTION  fn_total_gasto_cliente
-- Justificativa: é um cálculo escalar reutilizável (total que um cliente já
-- gastou em produtos + serviços). Como FUNCTION, pode ser usada em SELECTs,
-- relatórios e na própria aplicação sem reescrever a soma.
CREATE OR REPLACE FUNCTION fn_total_gasto_cliente(p_idcliente INT)
RETURNS NUMERIC AS
$$
DECLARE
    v_produtos NUMERIC(10,2);
    v_servicos NUMERIC(10,2);
BEGIN
    SELECT COALESCE(SUM(iv.precototal), 0)
      INTO v_produtos
      FROM venda_produto vp
      JOIN item_venda iv ON iv.idvenda = vp.id
     WHERE vp.idcliente = p_idcliente;

    SELECT COALESCE(SUM(ags.precototal), 0)
      INTO v_servicos
      FROM agendamento a
      JOIN agendamento_servico ags ON ags.idagendamento = a.id
     WHERE a.idcliente = p_idcliente;

    RETURN v_produtos + v_servicos;
END;
$$ LANGUAGE plpgsql;

-- 3) FUNCTION  fn_relatorio_faturamento  (retorna tabela)
-- Justificativa: relatório gerencial de faturamento (serviços + produtos)
-- dentro de um período. Uma FUNCTION que RETORNA TABELA permite parametrizar
-- as datas e consumir o resultado como se fosse uma tabela/visão dinâmica.
CREATE OR REPLACE FUNCTION fn_relatorio_faturamento(
    p_inicio DATE,
    p_fim    DATE
)
RETURNS TABLE (
    faturamento_servicos NUMERIC,
    faturamento_produtos NUMERIC,
    faturamento_total    NUMERIC
) AS
$$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COALESCE(SUM(ags.precototal), 0)
           FROM agendamento a
           JOIN agendamento_servico ags ON ags.idagendamento = a.id
          WHERE a.datahora::date BETWEEN p_inicio AND p_fim),
        (SELECT COALESCE(SUM(iv.precototal), 0)
           FROM venda_produto vp
           JOIN item_venda iv ON iv.idvenda = vp.id
          WHERE vp.datavenda::date BETWEEN p_inicio AND p_fim),
        (SELECT COALESCE(SUM(ags.precototal), 0)
           FROM agendamento a
           JOIN agendamento_servico ags ON ags.idagendamento = a.id
          WHERE a.datahora::date BETWEEN p_inicio AND p_fim)
      + (SELECT COALESCE(SUM(iv.precototal), 0)
           FROM venda_produto vp
           JOIN item_venda iv ON iv.idvenda = vp.id
          WHERE vp.datavenda::date BETWEEN p_inicio AND p_fim);
END;
$$ LANGUAGE plpgsql;