import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import threading
import time
from datetime import datetime
import re
import pickle
import webbrowser
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import io
import base64
import hashlib
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("jsonmaster.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("JSONMaster")

# Ícones em base64 (exemplos - seriam substituídos por ícones reais)
ICONS = {
    "app": "...",  # Base64 do ícone do aplicativo
    "open": "...",  # Base64 do ícone de abrir
    "save": "...",  # Base64 do ícone de salvar
    "export": "...",  # Base64 do ícone de exportar
    "chart": "...",  # Base64 do ícone de gráfico
    "filter": "...",  # Base64 do ícone de filtro
    "settings": "...",  # Base64 do ícone de configurações
    "help": "...",  # Base64 do ícone de ajuda
}

class ToolTip:
    """Classe para criar tooltips nos widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.text, background="#ffffe0", 
                         relief="solid", borderwidth=1, padding=(5, 2))
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class StatusBar(ttk.Frame):
    """Barra de status personalizada"""
    def __init__(self, master):
        super().__init__(master, relief=tk.SUNKEN)
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        
        self.progress_var = tk.DoubleVar()
        self.progress_var.set(0.0)
        
        self.status_label = ttk.Label(self, textvariable=self.status_var, padding=(5, 2))
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor=tk.W)
        
        self.progress = ttk.Progressbar(self, variable=self.progress_var, length=150, mode="determinate")
        self.progress.pack(side=tk.RIGHT, padx=5)
        
        self.time_var = tk.StringVar()
        self.update_time()
        self.time_label = ttk.Label(self, textvariable=self.time_var, padding=(5, 2))
        self.time_label.pack(side=tk.RIGHT)
    
    def update_time(self):
        self.time_var.set(datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_time)
    
    def set_status(self, text, progress=None):
        self.status_var.set(text)
        if progress is not None:
            self.progress_var.set(progress)
    
    def start_progress(self):
        self.progress.start()
    
    def stop_progress(self):
        self.progress.stop()
        self.progress_var.set(0)

class SearchFrame(ttk.LabelFrame):
    """Frame de pesquisa avançada"""
    def __init__(self, master, callback):
        super().__init__(master, text="Pesquisa Avançada", padding=(10, 5))
        self.callback = callback
        
        # Campo de pesquisa
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, expand=True, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        search_btn = ttk.Button(search_frame, text="Pesquisar", command=self.search)
        search_btn.pack(side=tk.LEFT)
        
        # Opções de pesquisa
        options_frame = ttk.Frame(self)
        options_frame.pack(fill=tk.X, expand=True, pady=5)
        
        self.case_sensitive_var = tk.BooleanVar(value=False)
        case_check = ttk.Checkbutton(options_frame, text="Case sensitive", variable=self.case_sensitive_var)
        case_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.regex_var = tk.BooleanVar(value=False)
        regex_check = ttk.Checkbutton(options_frame, text="Usar regex", variable=self.regex_var)
        regex_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_fields_var = tk.StringVar(value="all")
        ttk.Radiobutton(options_frame, text="Todos os campos", variable=self.search_fields_var, value="all").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(options_frame, text="Campos selecionados", variable=self.search_fields_var, value="selected").pack(side=tk.LEFT)
        
        # Atalhos de teclado
        self.search_entry.bind("<Return>", lambda e: self.search())
        self.search_entry.bind("<Escape>", lambda e: self.clear())
        
        # Botão de limpar
        clear_btn = ttk.Button(search_frame, text="Limpar", command=self.clear)
        clear_btn.pack(side=tk.LEFT, padx=(5, 0))
    
    def search(self):
        search_text = self.search_var.get()
        if not search_text:
            return
        
        options = {
            "case_sensitive": self.case_sensitive_var.get(),
            "regex": self.regex_var.get(),
            "fields": self.search_fields_var.get()
        }
        
        self.callback(search_text, options)
    
    def clear(self):
        self.search_var.set("")
        self.callback("", {"clear": True})

class FilterDialog(tk.Toplevel):
    """Diálogo para configurar filtros avançados"""
    def __init__(self, parent, fields, callback):
        super().__init__(parent)
        self.title("Filtros Avançados")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()
        
        self.fields = fields
        self.callback = callback
        self.filters = []
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de filtros
        filters_frame = ttk.LabelFrame(main_frame, text="Filtros Ativos", padding=5)
        filters_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar para a lista de filtros
        scrollbar = ttk.Scrollbar(filters_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.filters_list = tk.Listbox(filters_frame, yscrollcommand=scrollbar.set, height=10)
        self.filters_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.config(command=self.filters_list.yview)
        
        # Botões para gerenciar filtros
        btn_frame = ttk.Frame(filters_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Adicionar", command=self.add_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remover", command=self.remove_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpar Todos", command=self.clear_filters).pack(side=tk.LEFT, padx=5)
        
        # Frame para adicionar novo filtro
        add_frame = ttk.LabelFrame(main_frame, text="Adicionar Filtro", padding=5)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Campo
        field_frame = ttk.Frame(add_frame)
        field_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(field_frame, text="Campo:").pack(side=tk.LEFT, padx=(0, 5))
        self.field_var = tk.StringVar()
        self.field_combo = ttk.Combobox(field_frame, textvariable=self.field_var, values=self.fields, state="readonly")
        self.field_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Operador
        op_frame = ttk.Frame(add_frame)
        op_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(op_frame, text="Operador:").pack(side=tk.LEFT, padx=(0, 5))
        self.op_var = tk.StringVar()
        operators = ["=", "!=", ">", "<", ">=", "<=", "contém", "não contém", "começa com", "termina com", "está vazio", "não está vazio"]
        self.op_combo = ttk.Combobox(op_frame, textvariable=self.op_var, values=operators, state="readonly")
        self.op_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.op_combo.current(0)
        
        # Valor
        val_frame = ttk.Frame(add_frame)
        val_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(val_frame, text="Valor:").pack(side=tk.LEFT, padx=(0, 5))
        self.val_var = tk.StringVar()
        self.val_entry = ttk.Entry(val_frame, textvariable=self.val_var)
        self.val_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botões de ação
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Aplicar Filtros", command=self.apply_filters).pack(side=tk.RIGHT, padx=5)
        ttk.Button(action_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def add_filter(self):
        field = self.field_var.get()
        op = self.op_var.get()
        val = self.val_var.get()
        
        if not field:
            messagebox.showwarning("Aviso", "Selecione um campo para o filtro.")
            return
        
        if op not in ["está vazio", "não está vazio"] and not val and op != "=":
            messagebox.showwarning("Aviso", "Informe um valor para o filtro.")
            return
        
        filter_str = f"{field} {op} {val}"
        self.filters.append({"field": field, "op": op, "value": val})
        self.filters_list.insert(tk.END, filter_str)
        
        # Limpar campos
        self.val_var.set("")
    
    def remove_filter(self):
        selected = self.filters_list.curselection()
        if not selected:
            return
        
        for i in reversed(selected):
            self.filters_list.delete(i)
            self.filters.pop(i)
    
    def clear_filters(self):
        self.filters_list.delete(0, tk.END)
        self.filters = []
    
    def apply_filters(self):
        self.callback(self.filters)
        self.destroy()

class ChartDialog(tk.Toplevel):
    """Diálogo para criar gráficos a partir dos dados"""
    def __init__(self, parent, data, fields):
        super().__init__(parent)
        self.title("Visualização de Dados")
        self.geometry("800x600")
        self.transient(parent)
        
        self.data = data
        self.fields = fields
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de configuração
        config_frame = ttk.LabelFrame(main_frame, text="Configuração do Gráfico", padding=5)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tipo de gráfico
        type_frame = ttk.Frame(config_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="Tipo de Gráfico:").pack(side=tk.LEFT, padx=(0, 5))
        self.chart_type_var = tk.StringVar()
        chart_types = ["Barras", "Linhas", "Pizza", "Dispersão", "Histograma"]
        self.chart_type_combo = ttk.Combobox(type_frame, textvariable=self.chart_type_var, values=chart_types, state="readonly")
        self.chart_type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chart_type_combo.current(0)
        
        # Campo X
        x_frame = ttk.Frame(config_frame)
        x_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(x_frame, text="Campo X (Eixo horizontal):").pack(side=tk.LEFT, padx=(0, 5))
        self.x_field_var = tk.StringVar()
        self.x_field_combo = ttk.Combobox(x_frame, textvariable=self.x_field_var, values=self.fields, state="readonly")
        self.x_field_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Campo Y
        y_frame = ttk.Frame(config_frame)
        y_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(y_frame, text="Campo Y (Eixo vertical):").pack(side=tk.LEFT, padx=(0, 5))
        self.y_field_var = tk.StringVar()
        self.y_field_combo = ttk.Combobox(y_frame, textvariable=self.y_field_var, values=self.fields, state="readonly")
        self.y_field_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Título
        title_frame = ttk.Frame(config_frame)
        title_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(title_frame, text="Título:").pack(side=tk.LEFT, padx=(0, 5))
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(title_frame, textvariable=self.title_var)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botão para gerar gráfico
        ttk.Button(config_frame, text="Gerar Gráfico", command=self.generate_chart).pack(pady=10)
        
        # Frame para o gráfico
        self.chart_frame = ttk.LabelFrame(main_frame, text="Visualização", padding=5)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Botões de ação
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Exportar Gráfico", command=self.export_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Fechar", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Variáveis para o gráfico
        self.fig = None
        self.canvas = None
    
    def generate_chart(self):
        x_field = self.x_field_var.get()
        y_field = self.y_field_var.get()
        chart_type = self.chart_type_var.get()
        title = self.title_var.get() or f"Gráfico de {chart_type}"
        
        if not x_field or not y_field:
            messagebox.showwarning("Aviso", "Selecione os campos para os eixos X e Y.")
            return
        
        # Limpar o frame do gráfico
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Preparar os dados
        df = pd.DataFrame(self.data)
        
        # Criar a figura e o eixo
        self.fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        
        try:
            # Gerar o gráfico com base no tipo selecionado
            if chart_type == "Barras":
                df.plot(kind='bar', x=x_field, y=y_field, ax=ax, legend=True)
            elif chart_type == "Linhas":
                df.plot(kind='line', x=x_field, y=y_field, ax=ax, legend=True)
            elif chart_type == "Pizza":
                df.plot(kind='pie', y=y_field, labels=df[x_field], ax=ax, autopct='%1.1f%%')
            elif chart_type == "Dispersão":
                df.plot(kind='scatter', x=x_field, y=y_field, ax=ax)
            elif chart_type == "Histograma":
                df[y_field].plot(kind='hist', ax=ax, bins=20)
            
            # Configurar o gráfico
            ax.set_title(title)
            ax.set_xlabel(x_field)
            ax.set_ylabel(y_field)
            plt.tight_layout()
            
            # Adicionar o gráfico ao frame
            canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.canvas = canvas
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar o gráfico: {str(e)}")
            logger.error(f"Erro ao gerar gráfico: {str(e)}")
    
    def export_chart(self):
        if not self.fig:
            messagebox.showwarning("Aviso", "Nenhum gráfico gerado para exportar.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("Imagem PNG", "*.png"),
                ("Imagem JPEG", "*.jpg"),
                ("Imagem SVG", "*.svg"),
                ("Documento PDF", "*.pdf")
            ]
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Exportação Concluída", f"Gráfico exportado com sucesso para:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar o gráfico: {str(e)}")

class BatchProcessDialog(tk.Toplevel):
    """Diálogo para processamento em lote de múltiplos arquivos"""
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Processamento em Lote")
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()
        
        self.callback = callback
        self.files = []
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de arquivos
        files_frame = ttk.LabelFrame(main_frame, text="Arquivos para Processamento", padding=5)
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Lista de arquivos
        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.files_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.config(command=self.files_list.yview)
        
        # Botões para gerenciar arquivos
        btn_frame = ttk.Frame(files_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Adicionar Arquivos", command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Adicionar Pasta", command=self.add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remover Selecionados", command=self.remove_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpar Todos", command=self.clear_files).pack(side=tk.LEFT, padx=5)
        
        # Frame de opções
        options_frame = ttk.LabelFrame(main_frame, text="Opções de Processamento", padding=5)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Opção de campos
        fields_frame = ttk.Frame(options_frame)
        fields_frame.pack(fill=tk.X, pady=5)
        
        self.fields_var = tk.StringVar(value="auto")
        ttk.Radiobutton(fields_frame, text="Detectar campos automaticamente", variable=self.fields_var, value="auto").pack(anchor=tk.W)
        ttk.Radiobutton(fields_frame, text="Usar campos do arquivo atual", variable=self.fields_var, value="current").pack(anchor=tk.W)
        
        # Opção de exportação
        export_frame = ttk.Frame(options_frame)
        export_frame.pack(fill=tk.X, pady=5)
        
        self.export_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(export_frame, text="Exportar resultados automaticamente", variable=self.export_var).pack(anchor=tk.W)
        
        self.export_format_var = tk.StringVar(value="csv")
        export_format_frame = ttk.Frame(export_frame)
        export_format_frame.pack(fill=tk.X, padx=(20, 0), pady=5)
        
        ttk.Radiobutton(export_format_frame, text="CSV", variable=self.export_format_var, value="csv").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(export_format_frame, text="Excel", variable=self.export_format_var, value="excel").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(export_format_frame, text="JSON", variable=self.export_format_var, value="json").pack(side=tk.LEFT)
        
        # Pasta de destino
        dest_frame = ttk.Frame(export_frame)
        dest_frame.pack(fill=tk.X, padx=(20, 0), pady=5)
        
        ttk.Label(dest_frame, text="Pasta de destino:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.dest_var = tk.StringVar()
        dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_var)
        dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(dest_frame, text="Procurar", command=self.browse_dest).pack(side=tk.LEFT)
        
        # Botões de ação
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Iniciar Processamento", command=self.start_processing).pack(side=tk.RIGHT, padx=5)
        ttk.Button(action_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def add_files(self):
        file_paths = filedialog.askopenfilenames(
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        
        for path in file_paths:
            if path not in self.files:
                self.files.append(path)
                self.files_list.insert(tk.END, path)
    
    def add_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return
        
        try:
            json_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.json')]
            
            for path in json_files:
                if path not in self.files:
                    self.files.append(path)
                    self.files_list.insert(tk.END, path)
            
            if not json_files:
                messagebox.showinfo("Informação", "Nenhum arquivo JSON encontrado na pasta selecionada.")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar arquivos da pasta: {str(e)}")
    
    def remove_files(self):
        selected = self.files_list.curselection()
        if not selected:
            return
        
        for i in reversed(selected):
            self.files_list.delete(i)
            self.files.pop(i)
    
    def clear_files(self):
        self.files_list.delete(0, tk.END)
        self.files = []
    
    def browse_dest(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.dest_var.set(folder_path)
    
    def start_processing(self):
        if not self.files:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado para processamento.")
            return
        
        options = {
            "fields_mode": self.fields_var.get(),
            "export": self.export_var.get(),
            "export_format": self.export_format_var.get(),
            "dest_folder": self.dest_var.get() if self.export_var.get() else None
        }
        
        if options["export"] and not options["dest_folder"]:
            messagebox.showwarning("Aviso", "Selecione uma pasta de destino para exportação.")
            return
        
        self.callback(self.files, options)
        self.destroy()

class SettingsDialog(tk.Toplevel):
    """Diálogo de configurações do aplicativo"""
    def __init__(self, parent, settings, callback):
        super().__init__(parent)
        self.title("Configurações")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()
        
        self.settings = settings.copy()
        self.callback = callback
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Aba de aparência
        appearance_frame = ttk.Frame(notebook, padding=10)
        notebook.add(appearance_frame, text="Aparência")
        
        # Tema
        theme_frame = ttk.Frame(appearance_frame)
        theme_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(theme_frame, text="Tema:").pack(side=tk.LEFT, padx=(0, 5))
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "clam"))
        themes = ["clam", "alt", "default", "classic", "vista", "xpnative", "aqua"]
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=themes, state="readonly")
        theme_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Tamanho da fonte
        font_frame = ttk.Frame(appearance_frame)
        font_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(font_frame, text="Tamanho da fonte:").pack(side=tk.LEFT, padx=(0, 5))
        self.font_size_var = tk.IntVar(value=self.settings.get("font_size", 10))
        font_spin = ttk.Spinbox(font_frame, from_=8, to=16, textvariable=self.font_size_var, width=5)
        font_spin.pack(side=tk.LEFT)
        
        # Aba de comportamento
        behavior_frame = ttk.Frame(notebook, padding=10)
        notebook.add(behavior_frame, text="Comportamento")
        
        # Autosalvar
        autosave_frame = ttk.Frame(behavior_frame)
        autosave_frame.pack(fill=tk.X, pady=5)
        
        self.autosave_var = tk.BooleanVar(value=self.settings.get("autosave", False))
        ttk.Checkbutton(autosave_frame, text="Autosalvar configurações", variable=self.autosave_var).pack(anchor=tk.W)
        
        # Confirmar ao sair
        confirm_frame = ttk.Frame(behavior_frame)
        confirm_frame.pack(fill=tk.X, pady=5)
        
        self.confirm_exit_var = tk.BooleanVar(value=self.settings.get("confirm_exit", True))
        ttk.Checkbutton(confirm_frame, text="Confirmar ao sair", variable=self.confirm_exit_var).pack(anchor=tk.W)
        
        # Número máximo de itens recentes
        recent_frame = ttk.Frame(behavior_frame)
        recent_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(recent_frame, text="Número máximo de arquivos recentes:").pack(side=tk.LEFT, padx=(0, 5))
        self.max_recent_var = tk.IntVar(value=self.settings.get("max_recent", 10))
        recent_spin = ttk.Spinbox(recent_frame, from_=0, to=20, textvariable=self.max_recent_var, width=5)
        recent_spin.pack(side=tk.LEFT)
        
        # Aba de exportação
        export_frame = ttk.Frame(notebook, padding=10)
        notebook.add(export_frame, text="Exportação")
        
        # Formato padrão
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="Formato padrão de exportação:").pack(anchor=tk.W, pady=(0, 5))
        
        self.default_format_var = tk.StringVar(value=self.settings.get("default_format", "csv"))
        ttk.Radiobutton(format_frame, text="CSV", variable=self.default_format_var, value="csv").pack(anchor=tk.W, padx=(20, 0))
        ttk.Radiobutton(format_frame, text="Excel", variable=self.default_format_var, value="excel").pack(anchor=tk.W, padx=(20, 0))
        ttk.Radiobutton(format_frame, text="JSON", variable=self.default_format_var, value="json").pack(anchor=tk.W, padx=(20, 0))
        ttk.Radiobutton(format_frame, text="PDF", variable=self.default_format_var, value="pdf").pack(anchor=tk.W, padx=(20, 0))
        
        # Pasta padrão
        folder_frame = ttk.Frame(export_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(folder_frame, text="Pasta padrão para exportação:").pack(anchor=tk.W, pady=(0, 5))
        
        folder_select_frame = ttk.Frame(folder_frame)
        folder_select_frame.pack(fill=tk.X, padx=(20, 0))
        
        self.default_folder_var = tk.StringVar(value=self.settings.get("default_folder", ""))
        folder_entry = ttk.Entry(folder_select_frame, textvariable=self.default_folder_var)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(folder_select_frame, text="Procurar", command=self.browse_folder).pack(side=tk.LEFT)
        
        # Botões de ação
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Salvar", command=self.save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(action_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(action_frame, text="Restaurar Padrões", command=self.restore_defaults).pack(side=tk.LEFT, padx=5)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.default_folder_var.set(folder_path)
    
    def restore_defaults(self):
        default_settings = {
            "theme": "clam",
            "font_size": 10,
            "autosave": False,
            "confirm_exit": True,
            "max_recent": 10,
            "default_format": "csv",
            "default_folder": ""
        }
        
        if messagebox.askyesno("Restaurar Padrões", "Tem certeza que deseja restaurar todas as configurações para os valores padrão?"):
            self.settings = default_settings.copy()
            
            # Atualizar os widgets
            self.theme_var.set(default_settings["theme"])
            self.font_size_var.set(default_settings["font_size"])
            self.autosave_var.set(default_settings["autosave"])
            self.confirm_exit_var.set(default_settings["confirm_exit"])
            self.max_recent_var.set(default_settings["max_recent"])
            self.default_format_var.set(default_settings["default_format"])
            self.default_folder_var.set(default_settings["default_folder"])
    
    def save_settings(self):
        self.settings.update({
            "theme": self.theme_var.get(),
            "font_size": self.font_size_var.get(),
            "autosave": self.autosave_var.get(),
            "confirm_exit": self.confirm_exit_var.get(),
            "max_recent": self.max_recent_var.get(),
            "default_format": self.default_format_var.get(),
            "default_folder": self.default_folder_var.get()
        })
        
        self.callback(self.settings)
        self.destroy()

class JSONMasterPro:
    """Aplicação principal para extração e análise de JSON"""
    def __init__(self, root):
        self.root = root
        self.root.title("JSONMaster Pro - Extrator e Analisador Avançado")
        self.root.geometry("1200x800")
        
        # Configurações padrão
        self.settings = {
            "theme": "clam",
            "font_size": 10,
            "autosave": False,
            "confirm_exit": True,
            "max_recent": 10,
            "default_format": "csv",
            "default_folder": ""
        }
        
        # Carregar configurações salvas
        self.load_settings()
        
        # Aplicar tema
        self.apply_theme()
        
        # Variáveis de estado
        self.json_data = None
        self.available_fields = []
        self.selected_fields = []
        self.extracted_data = []
        self.current_file_path = None
        self.recent_files = []
        self.filters = []
        self.is_modified = False
        
        # Configurar a interface
        self.setup_ui()
        
        # Carregar arquivos recentes
        self.load_recent_files()
        
        # Configurar atalhos de teclado
        self.setup_shortcuts()
        
        # Configurar manipuladores de eventos
        self.setup_event_handlers()
    
    def load_settings(self):
        """Carregar configurações salvas"""
        settings_file = os.path.join(os.path.expanduser("~"), ".jsonmaster_settings")
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "rb") as f:
                    saved_settings = pickle.load(f)
                    self.settings.update(saved_settings)
                logger.info("Configurações carregadas com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar configurações: {str(e)}")
    
    def save_settings(self):
        """Salvar configurações"""
        settings_file = os.path.join(os.path.expanduser("~"), ".jsonmaster_settings")
        
        try:
            with open(settings_file, "wb") as f:
                pickle.dump(self.settings, f)
            logger.info("Configurações salvas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {str(e)}")
    
    def apply_theme(self):
        """Aplicar tema e configurações visuais"""
        style = ttk.Style()
        style.theme_use(self.settings["theme"])
        
        # Configurar fontes
        default_font = ("Helvetica", self.settings["font_size"])
        heading_font = ("Helvetica", self.settings["font_size"] + 2, "bold")
        
        style.configure(".", font=default_font)
        style.configure("Heading.TLabel", font=heading_font)
        style.configure("TButton", padding=6)
        style.configure("Accent.TButton", background="#4a6baf", foreground="white")
    
    def setup_ui(self):
        """Configurar a interface do usuário"""
        # Criar menu
        self.create_menu()
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Painel superior
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Área de seleção de arquivo
        file_frame = ttk.LabelFrame(top_frame, text="Arquivo JSON", padding=5)
        file_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, expand=True)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(file_select_frame, text="Procurar", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT)
        
        # Botões de ação rápida
        action_frame = ttk.Frame(top_frame)
        action_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        refresh_btn = ttk.Button(action_frame, text="Atualizar", command=self.refresh_data)
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        filter_btn = ttk.Button(action_frame, text="Filtros", command=self.show_filters)
        filter_btn.pack(side=tk.LEFT, padx=2)
        
        chart_btn = ttk.Button(action_frame, text="Gráficos", command=self.show_charts)
        chart_btn.pack(side=tk.LEFT, padx=2)
        
        batch_btn = ttk.Button(action_frame, text="Lote", command=self.show_batch_process)
        batch_btn.pack(side=tk.LEFT, padx=2)
        
        # Painel central
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Painel de pesquisa
        self.search_frame = SearchFrame(center_frame, self.search_callback)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Painel de campos
        fields_frame = ttk.Frame(center_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame esquerdo - campos disponíveis
        left_frame = ttk.LabelFrame(fields_frame, text="Campos Disponíveis", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Adicionar barra de pesquisa para campos disponíveis
        self.available_search_var = tk.StringVar()
        self.available_search_var.trace("w", self.filter_available_fields)
        available_search_frame = ttk.Frame(left_frame)
        available_search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(available_search_frame, text="Filtrar:").pack(side=tk.LEFT, padx=(0, 5))
        available_search_entry = ttk.Entry(available_search_frame, textvariable=self.available_search_var)
        available_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Lista de campos disponíveis com scrollbar
        available_list_frame = ttk.Frame(left_frame)
        available_list_frame.pack(fill=tk.BOTH, expand=True)
        
        available_scrollbar = ttk.Scrollbar(available_list_frame)
        available_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.available_listbox = tk.Listbox(available_list_frame, selectmode=tk.MULTIPLE, 
                                           yscrollcommand=available_scrollbar.set)
        self.available_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        available_scrollbar.config(command=self.available_listbox.yview)
        
        # Frame central - botões de transferência
        mid_frame = ttk.Frame(fields_frame)
        mid_frame.pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(mid_frame, text=">>", command=self.add_fields, width=5)
        add_btn.pack(pady=5)
        
        remove_btn = ttk.Button(mid_frame, text="<<", command=self.remove_fields, width=5)
        remove_btn.pack(pady=5)
        
        add_all_btn = ttk.Button(mid_frame, text="Todos >>", command=self.add_all_fields, width=10)
        add_all_btn.pack(pady=5)
        
        remove_all_btn = ttk.Button(mid_frame, text="<< Todos", command=self.remove_all_fields, width=10)
        remove_all_btn.pack(pady=5)
        
        # Frame direito - campos selecionados
        right_frame = ttk.LabelFrame(fields_frame, text="Campos Selecionados", padding=5)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Adicionar barra de pesquisa para campos selecionados
        self.selected_search_var = tk.StringVar()
        self.selected_search_var.trace("w", self.filter_selected_fields)
        selected_search_frame = ttk.Frame(right_frame)
        selected_search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(selected_search_frame, text="Filtrar:").pack(side=tk.LEFT, padx=(0, 5))
        selected_search_entry = ttk.Entry(selected_search_frame, textvariable=self.selected_search_var)
        selected_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Lista de campos selecionados com scrollbar
        selected_list_frame = ttk.Frame(right_frame)
        selected_list_frame.pack(fill=tk.BOTH, expand=True)
        
        selected_scrollbar = ttk.Scrollbar(selected_list_frame)
        selected_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.selected_listbox = tk.Listbox(selected_list_frame, selectmode=tk.MULTIPLE, 
                                          yscrollcommand=selected_scrollbar.set)
        self.selected_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        selected_scrollbar.config(command=self.selected_listbox.yview)
        
        # Botões de extração
        extract_frame = ttk.Frame(main_frame)
        extract_frame.pack(fill=tk.X, pady=(0, 10))
        
        extract_btn = ttk.Button(extract_frame, text="Extrair Dados", command=self.extract_data, style="Accent.TButton")
        extract_btn.pack(side=tk.LEFT)
        
        export_btn = ttk.Button(extract_frame, text="Exportar Resultados", command=self.export_data)
        export_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        stats_btn = ttk.Button(extract_frame, text="Estatísticas", command=self.show_statistics)
        stats_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Área de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para diferentes visualizações
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de tabela
        table_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(table_frame, text="Tabela")
        
        # Tabela de resultados com scrollbars
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        y_scrollbar = ttk.Scrollbar(table_container)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.result_tree = ttk.Treeview(table_container, yscrollcommand=y_scrollbar.set, 
                                       xscrollcommand=x_scrollbar.set)
        self.result_tree.pack(fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.result_tree.yview)
        x_scrollbar.config(command=self.result_tree.xview)
        
        # Aba de JSON
        json_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(json_frame, text="JSON")
        
        json_scrollbar = ttk.Scrollbar(json_frame)
        json_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.json_text = tk.Text(json_frame, wrap=tk.NONE, yscrollcommand=json_scrollbar.set)
        self.json_text.pack(fill=tk.BOTH, expand=True)
        json_scrollbar.config(command=self.json_text.yview)
        
        # Aba de visualização
        viz_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(viz_frame, text="Visualização")
        
        self.viz_container = ttk.Frame(viz_frame)
        self.viz_container.pack(fill=tk.BOTH, expand=True)
        
        # Barra de status
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Configurar arrastar e soltar
        self.root.drop_target_register(tk.DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)
    
    def create_menu(self):
        """Criar a barra de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        
        file_menu.add_command(label="Abrir...", command=self.browse_file, accelerator="Ctrl+O")
        
        # Submenu de arquivos recentes
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Abrir Recente", menu=self.recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Salvar Resultados", command=self.save_results, accelerator="Ctrl+S")
        file_menu.add_command(label="Salvar Como...", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exportar...", command=self.export_data, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.confirm_exit, accelerator="Alt+F4")
        
        # Menu Editar
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        
        edit_menu.add_command(label="Copiar Seleção", command=self.copy_selection, accelerator="Ctrl+C")
        edit_menu.add_command(label="Selecionar Tudo", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Pesquisar...", command=self.focus_search, accelerator="Ctrl+F")
        edit_menu.add_command(label="Filtrar...", command=self.show_filters, accelerator="Ctrl+Shift+F")
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferências...", command=self.show_settings)
        
        # Menu Visualizar
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizar", menu=view_menu)
        
        view_menu.add_command(label="Atualizar", command=self.refresh_data, accelerator="F5")
        view_menu.add_separator()
        view_menu.add_command(label="Estatísticas", command=self.show_statistics)
        view_menu.add_command(label="Gráficos", command=self.show_charts)
        view_menu.add_separator()
        view_menu.add_command(label="Expandir Todos", command=self.expand_all)
        view_menu.add_command(label="Recolher Todos", command=self.collapse_all)
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        
        tools_menu.add_command(label="Processamento em Lote", command=self.show_batch_process)
        tools_menu.add_command(label="Validar JSON", command=self.validate_json)
        tools_menu.add_command(label="Formatar JSON", command=self.format_json)
        tools_menu.add_separator()
        tools_menu.add_command(label="Comparar Arquivos", command=self.compare_files)
        tools_menu.add_command(label="Mesclar Arquivos", command=self.merge_files)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        
        help_menu.add_command(label="Documentação", command=self.show_documentation)
        help_menu.add_command(label="Atalhos de Teclado", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="Verificar Atualizações", command=self.check_updates)
        help_menu.add_separator()
        help_menu.add_command(label="Sobre", command=self.show_about)
    
    def setup_shortcuts(self):
        """Configurar atalhos de teclado"""
        self.root.bind("<Control-o>", lambda e: self.browse_file())
        self.root.bind("<Control-s>", lambda e: self.save_results())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as())
        self.root.bind("<Control-e>", lambda e: self.export_data())
        self.root.bind("<Control-f>", lambda e: self.focus_search())
        self.root.bind("<Control-Shift-F>", lambda e: self.show_filters())
        self.root.bind("<F5>", lambda e: self.refresh_data())
        self.root.bind("<Control-a>", lambda e: self.select_all())
        self.root.bind("<Control-c>", lambda e: self.copy_selection())
    
    def setup_event_handlers(self):
        """Configurar manipuladores de eventos"""
        # Confirmar ao fechar a janela
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        
        # Duplo clique nas listas
        self.available_listbox.bind("<Double-Button-1>", lambda e: self.add_fields())
        self.selected_listbox.bind("<Double-Button-1>", lambda e: self.remove_fields())
        
        # Arrastar e soltar entre listas
        # Nota: Implementação simplificada, em uma aplicação real seria mais complexo
        self.available_listbox.bind("<B1-Motion>", self.start_drag)
        self.selected_listbox.bind("<B1-Motion>", self.start_drag)
        
        # Clique direito para menu de contexto
        self.result_tree.bind("<Button-3>", self.show_context_menu)
    
    def load_recent_files(self):
        """Carregar lista de arquivos recentes"""
        recent_file = os.path.join(os.path.expanduser("~"), ".jsonmaster_recent")
        
        if os.path.exists(recent_file):
            try:
                with open(recent_file, "rb") as f:
                    self.recent_files = pickle.load(f)
                self.update_recent_menu()
                logger.info("Arquivos recentes carregados com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar arquivos recentes: {str(e)}")
    
    def save_recent_files(self):
        """Salvar lista de arquivos recentes"""
        recent_file = os.path.join(os.path.expanduser("~"), ".jsonmaster_recent")
        
        try:
            with open(recent_file, "wb") as f:
                pickle.dump(self.recent_files, f)
            logger.info("Arquivos recentes salvos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar arquivos recentes: {str(e)}")
    
    def update_recent_menu(self):
        """Atualizar o menu de arquivos recentes"""
        # Limpar menu atual
        self.recent_menu.delete(0, tk.END)
        
        if not self.recent_files:
            self.recent_menu.add_command(label="(Nenhum arquivo recente)", state=tk.DISABLED)
            return
        
        # Adicionar arquivos recentes ao menu
        for path in self.recent_files:
            # Truncar caminho se for muito longo
            display_path = path
            if len(path) > 50:
                display_path = "..." + path[-47:]
            
            self.recent_menu.add_command(
                label=display_path,
                command=lambda p=path: self.open_recent_file(p)
            )
        
        # Adicionar opção para limpar a lista
        if self.recent_files:
            self.recent_menu.add_separator()
            self.recent_menu.add_command(label="Limpar Lista", command=self.clear_recent_files)
    
    def add_to_recent_files(self, path):
        """Adicionar arquivo à lista de recentes"""
        # Remover se já existir
        if path in self.recent_files:
            self.recent_files.remove(path)
        
        # Adicionar ao início da lista
        self.recent_files.insert(0, path)
        
        # Limitar o número de arquivos recentes
        max_recent = self.settings.get("max_recent", 10)
        if len(self.recent_files) > max_recent:
            self.recent_files = self.recent_files[:max_recent]
        
        # Atualizar menu e salvar
        self.update_recent_menu()
        self.save_recent_files()
    
    def open_recent_file(self, path):
        """Abrir um arquivo recente"""
        if os.path.exists(path):
            self.load_json_file(path)
        else:
            messagebox.showwarning("Arquivo não encontrado", f"O arquivo não foi encontrado:\n{path}")
            # Remover da lista de recentes
            if path in self.recent_files:
                self.recent_files.remove(path)
                self.update_recent_menu()
                self.save_recent_files()
    
    def clear_recent_files(self):
        """Limpar a lista de arquivos recentes"""
        if messagebox.askyesno("Limpar Lista", "Tem certeza que deseja limpar a lista de arquivos recentes?"):
            self.recent_files = []
            self.update_recent_menu()
            self.save_recent_files()
    
    def browse_file(self):
        """Abrir diálogo para selecionar arquivo JSON"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            self.load_json_file(file_path)
    
    def load_json_file(self, file_path):
        """Carregar arquivo JSON"""
        self.status_bar.set_status("Carregando arquivo...", 0)
        self.status_bar.start_progress()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.json_data = json.load(file)
            
            self.file_path_var.set(file_path)
            self.current_file_path = file_path
            
            # Adicionar à lista de arquivos recentes
            self.add_to_recent_files(file_path)
            
            # Extrair todos os campos possíveis do primeiro item
            if self.json_data and isinstance(self.json_data, list) and len(self.json_data) > 0:
                first_item = self.json_data[0]
                properties = first_item.get("properties", {})
                
                # Limpar e preencher a lista de campos disponíveis
                self.available_fields = list(properties.keys())
                self.update_available_listbox()
                
                # Limpar campos selecionados e resultados
                self.selected_fields = []
                self.selected_listbox.delete(0, tk.END)
                self.clear_results()
                
                self.status_bar.set_status(f"Arquivo carregado: {os.path.basename(file_path)} ({len(self.json_data)} itens)", 100)
                self.is_modified = False
                
                # Mostrar mensagem de sucesso
                messagebox.showinfo("Sucesso", f"Arquivo JSON carregado com sucesso.\n{len(self.json_data)} itens encontrados.")
            else:
                self.status_bar.set_status("Aviso: Formato de dados não reconhecido", 100)
                messagebox.showwarning("Aviso", "O arquivo JSON não contém dados no formato esperado.")
        
        except json.JSONDecodeError as e:
            self.status_bar.set_status("Erro: JSON inválido", 100)
            messagebox.showerror("Erro de JSON", f"O arquivo não contém JSON válido:\n{str(e)}")
            logger.error(f"Erro ao decodificar JSON: {str(e)}")
        
        except Exception as e:
            self.status_bar.set_status("Erro ao carregar arquivo", 100)
            messagebox.showerror("Erro", f"Erro ao carregar o arquivo JSON:\n{str(e)}")
            logger.error(f"Erro ao carregar arquivo: {str(e)}")
        
        finally:
            self.status_bar.stop_progress()
    
    def update_available_listbox(self):
        """Atualizar a lista de campos disponíveis"""
        self.available_listbox.delete(0, tk.END)
        
        search_text = self.available_search_var.get().lower()
        
        for field in sorted(self.available_fields):
            if not search_text or search_text in field.lower():
                self.available_listbox.insert(tk.END, field)
    
    def filter_available_fields(self, *args):
        """Filtrar a lista de campos disponíveis com base na pesquisa"""
        self.update_available_listbox()
    
    def filter_selected_fields(self, *args):
        """Filtrar a lista de campos selecionados com base na pesquisa"""
        self.selected_listbox.delete(0, tk.END)
        
        search_text = self.selected_search_var.get().lower()
        
        for field in self.selected_fields:
            if not search_text or search_text in field.lower():
                self.selected_listbox.insert(tk.END, field)
    
    def add_fields(self):
        """Adicionar campos selecionados à lista de campos selecionados"""
        selected_indices = self.available_listbox.curselection()
        
        for i in selected_indices:
            field = self.available_listbox.get(i)
            if field not in self.selected_fields:
                self.selected_fields.append(field)
        
        # Ordenar campos selecionados
        self.selected_fields.sort()
        
        # Atualizar listbox
        self.filter_selected_fields()
        self.is_modified = True
    
    def remove_fields(self):
        """Remover campos da lista de campos selecionados"""
        selected_indices = self.selected_listbox.curselection()
        
        # Converter para lista de campos
        fields_to_remove = [self.selected_listbox.get(i) for i in selected_indices]
        
        # Remover campos
        for field in fields_to_remove:
            if field in self.selected_fields:
                self.selected_fields.remove(field)
        
        # Atualizar listbox
        self.filter_selected_fields()
        self.is_modified = True
    
    def add_all_fields(self):
        """Adicionar todos os campos disponíveis"""
        self.selected_fields = list(self.available_fields)
        self.selected_fields.sort()
        self.filter_selected_fields()
        self.is_modified = True
    
    def remove_all_fields(self):
        """Remover todos os campos selecionados"""
        self.selected_fields = []
        self.selected_listbox.delete(0, tk.END)
        self.is_modified = True
    
    def extract_data(self):
        """Extrair dados com base nos campos selecionados"""
        if not self.json_data:
            messagebox.showwarning("Aviso", "Nenhum arquivo JSON carregado.")
            return
        
        if not self.selected_fields:
            messagebox.showwarning("Aviso", "Nenhum campo selecionado para extração.")
            return
        
        self.status_bar.set_status("Extraindo dados...", 0)
        self.status_bar.start_progress()
        
        try:
            # Limpar resultados anteriores
            self.clear_results()
            
            # Configurar as colunas da tabela
            self.result_tree["columns"] = self.selected_fields
            self.result_tree.column("#0", width=60, minwidth=60, stretch=tk.NO)
            self.result_tree.heading("#0", text="Item")
            
            for field in self.selected_fields:
                self.result_tree.column(field, width=150, minwidth=100)
                self.result_tree.heading(field, text=field.capitalize())
            
            # Extrair e mostrar os dados
            self.extracted_data = []
            total_items = len(self.json_data)
            
            for i, item in enumerate(self.json_data):
                properties = item.get("properties", {})
                row_data = {}
                
                for field in self.selected_fields:
                    row_data[field] = properties.get(field, "N/A")
                
                self.extracted_data.append(row_data)
                
                # Aplicar filtros se existirem
                if self.filters and not self.apply_filters(row_data):
                    continue
                
                # Adicionar à tabela
                values = [row_data.get(field, "N/A") for field in self.selected_fields]
                self.result_tree.insert("", tk.END, text=f"Item {i+1}", values=values, tags=('item',))
                
                # Atualizar barra de progresso a cada 100 itens
                if i % 100 == 0:
                    progress = int((i / total_items) * 100)
                    self.status_bar.set_status(f"Extraindo dados... ({i}/{total_items})", progress)
                    self.root.update_idletasks()
            
            # Atualizar visualização JSON
            self.update_json_view()
            
            # Alternar para a aba de tabela
            self.results_notebook.select(0)
            
            self.status_bar.set_status(f"Extração concluída: {len(self.extracted_data)} itens processados", 100)
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Extração Concluída", f"{len(self.extracted_data)} itens extraídos com sucesso.")
        
        except Exception as e:
            self.status_bar.set_status("Erro durante a extração", 100)
            messagebox.showerror("Erro", f"Erro ao extrair dados:\n{str(e)}")
            logger.error(f"Erro durante extração: {str(e)}")
        
        finally:
            self.status_bar.stop_progress()
    
    def apply_filters(self, row_data):
        """Aplicar filtros aos dados"""
        if not self.filters:
            return True
        
        for filter_item in self.filters:
            field = filter_item["field"]
            op = filter_item["op"]
            value = filter_item["value"]
            
            field_value = row_data.get(field, "")
            
            # Converter para números se possível para comparações numéricas
            try:
                if isinstance(field_value, str) and field_value.replace('.', '', 1).isdigit():
                    field_value = float(field_value)
                if value.replace('.', '', 1).isdigit():
                    value = float(value)
            except:
                pass
            
            # Aplicar operador
            if op == "=" and field_value != value:
                return False
            elif op == "!=" and field_value == value:
                return False
            elif op == ">" and not (isinstance(field_value, (int, float)) and field_value > value):
                return False
            elif op == "<" and not (isinstance(field_value, (int, float)) and field_value < value):
                return False
            elif op == ">=" and not (isinstance(field_value, (int, float)) and field_value >= value):
                return False
            elif op == "<=" and not (isinstance(field_value, (int, float)) and field_value <= value):
                return False
            elif op == "contém" and not (isinstance(field_value, str) and value in field_value):
                return False
            elif op == "não contém" and (isinstance(field_value, str) and value in field_value):
                return False
            elif op == "começa com" and not (isinstance(field_value, str) and field_value.startswith(value)):
                return False
            elif op == "termina com" and not (isinstance(field_value, str) and field_value.endswith(value)):
                return False
            elif op == "está vazio" and field_value:
                return False
            elif op == "não está vazio" and not field_value:
                return False
        
        return True
    
    def update_json_view(self):
        """Atualizar a visualização JSON"""
        if not self.extracted_data:
            return
        
        self.json_text.delete(1.0, tk.END)
        
        try:
            json_str = json.dumps(self.extracted_data, indent=2, ensure_ascii=False)
            self.json_text.insert(tk.END, json_str)
            
            # Adicionar destaque de sintaxe básico
            self.highlight_json()
        
        except Exception as e:
            self.json_text.insert(tk.END, f"Erro ao formatar JSON: {str(e)}")
            logger.error(f"Erro ao formatar JSON: {str(e)}")
    
    def highlight_json(self):
        """Adicionar destaque de sintaxe básico ao JSON"""
        # Esta é uma implementação simplificada
        # Em uma aplicação real, usaríamos uma biblioteca mais robusta
        
        # Configurar tags
        self.json_text.tag_configure("string", foreground="green")
        self.json_text.tag_configure("number", foreground="blue")
        self.json_text.tag_configure("boolean", foreground="purple")
        self.json_text.tag_configure("null", foreground="red")
        self.json_text.tag_configure("key", foreground="brown")
        
        # Aplicar destaque
        content = self.json_text.get(1.0, tk.END)
        
        # Strings
        start = 1.0
        while True:
            pos = self.json_text.search('"', start, tk.END)
            if not pos:
                break
            
            end_pos = self.json_text.search('"', f"{pos}+1c", tk.END)
            if not end_pos:
                break
            
            # Verificar se é uma chave
            line, col = map(int, pos.split('.'))
            line_content = self.json_text.get(f"{line}.0", f"{line}.end")
            
            if ':' in line_content[col:int(end_pos.split('.')[1])+2]:
                self.json_text.tag_add("key", pos, f"{end_pos}+1c")
            else:
                self.json_text.tag_add("string", pos, f"{end_pos}+1c")
            
            start = f"{end_pos}+1c"
        
        # Números
        for pattern in [r'\b\d+\b', r'\b\d+\.\d+\b']:
            start = 1.0
            while True:
                pos = self.json_text.search(pattern, start, tk.END, regexp=True)
                if not pos:
                    break
                
                line, col = map(int, pos.split('.'))
                line_content = self.json_text.get(f"{line}.0", f"{line}.end")
                
                # Encontrar o final do número
                match_length = 0
                for c in line_content[col:]:
                    if c.isdigit() or c == '.':
                        match_length += 1
                    else:
                        break
                
                end_pos = f"{line}.{col + match_length}"
                self.json_text.tag_add("number", pos, end_pos)
                
                start = end_pos
        
        # Booleanos e null
        for word, tag in [("true", "boolean"), ("false", "boolean"), ("null", "null")]:
            start = 1.0
            while True:
                pos = self.json_text.search(word, start, tk.END)
                if not pos:
                    break
                
                end_pos = f"{pos}+{len(word)}c"
                self.json_text.tag_add(tag, pos, end_pos)
                
                start = end_pos
    
    def clear_results(self):
        """Limpar resultados anteriores"""
        # Limpar tabela
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # Limpar visualização JSON
        self.json_text.delete(1.0, tk.END)
        
        # Limpar visualização
        for widget in self.viz_container.winfo_children():
            widget.destroy()
    
    def export_data(self):
        """Exportar dados extraídos"""
        if not self.extracted_data:
            messagebox.showwarning("Aviso", "Nenhum dado extraído para exportar.")
            return
        
        # Determinar o formato padrão
        default_format = self.settings.get("default_format", "csv")
        default_ext = {"csv": ".csv", "excel": ".xlsx", "json": ".json", "pdf": ".pdf"}[default_format]
        
        # Determinar a pasta padrão
        default_folder = self.settings.get("default_folder", "")
        initial_dir = default_folder if default_folder and os.path.exists(default_folder) else os.path.dirname(self.current_file_path) if self.current_file_path else None
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=[
                ("Arquivos CSV", "*.csv"),
                ("Arquivos Excel", "*.xlsx"),
                ("Arquivos JSON", "*.json"),
                ("Documentos PDF", "*.pdf"),
                ("Todos os arquivos", "*.*")
            ],
            initialdir=initial_dir
        )
        
        if not file_path:
            return
        
        self.status_bar.set_status("Exportando dados...", 0)
        self.status_bar.start_progress()
        
        try:
            # Determinar o formato com base na extensão
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.csv':
                self.export_to_csv(file_path)
            elif ext == '.xlsx':
                self.export_to_excel(file_path)
            elif ext == '.json':
                self.export_to_json(file_path)
            elif ext == '.pdf':
                self.export_to_pdf(file_path)
            else:
                # Formato padrão
                self.export_to_csv(file_path)
            
            self.status_bar.set_status(f"Dados exportados para {os.path.basename(file_path)}", 100)
            messagebox.showinfo("Exportação Concluída", f"Dados exportados com sucesso para:\n{file_path}")
        
        except Exception as e:
            self.status_bar.set_status("Erro ao exportar", 100)
            messagebox.showerror("Erro", f"Erro ao exportar dados:\n{str(e)}")
            logger.error(f"Erro ao exportar dados: {str(e)}")
        
        finally:
            self.status_bar.stop_progress()
    
    def export_to_csv(self, file_path):
        """Exportar dados para CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.selected_fields)
            writer.writeheader()
            writer.writerows(self.extracted_data)
    
    def export_to_excel(self, file_path):
        """Exportar dados para Excel"""
        df = pd.DataFrame(self.extracted_data)
        df.to_excel(file_path, index=False)
    
    def export_to_json(self, file_path):
        """Exportar dados para JSON"""
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.extracted_data, jsonfile, indent=2, ensure_ascii=False)
    
    def export_to_pdf(self, file_path):
        """Exportar dados para PDF"""
        # Esta é uma implementação simplificada
        # Em uma aplicação real, usaríamos uma biblioteca como ReportLab ou WeasyPrint
        
        # Converter para DataFrame
        df = pd.DataFrame(self.extracted_data)
        
        # Criar um arquivo HTML temporário
        html_file = file_path + ".temp.html"
        
        # Converter DataFrame para HTML
        html_content = df.to_html(index=False)
        
        # Adicionar estilos básicos
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Dados Exportados</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h1>Dados Exportados</h1>
            <p>Arquivo: {os.path.basename(self.current_file_path) if self.current_file_path else "Desconhecido"}</p>
            <p>Data: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
            {html_content}
        </body>
        </html>
        """
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(styled_html)
        
        # Converter HTML para PDF
        try:
            import weasyprint
            weasyprint.HTML(html_file).write_pdf(file_path)
        except ImportError:
            # Fallback se weasyprint não estiver disponível
            messagebox.showinfo("Informação", "Para exportar para PDF, instale a biblioteca WeasyPrint:\npip install weasyprint")
            webbrowser.open(html_file)
            return
        
        # Remover arquivo temporário
        try:
            os.remove(html_file)
        except:
            pass
    
    def save_results(self):
        """Salvar resultados no formato atual"""
        if not self.extracted_data:
            messagebox.showwarning("Aviso", "Nenhum dado extraído para salvar.")
            return
        
        if not self.current_file_path:
            self.save_as()
            return
        
        # Determinar o formato com base na extensão
        ext = os.path.splitext(self.current_file_path)[1].lower()
        
        # Criar um novo nome de arquivo para os resultados
        base_name = os.path.basename(self.current_file_path)
        base_name_without_ext = os.path.splitext(base_name)[0]
        dir_name = os.path.dirname(self.current_file_path)
        
        result_file = os.path.join(dir_name, f"{base_name_without_ext}_results.json")
        
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Salvo com Sucesso", f"Resultados salvos em:\n{result_file}")
            self.is_modified = False
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar resultados:\n{str(e)}")
            logger.error(f"Erro ao salvar resultados: {str(e)}")
    
    def save_as(self):
        """Salvar resultados com um novo nome"""
        if not self.extracted_data:
            messagebox.showwarning("Aviso", "Nenhum dado extraído para salvar.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("Arquivos JSON", "*.json"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Salvo com Sucesso", f"Resultados salvos em:\n{file_path}")
                self.is_modified = False
            
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar resultados:\n{str(e)}")
                logger.error(f"Erro ao salvar resultados: {str(e)}")
    
    def refresh_data(self):
        """Atualizar dados do arquivo atual"""
        if not self.current_file_path:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado para atualizar.")
            return
        
        if self.is_modified and messagebox.askyesno("Confirmar", "Há alterações não salvas. Deseja continuar e perder essas alterações?"):
            self.load_json_file(self.current_file_path)
        elif not self.is_modified:
            self.load_json_file(self.current_file_path)
    
    def show_filters(self):
        """Mostrar diálogo de filtros"""
        if not self.available_fields:
            messagebox.showwarning("Aviso", "Nenhum campo disponível para filtrar.")
            return
        
        dialog = FilterDialog(self.root, self.available_fields, self.apply_filters_callback)
        self.root.wait_window(dialog)
    
    def apply_filters_callback(self, filters):
        """Callback para aplicar filtros"""
        self.filters = filters
        
        if self.extracted_data:
            # Re-extrair dados com os novos filtros
            self.extract_data()
    
    def show_charts(self):
        """Mostrar diálogo de gráficos"""
        if not self.extracted_data:
            messagebox.showwarning("Aviso", "Extraia dados primeiro para criar gráficos.")
            return
        
        dialog = ChartDialog(self.root, self.extracted_data, self.selected_fields)
        self.root.wait_window(dialog)
    
    def show_batch_process(self):
        """Mostrar diálogo de processamento em lote"""
        dialog = BatchProcessDialog(self.root, self.batch_process_callback)
        self.root.wait_window(dialog)
    
    def batch_process_callback(self, files, options):
        """Callback para processamento em lote"""
        if not files:
            return
        
        self.status_bar.set_status(f"Processando em lote: 0/{len(files)}", 0)
        self.status_bar.start_progress()
        
        results = []
        fields_mode = options["fields_mode"]
        current_fields = self.selected_fields.copy() if fields_mode == "current" else []
        
        try:
            for i, file_path in enumerate(files):
                progress = int((i / len(files)) * 100)
                self.status_bar.set_status(f"Processando em lote: {i+1}/{len(files)} - {os.path.basename(file_path)}", progress)
                self.root.update_idletasks()
                
                # Carregar arquivo
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extrair campos se necessário
                if fields_mode == "auto" and data and isinstance(data, list) and len(data) > 0:
                    first_item = data[0]
                    properties = first_item.get("properties", {})
                    current_fields = list(properties.keys())
                
                # Extrair dados
                file_results = []
                for item in data:
                    properties = item.get("properties", {})
                    row_data = {}
                    
                    for field in current_fields:
                        row_data[field] = properties.get(field, "N/A")
                    
                    file_results.append(row_data)
                
                # Adicionar aos resultados
                results.extend(file_results)
                
                # Exportar se necessário
                if options["export"]:
                    dest_folder = options["dest_folder"]
                    base_name = os.path.basename(file_path)
                    base_name_without_ext = os.path.splitext(base_name)[0]
                    
                    export_format = options["export_format"]
                    ext = {"csv": ".csv", "excel": ".xlsx", "json": ".json"}[export_format]
                    
                    export_path = os.path.join(dest_folder, f"{base_name_without_ext}_results{ext}")
                    
                    # Exportar no formato selecionado
                    if export_format == "csv":
                        with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=current_fields)
                            writer.writeheader()
                            writer.writerows(file_results)
                    
                    elif export_format == "excel":
                        df = pd.DataFrame(file_results)
                        df.to_excel(export_path, index=False)
                    
                    elif export_format == "json":
                        with open(export_path, 'w', encoding='utf-8') as jsonfile:
                            json.dump(file_results, jsonfile, indent=2, ensure_ascii=False)
            
            # Atualizar interface com os resultados combinados
            if results:
                self.json_data = [{"properties": item} for item in results]
                self.extracted_data = results
                
                # Atualizar campos disponíveis
                all_fields = set()
                for item in results:
                    all_fields.update(item.keys())
                
                self.available_fields = list(all_fields)
                self.update_available_listbox()
                
                # Atualizar campos selecionados
                self.selected_fields = list(all_fields)
                self.selected_fields.sort()
                self.filter_selected_fields()
                
                # Atualizar resultados
                self.update_results_with_data(results)
                
                messagebox.showinfo("Processamento Concluído", 
                                   f"Processamento em lote concluído.\n{len(files)} arquivos processados.\n{len(results)} itens extraídos.")
            
            self.status_bar.set_status(f"Processamento em lote concluído: {len(files)} arquivos", 100)
        
        except Exception as e:
            self.status_bar.set_status("Erro no processamento em lote", 100)
            messagebox.showerror("Erro", f"Erro durante o processamento em lote:\n{str(e)}")
            logger.error(f"Erro no processamento em lote: {str(e)}")
        
        finally:
            self.status_bar.stop_progress()
    
    def update_results_with_data(self, data):
        """Atualizar resultados com dados fornecidos"""
        # Limpar resultados anteriores
        self.clear_results()
        
        # Configurar as colunas da tabela
        self.result_tree["columns"] = self.selected_fields
        self.result_tree.column("#0", width=60, minwidth=60, stretch=tk.NO)
        self.result_tree.heading("#0", text="Item")
        
        for field in self.selected_fields:
            self.result_tree.column(field, width=150, minwidth=100)
            self.result_tree.heading(field, text=field.capitalize())
        
        # Adicionar dados à tabela
        for i, row_data in enumerate(data):
            values = [row_data.get(field, "N/A") for field in self.selected_fields]
            self.result_tree.insert("", tk.END, text=f"Item {i+1}", values=values, tags=('item',))
        
        # Atualizar visualização JSON
        self.json_text.delete(1.0, tk.END)
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        self.json_text.insert(tk.END, json_str)
        self.highlight_json()
        
        # Alternar para a aba de tabela
        self.results_notebook.select(0)
    
    def show_statistics(self):
        """Mostrar estatísticas dos dados extraídos"""
        if not self.extracted_data:
            messagebox.showwarning("Aviso", "Extraia dados primeiro para ver estatísticas.")
            return
        
        # Converter para DataFrame para facilitar a análise
        df = pd.DataFrame(self.extracted_data)
        
        # Criar janela de estatísticas
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estatísticas dos Dados")
        stats_window.geometry("800x600")
        stats_window.transient(self.root)
        
        # Frame principal
        main_frame = ttk.Frame(stats_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para diferentes tipos de estatísticas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de resumo
        summary_frame = ttk.Frame(notebook, padding=10)
        notebook.add(summary_frame, text="Resumo")
        
        # Informações gerais
        ttk.Label(summary_frame, text="Informações Gerais", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        info_text = f"""
        Total de itens: {len(self.extracted_data)}
        Total de campos: {len(self.selected_fields)}
        """
        
        ttk.Label(summary_frame, text=info_text).pack(anchor=tk.W, pady=(0, 10))
        
        # Estatísticas numéricas
        ttk.Label(summary_frame, text="Estatísticas Numéricas", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(10, 10))
        
        # Encontrar campos numéricos
        numeric_fields = []
        for field in self.selected_fields:
            try:
                # Verificar se o campo pode ser convertido para numérico
                pd.to_numeric(df[field], errors='raise')
                numeric_fields.append(field)
            except:
                continue
        
        if numeric_fields:
            # Criar tabela para estatísticas numéricas
            stats_frame = ttk.Frame(summary_frame)
            stats_frame.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbars
            y_scrollbar = ttk.Scrollbar(stats_frame)
            y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            x_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.HORIZONTAL)
            x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Treeview para estatísticas
            stats_tree = ttk.Treeview(stats_frame, yscrollcommand=y_scrollbar.set, 
                                     xscrollcommand=x_scrollbar.set)
            stats_tree.pack(fill=tk.BOTH, expand=True)
            
            y_scrollbar.config(command=stats_tree.yview)
            x_scrollbar.config(command=stats_tree.xview)
            
            # Configurar colunas
            stats = ["Contagem", "Média", "Mediana", "Mínimo", "Máximo", "Desvio Padrão"]
            stats_tree["columns"] = stats
            stats_tree.column("#0", width=150, minwidth=150)
            stats_tree.heading("#0", text="Campo")
            
            for stat in stats:
                stats_tree.column(stat, width=100, minwidth=80)
                stats_tree.heading(stat, text=stat)
            
            # Calcular e adicionar estatísticas
            for field in numeric_fields:
                numeric_data = pd.to_numeric(df[field], errors='coerce')
                
                count = numeric_data.count()
                mean = numeric_data.mean() if count > 0 else "N/A"
                median = numeric_data.median() if count > 0 else "N/A"
                min_val = numeric_data.min() if count > 0 else "N/A"
                max_val = numeric_data.max() if count > 0 else "N/A"
                std = numeric_data.std() if count > 0 else "N/A"
                
                # Formatar valores
                mean = f"{mean:.2f}" if isinstance(mean, float) else mean
                median = f"{median:.2f}" if isinstance(median, float) else median
                std = f"{std:.2f}" if isinstance(std, float) else std
                
                stats_tree.insert("", tk.END, text=field, values=[count, mean, median, min_val, max_val, std])
        else:
            ttk.Label(summary_frame, text="Nenhum campo numérico encontrado.").pack(anchor=tk.W)
        
        # Aba de distribuição de valores
        dist_frame = ttk.Frame(notebook, padding=10)
        notebook.add(dist_frame, text="Distribuição de Valores")
        
        # Seleção de campo
        field_frame = ttk.Frame(dist_frame)
        field_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(field_frame, text="Campo:").pack(side=tk.LEFT, padx=(0, 5))
        
        field_var = tk.StringVar()
        field_combo = ttk.Combobox(field_frame, textvariable=field_var, values=self.selected_fields, state="readonly")
        field_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if self.selected_fields:
            field_combo.current(0)
        
        # Frame para o gráfico
        chart_frame = ttk.Frame(dist_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Função para atualizar o gráfico
        def update_chart(*args):
            field = field_var.get()
            if not field:
                return
            
            # Limpar frame do gráfico
            for widget in chart_frame.winfo_children():
                widget.destroy()
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            
            # Verificar tipo de dados
            try:
                # Tentar converter para numérico
                numeric_data = pd.to_numeric(df[field], errors='coerce')
                if numeric_data.count() > 0:
                    # Histograma para dados numéricos
                    numeric_data.plot(kind='hist', bins=20, ax=ax)
                    ax.set_title(f"Distribuição de {field}")
                    ax.set_xlabel(field)
                    ax.set_ylabel("Frequência")
                else:
                    raise ValueError("Sem dados numéricos")
            except:
                # Gráfico de barras para dados categóricos
                value_counts = df[field].value_counts().sort_values(ascending=False).head(20)
                value_counts.plot(kind='bar', ax=ax)
                ax.set_title(f"Top 20 valores para {field}")
                ax.set_xlabel(field)
                ax.set_ylabel("Contagem")
                plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            
            # Adicionar canvas ao frame
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Vincular atualização do gráfico à seleção de campo
        field_var.trace("w", update_chart)
        
        # Inicializar com o primeiro campo
        if self.selected_fields:
            update_chart()
        
        # Aba de correlação (apenas para campos numéricos)
        if len(numeric_fields) >= 2:
            corr_frame = ttk.Frame(notebook, padding=10)
            notebook.add(corr_frame, text="Correlação")
            
            # Criar matriz de correlação
            numeric_df = df[numeric_fields].apply(pd.to_numeric, errors='coerce')
            corr_matrix = numeric_df.corr()
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
            
            # Criar mapa de calor
            im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
            
            # Adicionar barra de cores
            plt.colorbar(im, ax=ax)
            
            # Configurar eixos
            ax.set_xticks(np.arange(len(numeric_fields)))
            ax.set_yticks(np.arange(len(numeric_fields)))
            ax.set_xticklabels(numeric_fields, rotation=45, ha='right')
            ax.set_yticklabels(numeric_fields)
            
            # Adicionar valores
            for i in range(len(numeric_fields)):
                for j in range(len(numeric_fields)):
                    text = ax.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}",
                                  ha="center", va="center", color="black")
            
            ax.set_title("Matriz de Correlação")
            plt.tight_layout()
            
            # Adicionar canvas ao frame
            canvas = FigureCanvasTkAgg(fig, master=corr_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def validate_json(self):
        """Validar o JSON carregado"""
        if not self.current_file_path:
            messagebox.showwarning("Aviso", "Nenhum arquivo JSON carregado.")
            return
        
        try:
            with open(self.current_file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            
            messagebox.showinfo("Validação", "O arquivo JSON é válido.")
        
        except json.JSONDecodeError as e:
            messagebox.showerror("Erro de JSON", f"O arquivo contém JSON inválido:\n{str(e)}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao validar o arquivo JSON:\n{str(e)}")
    
    def format_json(self):
        """Formatar o JSON carregado"""
        if not self.current_file_path:
            messagebox.showwarning("Aviso", "Nenhum arquivo JSON carregado.")
            return
        
        try:
            # Ler o JSON
            with open(self.current_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Criar um novo nome de arquivo
            base_name = os.path.basename(self.current_file_path)
            base_name_without_ext = os.path.splitext(base_name)[0]
            dir_name = os.path.dirname(self.current_file_path)
            
            formatted_file = os.path.join(dir_name, f"{base_name_without_ext}_formatted.json")
            
            # Escrever o JSON formatado
            with open(formatted_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Formatação Concluída", f"JSON formatado salvo em:\n{formatted_file}")
        
        except json.JSONDecodeError as e:
            messagebox.showerror("Erro de JSON", f"O arquivo contém JSON inválido:\n{str(e)}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao formatar o arquivo JSON:\n{str(e)}")
    
    def compare_files(self):
        """Comparar dois arquivos JSON"""
        # Selecionar o primeiro arquivo
        file1 = filedialog.askopenfilename(
            title="Selecione o primeiro arquivo JSON",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        
        if not file1:
            return
        
        # Selecionar o segundo arquivo
        file2 = filedialog.askopenfilename(
            title="Selecione o segundo arquivo JSON",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        
        if not file2:
            return
        
        try:
            # Carregar os arquivos
            with open(file1, 'r', encoding='utf-8') as f:
                data1 = json.load(f)
            
            with open(file2, 'r', encoding='utf-8') as f:
                data2 = json.load(f)
            
            # Verificar se são listas
            if not isinstance(data1, list) or not isinstance(data2, list):
                messagebox.showwarning("Aviso", "Ambos os arquivos devem conter listas de objetos.")
                return
            
            # Extrair propriedades
            props1 = [item.get("properties", {}) for item in data1]
            props2 = [item.get("properties", {}) for item in data2]
            
            # Encontrar todos os campos
            all_fields = set()
            for item in props1 + props2:
                all_fields.update(item.keys())
            
            # Criar DataFrames
            df1 = pd.DataFrame(props1)
            df2 = pd.DataFrame(props2)
            
            # Criar janela de comparação
            compare_window = tk.Toplevel(self.root)
            compare_window.title("Comparação de Arquivos")
            compare_window.geometry("900x700")
            compare_window.transient(self.root)
            
            # Frame principal
            main_frame = ttk.Frame(compare_window, padding=10)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Informações dos arquivos
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(info_frame, text=f"Arquivo 1: {os.path.basename(file1)} ({len(data1)} itens)").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Arquivo 2: {os.path.basename(file2)} ({len(data2)} itens)").pack(anchor=tk.W)
            
            # Notebook para diferentes visualizações
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True)
            
            # Aba de resumo
            summary_frame = ttk.Frame(notebook, padding=10)
            notebook.add(summary_frame, text="Resumo")
            
            # Diferenças de tamanho
            ttk.Label(summary_frame, text="Diferenças de Tamanho", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
            
            size_diff = len(data1) - len(data2)
            if size_diff > 0:
                ttk.Label(summary_frame, text=f"O arquivo 1 tem {size_diff} itens a mais que o arquivo 2.").pack(anchor=tk.W)
            elif size_diff < 0:
                ttk.Label(summary_frame, text=f"O arquivo 2 tem {abs(size_diff)} itens a mais que o arquivo 1.").pack(anchor=tk.W)
            else:
                ttk.Label(summary_frame, text="Ambos os arquivos têm o mesmo número de itens.").pack(anchor=tk.W)
            
            # Diferenças de campos
            ttk.Label(summary_frame, text="Diferenças de Campos", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(10, 10))
            
            fields1 = set(df1.columns)
            fields2 = set(df2.columns)
            
            unique_fields1 = fields1 - fields2
            unique_fields2 = fields2 - fields1
            common_fields = fields1.intersection(fields2)
            
            if unique_fields1:
                ttk.Label(summary_frame, text=f"Campos exclusivos do arquivo 1: {', '.join(unique_fields1)}").pack(anchor=tk.W)
            else:
                ttk.Label(summary_frame, text="Não há campos exclusivos do arquivo 1.").pack(anchor=tk.W)
            
            if unique_fields2:
                ttk.Label(summary_frame, text=f"Campos exclusivos do arquivo 2: {', '.join(unique_fields2)}").pack(anchor=tk.W)
            else:
                ttk.Label(summary_frame, text="Não há campos exclusivos do arquivo 2.").pack(anchor=tk.W)
            
            ttk.Label(summary_frame, text=f"Campos em comum: {len(common_fields)}").pack(anchor=tk.W)
            
            # Aba de diferenças de valores
            values_frame = ttk.Frame(notebook, padding=10)
            notebook.add(values_frame, text="Diferenças de Valores")
            
            # Seleção de campo
            field_frame = ttk.Frame(values_frame)
            field_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(field_frame, text="Campo:").pack(side=tk.LEFT, padx=(0, 5))
            
            field_var = tk.StringVar()
            field_combo = ttk.Combobox(field_frame, textvariable=field_var, values=sorted(common_fields), state="readonly")
            field_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            if common_fields:
                field_combo.current(0)
            
            # Tabela de diferenças
            diff_frame = ttk.Frame(values_frame)
            diff_frame.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbars
            y_scrollbar = ttk.Scrollbar(diff_frame)
            y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            x_scrollbar = ttk.Scrollbar(diff_frame, orient=tk.HORIZONTAL)
            x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Treeview para diferenças
            diff_tree = ttk.Treeview(diff_frame, yscrollcommand=y_scrollbar.set, 
                                    xscrollcommand=x_scrollbar.set)
            diff_tree.pack(fill=tk.BOTH, expand=True)
            
            y_scrollbar.config(command=diff_tree.yview)
            x_scrollbar.config(command=diff_tree.xview)
            
            # Configurar colunas
            diff_tree["columns"] = ["index", "valor1", "valor2"]
            diff_tree.column("#0", width=60, minwidth=60, stretch=tk.NO)
            diff_tree.heading("#0", text="Status")
            
            diff_tree.column("index", width=80, minwidth=80)
            diff_tree.heading("index", text="Índice")
            
            diff_tree.column("valor1", width=300, minwidth=150)
            diff_tree.heading("valor1", text="Valor no Arquivo 1")
            
            diff_tree.column("valor2", width=300, minwidth=150)
            diff_tree.heading("valor2", text="Valor no Arquivo 2")
            
            # Função para atualizar a tabela de diferenças
            def update_diff_table(*args):
                field = field_var.get()
                if not field:
                    return
                
                # Limpar tabela
                for item in diff_tree.get_children():
                    diff_tree.delete(item)
                
                # Comparar valores
                for i in range(max(len(df1), len(df2))):
                    if i < len(df1) and i < len(df2):
                        val1 = df1.iloc[i].get(field, "N/A")
                        val2 = df2.iloc[i].get(field, "N/A")
                        
                        if val1 != val2:
                            diff_tree.insert("", tk.END, text="≠", values=[i, val1, val2], tags=('diff',))
                    elif i < len(df1):
                        val1 = df1.iloc[i].get(field, "N/A")
                        diff_tree.insert("", tk.END, text="+", values=[i, val1, "N/A"], tags=('add',))
                    elif i < len(df2):
                        val2 = df2.iloc[i].get(field, "N/A")
                        diff_tree.insert("", tk.END, text="-", values=[i, "N/A", val2], tags=('remove',))
            
            # Configurar cores para as diferenças
            diff_tree.tag_configure('diff', background='#ffffcc')
            diff_tree.tag_configure('add', background='#ccffcc')
            diff_tree.tag_configure('remove', background='#ffcccc')
            
            # Vincular atualização da tabela à seleção de campo
            field_var.trace("w", update_diff_table)
            
            # Inicializar com o primeiro campo
            if common_fields:
                update_diff_table()
            
            # Aba de estatísticas comparativas
            stats_frame = ttk.Frame(notebook, padding=10)
            notebook.add(stats_frame, text="Estatísticas Comparativas")
            
            # Encontrar campos numéricos comuns
            numeric_fields = []
            for field in common_fields:
                try:
                    pd.to_numeric(df1[field], errors='raise')
                    pd.to_numeric(df2[field], errors='raise')
                    numeric_fields.append(field)
                except:
                    continue
            
            if numeric_fields:
                # Criar tabela para estatísticas comparativas
                stats_tree_frame = ttk.Frame(stats_frame)
                stats_tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
                
                # Scrollbars
                stats_y_scrollbar = ttk.Scrollbar(stats_tree_frame)
                stats_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                stats_x_scrollbar = ttk.Scrollbar(stats_tree_frame, orient=tk.HORIZONTAL)
                stats_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
                
                # Treeview para estatísticas
                stats_tree = ttk.Treeview(stats_tree_frame, yscrollcommand=stats_y_scrollbar.set, 
                                         xscrollcommand=stats_x_scrollbar.set)
                stats_tree.pack(fill=tk.BOTH, expand=True)
                
                stats_y_scrollbar.config(command=stats_tree.yview)
                stats_x_scrollbar.config(command=stats_tree.xview)
                
                # Configurar colunas
                stats = ["média1", "média2", "diff_média", "mediana1", "mediana2", "diff_mediana", 
                        "min1", "min2", "diff_min", "max1", "max2", "diff_max"]
                stats_tree["columns"] = stats
                stats_tree.column("#0", width=150, minwidth=150)
                stats_tree.heading("#0", text="Campo")
                
                for stat in stats:
                    stats_tree.column(stat, width=80, minwidth=80)
                    stats_tree.heading(stat, text=stat.replace('_', ' ').capitalize())
                
                # Calcular e adicionar estatísticas
                for field in numeric_fields:
                    numeric_data1 = pd.to_numeric(df1[field], errors='coerce')
                    numeric_data2 = pd.to_numeric(df2[field], errors='coerce')
                    
                    mean1 = numeric_data1.mean()
                    mean2 = numeric_data2.mean()
                    diff_mean = mean1 - mean2
                    
                    median1 = numeric_data1.median()
                    median2 = numeric_data2.median()
                    diff_median = median1 - median2
                    
                    min1 = numeric_data1.min()
                    min2 = numeric_data2.min()
                    diff_min = min1 - min2
                    
                    max1 = numeric_data1.max()
                    max2 = numeric_data2.max()
                    diff_max = max1 - max2
                    
                    # Formatar valores
                    values = [
                        f"{mean1:.2f}", f"{mean2:.2f}", f"{diff_mean:.2f}",
                        f"{median1:.2f}", f"{median2:.2f}", f"{diff_median:.2f}",
                        f"{min1:.2f}", f"{min2:.2f}", f"{diff_min:.2f}",
                        f"{max1:.2f}", f"{max2:.2f}", f"{diff_max:.2f}"
                    ]
                    
                    stats_tree.insert("", tk.END, text=field, values=values)
                
                # Adicionar gráfico comparativo
                chart_frame = ttk.LabelFrame(stats_frame, text="Gráfico Comparativo")
                chart_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
                
                # Seleção de campo para o gráfico
                chart_field_frame = ttk.Frame(chart_frame)
                chart_field_frame.pack(fill=tk.X, pady=(5, 10))
                
                ttk.Label(chart_field_frame, text="Campo:").pack(side=tk.LEFT, padx=(0, 5))
                
                chart_field_var = tk.StringVar()
                chart_field_combo = ttk.Combobox(chart_field_frame, textvariable=chart_field_var, 
                                               values=numeric_fields, state="readonly")
                chart_field_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                if numeric_fields:
                    chart_field_combo.current(0)
                
                # Frame para o gráfico
                chart_container = ttk.Frame(chart_frame)
                chart_container.pack(fill=tk.BOTH, expand=True)
                
                # Função para atualizar o gráfico
                def update_chart(*args):
                    field = chart_field_var.get()
                    if not field:
                        return
                    
                    # Limpar frame do gráfico
                    for widget in chart_container.winfo_children():
                        widget.destroy()
                    
                    # Criar figura
                    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
                    
                    # Converter para numérico
                    numeric_data1 = pd.to_numeric(df1[field], errors='coerce')
                    numeric_data2 = pd.to_numeric(df2[field], errors='coerce')
                    
                    # Criar histograma comparativo
                    ax.hist(numeric_data1.dropna(), bins=20, alpha=0.5, label=f"Arquivo 1")
                    ax.hist(numeric_data2.dropna(), bins=20, alpha=0.5, label=f"Arquivo 2")
                    
                    ax.set_title(f"Comparação de {field}")
                    ax.set_xlabel(field)
                    ax.set_ylabel("Frequência")
                    ax.legend()
                    
                    plt.tight_layout()
                    
                    # Adicionar canvas ao frame
                    canvas = FigureCanvasTkAgg(fig, master=chart_container)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                # Vincular atualização do gráfico à seleção de campo
                chart_field_var.trace("w", update_chart)
                
                # Inicializar com o primeiro campo
                if numeric_fields:
                    update_chart()
            else:
                ttk.Label(stats_frame, text="Nenhum campo numérico comum encontrado para análise estatística.").pack(anchor=tk.W)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao comparar os arquivos:\n{str(e)}")
            logger.error(f"Erro ao comparar arquivos: {str(e)}")
    
    def merge_files(self):
        """Mesclar múltiplos arquivos JSON"""
        # Selecionar arquivos
        file_paths = filedialog.askopenfilenames(
            title="Selecione os arquivos JSON para mesclar",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_paths:
            return
        
        try:
            # Carregar todos os arquivos
            all_data = []
            
            for file_path in file_paths:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    messagebox.showwarning("Aviso", f"O arquivo {os.path.basename(file_path)} não contém uma lista de objetos.")
            
            if not all_data:
                messagebox.showwarning("Aviso", "Nenhum dado válido encontrado para mesclar.")
                return
            
            # Salvar arquivo mesclado
            save_path = filedialog.asksaveasfilename(
                title="Salvar arquivo mesclado",
                defaultextension=".json",
                filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
            )
            
            if not save_path:
                return
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Mesclagem Concluída", 
                               f"Arquivos mesclados com sucesso.\n{len(file_paths)} arquivos combinados.\n{len(all_data)} itens no total.\nSalvo em: {save_path}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao mesclar os arquivos:\n{str(e)}")
            logger.error(f"Erro ao mesclar arquivos: {str(e)}")
    
    def search_callback(self, search_text, options):
        """Callback para pesquisa"""
        if not self.extracted_data or not search_text:
            return
        
        if options.get("clear", False):
            # Limpar pesquisa e mostrar todos os itens
            for item in self.result_tree.get_children():
                self.result_tree.item(item, tags=('item',))
            return
        
        # Configurar opções de pesquisa
        case_sensitive = options.get("case_sensitive", False)
        use_regex = options.get("regex", False)
        search_fields = options.get("fields", "all")
        
        # Preparar o texto de pesquisa
        if not case_sensitive and not use_regex:
            search_text = search_text.lower()
        
        # Determinar campos para pesquisar
        fields_to_search = self.selected_fields if search_fields == "all" else [f for f in self.selected_fields if f in self.selected_listbox.get(0, tk.END)]
        
        # Limpar tags anteriores
        for item in self.result_tree.get_children():
            self.result_tree.item(item, tags=('item',))
        
        # Configurar tag para resultados
        self.result_tree.tag_configure('match', background='#ffffcc')
        
        # Pesquisar nos itens
        for item in self.result_tree.get_children():
            values = self.result_tree.item(item)['values']
            
            for i, field in enumerate(self.selected_fields):
                if field not in fields_to_search:
                    continue
                
                value = str(values[i])
                
                if use_regex:
                    try:
                        pattern = re.compile(search_text, 0 if case_sensitive else re.IGNORECASE)
                        if pattern.search(value):
                            self.result_tree.item(item, tags=('match',))
                            break
                    except re.error:
                        # Ignorar erros de regex inválido
                        pass
                else:
                    if not case_sensitive:
                        value = value.lower()
                    
                    if search_text in value:
                        self.result_tree.item(item, tags=('match',))
                        break
    
    def focus_search(self):
        """Focar no campo de pesquisa"""
        self.search_frame.search_entry.focus_set()
    
    def copy_selection(self):
        """Copiar seleção para a área de transferência"""
        focused_widget = self.root.focus_get()
        
        if focused_widget == self.result_tree:
            # Copiar da tabela de resultados
            selected_items = self.result_tree.selection()
            if not selected_items:
                return
            
            # Preparar dados
            headers = ["Item"] + list(self.selected_fields)
            rows = [headers]
            
            for item in selected_items:
                item_text = self.result_tree.item(item, "text")
                values = self.result_tree.item(item, "values")
                rows.append([item_text] + list(values))
            
            # Formatar como texto tabulado
            text = "\n".join(["\t".join(map(str, row)) for row in rows])
            
            # Copiar para a área de transferência
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            
            self.status_bar.set_status(f"{len(selected_items)} itens copiados para a área de transferência")
        
        elif focused_widget == self.json_text:
            # Copiar do texto JSON
            selected_text = self.json_text.get(tk.SEL_FIRST, tk.SEL_LAST) if self.json_text.tag_ranges(tk.SEL) else ""
            
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                
                self.status_bar.set_status("Texto selecionado copiado para a área de transferência")
    
    def select_all(self):
        """Selecionar todos os itens"""
        focused_widget = self.root.focus_get()
        
        if focused_widget == self.result_tree:
            # Selecionar todos os itens na tabela
            for item in self.result_tree.get_children():
                self.result_tree.selection_add(item)
        
        elif focused_widget == self.json_text:
            # Selecionar todo o texto
            self.json_text.tag_add(tk.SEL, "1.0", tk.END)
            self.json_text.mark_set(tk.INSERT, "1.0")
            self.json_text.see(tk.INSERT)
    
    def expand_all(self):
        """Expandir todos os itens na tabela"""
        for item in self.result_tree.get_children():
            self.result_tree.item(item, open=True)
    
    def collapse_all(self):
        """Recolher todos os itens na tabela"""
        for item in self.result_tree.get_children():
            self.result_tree.item(item, open=False)
    
    def show_context_menu(self, event):
        """Mostrar menu de contexto para a tabela de resultados"""
        # Criar menu de contexto
        context_menu = tk.Menu(self.root, tearoff=0)
        
        # Adicionar opções
        context_menu.add_command(label="Copiar", command=self.copy_selection)
        context_menu.add_command(label="Selecionar Todos", command=self.select_all)
        context_menu.add_separator()
        context_menu.add_command(label="Exportar Seleção", command=self.export_selection)
        
        # Mostrar menu
        context_menu.post(event.x_root, event.y_root)
    
    def export_selection(self):
        """Exportar apenas os itens selecionados"""
        selected_items = self.result_tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Nenhum item selecionado para exportar.")
            return
        
        # Coletar dados dos itens selecionados
        selected_data = []
        
        for item in selected_items:
            values = self.result_tree.item(item, "values")
            row_data = {}
            
            for i, field in enumerate(self.selected_fields):
                row_data[field] = values[i]
            
            selected_data.append(row_data)
        
        # Determinar o formato padrão
        default_format = self.settings.get("default_format", "csv")
        default_ext = {"csv": ".csv", "excel": ".xlsx", "json": ".json", "pdf": ".pdf"}[default_format]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=[
                ("Arquivos CSV", "*.csv"),
                ("Arquivos Excel", "*.xlsx"),
                ("Arquivos JSON", "*.json"),
                ("Documentos PDF", "*.pdf"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Determinar o formato com base na extensão
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.csv':
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.selected_fields)
                    writer.writeheader()
                    writer.writerows(selected_data)
            
            elif ext == '.xlsx':
                df = pd.DataFrame(selected_data)
                df.to_excel(file_path, index=False)
            
            elif ext == '.json':
                with open(file_path, 'w', encoding='utf-8') as jsonfile:
                    json.dump(selected_data, jsonfile, indent=2, ensure_ascii=False)
            
            elif ext == '.pdf':
                # Converter para DataFrame
                df = pd.DataFrame(selected_data)
                
                # Criar um arquivo HTML temporário
                html_file = file_path + ".temp.html"
                
                # Converter DataFrame para HTML
                html_content = df.to_html(index=False)
                
                # Adicionar estilos básicos
                styled_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Seleção Exportada</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    </style>
                </head>
                <body>
                    <h1>Seleção Exportada</h1>
                    <p>Arquivo: {os.path.basename(self.current_file_path) if self.current_file_path else "Desconhecido"}</p>
                    <p>Data: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                    <p>Itens selecionados: {len(selected_data)}</p>
                    {html_content}
                </body>
                </html>
                """
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(styled_html)
                
                # Converter HTML para PDF
                try:
                    import weasyprint
                    weasyprint.HTML(html_file).write_pdf(file_path)
                except ImportError:
                    # Fallback se weasyprint não estiver disponível
                    messagebox.showinfo("Informação", "Para exportar para PDF, instale a biblioteca WeasyPrint:\npip install weasyprint")
                    webbrowser.open(html_file)
                    return
                
                # Remover arquivo temporário
                try:
                    os.remove(html_file)
                except:
                    pass
            
            messagebox.showinfo("Exportação Concluída", f"{len(selected_data)} itens exportados com sucesso para:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar seleção:\n{str(e)}")
            logger.error(f"Erro ao exportar seleção: {str(e)}")
    
    def start_drag(self, event):
        """Iniciar operação de arrastar"""
        # Esta é uma implementação simplificada
        # Em uma aplicação real, seria mais complexo
        pass
    
    def handle_drop(self, event):
        """Manipular soltar arquivos"""
        # Obter caminho do arquivo
        file_path = event.data
        
        # Remover chaves e aspas se presentes (formato do TkDND)
        if file_path.startswith("{") and file_path.endswith("}"):
            file_path = file_path[1:-1]
        
        if file_path.startswith('"') and file_path.endswith('"'):
            file_path = file_path[1:-1]
        
        # Verificar se é um arquivo JSON
        if file_path.lower().endswith(".json"):
            self.load_json_file(file_path)
        else:
            messagebox.showwarning("Arquivo não suportado", "Apenas arquivos JSON são suportados.")
    
    def show_settings(self):
        """Mostrar diálogo de configurações"""
        dialog = SettingsDialog(self.root, self.settings, self.update_settings)
        self.root.wait_window(dialog)
    
    def update_settings(self, new_settings):
        """Atualizar configurações"""
        old_theme = self.settings.get("theme")
        old_font_size = self.settings.get("font_size")
        
        self.settings.update(new_settings)
        
        # Aplicar novas configurações
        if old_theme != new_settings["theme"] or old_font_size != new_settings["font_size"]:
            self.apply_theme()
        
        # Salvar configurações
        if new_settings.get("autosave", False):
            self.save_settings()
    
    def show_documentation(self):
        """Mostrar documentação"""
        # Em uma aplicação real, abriria a documentação
        webbrowser.open("https://github.com/seu-usuario/jsonmaster-pro/wiki")
    
    def show_shortcuts(self):
        """Mostrar atalhos de teclado"""
        shortcuts = """
        Atalhos de Teclado:
        
        Arquivo:
        - Ctrl+O: Abrir arquivo
        - Ctrl+S: Salvar resultados
        - Ctrl+Shift+S: Salvar como
        - Ctrl+E: Exportar dados
        - Alt+F4: Sair
        
        Editar:
        - Ctrl+C: Copiar seleção
        - Ctrl+A: Selecionar tudo
        - Ctrl+F: Pesquisar
        - Ctrl+Shift+F: Filtrar
        
        Visualizar:
        - F5: Atualizar
        """
        
        messagebox.showinfo("Atalhos de Teclado", shortcuts)
    
    def check_updates(self):
        """Verificar atualizações"""
        # Em uma aplicação real, verificaria atualizações online
        messagebox.showinfo("Verificação de Atualizações", "Você está usando a versão mais recente do JSONMaster Pro.")
    
    def show_about(self):
        """Mostrar informações sobre o aplicativo"""
        about_text = """
        JSONMaster Pro - Extrator e Analisador Avançado
        
        Versão: 2.0.0
        
        Uma ferramenta poderosa para extração, análise e visualização de dados JSON.
        
        Desenvolvido por: Seu Nome
        
        © 2023 Todos os direitos reservados.
        """
        
        messagebox.showinfo("Sobre", about_text)
    
    def confirm_exit(self):
        """Confirmar saída do aplicativo"""
        if self.settings.get("confirm_exit", True) and self.is_modified:
            if not messagebox.askyesno("Confirmar Saída", "Há alterações não salvas. Deseja realmente sair?"):
                return
        
        # Salvar configurações e arquivos recentes
        self.save_settings()
        self.save_recent_files()
        
        # Fechar aplicativo
        self.root.destroy()

def main():
    # Usar ThemedTk para temas mais modernos
    try:
        root = ThemedTk(theme="arc")
    except:
        # Fallback para Tk padrão
        root = tk.Tk()
    
    app = JSONMasterPro(root)
    root.mainloop()

if __name__ == "__main__":
    main()