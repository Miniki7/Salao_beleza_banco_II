import tkinter as tk
from database.connection import execute_query
from utils.constants import COLORS, FONTS, FORMAS_PAGAMENTO
from utils.widgets import (
    btn_primario, btn_secundario, btn_perigo,
    lbl_titulo, lbl_campo, entry_padrao, combo_padrao,
    criar_treeview, preencher_treeview,
    frame_pesquisa, validar_campos, validar_positivo,
    mostrar_erro, mostrar_sucesso, confirmar,
)


def _listar(filtro=""):
    sql = """
        SELECT p.id, COALESCE(a.id::text, '-') AS agendamento,
               p.forma_pagamento, p.valor_total, p.observacao, p.data_hora
        FROM pagamento p
        LEFT JOIN agendamento a ON a.id = p.agendamento_id
        {where}
        ORDER BY p.data_hora DESC
    """
    if filtro:
        return execute_query(
            sql.format(where="WHERE p.forma_pagamento ILIKE %s"),
            (f"%{filtro}%",), fetch=True) or []
    return execute_query(sql.format(where=""), fetch=True) or []


def _inserir(d):
    execute_query(
        "INSERT INTO pagamento (agendamento_id,forma_pagamento,valor_total,observacao) "
        "VALUES (%s,%s,%s,%s)",
        (d["agendamento_id"] or None, d["forma_pagamento"],
         float(d["valor_total"]), d["observacao"]),
    )


def _excluir(id_):
    execute_query("DELETE FROM pagamento WHERE id=%s", (id_,))


def _agendamentos_disponiveis():
    return execute_query(
        "SELECT a.id, c.nome AS cliente FROM agendamento a "
        "JOIN cliente c ON c.id = a.cliente_id ORDER BY a.id DESC LIMIT 100",
        fetch=True) or []


class TelaPagamentos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["fundo"])
        self._build()
        self._carregar()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["fundo"])
        hdr.pack(fill="x", padx=20, pady=(20, 5))
        lbl_titulo(hdr, "💳 Pagamentos").pack(side="left")

        acoes = tk.Frame(self, bg=COLORS["fundo"])
        acoes.pack(fill="x", padx=20, pady=5)
        btn_primario(acoes, "➕ Registrar", self._novo).pack(side="left", padx=3)
        btn_perigo(acoes, "🗑️ Excluir", self._excluir).pack(side="left", padx=3)

        self._var_pesq = frame_pesquisa(self, self._pesquisar, self._carregar)
        tk.Frame(self, bg=COLORS["borda"], height=1).pack(fill="x", padx=10, pady=5)

        colunas = ["ID", "Agendamento", "Forma Pgto", "Valor (R$)", "Observação", "Data/Hora"]
        larguras = [50, 90, 130, 100, 180, 140]
        self._tree = criar_treeview(self, colunas, larguras)

    def _carregar(self, filtro=""):
        dados = _listar(filtro)
        for item in self._tree.get_children():
            self._tree.delete(item)
        for i, row in enumerate(dados):
            tag = "par" if i % 2 == 0 else "impar"
            v = list(row.values())
            v[3] = f"R$ {float(v[3]):.2f}"
            self._tree.insert("", "end", values=v, tags=(tag,))

    def _pesquisar(self, t):
        self._carregar(t.strip())

    def _sel_id(self):
        sel = self._tree.selection()
        if not sel:
            mostrar_erro("Selecione um pagamento.")
            return None
        return self._tree.item(sel[0])["values"][0]

    def _novo(self):
        FormPagamento(self, self._carregar)

    def _excluir(self):
        id_ = self._sel_id()
        if not id_:
            return
        if confirmar(f"Excluir pagamento ID {id_}?"):
            try:
                _excluir(id_)
                mostrar_sucesso("Pagamento excluído!")
                self._carregar()
            except Exception as e:
                mostrar_erro(f"Erro: {e}")


class FormPagamento(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Registrar Pagamento")
        self.geometry("480x400")
        self.configure(bg=COLORS["branco"])
        self.resizable(False, False)
        self.grab_set()
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2 - 240
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - 200
        self.geometry(f"+{px}+{py}")
        self._agendamentos = _agendamentos_disponiveis()
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["rosa_principal"], height=50)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Registrar Pagamento", font=FONTS["subtitulo"],
                 fg=COLORS["branco"], bg=COLORS["rosa_principal"]).pack(side="left", padx=20, pady=12)

        body = tk.Frame(self, bg=COLORS["branco"], padx=30, pady=10)
        body.pack(fill="both", expand=True)

        # Agendamento (opcional)
        lbl_campo(body, "Agendamento (opcional)", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
        opcoes_ag = ["– Nenhum –"] + [f"{a['id']} – {a['cliente']}" for a in self._agendamentos]
        self._cb_ag = combo_padrao(body, opcoes_ag)
        self._cb_ag.set(opcoes_ag[0])
        self._cb_ag.pack(fill="x")

        # Forma de pagamento
        lbl_campo(body, "Forma de Pagamento *", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
        self._cb_forma = combo_padrao(body, FORMAS_PAGAMENTO)
        self._cb_forma.set(FORMAS_PAGAMENTO[0])
        self._cb_forma.pack(fill="x")

        # Valor
        lbl_campo(body, "Valor Total (R$) *", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
        self._entry_valor = entry_padrao(body, largura=45)
        self._entry_valor.pack(fill="x")

        # Observação
        lbl_campo(body, "Observação", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
        self._entry_obs = entry_padrao(body, largura=45)
        self._entry_obs.pack(fill="x")

        rodape = tk.Frame(self, bg=COLORS["branco"], pady=10)
        rodape.pack(fill="x", padx=30)
        btn_primario(rodape, "💾 Salvar", self._salvar, largura=12).pack(side="right", padx=5)
        btn_secundario(rodape, "Cancelar", self.destroy, largura=12).pack(side="right")

    def _salvar(self):
        valor = self._entry_valor.get().strip()
        ok, msg = validar_positivo(valor, "Valor Total")
        if not ok:
            mostrar_erro(msg)
            return

        ag_sel = self._cb_ag.get()
        ag_id = None
        if ag_sel and not ag_sel.startswith("–"):
            ag_id = int(ag_sel.split("–")[0].strip())

        d = {
            "agendamento_id": ag_id,
            "forma_pagamento": self._cb_forma.get(),
            "valor_total": valor,
            "observacao": self._entry_obs.get().strip(),
        }
        try:
            _inserir(d)
            mostrar_sucesso("Pagamento registrado!")
            self.callback()
            self.destroy()
        except Exception as e:
            mostrar_erro(f"Erro: {e}")
