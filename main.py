import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
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

class PyAppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("PyAppLauncher")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # Configurar tema e cores
        self.colors = {
            "primary": "#6c5ce7",
            "primary_light": "#a29bfe",
            "secondary": "#00b894",
            "accent": "#fdcb6e",
            "danger": "#d63031",
            "background": "#f5f6fa",
            "card": "#ffffff",
            "text": "#2d3436",
            "text_light": "#636e72"
        }
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar estilos personalizados
        self.configure_styles()
        
        # Variáveis
        self.apps = []
        self.running_processes = {}  # Armazenar processos em execução {file: process}
        self.cards = []
        self.current_category = "Todos"
        self.categories = ["Todos"]
        self.search_term = ""
        
        # Diretório de aplicações
        self.apps_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps")
        
        # Criar diretório de apps se não existir
        if not os.path.exists(self.apps_dir):
            os.makedirs(self.apps_dir)
            self.create_example_app()
        
        # Arquivo de metadados
        self.metadata_file = os.path.join(self.apps_dir, "metadata.json")
        self.load_metadata()
        
        # Criar interface
        self.create_interface()
        
        # Carregar aplicações
        self.scan_apps()
        
        # Configurar encerramento adequado
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        """Encerrar processos em execução antes de fechar o aplicativo"""
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
        self.style.configure("CardTitle.TLabel", background=self.colors["card"], foreground=self.colors["text"], font=("Arial", 12, "bold"))
        self.style.configure("CardDesc.TLabel", background=self.colors["card"], foreground=self.colors["text_light"], font=("Arial", 10))
        
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
    
    def create_interface(self):
        """Criar a interface principal"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title_label = ttk.Label(self.top_frame, text="PyAppLauncher", font=("Arial", 18, "bold"), foreground=self.colors["primary"])
        title_label.pack(side=tk.LEFT)
        
        # Frame de pesquisa
        search_frame = ttk.Frame(self.top_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT)
        
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
                    last_run = metadata.get("last_run", "Nunca")
                    icon = metadata.get("icon", "")
                else:
                    # Criar metadados padrão
                    description = self.extract_description(app_path)
                    category = "Outros"
                    color = self.get_random_color()
                    last_run = "Nunca"
                    icon = ""
                    
                    self.app_metadata[file] = {
                        "name": app_name,
                        "description": description,
                        "category": category,
                        "color": color,
                        "last_run": last_run,
                        "icon": icon
                    }
                
                # Adicionar app à lista
                self.apps.append({
                    "file": file,
                    "path": app_path,
                    "name": app_name,
                    "description": description,
                    "category": category,
                    "color": color,
                    "last_run": last_run,
                    "icon": icon
                })
                
                # Adicionar categoria se for nova
                if category not in self.categories:
                    self.categories.append(category)
        
        # Salvar metadados atualizados
        self.save_metadata()
        
        # Atualizar categorias
        self.update_categories()
        
        # Atualizar exibição
        self.update_app_display()
    
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
    
    def get_random_color(self):
        """Gerar uma cor aleatória para o card"""
        colors = [
            "#6c5ce7", "#00b894", "#fdcb6e", "#e17055", "#74b9ff",
            "#a29bfe", "#55efc4", "#fab1a0", "#81ecec", "#ff7675"
        ]
        return random.choice(colors)
    
    def update_categories(self):
        """Atualizar botões de categorias"""
        # Limpar frame de categorias
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        
        # Adicionar botões de categorias
        for category in self.categories:
            style = "CategorySelected.TButton" if category == self.current_category else "Category.TButton"
            btn = ttk.Button(self.categories_frame, text=category, style=style,
                           command=lambda c=category: self.set_category(c))
            btn.pack(side=tk.LEFT, padx=(0, 5), pady=5)
    
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
        
        # Filtrar apps por categoria e termo de pesquisa
        filtered_apps = self.apps
        if self.current_category != "Todos":
            filtered_apps = [app for app in filtered_apps if app["category"] == self.current_category]
        
        if self.search_term:
            filtered_apps = [app for app in filtered_apps if 
                           self.search_term in app["name"].lower() or 
                           self.search_term in app["description"].lower()]
        
        # Exibir mensagem se não houver apps
        if not filtered_apps:
            no_apps_label = ttk.Label(self.cards_frame, text="Nenhuma aplicação encontrada", 
                                    font=("Arial", 14), foreground=self.colors["text_light"])
            no_apps_label.pack(pady=50)
            return
        
        # Criar grid para os cards
        row, col = 0, 0
        max_cols = 4  # Número de colunas para cards quadrados
        
        for app in filtered_apps:
            # Criar card
            self.create_app_card(app, row, col)
            
            # Atualizar posição
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def create_app_card(self, app, row, col):
        """Criar card para uma aplicação"""
        # Frame do card - agora quadrado
        card = ttk.Frame(self.cards_frame, style="Card.TFrame")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Definir tamanho do card (quadrado)
        card_size = 200
        card.configure(width=card_size, height=card_size)
        
        # Barra colorida superior
        color_bar = tk.Frame(card, background=app["color"], height=5)
        color_bar.pack(fill=tk.X)
        
        # Conteúdo do card
        content = ttk.Frame(card, style="Card.TFrame")
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Ícone da aplicação (primeira letra do nome)
        icon_size = 50
        icon_frame = tk.Frame(content, width=icon_size, height=icon_size, 
                            background=app["color"])
        icon_frame.pack(pady=(5, 0))
        
        # Manter o tamanho do frame
        icon_frame.pack_propagate(False)
        
        # Texto do ícone (primeira letra)
        icon_text = app["name"][0].upper()
        icon_label = tk.Label(icon_frame, text=icon_text, font=("Arial", 24, "bold"),
                            foreground="white", background=app["color"])
        icon_label.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(content, text=app["name"], style="CardTitle.TLabel", anchor="center")
        title.pack(fill=tk.X, pady=(5, 0))
        
        # Descrição
        desc_text = app["description"]
        if len(desc_text) > 80:
            desc_text = desc_text[:77] + "..."
        
        desc = ttk.Label(content, text=desc_text, style="CardDesc.TLabel", 
                       wraplength=card_size-20, anchor="center", justify="center")
        desc.pack(fill=tk.X, pady=(5, 0), expand=True)
        
        # Categoria
        category_label = ttk.Label(content, text=app["category"], 
                                 style="CardDesc.TLabel", anchor="center")
        category_label.pack(fill=tk.X)
        
        # Status de execução
        is_running = app["file"] in self.running_processes
        status_text = "Em execução" if is_running else "Parado"
        status_color = self.colors["secondary"] if is_running else self.colors["text_light"]
        
        status_frame = ttk.Frame(content, style="Card.TFrame")
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        status_indicator = tk.Frame(status_frame, width=8, height=8, background=status_color)
        status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        status_label = ttk.Label(status_frame, text=status_text, 
                               style="CardDesc.TLabel", foreground=status_color)
        status_label.pack(side=tk.LEFT)
        
        # Botões
        button_frame = ttk.Frame(content, style="Card.TFrame")
        button_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Botão Executar
        run_button = ttk.Button(button_frame, text="Executar", style="Success.TButton",
                              command=lambda: self.run_app(app),
                              state="disabled" if is_running else "normal")
        run_button.pack(side=tk.LEFT, padx=(0, 2), fill=tk.X, expand=True)
        
        # Botão Parar
        stop_button = ttk.Button(button_frame, text="Parar", style="Danger.TButton",
                               command=lambda: self.stop_app(app),
                               state="normal" if is_running else "disabled")
        stop_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Botão Editar
        edit_button = ttk.Button(button_frame, text="Editar", style="Primary.TButton",
                               command=lambda: self.edit_app(app))
        edit_button.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)
        
        # Configurar grid
        self.cards_frame.grid_columnconfigure(col, weight=1)
        self.cards_frame.grid_rowconfigure(row, weight=1)
    
    def run_app(self, app):
        """Executar uma aplicação"""
        if app["file"] in self.running_processes:
            messagebox.showinfo("Aplicação em Execução", f"A aplicação '{app['name']}' já está em execução.")
            return
        
        try:
            # Atualizar status
            self.status_var.set(f"Executando: {app['name']}")
            
            # Executar o processo
            process = subprocess.Popen([sys.executable, app["path"]])
            
            # Armazenar o processo
            self.running_processes[app["file"]] = process
            
            # Atualizar última execução
            now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            app["last_run"] = now
            self.app_metadata[app["file"]]["last_run"] = now
            self.save_metadata()
            
            # Atualizar exibição
            self.update_app_display()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar '{app['name']}': {str(e)}")
    
    def stop_app(self, app):
        """Parar uma aplicação em execução"""
        if app["file"] not in self.running_processes:
            return
        
        process = self.running_processes[app["file"]]
        
        if messagebox.askyesno("Confirmar", f"Deseja encerrar a aplicação '{app['name']}'?"):
            try:
                # Encerrar o processo
                self.terminate_process(process)
                
                # Remover da lista de processos
                del self.running_processes[app["file"]]
                
                # Atualizar status
                self.status_var.set(f"Aplicação '{app['name']}' encerrada")
                
                # Atualizar exibição
                self.update_app_display()
                
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
    
    def edit_app(self, app):
        """Editar metadados de uma aplicação"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Editar {app['name']}")
        edit_window.geometry("400x350")
        edit_window.resizable(False, False)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(edit_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        ttk.Label(main_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=app["name"])
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Categoria:").grid(row=1, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar(value=app["category"])
        category_combo = ttk.Combobox(main_frame, textvariable=category_var, width=28)
        category_combo['values'] = [cat for cat in self.categories if cat != "Todos"]
        category_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Descrição:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        description_text = tk.Text(main_frame, width=30, height=6)
        description_text.insert("1.0", app["description"])
        description_text.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Cor:").grid(row=3, column=0, sticky=tk.W, pady=5)
        color_var = tk.StringVar(value=app["color"])
        
        # Frame para preview de cor
        color_frame = ttk.Frame(main_frame)
        color_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        color_preview = tk.Frame(color_frame, width=30, height=20, background=app["color"])
        color_preview.pack(side=tk.LEFT, padx=(0, 5))
        
        color_button = ttk.Button(color_frame, text="Escolher Cor", 
                                command=lambda: self.choose_color(color_var, color_preview))
        color_button.pack(side=tk.LEFT)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        save_button = ttk.Button(button_frame, text="Salvar", style="Success.TButton",
                               command=lambda: self.save_app_edit(app, name_var.get(), 
                                                               category_var.get(), 
                                                               description_text.get("1.0", tk.END).strip(),
                                                               color_var.get(),
                                                               edit_window))
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancelar", 
                                 command=edit_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def choose_color(self, color_var, color_preview):
        """Escolher cor para o card"""
        colors = [
            "#6c5ce7", "#00b894", "#fdcb6e", "#e17055", "#74b9ff",
            "#a29bfe", "#55efc4", "#fab1a0", "#81ecec", "#ff7675"
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
    
    def save_app_edit(self, app, name, category, description, color, window):
        """Salvar edições de uma aplicação"""
        # Atualizar metadados
        self.app_metadata[app["file"]]["name"] = name
        self.app_metadata[app["file"]]["category"] = category
        self.app_metadata[app["file"]]["description"] = description
        self.app_metadata[app["file"]]["color"] = color
        
        # Salvar metadados
        self.save_metadata()
        
        # Atualizar app na lista
        app["name"] = name
        app["category"] = category
        app["description"] = description
        app["color"] = color
        
        # Atualizar categorias e exibição
        if category not in self.categories and category != "Todos":
            self.categories.append(category)
            self.update_categories()
        
        self.update_app_display()
        
        # Fechar janela
        window.destroy()
    
    def create_example_app(self):
        """Criar aplicativo de exemplo"""
        example_path = os.path.join(self.apps_dir, "exemplo_calculadora.py")
        
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write('''"""
Calculadora Simples
Uma calculadora básica com operações de adição, subtração, multiplicação e divisão.
"""
import tkinter as tk
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("Calculadora")
    root.geometry("300x400")
    root.resizable(False, False)
    
    # Variáveis
    result_var = tk.StringVar(value="0")
    operation = {"first": 0, "operator": None}
    
    # Funções
    def add_digit(digit):
        current = result_var.get()
        if current == "0" or current == "Erro":
            result_var.set(digit)
        else:
            result_var.set(current + digit)
    
    def set_operator(op):
        try:
            operation["first"] = float(result_var.get())
            operation["operator"] = op
            result_var.set("0")
        except:
            result_var.set("Erro")
    
    def calculate():
        try:
            second = float(result_var.get())
            if operation["operator"] == "+":
                result = operation["first"] + second
            elif operation["operator"] == "-":
                result = operation["first"] - second
            elif operation["operator"] == "*":
                result = operation["first"] * second
            elif operation["operator"] == "/":
                if second == 0:
                    result_var.set("Erro")
                    return
                result = operation["first"] / second
            else:
                return
            
            # Formatar resultado
            if result == int(result):
                result_var.set(str(int(result)))
            else:
                result_var.set(str(result))
        except:
            result_var.set("Erro")
    
    def clear():
        result_var.set("0")
        operation["first"] = 0
        operation["operator"] = None
    
    # Interface
    # Display
    display = ttk.Entry(root, textvariable=result_var, font=("Arial", 24), justify="right")
    display.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    
    # Botões
    buttons = [
        ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
        ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
        ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
        ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
        ("C", 5, 0, 4)  # Botão que ocupa 4 colunas
    ]
    
    for btn_text, row, col, *args in buttons:
        # Verificar se há um argumento extra para colspan
        colspan = args[0] if args else 1
        
        if btn_text in "0123456789.":
            cmd = lambda x=btn_text: add_digit(x)
        elif btn_text in "+-*/":
            cmd = lambda x=btn_text: set_operator(x)
        elif btn_text == "=":
            cmd = calculate
        elif btn_text == "C":
            cmd = clear
        
        btn = ttk.Button(root, text=btn_text, command=cmd)
        btn.grid(row=row, column=col, columnspan=colspan, padx=5, pady=5, sticky="nsew")
    
    # Configurar grid
    for i in range(4):
        root.grid_columnconfigure(i, weight=1)
    for i in range(1, 6):
        root.grid_rowconfigure(i, weight=1)
    
    root.mainloop()

if __name__ == "__main__":
    main()
''')

        # Criar outro exemplo
        example_path2 = os.path.join(self.apps_dir, "exemplo_bloco_notas.py")
        
        with open(example_path2, 'w', encoding='utf-8') as f:
            f.write('''"""
Bloco de Notas Simples
Um editor de texto básico para criar e editar arquivos de texto.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

def main():
    root = tk.Tk()
    root.title("Bloco de Notas")
    root.geometry("700x500")
    
    # Variáveis
    current_file = None
    
    # Funções
    def new_file():
        text_area.delete(1.0, tk.END)
        root.title("Bloco de Notas - Novo arquivo")
        nonlocal current_file
        current_file = None
    
    def open_file():
        file_path = filedialog.askopenfilename(
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, content)
                root.title(f"Bloco de Notas - {os.path.basename(file_path)}")
                nonlocal current_file
                current_file = file_path
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {e}")
    
    def save_file():
        nonlocal current_file
        if current_file:
            try:
                content = text_area.get(1.0, tk.END)
                with open(current_file, "w", encoding="utf-8") as file:
                    file.write(content)
                messagebox.showinfo("Salvo", "Arquivo salvo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")
        else:
            save_as()
    
    def save_as():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            try:
                content = text_area.get(1.0, tk.END)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                root.title(f"Bloco de Notas - {os.path.basename(file_path)}")
                nonlocal current_file
                current_file = file_path
                messagebox.showinfo("Salvo", "Arquivo salvo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")
    
    # Interface
    # Menu
    menu_bar = tk.Menu(root)
    
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Novo", command=new_file)
    file_menu.add_command(label="Abrir", command=open_file)
    file_menu.add_command(label="Salvar", command=save_file)
    file_menu.add_command(label="Salvar como", command=save_as)
    file_menu.add_separator()
    file_menu.add_command(label="Sair", command=root.destroy)
    
    menu_bar.add_cascade(label="Arquivo", menu=file_menu)
    
    root.config(menu=menu_bar)
    
    # Área de texto
    text_area = tk.Text(root, font=("Consolas", 12))
    text_area.pack(expand=True, fill=tk.BOTH)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(text_area)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Configurar scrollbar
    text_area.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=text_area.yview)
    
    root.mainloop()

if __name__ == "__main__":
    main()
''')

if __name__ == "__main__":
    root = tk.Tk()
    app = PyAppLauncher(root)
    root.mainloop()