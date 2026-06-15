import tkinter as tk
from tkinter import ttk
from datetime import date
from database.connection import execute_query
from utils.constants import COLORS, FONTS
from utils.widgets import (
    btn_primario, btn_secundario, btn_perigo,
    lbl_titulo, lbl_campo, entry_padrao,
    criar_treeview, preencher_treeview,
    janela_modal, frame_pesquisa,
    validar_campos, formatar_cpf, formatar_telefone,
    mostrar_erro, mostrar_sucesso, confirmar,
)


# ─── Queries ────────────────────────────────

def _listar(filtro=""):
    if filtro:
        return execute_query(
            "SELECT id, nome, cpf, telefone, email, data_nascimento, data_cadastro "
            "FROM cliente WHERE nome ILIKE %s OR cpf ILIKE %s ORDER BY nome",
            (f"%{filtro}%", f"%{filtro}%"), fetch=True,
        ) or []
    return execute_query(
        "SELECT id, nome, cpf, telefone, email, data_nascimento, data_cadastro "
        "FROM cliente ORDER BY nome",
        fetch=True,
    ) or []


def _inserir(d):
    execute_query(
        "INSERT INTO cliente (nome,email,senha,cpf,telefone,endereco,data_nascimento) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (d["nome"], d["email"], d["senha"], d["cpf"],
         d["telefone"], d["endereco"], d["data_nascimento"] or None),
    )


def _atualizar(id_, d):
    execute_query(
        "UPDATE cliente SET nome=%s,email=%s,senha=%s,cpf=%s,telefone=%s,"
        "endereco=%s,data_nascimento=%s WHERE id=%s",
        (d["nome"], d["email"], d["senha"], d["cpf"],
         d["telefone"], d["endereco"], d["data_nascimento"] or None, id_),
    )


def _excluir(id_):
    execute_query("DELETE FROM cliente WHERE id=%s", (id_,))


def _buscar_por_id(id_):
    return execute_query(
        "SELECT * FROM cliente WHERE id=%s", (id_,), fetch_one=True,
    )


# ─── Tela Principal ─────────────────────────

class TelaClientes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["fundo"])
        self._build()
        self._carregar()

    def _build(self):
        # Cabeçalho
        hdr = tk.Frame(self, bg=COLORS["fundo"])
        hdr.pack(fill="x", padx=20, pady=(20, 5))
        lbl_titulo(hdr, "👤 Clientes").pack(side="left")

        # Botões de ação
        acoes = tk.Frame(self, bg=COLORS["fundo"])
        acoes.pack(fill="x", padx=20, pady=5)
        btn_primario(acoes, "➕ Adicionar", self._abrir_form_novo).pack(side="left", padx=3)
        btn_secundario(acoes, "✏️ Editar", self._editar).pack(side="left", padx=3)
        btn_perigo(acoes, "🗑️ Excluir", self._excluir).pack(side="left", padx=3)

        # Pesquisa
        self._var_pesq = frame_pesquisa(self, self._pesquisar, self._carregar)

        # Separador
        tk.Frame(self, bg=COLORS["borda"], height=1).pack(fill="x", padx=10, pady=5)

        # Treeview
        colunas = ["ID", "Nome", "CPF", "Telefone", "Email", "Nascimento", "Cadastro"]
        larguras = [50, 180, 120, 120, 180, 100, 130]
        self._tree = criar_treeview(self, colunas, larguras)

    def _carregar(self, filtro=""):
        dados = _listar(filtro)
        preencher_treeview(self._tree, dados)

    def _pesquisar(self, texto):
        self._carregar(texto.strip())

    def _selecao_id(self):
        sel = self._tree.selection()
        if not sel:
            mostrar_erro("Selecione um cliente na tabela.")
            return None
        return self._tree.item(sel[0])["values"][0]

    def _abrir_form_novo(self):
        FormCliente(self, None, self._carregar)

    def _editar(self):
        id_ = self._selecao_id()
        if id_:
            FormCliente(self, id_, self._carregar)

    def _excluir(self):
        id_ = self._selecao_id()
        if not id_:
            return
        if confirmar(f"Excluir cliente ID {id_}? Esta ação não pode ser desfeita."):
            try:
                _excluir(id_)
                mostrar_sucesso("Cliente excluído com sucesso!")
                self._carregar()
            except Exception as e:
                mostrar_erro(f"Erro ao excluir: {e}")


# ─── Formulário ─────────────────────────────

class FormCliente(tk.Toplevel):
    def __init__(self, parent, id_cliente, callback):
        super().__init__(parent)
        self.id_cliente = id_cliente
        self.callback = callback
        self._editar = id_cliente is not None

        self.title("Editar Cliente" if self._editar else "Novo Cliente")
        self.geometry("520x560")
        self.configure(bg=COLORS["branco"])
        self.resizable(False, False)
        self.grab_set()

        # Centralizar
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2 - 260
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - 280
        self.geometry(f"+{px}+{py}")

        self._build()
        if self._editar:
            self._popular()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS["rosa_principal"], height=50)
        hdr.pack(fill="x")
        titulo = "Editar Cliente" if self._editar else "Novo Cliente"
        tk.Label(hdr, text=titulo, font=FONTS["subtitulo"],
                 fg=COLORS["branco"], bg=COLORS["rosa_principal"]).pack(
            side="left", padx=20, pady=12)

        # Corpo do formulário
        body = tk.Frame(self, bg=COLORS["branco"], padx=30, pady=10)
        body.pack(fill="both", expand=True)

        campos = [
            ("Nome *", "nome"), ("Email", "email"), ("Senha", "senha"),
            ("CPF *", "cpf"), ("Telefone", "telefone"), ("Endereço", "endereco"),
            ("Data de Nascimento (AAAA-MM-DD)", "data_nascimento"),
        ]
        self._entries = {}
        for label, key in campos:
            lbl_campo(body, label, bg=COLORS["branco"]).pack(anchor="w", pady=(8, 0))
            e = entry_padrao(body, largura=45)
            e.pack(fill="x")
            self._entries[key] = e

        # Rodapé
        rodape = tk.Frame(self, bg=COLORS["branco"], pady=10)
        rodape.pack(fill="x", padx=30)
        btn_primario(rodape, "💾 Salvar", self._salvar, largura=12).pack(side="right", padx=5)
        btn_secundario(rodape, "Cancelar", self.destroy, largura=12).pack(side="right")

    def _popular(self):
        dados = _buscar_por_id(self.id_cliente)
        if not dados:
            return
        for key, entry in self._entries.items():
            valor = dados.get(key)
            if valor is None:
                valor = ""
            entry.delete(0, "end")
            entry.insert(0, str(valor))

    def _salvar(self):
        d = {k: e.get().strip() for k, e in self._entries.items()}

        # Validações
        ok, msg = validar_campos({"Nome": d["nome"], "CPF": d["cpf"]})
        if not ok:
            mostrar_erro(msg)
            return

        d["cpf"] = formatar_cpf(d["cpf"])
        if d["telefone"]:
            d["telefone"] = formatar_telefone(d["telefone"])

        try:
            if self._editar:
                _atualizar(self.id_cliente, d)
                mostrar_sucesso("Cliente atualizado com sucesso!")
            else:
                _inserir(d)
                mostrar_sucesso("Cliente cadastrado com sucesso!")
            self.callback()
            self.destroy()
        except Exception as e:
            mostrar_erro(f"Erro ao salvar: {e}")
