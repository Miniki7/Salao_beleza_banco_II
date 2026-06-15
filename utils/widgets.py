import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLORS, FONTS


# ─────────────────────────────────────────────
# Botões padronizados
# ─────────────────────────────────────────────

def btn_primario(parent, texto, comando, largura=14):
    return tk.Button(
        parent, text=texto, command=comando,
        bg=COLORS["rosa_principal"], fg=COLORS["branco"],
        font=FONTS["botao"], relief="flat", cursor="hand2",
        padx=10, pady=6, width=largura,
        activebackground=COLORS["rosa_claro"],
        activeforeground=COLORS["branco"],
    )


def btn_secundario(parent, texto, comando, largura=14):
    return tk.Button(
        parent, text=texto, command=comando,
        bg=COLORS["azul_suave"], fg=COLORS["texto"],
        font=FONTS["botao"], relief="flat", cursor="hand2",
        padx=10, pady=6, width=largura,
        activebackground="#8FA8FF",
        activeforeground=COLORS["branco"],
    )


def btn_perigo(parent, texto, comando, largura=14):
    return tk.Button(
        parent, text=texto, command=comando,
        bg=COLORS["erro"], fg=COLORS["branco"],
        font=FONTS["botao"], relief="flat", cursor="hand2",
        padx=10, pady=6, width=largura,
        activebackground="#C9302C",
        activeforeground=COLORS["branco"],
    )


def btn_sucesso(parent, texto, comando, largura=14):
    return tk.Button(
        parent, text=texto, command=comando,
        bg=COLORS["sucesso"], fg=COLORS["branco"],
        font=FONTS["botao"], relief="flat", cursor="hand2",
        padx=10, pady=6, width=largura,
        activebackground="#449D44",
        activeforeground=COLORS["branco"],
    )


# ─────────────────────────────────────────────
# Labels padronizadas
# ─────────────────────────────────────────────

def lbl_titulo(parent, texto, bg=None):
    return tk.Label(
        parent, text=texto, font=FONTS["titulo"],
        fg=COLORS["rosa_principal"],
        bg=bg or COLORS["fundo"],
    )


def lbl_campo(parent, texto, bg=None):
    return tk.Label(
        parent, text=texto, font=FONTS["normal"],
        fg=COLORS["texto"], bg=bg or COLORS["branco"],
        anchor="w",
    )


# ─────────────────────────────────────────────
# Entry padronizado
# ─────────────────────────────────────────────

def entry_padrao(parent, largura=30, **kwargs):
    e = tk.Entry(
        parent, width=largura, font=FONTS["normal"],
        fg=COLORS["texto"], bg=COLORS["branco"],
        relief="solid", bd=1, **kwargs,
    )
    e.configure(highlightthickness=1,
                 highlightcolor=COLORS["rosa_principal"],
                 highlightbackground=COLORS["borda"])
    return e


def combo_padrao(parent, valores, largura=28, **kwargs):
    style = ttk.Style()
    style.configure("Custom.TCombobox",
                     fieldbackground=COLORS["branco"],
                     background=COLORS["branco"],
                     foreground=COLORS["texto"],
                     font=FONTS["normal"])
    c = ttk.Combobox(
        parent, values=valores, width=largura,
        state="readonly", style="Custom.TCombobox", **kwargs,
    )
    return c


# ─────────────────────────────────────────────
# Treeview padronizada
# ─────────────────────────────────────────────

def criar_treeview(parent, colunas, larguras=None, scroll_y=True):
    frame = tk.Frame(parent, bg=COLORS["fundo"])
    frame.pack(fill="both", expand=True, padx=10, pady=5)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Salao.Treeview",
        background=COLORS["branco"],
        fieldbackground=COLORS["branco"],
        foreground=COLORS["texto"],
        rowheight=28,
        font=FONTS["normal"],
    )
    style.configure(
        "Salao.Treeview.Heading",
        background=COLORS["rosa_principal"],
        foreground=COLORS["branco"],
        font=FONTS["botao"],
        relief="flat",
    )
    style.map("Salao.Treeview",
              background=[("selected", COLORS["azul_suave"])],
              foreground=[("selected", COLORS["texto"])])

    tree = ttk.Treeview(
        frame, columns=colunas, show="headings",
        style="Salao.Treeview", selectmode="browse",
    )

    for i, col in enumerate(colunas):
        larg = (larguras[i] if larguras and i < len(larguras) else 120)
        tree.heading(col, text=col)
        tree.column(col, width=larg, anchor="center", minwidth=60)

    tree.tag_configure("par",   background=COLORS["branco"])
    tree.tag_configure("impar", background=COLORS["tabela_alt"])

    if scroll_y:
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

    tree.pack(fill="both", expand=True)
    return tree


def preencher_treeview(tree, dados):
    """Limpa e preenche a Treeview com linhas alternadas."""
    for item in tree.get_children():
        tree.delete(item)
    for i, linha in enumerate(dados):
        tag = "par" if i % 2 == 0 else "impar"
        tree.insert("", "end", values=list(linha.values()), tags=(tag,))


# ─────────────────────────────────────────────
# Janela modal padronizada
# ─────────────────────────────────────────────

def janela_modal(parent, titulo, largura=520, altura=500):
    top = tk.Toplevel(parent)
    top.title(titulo)
    top.geometry(f"{largura}x{altura}")
    top.configure(bg=COLORS["branco"])
    top.grab_set()
    top.resizable(False, False)

    # Centralizar
    top.update_idletasks()
    px = parent.winfo_rootx() + (parent.winfo_width() // 2) - (largura // 2)
    py = parent.winfo_rooty() + (parent.winfo_height() // 2) - (altura // 2)
    top.geometry(f"+{px}+{py}")

    # Cabeçalho
    header = tk.Frame(top, bg=COLORS["rosa_principal"], height=50)
    header.pack(fill="x")
    tk.Label(
        header, text=titulo, font=FONTS["subtitulo"],
        fg=COLORS["branco"], bg=COLORS["rosa_principal"],
    ).pack(side="left", padx=20, pady=12)

    return top


# ─────────────────────────────────────────────
# Frame de pesquisa
# ─────────────────────────────────────────────

def frame_pesquisa(parent, callback_pesquisa, callback_limpar, bg=None):
    bg = bg or COLORS["fundo"]
    frame = tk.Frame(parent, bg=bg)
    frame.pack(fill="x", padx=10, pady=(5, 0))

    tk.Label(frame, text="🔍 Pesquisar:", font=FONTS["normal"],
             fg=COLORS["texto"], bg=bg).pack(side="left", padx=(0, 5))

    var = tk.StringVar()
    e = entry_padrao(frame, largura=30, textvariable=var)
    e.pack(side="left", padx=5)
    e.bind("<Return>", lambda _: callback_pesquisa(var.get()))

    btn_primario(frame, "Buscar", lambda: callback_pesquisa(var.get()),
                 largura=8).pack(side="left", padx=3)
    btn_secundario(frame, "Limpar", callback_limpar,
                   largura=8).pack(side="left", padx=3)

    return var


# ─────────────────────────────────────────────
# Utilitários de validação
# ─────────────────────────────────────────────

def validar_campos(campos: dict) -> tuple[bool, str]:
    """
    campos = {"Nome": valor, "CPF": valor, ...}
    Retorna (True, "") se tudo OK, ou (False, mensagem) se houver erro.
    """
    for nome, valor in campos.items():
        if valor is None or str(valor).strip() == "":
            return False, f"O campo '{nome}' é obrigatório."
    return True, ""


def validar_positivo(valor, nome="Valor") -> tuple[bool, str]:
    try:
        n = float(str(valor).replace(",", "."))
        if n <= 0:
            return False, f"'{nome}' deve ser maior que zero."
        return True, ""
    except ValueError:
        return False, f"'{nome}' deve ser um número válido."


def formatar_cpf(cpf: str) -> str:
    digits = "".join(filter(str.isdigit, cpf))
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    return cpf


def formatar_telefone(tel: str) -> str:
    digits = "".join(filter(str.isdigit, tel))
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return tel


def mostrar_erro(msg: str):
    messagebox.showerror("Erro", msg)


def mostrar_sucesso(msg: str):
    messagebox.showinfo("Sucesso", msg)


def confirmar(msg: str) -> bool:
    return messagebox.askyesno("Confirmação", msg)
