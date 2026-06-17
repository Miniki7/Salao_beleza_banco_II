-- =======================================================================
-- INSERTS
-- =======================================================================

INSERT INTO cliente (nome, email, senha, cpf, telefone, endereco, datanascimento, datacadastro) VALUES
('Ana Silva Oliveira', 'ana.silva@email.com', 'senhaAna123', 12345678901, '(11) 98765-4321', 'Rua das Flores, 123 - SP', '1990-05-14', '2026-01-10 09:30:00'),
('Bruno Santos Souza', 'bruno.santos@email.com', 'bruno@321', 23456789012, '(11) 97654-3210', 'Av. Paulista, 1500 - SP', '1985-11-22', '2026-01-15 14:15:00'),
('Camila Rodrigues Lima', 'camila.lima@email.com', 'camilasenhasegura', 34567890123, '(21) 96543-2109', 'Rua Copacabana, 45 - RJ', '1995-03-08', '2026-02-02 11:00:00'),
('Diego Almeida Costa', 'diego.costa@email.com', 'diego9988', 45678901234, '(31) 95432-1098', 'Rua Bahia, 88 - BH', '1988-08-30', '2026-02-20 16:45:00'),
('Elena Pereira Barbosa', 'elena.b@email.com', 'elena12345', 56789012345, '(11) 94321-0987', 'Alameda Lorena, 712 - SP', '2000-12-01', '2026-03-05 10:20:00'),
('Felipe Melo Duarte', 'felipe.melo@email.com', 'fepassword', 67890123456, '(11) 93210-9876', 'Rua Augusta, 2100 - SP', '1993-07-19', '2026-03-12 15:30:00'),
('Gabriela Freitas Reis', 'gabi.freitas@email.com', 'gabi#2026', 78901234567, '(21) 92109-8765', 'Av. Atlântica, 500 - RJ', '1992-01-25', '2026-04-01 09:00:00'),
('Heitor Vieira Rocha', 'heitor.rocha@email.com', 'heitor_mudar', 89012345678, '(41) 91098-7654', 'Rua XV de Novembro, 300 - PR', '1982-04-12', '2026-04-18 17:10:00'),
('Isabela Mendes Borges', 'isabela.m@email.com', 'bellamendes', 90123456789, '(11) 90987-6543', 'Rua Pamplona, 1050 - SP', '1997-09-05', '2026-05-02 13:25:00'),
('João Pedro Carvalho', 'joao.pedro@email.com', 'jpcarvalho1', 12309847561, '(31) 99876-5432', 'Av. Afonso Pena, 1200 - BH', '1989-02-17', '2026-05-25 11:40:00');

INSERT INTO funcionario (nome, email, senha, cpf, telefone, endereco, datanascimento, datacadastro, status) VALUES
('Marcos Cabelereiro Master', 'marcos.hair@salao.com', 'marcos987', 10928374655, '(11) 98888-1111', 'Rua dos Pinheiros, 50 - SP', '1984-06-20', '2025-01-01 08:00:00', 'Ativo'),
('Juliana Manicure Profissional', 'juliana.nails@salao.com', 'ju_unhas', 21938475646, '(11) 98888-2222', 'Rua Fradique Coutinho, 120 - SP', '1991-03-15', '2025-01-01 08:00:00', 'Ativo'),
('Ricardo Barbeiro Visagista', 'ricardo.barber@salao.com', 'ricardo_barba', 32049586737, '(11) 98888-3333', 'Av. Rebouças, 3000 - SP', '1987-09-10', '2025-03-15 08:30:00', 'Ativo'),
('Patricia Esteticista', 'patricia.beauty@salao.com', 'paty_facial', 43150697828, '(11) 98888-4444', 'Rua Bela Cintra, 800 - SP', '1989-11-05', '2025-05-10 09:00:00', 'Ativo'),
('Lucas Colorista Expert', 'lucas.color@salao.com', 'lucas_tintura', 54261708919, '(11) 98888-5555', 'Rua Oscar Freire, 450 - SP', '1992-02-28', '2025-06-01 08:00:00', 'Ativo'),
('Amanda Podóloga', 'amanda.podo@salao.com', 'amanda_pes', 65372819001, '(11) 98888-6666', 'Rua Estados Unidos, 150 - SP', '1983-05-12', '2025-08-20 09:15:00', 'Ativo'),
('Thiago Designer de Sobrancelha', 'thiago.brows@salao.com', 'thiago_olhar', 76483920112, '(11) 98888-7777', 'Rua Consolação, 2500 - SP', '1995-10-22', '2025-10-01 10:00:00', 'Ativo'),
('Carla Maquiadora MakeUP', 'carla.make@salao.com', 'carla_batom', 87594031223, '(11) 98888-8888', 'Alameda Jaú, 950 - SP', '1994-08-14', '2025-11-15 08:00:00', 'Ativo'),
('Fernanda Recepcionista Principal', 'fernanda.recepcao@salao.com', 'fer_agenda', 98605142334, '(11) 98888-9999', 'Rua Mourato Coelho, 600 - SP', '1998-04-03', '2025-01-01 07:30:00', 'Ativo'),
('Roberto Auxiliar de Serviços', 'roberto.aux@salao.com', 'roberto_limpa', 12349876512, '(11) 97777-0000', 'Rua Cardeal Arcoverde, 1800 - SP', '1980-01-30', '2025-02-01 07:00:00', 'Ativo');

INSERT INTO produto (nome, marca, observacao, preco, estoque, estoque_minimo, datahora) VALUES
('Shampoo Hidratação Profunda 500ml', 'LOréal Professionnel', 'Uso diário para cabelos secos', 120.00, 25, 4, '2026-01-05 10:00:00'),
('Condicionador Absolut Repair 500ml', 'LOréal Professionnel', 'Reconstrução capilar instantânea', 145.00, 20, 4, '2026-01-05 10:05:00'),
('Óleo Capilar Reflexion 100ml', 'Wella Professionals', 'Finalizador e protetor térmico', 190.00, 15, 4, '2026-01-12 11:30:00'),
('Pomada Modeladora Efeito Matte 100g', 'Keune', 'Para fixação forte de penteados masculinos', 95.00, 40, 4, '2026-02-01 14:00:00'),
('Máscara de Nutrição Cronograma 500g', 'Kérastase', 'Tratamento de alto padrão', 320.00, 8, 4, '2026-02-15 09:45:00'),
('Base Fortalecedora de Unhas 10ml', 'Risqué', 'Tratamento contra unhas quebradiças', 15.00, 100, 4, '2026-03-01 16:20:00'),
('Creme Esfoliante Facial Antiacne', 'La Roche-Posay', 'Uso cabine e revenda', 89.90, 12, 4, '2026-03-20 10:10:00'),
('Água Micelar Demaquilante 200ml', 'Bioderma', 'Limpeza suave pré-maquiagem', 65.00, 18, 4, '2026-04-02 11:15:00'),
('Tônico Capilar Antiqueda 100ml', 'Vichy', 'Tratamento para o couro cabeludo', 160.00, 10, 4, '2026-04-10 15:30:00'),
('Esmalte Coleção Outono Vermelho', 'Colorama', 'Cor clássica de alta durabilidade', 8.50, 150, 4, '2026-05-01 09:00:00');

INSERT INTO servico (nome, descricao, preco, tempoestimado) VALUES
('Corte de Cabelo Feminino', 'Corte, lavagem simples e secagem rápida', 150.00, 60),
('Escova Progressiva Sem Formol', 'Alinhamento térmico capilar de longa duração', 350.00, 150),
('Corte de Cabelo Masculino', 'Corte moderno na tesoura ou máquina', 70.00, 40),
('Barba Completa com Toalha Quente', 'Barboterapia clássica com hidratação de fios', 60.00, 30),
('Manicure e Pedicure Simples', 'Corte, lixamento e esmaltação comum', 65.00, 60),
('Alongamento de Unhas em Gel', 'Aplicação completa e acabamento realista', 180.00, 120),
('Limpeza de Pele Profunda', 'Extração de cravos e aplicação de máscara calmante', 140.00, 90),
('Design de Sobrancelha com Henna', 'Alinhamento geométrico do olhar com preenchimento', 55.00, 40),
('Mechas / Luzes no Cabelo', 'Descoloração global em mechas com proteção plex', 450.00, 240),
('Maquiagem Profissional Festa', 'Maquiagem completa com aplicação de cílios postiços', 200.00, 75);

INSERT INTO agendamento (idcliente, idfuncionario, datahora, status, observacao, datacadastro) VALUES
(1, 1, '2026-06-10 09:00:00', 'Agendado', 'Cliente prefere secador morno', '2026-06-05 14:00:00'),
(2, 3, '2026-06-10 10:30:00', 'Agendado', 'Fazer degradê navalhado', '2026-06-06 09:15:00'),
(3, 2, '2026-06-10 14:00:00', 'Confirmado', 'Trazer o próprio esmalte se possível', '2026-06-07 11:30:00'),
(4, 3, '2026-06-11 09:00:00', 'Agendado', NULL, '2026-06-08 16:00:00'),
(5, 5, '2026-06-11 13:00:00', 'Confirmado', 'Avaliação de cor antes do procedimento', '2026-06-08 17:45:00'),
(6, 6, '2026-06-12 10:00:00', 'Agendado', 'Problema com unha encravada no pé esquerdo', '2026-06-09 10:00:00'),
(7, 8, '2026-06-12 16:00:00', 'Agendado', 'Maquiagem para casamento à noite', '2026-06-09 11:20:00'),
(8, 4, '2026-06-13 11:00:00', 'Agendado', 'Pele muito sensível', '2026-06-09 13:05:00'),
(9, 2, '2026-06-13 15:00:00', 'Agendado', 'Manutenção do alongamento em gel', '2026-06-09 14:40:00'),
(10, 1, '2026-06-15 09:00:00', 'Agendado', NULL, '2026-06-09 18:22:00');

INSERT INTO venda_produto (idcliente, idfuncionario, datavenda) VALUES
(1, 9, '2026-06-01 11:30:00'),
(3, 9, '2026-06-02 15:45:00'),
(2, 3, '2026-06-02 18:00:00'),
(5, 5, '2026-06-03 12:20:00'),
(7, 9, '2026-06-04 10:15:00'),
(4, 9, '2026-06-05 16:40:00'),
(9, 2, '2026-06-06 14:10:00'),
(6, 9, '2026-06-07 11:00:00'),
(10, 9, '2026-06-08 13:25:00'),
(8, 4, '2026-06-08 17:50:00');

INSERT INTO item_venda (idvenda, idproduto, quantidade, precototal) VALUES
(1, 1, 1, 120.00), -- Venda 1: 1 Shampoo LOréal
(1, 2, 1, 145.00), -- Venda 1: 1 Condicionador LOréal
(2, 6, 2, 30.00),  -- Venda 2: 2 Bases Fortalecedoras
(3, 4, 1, 95.00),  -- Venda 3: 1 Pomada Keune
(4, 5, 1, 320.00), -- Venda 4: 1 Máscara Kérastase
(5, 8, 1, 65.00),  -- Venda 5: 1 Água Micelar
(6, 4, 1, 95.00),  -- Venda 6: 1 Pomada Keune
(7, 10, 3, 25.50), -- Venda 7: 3 Esmaltes Colorama
(8, 9, 1, 160.00), -- Venda 8: 1 Tônico Vichy
(9, 3, 1, 190.00); -- Venda 9: 1 Óleo Capilar Wella

INSERT INTO pagamento (idagendamento, formapag, valortotal, observacao, datahora) VALUES
(1, 'Pix', 150.00, 'Pagamento integral realizado via chave CNPJ', '2026-06-09 09:30:00'),
(2, 'Cartão de Crédito', 85.00, 'Parcelado em 1x no Visa', '2026-06-09 10:45:00'),
(3, 'Dinheiro', 45.00, 'Cliente pagou com nota de R$ 50,00 (Troco R$ 5,00)', '2026-06-09 11:15:00'),
(4,'Pix', 210.00, 'Pagamento aprovado instantaneamente', '2026-06-09 14:00:00'),
(5, 'Cartão de Débito', 120.00, 'Transação realizada na máquina Master', '2026-06-09 15:30:00'),
(6, 'Pix', 60.00, 'Transferência feita pelo marido da cliente', '2026-06-09 16:20:00'),
(7, 'Cartão de Crédito', 350.00, 'Parcelado em 3x sem juros no Elo', '2026-06-09 17:00:00'),
(8, 'Dinheiro', 90.00, 'Valor exato em espécie', '2026-06-09 17:45:00'),
(9, 'Cartão de Débito', 130.00, 'Aproximação efetuada com sucesso', '2026-06-09 18:30:00'),
(10, 'Pix', 180.00, 'Sinal de 50% pago antes e o restante agora no Pix', '2026-06-09 19:15:00');

INSERT INTO agendamento_servico (idagendamento, idservico, precototal) VALUES
-- Cliente 1 fez Corte de Cabelo (Serviço 1) e Barba (Serviço 2)
(1, 1, 90.00),
(1, 2, 60.00),
-- Cliente 2 fez Manicure Simples (Serviço 3)
(2, 3, 85.00),
-- Cliente 3 fez Design de Sobrancelha (Serviço 4)
(3, 4, 45.00),
-- Cliente 4 fez Coloração de Cabelo (Serviço 5)
(4, 5, 210.00),
-- Cliente 5 fez Escova Hidratante (Serviço 6)
(5, 6, 120.00),
-- Cliente 6 fez Depilação Buço (Serviço 7)
(6, 7, 60.00),
-- Cliente 7 fez Progressiva (Serviço 8) e Pedicure (Serviço 9)
(7, 8, 280.00),
(7, 9, 70.00),
-- Cliente 8 fez Maquiagem Social (Serviço 10)
(8, 10, 90.00),
-- Cliente 9 fez Corte Infantil (Serviço 1) com preço promocional
(9, 1, 130.00),
-- Cliente 10 fez Limpeza de Pele (Serviço 11)
(10, 6, 180.00);