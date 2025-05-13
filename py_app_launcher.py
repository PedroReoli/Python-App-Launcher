import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import threading
import datetime
import json
import time
import platform
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import io
import traceback

# Importar backend
from py_app_launcher_backend import PyAppLauncherBackend

class PyAppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("PyAppLauncher Avançado")
        self.root.geometry("1200x700")
        self.root.minsize(900, 600)
        
        # Inicializar backend
        self.backend = PyAppLauncherBackend()
        
        # Variáveis
        self.cards = []
        self.current_category = "Todos"
        self.current_group = "Todos"
        self.search_term = ""
        self.view_mode = self.backend.config["behavior"]["default_view"]
        self.drag_data = {"widget": None, "x": 0, "y": 0, "item": None}
        
        # Configurar tema e cores
        self.colors = self.backend.get_colors()
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar estilos personalizados
        self.configure_styles()
        
        # Criar interface
        self.create_interface()
        
        # Carregar aplicações
        self.scan_apps()
        
        # Iniciar monitoramento de processos
        self.monitoring_thread = threading.Thread(target=self.backend.monitor_processes, daemon=True)
        self.monitoring_thread.start()
        
        # Configurar atualização automática se habilitada
        self.setup_auto_refresh()
        
        # Configurar encerramento adequado
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        """Encerrar aplicação"""
        if self.backend.running_processes:
            if messagebox.askyesno("Confirmar Saída", 
                                 "Existem aplicações em execução. Deseja encerrá-las e sair?"):
                self.backend.shutdown()
                self.root.destroy()
        else:
            self.backend.shutdown()
            self.root.destroy()
    
    def configure_styles(self):
        """Configurar estilos personalizados para widgets"""
        # Obter configurações de fonte
        font_family = self.backend.config["font"]["family"]
        font_sizes = self.backend.config["font"]["size"]
        
        # Configurar estilos básicos
        self.style.configure("TFrame", background=self.colors["background"])
        self.style.configure("Card.TFrame", background=self.colors["card"])
        
        self.style.configure("TLabel", background=self.colors["background"], foreground=self.colors["text"], 
                           font=(font_family, font_sizes["normal"]))
        self.style.configure("Card.TLabel", background=self.colors["card"], foreground=self.colors["text"], 
                           font=(font_family, font_sizes["normal"]))
        self.style.configure("CardTitle.TLabel", background=self.colors["card"], foreground=self.colors["text"], 
                           font=(font_family, font_sizes["normal"], "bold"))
        self.style.configure("CardDesc.TLabel", background=self.colors["card"], foreground=self.colors["text_light"], 
                           font=(font_family, font_sizes["small"]))
        
        self.style.configure("Category.TButton", background=self.colors["background"], foreground=self.colors["text"])
        self.style.configure("CategorySelected.TButton", background=self.colors["primary_light"], foreground="white")
        
        self.style.configure("Primary.TButton", background=self.colors["primary"], foreground="white")
        self.style.map("Primary.TButton",
                      background=[('active', self.colors["primary_light"])],
                      foreground=[('active', 'white')])
        
        self.style.configure("Success.TButton", background=self.colors["secondary"], foreground="white")
        self.style.map("Success.TButton",
                      background=[('active', "#00d1a0")],
                      foreground=[('active', 'white')])
        
        self.style.configure("Danger.TButton", background=self.colors["danger"], foreground="white")
        self.style.map("Danger.TButton",
                      background=[('active', "#ff4d4d")],
                      foreground=[('active', 'white')])
        
        # Estilo para botões pequenos
        self.style.configure("Small.TButton", padding=2)
        
        # Estilo para botões da barra de ferramentas
        self.style.configure("Toolbar.TButton", background=self.colors["background"])
        
        # Estilo para itens de lista
        self.style.configure("List.TFrame", background=self.colors["card"], relief="solid", borderwidth=1)
        
        # Estilos para Kanban
        self.style.configure("Kanban.TFrame", background=self.colors["background"], padding=5)
        self.style.configure("KanbanColumn.TFrame", background=self.colors["card"], relief="solid", borderwidth=1, padding=5)
        self.style.configure("KanbanHeader.TLabel", background=self.colors["card"], foreground=self.colors["text"], 
                           font=(font_family, font_sizes["large"], "bold"))
        
        # Estilos para abas
        self.style.configure("TNotebook", background=self.colors["background"])
        self.style.configure("TNotebook.Tab", background=self.colors["background"], padding=[10, 5])
        self.style.map("TNotebook.Tab",
                      background=[("selected", self.colors["primary_light"])],
                      foreground=[("selected", "white")])
        
        # Estilos para configurações
        self.style.configure("Settings.TFrame", background=self.colors["background"], padding=10)
        self.style.configure("SettingsSection.TFrame", background=self.colors["card"], relief="solid", 
                           borderwidth=1, padding=10)
        self.style.configure("SettingsTitle.TLabel", background=self.colors["card"], foreground=self.colors["text"], 
                           font=(font_family, font_sizes["large"], "bold"))
        self.style.configure("SettingsSubtitle.TLabel", background=self.colors["card"], foreground=self.colors["text"], 
                           font=(font_family, font_sizes["normal"], "bold"))
    
    def create_interface(self):
        """Criar a interface principal"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título com logo
        title_frame = ttk.Frame(self.top_frame)
        title_frame.pack(side=tk.LEFT)
        
        # Criar um logo simples
        logo_canvas = tk.Canvas(title_frame, width=32, height=32, bg=self.colors["primary"], highlightthickness=0)
        logo_canvas.create_text(16, 16, text="PL", fill="white", font=("Arial", 14, "bold"))
        logo_canvas.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = ttk.Label(title_frame, text="PyAppLauncher", font=("Arial", 18, "bold"), foreground=self.colors["primary"])
        title_label.pack(side=tk.LEFT)
        
        # Barra de ferramentas
        toolbar_frame = ttk.Frame(self.top_frame)
        toolbar_frame.pack(side=tk.LEFT, padx=20)
        
        # Botão de atualização
        refresh_btn = ttk.Button(toolbar_frame, text="🔄 Atualizar", style="Toolbar.TButton", 
                               command=self.scan_apps)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão de nova aplicação
        new_app_btn = ttk.Button(toolbar_frame, text="➕ Nova Aplicação", style="Toolbar.TButton", 
                               command=self.create_new_app)
        new_app_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão de gerenciamento de dependências
        deps_btn = ttk.Button(toolbar_frame, text="📦 Dependências", style="Toolbar.TButton", 
                            command=self.manage_dependencies)
        deps_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão de gerenciamento de grupos
        groups_btn = ttk.Button(toolbar_frame, text="🗂️ Grupos", style="Toolbar.TButton", 
                              command=self.manage_groups)
        groups_btn.pack(side=tk.LEFT, padx=5)
        
        # Botões de alternância de visualização
        view_frame = ttk.Frame(toolbar_frame)
        view_frame.pack(side=tk.LEFT, padx=15)
        
        grid_btn = ttk.Button(view_frame, text="📊 Grid", style="Toolbar.TButton", 
                            command=lambda: self.set_view_mode("grid"))
        grid_btn.pack(side=tk.LEFT, padx=2)
        
        list_btn = ttk.Button(view_frame, text="📋 Lista", style="Toolbar.TButton", 
                            command=lambda: self.set_view_mode("list"))
        list_btn.pack(side=tk.LEFT, padx=2)
        
        kanban_btn = ttk.Button(view_frame, text="📌 Kanban", style="Toolbar.TButton", 
                              command=lambda: self.set_view_mode("kanban"))
        kanban_btn.pack(side=tk.LEFT, padx=2)
        
        # Botão de dashboard
        dashboard_btn = ttk.Button(toolbar_frame, text="📈 Dashboard", style="Toolbar.TButton", 
                                 command=self.show_dashboard)
        dashboard_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão de configurações
        settings_btn = ttk.Button(toolbar_frame, text="⚙️ Configurações", style="Toolbar.TButton", 
                                command=self.show_settings)
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame de pesquisa
        search_frame = ttk.Frame(self.top_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT)
        
        # Frame de grupos
        self.groups_frame = ttk.Frame(self.main_frame)
        self.groups_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Frame de categorias
        self.categories_frame = ttk.Frame(self.main_frame)
        self.categories_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame de conteúdo
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para scrolling
        self.canvas = tk.Canvas(self.content_frame, background=self.colors["background"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame para os cards
        self.cards_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        
        # Configurar rolagem
        self.cards_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Barra de status
        self.status_var = tk.StringVar(value="Pronto")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_auto_refresh(self):
        """Configurar atualização automática"""
        interval = self.backend.config["behavior"]["auto_refresh_interval"]
        if interval > 0:
            def auto_refresh():
                self.scan_apps()
                self.root.after(interval * 1000, auto_refresh)
            
            self.root.after(interval * 1000, auto_refresh)
    
    def on_frame_configure(self, event):
        """Atualizar região de rolagem quando o frame muda de tamanho"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Ajustar largura do frame interno quando o canvas muda de tamanho"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def on_mousewheel(self, event):
        """Permitir rolagem com o mouse"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def on_search_change(self, *args):
        """Atualizar a exibição quando o termo de pesquisa muda"""
        self.search_term = self.search_var.get().lower()
        self.update_app_display()
    
    def set_view_mode(self, mode):
        """Definir modo de visualização (grid, list ou kanban)"""
        if mode != self.view_mode:
            self.view_mode = mode
            self.update_app_display()
    
    def scan_apps(self):
        """Escanear aplicações e atualizar interface"""
        self.apps, categories = self.backend.scan_apps()
        
        # Atualizar grupos e categorias
        self.update_groups_display()
        self.update_categories_display(categories)
        
        # Atualizar exibição
        self.update_app_display()
        
        # Atualizar status
        self.status_var.set(f"Encontradas {len(self.apps)} aplicações")
    
    def update_groups_display(self):
        """Atualizar botões de grupos"""
        # Limpar frame de grupos
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
        
        # Adicionar label
        group_label = ttk.Label(self.groups_frame, text="Grupos:", font=("Arial", 10, "bold"))
        group_label.pack(side=tk.LEFT, padx=(0, 5), pady=5)
        
        # Adicionar botões de grupos
        for group in self.backend.groups.keys():
            style = "CategorySelected.TButton" if group == self.current_group else "Category.TButton"
            btn = ttk.Button(self.groups_frame, text=group, style=style,
                           command=lambda g=group: self.set_group(g))
            btn.pack(side=tk.LEFT, padx=(0, 5), pady=5)
    
    def update_categories_display(self, categories):
        """Atualizar botões de categorias"""
        # Limpar frame de categorias
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        
        # Adicionar label
        cat_label = ttk.Label(self.categories_frame, text="Categorias:", font=("Arial", 10, "bold"))
        cat_label.pack(side=tk.LEFT, padx=(0, 5), pady=5)
        
        # Adicionar botões de categorias
        for category in categories:
            style = "CategorySelected.TButton" if category == self.current_category else "Category.TButton"
            btn = ttk.Button(self.categories_frame, text=category, style=style,
                           command=lambda c=category: self.set_category(c))
            btn.pack(side=tk.LEFT, padx=(0, 5), pady=5)
    
    def set_group(self, group):
        """Definir grupo atual"""
        self.current_group = group
        self.update_groups_display()
        self.update_app_display()
    
    def set_category(self, category):
        """Definir categoria atual"""
        self.current_category = category
        self.update_categories_display([cat for cat in set(app["category"] for app in self.apps) | {"Todos"}])
        self.update_app_display()
    
    def update_app_display(self):
        """Atualizar exibição dos cards de aplicações"""
        # Limpar frame de cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        # Filtrar apps por grupo
        filtered_apps = self.apps
        if self.current_group != "Todos":
            group_files = self.backend.groups.get(self.current_group, [])
            filtered_apps = [app for app in filtered_apps if app["file"] in group_files]
        
        # Filtrar apps por categoria
        if self.current_category != "Todos":
            filtered_apps = [app for app in filtered_apps if app["category"] == self.current_category]
        
        # Filtrar por termo de pesquisa
        if self.search_term:
            filtered_apps = [app for app in filtered_apps if 
                           self.search_term in app["name"].lower() or 
                           self.search_term in app["description"].lower() or
                           any(self.search_term in tag.lower() for tag in app["tags"])]
        
        # Exibir mensagem se não houver apps
        if not filtered_apps:
            no_apps_label = ttk.Label(self.cards_frame, text="Nenhuma aplicação encontrada", 
                                    font=("Arial", 14), foreground=self.colors["text_light"])
            no_apps_label.pack(pady=50)
            return
        
        if self.view_mode == "grid":
            self.display_grid_view(filtered_apps)
        elif self.view_mode == "list":
            self.display_list_view(filtered_apps)
        elif self.view_mode == "kanban":
            self.display_kanban_view(filtered_apps)
    
    def display_grid_view(self, apps):
        """Exibir apps em visualização em grade"""
        # Criar grid para os cards
        row, col = 0, 0
        max_cols = self.backend.config["layout"]["max_columns"]
        
        for app in apps:
            # Criar card
            self.create_compact_card(app, row, col)
            
            # Atualizar posição
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def display_list_view(self, apps):
        """Exibir apps em visualização em lista"""
        for i, app in enumerate(apps):
            self.create_list_item(app, i)
    
    def display_kanban_view(self, apps):
        """Exibir apps em visualização kanban"""
        # Criar frame para colunas kanban
        kanban_frame = ttk.Frame(self.cards_frame, style="Kanban.TFrame")
        kanban_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar colunas
        num_columns = len(self.backend.kanban_columns)
        for i in range(num_columns):
            kanban_frame.columnconfigure(i, weight=1)
        
        # Criar colunas
        column_frames = {}
        for i, column in enumerate(self.backend.kanban_columns):
            frame = ttk.Frame(kanban_frame, style="KanbanColumn.TFrame")
            frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            
            # Título da coluna
            header = ttk.Label(frame, text=column, style="KanbanHeader.TLabel")
            header.pack(fill=tk.X, pady=(0, 10))
            
            # Configurar para receber drag and drop
            frame.bind("<ButtonRelease-1>", lambda e, col=column: self.on_kanban_drop(e, col))
            
            column_frames[column] = frame
        
        # Adicionar botão para gerenciar colunas
        manage_btn = ttk.Button(kanban_frame, text="Gerenciar Colunas", 
                              command=self.manage_kanban_columns)
        manage_btn.grid(row=1, column=0, columnspan=num_columns, pady=10)
        
        # Separar apps por estado
        apps_by_column = {column: [] for column in self.backend.kanban_columns}
        for app in apps:
            column = app["kanban_state"]
            if column in apps_by_column:
                apps_by_column[column].append(app)
        
        # Criar cards para cada coluna
        for column, column_apps in apps_by_column.items():
            if column in column_frames:
                for app in column_apps:
                    self.create_kanban_card(app, column_frames[column])
    
    def create_compact_card(self, app, row, col):
        """Criar card compacto para uma aplicação"""
        # Frame do card - mais compacto
        card = ttk.Frame(self.cards_frame, style="Card.TFrame")
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Definir tamanho do card
        card_size = self.backend.config["layout"]["card_size"]
        card.configure(width=card_size, height=card_size)
        
        # Adicionar borda
        card_border = ttk.Frame(card, style="Card.TFrame", relief="solid", borderwidth=1)
        card_border.pack(fill=tk.BOTH, expand=True)
        
        # Barra colorida superior
        color_bar = tk.Frame(card_border, background=app["color"], height=4)
        color_bar.pack(fill=tk.X)
        
        # Conteúdo do card
        content = ttk.Frame(card_border, style="Card.TFrame")
        content.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
        
        # Ícone da aplicação (primeira letra do nome)
        icon_size = 40
        icon_frame = tk.Frame(content, width=icon_size, height=icon_size, 
                            background=app["color"])
        icon_frame.pack(pady=(2, 0))
        
        # Manter o tamanho do frame
        icon_frame.pack_propagate(False)
        
        # Texto do ícone (primeira letra)
        icon_text = app["name"][0].upper()
        icon_label = tk.Label(icon_frame, text=icon_text, font=("Arial", 20, "bold"),
                            foreground="white", background=app["color"])
        icon_label.pack(fill=tk.BOTH, expand=True)
        
        # Título (clicável para editar)
        title_var = tk.StringVar(value=app["name"])
        title = ttk.Label(content, textvariable=title_var, style="CardTitle.TLabel", anchor="center")
        title.pack(fill=tk.X, pady=(3, 0))
        title.bind("<Double-Button-1>", lambda e, a=app, v=title_var: self.edit_app_name(a, v))
        
        # Descrição (mais curta)
        if self.backend.config["layout"]["show_description_in_grid"]:
            desc_text = app["description"]
            if len(desc_text) > 60:
                desc_text = desc_text[:57] + "..."
            
            desc_var = tk.StringVar(value=desc_text)
            desc = ttk.Label(content, textvariable=desc_var, style="CardDesc.TLabel", 
                           wraplength=card_size-20, anchor="center", justify="center")
            desc.pack(fill=tk.X, pady=(2, 0), expand=True)
            desc.bind("<Double-Button-1>", lambda e, a=app, v=desc_var: self.edit_app_description(a, v))
        
        # Status de execução
        is_running = app["file"] in self.backend.running_processes
        status_text = "Em execução" if is_running else "Parado"
        status_color = self.colors["secondary"] if is_running else self.colors["text_light"]
        
        status_frame = ttk.Frame(content, style="Card.TFrame")
        status_frame.pack(fill=tk.X, pady=(2, 0))
        
        status_indicator = tk.Frame(status_frame, width=6, height=6, background=status_color)
        status_indicator.pack(side=tk.LEFT, padx=(0, 3))
        
        status_label = ttk.Label(status_frame, text=status_text, 
                               style="CardDesc.TLabel", foreground=status_color)
        status_label.pack(side=tk.LEFT)
        
        # Contagem de execuções
        run_count_label = ttk.Label(status_frame, text=f"({app['run_count']})", 
                                  style="CardDesc.TLabel", foreground=self.colors["text_light"])
        run_count_label.pack(side=tk.RIGHT)
        
        # Botões
        button_frame = ttk.Frame(content, style="Card.TFrame")
        button_frame.pack(fill=tk.X, pady=(3, 0))
        
        # Botão Executar
        run_button = ttk.Button(button_frame, text="▶", style="Success.TButton",
                              command=lambda: self.run_app(app),
                              state="disabled" if is_running else "normal",
                              width=2)
        run_button.pack(side=tk.LEFT, padx=(0, 2), fill=tk.X, expand=True)
        
        # Botão Parar
        stop_button = ttk.Button(button_frame, text="■", style="Danger.TButton",
                               command=lambda: self.stop_app(app),
                               state="normal" if is_running else "disabled",
                               width=2)
        stop_button.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        
        # Botão Editar
        edit_button = ttk.Button(button_frame, text="✎", style="Primary.TButton",
                               command=lambda: self.edit_app(app),
                               width=2)
        edit_button.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        
        # Botão Código
        code_button = ttk.Button(button_frame, text="</>", style="Primary.TButton",
                               command=lambda: self.open_code(app),
                               width=2)
        code_button.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)
        
        # Configurar grid
        self.cards_frame.grid_columnconfigure(col, weight=1)
        self.cards_frame.grid_rowconfigure(row, weight=1)
        
        # Configurar drag and drop para grupos
        card.bind("<ButtonPress-1>", lambda e, a=app: self.on_drag_start(e, a, card))
        card.bind("<B1-Motion>", self.on_drag_motion)
        card.bind("<ButtonRelease-1>", self.on_drag_release)
    
    def create_list_item(self, app, index):
        """Criar item de lista para uma aplicação"""
        # Frame do item de lista
        item = ttk.Frame(self.cards_frame, style="List.TFrame")
        item.pack(fill=tk.X, padx=5, pady=2)
        
        # Indicador de cor
        color_indicator = tk.Frame(item, background=app["color"], width=5)
        color_indicator.pack(side=tk.LEFT, fill=tk.Y)
        
        # Frame de conteúdo
        content = ttk.Frame(item, style="Card.TFrame", padding=(10, 5))
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Linha superior: Título e status
        top_row = ttk.Frame(content, style="Card.TFrame")
        top_row.pack(fill=tk.X)
        
        # Título (clicável para editar)
        title_var = tk.StringVar(value=app["name"])
        title = ttk.Label(top_row, textvariable=title_var, style="CardTitle.TLabel")
        title.pack(side=tk.LEFT)
        title.bind("<Double-Button-1>", lambda e, a=app, v=title_var: self.edit_app_name(a, v))
        
        # Badge de categoria
        category_badge = ttk.Label(top_row, text=app["category"], 
                                 background=self.colors["primary_light"], foreground="white",
                                 padding=(5, 0))
        category_badge.pack(side=tk.LEFT, padx=10)
        
        # Badges de grupo
        for group_name, group_files in self.backend.groups.items():
            if app["file"] in group_files and group_name != "Todos":
                group_badge = ttk.Label(top_row, text=group_name, 
                                      background=self.colors["accent"], foreground=self.colors["text"],
                                      padding=(5, 0))
                group_badge.pack(side=tk.LEFT, padx=5)
        
        # Status
        is_running = app["file"] in self.backend.running_processes
        status_text = "Em execução" if is_running else "Parado"
        status_color = self.colors["secondary"] if is_running else self.colors["text_light"]
        
        status_frame = ttk.Frame(top_row, style="Card.TFrame")
        status_frame.pack(side=tk.RIGHT)
        
        status_indicator = tk.Frame(status_frame, width=8, height=8, background=status_color)
        status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        status_label = ttk.Label(status_frame, text=status_text, 
                               style="CardDesc.TLabel", foreground=status_color)
        status_label.pack(side=tk.LEFT)
        
        # Descrição (clicável para editar)
        desc_var = tk.StringVar(value=app["description"])
        desc = ttk.Label(content, textvariable=desc_var, style="CardDesc.TLabel", 
                       wraplength=600)
        desc.pack(fill=tk.X, pady=(5, 0))
        desc.bind("<Double-Button-1>", lambda e, a=app, v=desc_var: self.edit_app_description(a, v))
        
        # Linha inferior: Informações e botões
        bottom_row = ttk.Frame(content, style="Card.TFrame")
        bottom_row.pack(fill=tk.X, pady=(5, 0))
        
        # Informações de execução
        info_frame = ttk.Frame(bottom_row, style="Card.TFrame")
        info_frame.pack(side=tk.LEFT)
        
        # Mostrar métricas se configurado
        if self.backend.config["layout"]["show_metrics_in_list"]:
            last_run_label = ttk.Label(info_frame, 
                                     text=f"Última execução: {app['last_run']} | Execuções: {app['run_count']} | CPU: {app['avg_cpu']:.1f}% | Memória: {app['avg_memory']:.1f} MB", 
                                     style="CardDesc.TLabel", foreground=self.colors["text_light"])
            last_run_label.pack(side=tk.LEFT)
        else:
            last_run_label = ttk.Label(info_frame, 
                                     text=f"Última execução: {app['last_run']} | Execuções: {app['run_count']}", 
                                     style="CardDesc.TLabel", foreground=self.colors["text_light"])
            last_run_label.pack(side=tk.LEFT)
        
        # Mostrar tags se configurado
        if self.backend.config["layout"]["show_tags_in_list"] and app["tags"]:
            tags_label = ttk.Label(info_frame, 
                                 text=f" | Tags: {', '.join(app['tags'])}", 
                                 style="CardDesc.TLabel", foreground=self.colors["text_light"])
            tags_label.pack(side=tk.LEFT)
        
        # Dependências
        if app["dependencies"]:
            deps_label = ttk.Label(info_frame, 
                                 text=f" | Deps: {', '.join(app['dependencies'])}", 
                                 style="CardDesc.TLabel", foreground=self.colors["text_light"])
            deps_label.pack(side=tk.LEFT)
        
        # Botões
        button_frame = ttk.Frame(bottom_row, style="Card.TFrame")
        button_frame.pack(side=tk.RIGHT)
        
        # Botão Executar
        run_button = ttk.Button(button_frame, text="Executar", style="Success.TButton",
                              command=lambda: self.run_app(app),
                              state="disabled" if is_running else "normal",
                              width=8)
        run_button.pack(side=tk.LEFT, padx=2)
        
        # Botão Parar
        stop_button = ttk.Button(button_frame, text="Parar", style="Danger.TButton",
                               command=lambda: self.stop_app(app),
                               state="normal" if is_running else "disabled",
                               width=6)
        stop_button.pack(side=tk.LEFT, padx=2)
        
        # Botão Editar
        edit_button = ttk.Button(button_frame, text="Editar", style="Primary.TButton",
                               command=lambda: self.edit_app(app),
                               width=6)
        edit_button.pack(side=tk.LEFT, padx=2)
        
        # Botão Código
        code_button = ttk.Button(button_frame, text="Código", style="Primary.TButton",
                               command=lambda: self.open_code(app),
                               width=6)
        code_button.pack(side=tk.LEFT, padx=2)
        
        # Botão Métricas
        metrics_button = ttk.Button(button_frame, text="Métricas", style="Primary.TButton",
                                  command=lambda: self.show_app_metrics(app),
                                  width=8)
        metrics_button.pack(side=tk.LEFT, padx=2)
        
        # Configurar drag and drop para grupos
        item.bind("<ButtonPress-1>", lambda e, a=app: self.on_drag_start(e, a, item))
        item.bind("<B1-Motion>", self.on_drag_motion)
        item.bind("<ButtonRelease-1>", self.on_drag_release)
    
    def create_kanban_card(self, app, parent_frame):
        """Criar card para visualização kanban"""
        # Frame do card
        card = ttk.Frame(parent_frame, style="Card.TFrame")
        card.pack(fill=tk.X, padx=5, pady=5)
        
        # Adicionar borda
        card_border = ttk.Frame(card, style="Card.TFrame", relief="solid", borderwidth=1)
        card_border.pack(fill=tk.BOTH, expand=True)
        
        # Barra colorida superior
        color_bar = tk.Frame(card_border, background=app["color"], height=4)
        color_bar.pack(fill=tk.X)
        
        # Conteúdo do card
        content = ttk.Frame(card_border, style="Card.TFrame")
        content.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
        
        # Título (clicável para editar)
        title_var = tk.StringVar(value=app["name"])
        title = ttk.Label(content, textvariable=title_var, style="CardTitle.TLabel")
        title.pack(fill=tk.X)
        title.bind("<Double-Button-1>", lambda e, a=app, v=title_var: self.edit_app_name(a, v))
        
        # Descrição (curta)
        desc_text = app["description"]
        if len(desc_text) > 100:
            desc_text = desc_text[:97] + "..."
        
        desc_var = tk.StringVar(value=desc_text)
        desc = ttk.Label(content, textvariable=desc_var, style="CardDesc.TLabel", 
                       wraplength=250)
        desc.pack(fill=tk.X, pady=(5, 0))
        desc.bind("<Double-Button-1>", lambda e, a=app, v=desc_var: self.edit_app_description(a, v))
        
        # Botões de ação
        button_frame = ttk.Frame(content, style="Card.TFrame")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botão Executar
        is_running = app["file"] in self.backend.running_processes
        run_button = ttk.Button(button_frame, text="▶", style="Success.TButton",
                              command=lambda: self.run_app(app),
                              state="disabled" if is_running else "normal",
                              width=2)
        run_button.pack(side=tk.RIGHT, padx=2)
        
        # Botão Editar
        edit_button = ttk.Button(button_frame, text="✎", style="Primary.TButton",
                               command=lambda: self.edit_app(app),
                               width=2)
        edit_button.pack(side=tk.RIGHT, padx=2)
        
        # Configurar drag and drop para kanban
        card.bind("<ButtonPress-1>", lambda e, a=app: self.on_drag_start(e, a, card))
        card.bind("<B1-Motion>", self.on_drag_motion)
        card.bind("<ButtonRelease-1>", self.on_drag_release)
    
    def on_drag_start(self, event, app, widget):
        """Iniciar arrasto de um card"""
        self.drag_data["widget"] = widget
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["item"] = app
    
    def on_drag_motion(self, event):
        """Mover card durante arrasto"""
        if not self.drag_data["widget"]:
            return
        
        # Calcular nova posição
        x = self.drag_data["widget"].winfo_x() + event.x - self.drag_data["x"]
        y = self.drag_data["widget"].winfo_y() + event.y - self.drag_data["y"]
        
        # Mover widget
        self.drag_data["widget"].place(x=x, y=y, width=self.drag_data["widget"].winfo_width())
    
    def on_drag_release(self, event):
        """Finalizar arrasto de um card"""
        if not self.drag_data["widget"] or not self.drag_data["item"]:
            return
        
        # Verificar se está sobre um grupo
        for widget in self.groups_frame.winfo_children():
            if isinstance(widget, ttk.Button) and widget.winfo_class() == "TButton":
                # Obter coordenadas do botão
                x1 = widget.winfo_rootx()
                y1 = widget.winfo_rooty()
                x2 = x1 + widget.winfo_width()
                y2 = y1 + widget.winfo_height()
                
                # Verificar se o mouse está sobre o botão
                if (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
                    # Obter nome do grupo
                    group_name = widget.cget("text")
                    
                    # Adicionar app ao grupo
                    app_file = self.drag_data["item"]["file"]
                    success, message = self.backend.add_app_to_group(app_file, group_name)
                    
                    if success:
                        self.status_var.set(f"Aplicação adicionada ao grupo {group_name}")
                    else:
                        self.status_var.set(message)
                    
                    # Atualizar exibição
                    self.scan_apps()
                    break
        
        # Restaurar widget
        self.drag_data["widget"].place_forget()
        self.update_app_display()
        
        # Limpar dados de arrasto
        self.drag_data = {"widget": None, "x": 0, "y": 0, "item": None}
    
    def on_kanban_drop(self, event, column):
        """Processar soltura de um card em uma coluna kanban"""
        if not self.drag_data["item"]:
            return
        
        # Atualizar estado kanban
        app_file = self.drag_data["item"]["file"]
        success, message = self.backend.update_kanban_state(app_file, column)
        
        if success:
            self.status_var.set(f"Aplicação movida para {column}")
        else:
            self.status_var.set(message)
        
        # Atualizar exibição
        self.scan_apps()
    
    def edit_app_name(self, app, title_var):
        """Editar nome da aplicação in-place"""
        new_name = simpledialog.askstring("Editar Nome", "Novo nome:", initialvalue=app["name"])
        if new_name:
            success, message = self.backend.update_app_metadata(app["file"], name=new_name)
            if success:
                title_var.set(new_name)
                app["name"] = new_name
                self.status_var.set("Nome atualizado com sucesso")
            else:
                self.status_var.set(message)
    
    def edit_app_description(self, app, desc_var):
        """Editar descrição da aplicação in-place"""
        new_desc = simpledialog.askstring("Editar Descrição", "Nova descrição:", initialvalue=app["description"])
        if new_desc:
            success, message = self.backend.update_app_metadata(app["file"], description=new_desc)
            if success:
                desc_var.set(new_desc)
                app["description"] = new_desc
                self.status_var.set("Descrição atualizada com sucesso")
            else:
                self.status_var.set(message)
    
    def run_app(self, app):
        """Executar uma aplicação"""
        success, message = self.backend.run_app(app["file"])
        
        if success:
            self.status_var.set(f"Executando: {app['name']}")
            # Atualizar app na lista
            app["last_run"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            app["run_count"] += 1
            # Atualizar exibição
            self.update_app_display()
        else:
            if "Dependências faltando" in message and self.backend.config["behavior"]["auto_check_dependencies"]:
                if messagebox.askyesno("Dependências Faltando", 
                                     f"{message}\n\nDeseja instalá-las agora?"):
                    missing_deps = self.backend.check_dependencies(app["dependencies"])
                    self.install_dependencies(missing_deps)
            else:
                messagebox.showerror("Erro", message)
    
    def stop_app(self, app):
        """Parar uma aplicação em execução"""
        if self.backend.config["behavior"]["confirm_app_close"]:
            if not messagebox.askyesno("Confirmar", f"Deseja encerrar a aplicação '{app['name']}'?"):
                return
        
        success, message = self.backend.stop_app(app["file"])
        
        if success:
            self.status_var.set(f"Aplicação '{app['name']}' encerrada")
            # Atualizar exibição
            self.update_app_display()
        else:
            messagebox.showerror("Erro", message)
    
    def edit_app(self, app):
        """Editar metadados de uma aplicação"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Editar {app['name']}")
        edit_window.geometry("500x500")
        edit_window.resizable(False, False)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(edit_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Aba de informações básicas
        basic_frame = ttk.Frame(notebook, padding=10)
        notebook.add(basic_frame, text="Informações Básicas")
        
        # Aba de grupos
        groups_frame = ttk.Frame(notebook, padding=10)
        notebook.add(groups_frame, text="Grupos")
        
        # Aba de dependências
        deps_frame = ttk.Frame(notebook, padding=10)
        notebook.add(deps_frame, text="Dependências")
        
        # Aba de kanban
        kanban_frame = ttk.Frame(notebook, padding=10)
        notebook.add(kanban_frame, text="Kanban")
        
        # Campos na aba básica
        ttk.Label(basic_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=app["name"])
        name_entry = ttk.Entry(basic_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(basic_frame, text="Categoria:").grid(row=1, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar(value=app["category"])
        category_combo = ttk.Combobox(basic_frame, textvariable=category_var, width=28)
        categories = list(set(a["category"] for a in self.apps))
        category_combo['values'] = categories
        category_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(basic_frame, text="Descrição:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        description_text = tk.Text(basic_frame, width=30, height=6)
        description_text.insert("1.0", app["description"])
        description_text.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(basic_frame, text="Cor:").grid(row=3, column=0, sticky=tk.W, pady=5)
        color_var = tk.StringVar(value=app["color"])
        
        # Frame para preview de cor
        color_frame = ttk.Frame(basic_frame)
        color_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        color_preview = tk.Frame(color_frame, width=30, height=20, background=app["color"])
        color_preview.pack(side=tk.LEFT, padx=(0, 5))
        
        color_button = ttk.Button(color_frame, text="Escolher Cor", 
                                command=lambda: self.choose_color(color_var, color_preview))
        color_button.pack(side=tk.LEFT)
        
        # Tags
        ttk.Label(basic_frame, text="Tags:").grid(row=4, column=0, sticky=tk.W, pady=5)
        tags_var = tk.StringVar(value=", ".join(app["tags"]))
        tags_entry = ttk.Entry(basic_frame, textvariable=tags_var, width=30)
        tags_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        ttk.Label(basic_frame, text="(separadas por vírgula)", foreground=self.colors["text_light"]).grid(row=4, column=2, sticky=tk.W, pady=5)
        
        # Campos na aba de grupos
        ttk.Label(groups_frame, text="Grupos Disponíveis:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Lista de grupos com checkboxes
        groups_listbox_frame = ttk.Frame(groups_frame)
        groups_listbox_frame.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        groups_vars = {}
        row = 0
        for group_name in self.backend.groups.keys():
            if group_name != "Todos":
                var = tk.BooleanVar(value=app["file"] in self.backend.groups[group_name])
                groups_vars[group_name] = var
                ttk.Checkbutton(groups_listbox_frame, text=group_name, variable=var).grid(row=row, column=0, sticky=tk.W)
                row += 1
        
        # Adicionar novo grupo
        ttk.Label(groups_frame, text="Novo Grupo:").grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        new_group_var = tk.StringVar()
        new_group_entry = ttk.Entry(groups_frame, textvariable=new_group_var, width=20)
        new_group_entry.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        add_group_button = ttk.Button(groups_frame, text="Adicionar Grupo", 
                                    command=lambda: self.add_new_group_from_edit(new_group_var.get(), groups_vars, groups_listbox_frame))
        add_group_button.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # Campos na aba de dependências
        ttk.Label(deps_frame, text="Dependências Detectadas:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        deps_text = tk.Text(deps_frame, width=40, height=10)
        deps_text.grid(row=1, column=0, sticky=tk.W, pady=5)
        deps_text.insert("1.0", "\n".join(app["dependencies"]))
        
        check_deps_button = ttk.Button(deps_frame, text="Verificar Dependências", 
                                     command=lambda: self.check_and_show_deps(app["dependencies"], deps_frame))
        check_deps_button.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        install_deps_button = ttk.Button(deps_frame, text="Instalar Dependências Faltantes", 
                                       command=lambda: self.install_deps_from_text(deps_text.get("1.0", tk.END)))
        install_deps_button.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Campos na aba de kanban
        ttk.Label(kanban_frame, text="Estado Kanban:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        kanban_var = tk.StringVar(value=app["kanban_state"])
        for i, column in enumerate(self.backend.kanban_columns):
            ttk.Radiobutton(kanban_frame, text=column, variable=kanban_var, value=column).grid(row=i+1, column=0, sticky=tk.W, pady=2)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        save_button = ttk.Button(button_frame, text="Salvar", style="Success.TButton",
                               command=lambda: self.save_app_edit(app, name_var.get(), 
                                                               category_var.get(), 
                                                               description_text.get("1.0", tk.END).strip(),
                                                               color_var.get(),
                                                               tags_var.get().split(","),
                                                               deps_text.get("1.0", tk.END).strip().split("\n"),
                                                               kanban_var.get(),
                                                               groups_vars,
                                                               edit_window))
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancelar", 
                                 command=edit_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def add_new_group_from_edit(self, group_name, groups_vars, parent_frame):
        """Adicionar um novo grupo a partir da tela de edição"""
        success, message = self.backend.create_group(group_name)
        
        if success:
            # Adicionar checkbox
            var = tk.BooleanVar(value=False)
            groups_vars[group_name] = var
            ttk.Checkbutton(parent_frame, text=group_name, variable=var).grid(row=len(groups_vars)-1, column=0, sticky=tk.W)
            self.status_var.set("Grupo criado com sucesso")
        else:
            messagebox.showerror("Erro", message)
    
    def check_and_show_deps(self, dependencies, parent_frame):
        """Verificar dependências e mostrar status"""
        missing = self.backend.check_dependencies(dependencies)
        
        # Limpar widgets existentes
        for widget in parent_frame.winfo_children():
            if isinstance(widget, ttk.Label) and hasattr(widget, 'dep_status'):
                widget.destroy()
        
        # Mostrar status
        ttk.Label(parent_frame, text="Status das Dependências:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(15, 5))
        
        row = 5
        for dep in dependencies:
            status = "Faltando" if dep in missing else "Instalado"
            color = self.colors["danger"] if dep in missing else self.colors["secondary"]
            label = ttk.Label(parent_frame, text=f"{dep}: {status}", foreground=color)
            label.dep_status = True
            label.grid(row=row, column=0, sticky=tk.W, pady=2)
            row += 1
    
    def install_deps_from_text(self, deps_text):
        """Instalar dependências a partir do texto"""
        deps = [dep.strip() for dep in deps_text.strip().split("\n") if dep.strip()]
        missing = self.backend.check_dependencies(deps)
        
        if missing:
            self.install_dependencies(missing)
        else:
            messagebox.showinfo("Dependências", "Todas as dependências já estão instaladas")
    
    def choose_color(self, color_var, color_preview):
        """Escolher cor para o card"""
        color = colorchooser.askcolor(initialcolor=color_var.get())[1]
        if color:
            color_var.set(color)
            color_preview.config(background=color)
    
    def save_app_edit(self, app, name, category, description, color, tags, dependencies, kanban_state, groups_vars, window):
        """Salvar edições de uma aplicação"""
        # Limpar tags
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        # Limpar dependências
        dependencies = [dep.strip() for dep in dependencies if dep.strip()]
        
        # Atualizar metadados
        success, message = self.backend.update_app_metadata(
            app["file"], 
            name=name,
            category=category,
            description=description,
            color=color,
            tags=tags,
            dependencies=dependencies
        )
        
        if not success:
            messagebox.showerror("Erro", message)
            return
        
        # Atualizar estado kanban
        success, message = self.backend.update_kanban_state(app["file"], kanban_state)
        
        if not success:
            messagebox.showerror("Erro", message)
            return
        
        # Atualizar grupos
        for group_name, var in groups_vars.items():
            if var.get() and app["file"] not in self.backend.groups[group_name]:
                self.backend.add_app_to_group(app["file"], group_name)
            elif not var.get() and app["file"] in self.backend.groups[group_name]:
                self.backend.remove_app_from_group(app["file"], group_name)
        
        # Atualizar exibição
        self.scan_apps()
        
        # Fechar janela
        window.destroy()
        
        # Mostrar mensagem de sucesso
        self.status_var.set("Aplicação atualizada com sucesso")
    
    def open_code(self, app):
        """Abrir código da aplicação no editor padrão"""
        success, message = self.backend.open_code(app["file"])
        
        if not success:
            messagebox.showerror("Erro", message)
    
    def create_new_app(self):
        """Criar uma nova aplicação"""
        new_app_window = tk.Toplevel(self.root)
        new_app_window.title("Criar Nova Aplicação")
        new_app_window.geometry("450x400")
        new_app_window.resizable(False, False)
        new_app_window.transient(self.root)
        new_app_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(new_app_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        ttk.Label(main_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Nome do Arquivo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        filename_var = tk.StringVar()
        filename_entry = ttk.Entry(main_frame, textvariable=filename_var, width=30)
        filename_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text=".py", foreground=self.colors["text_light"]).grid(row=1, column=2, sticky=tk.W)
        
        # Atualizar nome do arquivo quando o nome muda
        def update_filename(*args):
            filename = name_var.get().lower().replace(" ", "_")
            filename_var.set(filename)
        
        name_var.trace("w", update_filename)
        
        ttk.Label(main_frame, text="Categoria:").grid(row=2, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar(value="Outros")
        category_combo = ttk.Combobox(main_frame, textvariable=category_var, width=28)
        categories = list(set(a["category"] for a in self.apps))
        category_combo['values'] = categories
        category_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Descrição:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        description_text = tk.Text(main_frame, width=30, height=6)
        description_text.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Modelo:").grid(row=4, column=0, sticky=tk.W, pady=5)
        template_var = tk.StringVar(value="Básico")
        template_combo = ttk.Combobox(main_frame, textvariable=template_var, width=28)
        template_combo['values'] = ["Básico", "Aplicação GUI", "Aplicação Console", "Vazio"]
        template_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Grupo
        ttk.Label(main_frame, text="Grupo:").grid(row=5, column=0, sticky=tk.W, pady=5)
        group_var = tk.StringVar(value="Todos")
        group_combo = ttk.Combobox(main_frame, textvariable=group_var, width=28)
        group_combo['values'] = list(self.backend.groups.keys())
        group_combo.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=15)
        
        create_button = ttk.Button(button_frame, text="Criar", style="Success.TButton",
                                 command=lambda: self.create_app_file(
                                     name_var.get(),
                                     filename_var.get(),
                                     category_var.get(),
                                     description_text.get("1.0", tk.END).strip(),
                                     template_var.get(),
                                     group_var.get(),
                                     new_app_window))
        create_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancelar", 
                                 command=new_app_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def create_app_file(self, name, filename, category, description, template, group, window):
        """Criar um novo arquivo de aplicação"""
        success, message = self.backend.create_new_app(name, filename, category, description, template, group)
        
        if success:
            # Atualizar exibição
            self.scan_apps()
            
            # Fechar janela
            window.destroy()
            
            # Mostrar mensagem de sucesso
            self.status_var.set(message)
        else:
            messagebox.showerror("Erro", message)
    
    def manage_dependencies(self):
        """Gerenciar dependências de todas as aplicações"""
        deps_window = tk.Toplevel(self.root)
        deps_window.title("Gerenciador de Dependências")
        deps_window.geometry("600x500")
        deps_window.transient(self.root)
        deps_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(deps_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Gerenciador de Dependências", font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Aba de dependências de aplicações
        apps_deps_frame = ttk.Frame(notebook, padding=10)
        notebook.add(apps_deps_frame, text="Dependências de Aplicações")
        
        # Aba de gerenciamento de pip
        pip_frame = ttk.Frame(notebook, padding=10)
        notebook.add(pip_frame, text="Gerenciador de Pacotes")
        
        # Conteúdo da aba de dependências de aplicações
        ttk.Label(apps_deps_frame, text="Dependências por Aplicação:").pack(anchor=tk.W, pady=(0, 5))
        
        # Criar treeview para mostrar dependências
        deps_tree = ttk.Treeview(apps_deps_frame, columns=("app", "deps", "status"), show="headings")
        deps_tree.heading("app", text="Aplicação")
        deps_tree.heading("deps", text="Dependências")
        deps_tree.heading("status", text="Status")
        
        deps_tree.column("app", width=150)
        deps_tree.column("deps", width=250)
        deps_tree.column("status", width=100)
        
        deps_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Preencher treeview
        all_deps = {}
        for app in self.apps:
            deps_str = ", ".join(app["dependencies"]) if app["dependencies"] else "Nenhuma"
            missing = self.backend.check_dependencies(app["dependencies"])
            status = "Faltando" if missing else "OK"
            
            deps_tree.insert("", "end", values=(app["name"], deps_str, status))
            
            # Coletar todas as dependências
            for dep in app["dependencies"]:
                if dep not in all_deps:
                    all_deps[dep] = []
                all_deps[dep].append(app["name"])
        
        # Botões
        ttk.Button(apps_deps_frame, text="Verificar Todas", 
                 command=lambda: self.refresh_deps_tree(deps_tree)).pack(side=tk.LEFT, pady=10)
        
        ttk.Button(apps_deps_frame, text="Instalar Faltantes", 
                 command=lambda: self.install_all_missing_deps()).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Conteúdo da aba de gerenciamento de pip
        ttk.Label(pip_frame, text="Pacotes Instalados:").pack(anchor=tk.W, pady=(0, 5))
        
        # Criar treeview para mostrar pacotes
        packages_tree = ttk.Treeview(pip_frame, columns=("package", "version"), show="headings")
        packages_tree.heading("package", text="Pacote")
        packages_tree.heading("version", text="Versão")
        
        packages_tree.column("package", width=200)
        packages_tree.column("version", width=100)
        
        packages_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Preencher treeview de pacotes
        self.fill_packages_tree(packages_tree)
        
        # Frame para instalar pacote
        install_frame = ttk.Frame(pip_frame)
        install_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(install_frame, text="Instalar Pacote:").pack(side=tk.LEFT)
        
        package_var = tk.StringVar()
        package_entry = ttk.Entry(install_frame, textvariable=package_var, width=20)
        package_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(install_frame, text="Instalar", 
                 command=lambda: self.install_package(package_var.get(), packages_tree)).pack(side=tk.LEFT)
        
        # Botões
        ttk.Button(pip_frame, text="Atualizar Lista", 
                 command=lambda: self.fill_packages_tree(packages_tree)).pack(side=tk.LEFT, pady=10)
        
        ttk.Button(pip_frame, text="Atualizar Selecionado", 
                 command=lambda: self.update_selected_package(packages_tree)).pack(side=tk.LEFT, padx=10, pady=10)
        
        ttk.Button(pip_frame, text="Desinstalar Selecionado", 
                 command=lambda: self.uninstall_selected_package(packages_tree)).pack(side=tk.LEFT, padx=10, pady=10)
    
    def refresh_deps_tree(self, tree):
        """Atualizar treeview de dependências"""
        # Limpar treeview
        for item in tree.get_children():
            tree.delete(item)
        
        # Preencher treeview
        for app in self.apps:
            deps_str = ", ".join(app["dependencies"]) if app["dependencies"] else "Nenhuma"
            missing = self.backend.check_dependencies(app["dependencies"])
            status = "Faltando" if missing else "OK"
            
            tree.insert("", "end", values=(app["name"], deps_str, status))
    
    def install_all_missing_deps(self):
        """Instalar todas as dependências faltantes"""
        all_deps = []
        for app in self.apps:
            all_deps.extend(app["dependencies"])
        
        # Remover duplicatas
        all_deps = list(set(all_deps))
        
        # Verificar faltantes
        missing = self.backend.check_dependencies(all_deps)
        
        if missing:
            self.install_dependencies(missing)
        else:
            messagebox.showinfo("Dependências", "Todas as dependências já estão instaladas")
    
    def fill_packages_tree(self, tree):
        """Preencher treeview de pacotes instalados"""
        # Limpar treeview
        for item in tree.get_children():
            tree.delete(item)
        
        # Obter pacotes instalados
        packages = self.backend.get_installed_packages()
        
        # Adicionar à treeview
        for package in packages:
            tree.insert("", "end", values=(package["name"], package["version"]))
    
    def install_package(self, package_name, tree):
        """Instalar pacote via pip"""
        if not package_name:
            messagebox.showerror("Erro", "Nome do pacote é obrigatório")
            return
        
        # Criar janela de progresso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Instalando Pacote")
        progress_window.geometry("400x200")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Frame principal
        progress_frame = ttk.Frame(progress_window, padding=15)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label de status
        status_var = tk.StringVar(value=f"Instalando {package_name}...")
        status_label = ttk.Label(progress_frame, textvariable=status_var)
        status_label.pack(pady=(0, 10))
        
        # Área de log
        log_text = tk.Text(progress_frame, height=8, width=50)
        log_text.pack(fill=tk.BOTH, expand=True)
        
        # Função de callback
        def update_status(message, success):
            status_var.set(message)
            log_text.insert(tk.END, message + "\n")
            log_text.see(tk.END)
            
            if success is not None:
                # Adicionar botão de fechar
                ttk.Button(progress_frame, text="Fechar", 
                         command=progress_window.destroy).pack(pady=10)
                
                               # Atualizar lista de pacotes
                if success:
                    self.fill_packages_tree(tree)
        
        # Instalar pacote
        self.backend.install_package(package_name, update_status)
    
    def update_selected_package(self, tree):
        """Atualizar pacote selecionado"""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Seleção", "Selecione um pacote para atualizar")
            return
        
        # Obter nome do pacote
        package_name = tree.item(selection[0], "values")[0]
        
        # Criar janela de progresso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Atualizando Pacote")
        progress_window.geometry("400x200")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Frame principal
        progress_frame = ttk.Frame(progress_window, padding=15)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label de status
        status_var = tk.StringVar(value=f"Atualizando {package_name}...")
        status_label = ttk.Label(progress_frame, textvariable=status_var)
        status_label.pack(pady=(0, 10))
        
        # Área de log
        log_text = tk.Text(progress_frame, height=8, width=50)
        log_text.pack(fill=tk.BOTH, expand=True)
        
        # Função de callback
        def update_status(message, success):
            status_var.set(message)
            log_text.insert(tk.END, message + "\n")
            log_text.see(tk.END)
            
            if success is not None:
                # Adicionar botão de fechar
                ttk.Button(progress_frame, text="Fechar", 
                         command=progress_window.destroy).pack(pady=10)
                
                # Atualizar lista de pacotes
                if success:
                    self.fill_packages_tree(tree)
        
        # Atualizar pacote
        self.backend.install_package(f"{package_name} --upgrade", update_status)
    
    def uninstall_selected_package(self, tree):
        """Desinstalar pacote selecionado"""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Seleção", "Selecione um pacote para desinstalar")
            return
        
        # Obter nome do pacote
        package_name = tree.item(selection[0], "values")[0]
        
        # Confirmar desinstalação
        if not messagebox.askyesno("Confirmar", f"Deseja desinstalar o pacote {package_name}?"):
            return
        
        # Criar janela de progresso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Desinstalando Pacote")
        progress_window.geometry("400x200")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Frame principal
        progress_frame = ttk.Frame(progress_window, padding=15)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label de status
        status_var = tk.StringVar(value=f"Desinstalando {package_name}...")
        status_label = ttk.Label(progress_frame, textvariable=status_var)
        status_label.pack(pady=(0, 10))
        
        # Área de log
        log_text = tk.Text(progress_frame, height=8, width=50)
        log_text.pack(fill=tk.BOTH, expand=True)
        
        # Função de callback
        def update_status(message, success):
            status_var.set(message)
            log_text.insert(tk.END, message + "\n")
            log_text.see(tk.END)
            
            if success is not None:
                # Adicionar botão de fechar
                ttk.Button(progress_frame, text="Fechar", 
                         command=progress_window.destroy).pack(pady=10)
                
                # Atualizar lista de pacotes
                if success:
                    self.fill_packages_tree(tree)
        
        # Desinstalar pacote
        self.backend.uninstall_package(package_name, update_status)
    
    def install_dependencies(self, dependencies):
        """Instalar dependências faltantes"""
        if not dependencies:
            messagebox.showinfo("Dependências", "Todas as dependências já estão instaladas")
            return
        
        # Criar janela de progresso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Instalando Dependências")
        progress_window.geometry("400x300")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(progress_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label de status
        status_var = tk.StringVar(value="Preparando para instalar dependências...")
        status_label = ttk.Label(main_frame, textvariable=status_var)
        status_label.pack(pady=(0, 10))
        
        # Área de log
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_text = tk.Text(log_frame, height=10, width=50)
        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Função de callback
        def update_status(message, success):
            log_text.insert(tk.END, message + "\n")
            log_text.see(tk.END)
            
            if success is not None:
                status_var.set("Instalação concluída")
                # Adicionar botão de fechar
                ttk.Button(main_frame, text="Fechar", 
                         command=progress_window.destroy).pack(pady=10)
        
        # Instalar dependências
        self.backend.install_dependencies(dependencies, update_status)
    
    def manage_groups(self):
        """Gerenciar grupos de aplicações"""
        groups_window = tk.Toplevel(self.root)
        groups_window.title("Gerenciador de Grupos")
        groups_window.geometry("500x400")
        groups_window.transient(self.root)
        groups_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(groups_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Gerenciador de Grupos", font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Frame para lista de grupos
        groups_frame = ttk.Frame(main_frame)
        groups_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Lista de grupos
        ttk.Label(groups_frame, text="Grupos:").pack(anchor=tk.W, pady=(0, 5))
        
        groups_listbox = tk.Listbox(groups_frame, height=10)
        groups_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        groups_scrollbar = ttk.Scrollbar(groups_frame, orient=tk.VERTICAL, command=groups_listbox.yview)
        groups_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        groups_listbox.config(yscrollcommand=groups_scrollbar.set)
        
        # Preencher lista de grupos
        for group in self.backend.groups.keys():
            groups_listbox.insert(tk.END, group)
        
        # Frame para detalhes do grupo
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label para detalhes
        details_label = ttk.Label(details_frame, text="Selecione um grupo para ver detalhes")
        details_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Lista de aplicações no grupo
        apps_listbox = tk.Listbox(details_frame, height=8)
        apps_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Função para mostrar detalhes do grupo
        def show_group_details(event):
            selection = groups_listbox.curselection()
            if selection:
                group_name = groups_listbox.get(selection[0])
                details_label.config(text=f"Aplicações no grupo '{group_name}':")
                
                # Limpar lista
                apps_listbox.delete(0, tk.END)
                
                # Preencher com aplicações do grupo
                if group_name in self.backend.groups:
                    for file in self.backend.groups[group_name]:
                        # Encontrar nome da aplicação
                        app_name = file
                        for app in self.apps:
                            if app["file"] == file:
                                app_name = app["name"]
                                break
                        
                        apps_listbox.insert(tk.END, app_name)
        
        # Vincular evento de seleção
        groups_listbox.bind("<<ListboxSelect>>", show_group_details)
        
        # Frame para botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Botão para adicionar grupo
        def add_group():
            group_name = simpledialog.askstring("Novo Grupo", "Nome do grupo:", parent=groups_window)
            if group_name:
                success, message = self.backend.create_group(group_name)
                if success:
                    groups_listbox.insert(tk.END, group_name)
                    self.update_groups_display()
                else:
                    messagebox.showerror("Erro", message)
        
        add_button = ttk.Button(buttons_frame, text="Adicionar Grupo", command=add_group)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botão para remover grupo
        def remove_group():
            selection = groups_listbox.curselection()
            if selection:
                group_name = groups_listbox.get(selection[0])
                success, message = self.backend.delete_group(group_name)
                if success:
                    groups_listbox.delete(selection[0])
                    apps_listbox.delete(0, tk.END)
                    details_label.config(text="Selecione um grupo para ver detalhes")
                    self.update_groups_display()
                else:
                    messagebox.showerror("Erro", message)
        
        remove_button = ttk.Button(buttons_frame, text="Remover Grupo", command=remove_group)
        remove_button.pack(side=tk.LEFT, padx=5)
        
        # Botão para renomear grupo
        def rename_group():
            selection = groups_listbox.curselection()
            if selection:
                old_name = groups_listbox.get(selection[0])
                new_name = simpledialog.askstring("Renomear Grupo", "Novo nome:", parent=groups_window, initialvalue=old_name)
                if new_name:
                    success, message = self.backend.rename_group(old_name, new_name)
                    if success:
                        groups_listbox.delete(selection[0])
                        groups_listbox.insert(selection[0], new_name)
                        self.update_groups_display()
                    else:
                        messagebox.showerror("Erro", message)
        
        rename_button = ttk.Button(buttons_frame, text="Renomear Grupo", command=rename_group)
        rename_button.pack(side=tk.LEFT, padx=5)
    
    def manage_kanban_columns(self):
        """Gerenciar colunas do kanban"""
        columns_window = tk.Toplevel(self.root)
        columns_window.title("Gerenciar Colunas Kanban")
        columns_window.geometry("400x300")
        columns_window.transient(self.root)
        columns_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(columns_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Gerenciar Colunas Kanban", font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Frame para lista de colunas
        columns_frame = ttk.Frame(main_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Lista de colunas
        ttk.Label(columns_frame, text="Colunas:").pack(anchor=tk.W, pady=(0, 5))
        
        columns_listbox = tk.Listbox(columns_frame, height=10)
        columns_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        columns_scrollbar = ttk.Scrollbar(columns_frame, orient=tk.VERTICAL, command=columns_listbox.yview)
        columns_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        columns_listbox.config(yscrollcommand=columns_scrollbar.set)
        
        # Preencher lista de colunas
        for column in self.backend.kanban_columns:
            columns_listbox.insert(tk.END, column)
        
        # Frame para botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Botão para adicionar coluna
        def add_column():
            column_name = simpledialog.askstring("Nova Coluna", "Nome da coluna:", parent=columns_window)
            if column_name and column_name not in self.backend.kanban_columns:
                columns = self.backend.kanban_columns.copy()
                columns.append(column_name)
                success, message = self.backend.update_kanban_columns(columns)
                if success:
                    columns_listbox.insert(tk.END, column_name)
                    self.update_app_display()
                else:
                    messagebox.showerror("Erro", message)
        
        add_button = ttk.Button(buttons_frame, text="Adicionar Coluna", command=add_column)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botão para remover coluna
        def remove_column():
            selection = columns_listbox.curselection()
            if selection:
                column_name = columns_listbox.get(selection[0])
                if len(self.backend.kanban_columns) <= 1:
                    messagebox.showerror("Erro", "É necessário pelo menos uma coluna")
                    return
                
                columns = [col for col in self.backend.kanban_columns if col != column_name]
                success, message = self.backend.update_kanban_columns(columns)
                if success:
                    columns_listbox.delete(selection[0])
                    self.update_app_display()
                else:
                    messagebox.showerror("Erro", message)
        
        remove_button = ttk.Button(buttons_frame, text="Remover Coluna", command=remove_column)
        remove_button.pack(side=tk.LEFT, padx=5)
        
        # Botão para mover coluna para cima
        def move_up():
            selection = columns_listbox.curselection()
            if selection and selection[0] > 0:
                idx = selection[0]
                column_name = columns_listbox.get(idx)
                
                columns = self.backend.kanban_columns.copy()
                columns.remove(column_name)
                columns.insert(idx - 1, column_name)
                
                success, message = self.backend.update_kanban_columns(columns)
                if success:
                    columns_listbox.delete(idx)
                    columns_listbox.insert(idx - 1, column_name)
                    columns_listbox.selection_set(idx - 1)
                    self.update_app_display()
                else:
                    messagebox.showerror("Erro", message)
        
        move_up_button = ttk.Button(buttons_frame, text="Mover ▲", command=move_up)
        move_up_button.pack(side=tk.LEFT, padx=5)
        
        # Botão para mover coluna para baixo
        def move_down():
            selection = columns_listbox.curselection()
            if selection and selection[0] < columns_listbox.size() - 1:
                idx = selection[0]
                column_name = columns_listbox.get(idx)
                
                columns = self.backend.kanban_columns.copy()
                columns.remove(column_name)
                columns.insert(idx + 1, column_name)
                
                success, message = self.backend.update_kanban_columns(columns)
                if success:
                    columns_listbox.delete(idx)
                    columns_listbox.insert(idx + 1, column_name)
                    columns_listbox.selection_set(idx + 1)
                    self.update_app_display()
                else:
                    messagebox.showerror("Erro", message)
        
        move_down_button = ttk.Button(buttons_frame, text="Mover ▼", command=move_down)
        move_down_button.pack(side=tk.LEFT, padx=5)
    
    def show_dashboard(self):
        """Mostrar dashboard de estatísticas"""
        dashboard_window = tk.Toplevel(self.root)
        dashboard_window.title("Dashboard de Estatísticas")
        dashboard_window.geometry("800x600")
        dashboard_window.transient(self.root)
        
        # Frame principal
        main_frame = ttk.Frame(dashboard_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Dashboard de Estatísticas", font=("Arial", 16, "bold")).pack(pady=(0, 15))
        
        # Obter estatísticas
        stats = self.backend.get_app_statistics()
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de visão geral
        overview_frame = ttk.Frame(notebook, padding=10)
        notebook.add(overview_frame, text="Visão Geral")
        
        # Aba de uso de aplicações
        usage_frame = ttk.Frame(notebook, padding=10)
        notebook.add(usage_frame, text="Uso de Aplicações")
        
        # Aba de desempenho
        performance_frame = ttk.Frame(notebook, padding=10)
        notebook.add(performance_frame, text="Desempenho")
        
        # Aba de categorias
        categories_frame = ttk.Frame(notebook, padding=10)
        notebook.add(categories_frame, text="Categorias")
        
        # Conteúdo da aba de visão geral
        overview_top_frame = ttk.Frame(overview_frame)
        overview_top_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Estatísticas gerais
        stats_frame = ttk.Frame(overview_top_frame, relief="solid", borderwidth=1)
        stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(stats_frame, text="Estatísticas Gerais", font=("Arial", 12, "bold")).pack(pady=5)
        
        total_runtime_str = f"{stats['total_runtime']/3600:.1f} horas" if stats['total_runtime'] > 3600 else f"{stats['total_runtime']/60:.1f} minutos"
        
        ttk.Label(stats_frame, text=f"Total de Aplicações: {stats['total_apps']}").pack(anchor=tk.W, padx=10, pady=2)
        ttk.Label(stats_frame, text=f"Total de Execuções: {stats['total_runs']}").pack(anchor=tk.W, padx=10, pady=2)
        ttk.Label(stats_frame, text=f"Tempo Total de Execução: {total_runtime_str}").pack(anchor=tk.W, padx=10, pady=2)
        
        # Aplicações mais usadas
        top_apps_frame = ttk.Frame(overview_top_frame, relief="solid", borderwidth=1)
        top_apps_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        ttk.Label(top_apps_frame, text="Aplicações Mais Usadas", font=("Arial", 12, "bold")).pack(pady=5)
        
        for app in stats['top_apps']:
            ttk.Label(top_apps_frame, text=f"{app['name']}: {app['run_count']} execuções").pack(anchor=tk.W, padx=10, pady=2)
        
        # Gráfico de execuções por dia
        if stats['executions_by_day']['dates']:
            fig, ax = plt.subplots(figsize=(8, 4))
            
            dates = stats['executions_by_day']['dates']
            counts = stats['executions_by_day']['executions']
            
            ax.bar(dates, counts, color=self.colors["primary"])
            ax.set_xlabel("Data")
            ax.set_ylabel("Execuções")
            ax.set_title("Execuções por Dia")
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Adicionar gráfico à interface
            canvas = FigureCanvasTkAgg(fig, master=overview_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(overview_frame, text="Sem dados de execução suficientes para gerar gráfico").pack(pady=20)
        
        # Conteúdo da aba de uso de aplicações
        if stats['top_apps']:
            fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            
            # Dados para gráfico de pizza
            app_names = [app["name"] for app in stats['top_apps']]
            app_runs = [app["run_count"] for app in stats['top_apps']]
            
            ax1.pie(app_runs, labels=app_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax1.set_title("Distribuição de Execuções")
            
            # Gráfico de barras para tempo de execução
            top_runtime_apps = sorted(self.apps, key=lambda x: x["total_runtime"], reverse=True)[:5]
            app_names = [app["name"] for app in top_runtime_apps]
            app_runtimes = [app["total_runtime"]/60 for app in top_runtime_apps]  # Converter para minutos
            
            ax2.barh(app_names, app_runtimes, color=self.colors["secondary"])
            ax2.set_xlabel("Tempo de Execução (minutos)")
            ax2.set_title("Tempo Total de Execução")
            
            plt.tight_layout()
            
            # Adicionar gráfico à interface
            canvas2 = FigureCanvasTkAgg(fig2, master=usage_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(usage_frame, text="Sem dados de execução suficientes para gerar gráficos").pack(pady=20)
        
        # Conteúdo da aba de desempenho
        perf_apps = sorted(self.apps, key=lambda x: x["avg_cpu"], reverse=True)[:5]
        if perf_apps:
            fig3, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
            
            # Dados para gráficos de desempenho
            app_names = [app["name"] for app in perf_apps]
            app_cpu = [app["avg_cpu"] for app in perf_apps]
            
            ax1.barh(app_names, app_cpu, color=self.colors["primary"])
            ax1.set_xlabel("Uso de CPU (%)")
            ax1.set_title("Uso Médio de CPU")
            
            # Ordenar por uso de memória
            mem_apps = sorted(self.apps, key=lambda x: x["avg_memory"], reverse=True)[:5]
            app_names = [app["name"] for app in mem_apps]
            app_memory = [app["avg_memory"] for app in mem_apps]
            
            ax2.barh(app_names, app_memory, color=self.colors["accent"])
            ax2.set_xlabel("Uso de Memória (MB)")
            ax2.set_title("Uso Médio de Memória")
            
            plt.tight_layout()
            
            # Adicionar gráfico à interface
            canvas3 = FigureCanvasTkAgg(fig3, master=performance_frame)
            canvas3.draw()
            canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(performance_frame, text="Sem dados de desempenho suficientes para gerar gráficos").pack(pady=20)
        
        # Conteúdo da aba de categorias
        if stats['categories']:
            fig4, ax = plt.subplots(figsize=(8, 6))
            
            categories = list(stats['categories'].keys())
            counts = list(stats['categories'].values())
            
            ax.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90, colors=plt.cm.tab10.colors)
            ax.set_title("Distribuição de Aplicações por Categoria")
            
            plt.tight_layout()
            
            # Adicionar gráfico à interface
            canvas4 = FigureCanvasTkAgg(fig4, master=categories_frame)
            canvas4.draw()
            canvas4.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(categories_frame, text="Sem dados de categorias suficientes para gerar gráfico").pack(pady=20)
    
    def show_app_metrics(self, app):
        """Mostrar métricas detalhadas de uma aplicação"""
        metrics_window = tk.Toplevel(self.root)
        metrics_window.title(f"Métricas: {app['name']}")
        metrics_window.geometry("700x500")
        metrics_window.transient(self.root)
        
        # Frame principal
        main_frame = ttk.Frame(metrics_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text=f"Métricas: {app['name']}", font=("Arial", 16, "bold")).pack(pady=(0, 15))
        
        # Obter métricas
        metrics = self.backend.get_app_metrics(app["file"])
        
        if not metrics:
            ttk.Label(main_frame, text="Não foi possível obter métricas para esta aplicação").pack(pady=20)
            return
        
        # Estatísticas básicas
        stats_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1)
        stats_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        ttk.Label(stats_frame, text="Estatísticas de Uso", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Formatar tempo total
        total_runtime = app["total_runtime"]
        if total_runtime > 3600:
            runtime_str = f"{total_runtime/3600:.2f} horas"
        elif total_runtime > 60:
            runtime_str = f"{total_runtime/60:.2f} minutos"
        else:
            runtime_str = f"{total_runtime:.2f} segundos"
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(stats_grid, text="Total de Execuções:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(stats_grid, text=str(app["run_count"])).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="Tempo Total de Execução:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(stats_grid, text=runtime_str).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="Última Execução:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(stats_grid, text=app["last_run"]).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="Uso Médio de CPU:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(20, 0))
        ttk.Label(stats_grid, text=f"{app['avg_cpu']:.2f}%").grid(row=0, column=3, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="Uso Médio de Memória:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(20, 0))
        ttk.Label(stats_grid, text=f"{app['avg_memory']:.2f} MB").grid(row=1, column=3, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="Categoria:").grid(row=2, column=2, sticky=tk.W, pady=2, padx=(20, 0))
        ttk.Label(stats_grid, text=app["category"]).grid(row=2, column=3, sticky=tk.W, pady=2)
        
        # Notebook para gráficos
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de histórico de execução
        history_frame = ttk.Frame(notebook, padding=10)
        notebook.add(history_frame, text="Histórico de Execução")
        
        # Aba de desempenho
        performance_frame = ttk.Frame(notebook, padding=10)
        notebook.add(performance_frame, text="Desempenho")
        
        # Conteúdo da aba de histórico
        if metrics['history']:
            # Gráfico de histórico de execução
            fig, ax = plt.subplots(figsize=(8, 4))
            
            dates = [run["date"] for run in metrics['history']]
            runtimes = [run["runtime"]/60 for run in metrics['history']]  # Converter para minutos
            
            ax.bar(dates, runtimes, color=self.colors["primary"])
            ax.set_xlabel("Data")
            ax.set_ylabel("Tempo de Execução (minutos)")
            ax.set_title("Histórico de Tempo de Execução")
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Adicionar gráfico à interface
            canvas = FigureCanvasTkAgg(fig, master=history_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(history_frame, text="Sem histórico de execução disponível").pack(pady=20)
        
        # Conteúdo da aba de desempenho
        if metrics['history']:
            # Gráfico de CPU e memória
            fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
            
            dates = [run["date"] for run in metrics['history']]
            cpu_values = [run["avg_cpu"] for run in metrics['history']]
            memory_values = [run["avg_memory"] for run in metrics['history']]
            
            ax1.plot(dates, cpu_values, 'o-', color=self.colors["primary"])
            ax1.set_xlabel("Data")
            ax1.set_ylabel("CPU (%)")
            ax1.set_title("Histórico de Uso de CPU")
            plt.setp(ax1.get_xticklabels(), rotation=45)
            
            ax2.plot(dates, memory_values, 'o-', color=self.colors["accent"])
            ax2.set_xlabel("Data")
            ax2.set_ylabel("Memória (MB)")
            ax2.set_title("Histórico de Uso de Memória")
            plt.setp(ax2.get_xticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Adicionar gráfico à interface
            canvas2 = FigureCanvasTkAgg(fig2, master=performance_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(performance_frame, text="Sem dados de desempenho disponíveis").pack(pady=20)
    
    def show_settings(self):
        """Mostrar tela de configurações"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configurações")
        settings_window.geometry("700x600")
        settings_window.transient(self.root)
        
        # Frame principal
        main_frame = ttk.Frame(settings_window, style="Settings.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Configurações", font=("Arial", 16, "bold")).pack(pady=(0, 15))
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Aba de aparência
        appearance_frame = ttk.Frame(notebook, style="Settings.TFrame")
        notebook.add(appearance_frame, text="Aparência")
        
        # Aba de layout
        layout_frame = ttk.Frame(notebook, style="Settings.TFrame")
        notebook.add(layout_frame, text="Layout")
        
        # Aba de comportamento
        behavior_frame = ttk.Frame(notebook, style="Settings.TFrame")
        notebook.add(behavior_frame, text="Comportamento")
        
        # Aba de avançado
        advanced_frame = ttk.Frame(notebook, style="Settings.TFrame")
        notebook.add(advanced_frame, text="Avançado")
        
        # Conteúdo da aba de aparência
        appearance_section = ttk.Frame(appearance_frame, style="SettingsSection.TFrame")
        appearance_section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(appearance_section, text="Tema", style="SettingsTitle.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Tema
        theme_frame = ttk.Frame(appearance_section)
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        theme_var = tk.StringVar(value=self.backend.config["theme"])
        ttk.Radiobutton(theme_frame, text="Claro", variable=theme_var, value="light").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(theme_frame, text="Escuro", variable=theme_var, value="dark").pack(side=tk.LEFT)
        
        # Cores
        ttk.Label(appearance_section, text="Cores", style="SettingsSubtitle.TLabel").pack(anchor=tk.W, padx=10, pady=(15, 5))
        
        colors_frame = ttk.Frame(appearance_section)
        colors_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Cores primárias
        primary_frame = ttk.Frame(colors_frame)
        primary_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(primary_frame, text="Cor Primária:").pack(side=tk.LEFT)
        
        primary_color = self.backend.config["colors"][theme_var.get()]["primary"]
        primary_var = tk.StringVar(value=primary_color)
        
        primary_preview = tk.Frame(primary_frame, width=20, height=20, background=primary_color)
        primary_preview.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(primary_frame, text="Escolher", 
                 command=lambda: self.choose_theme_color(theme_var.get(), "primary", primary_var, primary_preview)).pack(side=tk.LEFT)
        
        # Cores secundárias
        secondary_frame = ttk.Frame(colors_frame)
        secondary_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(secondary_frame, text="Cor Secundária:").pack(side=tk.LEFT)
        
        secondary_color = self.backend.config["colors"][theme_var.get()]["secondary"]
        secondary_var = tk.StringVar(value=secondary_color)
        
        secondary_preview = tk.Frame(secondary_frame, width=20, height=20, background=secondary_color)
        secondary_preview.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(secondary_frame, text="Escolher", 
                 command=lambda: self.choose_theme_color(theme_var.get(), "secondary", secondary_var, secondary_preview)).pack(side=tk.LEFT)
        
        # Fonte
        ttk.Label(appearance_section, text="Fonte", style="SettingsSubtitle.TLabel").pack(anchor=tk.W, padx=10, pady=(15, 5))
        
        font_frame = ttk.Frame(appearance_section)
        font_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(font_frame, text="Família:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        font_family_var = tk.StringVar(value=self.backend.config["font"]["family"])
        font_family_combo = ttk.Combobox(font_frame, textvariable=font_family_var, width=20)
        font_family_combo['values'] = ["Arial", "Helvetica", "Verdana", "Tahoma", "Calibri", "Segoe UI"]
        font_family_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(font_frame, text="Tamanho Normal:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        font_size_var = tk.IntVar(value=self.backend.config["font"]["size"]["normal"])
        font_size_combo = ttk.Combobox(font_frame, textvariable=font_size_var, width=5)
        font_size_combo['values'] = [8, 9, 10, 11, 12, 14]
        font_size_combo.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Conteúdo da aba de layout
        layout_section = ttk.Frame(layout_frame, style="SettingsSection.TFrame")
        layout_section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(layout_section, text="Visualização em Grade", style="SettingsTitle.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Tamanho do card
        card_frame = ttk.Frame(layout_section)
        card_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(card_frame, text="Tamanho do Card:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        card_size_var = tk.IntVar(value=self.backend.config["layout"]["card_size"])
        card_size_scale = ttk.Scale(card_frame, from_=120, to=200, variable=card_size_var, orient=tk.HORIZONTAL, length=200)
        card_size_scale.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        card_size_label = ttk.Label(card_frame, textvariable=card_size_var)
        card_size_label.grid(row=0, column=2, sticky=tk.W, pady=2, padx=5)
        
        # Número máximo de colunas
        ttk.Label(card_frame, text="Máximo de Colunas:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        max_cols_var = tk.IntVar(value=self.backend.config["layout"]["max_columns"])
        max_cols_combo = ttk.Combobox(card_frame, textvariable=max_cols_var, width=5)
        max_cols_combo['values'] = [3, 4, 5, 6, 7, 8]
        max_cols_combo.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Mostrar descrição em grid
        show_desc_var = tk.BooleanVar(value=self.backend.config["layout"]["show_description_in_grid"])
        ttk.Checkbutton(card_frame, text="Mostrar descrição nos cards", variable=show_desc_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Label(layout_section, text="Visualização em Lista", style="SettingsTitle.TLabel").pack(anchor=tk.W, padx=10, pady=(15, 5))
        
        # Opções de lista
        list_frame = ttk.Frame(layout_section)
        list_frame.pack(fill=tk.X, padx=10, pady=5)
        
        compact_list_var = tk.BooleanVar(value=self.backend.config["layout"]["compact_list_view"])
        ttk.Checkbutton(list_frame, text="Visualização compacta", variable=compact_list_var).pack(anchor=tk.W, pady=2)
        
        show_tags_var = tk.BooleanVar(value=self.backend.config["layout"]["show_tags_in_list"])
        ttk.Checkbutton(list_frame, text="Mostrar tags", variable=show_tags_var).pack(anchor=tk.W, pady=2)
        
        show_metrics_var = tk.BooleanVar(value=self.backend.config["layout"]["show_metrics_in_list"])
        ttk.Checkbutton(list_frame, text="Mostrar métricas", variable=show_metrics_var).pack(anchor=tk.W, pady=2)
        
        # Conteúdo da aba de comportamento
        behavior_section = ttk.Frame(behavior_frame, style="SettingsSection.TFrame")
        behavior_section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(behavior_section, text="Comportamento Geral", style="SettingsTitle.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Opções de comportamento
        behavior_options_frame = ttk.Frame(behavior_section)
        behavior_options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        confirm_close_var = tk.BooleanVar(value=self.backend.config["behavior"]["confirm_app_close"])
        ttk.Checkbutton(behavior_options_frame, text="Confirmar encerramento de aplicações", variable=confirm_close_var).pack(anchor=tk.W, pady=2)
        
        check_deps_var = tk.BooleanVar(value=self.backend.config["behavior"]["auto_check_dependencies"])
        ttk.Checkbutton(behavior_options_frame, text="Verificar dependências automaticamente", variable=check_deps_var).pack(anchor=tk.W, pady=2)
        
        show_notif_var = tk.BooleanVar(value=self.backend.config["behavior"]["show_notifications"])
        ttk.Checkbutton(behavior_options_frame, text="Mostrar notificações", variable=show_notif_var).pack(anchor=tk.W, pady=2)
        
        # Atualização automática
        ttk.Label(behavior_section, text="Atualização Automática", style="SettingsSubtitle.TLabel").pack(anchor=tk.W, padx=10, pady=(15, 5))
        
        refresh_frame = ttk.Frame(behavior_section)
        refresh_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(refresh_frame, text="Intervalo de Atualização (segundos):").pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_var = tk.IntVar(value=self.backend.config["behavior"]["auto_refresh_interval"])
        refresh_combo = ttk.Combobox(refresh_frame, textvariable=refresh_var, width=5)
        refresh_combo['values'] = [0, 5, 10, 30, 60, 300, 600]
        refresh_combo.pack(side=tk.LEFT)
        
        ttk.Label(refresh_frame, text="(0 = desativado)").pack(side=tk.LEFT, padx=5)
        
        # Visualização padrão
        ttk.Label(behavior_section, text="Visualização Padrão", style="SettingsSubtitle.TLabel").pack(anchor=tk.W, padx=10, pady=(15, 5))
        
        view_frame = ttk.Frame(behavior_section)
        view_frame.pack(fill=tk.X, padx=10, pady=5)
        
        view_var = tk.StringVar(value=self.backend.config["behavior"]["default_view"])
        ttk.Radiobutton(view_frame, text="Grade", variable=view_var, value="grid").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(view_frame, text="Lista", variable=view_var, value="list").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(view_frame, text="Kanban", variable=view_var, value="kanban").pack(side=tk.LEFT)
        
        # Ordenação padrão
        ttk.Label(behavior_section, text="Ordenação Padrão", style="SettingsSubtitle.TLabel").pack(anchor=tk.W, padx=10, pady=(15, 5))
        
        sort_frame = ttk.Frame(behavior_section)
        sort_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(sort_frame, text="Ordenar por:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        sort_var = tk.StringVar(value=self.backend.config["behavior"]["default_sort"])
        sort_combo = ttk.Combobox(sort_frame, textvariable=sort_var, width=15)
        sort_combo['values'] = ["name", "last_run", "run_count"]
        sort_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(sort_frame, text="Direção:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        sort_dir_var = tk.StringVar(value=self.backend.config["behavior"]["default_sort_direction"])
        sort_dir_combo = ttk.Combobox(sort_frame, textvariable=sort_dir_var, width=15)
        sort_dir_combo['values'] = ["asc", "desc"]
        sort_dir_combo.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Conteúdo da aba avançada
        advanced_section = ttk.Frame(advanced_frame, style="SettingsSection.TFrame")
        advanced_section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(advanced_section, text="Configurações Avançadas", style="SettingsTitle.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Botão para exportar configurações
        export_button = ttk.Button(advanced_section, text="Exportar Configurações", 
                                 command=lambda: self.export_settings())
        export_button.pack(anchor=tk.W, padx=10, pady=5)
        
        # Botão para importar configurações
        import_button = ttk.Button(advanced_section, text="Importar Configurações", 
                                 command=lambda: self.import_settings())
        import_button.pack(anchor=tk.W, padx=10, pady=5)
        
        # Botão para redefinir configurações
        reset_button = ttk.Button(advanced_section, text="Redefinir Configurações", 
                                command=lambda: self.reset_settings())
        reset_button.pack(anchor=tk.W, padx=10, pady=5)
        
        # Botões de ação
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        save_button = ttk.Button(buttons_frame, text="Salvar", style="Success.TButton",
                               command=lambda: self.save_settings(
                                   theme_var.get(),
                                   primary_var.get(),
                                   secondary_var.get(),
                                   font_family_var.get(),
                                   font_size_var.get(),
                                   card_size_var.get(),
                                   max_cols_var.get(),
                                   show_desc_var.get(),
                                   compact_list_var.get(),
                                   show_tags_var.get(),
                                   show_metrics_var.get(),
                                   confirm_close_var.get(),
                                   check_deps_var.get(),
                                   show_notif_var.get(),
                                   refresh_var.get(),
                                   view_var.get(),
                                   sort_var.get(),
                                   sort_dir_var.get(),
                                   settings_window
                               ))
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(buttons_frame, text="Cancelar", 
                                 command=settings_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def choose_theme_color(self, theme, color_key, color_var, color_preview):
        """Escolher cor para o tema"""
        color = colorchooser.askcolor(initialcolor=color_var.get())[1]
        if color:
            color_var.set(color)
            color_preview.config(background=color)
    
    def save_settings(self, theme, primary_color, secondary_color, font_family, font_size, 
                    card_size, max_cols, show_desc, compact_list, show_tags, show_metrics,
                    confirm_close, check_deps, show_notif, refresh_interval, default_view,
                    default_sort, default_sort_dir, window):
        """Salvar configurações"""
        # Atualizar configurações
        self.backend.config["theme"] = theme
        self.backend.config["colors"][theme]["primary"] = primary_color
        self.backend.config["colors"][theme]["secondary"] = secondary_color
        self.backend.config["font"]["family"] = font_family
        self.backend.config["font"]["size"]["normal"] = font_size
        self.backend.config["layout"]["card_size"] = card_size
        self.backend.config["layout"]["max_columns"] = max_cols
        self.backend.config["layout"]["show_description_in_grid"] = show_desc
        self.backend.config["layout"]["compact_list_view"] = compact_list
        self.backend.config["layout"]["show_tags_in_list"] = show_tags
        self.backend.config["layout"]["show_metrics_in_list"] = show_metrics
        self.backend.config["behavior"]["confirm_app_close"] = confirm_close
        self.backend.config["behavior"]["auto_check_dependencies"] = check_deps
        self.backend.config["behavior"]["show_notifications"] = show_notif
        self.backend.config["behavior"]["auto_refresh_interval"] = refresh_interval
        self.backend.config["behavior"]["default_view"] = default_view
        self.backend.config["behavior"]["default_sort"] = default_sort
        self.backend.config["behavior"]["default_sort_direction"] = default_sort_dir
        
        # Salvar configurações
        self.backend.save_config()
        
        # Atualizar cores
        self.colors = self.backend.get_colors()
        
        # Reconfigurar estilos
        self.configure_styles()
        
        # Atualizar exibição
        self.scan_apps()
        
        # Configurar atualização automática
        self.setup_auto_refresh()
        
        # Fechar janela
        window.destroy()
        
        # Mostrar mensagem de sucesso
        self.status_var.set("Configurações salvas com sucesso")
    
    def export_settings(self):
        """Exportar configurações para arquivo"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Exportar Configurações"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.backend.config, f, indent=2, ensure_ascii=False)
                self.status_var.set("Configurações exportadas com sucesso")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar configurações: {str(e)}")
    
    def import_settings(self):
        """Importar configurações de arquivo"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Importar Configurações"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Verificar se é um arquivo de configuração válido
                if "theme" not in config or "colors" not in config:
                    messagebox.showerror("Erro", "Arquivo de configuração inválido")
                    return
                
                # Atualizar configurações
                self.backend.config = config
                self.backend.save_config()
                
                # Atualizar cores
                self.colors = self.backend.get_colors()
                
                # Reconfigurar estilos
                self.configure_styles()
                
                # Atualizar exibição
                self.scan_apps()
                
                # Configurar atualização automática
                self.setup_auto_refresh()
                
                self.status_var.set("Configurações importadas com sucesso")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar configurações: {str(e)}")
    
    def reset_settings(self):
        """Redefinir configurações para padrão"""
        if messagebox.askyesno("Confirmar", "Deseja redefinir todas as configurações para o padrão?"):
            # Excluir arquivo de configuração
            if os.path.exists(self.backend.config_file):
                os.remove(self.backend.config_file)
            
            # Recarregar configurações
            self.backend.load_config()
            
            # Atualizar cores
            self.colors = self.backend.get_colors()
            
            # Reconfigurar estilos
            self.configure_styles()
            
            # Atualizar exibição
            self.scan_apps()
            
            # Configurar atualização automática
            self.setup_auto_refresh()
            
            self.status_var.set("Configurações redefinidas com sucesso")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyAppLauncher(root)
    root.mainloop()