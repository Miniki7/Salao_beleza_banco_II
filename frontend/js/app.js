/* Controlador principal: navegação, CRUD genérico e telas de
   Agendamentos, Vendas e Dashboard. */

const content = document.getElementById("content");

// ─── Inicialização ──────────────────────────────────────────
function init() {
  const menu = document.getElementById("menu");
  MENU.forEach(m => {
    const b = document.createElement("button");
    b.textContent = m.label;
    b.dataset.chave = m.chave;
    b.onclick = () => navegar(m.chave);
    menu.appendChild(b);
  });
  verificarBanco();
  navegar("home");
}

async function verificarBanco() {
  const el = document.getElementById("db-status");
  try {
    const r = await API.get("/api/health");
    if (r.banco_ok) { el.textContent = "● banco conectado"; el.className = "db-status ok"; }
    else { el.textContent = "● banco offline"; el.className = "db-status erro"; }
  } catch { el.textContent = "● API offline"; el.className = "db-status erro"; }
}

function navegar(chave) {
  document.querySelectorAll("#menu button").forEach(b =>
    b.classList.toggle("ativo", b.dataset.chave === chave));
  if (chave === "home") return telaDashboard();
  if (chave === "agendamentos") return telaAgendamentos();
  if (chave === "vendas") return telaVendas();
  return telaEntidade(chave);
}

// ─── Helpers de opções remotas ──────────────────────────────
async function carregarOpcoes(remote) {
  const dados = await API.get(remote.endpoint + (remote.query || ""));
  return dados.map(r => ({
    value: r[remote.value],
    label: typeof remote.label === "function" ? remote.label(r) : r[remote.label],
  }));
}

// ============================================================
//  CRUD GENÉRICO (clientes, funcionários, produtos, serviços, pagamentos)
// ============================================================
function telaEntidade(chave) {
  const cfg = ENTIDADES[chave];
  content.innerHTML = `
    <div class="page-header"><h1>${cfg.titulo}</h1></div>
    <div class="toolbar">
      <button class="btn btn-primario" id="btn-novo">Adicionar</button>
      <input class="busca" id="busca" placeholder="Pesquisar..." />
    </div>
    <hr class="sep" />
    <div class="tabela-wrap"><table>
      <thead><tr>${cfg.colunas.map(c => `<th>${c.label}</th>`).join("")}<th></th></tr></thead>
      <tbody id="tbody"></tbody>
    </table></div>`;

  document.getElementById("btn-novo").onclick = () => formEntidade(cfg, null);
  const busca = document.getElementById("busca");
  let t;
  busca.oninput = () => { clearTimeout(t); t = setTimeout(() => carregar(cfg, busca.value), 250); };
  carregar(cfg, "");
}

async function carregar(cfg, busca) {
  const tbody = document.getElementById("tbody");
  try {
    const dados = await API.get(`${cfg.endpoint}?busca=${encodeURIComponent(busca)}`);
    if (!dados.length) {
      tbody.innerHTML = `<tr><td class="vazio" colspan="${cfg.colunas.length + 1}">Nenhum registro encontrado.</td></tr>`;
      return;
    }
    tbody.innerHTML = dados.map(row => {
      const tds = cfg.colunas.map(c => {
        const val = row[c.key];
        return `<td>${c.fmt ? c.fmt(val, row) : Fmt.texto(val)}</td>`;
      }).join("");
      return `<tr>${tds}
        <td class="acoes">
          <button class="btn btn-secundario btn-sm" onclick="editarEntidade('${cfg.endpoint}','${cfg.titulo}',${row.id})">Editar</button>
          <button class="btn btn-perigo btn-sm" onclick="excluirEntidade('${cfg.endpoint}',${row.id})">Excluir</button>
        </td></tr>`;
    }).join("");
  } catch (e) { toast(e.message, "erro"); }
}

async function editarEntidade(endpoint, titulo, id) {
  const cfg = Object.values(ENTIDADES).find(c => c.endpoint === endpoint);
  try {
    const reg = await API.get(`${endpoint}/${id}`);
    formEntidade(cfg, reg);
  } catch (e) { toast(e.message, "erro"); }
}

async function excluirEntidade(endpoint, id) {
  const cfg = Object.values(ENTIDADES).find(c => c.endpoint === endpoint);
  if (!confirmar(`Excluir o registro #${id}? Esta ação não pode ser desfeita.`)) return;
  try {
    await API.del(`${endpoint}/${id}`);
    toast("Registro excluído com sucesso!", "sucesso");
    carregar(cfg, document.getElementById("busca")?.value || "");
  } catch (e) { toast(e.message, "erro"); }
}

async function formEntidade(cfg, reg) {
  // carrega opções remotas, se houver
  for (const c of cfg.campos) {
    if (c.remote) {
      c.opcoes = await carregarOpcoes(c.remote);
      if (c.vazio) c.opcoes = [{ value: "", label: c.vazio }, ...c.opcoes];
    }
  }
  const html = cfg.campos.map(c => campoHTML(c, reg ? reg[c.key] : (c.type === "select" && c.opcoes ? c.opcoes[0].value : ""))).join("");
  Modal.abrir({
    titulo: (reg ? "Editar " : "Novo ") + cfg.titulo.replace(/s$/, ""),
    html: `<div class="grid-2">${html}</div>`,
    aoSalvar: async () => {
      let dados = {};
      cfg.campos.forEach(c => { dados[c.key] = lerCampo(c); });
      if (cfg.prepararDados) dados = cfg.prepararDados(dados);
      try {
        if (reg) await API.put(`${cfg.endpoint}/${reg.id}`, dados);
        else await API.post(cfg.endpoint, dados);
        toast(reg ? "Atualizado com sucesso!" : "Cadastrado com sucesso!", "sucesso");
        Modal.fechar();
        carregar(cfg, document.getElementById("busca")?.value || "");
      } catch (e) { toast(e.message, "erro"); }
    },
  });
}

// ============================================================
//  AGENDAMENTOS
// ============================================================
async function telaAgendamentos() {
  content.innerHTML = `
    <div class="page-header"><h1>Agendamentos</h1></div>
    <div class="toolbar">
      <button class="btn btn-primario" id="btn-novo">Novo agendamento</button>
      <input class="busca" id="busca" placeholder="Cliente ou funcionário..." />
    </div>
    <hr class="sep" />
    <div class="tabela-wrap"><table>
      <thead><tr><th>ID</th><th>Cliente</th><th>Funcionário</th><th>Data/Hora</th>
        <th>Status</th><th>Serviços</th><th>Total</th><th></th></tr></thead>
      <tbody id="tbody"></tbody>
    </table></div>`;
  document.getElementById("btn-novo").onclick = () => formAgendamento(null);
  const busca = document.getElementById("busca");
  let t;
  busca.oninput = () => { clearTimeout(t); t = setTimeout(carregarAgendamentos, 250); };
  carregarAgendamentos();
}

async function carregarAgendamentos() {
  const tbody = document.getElementById("tbody");
  const busca = document.getElementById("busca").value;
  try {
    const dados = await API.get(`/api/agendamentos?busca=${encodeURIComponent(busca)}`);
    if (!dados.length) { tbody.innerHTML = `<tr><td class="vazio" colspan="8">Nenhum agendamento.</td></tr>`; return; }
    tbody.innerHTML = dados.map(a => {
      const tagCls = a.status === "Cancelado" ? "cancelado" : a.status === "Concluído" ? "ok" : "neutro";
      return `<tr>
        <td>${a.id_agendamento}</td><td>${a.cliente}</td><td>${a.funcionario}</td>
        <td>${Fmt.dataHora(a.data_hora)}</td>
        <td><span class="tag ${tagCls}">${a.status || "—"}</span></td>
        <td>${Fmt.texto(a.servicos)}</td><td>${Fmt.moeda(a.valor_total_servicos)}</td>
        <td class="acoes">
          <button class="btn btn-secundario btn-sm" onclick="formAgendamento(${a.id_agendamento})">Editar</button>
          <button class="btn btn-perigo btn-sm" onclick="excluirAgendamento(${a.id_agendamento})">Excluir</button>
        </td></tr>`;
    }).join("");
  } catch (e) { toast(e.message, "erro"); }
}

async function excluirAgendamento(id) {
  if (!confirmar(`Excluir o agendamento #${id}?`)) return;
  try { await API.del(`/api/agendamentos/${id}`); toast("Agendamento excluído!", "sucesso"); carregarAgendamentos(); }
  catch (e) { toast(e.message, "erro"); }
}

async function formAgendamento(id) {
  const [clientes, funcionarios, servicos] = await Promise.all([
    API.get("/api/clientes"),
    API.get("/api/funcionarios?apenas_ativos=true"),
    API.get("/api/servicos"),
  ]);
  let reg = null, servicosSel = {};
  if (id) {
    reg = await API.get(`/api/agendamentos/${id}`);
    reg.servicos.forEach(s => servicosSel[s.idservico] = Number(s.precototal));
  }
  const optCli = clientes.map(c => `<option value="${c.id}" ${reg && reg.idcliente === c.id ? "selected" : ""}>${c.id} – ${c.nome}</option>`).join("");
  const optFunc = funcionarios.map(f => `<option value="${f.id}" ${reg && reg.idfuncionario === f.id ? "selected" : ""}>${f.id} – ${f.nome}</option>`).join("");
  const dh = reg && reg.datahora ? String(reg.datahora).slice(0, 16) : "";
  const status = reg ? reg.status : "Agendado";
  const optStatus = ["Agendado", "Confirmado", "Concluído", "Cancelado"]
    .map(s => `<option ${status === s ? "selected" : ""}>${s}</option>`).join("");
  const listaServ = servicos.map(s => {
    const checked = servicosSel[s.id] !== undefined;
    const preco = checked ? servicosSel[s.id] : Number(s.preco);
    return `<label>
      <input type="checkbox" class="chk-serv" value="${s.id}" ${checked ? "checked" : ""} />
      ${s.nome}
      <input type="number" step="0.01" class="preco-serv" data-id="${s.id}" value="${preco}" style="width:90px;margin-left:auto" />
    </label>`;
  }).join("");

  Modal.abrir({
    titulo: id ? "Editar Agendamento" : "Novo Agendamento",
    html: `
      <div class="grid-2">
        <div class="campo"><label>Cliente <small>*</small></label><select id="f_cli">${optCli}</select></div>
        <div class="campo"><label>Funcionário <small>*</small></label><select id="f_func">${optFunc}</select></div>
        <div class="campo"><label>Data e Hora <small>*</small></label><input type="datetime-local" id="f_dh" value="${dh}" /></div>
        <div class="campo"><label>Status</label><select id="f_status">${optStatus}</select></div>
      </div>
      <div class="campo"><label>Observação</label><textarea id="f_obs" rows="2">${reg ? escapeHtml(reg.observacao || "") : ""}</textarea></div>
      <div class="campo"><label>Serviços <small>* (marque e ajuste o preço)</small></label>
        <div class="check-list">${listaServ}</div></div>`,
    aoSalvar: async () => {
      const checks = [...document.querySelectorAll(".chk-serv:checked")];
      const servicosPayload = checks.map(ch => {
        const preco = document.querySelector(`.preco-serv[data-id="${ch.value}"]`).value;
        return { idservico: Number(ch.value), precototal: Number(preco) };
      });
      const payload = {
        idcliente: Number(document.getElementById("f_cli").value),
        idfuncionario: Number(document.getElementById("f_func").value),
        datahora: document.getElementById("f_dh").value,
        status: document.getElementById("f_status").value,
        observacao: document.getElementById("f_obs").value.trim() || null,
        servicos: servicosPayload,
      };
      try {
        if (id) await API.put(`/api/agendamentos/${id}`, payload);
        else await API.post("/api/agendamentos", payload);
        toast(id ? "Agendamento atualizado!" : "Agendamento criado!", "sucesso");
        Modal.fechar(); carregarAgendamentos();
      } catch (e) { toast(e.message, "erro"); }
    },
  });
}

// ============================================================
//  VENDAS
// ============================================================
async function telaVendas() {
  content.innerHTML = `
    <div class="page-header"><h1>Vendas</h1></div>
    <div class="toolbar">
      <button class="btn btn-primario" id="btn-novo">Nova venda</button>
      <input class="busca" id="busca" placeholder="Cliente ou funcionário..." />
    </div>
    <hr class="sep" />
    <div class="tabela-wrap"><table>
      <thead><tr><th>ID</th><th>Cliente</th><th>Funcionário</th><th>Data</th>
        <th>Itens</th><th>Total</th><th></th></tr></thead>
      <tbody id="tbody"></tbody>
    </table></div>`;
  document.getElementById("btn-novo").onclick = () => formVenda();
  const busca = document.getElementById("busca");
  let t;
  busca.oninput = () => { clearTimeout(t); t = setTimeout(carregarVendas, 250); };
  carregarVendas();
}

async function carregarVendas() {
  const tbody = document.getElementById("tbody");
  const busca = document.getElementById("busca").value;
  try {
    const dados = await API.get(`/api/vendas?busca=${encodeURIComponent(busca)}`);
    if (!dados.length) { tbody.innerHTML = `<tr><td class="vazio" colspan="7">Nenhuma venda.</td></tr>`; return; }
    tbody.innerHTML = dados.map(v => `<tr>
      <td>${v.id}</td><td>${v.cliente}</td><td>${v.funcionario}</td>
      <td>${Fmt.dataHora(v.datavenda)}</td><td>${v.itens}</td><td>${Fmt.moeda(v.total)}</td>
      <td class="acoes">
        <button class="btn btn-secundario btn-sm" onclick="detalheVenda(${v.id})">Detalhes</button>
        <button class="btn btn-perigo btn-sm" onclick="excluirVenda(${v.id})">Excluir</button>
      </td></tr>`).join("");
  } catch (e) { toast(e.message, "erro"); }
}

async function detalheVenda(id) {
  try {
    const v = await API.get(`/api/vendas/${id}`);
    const linhas = v.itens.map(i => `<tr><td>${i.produto}</td><td>${i.quantidade}</td>
      <td>${Fmt.moeda(i.preco_unitario)}</td><td>${Fmt.moeda(i.precototal)}</td></tr>`).join("");
    const total = v.itens.reduce((s, i) => s + Number(i.precototal), 0);
    Modal.abrir({
      titulo: `Detalhes da Venda #${id}`,
      html: `<table class="mini-tabela"><thead><tr><th>Produto</th><th>Qtd</th><th>Unit.</th><th>Subtotal</th></tr></thead>
        <tbody>${linhas}</tbody></table><div class="total-box">Total: ${Fmt.moeda(total)}</div>`,
      aoSalvar: null, textoSalvar: "",
    });
  } catch (e) { toast(e.message, "erro"); }
}

async function excluirVenda(id) {
  if (!confirmar(`Excluir a venda #${id}? O estoque será devolvido.`)) return;
  try { await API.del(`/api/vendas/${id}`); toast("Venda excluída e estoque devolvido!", "sucesso"); carregarVendas(); }
  catch (e) { toast(e.message, "erro"); }
}

async function formVenda() {
  const [clientes, funcionarios, produtos] = await Promise.all([
    API.get("/api/clientes"),
    API.get("/api/funcionarios?apenas_ativos=true"),
    API.get("/api/produtos?com_estoque=true"),
  ]);
  const itens = []; // {idproduto, nome, quantidade, preco, subtotal}

  const optCli = clientes.map(c => `<option value="${c.id}">${c.id} – ${c.nome}</option>`).join("");
  const optFunc = funcionarios.map(f => `<option value="${f.id}">${f.id} – ${f.nome}</option>`).join("");
  const optProd = produtos.map(p => `<option value="${p.id}">${p.nome} (${Fmt.moeda(p.preco)} | est: ${p.estoque})</option>`).join("");

  Modal.abrir({
    titulo: "Nova Venda",
    textoSalvar: "Finalizar venda",
    html: `
      <div class="grid-2">
        <div class="campo"><label>Cliente <small>*</small></label><select id="f_cli">${optCli}</select></div>
        <div class="campo"><label>Funcionário <small>*</small></label><select id="f_func">${optFunc}</select></div>
      </div>
      <div class="campo"><label>Adicionar produto</label>
        <div class="linha-add">
          <div class="campo"><select id="f_prod">${optProd}</select></div>
          <div class="campo" style="max-width:90px"><input type="number" id="f_qtd" value="1" min="1" /></div>
          <button class="btn btn-sucesso" id="btn-add" type="button">Adicionar</button>
        </div>
      </div>
      <table class="mini-tabela"><thead><tr><th>Produto</th><th>Qtd</th><th>Unit.</th><th>Subtotal</th><th></th></tr></thead>
        <tbody id="itens-body"><tr><td class="vazio" colspan="5">Nenhum item.</td></tr></tbody></table>
      <div class="total-box" id="venda-total">Total: ${Fmt.moeda(0)}</div>`,
    aoSalvar: async () => {
      if (!itens.length) { toast("Adicione pelo menos um produto.", "erro"); return; }
      const payload = {
        idcliente: Number(document.getElementById("f_cli").value),
        idfuncionario: Number(document.getElementById("f_func").value),
        itens: itens.map(i => ({ idproduto: i.idproduto, quantidade: i.quantidade })),
      };
      try {
        await API.post("/api/vendas", payload);
        toast("Venda registrada! Estoque atualizado.", "sucesso");
        Modal.fechar(); carregarVendas();
      } catch (e) { toast(e.message, "erro"); }
    },
  });

  function renderItens() {
    const body = document.getElementById("itens-body");
    if (!itens.length) { body.innerHTML = `<tr><td class="vazio" colspan="5">Nenhum item.</td></tr>`; }
    else {
      body.innerHTML = itens.map((i, idx) => `<tr>
        <td>${i.nome}</td><td>${i.quantidade}</td><td>${Fmt.moeda(i.preco)}</td><td>${Fmt.moeda(i.subtotal)}</td>
        <td class="acoes"><button class="btn btn-perigo btn-sm" data-idx="${idx}">Remover</button></td></tr>`).join("");
      body.querySelectorAll("button[data-idx]").forEach(b =>
        b.onclick = () => { itens.splice(Number(b.dataset.idx), 1); renderItens(); });
    }
    const total = itens.reduce((s, i) => s + i.subtotal, 0);
    document.getElementById("venda-total").textContent = "Total: " + Fmt.moeda(total);
  }

  document.getElementById("btn-add").onclick = () => {
    const pid = Number(document.getElementById("f_prod").value);
    const qtd = Number(document.getElementById("f_qtd").value);
    const prod = produtos.find(p => p.id === pid);
    if (!prod) { toast("Selecione um produto.", "erro"); return; }
    if (!qtd || qtd <= 0) { toast("Quantidade deve ser maior que zero.", "erro"); return; }
    const jaTem = itens.find(i => i.idproduto === pid);
    const qtdTotal = (jaTem ? jaTem.quantidade : 0) + qtd;
    if (qtdTotal > prod.estoque) { toast(`Estoque insuficiente (disponível: ${prod.estoque}).`, "erro"); return; }
    if (jaTem) { jaTem.quantidade = qtdTotal; jaTem.subtotal = qtdTotal * Number(prod.preco); }
    else itens.push({ idproduto: pid, nome: prod.nome, quantidade: qtd, preco: Number(prod.preco), subtotal: qtd * Number(prod.preco) });
    renderItens();
  };
}

// ============================================================
//  DASHBOARD
// ============================================================
async function telaDashboard() {
  content.innerHTML = `<div class="page-header"><h1>Início</h1></div><hr class="sep" /><div id="dash">Carregando…</div>`;
  try {
    const d = await API.get("/api/dashboard");

    const alertas = d.alertas_estoque.length
      ? d.alertas_estoque.map(p => `<tr><td>${p.nome}</td>
          <td><span class="tag alerta">${p.estoque}</span></td><td>${p.estoque_minimo}</td></tr>`).join("")
      : `<tr><td class="vazio" colspan="3">Nenhum produto com estoque baixo.</td></tr>`;

    const topCli = d.top_clientes.length
      ? d.top_clientes.map(c => `<tr><td>${c.nome}</td><td>${Fmt.moeda(c.valor_total_gasto)}</td></tr>`).join("")
      : `<tr><td class="vazio" colspan="2">Sem dados.</td></tr>`;

    const fat = d.faturamento_funcionarios.length
      ? d.faturamento_funcionarios.map(f => `<tr><td>${f.nome}</td><td>${Fmt.moeda(f.faturamento_total_funcionario)}</td></tr>`).join("")
      : `<tr><td class="vazio" colspan="2">Sem dados.</td></tr>`;

    document.getElementById("dash").innerHTML = `
      <div class="painel">
        <h3>Alertas de Estoque</h3>
        <table><thead><tr><th>Produto</th><th>Estoque</th><th>Mínimo</th></tr></thead><tbody>${alertas}</tbody></table>
      </div>
      <div class="painel-grid">
        <div class="painel"><h3>Top Clientes (gasto total)</h3>
          <table><thead><tr><th>Cliente</th><th>Total</th></tr></thead><tbody>${topCli}</tbody></table></div>
        <div class="painel"><h3>Faturamento por Funcionário</h3>
          <table><thead><tr><th>Funcionário</th><th>Total</th></tr></thead><tbody>${fat}</tbody></table></div>
      </div>`;
  } catch (e) {
    document.getElementById("dash").innerHTML =
      `<div class="painel"><p>Não foi possível carregar o dashboard.</p>
       <p style="color:var(--erro)">${e.message}</p>
       <p>Verifique se o banco está rodando e o <code>backend/.env</code> está configurado.</p></div>`;
  }
}

window.addEventListener("DOMContentLoaded", init);
