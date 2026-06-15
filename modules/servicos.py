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
    if filtro:
        return execute_query(
            "SELECT id, nome, descricao, preco, tempo_estimado FROM servico "
            "WHERE nome ILIKE %s ORDER BY nome",
            (f"%{filtro}%",), fetch=True) or []
    return execute_query(
        "SELECT id, nome, descricao, preco, tempo_estimado FROM servico ORDER BY nome",
        fetch=True) or []


def _inserir(d):
    execute_query(
        "INSERT INTO servico (nome,descricao,preco,tempo_estimado) VALUES (%s,%s,%s,%s)",
        (d["nome"], d["descricao"], float(d["preco"]),
         int(d["tempo_estimado"]) if d["tempo_estimado"] else None),
    )


def _atualizar(id_, d):
    execute_query(
        "UPDATE servico SET nome=%s,descricao=%s,preco=%s,tempo_estimado=%s WHERE id=%s",
        (d["nome"], d["descricao"], float(d["preco"]),
         int(d["tempo_estimado"]) if d["tempo_estimado"] else None, id_),
    )


def _excluir(id_):
    execute_query("DELETE FROM servico WHERE id=%s", (id_,))


def _buscar_por_id(id_):
    return execute_query("SELECT * FROM servico WHERE id=%s", (id_,), fetch_one=True)


def listar_todos():
    return execute_query("SELECT id, nome, preco FROM servico ORDER BY nome", fetch=True) or []


class TelaServicos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["fundo"])
        self._build()
        self._carregar()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["fundo"])
        hdr.pack(fill="x", padx=20, pady=(20, 5))
        lbl_titulo(hdr, "✂️ Serviços").pack(side="left")

        acoes = tk.Frame(self, bg=COLORS["fundo"])
        acoes.pack(fill="x", padx=20, pady=5)
        btn_primario(acoes, "➕ Adicionar", self._novo).pack(side="left", padx=3)
        btn_secundario(acoes, "✏️ Editar", self._editar).pack(side="left", padx=3)
        btn_perigo(acoes, "🗑️ Excluir", self._excluir).pack(side="left", padx=3)

        self._var_pesq = frame_pesquisa(self, self._pesquisar, self._carregar)
        tk.Frame(self, bg=COLORS["borda"], height=1).pack(fill="x", padx=10, pady=5)

        colunas = ["ID", "Nome", "Descrição", "Preço (R$)", "Tempo (min)"]
        larguras = [50, 180, 250, 90, 90]
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
            mostrar_erro("Selecione um serviço.")
            return None
        return self._tree.item(sel[0])["values"][0]

    def _novo(self):
        FormServico(self, None, self._carregar)

    def _editar(self):
        id_ = self._sel_id()
        if id_:
            FormServico(self, id_, self._carregar)

    def _excluir(self):
        id_ = self._sel_id()
        if not id_:
            return
        if confirmar(f"Excluir serviço ID {id_}?"):
            try:
                _excluir(id_)
                mostrar_sucesso("Serviço excluído!")
                self._carregar()
            except Exception as e:
                mostrar_erro(f"Erro: {e}")


class FormServico(tk.Toplevel):
    def __init__(self, parent, id_, callback):
        super().__init__(parent)
        self.id_ = id_
        self.callback = callback
        self._edit = id_ is not None
        self.title("Editar Serviço" if self._edit else "Novo Serviço")
        self.geometry("480x400")
        self.configure(bg=COLORS["branco"])
        self.resizable(False, False)
        self.grab_set()
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2 - 240
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - 200
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
            ("Nome *", "nome"), ("Descrição", "descricao"),
            ("Preço (R$) *", "preco"), ("Tempo Estimado (minutos)", "tempo_estimado"),
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
            v = d.get(k) or ""
            e.delete(0, "end")
            e.insert(0, str(v))

    def _salvar(self):
        d = {k: e.get().strip() for k, e in self._entries.items()}
        ok, msg = validar_campos({"Nome": d["nome"], "Preço": d["preco"]})
        if not ok:
            mostrar_erro(msg)
            return
        ok, msg = validar_positivo(d["preco"], "Preço")
        if not ok:
            mostrar_erro(msg)
            return
        try:
            if self._edit:
                _atualizar(self.id_, d)
                mostrar_sucesso("Serviço atualizado!")
            else:
                _inserir(d)
                mostrar_sucesso("Serviço cadastrado!")
            self.callback()
            self.destroy()
        except Exception as e:
            mostrar_erro(f"Erro: {e}")
