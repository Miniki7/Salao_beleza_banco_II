# ============================================
# IDENTIDADE VISUAL – SALÃO DE BELEZA
# ============================================

# Paleta de cores oficial
COLORS = {
    "rosa_principal": "#E98688",
    "verde_suave":    "#CCEDCE",
    "rosa_claro":     "#FEB3C2",
    "bege":           "#F8D3AD",
    "azul_suave":     "#AABDFF",
    "texto":          "#4F4F4F",
    "branco":         "#FFFFFF",
    "fundo":          "#FFF8F8",
    "sidebar":        "#F2D4D5",
    "sidebar_hover":  "#E98688",
    "sidebar_text":   "#4F4F4F",
    "tabela_alt":     "#FFF0F0",
    "borda":          "#E0C8C8",
    "erro":           "#D9534F",
    "sucesso":        "#5CB85C",
    "aviso":          "#F0AD4E",
}

# Fontes
FONTS = {
    "titulo":       ("Segoe UI", 18, "bold"),
    "subtitulo":    ("Segoe UI", 13, "bold"),
    "normal":       ("Segoe UI", 11),
    "pequeno":      ("Segoe UI", 9),
    "botao":        ("Segoe UI", 10, "bold"),
    "sidebar":      ("Segoe UI", 11),
    "sidebar_title":("Segoe UI", 13, "bold"),
    "card_num":     ("Segoe UI", 22, "bold"),
    "card_label":   ("Segoe UI", 10),
}

# Dimensões gerais
SIDEBAR_WIDTH  = 200
WINDOW_MIN_W   = 1100
WINDOW_MIN_H   = 680

# Módulos do menu
MENU_ITEMS = [
    ("🏠  Home",          "home"),
    ("👤  Clientes",       "clientes"),
    ("👩‍💼  Funcionários",   "funcionarios"),
    ("📦  Produtos",       "produtos"),
    ("✂️  Serviços",       "servicos"),
    ("📅  Agendamentos",   "agendamentos"),
    ("🛒  Vendas",         "vendas"),
    ("💳  Pagamentos",     "pagamentos"),
]

# Status possíveis
STATUS_AGENDAMENTO = ["Agendado", "Concluído", "Cancelado"]
STATUS_VENDA       = ["Ativa", "Cancelada"]
STATUS_FUNCIONARIO = ["Ativo", "Inativo"]
FORMAS_PAGAMENTO   = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito",
                      "PIX", "Transferência", "Outro"]
