import tkinter as tk
from tkinter import ttk
from database.connection import execute_query
from utils.constants import COLORS, FONTS, STATUS_VENDA
from utils.widgets import (
    btn_primario, btn_secundario, btn_perigo, btn_sucesso,
    lbl_titulo, lbl_campo, entry_padrao, combo_padrao,
    criar_treeview, preencher_treeview,
    frame_pesquisa, validar_positivo,
    mostrar_erro, mostrar_sucesso, confirmar,
)


# ─── Queries ────────────────────────────────

def _listar(filtro=""):
    sql = """
        SELECT v.id, c.nome AS cliente, f.nome AS funcionario,
               v.data_venda, v.status,
               COALESCE(SUM(iv.quantidade * iv.preco_unitario), 0) AS total
        FROM venda v
        JOIN cliente c ON c.id = v.cliente_id
        JOIN funcionario f ON f.id = v.funcionario_id
        LEFT JOIN item_venda iv ON iv.venda_id = v.id
        {where}
        GROUP BY v.id, c.nome, f.nome, v.data_venda, v.status
        ORDER BY v.data_venda DESC
    """
    if filtro:
        return execute_query(
            sql.format(where="WHERE c.nome ILIKE %s OR f.nome ILIKE %s"),
            (f"%{filtro}%", f"%{filtro}%"), fetch=True) or []
    return execute_query(sql.format(where=""), fetch=True) or []


def _criar_venda(cliente_id, funcionario_id):
    row = execute_query(
        "INSERT INTO venda (cliente_id,funcionario_id) VALUES (%s,%s) RETURNING id",
        (cliente_id, funcionario_id), fetch_one=True)
    return row["id"]


def _inserir_item(venda_id, produto_id, quantidade, preco_unit):
    execute_query(
        "INSERT INTO item_venda (venda_id,produto_id,quantidade,preco_unitario) "
        "VALUES (%s,%s,%s,%s)",
        (venda_id, produto_id, quantidade, preco_unit))


def _itens_venda(venda_id):
    return execute_query(
        "SELECT iv.id, p.nome, iv.quantidade, iv.preco_unitario, "
        "(iv.quantidade * iv.preco_unitario) AS subtotal "
        "FROM item_venda iv JOIN produto p ON p.id = iv.produto_id "
        "WHERE iv.venda_id=%s",
        (venda_id,), fetch=True) or []


def _cancelar(venda_id):
    execute_query("UPDATE venda SET status='Cancelada' WHERE id=%s", (venda_id,))


def _reativar(venda_id):
    execute_query("UPDATE venda SET status='Ativa' WHERE id=%s", (venda_id,))


def _excluir_item(item_id):
    execute_query("DELETE FROM item_venda WHERE id=%s", (item_id,))


def _clientes():
    return execute_query("SELECT id, nome FROM cliente ORDER BY nome", fetch=True) or []


def _funcionarios():
    return execute_query(
        "SELECT id, nome FROM funcionario WHERE status='Ativo' ORDER BY nome",
        fetch=True) or []


def _produtos():
    return execute_query(
        "SELECT id, nome, preco, estoque FROM produto WHERE estoque > 0 ORDER BY nome",
        fetch=True) or []


def _venda_por_id(id_):
    return execute_query("SELECT * FROM venda WHERE id=%s", (id_,), fetch_one=True)


# ─── Tela Principal ─────────────────────────

class TelaVendas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["fundo"])
        self._build()
        self._carregar()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["fundo"])
        hdr.pack(fill="x", padx=20, pady=(20, 5))
        lbl_titulo(hdr, "🛒 Vendas").pack(side="left")

        acoes = tk.Frame(self, bg=COLORS["fundo"])
        acoes.pack(fill="x", padx=20, pady=5)
        btn_primario(acoes, "➕ Nova Venda", self._nova).pack(side="left", padx=3)
        btn_secundario(acoes, "📋 Detalhes", self._detalhes).pack(side="left", padx=3)
        btn_perigo(acoes, "🚫 Cancelar", self._cancelar).pack(side="left", padx=3)
        btn_sucesso(acoes, "✅ Reativar", self._reativar, largura=10).pack(side="left", padx=3)

        self._var_pesq = frame_pesquisa(self, self._pesquisar, self._carregar)
        tk.Frame(self, bg=COLORS["borda"], height=1).pack(fill="x", padx=10, pady=5)

        colunas = ["ID", "Cliente", "Funcionário", "Data", "Status", "Total (R$)"]
        larguras = [50, 160, 140, 130, 80, 100]
        self._tree = criar_treeview(self, colunas, larguras)

    def _carregar(self, filtro=""):
        dados = _listar(filtro)
        for item in self._tree.get_children():
            self._tree.delete(item)
        for i, row in enumerate(dados):
            tag = "par" if i % 2 == 0 else "impar"
            v = list(row.values())
            v[5] = f"R$ {float(v[5]):.2f}"
            if row.get("status") == "Cancelada":
                tag = "cancelada"
            self._tree.insert("", "end", values=v, tags=(tag,))
        self._tree.tag_configure("cancelada", foreground=COLORS["erro"])

    def _pesquisar(self, t):
        self._carregar(t.strip())

    def _sel_id(self):
        sel = self._tree.selection()
        if not sel:
            mostrar_erro("Selecione uma venda.")
            return None
        return self._tree.item(sel[0])["values"][0]

    def _nova(self):
        FormVenda(self, self._carregar)

    def _detalhes(self):
        id_ = self._sel_id()
        if id_:
            DetalheVenda(self, id_)

    def _cancelar(self):
        id_ = self._sel_id()
        if not id_:
            return
        v = _venda_por_id(id_)
        if v and v["status"] == "Cancelada":
            mostrar_erro("Esta venda já está cancelada.")
            return
        if confirmar(f"Cancelar venda ID {id_}? O estoque será restaurado."):
            try:
                _cancelar(id_)
                mostrar_sucesso("Venda cancelada e estoque restaurado!")
                self._carregar()
            except Exception as e:
                mostrar_erro(f"Erro: {e}")

    def _reativar(self):
        id_ = self._sel_id()
        if not id_:
            return
        v = _venda_por_id(id_)
        if v and v["status"] == "Ativa":
            mostrar_erro("Esta venda já está ativa.")
            return
        if confirmar(f"Reativar venda ID {id_}?"):
            try:
                _reativar(id_)
                mostrar_sucesso("Venda reativada!")
                self._carregar()
            except Exception as e:
                mostrar_erro(f"Erro: {e}")


# ─── Formulário Nova Venda ───────────────────

class FormVenda(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Nova Venda")
        self.geometry("700x620")
        self.configure(bg=COLORS["branco"])
        self.resizable(False, False)
        self.grab_set()
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2 - 350
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - 310
        self.geometry(f"+{px}+{py}")
        self._clientes = _clientes()
        self._funcionarios = _funcionarios()
        self._produtos_lista = _produtos()
        self._itens = []          # lista de dicts temporária
        self._venda_id = None
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["rosa_principal"], height=50)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Nova Venda", font=FONTS["subtitulo"],
                 fg=COLORS["branco"], bg=COLORS["rosa_principal"]).pack(side="left", padx=20, pady=12)

        body = tk.Frame(self, bg=COLORS["branco"], padx=20, pady=10)
        body.pack(fill="both", expand=True)

        # Cliente / Funcionário
        topo = tk.Frame(body, bg=COLORS["branco"])
        topo.pack(fill="x")

        col1 = tk.Frame(topo, bg=COLORS["branco"])
        col1.pack(side="left", expand=True, fill="x", padx=(0, 10))
        lbl_campo(col1, "Cliente *", bg=COLORS["branco"]).pack(anchor="w")
        nomes_cli = [f"{c['id']} – {c['nome']}" for c in self._clientes]
        self._cb_cli = combo_padrao(col1, nomes_cli, largura=28)
        self._cb_cli.pack(fill="x")

        col2 = tk.Frame(topo, bg=COLORS["branco"])
        col2.pack(side="left", expand=True, fill="x")
        lbl_campo(col2, "Funcionário *", bg=COLORS["branco"]).pack(anchor="w")
        nomes_func = [f"{f['id']} – {f['nome']}" for f in self._funcionarios]
        self._cb_func = combo_padrao(col2, nomes_func, largura=28)
        self._cb_func.pack(fill="x")

        tk.Frame(body, bg=COLORS["borda"], height=1).pack(fill="x", pady=10)

        # Adicionar produto
        lbl_campo(body, "Adicionar Produto", bg=COLORS["branco"]).pack(anchor="w")
        prod_frame = tk.Frame(body, bg=COLORS["branco"])
        prod_frame.pack(fill="x", pady=5)

        nomes_prod = [f"{p['id']} – {p['nome']}  (R${float(p['preco']):.2f} | est:{p['estoque']})"
                      for p in self._produtos_lista]
        self._cb_prod = combo_padrao(prod_frame, nomes_prod, largura=38)
        self._cb_prod.pack(side="left", padx=(0, 8))

        lbl_campo(prod_frame, "Qtd:", bg=COLORS["branco"]).pack(side="left")
        self._entry_qtd = entry_padrao(prod_frame, largura=5)
        self._entry_qtd.insert(0, "1")
        self._entry_qtd.pack(side="left", padx=5)

        btn_sucesso(prod_frame, "➕ Add", self._add_item, largura=8).pack(side="left")

        # Lista de itens
        lbl_campo(body, "Itens da Venda:", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 2))
        cols = ["Produto", "Qtd", "Preço Unit.", "Subtotal"]
        larg = [220, 60, 100, 100]
        self._tree_itens = criar_treeview(body, cols, larg)
        # Remover item
        btn_perigo(body, "🗑️ Remover Item", self._remover_item, largura=16).pack(anchor="e", padx=10, pady=2)

        # Total
        self._lbl_total = tk.Label(body, text="Total: R$ 0,00",
                                    font=FONTS["subtitulo"], fg=COLORS["rosa_principal"],
                                    bg=COLORS["branco"])
        self._lbl_total.pack(anchor="e", pady=5)

        # Rodapé
        rodape = tk.Frame(self, bg=COLORS["branco"], pady=10)
        rodape.pack(fill="x", padx=20)
        btn_primario(rodape, "✅ Finalizar Venda", self._finalizar, largura=18).pack(side="right", padx=5)
        btn_secundario(rodape, "Cancelar", self.destroy, largura=12).pack(side="right")

    def _add_item(self):
        prod_sel = self._cb_prod.get()
        qtd_str = self._entry_qtd.get().strip()
        if not prod_sel:
            mostrar_erro("Selecione um produto.")
            return
        try:
            qtd = int(qtd_str)
            if qtd <= 0:
                raise ValueError
        except ValueError:
            mostrar_erro("Quantidade deve ser um número inteiro positivo.")
            return
        prod_id = int(prod_sel.split("–")[0].strip())
        prod = next((p for p in self._produtos_lista if p["id"] == prod_id), None)
        if not prod:
            mostrar_erro("Produto não encontrado.")
            return
        if qtd > prod["estoque"]:
            mostrar_erro(f"Estoque insuficiente. Disponível: {prod['estoque']}")
            return
        subtotal = qtd * float(prod["preco"])
        self._itens.append({
            "produto_id": prod["id"],
            "nome": prod["nome"],
            "quantidade": qtd,
            "preco_unitario": float(prod["preco"]),
            "subtotal": subtotal,
        })
        self._atualizar_itens()

    def _atualizar_itens(self):
        for item in self._tree_itens.get_children():
            self._tree_itens.delete(item)
        total = 0
        for i, it in enumerate(self._itens):
            tag = "par" if i % 2 == 0 else "impar"
            self._tree_itens.insert("", "end", values=[
                it["nome"], it["quantidade"],
                f"R$ {it['preco_unitario']:.2f}",
                f"R$ {it['subtotal']:.2f}"
            ], tags=(tag,))
            total += it["subtotal"]
        self._lbl_total.config(text=f"Total: R$ {total:.2f}")

    def _remover_item(self):
        sel = self._tree_itens.selection()
        if not sel:
            mostrar_erro("Selecione um item para remover.")
            return
        idx = self._tree_itens.index(sel[0])
        self._itens.pop(idx)
        self._atualizar_itens()

    def _finalizar(self):
        cli_sel = self._cb_cli.get()
        func_sel = self._cb_func.get()
        if not cli_sel or not func_sel:
            mostrar_erro("Selecione cliente e funcionário.")
            return
        if not self._itens:
            mostrar_erro("Adicione pelo menos um produto.")
            return
        cliente_id = int(cli_sel.split("–")[0].strip())
        func_id = int(func_sel.split("–")[0].strip())
        try:
            venda_id = _criar_venda(cliente_id, func_id)
            for it in self._itens:
                _inserir_item(venda_id, it["produto_id"], it["quantidade"], it["preco_unitario"])
            mostrar_sucesso(f"Venda #{venda_id} registrada com sucesso!\nEstoque atualizado automaticamente.")
            self.callback()
            self.destroy()
        except Exception as e:
            mostrar_erro(f"Erro ao registrar venda: {e}")


# ─── Detalhe da Venda ────────────────────────

class DetalheVenda(tk.Toplevel):
    def __init__(self, parent, venda_id):
        super().__init__(parent)
        self.title(f"Detalhes – Venda #{venda_id}")
        self.geometry("550x400")
        self.configure(bg=COLORS["branco"])
        self.resizable(False, False)
        self.grab_set()
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2 - 275
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - 200
        self.geometry(f"+{px}+{py}")

        hdr = tk.Frame(self, bg=COLORS["rosa_principal"], height=50)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"Detalhes – Venda #{venda_id}", font=FONTS["subtitulo"],
                 fg=COLORS["branco"], bg=COLORS["rosa_principal"]).pack(side="left", padx=20, pady=12)

        body = tk.Frame(self, bg=COLORS["branco"], padx=20, pady=10)
        body.pack(fill="both", expand=True)

        colunas = ["Produto", "Qtd", "Preço Unit.", "Subtotal"]
        larguras = [200, 60, 110, 110]
        tree = criar_treeview(body, colunas, larguras)

        itens = _itens_venda(venda_id)
        total = 0
        for i, it in enumerate(itens):
            tag = "par" if i % 2 == 0 else "impar"
            sub = float(it["subtotal"])
            tree.insert("", "end", values=[
                it["nome"], it["quantidade"],
                f"R$ {float(it['preco_unitario']):.2f}",
                f"R$ {sub:.2f}"
            ], tags=(tag,))
            total += sub

        tk.Label(body, text=f"Total: R$ {total:.2f}", font=FONTS["subtitulo"],
                  fg=COLORS["rosa_principal"], bg=COLORS["branco"]).pack(anchor="e", pady=5)

        btn_secundario(self, "Fechar", self.destroy, largura=10).pack(pady=8)
