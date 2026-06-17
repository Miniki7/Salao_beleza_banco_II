-- #######################################################################
-- TRIGGER
-- #######################################################################
-- Justificativa: o controle de estoque deve ser AUTOMÁTICO e confiável.
-- Em vez de confiar que toda parte do sistema lembre de dar baixa no estoque
-- ao vender, um TRIGGER garante que, a CADA item de venda inserido, o estoque
-- do produto é debitado na mesma transação. Também emite um alerta (NOTICE)
-- quando o estoque fica igual/abaixo do mínimo cadastrado.

CREATE OR REPLACE FUNCTION fn_baixar_estoque()
RETURNS TRIGGER AS
$$
DECLARE
    v_estoque_atual  INT;
    v_estoque_minimo INT;
BEGIN
    -- 1) Baixa o estoque do produto vendido
    UPDATE produto
       SET estoque = estoque - NEW.quantidade
     WHERE id = NEW.idproduto;

    -- 2) Lê os valores já atualizados
    SELECT estoque, estoque_minimo
      INTO v_estoque_atual, v_estoque_minimo
      FROM produto
     WHERE id = NEW.idproduto;

    -- 3) Impede estoque negativo (não há mercadoria suficiente)
    IF v_estoque_atual < 0 THEN
        RAISE EXCEPTION 'Estoque insuficiente para o produto % (faltam % unidades).',
            NEW.idproduto, ABS(v_estoque_atual);
    END IF;

    -- 4) Alerta de estoque baixo
    IF v_estoque_atual <= v_estoque_minimo THEN
        RAISE NOTICE 'ALERTA: produto % com estoque baixo (% un., mínimo %).',
            NEW.idproduto, v_estoque_atual, v_estoque_minimo;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_baixar_estoque ON item_venda;
CREATE TRIGGER trg_baixar_estoque
AFTER INSERT ON item_venda
FOR EACH ROW
EXECUTE FUNCTION fn_baixar_estoque();