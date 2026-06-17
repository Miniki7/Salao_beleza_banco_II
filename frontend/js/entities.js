/* Configuração declarativa das entidades de CRUD "padrão".
   Agendamentos e Vendas têm telas próprias (em app.js) por terem filhos. */

const ENTIDADES = {
  clientes: {
    titulo: "Clientes", endpoint: "/api/clientes",
    colunas: [
      { key: "id", label: "ID" },
      { key: "nome", label: "Nome" },
      { key: "cpf", label: "CPF", fmt: Fmt.cpf },
      { key: "telefone", label: "Telefone", fmt: Fmt.texto },
      { key: "email", label: "E-mail", fmt: Fmt.texto },
      { key: "datacadastro", label: "Cadastro", fmt: Fmt.data },
    ],
    campos: [
      { key: "nome", label: "Nome", type: "text", required: true },
      { key: "email", label: "E-mail", type: "email" },
      { key: "senha", label: "Senha", type: "text", required: true },
      { key: "cpf", label: "CPF (só números)", type: "number" },
      { key: "telefone", label: "Telefone", type: "text" },
      { key: "endereco", label: "Endereço", type: "text" },
      { key: "datanascimento", label: "Nascimento", type: "date" },
    ],
  },

  funcionarios: {
    titulo: "Funcionários", endpoint: "/api/funcionarios",
    colunas: [
      { key: "id", label: "ID" },
      { key: "nome", label: "Nome" },
      { key: "cpf", label: "CPF", fmt: Fmt.cpf },
      { key: "telefone", label: "Telefone", fmt: Fmt.texto },
      { key: "email", label: "E-mail", fmt: Fmt.texto },
      { key: "status", label: "Status", fmt: (v) =>
        `<span class="tag ${v === 'Ativo' ? 'ok' : 'neutro'}">${v || '—'}</span>` },
    ],
    campos: [
      { key: "nome", label: "Nome", type: "text", required: true },
      { key: "email", label: "E-mail", type: "email" },
      { key: "senha", label: "Senha", type: "text", required: true },
      { key: "cpf", label: "CPF (só números)", type: "number" },
      { key: "telefone", label: "Telefone", type: "text" },
      { key: "endereco", label: "Endereço", type: "text" },
      { key: "datanascimento", label: "Nascimento", type: "date" },
      { key: "status", label: "Status", type: "select", opcoes: ["Ativo", "Inativo"] },
    ],
  },

  produtos: {
    titulo: "Produtos", endpoint: "/api/produtos",
    colunas: [
      { key: "id", label: "ID" },
      { key: "nome", label: "Nome" },
      { key: "marca", label: "Marca", fmt: Fmt.texto },
      { key: "preco", label: "Preço", fmt: Fmt.moeda },
      { key: "estoque", label: "Estoque", fmt: (v, r) =>
        `<span class="tag ${v <= r.estoque_minimo ? 'alerta' : 'ok'}">${v}</span>` },
      { key: "estoque_minimo", label: "Mínimo" },
    ],
    campos: [
      { key: "nome", label: "Nome", type: "text", required: true },
      { key: "marca", label: "Marca", type: "text" },
      { key: "observacao", label: "Observação", type: "textarea" },
      { key: "preco", label: "Preço (R$)", type: "number", required: true, step: "0.01" },
      { key: "estoque", label: "Estoque", type: "number" },
      { key: "estoque_minimo", label: "Estoque mínimo", type: "number" },
    ],
  },

  servicos: {
    titulo: "Serviços", endpoint: "/api/servicos",
    colunas: [
      { key: "id", label: "ID" },
      { key: "nome", label: "Nome" },
      { key: "descricao", label: "Descrição", fmt: Fmt.texto },
      { key: "preco", label: "Preço", fmt: Fmt.moeda },
      { key: "tempoestimado", label: "Tempo (min)", fmt: Fmt.texto },
    ],
    campos: [
      { key: "nome", label: "Nome", type: "text", required: true },
      { key: "descricao", label: "Descrição", type: "textarea" },
      { key: "preco", label: "Preço (R$)", type: "number", required: true, step: "0.01" },
      { key: "tempoestimado", label: "Tempo estimado (min)", type: "number" },
    ],
  },

  pagamentos: {
    titulo: "Pagamentos", endpoint: "/api/pagamentos",
    colunas: [
      { key: "id", label: "ID" },
      { key: "idagendamento", label: "Agend.", fmt: Fmt.texto },
      { key: "cliente", label: "Cliente", fmt: Fmt.texto },
      { key: "formapag", label: "Forma" },
      { key: "valortotal", label: "Valor", fmt: Fmt.moeda },
      { key: "datahora", label: "Data/Hora", fmt: Fmt.dataHora },
    ],
    campos: [
      { key: "idagendamento", label: "Agendamento (opcional)", type: "select",
        remote: { endpoint: "/api/agendamentos", value: "id_agendamento",
                  label: (r) => `#${r.id_agendamento} – ${r.cliente}` }, vazio: "— Nenhum —" },
      { key: "formapag", label: "Forma de pagamento", type: "select", required: true,
        opcoes: ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Pix", "Transferência", "Outro"] },
      { key: "valortotal", label: "Valor total (R$)", type: "number", required: true, step: "0.01" },
      { key: "observacao", label: "Observação", type: "textarea" },
    ],
    // converte tipos antes de enviar
    prepararDados(d) {
      d.idagendamento = d.idagendamento ? Number(d.idagendamento) : null;
      return d;
    },
  },
};

// Itens do menu lateral (ordem de exibição)
const MENU = [
  { chave: "home", label: "Início" },
  { chave: "clientes", label: "Clientes" },
  { chave: "funcionarios", label: "Funcionários" },
  { chave: "produtos", label: "Produtos" },
  { chave: "servicos", label: "Serviços" },
  { chave: "agendamentos", label: "Agendamentos" },
  { chave: "vendas", label: "Vendas" },
  { chave: "pagamentos", label: "Pagamentos" },
];
