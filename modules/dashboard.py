import tkinter as tk
from database.connection import execute_query
from utils.constants import COLORS, FONTS


def _totais():
    def count(tbl):
        r = execute_query(f"SELECT COUNT(*) AS n FROM {tbl}", fetch_one=True)
        return r["n"] if r else 0

    return {
        "clientes":     count("cliente"),
        "funcionarios": count("funcionario"),
        "produtos":     count("produto"),
        "servicos":     count("servico"),
        "agendamentos": count("agendamento"),
        "vendas":       count("venda"),
        "pagamentos":   count("pagamento"),
    }


def _alertas_estoque():
    return execute_query(
        "SELECT nome, estoque, estoque_minimo FROM produto WHERE estoque <= estoque_minimo",
        fetch=True) or []


def _agendamentos_hoje():
    return execute_query(
        "SELECT a.id, c.nome AS cliente, a.data_hora, a.status "
        "FROM agendamento a JOIN cliente c ON c.id = a.cliente_id "
        "WHERE DATE(a.data_hora) = CURRENT_DATE ORDER BY a.data_hora",
        fetch=True) or []


def _faturamento_mes():
    r = execute_query(
        "SELECT COALESCE(SUM(iv.quantidade * iv.preco_unitario), 0) AS total "
        "FROM item_venda iv JOIN venda v ON v.id = iv.venda_id "
        "WHERE v.status = 'Ativa' AND DATE_TRUNC('month', v.data_venda) = DATE_TRUNC('month', CURRENT_DATE)",
        fetch_one=True)
    return float(r["total"]) if r else 0.0


class TelaDashboard(tk.Frame):
    def __init__(self, parent, nav_callback=None):
        super().__init__(parent, bg=COLORS["fundo"])
        self._nav = nav_callback
        self._build()

    def _build(self):
        # Título
        hdr = tk.Frame(self, bg=COLORS["fundo"])
        hdr.pack(fill="x", padx=20, pady=(20, 5))
        tk.Label(hdr, text="💄 Dashboard – Salão de Beleza",
                 font=FONTS["titulo"], fg=COLORS["rosa_principal"],
                 bg=COLORS["fundo"]).pack(side="left")

        btn_ref = tk.Button(hdr, text="🔄 Atualizar", command=self._refresh,
                             bg=COLORS["azul_suave"], fg=COLORS["texto"],
                             font=FONTS["botao"], relief="flat", cursor="hand2",
                             padx=8, pady=4)
        btn_ref.pack(side="right", padx=10)

        tk.Frame(self, bg=COLORS["borda"], height=1).pack(fill="x", padx=20, pady=5)

        # Container scrollável
        canvas = tk.Canvas(self, bg=COLORS["fundo"], highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        self._inner = tk.Frame(canvas, bg=COLORS["fundo"])
        self._win_id = canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                     lambda e: canvas.itemconfig(self._win_id, width=e.width))
        canvas.bind_all("<MouseWheel>",
                         lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._populate()

    def _populate(self):
        # Limpar inner
        for w in self._inner.winfo_children():
            w.destroy()

        try:
            totais = _totais()
            alertas = _alertas_estoque()
            hoje = _agendamentos_hoje()
            fat = _faturamento_mes()
        except Exception:
            tk.Label(self._inner, text="⚠️ Banco de dados não conectado.\n"
                     "Configure a conexão em database/connection.py",
                     font=FONTS["normal"], fg=COLORS["erro"],
                     bg=COLORS["fundo"]).pack(pady=40)
            return

        # ── CARDS principais ─────────────────────
        self._secao("📊 Resumo Geral")
        card_dados = [
            ("👤", "Clientes",      totais["clientes"],     COLORS["rosa_claro"],    "clientes"),
            ("👩‍💼", "Funcionários",  totais["funcionarios"], COLORS["verde_suave"],   "funcionarios"),
            ("📦", "Produtos",      totais["produtos"],     COLORS["bege"],          "produtos"),
            ("✂️", "Serviços",      totais["servicos"],     COLORS["azul_suave"],    "servicos"),
            ("📅", "Agendamentos",  totais["agendamentos"], COLORS["rosa_principal"],"agendamentos"),
            ("🛒", "Vendas",        totais["vendas"],       COLORS["verde_suave"],   "vendas"),
            ("💳", "Pagamentos",    totais["pagamentos"],   COLORS["bege"],          "pagamentos"),
        ]
        self._cards_row(card_dados)

        # ── Faturamento ──────────────────────────
        self._secao("💰 Faturamento do Mês")
        fat_frame = tk.Frame(self._inner, bg=COLORS["verde_suave"],
                              relief="flat", bd=0, padx=30, pady=20)
        fat_frame.pack(padx=20, pady=5, fill="x")
        tk.Label(fat_frame, text=f"R$ {fat:,.2f}",
                  font=("Segoe UI", 26, "bold"),
                  fg="#2E7D32", bg=COLORS["verde_suave"]).pack()
        tk.Label(fat_frame, text="Total de vendas ativas no mês atual",
                  font=FONTS["pequeno"], fg=COLORS["texto"],
                  bg=COLORS["verde_suave"]).pack()

        # ── Alertas de estoque ───────────────────
        self._secao("⚠️ Alertas de Estoque")
        if alertas:
            for a in alertas:
                linha = tk.Frame(self._inner, bg="#FFF3CD", relief="flat", pady=6, padx=15)
                linha.pack(fill="x", padx=20, pady=2)
                tk.Label(linha,
                          text=f"⚠️  {a['nome']}  |  Estoque: {a['estoque']}  |  Mínimo: {a['estoque_minimo']}",
                          font=FONTS["normal"], fg="#856404", bg="#FFF3CD").pack(anchor="w")
        else:
            tk.Label(self._inner, text="✅  Todos os produtos com estoque adequado!",
                      font=FONTS["normal"], fg=COLORS["sucesso"],
                      bg=COLORS["fundo"]).pack(padx=20, anchor="w", pady=5)

        # ── Agendamentos hoje ────────────────────
        self._secao("📅 Agendamentos de Hoje")
        if hoje:
            for ag in hoje:
                cor = COLORS["verde_suave"] if ag["status"] == "Agendado" else "#F8D7DA"
                linha = tk.Frame(self._inner, bg=cor, relief="flat", pady=6, padx=15)
                linha.pack(fill="x", padx=20, pady=2)
                tk.Label(linha,
                          text=f"#{ag['id']}  |  {ag['cliente']}  |  "
                               f"{str(ag['data_hora'])[11:16]}  |  {ag['status']}",
                          font=FONTS["normal"], fg=COLORS["texto"], bg=cor).pack(anchor="w")
        else:
            tk.Label(self._inner, text="Nenhum agendamento para hoje.",
                      font=FONTS["normal"], fg=COLORS["texto"],
                      bg=COLORS["fundo"]).pack(padx=20, anchor="w", pady=5)

    def _secao(self, titulo):
        f = tk.Frame(self._inner, bg=COLORS["fundo"])
        f.pack(fill="x", padx=20, pady=(18, 4))
        tk.Label(f, text=titulo, font=FONTS["subtitulo"],
                  fg=COLORS["texto"], bg=COLORS["fundo"]).pack(side="left")
        tk.Frame(self._inner, bg=COLORS["borda"], height=1).pack(fill="x", padx=20)

    def _cards_row(self, dados):
        row = tk.Frame(self._inner, bg=COLORS["fundo"])
        row.pack(fill="x", padx=20, pady=8)
        for emoji, label, numero, cor, modulo in dados:
            self._card(row, emoji, label, numero, cor, modulo)

    def _card(self, parent, emoji, label, numero, cor, modulo):
        f = tk.Frame(parent, bg=cor, relief="flat", bd=0,
                      padx=12, pady=14, cursor="hand2")
        f.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        tk.Label(f, text=emoji, font=("Segoe UI", 20),
                  fg=COLORS["texto"], bg=cor).pack()
        tk.Label(f, text=str(numero), font=FONTS["card_num"],
                  fg=COLORS["texto"], bg=cor).pack()
        tk.Label(f, text=label, font=FONTS["card_label"],
                  fg=COLORS["texto"], bg=cor).pack()

        def click(m=modulo):
            if self._nav:
                self._nav(m)
        f.bind("<Button-1>", lambda e: click())
        for child in f.winfo_children():
            child.bind("<Button-1>", lambda e: click())

    def _refresh(self):
        self._populate()
