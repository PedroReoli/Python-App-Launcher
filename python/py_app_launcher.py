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

class PyAppLauncher:
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