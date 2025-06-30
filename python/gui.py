import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tkinter import ttk

class ModernAppUI:
    def __init__(self, root):
        # Estilo claro e moderno
        self.style = Style(theme="flatly")  # flatly = claro, moderno, sem modo escuro
        root.title("Python App Launcher - UI Moderna")
        root.geometry("1200x700")
        root.minsize(900, 600)

        # Frame principal
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(fill=BOTH, expand=YES)

        # Header
        self.create_header()
        # Conteúdo principal
        self.create_main_content()
        # Sidebar
        self.create_sidebar()

    def create_header(self):
        header = ttk.Frame(self.main_frame, padding=(0, 0, 0, 10))
        header.pack(fill=X)
        title = ttk.Label(header, text="Python App Launcher", font=("Segoe UI", 22, "bold"), bootstyle=PRIMARY)
        title.pack(side=LEFT)
        # Botão de IA
        ia_btn = ttk.Button(header, text="🤖 IA", bootstyle=SUCCESS, width=8)
        ia_btn.pack(side=RIGHT, padx=5)
        # Botão de configurações
        config_btn = ttk.Button(header, text="⚙️ Config", bootstyle=INFO, width=10)
        config_btn.pack(side=RIGHT, padx=5)
        # Campo de busca
        search = ttk.Entry(header, width=30)
        search.pack(side=RIGHT, padx=10)

    def create_sidebar(self):
        sidebar = ttk.Frame(self.main_frame, width=180, padding=(0, 10, 10, 0))
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)
        # Navegação
        nav_label = ttk.Label(sidebar, text="Navegação", font=("Segoe UI", 12, "bold"), bootstyle=SECONDARY)
        nav_label.pack(anchor=W, pady=(0, 10))
        for item in ["Início", "Apps", "Grupos", "Categorias", "Estatísticas", "Sobre"]:
            btn = ttk.Button(sidebar, text=item, bootstyle=OUTLINE, width=18)
            btn.pack(anchor=W, pady=2)

    def create_main_content(self):
        content = ttk.Frame(self.main_frame, padding=10, style="secondary.TFrame")
        content.pack(side=LEFT, fill=BOTH, expand=YES)
        # Cards de apps (exemplo)
        cards_frame = ttk.Frame(content)
        cards_frame.pack(fill=BOTH, expand=YES)
        for i in range(6):
            card = ttk.Frame(cards_frame, padding=15, style="info.TFrame", relief=RAISED)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            title = ttk.Label(card, text=f"App {i+1}", font=("Segoe UI", 12, "bold"), bootstyle=INFO)
            title.pack(anchor=W)
            desc = ttk.Label(card, text="Descrição do app...", font=("Segoe UI", 9), bootstyle=SECONDARY)
            desc.pack(anchor=W, pady=(5, 0))
            btns = ttk.Frame(card)
            btns.pack(anchor=E, pady=(10, 0))
            ttk.Button(btns, text="Abrir", bootstyle=SUCCESS, width=8).pack(side=LEFT, padx=2)
            ttk.Button(btns, text="Editar", bootstyle=WARNING, width=8).pack(side=LEFT, padx=2)
            ttk.Button(btns, text="Excluir", bootstyle=DANGER, width=8).pack(side=LEFT, padx=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernAppUI(root)
    root.mainloop() 