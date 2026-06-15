import tkinter as tk
from tkinter import ttk
from database.connection import execute_query
from utils.constants import COLORS, FONTS, STATUS_AGENDAMENTO
from utils.widgets import (
    btn_primario, btn_secundario, btn_perigo,
    lbl_titulo, lbl_campo, entry_padrao, combo_padrao,
    criar_treeview, preencher_treeview,
    frame_pesquisa, validar_campos,
    mostrar_erro, mostrar_sucesso, confirmar,
)


# ─── Queries ────────────────────────────────

def _listar(filtro=""):
    sql = """
        SELECT a.id, c.nome AS cliente, f.nome AS funcionario,
               a.data_hora, a.status,
               STRING_AGG(s.nome, ', ') AS servicos
        FROM agendamento a
        JOIN cliente c ON c.id = a.cliente_id
        JOIN funcionario f ON f.id = a.funcionario_id
        LEFT JOIN agendamento_servico ags ON ags.agendamento_id = a.id
        LEFT JOIN servico s ON s.id = ags.servico_id
        {where}
        GROUP BY a.id, c.nome, f.nome, a.data_hora, a.status
        ORDER BY a.data_hora DESC
    """
    if filtro:
        return execute_query(
            sql.format(where="WHERE c.nome ILIKE %s OR f.nome ILIKE %s"),
            (f"%{filtro}%", f"%{filtro}%"), fetch=True) or []
    return execute_query(sql.format(where=""), fetch=True) or []


def _inserir(d, servico_ids):
    row = execute_query(
        "INSERT INTO agendamento (cliente_id,funcionario_id,data_hora,status,observacao) "
        "VALUES (%s,%s,%s,%s,%s) RETURNING id",
        (d["cliente_id"], d["funcionario_id"], d["data_hora"], d["status"], d["observacao"]),
        fetch_one=True,
    )
    ag_id = row["id"]
    for sid in servico_ids:
        execute_query(
            "INSERT INTO agendamento_servico (agendamento_id,servico_id) VALUES (%s,%s)",
            (ag_id, sid))


def _atualizar(id_, d, servico_ids):
    execute_query(
        "UPDATE agendamento SET cliente_id=%s,funcionario_id=%s,data_hora=%s,"
        "status=%s,observacao=%s WHERE id=%s",
        (d["cliente_id"], d["funcionario_id"], d["data_hora"],
         d["status"], d["observacao"], id_),
    )
    execute_query("DELETE FROM agendamento_servico WHERE agendamento_id=%s", (id_,))
    for sid in servico_ids:
        execute_query(
            "INSERT INTO agendamento_servico (agendamento_id,servico_id) VALUES (%s,%s)",
            (id_, sid))


def _excluir(id_):
    execute_query("DELETE FROM agendamento WHERE id=%s", (id_,))


def _buscar_por_id(id_):
    ag = execute_query("SELECT * FROM agendamento WHERE id=%s", (id_,), fetch_one=True)
    servs = execute_query(
        "SELECT servico_id FROM agendamento_servico WHERE agendamento_id=%s",
        (id_,), fetch=True) or []
    return ag, [r["servico_id"] for r in servs]


def _clientes():
    return execute_query("SELECT id, nome FROM cliente ORDER BY nome", fetch=True) or []


def _funcionarios():
    return execute_query(
        "SELECT id, nome FROM funcionario WHERE status='Ativo' ORDER BY nome",
        fetch=True) or []


def _servicos():
    return execute_query("SELECT id, nome, preco FROM servico ORDER BY nome", fetch=True) or []


# ─── Tela ────────────────────────────────────

class TelaAgendamentos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["fundo"])
        self._build()
        self._carregar()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["fundo"])
        hdr.pack(fill="x", padx=20, pady=(20, 5))
        lbl_titulo(hdr, "📅 Agendamentos").pack(side="left")

        acoes = tk.Frame(self, bg=COLORS["fundo"])
        acoes.pack(fill="x", padx=20, pady=5)
        btn_primario(acoes, "➕ Novo", self._novo).pack(side="left", padx=3)
        btn_secundario(acoes, "✏️ Editar", self._editar).pack(side="left", padx=3)
        btn_perigo(acoes, "🗑️ Excluir", self._excluir).pack(side="left", padx=3)

        self._var_pesq = frame_pesquisa(self, self._pesquisar, self._carregar)
        tk.Frame(self, bg=COLORS["borda"], height=1).pack(fill="x", padx=10, pady=5)

        colunas = ["ID", "Cliente", "Funcionário", "Data/Hora", "Status", "Serviços"]
        larguras = [50, 140, 130, 130, 80, 240]
        self._tree = criar_treeview(self, colunas, larguras)
        self._tree.column("Serviços", anchor="w")

    def _carregar(self, filtro=""):
        dados = _listar(filtro)
        for item in self._tree.get_children():
            self._tree.delete(item)
        for i, row in enumerate(dados):
            tag = "par" if i % 2 == 0 else "impar"
            status = row.get("status", "")
            if status == "Cancelado":
                tag = "cancelado"
            elif status == "Concluído":
                tag = "concluido"
            self._tree.insert("", "end", values=list(row.values()), tags=(tag,))
        self._tree.tag_configure("cancelado", foreground=COLORS["erro"])
        self._tree.tag_configure("concluido", foreground="#2E7D32")

    def _pesquisar(self, t):
        self._carregar(t.strip())

    def _sel_id(self):
        sel = self._tree.selection()
        if not sel:
            mostrar_erro("Selecione um agendamento.")
            return None
        return self._tree.item(sel[0])["values"][0]

    def _novo(self):
        FormAgendamento(self, None, self._carregar)

    def _editar(self):
        id_ = self._sel_id()
        if id_:
            FormAgendamento(self, id_, self._carregar)

    def _excluir(self):
        id_ = self._sel_id()
        if not id_:
            return
        if confirmar(f"Excluir agendamento ID {id_}?"):
            try:
                _excluir(id_)
                mostrar_sucesso("Agendamento excluído!")
                self._carregar()
            except Exception as e:
                mostrar_erro(f"Erro: {e}")


# ─── Formulário ──────────────────────────────

class FormAgendamento(tk.Toplevel):
    def __init__(self, parent, id_, callback):
        super().__init__(parent)
        self.id_ = id_
        self.callback = callback
        self._edit = id_ is not None
        self.title("Editar Agendamento" if self._edit else "Novo Agendamento")
        self.geometry("600x620")
        self.configure(bg=COLORS["branco"])
        self.resizable(False, False)
        self.grab_set()
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2 - 300
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - 310
        self.geometry(f"+{px}+{py}")
        self._clientes = _clientes()
        self._funcionarios = _funcionarios()
        self._servicos_lista = _servicos()
        self._build()
        if self._edit:
            self._popular()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["rosa_principal"], height=50)
        hdr.pack(fill="x")
        tk.Label(hdr, text=self.title(), font=FONTS["subtitulo"],
                 fg=COLORS["branco"], bg=COLORS["rosa_principal"]).pack(side="left", padx=20, pady=12)

        body = tk.Frame(self, bg=COLORS["branco"], padx=30, pady=10)
        body.pack(fill="both", expand=True)

        # Cliente
        lbl_campo(body, "Cliente *", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
        nomes_cli = [f"{c['id']} – {c['nome']}" for c in self._clientes]
        self._cb_cliente = combo_padrao(body, nomes_cli)
        self._cb_cliente.pack(fill="x")

        # Funcionário
        lbl_campo(body, "Funcionário *", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
        nomes_func = [f"{f['id']} – {f['nome']}" for f in self._funcionarios]
        self._cb_func = combo_padrao(body, nomes_func)
        self._cb_func.pack(fill="x")

        # Data/Hora
        lbl_campo(body, "Data e Hora * (AAAA-MM-DD HH:MM)", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
        self._entry_dt = entry_padrao(body, largura=45)
        self._entry_dt.pack(fill="x")

        # Status
        lbl_campo(body, "Status *", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
        self._cb_status = combo_padrao(body, STATUS_AGENDAMENTO)
        self._cb_status.set(STATUS_AGENDAMENTO[0])
        self._cb_status.pack(fill="x")

        # Observação
        lbl_campo(body, "Observação", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
        self._entry_obs = entry_padrao(body, largura=45)
        self._entry_obs.pack(fill="x")

        # Serviços (multiselect Listbox)
        lbl_campo(body, "Serviços * (Ctrl+Clique para múltiplos)", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
        frame_lb = tk.Frame(body, bg=COLORS["branco"])
        frame_lb.pack(fill="x")
        sb = tk.Scrollbar(frame_lb, orient="vertical")
        self._lb_servicos = tk.Listbox(
            frame_lb, selectmode="multiple", height=5,
            font=FONTS["normal"], fg=COLORS["texto"], bg=COLORS["branco"],
            relief="solid", bd=1, yscrollcommand=sb.set,
            selectbackground=COLORS["azul_suave"],
        )
        sb.config(command=self._lb_servicos.yview)
        for s in self._servicos_lista:
            self._lb_servicos.insert("end", f"{s['id']} – {s['nome']}  (R$ {float(s['preco']):.2f})")
        self._lb_servicos.pack(side="left", fill="x", expand=True)
        sb.pack(side="right", fill="y")

        # Rodapé
        rodape = tk.Frame(self, bg=COLORS["branco"], pady=10)
        rodape.pack(fill="x", padx=30)
        btn_primario(rodape, "💾 Salvar", self._salvar, largura=12).pack(side="right", padx=5)
        btn_secundario(rodape, "Cancelar", self.destroy, largura=12).pack(side="right")

    def _popular(self):
        ag, servico_ids = _buscar_por_id(self.id_)
        if not ag:
            return

        # Setar cliente
        for i, c in enumerate(self._clientes):
            if c["id"] == ag["cliente_id"]:
                self._cb_cliente.current(i)
                break

        # Setar funcionário
        for i, f in enumerate(self._funcionarios):
            if f["id"] == ag["funcionario_id"]:
                self._cb_func.current(i)
                break

        dt = ag.get("data_hora")
        if dt:
            self._entry_dt.insert(0, str(dt)[:16])
        self._cb_status.set(ag.get("status", STATUS_AGENDAMENTO[0]))
        self._entry_obs.insert(0, ag.get("observacao") or "")

        # Marcar serviços
        for i, s in enumerate(self._servicos_lista):
            if s["id"] in servico_ids:
                self._lb_servicos.selection_set(i)

    def _salvar(self):
        cli_sel = self._cb_cliente.get()
        func_sel = self._cb_func.get()
        dt = self._entry_dt.get().strip()
        obs = self._entry_obs.get().strip()
        status = self._cb_status.get()

        if not cli_sel or not func_sel:
            mostrar_erro("Selecione cliente e funcionário.")
            return
        if not dt:
            mostrar_erro("Informe a data e hora do agendamento.")
            return

        idxs = self._lb_servicos.curselection()
        if not idxs:
            mostrar_erro("Selecione pelo menos um serviço.")
            return

        cliente_id = int(cli_sel.split("–")[0].strip())
        func_id = int(func_sel.split("–")[0].strip())
        servico_ids = [self._servicos_lista[i]["id"] for i in idxs]

        d = {
            "cliente_id": cliente_id,
            "funcionario_id": func_id,
            "data_hora": dt,
            "status": status,
            "observacao": obs,
        }
        try:
            if self._edit:
                _atualizar(self.id_, d, servico_ids)
                mostrar_sucesso("Agendamento atualizado!")
            else:
                _inserir(d, servico_ids)
                mostrar_sucesso("Agendamento criado!")
            self.callback()
            self.destroy()
        except Exception as e:
            mostrar_erro(f"Erro: {e}")
