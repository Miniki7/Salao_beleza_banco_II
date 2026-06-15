import tkinter as tk
from database.connection import execute_query
from utils.constants import COLORS, FONTS
from utils.widgets import (
    btn_primario, btn_secundario, btn_perigo,
    lbl_titulo, lbl_campo, entry_padrao,
    criar_treeview, preencher_treeview,
    frame_pesquisa, validar_campos, validar_positivo,
    mostrar_erro, mostrar_sucesso, confirmar,
)


def _listar(filtro=""):
    sql = ("SELECT id, nome, marca, preco, estoque, estoque_minimo, data_cadastro "
           "FROM produto WHERE nome ILIKE %s OR marca ILIKE %s ORDER BY nome")
    if filtro:
        return execute_query(sql, (f"%{filtro}%", f"%{filtro}%"), fetch=True) or []
    return execute_query(
        "SELECT id, nome, marca, preco, estoque, estoque_minimo, data_cadastro "
        "FROM produto ORDER BY nome", fetch=True) or []


def _inserir(d):
    execute_query(
        "INSERT INTO produto (nome,marca,observacao,preco,estoque,estoque_minimo) "
        "VALUES (%s,%s,%s,%s,%s,%s)",
        (d["nome"], d["marca"], d["observacao"],
         float(d["preco"]), int(d["estoque"]), int(d["estoque_minimo"])),
    )


def _atualizar(id_, d):
    execute_query(
        "UPDATE produto SET nome=%s,marca=%s,observacao=%s,preco=%s,"
        "estoque=%s,estoque_minimo=%s WHERE id=%s",
        (d["nome"], d["marca"], d["observacao"],
         float(d["preco"]), int(d["estoque"]), int(d["estoque_minimo"]), id_),
    )


def _excluir(id_):
    execute_query("DELETE FROM produto WHERE id=%s", (id_,))


def _buscar_por_id(id_):
    return execute_query("SELECT * FROM produto WHERE id=%s", (id_,), fetch_one=True)


def listar_alertas():
    return execute_query(
        "SELECT nome, estoque, estoque_minimo FROM produto WHERE estoque <= estoque_minimo",
        fetch=True) or []


class TelaProdutos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["fundo"])
        self._build()
        self._carregar()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["fundo"])
        hdr.pack(fill="x", padx=20, pady=(20, 5))
        lbl_titulo(hdr, "📦 Produtos").pack(side="left")

        acoes = tk.Frame(self, bg=COLORS["fundo"])
        acoes.pack(fill="x", padx=20, pady=5)
        btn_primario(acoes, "➕ Adicionar", self._novo).pack(side="left", padx=3)
        btn_secundario(acoes, "✏️ Editar", self._editar).pack(side="left", padx=3)
        btn_perigo(acoes, "🗑️ Excluir", self._excluir).pack(side="left", padx=3)
        btn_secundario(acoes, "⚠️ Alertas", self._alertas, largura=10).pack(side="left", padx=10)

        self._var_pesq = frame_pesquisa(self, self._pesquisar, self._carregar)
        tk.Frame(self, bg=COLORS["borda"], height=1).pack(fill="x", padx=10, pady=5)

        colunas = ["ID", "Nome", "Marca", "Preço (R$)", "Estoque", "Est. Mín.", "Cadastro"]
        larguras = [50, 160, 120, 90, 70, 70, 120]
        self._tree = criar_treeview(self, colunas, larguras)

    def _carregar(self, filtro=""):
        dados = _listar(filtro)
        # Destacar itens com estoque baixo
        for item in self._tree.get_children():
            self._tree.delete(item)
        for i, row in enumerate(dados):
            tag = "par" if i % 2 == 0 else "impar"
            values = list(row.values())
            # Formata preço
            values[3] = f"R$ {float(values[3]):.2f}"
            estoque = int(values[4])
            est_min = int(values[5])
            if estoque <= est_min:
                tag = "alerta"
            self._tree.insert("", "end", values=values, tags=(tag,))
        self._tree.tag_configure("alerta", background="#FFE4B5", foreground="#8B4513")

    def _pesquisar(self, t):
        self._carregar(t.strip())

    def _sel_id(self):
        sel = self._tree.selection()
        if not sel:
            mostrar_erro("Selecione um produto.")
            return None
        return self._tree.item(sel[0])["values"][0]

    def _novo(self):
        FormProduto(self, None, self._carregar)

    def _editar(self):
        id_ = self._sel_id()
        if id_:
            FormProduto(self, id_, self._carregar)

    def _excluir(self):
        id_ = self._sel_id()
        if not id_:
            return
        if confirmar(f"Excluir produto ID {id_}?"):
            try:
                _excluir(id_)
                mostrar_sucesso("Produto excluído!")
                self._carregar()
            except Exception as e:
                mostrar_erro(f"Erro: {e}")

    def _alertas(self):
        itens = listar_alertas()
        if not itens:
            mostrar_sucesso("Nenhum produto com estoque baixo! ✅")
            return
        msg = "⚠️ Produtos com estoque baixo ou zerado:\n\n"
        for p in itens:
            msg += f"• {p['nome']}: {p['estoque']} un. (mín: {p['estoque_minimo']})\n"
        from tkinter import messagebox
        messagebox.showwarning("Alerta de Estoque", msg)


class FormProduto(tk.Toplevel):
    def __init__(self, parent, id_, callback):
        super().__init__(parent)
        self.id_ = id_
        self.callback = callback
        self._edit = id_ is not None
        self.title("Editar Produto" if self._edit else "Novo Produto")
        self.geometry("500x520")
        self.configure(bg=COLORS["branco"])
        self.resizable(False, False)
        self.grab_set()
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2 - 250
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - 260
        self.geometry(f"+{px}+{py}")
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

        self._entries = {}
        for label, key in [
            ("Nome *", "nome"), ("Marca", "marca"),
            ("Observação", "observacao"), ("Preço (R$) *", "preco"),
            ("Estoque *", "estoque"), ("Estoque Mínimo", "estoque_minimo"),
        ]:
            lbl_campo(body, label, bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
            e = entry_padrao(body, largura=45)
            e.pack(fill="x")
            self._entries[key] = e

        rodape = tk.Frame(self, bg=COLORS["branco"], pady=10)
        rodape.pack(fill="x", padx=30)
        btn_primario(rodape, "💾 Salvar", self._salvar, largura=12).pack(side="right", padx=5)
        btn_secundario(rodape, "Cancelar", self.destroy, largura=12).pack(side="right")

    def _popular(self):
        d = _buscar_por_id(self.id_)
        if not d:
            return
        for k, e in self._entries.items():
            v = d.get(k)
            if v is None:
                v = ""
            e.delete(0, "end")
            e.insert(0, str(v))

    def _salvar(self):
        d = {k: e.get().strip() for k, e in self._entries.items()}
        ok, msg = validar_campos({"Nome": d["nome"], "Preço": d["preco"], "Estoque": d["estoque"]})
        if not ok:
            mostrar_erro(msg)
            return
        ok, msg = validar_positivo(d["preco"], "Preço")
        if not ok:
            mostrar_erro(msg)
            return
        try:
            est = int(d["estoque"])
            if est < 0:
                mostrar_erro("Estoque não pode ser negativo.")
                return
        except ValueError:
            mostrar_erro("Estoque deve ser um número inteiro.")
            return
        try:
            if self._edit:
                _atualizar(self.id_, d)
                mostrar_sucesso("Produto atualizado!")
            else:
                _inserir(d)
                mostrar_sucesso("Produto cadastrado!")
            self.callback()
            self.destroy()
        except Exception as e:
            mostrar_erro(f"Erro ao salvar: {e}")
