import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import threading
import datetime
import json
import shutil
import psutil
import signal
from PIL import Image, ImageTk, ImageDraw
import io
import random
import time
import importlib
import pkg_resources
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import re
from collections import defaultdict
import platform
import traceback

# Para notificações no Windows
if platform.system() == "Windows":
    from win10toast import ToastNotifier

class PyAppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("PyAppLauncher Avançado")
        self.root.geometry("1200x700")
        self.root.minsize(900, 600)
        
        # Configurar tema e cores
        self.colors = {
            "primary": "#4a6baf",
            "primary_light": "#7590d5",
            "secondary": "#00b894",
            "accent": "#fdcb6e",
            "danger": "#e74c3c",
            "background": "#f8f9fa",
            "card": "#ffffff",
            "text": "#2d3436",
            "text_light": "#636e72",
            "border": "#e0e0e0",
            "kanban_todo": "#f8d7da",
            "kanban_doing": "#fff3cd",
            "kanban_done": "#d4edda"
        }
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar estilos personalizados
        self.configure_styles()
        
        # Variáveis
        self.apps = []
        self.running_processes = {}  # Armazenar processos em execução {file: process}
        self.process_metrics = {}    # Armazenar métricas de processos {file: {cpu: [], memory: [], timestamps: []}}
        self.cards = []
        self.current_category = "Todos"
        self.categories = ["Todos"]
        self.search_term = ""
        self.view_mode = "grid"  # grid, list, kanban
        self.groups = {}  # Grupos de aplicativos {group_name: [app_files]}
        self.current_group = "Todos"
        self.kanban_states = {}  # Estados kanban {file: state}
        
        # Diretórios
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.apps_dir = os.path.join(self.base_dir, "apps")
        self.data_dir = os.path.join(self.base_dir, "data")
        
        # Criar diretórios se não existirem
        if not os.path.exists(self.apps_dir):
            os.makedirs(self.apps_dir)
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Arquivos de dados
        self.metadata_file = os.path.join(self.base_dir, "metadata.json")
        self.runtime_file = os.path.join(self.data_dir, "runtime_data.json")
        self.groups_file = os.path.join(self.data_dir, "groups.json")
        self.kanban_file = os.path.join(self.data_dir, "kanban.json")
        self.stats_file = os.path.join(self.data_dir, "statistics.json")
        
        # Carregar dados
        self.load_metadata()
        self.load_runtime_data()
        self.load_groups()
        self.load_kanban_states()
        
        # Inicializar notificador para Windows
        if platform.system() == "Windows":
            try:
                self.notifier = ToastNotifier()
            except:
                self.notifier = None
                print("Não foi possível inicializar o notificador do Windows. Instale o pacote win10toast.")
        else:
            self.notifier = None
        
        # Criar interface
        self.create_interface()
        
        # Carregar aplicações
        self.scan_apps()
        
        # Iniciar monitoramento de processos
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        self.monitoring_thread.start()
        
        # Configurar encerramento adequado
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        """Encerrar processos em execução antes de fechar o aplicativo"""
        self.monitoring_active = False
        
        if self.running_processes:
            if messagebox.askyesno("Confirmar Saída", 
                                 "Existem aplicações em execução. Deseja encerrá-las e sair?"):
                for process in self.running_processes.values():
                    self.terminate_process(process)
                self.root.destroy()
        else:
            self.root.destroy()
    
    def configure_styles(self):
        """Configurar estilos personalizados para widgets"""
        self.style.configure("TFrame", background=self.colors["background"])
        self.style.configure("Card.TFrame", background=self.colors["card"])
        
        self.style.configure("TLabel", background=self.colors["background"], foreground=self.colors["text"])
        self.style.configure("Card.TLabel", background=self.colors["card"], foreground=self.colors["text"])
        self.style.configure("CardTitle.TLabel", background=self.colors["card"], foreground=self.colors["text"], font=("Arial", 11, "bold"))
        self.style.configure("CardDesc.TLabel", background=self.colors["card"], foreground=self.colors["text_light"], font=("Arial", 9))
        
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
        self.style.configure("KanbanHeader.TLabel", background=self.colors["card"], foreground=self.colors["text"], font=("Arial", 12, "bold"))
        
        # Estilos para abas
        self.style.configure("TNotebook", background=self.colors["background"])
        self.style.configure("TNotebook.Tab", background=self.colors["background"], padding=[10, 5])
        self.style.map("TNotebook.Tab",
                      background=[("selected", self.colors["primary_light"])],
                      foreground=[("selected", "white")])
    
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
    
    def load_metadata(self):
        """Carregar metadados das aplicações"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    self.app_metadata = json.load(f)
            except:
                self.app_metadata = {}
        else:
            self.app_metadata = {}
    
    def save_metadata(self):
        """Salvar metadados das aplicações"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.app_metadata, f, indent=2)
    
    def load_runtime_data(self):
        """Carregar dados de execução"""
        if os.path.exists(self.runtime_file):
            try:
                with open(self.runtime_file, 'r') as f:
                    self.runtime_data = json.load(f)
            except:
                self.runtime_data = {}
        else:
            self.runtime_data = {}
    
    def save_runtime_data(self):
        """Salvar dados de execução"""
        with open(self.runtime_file, 'w') as f:
            json.dump(self.runtime_data, f, indent=2)
    
    def load_groups(self):
        """Carregar grupos de aplicações"""
        if os.path.exists(self.groups_file):
            try:
                with open(self.groups_file, 'r') as f:
                    self.groups = json.load(f)
            except:
                self.groups = {"Todos": []}
        else:
            self.groups = {"Todos": []}
    
    def save_groups(self):
        """Salvar grupos de aplicações"""
        with open(self.groups_file, 'w') as f:
            json.dump(self.groups, f, indent=2)
    
    def load_kanban_states(self):
        """Carregar estados do kanban"""
        if os.path.exists(self.kanban_file):
            try:
                with open(self.kanban_file, 'r') as f:
                    self.kanban_states = json.load(f)
            except:
                self.kanban_states = {}
        else:
            self.kanban_states = {}
    
    def save_kanban_states(self):
        """Salvar estados do kanban"""
        with open(self.kanban_file, 'w') as f:
            json.dump(self.kanban_states, f, indent=2)
    
    def scan_apps(self):
        """Escanear diretório de aplicações"""
        self.apps = []
        self.categories = ["Todos"]
        
        # Listar arquivos Python na pasta apps
        for file in os.listdir(self.apps_dir):
            if file.endswith(".py") and file != "__init__.py":
                app_path = os.path.join(self.apps_dir, file)
                app_name = os.path.splitext(file)[0].replace("_", " ").title()
                
                # Verificar se há metadados para este app
                if file in self.app_metadata:
                    metadata = self.app_metadata[file]
                    app_name = metadata.get("name", app_name)
                    description = metadata.get("description", "")
                    category = metadata.get("category", "Outros")
                    color = metadata.get("color", self.get_random_color())
                    icon = metadata.get("icon", "")
                    tags = metadata.get("tags", [])
                    dependencies = metadata.get("dependencies", [])
                else:
                    # Criar metadados padrão
                    description = self.extract_description(app_path)
                    category = "Outros"
                    color = self.get_random_color()
                    icon = ""
                    tags = []
                    dependencies = self.extract_dependencies(app_path)
                    
                    self.app_metadata[file] = {
                        "name": app_name,
                        "description": description,
                        "category": category,
                        "color": color,
                        "icon": icon,
                        "tags": tags,
                        "dependencies": dependencies
                    }
                
                # Verificar dados de execução
                if file in self.runtime_data:
                    runtime = self.runtime_data[file]
                    last_run = runtime.get("last_run", "Nunca")
                    run_count = runtime.get("run_count", 0)
                    total_runtime = runtime.get("total_runtime", 0)
                    avg_cpu = runtime.get("avg_cpu", 0)
                    avg_memory = runtime.get("avg_memory", 0)
                else:
                    last_run = "Nunca"
                    run_count = 0
                    total_runtime = 0
                    avg_cpu = 0
                    avg_memory = 0
                    
                    self.runtime_data[file] = {
                        "last_run": last_run,
                        "run_count": run_count,
                        "total_runtime": total_runtime,
                        "avg_cpu": avg_cpu,
                        "avg_memory": avg_memory,
                        "run_history": []
                    }
                
                # Verificar estado kanban
                if file not in self.kanban_states:
                    self.kanban_states[file] = "todo"
                
                # Adicionar app à lista
                self.apps.append({
                    "file": file,
                    "path": app_path,
                    "name": app_name,
                    "description": description,
                    "category": category,
                    "color": color,
                    "icon": icon,
                    "tags": tags,
                    "dependencies": dependencies,
                    "last_run": last_run,
                    "run_count": run_count,
                    "total_runtime": total_runtime,
                    "avg_cpu": avg_cpu,
                    "avg_memory": avg_memory,
                    "kanban_state": self.kanban_states[file]
                })
                
                # Adicionar categoria se for nova
                if category not in self.categories:
                    self.categories.append(category)
                
                # Adicionar ao grupo "Todos" se não estiver em nenhum grupo
                in_any_group = False
                for group_name, group_files in self.groups.items():
                    if file in group_files:
                        in_any_group = True
                        break
                
                if not in_any_group and group_name != "Todos":
                    self.groups["Todos"].append(file)
        
        # Ordenar apps por contagem de execução (mais usados primeiro)
        self.apps.sort(key=lambda x: x["run_count"], reverse=True)
        
        # Salvar metadados atualizados
        self.save_metadata()
        self.save_runtime_data()
        self.save_groups()
        self.save_kanban_states()
        
        # Atualizar grupos e categorias
        self.update_groups_display()
        self.update_categories()
        
        # Atualizar exibição
        self.update_app_display()
        
        # Atualizar status
        self.status_var.set(f"Encontradas {len(self.apps)} aplicações")
    
    def extract_description(self, file_path):
        """Extrair descrição do arquivo Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Ler apenas o início do arquivo
                
                # Procurar por docstring
                import re
                docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if docstring_match:
                    return docstring_match.group(1).strip()
                
                # Procurar por comentários
                comment_lines = []
                for line in content.split('\n')[:10]:  # Primeiras 10 linhas
                    if line.strip().startswith('#'):
                        comment_lines.append(line.strip()[1:].strip())
                
                if comment_lines:
                    return ' '.join(comment_lines)
                
                return "Aplicação Python"
        except:
            return "Aplicação Python"
    
    def extract_dependencies(self, file_path):
        """Extrair dependências do arquivo Python"""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Procurar por imports
                import_patterns = [
                    r'import\s+(\w+)',
                    r'from\s+(\w+)\s+import',
                    r'import\s+(\w+)\s+as',
                ]
                
                for pattern in import_patterns:
                    for match in re.finditer(pattern, content):
                        module = match.group(1)
                        if module not in ['os', 'sys', 'time', 're', 'json', 'datetime', 'math', 'random', 'tkinter', 'threading']:
                            dependencies.append(module)
                
                # Remover duplicatas
                dependencies = list(set(dependencies))
                
                return dependencies
        except:
            return []
    
    def get_random_color(self):
        """Gerar uma cor aleatória para o card"""
        colors = [
            "#4a6baf", "#00b894", "#fdcb6e", "#e17055", "#74b9ff",
            "#a29bfe", "#55efc4", "#fab1a0", "#81ecec", "#ff7675"
        ]
        return random.choice(colors)
    
    def update_groups_display(self):
        """Atualizar botões de grupos"""
        # Limpar frame de grupos
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
        
        # Adicionar label
        group_label = ttk.Label(self.groups_frame, text="Grupos:", font=("Arial", 10, "bold"))
        group_label.pack(side=tk.LEFT, padx=(0, 5), pady=5)
        
        # Adicionar botões de grupos
        for group in self.groups.keys():
            style = "CategorySelected.TButton" if group == self.current_group else "Category.TButton"
            btn = ttk.Button(self.groups_frame, text=group, style=style,
                           command=lambda g=group: self.set_group(g))
            btn.pack(side=tk.LEFT, padx=(0, 5), pady=5)
    
    def update_categories(self):
        """Atualizar botões de categorias"""
        # Limpar frame de categorias
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        
        # Adicionar label
        cat_label = ttk.Label(self.categories_frame, text="Categorias:", font=("Arial", 10, "bold"))
        cat_label.pack(side=tk.LEFT, padx=(0, 5), pady=5)
        
        # Adicionar botões de categorias
        for category in self.categories:
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
        self.update_categories()
        self.update_app_display()
    
    def update_app_display(self):
        """Atualizar exibição dos cards de aplicações"""
        # Limpar frame de cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        # Filtrar apps por grupo
        filtered_apps = self.apps
        if self.current_group != "Todos":
            group_files = self.groups.get(self.current_group, [])
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
        max_cols = 5  # Número de colunas para cards compactos
        
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
        kanban_frame.columnconfigure(0, weight=1)
        kanban_frame.columnconfigure(1, weight=1)
        kanban_frame.columnconfigure(2, weight=1)
        
        # Criar colunas
        todo_frame = ttk.Frame(kanban_frame, style="KanbanColumn.TFrame")
        todo_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        doing_frame = ttk.Frame(kanban_frame, style="KanbanColumn.TFrame")
        doing_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        done_frame = ttk.Frame(kanban_frame, style="KanbanColumn.TFrame")
        done_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
        # Títulos das colunas
        todo_header = ttk.Label(todo_frame, text="A Fazer", style="KanbanHeader.TLabel")
        todo_header.pack(fill=tk.X, pady=(0, 10))
        
        doing_header = ttk.Label(doing_frame, text="Em Progresso", style="KanbanHeader.TLabel")
        doing_header.pack(fill=tk.X, pady=(0, 10))
        
        done_header = ttk.Label(done_frame, text="Concluído", style="KanbanHeader.TLabel")
        done_header.pack(fill=tk.X, pady=(0, 10))
        
        # Separar apps por estado
        todo_apps = [app for app in apps if app["kanban_state"] == "todo"]
        doing_apps = [app for app in apps if app["kanban_state"] == "doing"]
        done_apps = [app for app in apps if app["kanban_state"] == "done"]
        
        # Criar cards para cada coluna
        for app in todo_apps:
            self.create_kanban_card(app, todo_frame)
        
        for app in doing_apps:
            self.create_kanban_card(app, doing_frame)
        
        for app in done_apps:
            self.create_kanban_card(app, done_frame)
    
    def create_compact_card(self, app, row, col):
        """Criar card compacto para uma aplicação"""
        # Frame do card - mais compacto
        card = ttk.Frame(self.cards_frame, style="Card.TFrame")
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Definir tamanho do card (mais compacto)
        card_size = 160
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
        
        # Título
        title = ttk.Label(content, text=app["name"], style="CardTitle.TLabel", anchor="center")
        title.pack(fill=tk.X, pady=(3, 0))
        
        # Descrição (mais curta)
        desc_text = app["description"]
        if len(desc_text) > 60:
            desc_text = desc_text[:57] + "..."
        
        desc = ttk.Label(content, text=desc_text, style="CardDesc.TLabel", 
                       wraplength=card_size-20, anchor="center", justify="center")
        desc.pack(fill=tk.X, pady=(2, 0), expand=True)
        
        # Status de execução
        is_running = app["file"] in self.running_processes
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
        
        # Título
        title = ttk.Label(top_row, text=app["name"], style="CardTitle.TLabel")
        title.pack(side=tk.LEFT)
        
        # Badge de categoria
        category_badge = ttk.Label(top_row, text=app["category"], 
                                 background=self.colors["primary_light"], foreground="white",
                                 padding=(5, 0))
        category_badge.pack(side=tk.LEFT, padx=10)
        
        # Badge de grupo
        for group_name, group_files in self.groups.items():
            if app["file"] in group_files and group_name != "Todos":
                group_badge = ttk.Label(top_row, text=group_name, 
                                      background=self.colors["accent"], foreground=self.colors["text"],
                                      padding=(5, 0))
                group_badge.pack(side=tk.LEFT, padx=5)
        
        # Status
        is_running = app["file"] in self.running_processes
        status_text = "Em execução" if is_running else "Parado"
        status_color = self.colors["secondary"] if is_running else self.colors["text_light"]
        
        status_frame = ttk.Frame(top_row, style="Card.TFrame")
        status_frame.pack(side=tk.RIGHT)
        
        status_indicator = tk.Frame(status_frame, width=8, height=8, background=status_color)
        status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        status_label = ttk.Label(status_frame, text=status_text, 
                               style="CardDesc.TLabel", foreground=status_color)
        status_label.pack(side=tk.LEFT)
        
        # Descrição
        desc = ttk.Label(content, text=app["description"], style="CardDesc.TLabel", 
                       wraplength=600)
        desc.pack(fill=tk.X, pady=(5, 0))
        
        # Linha inferior: Última execução e botões
        bottom_row = ttk.Frame(content, style="Card.TFrame")
        bottom_row.pack(fill=tk.X, pady=(5, 0))
        
        # Informações de execução
        info_frame = ttk.Frame(bottom_row, style="Card.TFrame")
        info_frame.pack(side=tk.LEFT)
        
        last_run_label = ttk.Label(info_frame, 
                                 text=f"Última execução: {app['last_run']} | Execuções: {app['run_count']} | CPU: {app['avg_cpu']:.1f}% | Memória: {app['avg_memory']:.1f} MB", 
                                 style="CardDesc.TLabel", foreground=self.colors["text_light"])
        last_run_label.pack(side=tk.LEFT)
        
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
        
        # Título
        title = ttk.Label(content, text=app["name"], style="CardTitle.TLabel")
        title.pack(fill=tk.X)
        
        # Descrição (curta)
        desc_text = app["description"]
        if len(desc_text) > 100:
            desc_text = desc_text[:97] + "..."
        
        desc = ttk.Label(content, text=desc_text, style="CardDesc.TLabel", 
                       wraplength=250)
        desc.pack(fill=tk.X, pady=(5, 0))
        
        # Botões de ação
        button_frame = ttk.Frame(content, style="Card.TFrame")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botões para mover entre colunas
        if app["kanban_state"] != "todo":
            left_btn = ttk.Button(button_frame, text="◀", style="Primary.TButton",
                                command=lambda: self.move_kanban_card(app, "left"),
                                width=2)
            left_btn.pack(side=tk.LEFT, padx=2)
        
        if app["kanban_state"] != "done":
            right_btn = ttk.Button(button_frame, text="▶", style="Primary.TButton",
                                 command=lambda: self.move_kanban_card(app, "right"),
                                 width=2)
            right_btn.pack(side=tk.LEFT, padx=2)
        
        # Botão Executar
        is_running = app["file"] in self.running_processes
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
    
    def move_kanban_card(self, app, direction):
        """Mover card entre colunas kanban"""
        current_state = app["kanban_state"]
        
        if direction == "left":
            if current_state == "doing":
                new_state = "todo"
            elif current_state == "done":
                new_state = "doing"
            else:
                return
        elif direction == "right":
            if current_state == "todo":
                new_state = "doing"
            elif current_state == "doing":
                new_state = "done"
            else:
                return
        else:
            return
        
        # Atualizar estado
        app["kanban_state"] = new_state
        self.kanban_states[app["file"]] = new_state
        
        # Salvar estados
        self.save_kanban_states()
        
        # Atualizar exibição
        self.update_app_display()
    
    def run_app(self, app):
        """Executar uma aplicação"""
        if app["file"] in self.running_processes:
            messagebox.showinfo("Aplicação em Execução", f"A aplicação '{app['name']}' já está em execução.")
            return
        
        # Verificar dependências
        missing_deps = self.check_dependencies(app["dependencies"])
        if missing_deps:
            if messagebox.askyesno("Dependências Faltando", 
                                 f"As seguintes dependências estão faltando: {', '.join(missing_deps)}\n\nDeseja instalá-las agora?"):
                self.install_dependencies(missing_deps)
            else:
                return
        
        try:
            # Atualizar status
            self.status_var.set(f"Executando: {app['name']}")
            
            # Registrar hora de início
            start_time = time.time()
            
            # Executar o processo
            process = subprocess.Popen([sys.executable, app["path"]])
            
            # Armazenar o processo
            self.running_processes[app["file"]] = process
            
            # Inicializar métricas para este processo
            self.process_metrics[app["file"]] = {
                "cpu": [],
                "memory": [],
                "timestamps": [],
                "start_time": start_time
            }
            
            # Atualizar última execução
            now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            app["last_run"] = now
            app["run_count"] += 1
            
            if app["file"] in self.runtime_data:
                self.runtime_data[app["file"]]["last_run"] = now
                self.runtime_data[app["file"]]["run_count"] += 1
            else:
                self.runtime_data[app["file"]] = {
                    "last_run": now,
                    "run_count": 1,
                    "total_runtime": 0,
                    "avg_cpu": 0,
                    "avg_memory": 0,
                    "run_history": []
                }
            
            # Salvar dados de execução
            self.save_runtime_data()
            
            # Atualizar exibição
            self.update_app_display()
            
            # Mostrar notificação
            self.show_notification(f"Aplicação Iniciada", f"{app['name']} foi iniciada com sucesso.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar '{app['name']}': {str(e)}")
    
    def stop_app(self, app):
        """Parar uma aplicação em execução"""
        if app["file"] not in self.running_processes:
            return
        
        process = self.running_processes[app["file"]]
        
        if messagebox.askyesno("Confirmar", f"Deseja encerrar a aplicação '{app['name']}'?"):
            try:
                # Registrar métricas finais
                if app["file"] in self.process_metrics:
                    metrics = self.process_metrics[app["file"]]
                    start_time = metrics["start_time"]
                    end_time = time.time()
                    runtime = end_time - start_time
                    
                    # Calcular médias
                    avg_cpu = sum(metrics["cpu"]) / len(metrics["cpu"]) if metrics["cpu"] else 0
                    avg_memory = sum(metrics["memory"]) / len(metrics["memory"]) if metrics["memory"] else 0
                    
                    # Atualizar dados de execução
                    if app["file"] in self.runtime_data:
                        self.runtime_data[app["file"]]["total_runtime"] += runtime
                        self.runtime_data[app["file"]]["avg_cpu"] = avg_cpu
                        self.runtime_data[app["file"]]["avg_memory"] = avg_memory
                        
                        # Adicionar ao histórico
                        run_record = {
                            "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "runtime": runtime,
                            "avg_cpu": avg_cpu,
                            "avg_memory": avg_memory
                        }
                        self.runtime_data[app["file"]]["run_history"].append(run_record)
                        
                        # Limitar histórico a 20 entradas
                        if len(self.runtime_data[app["file"]]["run_history"]) > 20:
                            self.runtime_data[app["file"]]["run_history"] = self.runtime_data[app["file"]]["run_history"][-20:]
                    
                    # Atualizar app
                    app["avg_cpu"] = avg_cpu
                    app["avg_memory"] = avg_memory
                    app["total_runtime"] += runtime
                    
                    # Limpar métricas
                    del self.process_metrics[app["file"]]
                
                # Encerrar o processo
                self.terminate_process(process)
                
                # Remover da lista de processos
                del self.running_processes[app["file"]]
                
                # Atualizar status
                self.status_var.set(f"Aplicação '{app['name']}' encerrada")
                
                # Salvar dados de execução
                self.save_runtime_data()
                
                # Atualizar exibição
                self.update_app_display()
                
                # Mostrar notificação
                self.show_notification(f"Aplicação Encerrada", f"{app['name']} foi encerrada.")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao encerrar '{app['name']}': {str(e)}")
    
    def terminate_process(self, process):
        """Encerrar um processo de forma segura"""
        try:
            # Tentar encerrar o processo principal
            if process.poll() is None:  # Se o processo ainda estiver em execução
                if sys.platform == "win32":
                    # No Windows, usamos taskkill para encerrar a árvore de processos
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
                else:
                    # No Linux/Mac, usamos psutil para encerrar a árvore de processos
                    parent = psutil.Process(process.pid)
                    for child in parent.children(recursive=True):
                        child.terminate()
                    parent.terminate()
        except:
            # Se falhar, tentar matar o processo
            try:
                process.kill()
            except:
                pass
    
    def monitor_processes(self):
        """Monitorar processos em execução para coletar métricas"""
        while self.monitoring_active:
            try:
                for file, process in list(self.running_processes.items()):
                    # Verificar se o processo ainda está em execução
                    if process.poll() is not None:
                        # Processo terminou
                        self.status_var.set(f"Processo '{file}' terminou com código {process.returncode}")
                        
                        # Registrar métricas finais
                        if file in self.process_metrics:
                            metrics = self.process_metrics[file]
                            start_time = metrics["start_time"]
                            end_time = time.time()
                            runtime = end_time - start_time
                            
                            # Calcular médias
                            avg_cpu = sum(metrics["cpu"]) / len(metrics["cpu"]) if metrics["cpu"] else 0
                            avg_memory = sum(metrics["memory"]) / len(metrics["memory"]) if metrics["memory"] else 0
                            
                            # Atualizar dados de execução
                            if file in self.runtime_data:
                                self.runtime_data[file]["total_runtime"] += runtime
                                self.runtime_data[file]["avg_cpu"] = avg_cpu
                                self.runtime_data[file]["avg_memory"] = avg_memory
                                
                                # Adicionar ao histórico
                                run_record = {
                                    "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                                    "runtime": runtime,
                                    "avg_cpu": avg_cpu,
                                    "avg_memory": avg_memory
                                }
                                self.runtime_data[file]["run_history"].append(run_record)
                                
                                # Limitar histórico a 20 entradas
                                if len(self.runtime_data[file]["run_history"]) > 20:
                                    self.runtime_data[file]["run_history"] = self.runtime_data[file]["run_history"][-20:]
                            
                            # Limpar métricas
                            del self.process_metrics[file]
                        
                        # Remover da lista de processos
                        del self.running_processes[file]
                        
                        # Salvar dados de execução
                        self.save_runtime_data()
                        
                        # Atualizar exibição
                        self.root.after(0, self.update_app_display)
                        
                        continue
                    
                    try:
                        # Obter métricas do processo
                        proc = psutil.Process(process.pid)
                        
                        # CPU e memória
                        cpu_percent = proc.cpu_percent(interval=0.1)
                        memory_info = proc.memory_info()
                        memory_mb = memory_info.rss / (1024 * 1024)  # Converter para MB
                        
                        # Armazenar métricas
                        if file in self.process_metrics:
                            self.process_metrics[file]["cpu"].append(cpu_percent)
                            self.process_metrics[file]["memory"].append(memory_mb)
                            self.process_metrics[file]["timestamps"].append(time.time())
                    except:
                        # Processo pode ter terminado entre as verificações
                        pass
            except Exception as e:
                print(f"Erro no monitoramento: {str(e)}")
            
            # Aguardar antes da próxima verificação
            time.sleep(2)
    
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
        category_combo['values'] = [cat for cat in self.categories if cat != "Todos"]
        category_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(basic_frame, text="Descrição:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        description_text = tk.Text(basic_frame, width=30, height=6)
        description_text.insert("1.0", app["description"])
        description_text.grid(row=2, column=1, sticky=  app["description"])
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
        for group_name in self.groups.keys():
            if group_name != "Todos":
                var = tk.BooleanVar(value=app["file"] in self.groups[group_name])
                groups_vars[group_name] = var
                ttk.Checkbutton(groups_listbox_frame, text=group_name, variable=var).grid(row=row, column=0, sticky=tk.W)
                row += 1
        
        # Adicionar novo grupo
        ttk.Label(groups_frame, text="Novo Grupo:").grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        new_group_var = tk.StringVar()
        new_group_entry = ttk.Entry(groups_frame, textvariable=new_group_var, width=20)
        new_group_entry.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        add_group_button = ttk.Button(groups_frame, text="Adicionar Grupo", 
                                    command=lambda: self.add_new_group(new_group_var.get(), groups_vars, groups_listbox_frame))
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
        ttk.Radiobutton(kanban_frame, text="A Fazer", variable=kanban_var, value="todo").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(kanban_frame, text="Em Progresso", variable=kanban_var, value="doing").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(kanban_frame, text="Concluído", variable=kanban_var, value="done").grid(row=3, column=0, sticky=tk.W, pady=2)
        
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
    
    def add_new_group(self, group_name, groups_vars, parent_frame):
        """Adicionar um novo grupo"""
        if not group_name or group_name == "Todos" or group_name in self.groups:
            messagebox.showerror("Erro", "Nome de grupo inválido ou já existe")
            return
        
        # Adicionar grupo
        self.groups[group_name] = []
        
        # Adicionar checkbox
        var = tk.BooleanVar(value=False)
        groups_vars[group_name] = var
        ttk.Checkbutton(parent_frame, text=group_name, variable=var).grid(row=len(groups_vars)-1, column=0, sticky=tk.W)
        
        # Salvar grupos
        self.save_groups()
    
    def check_and_show_deps(self, dependencies, parent_frame):
        """Verificar dependências e mostrar status"""
        missing = self.check_dependencies(dependencies)
        
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
        missing = self.check_dependencies(deps)
        
        if missing:
            self.install_dependencies(missing)
        else:
            messagebox.showinfo("Dependências", "Todas as dependências já estão instaladas")
    
    def choose_color(self, color_var, color_preview):
        """Escolher cor para o card"""
        colors = [
            "#4a6baf", "#00b894", "#fdcb6e", "#e17055", "#74b9ff",
            "#a29bfe", "#55efc4", "#fab1a0", "#81ecec", "#ff7675",
            "#6c5ce7", "#00cec9", "#ffeaa7", "#ff7675", "#636e72"
        ]
        
        color_window = tk.Toplevel(self.root)
        color_window.title("Escolher Cor")
        color_window.geometry("300x150")
        color_window.resizable(False, False)
        color_window.transient(self.root)
        color_window.grab_set()
        
        color_frame = ttk.Frame(color_window, padding=10)
        color_frame.pack(fill=tk.BOTH, expand=True)
        
        # Grid de cores
        row, col = 0, 0
        for color in colors:
            def set_color(c=color):
                color_var.set(c)
                color_preview.config(background=c)
                color_window.destroy()
            
            color_btn = tk.Frame(color_frame, width=30, height=30, background=color)
            color_btn.grid(row=row, column=col, padx=5, pady=5)
            color_btn.bind("<Button-1>", lambda e, c=color: set_color(c))
            
            col += 1
            if col >= 5:
                col = 0
                row += 1
    
    def save_app_edit(self, app, name, category, description, color, tags, dependencies, kanban_state, groups_vars, window):
        """Salvar edições de uma aplicação"""
        # Limpar tags
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        # Limpar dependências
        dependencies = [dep.strip() for dep in dependencies if dep.strip()]
        
        # Atualizar metadados
        self.app_metadata[app["file"]]["name"] = name
        self.app_metadata[app["file"]]["category"] = category
        self.app_metadata[app["file"]]["description"] = description
        self.app_metadata[app["file"]]["color"] = color
        self.app_metadata[app["file"]]["tags"] = tags
        self.app_metadata[app["file"]]["dependencies"] = dependencies
        
        # Salvar metadados
        self.save_metadata()
        
        # Atualizar app na lista
        app["name"] = name
        app["category"] = category
        app["description"] = description
        app["color"] = color
        app["tags"] = tags
        app["dependencies"] = dependencies
        app["kanban_state"] = kanban_state
        
        # Atualizar estado kanban
        self.kanban_states[app["file"]] = kanban_state
        self.save_kanban_states()
        
        # Atualizar grupos
        for group_name, var in groups_vars.items():
            if var.get() and app["file"] not in self.groups[group_name]:
                self.groups[group_name].append(app["file"])
            elif not var.get() and app["file"] in self.groups[group_name]:
                self.groups[group_name].remove(app["file"])
        
        self.save_groups()
        
        # Atualizar categorias e exibição
        if category not in self.categories and category != "Todos":
            self.categories.append(category)
            self.update_categories()
        
        self.update_groups_display()
        self.update_app_display()
        
        # Fechar janela
        window.destroy()
    
    def open_code(self, app):
        """Abrir código da aplicação no editor padrão"""
        try:
            if sys.platform == "win32":
                os.startfile(app["path"])
            elif sys.platform == "darwin":  # macOS
                subprocess.call(["open", app["path"]])
            else:  # Linux
                subprocess.call(["xdg-open", app["path"]])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {str(e)}")
    
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
        category_combo['values'] = [cat for cat in self.categories if cat != "Todos"]
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
        group_combo['values'] = list(self.groups.keys())
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
        if not name or not filename:
            messagebox.showerror("Erro", "Nome e nome do arquivo são obrigatórios")
            return
        
        # Garantir que o nome do arquivo tenha extensão .py
        if not filename.endswith(".py"):
            filename += ".py"
        
        # Verificar se o arquivo já existe
        file_path = os.path.join(self.apps_dir, filename)
        if os.path.exists(file_path):
            messagebox.showerror("Erro", f"O arquivo {filename} já existe")
            return
        
        # Criar arquivo com modelo
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if template == "Básico":
                    f.write(f'"""\n{name}\n{description}\n"""\n\n')
                    f.write('def main():\n    print("Olá de ' + name + '")\n\n')
                    f.write('if __name__ == "__main__":\n    main()\n')
                elif template == "Aplicação GUI":
                    f.write(f'"""\n{name}\n{description}\n"""\n')
                    f.write('import tkinter as tk\nfrom tkinter import ttk\n\n')
                    f.write('def main():\n    root = tk.Tk()\n    root.title("' + name + '")\n')
                    f.write('    root.geometry("600x400")\n\n')
                    f.write('    # Seu código GUI aqui\n    label = ttk.Label(root, text="' + name + '")\n')
                    f.write('    label.pack(pady=20)\n\n')
                    f.write('    root.mainloop()\n\n')
                    f.write('if __name__ == "__main__":\n    main()\n')
                elif template == "Aplicação Console":
                    f.write(f'"""\n{name}\n{description}\n"""\n\n')
                    f.write('def main():\n    print("Bem-vindo ao ' + name + '")\n')
                    f.write('    # Seu código aqui\n    entrada = input("Digite algo: ")\n')
                    f.write('    print(f"Você digitou: {entrada}")\n\n')
                    f.write('if __name__ == "__main__":\n    main()\n')
                else:  # Vazio
                    f.write(f'"""\n{name}\n{description}\n"""\n\n')
                    f.write('# Seu código aqui\n')
            
            # Criar metadados
            color = self.get_random_color()
            dependencies = []
            
            self.app_metadata[filename] = {
                "name": name,
                "description": description,
                "category": category,
                "color": color,
                "icon": "",
                "tags": [],
                "dependencies": dependencies
            }
            
            # Criar dados de execução
            self.runtime_data[filename] = {
                "last_run": "Nunca",
                "run_count": 0,
                "total_runtime": 0,
                "avg_cpu": 0,
                "avg_memory": 0,
                "run_history": []
            }
            
            # Definir estado kanban
            self.kanban_states[filename] = "todo"
            
            # Adicionar ao grupo
            if group in self.groups:
                self.groups[group].append(filename)
            
            # Salvar dados
            self.save_metadata()
            self.save_runtime_data()
            self.save_kanban_states()
            self.save_groups()
            
            # Atualizar apps
            self.scan_apps()
            
            # Fechar janela
            window.destroy()
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Sucesso", f"Aplicação {name} criada com sucesso")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível criar o arquivo: {str(e)}")
    
    def check_dependencies(self, dependencies):
        """Verificar dependências faltantes"""
        missing = []
        for dep in dependencies:
            if dep.strip():
                try:
                    importlib.import_module(dep)
                except ImportError:
                    missing.append(dep)
        return missing
    
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
        
        # Função para instalar em thread separada
        def install_thread():
            for i, dep in enumerate(dependencies):
                status_var.set(f"Instalando {dep} ({i+1}/{len(dependencies)})...")
                log_text.insert(tk.END, f"Instalando {dep}...\n")
                log_text.see(tk.END)
                
                try:
                    # Instalar usando pip
                    process = subprocess.Popen(
                        [sys.executable, "-m", "pip", "install", dep],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Capturar saída
                    stdout, stderr = process.communicate()
                    
                    if process.returncode == 0:
                        log_text.insert(tk.END, f"Instalado com sucesso: {dep}\n")
                        log_text.insert(tk.END, stdout + "\n")
                    else:
                        log_text.insert(tk.END, f"Erro ao instalar {dep}:\n")
                        log_text.insert(tk.END, stderr + "\n")
                    
                    log_text.see(tk.END)
                    
                except Exception as e:
                    log_text.insert(tk.END, f"Erro: {str(e)}\n")
                    log_text.see(tk.END)
            
            status_var.set("Instalação concluída")
            
            # Adicionar botão de fechar
            ttk.Button(main_frame, text="Fechar", command=progress_window.destroy).pack(pady=10)
        
        # Iniciar thread de instalação
        threading.Thread(target=install_thread, daemon=True).start()
    
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
            missing = self.check_dependencies(app["dependencies"])
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
            missing = self.check_dependencies(app["dependencies"])
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
        missing = self.check_dependencies(all_deps)
        
        if missing:
            self.install_dependencies(missing)
        else:
            messagebox.showinfo("Dependências", "Todas as dependências já estão instaladas")
    
    def fill_packages_tree(self, tree):
        """Preencher treeview de pacotes instalados"""
        # Limpar treeview
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            # Obter pacotes instalados
            packages = pkg_resources.working_set
            
            # Ordenar por nome
            sorted_packages = sorted(packages, key=lambda p: p.key)
            
            # Adicionar à treeview
            for package in sorted_packages:
                tree.insert("", "end", values=(package.key, package.version))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar pacotes: {str(e)}")
    
    def install_package(self, package_name, tree):
        """Instalar pacote via pip"""
        if not package_name:
            messagebox.showerror("Erro", "Nome do pacote é obrigatório")
            return
        
        # Instalar pacote
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                messagebox.showinfo("Sucesso", f"Pacote {package_name} instalado com sucesso")
                self.fill_packages_tree(tree)
            else:
                messagebox.showerror("Erro", f"Erro ao instalar {package_name}:\n{stderr}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao instalar pacote: {str(e)}")
    
    def update_selected_package(self, tree):
        """Atualizar pacote selecionado"""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Seleção", "Selecione um pacote para atualizar")
            return
        
        # Obter nome do pacote
        package_name = tree.item(selection[0], "values")[0]
        
        # Atualizar pacote
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "--upgrade", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                messagebox.showinfo("Sucesso", f"Pacote {package_name} atualizado com sucesso")
                self.fill_packages_tree(tree)
            else:
                messagebox.showerror("Erro", f"Erro ao atualizar {package_name}:\n{stderr}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar pacote: {str(e)}")
    
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
        
        # Desinstalar pacote
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "uninstall", "-y", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                messagebox.showinfo("Sucesso", f"Pacote {package_name} desinstalado com sucesso")
                self.fill_packages_tree(tree)
            else:
                messagebox.showerror("Erro", f"Erro ao desinstalar {package_name}:\n{stderr}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao desinstalar pacote: {str(e)}")
    
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
        for group in self.groups.keys():
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
                if group_name in self.groups:
                    for file in self.groups[group_name]:
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
            if group_name and group_name not in self.groups:
                self.groups[group_name] = []
                self.save_groups()
                groups_listbox.insert(tk.END, group_name)
                self.update_groups_display()
        
        add_button = ttk.Button(buttons_frame, text="Adicionar Grupo", command=add_group)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botão para remover grupo
        def remove_group():
            selection = groups_listbox.curselection()
            if selection:
                group_name = groups_listbox.get(selection[0])
                if group_name == "Todos":
                    messagebox.showerror("Erro", "Não é possível remover o grupo 'Todos'")
                    return
                
                if messagebox.askyesno("Confirmar", f"Remover o grupo '{group_name}'?"):
                    del self.groups[group_name]
                    self.save_groups()
                    groups_listbox.delete(selection[0])
                    apps_listbox.delete(0, tk.END)
                    details_label.config(text="Selecione um grupo para ver detalhes")
                    self.update_groups_display()
        
        remove_button = ttk.Button(buttons_frame, text="Remover Grupo", command=remove_group)
        remove_button.pack(side=tk.LEFT, padx=5)
        
        # Botão para renomear grupo
        def rename_group():
            selection = groups_listbox.curselection()
            if selection:
                old_name = groups_listbox.get(selection[0])
                if old_name == "Todos":
                    messagebox.showerror("Erro", "Não é possível renomear o grupo 'Todos'")
                    return
                
                new_name = simpledialog.askstring("Renomear Grupo", "Novo nome:", parent=groups_window, initialvalue=old_name)
                if new_name and new_name != old_name and new_name not in self.groups:
                    self.groups[new_name] = self.groups[old_name]
                    del self.groups[old_name]
                    self.save_groups()
                    groups_listbox.delete(selection[0])
                    groups_listbox.insert(selection[0], new_name)
                    self.update_groups_display()
        
        rename_button = ttk.Button(buttons_frame, text="Renomear Grupo", command=rename_group)
        rename_button.pack(side=tk.LEFT, padx=5)
    
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
        
        total_apps = len(self.apps)
        total_runs = sum(app["run_count"] for app in self.apps)
        total_runtime = sum(app["total_runtime"] for app in self.apps)
        total_runtime_str = f"{total_runtime/3600:.1f} horas" if total_runtime > 3600 else f"{total_runtime/60:.1f} minutos"
        
        ttk.Label(stats_frame, text=f"Total de Aplicações: {total_apps}").pack(anchor=tk.W, padx=10, pady=2)
        ttk.Label(stats_frame, text=f"Total de Execuções: {total_runs}").pack(anchor=tk.W, padx=10, pady=2)
        ttk.Label(stats_frame, text=f"Tempo Total de Execução: {total_runtime_str}").pack(anchor=tk.W, padx=10, pady=2)
        
        # Aplicações mais usadas
        top_apps_frame = ttk.Frame(overview_top_frame, relief="solid", borderwidth=1)
        top_apps_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        ttk.Label(top_apps_frame, text="Aplicações Mais Usadas", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Ordenar por contagem de execução
        top_apps = sorted(self.apps, key=lambda x: x["run_count"], reverse=True)[:5]
        
        for app in top_apps:
            ttk.Label(top_apps_frame, text=f"{app['name']}: {app['run_count']} execuções").pack(anchor=tk.W, padx=10, pady=2)
        
        # Gráfico de execuções por dia
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Coletar dados de execução por dia
        executions_by_day = defaultdict(int)
        
        for app_file, runtime_data in self.runtime_data.items():
            for run in runtime_data.get("run_history", []):
                date = run.get("date", "").split()[0]  # Pegar apenas a data
                if date:
                    executions_by_day[date] += 1
        
        # Ordenar por data
        dates = sorted(executions_by_day.keys())
        counts = [executions_by_day[date] for date in dates]
        
        # Plotar gráfico
        if dates:
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
        # Gráfico de pizza para distribuição de execuções
        fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Dados para gráfico de pizza
        app_names = [app["name"] for app in top_apps]
        app_runs = [app["run_count"] for app in top_apps]
        
        if app_names:
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
        # Gráfico de barras para CPU e memória
        fig3, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        
        # Dados para gráficos de desempenho
        perf_apps = sorted(self.apps, key=lambda x: x["avg_cpu"], reverse=True)[:5]
        app_names = [app["name"] for app in perf_apps]
        app_cpu = [app["avg_cpu"] for app in perf_apps]
        
        if app_names:
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
        # Gráfico de pizza para distribuição por categoria
        fig4, ax = plt.subplots(figsize=(8, 6))
        
        # Contar aplicações por categoria
        category_counts = defaultdict(int)
        for app in self.apps:
            category_counts[app["category"]] += 1
        
        categories = list(category_counts.keys())
        counts = [category_counts[cat] for cat in categories]
        
        if categories:
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
        if app["file"] in self.runtime_data and self.runtime_data[app["file"]].get("run_history"):
            history = self.runtime_data[app["file"]]["run_history"]
            
            # Gráfico de histórico de execução
            fig, ax = plt.subplots(figsize=(8, 4))
            
            dates = [run["date"] for run in history]
            runtimes = [run["runtime"]/60 for run in history]  # Converter para minutos
            
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
        if app["file"] in self.runtime_data and self.runtime_data[app["file"]].get("run_history"):
            history = self.runtime_data[app["file"]]["run_history"]
            
            # Gráfico de CPU e memória
            fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
            
            dates = [run["date"] for run in history]
            cpu_values = [run["avg_cpu"] for run in history]
            memory_values = [run["avg_memory"] for run in history]
            
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
    
    def show_notification(self, title, message):
        """Mostrar notificação no Windows"""
        if platform.system() == "Windows" and self.notifier:
            try:
                self.notifier.show_toast(
                    title,
                    message,
                    duration=5,
                    threaded=True
                )
            except Exception as e:
                print(f"Erro ao mostrar notificação: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyAppLauncher(root)
    root.mainloop()