import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser, scrolledtext
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

# Importar sistema de IA
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bot'))
    from ai_system import AISystem
    from ai_integration import AIInterface
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ Sistema de IA não disponível")

class PyAppLauncherCompact:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 PyAppLauncher Ultra-Compacto")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        # Inicializar backend
        self.backend = PyAppLauncherBackend()
        
        # Inicializar IA se disponível
        self.ai_system = None
        if AI_AVAILABLE:
            self.ai_system = AISystem()
        
        # Variáveis
        self.cards = []
        self.current_category = "Todos"
        self.current_group = "Todos"
        self.search_term = ""
        self.view_mode = "compact"  # Novo modo ultra-compacto
        self.drag_data = {"widget": None, "x": 0, "y": 0, "item": None}
        self.show_ai_panel = False
        
        # Configurar tema e cores
        self.colors = self.backend.get_colors()
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar estilos personalizados
        self.configure_styles()
        
        # Criar interface ultra-compacta
        self.create_ultra_compact_interface()
        
        # Carregar aplicações
        self.scan_apps()
        
        # Iniciar monitoramento de processos
        self.monitoring_thread = threading.Thread(target=self.backend.monitor_processes, daemon=True)
        self.monitoring_thread.start()
        
        # Configurar atualização automática
        self.setup_auto_refresh()
        
        # Configurar encerramento adequado
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def configure_styles(self):
        """Configurar estilos para interface ultra-compacta"""
        font_family = self.backend.config["font"]["family"]
        font_sizes = self.backend.config["font"]["size"]
        
        # Estilos base
        self.style.configure("UltraCompact.TFrame", background=self.colors["background"])
        self.style.configure("Header.TFrame", background=self.colors["primary"], padding=5)
        self.style.configure("Sidebar.TFrame", background=self.colors["card"], padding=5)
        self.style.configure("Content.TFrame", background=self.colors["background"], padding=5)
        
        # Labels
        self.style.configure("Header.TLabel", background=self.colors["primary"], foreground="white", 
                           font=(font_family, 14, "bold"))
        self.style.configure("Compact.TLabel", background=self.colors["card"], foreground=self.colors["text"], 
                           font=(font_family, 9))
        self.style.configure("CompactTitle.TLabel", background=self.colors["card"], foreground=self.colors["text"], 
                           font=(font_family, 10, "bold"))
        
        # Botões
        self.style.configure("Compact.TButton", padding=3, font=(font_family, 8))
        self.style.configure("Action.TButton", background=self.colors["primary"], foreground="white", 
                           padding=5, font=(font_family, 9, "bold"))
        self.style.map("Action.TButton",
                      background=[('active', self.colors["primary_light"])],
                      foreground=[('active', 'white')])
        
        # Entry
        self.style.configure("Compact.TEntry", padding=3, font=(font_family, 9))
        
        # Notebook (para abas)
        self.style.configure("Compact.TNotebook", background=self.colors["background"])
        self.style.configure("Compact.TNotebook.Tab", padding=[8, 4], font=(font_family, 9))
        self.style.map("Compact.TNotebook.Tab",
                      background=[("selected", self.colors["primary_light"])],
                      foreground=[("selected", "white")])
    
    def create_ultra_compact_interface(self):
        """Criar interface ultra-compacta com IA integrada"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root, style="UltraCompact.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header compacto
        self.create_compact_header()
        
        # Frame de conteúdo principal
        self.content_frame = ttk.Frame(self.main_frame, style="Content.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Criar layout com sidebar e área principal
        self.create_sidebar_and_main_area()
        
        # Inicializar interface de IA se disponível
        if AI_AVAILABLE and self.ai_system:
            self.ai_interface = AIInterface(self.ai_content_frame, self.ai_system, [])
    
    def create_compact_header(self):
        """Criar header ultra-compacto"""
        header_frame = ttk.Frame(self.main_frame, style="Header.TFrame")
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Logo e título
        logo_frame = ttk.Frame(header_frame)
        logo_frame.pack(side=tk.LEFT)
        
        logo_canvas = tk.Canvas(logo_frame, width=24, height=24, bg=self.colors["primary"], highlightthickness=0)
        logo_canvas.create_text(12, 12, text="PL", fill="white", font=("Arial", 12, "bold"))
        logo_canvas.pack(side=tk.LEFT, padx=(0, 8))
        
        title_label = ttk.Label(logo_frame, text="PyAppLauncher Ultra-Compacto", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Barra de ferramentas compacta
        toolbar_frame = ttk.Frame(header_frame)
        toolbar_frame.pack(side=tk.RIGHT)
        
        # Botões de ação rápida
        quick_actions = [
            ("🔄", "Atualizar", self.scan_apps),
            ("➕", "Nova App", self.create_new_app),
            ("🤖", "IA", self.toggle_ai_panel),
            ("⚙️", "Config", self.show_settings),
            ("📊", "Dashboard", self.show_dashboard)
        ]
        
        for icon, tooltip, command in quick_actions:
            btn = ttk.Button(toolbar_frame, text=icon, style="Action.TButton", 
                           command=command, width=3)
            btn.pack(side=tk.LEFT, padx=2)
            
            # Tooltip simples
            self.create_tooltip(btn, tooltip)
        
        # Campo de busca compacto
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT, padx=20)
        
        ttk.Label(search_frame, text="🔍", style="Header.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                               style="Compact.TEntry", width=25)
        search_entry.pack(side=tk.LEFT)
    
    def create_sidebar_and_main_area(self):
        """Criar sidebar e área principal"""
        # Frame horizontal para sidebar e conteúdo
        h_frame = ttk.Frame(self.content_frame)
        h_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar compacta
        self.create_compact_sidebar(h_frame)
        
        # Área principal
        self.main_area_frame = ttk.Frame(h_frame, style="Content.TFrame")
        self.main_area_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Notebook para abas principais
        self.main_notebook = ttk.Notebook(self.main_area_frame, style="Compact.TNotebook")
        self.main_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de aplicações
        self.apps_frame = ttk.Frame(self.main_notebook, style="Content.TFrame")
        self.main_notebook.add(self.apps_frame, text="📱 Aplicações")
        
        # Aba de IA (se disponível)
        if AI_AVAILABLE:
            self.ai_content_frame = ttk.Frame(self.main_notebook, style="Content.TFrame")
            self.main_notebook.add(self.ai_content_frame, text="🤖 IA")
        
        # Criar área de aplicações
        self.create_apps_area()
    
    def create_compact_sidebar(self, parent):
        """Criar sidebar ultra-compacta"""
        sidebar_frame = ttk.Frame(parent, style="Sidebar.TFrame", width=200)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        sidebar_frame.pack_propagate(False)
        
        # Título da sidebar
        sidebar_title = ttk.Label(sidebar_frame, text="NAVEGAÇÃO", 
                                style="CompactTitle.TLabel")
        sidebar_title.pack(pady=(0, 10))
        
        # Categorias
        categories_frame = ttk.Frame(sidebar_frame)
        categories_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(categories_frame, text="📂 Categorias", 
                style="CompactTitle.TLabel").pack(anchor=tk.W)
        
        self.categories_frame = ttk.Frame(categories_frame)
        self.categories_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Grupos
        groups_frame = ttk.Frame(sidebar_frame)
        groups_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(groups_frame, text="🗂️ Grupos", 
                style="CompactTitle.TLabel").pack(anchor=tk.W)
        
        self.groups_frame = ttk.Frame(groups_frame)
        self.groups_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Visualizações
        views_frame = ttk.Frame(sidebar_frame)
        views_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(views_frame, text="👁️ Visualização", 
                style="CompactTitle.TLabel").pack(anchor=tk.W)
        
        views_buttons_frame = ttk.Frame(views_frame)
        views_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Botões de visualização
        view_modes = [
            ("📱", "Compact", "compact"),
            ("📊", "Grid", "grid"),
            ("📋", "List", "list"),
            ("📋", "Kanban", "kanban")
        ]
        
        for icon, name, mode in view_modes:
            btn = ttk.Button(views_buttons_frame, text=icon, style="Compact.TButton", 
                           command=lambda m=mode: self.set_view_mode(m), width=3)
            btn.pack(side=tk.LEFT, padx=1)
            self.create_tooltip(btn, name)
        
        # Estatísticas rápidas
        stats_frame = ttk.Frame(sidebar_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(stats_frame, text="📈 Estatísticas", 
                style="CompactTitle.TLabel").pack(anchor=tk.W)
        
        self.stats_frame = ttk.Frame(stats_frame)
        self.stats_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Status do sistema
        status_frame = ttk.Frame(sidebar_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(status_frame, text="💻 Status", 
                style="CompactTitle.TLabel").pack(anchor=tk.W)
        
        self.status_frame = ttk.Frame(status_frame)
        self.status_frame.pack(fill=tk.X, pady=(5, 0))
    
    def create_apps_area(self):
        """Criar área de aplicações ultra-compacta"""
        # Frame de aplicações
        self.apps_content_frame = ttk.Frame(self.apps_frame, style="Content.TFrame")
        self.apps_content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas e scrollbar para aplicações
        self.apps_canvas = tk.Canvas(self.apps_content_frame, bg=self.colors["background"], 
                                   highlightthickness=0)
        self.apps_scrollbar = ttk.Scrollbar(self.apps_content_frame, orient="vertical", 
                                          command=self.apps_canvas.yview)
        self.apps_scrollable_frame = ttk.Frame(self.apps_canvas, style="Content.TFrame")
        
        self.apps_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.apps_canvas.configure(scrollregion=self.apps_canvas.bbox("all"))
        )
        
        self.apps_canvas.create_window((0, 0), window=self.apps_scrollable_frame, anchor="nw")
        self.apps_canvas.configure(yscrollcommand=self.apps_scrollbar.set)
        
        # Configurar scroll com mouse
        self.apps_canvas.bind("<Configure>", self.on_canvas_configure)
        self.apps_canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        # Layout
        self.apps_canvas.pack(side="left", fill="both", expand=True)
        self.apps_scrollbar.pack(side="right", fill="y")
    
    def create_tooltip(self, widget, text):
        """Criar tooltip simples"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background="#ffffe0", 
                            relief="solid", borderwidth=1)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind("<Leave>", lambda e: hide_tooltip())
            tooltip.bind("<Leave>", lambda e: hide_tooltip())
        
        widget.bind("<Enter>", show_tooltip)
    
    def toggle_ai_panel(self):
        """Alternar painel de IA"""
        if AI_AVAILABLE:
            self.show_ai_panel = not self.show_ai_panel
            if self.show_ai_panel:
                self.main_notebook.select(1)  # Selecionar aba de IA
            else:
                self.main_notebook.select(0)  # Selecionar aba de apps
    
    def on_search_change(self, *args):
        """Atualizar busca"""
        self.search_term = self.search_var.get().lower()
        self.update_app_display()
    
    def set_view_mode(self, mode):
        """Definir modo de visualização"""
        self.view_mode = mode
        self.update_app_display()
    
    def scan_apps(self):
        """Escanear aplicações"""
        try:
            self.backend.scan_applications()
            self.update_app_display()
            self.update_sidebar()
            messagebox.showinfo("Sucesso", "Aplicações atualizadas!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao escanear aplicações: {e}")
    
    def update_sidebar(self):
        """Atualizar sidebar"""
        # Atualizar categorias
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        
        categories = ["Todos"] + list(set(app.get('category', 'Geral') for app in self.backend.apps))
        for category in categories:
            btn = ttk.Button(self.categories_frame, text=category, style="Compact.TButton",
                           command=lambda c=category: self.set_category(c))
            btn.pack(fill=tk.X, pady=1)
        
        # Atualizar grupos
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
        
        groups = ["Todos"] + list(set(group for app in self.backend.apps 
                                    for group in app.get('groups', [])))
        for group in groups:
            btn = ttk.Button(self.groups_frame, text=group, style="Compact.TButton",
                           command=lambda g=group: self.set_group(g))
            btn.pack(fill=tk.X, pady=1)
        
        # Atualizar estatísticas
        self.update_stats()
    
    def update_stats(self):
        """Atualizar estatísticas"""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        total_apps = len(self.backend.apps)
        running_apps = len(self.backend.running_processes)
        categories = len(set(app.get('category', 'Geral') for app in self.backend.apps))
        
        stats_text = f"📱 Apps: {total_apps}\n"
        stats_text += f"▶️ Rodando: {running_apps}\n"
        stats_text += f"📂 Categorias: {categories}"
        
        stats_label = ttk.Label(self.stats_frame, text=stats_text, style="Compact.TLabel")
        stats_label.pack(anchor=tk.W)
    
    def set_category(self, category):
        """Definir categoria atual"""
        self.current_category = category
        self.update_app_display()
    
    def set_group(self, group):
        """Definir grupo atual"""
        self.current_group = group
        self.update_app_display()
    
    def update_app_display(self):
        """Atualizar exibição de aplicações"""
        # Filtrar aplicações
        filtered_apps = []
        for app in self.backend.apps:
            # Filtro de categoria
            if self.current_category != "Todos" and app.get('category') != self.current_category:
                continue
            
            # Filtro de grupo
            if self.current_group != "Todos" and self.current_group not in app.get('groups', []):
                continue
            
            # Filtro de busca
            if self.search_term:
                search_fields = [
                    app.get('name', ''),
                    app.get('description', ''),
                    app.get('category', ''),
                    ' '.join(app.get('tags', []))
                ]
                if not any(self.search_term in field.lower() for field in search_fields):
                    continue
            
            filtered_apps.append(app)
        
        # Limpar área de aplicações
        for widget in self.apps_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Exibir aplicações no modo selecionado
        if self.view_mode == "compact":
            self.display_compact_view(filtered_apps)
        elif self.view_mode == "grid":
            self.display_grid_view(filtered_apps)
        elif self.view_mode == "list":
            self.display_list_view(filtered_apps)
        elif self.view_mode == "kanban":
            self.display_kanban_view(filtered_apps)
    
    def display_compact_view(self, apps):
        """Exibir aplicações em modo ultra-compacto"""
        if not apps:
            no_apps_label = ttk.Label(self.apps_scrollable_frame, 
                                    text="Nenhuma aplicação encontrada", 
                                    style="Compact.TLabel")
            no_apps_label.pack(pady=20)
            return
        
        # Criar grid compacto
        row = 0
        col = 0
        max_cols = 6  # 6 apps por linha
        
        for app in apps:
            # Frame do app compacto
            app_frame = ttk.Frame(self.apps_scrollable_frame, style="Sidebar.TFrame", 
                                relief="solid", borderwidth=1)
            app_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Nome do app (compacto)
            name_label = ttk.Label(app_frame, text=app.get('name', 'App'), 
                                 style="CompactTitle.TLabel")
            name_label.pack(pady=(5, 2))
            
            # Categoria (pequena)
            category_label = ttk.Label(app_frame, text=app.get('category', 'Geral'), 
                                     style="Compact.TLabel")
            category_label.pack()
            
            # Botões de ação compactos
            buttons_frame = ttk.Frame(app_frame)
            buttons_frame.pack(pady=(5, 5))
            
            # Botão executar
            run_btn = ttk.Button(buttons_frame, text="▶️", style="Compact.TButton", 
                               command=lambda a=app: self.run_app(a), width=2)
            run_btn.pack(side=tk.LEFT, padx=1)
            
            # Botão editar
            edit_btn = ttk.Button(buttons_frame, text="✏️", style="Compact.TButton", 
                                command=lambda a=app: self.edit_app(a), width=2)
            edit_btn.pack(side=tk.LEFT, padx=1)
            
            # Botão código
            code_btn = ttk.Button(buttons_frame, text="📄", style="Compact.TButton", 
                                command=lambda a=app: self.open_code(a), width=2)
            code_btn.pack(side=tk.LEFT, padx=1)
            
            # Próxima posição
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configurar grid
        for i in range(max_cols):
            self.apps_scrollable_frame.grid_columnconfigure(i, weight=1)
    
    def display_grid_view(self, apps):
        """Exibir aplicações em grid normal"""
        # Implementação similar ao compact_view mas com mais detalhes
        pass
    
    def display_list_view(self, apps):
        """Exibir aplicações em lista"""
        # Implementação de lista compacta
        pass
    
    def display_kanban_view(self, apps):
        """Exibir aplicações em kanban"""
        # Implementação de kanban compacto
        pass
    
    def run_app(self, app):
        """Executar aplicação"""
        try:
            self.backend.run_application(app)
            messagebox.showinfo("Sucesso", f"Aplicação {app.get('name')} iniciada!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar aplicação: {e}")
    
    def edit_app(self, app):
        """Editar aplicação"""
        # Implementação de edição compacta
        pass
    
    def open_code(self, app):
        """Abrir código da aplicação"""
        # Implementação de abertura de código
        pass
    
    def create_new_app(self):
        """Criar nova aplicação"""
        # Implementação de criação compacta
        pass
    
    def show_settings(self):
        """Mostrar configurações"""
        # Implementação de configurações compactas
        pass
    
    def show_dashboard(self):
        """Mostrar dashboard"""
        # Implementação de dashboard compacto
        pass
    
    def on_canvas_configure(self, event):
        """Configurar canvas"""
        self.apps_canvas.configure(scrollregion=self.apps_canvas.bbox("all"))
    
    def on_mousewheel(self, event):
        """Scroll com mouse"""
        self.apps_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_auto_refresh(self):
        """Configurar atualização automática"""
        refresh_interval = self.backend.config["behavior"]["refresh_interval"]
        if refresh_interval > 0:
            def auto_refresh():
                while True:
                    time.sleep(refresh_interval)
                    self.root.after(0, self.scan_apps)
            
            refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
            refresh_thread.start()
    
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