import tkinter as tk
from database.connection import execute_query
from utils.constants import COLORS, FONTS, STATUS_FUNCIONARIO
from utils.widgets import (
    btn_primario, btn_secundario, btn_perigo,
    lbl_titulo, lbl_campo, entry_padrao, combo_padrao,
    criar_treeview, preencher_treeview,
    frame_pesquisa, validar_campos,
    formatar_cpf, formatar_telefone,
    mostrar_erro, mostrar_sucesso, confirmar,
)


def _listar(filtro=""):
    if filtro:
        return execute_query(
            "SELECT id, nome, cpf, telefone, email, status FROM funcionario "
            "WHERE nome ILIKE %s OR cpf ILIKE %s ORDER BY nome",
            (f"%{filtro}%", f"%{filtro}%"), fetch=True,
        ) or []
    return execute_query(
        "SELECT id, nome, cpf, telefone, email, status FROM funcionario ORDER BY nome",
        fetch=True,
    ) or []


def _inserir(d):
    execute_query(
        "INSERT INTO funcionario (nome,email,senha,cpf,telefone,endereco,data_nascimento,status) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (d["nome"], d["email"], d["senha"], d["cpf"],
         d["telefone"], d["endereco"], d["data_nascimento"] or None, d["status"]),
    )


def _atualizar(id_, d):
    execute_query(
        "UPDATE funcionario SET nome=%s,email=%s,senha=%s,cpf=%s,telefone=%s,"
        "endereco=%s,data_nascimento=%s,status=%s WHERE id=%s",
        (d["nome"], d["email"], d["senha"], d["cpf"],
         d["telefone"], d["endereco"], d["data_nascimento"] or None, d["status"], id_),
    )


def _excluir(id_):
    execute_query("DELETE FROM funcionario WHERE id=%s", (id_,))


def _buscar_por_id(id_):
    return execute_query("SELECT * FROM funcionario WHERE id=%s", (id_,), fetch_one=True)


class TelaFuncionarios(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["fundo"])
        self._build()
        self._carregar()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["fundo"])
        hdr.pack(fill="x", padx=20, pady=(20, 5))
        lbl_titulo(hdr, "👩‍💼 Funcionários").pack(side="left")

        acoes = tk.Frame(self, bg=COLORS["fundo"])
        acoes.pack(fill="x", padx=20, pady=5)
        btn_primario(acoes, "➕ Adicionar", self._novo).pack(side="left", padx=3)
        btn_secundario(acoes, "✏️ Editar", self._editar).pack(side="left", padx=3)
        btn_perigo(acoes, "🗑️ Excluir", self._excluir).pack(side="left", padx=3)

        self._var_pesq = frame_pesquisa(self, self._pesquisar, self._carregar)
        tk.Frame(self, bg=COLORS["borda"], height=1).pack(fill="x", padx=10, pady=5)

        colunas = ["ID", "Nome", "CPF", "Telefone", "Email", "Status"]
        larguras = [50, 180, 120, 120, 180, 80]
        self._tree = criar_treeview(self, colunas, larguras)

    def _carregar(self, filtro=""):
        preencher_treeview(self._tree, _listar(filtro))

    def _pesquisar(self, t):
        self._carregar(t.strip())

    def _sel_id(self):
        sel = self._tree.selection()
        if not sel:
            mostrar_erro("Selecione um funcionário na tabela.")
            return None
        return self._tree.item(sel[0])["values"][0]

    def _novo(self):
        FormFuncionario(self, None, self._carregar)

    def _editar(self):
        id_ = self._sel_id()
        if id_:
            FormFuncionario(self, id_, self._carregar)

    def _excluir(self):
        id_ = self._sel_id()
        if not id_:
            return
        if confirmar(f"Excluir funcionário ID {id_}?"):
            try:
                _excluir(id_)
                mostrar_sucesso("Funcionário excluído!")
                self._carregar()
            except Exception as e:
                mostrar_erro(f"Erro: {e}")


class FormFuncionario(tk.Toplevel):
    def __init__(self, parent, id_, callback):
        super().__init__(parent)
        self.id_ = id_
        self.callback = callback
        self._edit = id_ is not None
        self.title("Editar Funcionário" if self._edit else "Novo Funcionário")
        self.geometry("520x600")
        self.configure(bg=COLORS["branco"])
        self.resizable(False, False)
        self.grab_set()
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2 - 260
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - 300
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
            ("Nome *", "nome"), ("Email", "email"), ("Senha", "senha"),
            ("CPF *", "cpf"), ("Telefone", "telefone"), ("Endereço", "endereco"),
            ("Data de Nascimento (AAAA-MM-DD)", "data_nascimento"),
        ]:
            lbl_campo(body, label, bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
            e = entry_padrao(body, largura=45)
            e.pack(fill="x")
            self._entries[key] = e

        lbl_campo(body, "Status *", bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
        self._status = combo_padrao(body, STATUS_FUNCIONARIO)
        self._status.set(STATUS_FUNCIONARIO[0])
        self._status.pack(fill="x")

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
        self._status.set(d.get("status", STATUS_FUNCIONARIO[0]))

    def _salvar(self):
        d = {k: e.get().strip() for k, e in self._entries.items()}
        d["status"] = self._status.get()
        ok, msg = validar_campos({"Nome": d["nome"], "CPF": d["cpf"]})
        if not ok:
            mostrar_erro(msg)
            return
        d["cpf"] = formatar_cpf(d["cpf"])
        if d["telefone"]:
            d["telefone"] = formatar_telefone(d["telefone"])
        try:
            if self._edit:
                _atualizar(self.id_, d)
                mostrar_sucesso("Funcionário atualizado!")
            else:
                _inserir(d)
                mostrar_sucesso("Funcionário cadastrado!")
            self.callback()
            self.destroy()
        except Exception as e:
            mostrar_erro(f"Erro ao salvar: {e}")
