#!/usr/bin/env python3
"""
=======================================================
SISTEMA DE GERENCIAMENTO – SALÃO DE BELEZA
=======================================================
Desenvolvido com Python 3 + Tkinter + PostgreSQL
=======================================================
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Adiciona o diretório raiz ao path para imports absolutos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.constants import COLORS, FONTS, MENU_ITEMS, SIDEBAR_WIDTH, WINDOW_MIN_W, WINDOW_MIN_H
from database.connection import test_connection, init_database


class SalaoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💄 Salão de Beleza – Sistema de Gerenciamento")
        self.geometry(f"{WINDOW_MIN_W}x{WINDOW_MIN_H}")
        self.minsize(WINDOW_MIN_W, WINDOW_MIN_H)
        self.configure(bg=COLORS["fundo"])

        # Ícone (opcional – coloque um .ico em assets/ se quiser)
        try:
            self.iconbitmap("assets/icon.ico")
        except Exception:
            pass

        self._tela_atual = None
        self._btn_ativo = None

        self._build_layout()
        self._verificar_banco()
        self._navegar("home")

    # ─── Layout ────────────────────────────────────────

    def _build_layout(self):
        # ── Sidebar ──
        self._sidebar = tk.Frame(self, bg=COLORS["sidebar"],
                                  width=SIDEBAR_WIDTH, relief="flat")
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Logo / título da sidebar
        logo_frame = tk.Frame(self._sidebar, bg=COLORS["rosa_principal"],
                               height=80, width=SIDEBAR_WIDTH)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="💄", font=("Segoe UI", 22),
                  bg=COLORS["rosa_principal"], fg=COLORS["branco"]).pack(pady=(15, 0))
        tk.Label(logo_frame, text="Salão Beauty",
                  font=FONTS["sidebar_title"],
                  bg=COLORS["rosa_principal"], fg=COLORS["branco"]).pack()

        # Separador
        tk.Frame(self._sidebar, bg=COLORS["borda"], height=1).pack(fill="x")

        # Botões do menu
        self._btns_menu = {}
        for label, chave in MENU_ITEMS:
            btn = tk.Button(
                self._sidebar,
                text=label,
                command=lambda c=chave: self._navegar(c),
                bg=COLORS["sidebar"],
                fg=COLORS["sidebar_text"],
                font=FONTS["sidebar"],
                anchor="w",
                relief="flat",
                cursor="hand2",
                padx=18, pady=10,
                width=20,
                activebackground=COLORS["sidebar_hover"],
                activeforeground=COLORS["branco"],
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: self._hover_in(b))
            btn.bind("<Leave>", lambda e, b=btn: self._hover_out(b))
            self._btns_menu[chave] = btn

        # Rodapé sidebar
        tk.Frame(self._sidebar, bg=COLORS["sidebar"]).pack(expand=True)
        tk.Label(self._sidebar, text="v1.0 – 2025",
                  font=FONTS["pequeno"], fg=COLORS["texto"],
                  bg=COLORS["sidebar"]).pack(pady=8)

        # ── Área principal ──
        self._main = tk.Frame(self, bg=COLORS["fundo"])
        self._main.pack(side="left", fill="both", expand=True)

    def _hover_in(self, btn):
        if btn != self._btn_ativo:
            btn.config(bg=COLORS["rosa_claro"], fg=COLORS["texto"])

    def _hover_out(self, btn):
        if btn != self._btn_ativo:
            btn.config(bg=COLORS["sidebar"], fg=COLORS["sidebar_text"])

    def _set_ativo(self, chave):
        if self._btn_ativo:
            self._btn_ativo.config(bg=COLORS["sidebar"], fg=COLORS["sidebar_text"])
        btn = self._btns_menu.get(chave)
        if btn:
            btn.config(bg=COLORS["rosa_principal"], fg=COLORS["branco"])
            self._btn_ativo = btn

    # ─── Navegação ─────────────────────────────────────

    def _navegar(self, chave: str):
        # Remove tela atual
        if self._tela_atual:
            self._tela_atual.destroy()

        self._set_ativo(chave)

        # Importação lazy para evitar imports circulares e agilizar startup
        if chave == "home":
            from modules.dashboard import TelaDashboard
            self._tela_atual = TelaDashboard(self._main, nav_callback=self._navegar)

        elif chave == "clientes":
            from modules.clientes import TelaClientes
            self._tela_atual = TelaClientes(self._main)

        elif chave == "funcionarios":
            from modules.funcionarios import TelaFuncionarios
            self._tela_atual = TelaFuncionarios(self._main)

        elif chave == "produtos":
            from modules.produtos import TelaProdutos
            self._tela_atual = TelaProdutos(self._main)

        elif chave == "servicos":
            from modules.servicos import TelaServicos
            self._tela_atual = TelaServicos(self._main)

        elif chave == "agendamentos":
            from modules.agendamentos import TelaAgendamentos
            self._tela_atual = TelaAgendamentos(self._main)

        elif chave == "vendas":
            from modules.vendas import TelaVendas
            self._tela_atual = TelaVendas(self._main)

        elif chave == "pagamentos":
            from modules.pagamentos import TelaPagamentos
            self._tela_atual = TelaPagamentos(self._main)

        if self._tela_atual:
            self._tela_atual.pack(fill="both", expand=True)

    # ─── Banco de dados ────────────────────────────────

    def _verificar_banco(self):
        ok, msg = test_connection()
        if not ok:
            messagebox.showwarning(
                "Banco de Dados",
                f"Não foi possível conectar ao PostgreSQL:\n\n{msg}\n\n"
                "Configure as credenciais em database/connection.py\n"
                "O sistema funcionará sem persistência de dados.",
            )
            return

        # Inicializa schema automaticamente
        ok2, msg2 = init_database()
        if not ok2:
            messagebox.showerror(
                "Erro ao Inicializar Banco",
                f"Erro ao criar tabelas:\n{msg2}"
            )


def main():
    app = SalaoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
