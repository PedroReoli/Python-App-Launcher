# Aplicação que mostra todos os arquivos e pastas de um diretório em formato markdown, html ou json.
import os
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox, font
import pathlib
from datetime import datetime
import json
import webbrowser
import threading
import re
import shutil
from functools import partial
import locale

# Configurar localização para português
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass  # Fallback para o locale padrão se não encontrar português

class VisualizadorDiretorios:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Estrutura de Diretórios")
        self.root.geometry("1100x750")
        
        # Configurações iniciais
        self.configurar_variaveis()
        self.configurar_tema()
        self.criar_widgets()
        self.carregar_configuracoes()
        
        # Centralizar a janela na tela
        self.centralizar_janela()
        
        # Configurar atalhos de teclado
        self.configurar_atalhos()
        
    def configurar_variaveis(self):
        """Configurar variáveis de controle e estado"""
        # Variáveis de controle
        self.tema_escuro = tk.BooleanVar(value=False)
        self.incluir_ocultos = tk.BooleanVar(value=False)
        self.mostrar_tamanho = tk.BooleanVar(value=True)
        self.profundidade_maxima = tk.StringVar(value="0")
        self.formato_saida = tk.StringVar(value="markdown")
        
        # Pastas a ignorar
        self.pastas_ignoradas = ["node_modules", ".git", ".idea", "__pycache__", "venv", "env", ".venv", ".env"]
        self.ignorar_padrao = tk.StringVar(value=",".join(self.pastas_ignoradas))
        
        # Filtro de extensões
        self.filtrar_extensoes = tk.BooleanVar(value=False)
        self.extensoes_filtro = tk.StringVar(value="")
        
        # Histórico de diretórios
        self.historico_diretorios = []
        self.max_historico = 10
        
        # Variáveis de estado
        self.diretorio_atual = ""
        self.ultima_saida = ""
        self.gerando_visualizacao = False
        
    def configurar_tema(self):
        """Configurar cores e estilos do tema"""
        # Tema claro (padrão)
        self.temas = {
            "claro": {
                "bg_principal": "#f8f9fa",
                "bg_cartao": "#ffffff",
                "texto_principal": "#212529",
                "texto_secundario": "#6c757d",
                "cor_destaque": "#0d6efd",
                "cor_destaque_hover": "#0b5ed7",
                "cor_borda": "#dee2e6",
                "bg_entrada": "#ffffff",
                "bg_saida": "#f8f9fa",
                "bg_botao_primario": "#0d6efd",
                "texto_botao_primario": "#ffffff",
                "bg_botao_secundario": "#e9ecef",
                "texto_botao_secundario": "#212529",
                "bg_status": "#f8f9fa",
                "sucesso": "#198754",
                "alerta": "#ffc107",
                "erro": "#dc3545",
                "info": "#0dcaf0"
            },
            "escuro": {
                "bg_principal": "#212529",
                "bg_cartao": "#343a40",
                "texto_principal": "#f8f9fa",
                "texto_secundario": "#adb5bd",
                "cor_destaque": "#0d6efd",
                "cor_destaque_hover": "#0b5ed7",
                "cor_borda": "#495057",
                "bg_entrada": "#2b3035",
                "bg_saida": "#2b3035",
                "bg_botao_primario": "#0d6efd",
                "texto_botao_primario": "#ffffff",
                "bg_botao_secundario": "#495057",
                "texto_botao_secundario": "#f8f9fa",
                "bg_status": "#343a40",
                "sucesso": "#20c997",
                "alerta": "#ffc107",
                "erro": "#dc3545",
                "info": "#0dcaf0"
            }
        }
        
        # Definir tema inicial
        self.tema_atual = "claro"
        self.cores = self.temas[self.tema_atual]
        
        # Configurar estilo ttk
        self.estilo = ttk.Style()
        self.estilo.theme_use("clam")
        self.aplicar_tema()
        
    def aplicar_tema(self):
        """Aplicar o tema atual aos widgets"""
        self.cores = self.temas[self.tema_atual]
        
        # Configurar estilos ttk
        self.estilo.configure("TFrame", background=self.cores["bg_principal"])
        self.estilo.configure("Card.TFrame", background=self.cores["bg_cartao"])
        
        self.estilo.configure("TLabel", 
                             background=self.cores["bg_principal"],
                             foreground=self.cores["texto_principal"])
        self.estilo.configure("Card.TLabel", 
                             background=self.cores["bg_cartao"],
                             foreground=self.cores["texto_principal"])
        self.estilo.configure("Secondary.TLabel", 
                             background=self.cores["bg_principal"],
                             foreground=self.cores["texto_secundario"])
        
        self.estilo.configure("TButton", 
                             background=self.cores["bg_botao_secundario"],
                             foreground=self.cores["texto_botao_secundario"])
        self.estilo.configure("Primary.TButton", 
                             background=self.cores["bg_botao_primario"],
                             foreground=self.cores["texto_botao_primario"])
        
        self.estilo.configure("TCheckbutton", 
                             background=self.cores["bg_cartao"],
                             foreground=self.cores["texto_principal"])
        
        self.estilo.configure("TEntry", 
                             fieldbackground=self.cores["bg_entrada"],
                             foreground=self.cores["texto_principal"])
        
        self.estilo.configure("TCombobox", 
                             fieldbackground=self.cores["bg_entrada"],
                             foreground=self.cores["texto_principal"])
        
        # Atualizar cores da janela principal
        self.root.configure(background=self.cores["bg_principal"])
        
        # Atualizar widgets existentes se já foram criados
        if hasattr(self, 'frame_principal'):
            self.frame_principal.configure(background=self.cores["bg_principal"])
            
            # Atualizar área de saída
            if hasattr(self, 'area_saida'):
                self.area_saida.configure(
                    background=self.cores["bg_saida"],
                    foreground=self.cores["texto_principal"],
                    insertbackground=self.cores["texto_principal"]
                )
                
            # Atualizar barra de status
            if hasattr(self, 'barra_status'):
                self.barra_status.configure(background=self.cores["bg_status"])
                
    def centralizar_janela(self):
        """Centralizar a janela na tela"""
        self.root.update_idletasks()
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        self.root.geometry(f'{largura}x{altura}+{x}+{y}')
        
    def configurar_atalhos(self):
        """Configurar atalhos de teclado"""
        self.root.bind("<Control-o>", lambda e: self.selecionar_diretorio())
        self.root.bind("<Control-g>", lambda e: self.gerar_visualizacao())
        self.root.bind("<Control-s>", lambda e: self.salvar_arquivo())
        self.root.bind("<Control-c>", lambda e: self.copiar_para_clipboard())
        self.root.bind("<F5>", lambda e: self.gerar_visualizacao())
        self.root.bind("<F1>", lambda e: self.mostrar_ajuda())
        
    def criar_widgets(self):
        """Criar todos os widgets da interface"""
        # Frame principal
        self.frame_principal = ttk.Frame(self.root, style="TFrame", padding=20)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        self.criar_cabecalho()
        
        # Seção de seleção de diretório
        self.criar_secao_diretorio()
        
        # Seção de opções
        self.criar_secao_opcoes()
        
        # Seção de saída
        self.criar_secao_saida()
        
        # Barra de status
        self.criar_barra_status()
        
    def criar_cabecalho(self):
        """Criar a seção de cabeçalho"""
        frame_cabecalho = ttk.Frame(self.frame_principal, style="TFrame")
        frame_cabecalho.pack(fill=tk.X, pady=(0, 20))
        
        # Título e subtítulo
        titulo = ttk.Label(
            frame_cabecalho, 
            text="Visualizador de Estrutura de Diretórios",
            font=("Segoe UI", 18, "bold"),
            style="TLabel"
        )
        titulo.pack(anchor=tk.W)
        
        subtitulo = ttk.Label(
            frame_cabecalho, 
            text="Gere representações visuais da estrutura de seus diretórios em formato Markdown",
            font=("Segoe UI", 11),
            style="Secondary.TLabel"
        )
        subtitulo.pack(anchor=tk.W, pady=(5, 0))
        
        # Botão de tema no canto direito
        frame_tema = ttk.Frame(frame_cabecalho, style="TFrame")
        frame_tema.pack(anchor=tk.E, side=tk.RIGHT)
        
        self.botao_tema = ttk.Checkbutton(
            frame_tema,
            text="Tema Escuro",
            variable=self.tema_escuro,
            command=self.alternar_tema,
            style="TCheckbutton"
        )
        self.botao_tema.pack(side=tk.RIGHT)
        
    def criar_secao_diretorio(self):
        """Criar a seção de seleção de diretório"""
        cartao_diretorio = ttk.Frame(
            self.frame_principal, 
            style="Card.TFrame", 
            padding=20
        )
        cartao_diretorio.pack(fill=tk.X, pady=(0, 20))
        cartao_diretorio.configure(borderwidth=1, relief="solid")
        
        # Título da seção
        titulo_diretorio = ttk.Label(
            cartao_diretorio, 
            text="Selecionar Diretório",
            font=("Segoe UI", 14, "bold"),
            style="Card.TLabel"
        )
        titulo_diretorio.pack(anchor=tk.W, pady=(0, 15))
        
        # Frame para o botão e entrada
        frame_selecao = ttk.Frame(cartao_diretorio, style="Card.TFrame")
        frame_selecao.pack(fill=tk.X)
        
        # Botão grande e destacado
        botao_selecionar = ttk.Button(
            frame_selecao,
            text="Escolher Pasta",
            command=self.selecionar_diretorio,
            style="Primary.TButton",
            width=20
        )
        botao_selecionar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Campo de entrada para o caminho
        self.entrada_diretorio = ttk.Entry(
            frame_selecao,
            font=("Segoe UI", 10),
            width=60
        )
        self.entrada_diretorio.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Histórico de diretórios
        frame_historico = ttk.Frame(cartao_diretorio, style="Card.TFrame")
        frame_historico.pack(fill=tk.X, pady=(10, 0))
        
        label_historico = ttk.Label(
            frame_historico,
            text="Histórico:",
            style="Card.TLabel"
        )
        label_historico.pack(side=tk.LEFT, padx=(0, 10))
        
        self.combo_historico = ttk.Combobox(
            frame_historico,
            font=("Segoe UI", 9),
            state="readonly",
            width=50
        )
        self.combo_historico.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combo_historico.bind("<<ComboboxSelected>>", self.selecionar_do_historico)
        
    def criar_secao_opcoes(self):
        """Criar a seção de opções"""
        cartao_opcoes = ttk.Frame(
            self.frame_principal, 
            style="Card.TFrame", 
            padding=20
        )
        cartao_opcoes.pack(fill=tk.X, pady=(0, 20))
        cartao_opcoes.configure(borderwidth=1, relief="solid")
        
        # Título da seção
        titulo_opcoes = ttk.Label(
            cartao_opcoes, 
            text="Opções de Visualização",
            font=("Segoe UI", 14, "bold"),
            style="Card.TLabel"
        )
        titulo_opcoes.pack(anchor=tk.W, pady=(0, 15))
        
        # Criar notebook para organizar as opções em abas
        notebook = ttk.Notebook(cartao_opcoes)
        notebook.pack(fill=tk.X, pady=(0, 15))
        
        # Aba de opções básicas
        aba_basicas = ttk.Frame(notebook, style="Card.TFrame", padding=10)
        notebook.add(aba_basicas, text="Opções Básicas")
        
        # Aba de filtros
        aba_filtros = ttk.Frame(notebook, style="Card.TFrame", padding=10)
        notebook.add(aba_filtros, text="Filtros")
        
        # Aba de formatação
        aba_formatacao = ttk.Frame(notebook, style="Card.TFrame", padding=10)
        notebook.add(aba_formatacao, text="Formatação")
        
        # Configurar opções básicas
        self.configurar_opcoes_basicas(aba_basicas)
        
        # Configurar filtros
        self.configurar_opcoes_filtros(aba_filtros)
        
        # Configurar formatação
        self.configurar_opcoes_formatacao(aba_formatacao)
        
        # Botão de gerar visualização
        botao_gerar = ttk.Button(
            cartao_opcoes,
            text="Gerar Visualização",
            command=self.gerar_visualizacao,
            style="Primary.TButton"
        )
        botao_gerar.pack(pady=(0, 5))
        
        # Dica sobre atalhos
        dica_atalho = ttk.Label(
            cartao_opcoes,
            text="Dica: Pressione F5 para gerar a visualização rapidamente",
            font=("Segoe UI", 9, "italic"),
            style="Card.TLabel",
            foreground=self.cores["texto_secundario"]
        )
        dica_atalho.pack()
        
    def configurar_opcoes_basicas(self, frame):
        """Configurar as opções básicas"""
        # Grid para organizar as opções
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        # Opção de profundidade máxima
        frame_profundidade = ttk.Frame(frame, style="Card.TFrame")
        frame_profundidade.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        label_profundidade = ttk.Label(
            frame_profundidade,
            text="Profundidade Máxima:",
            style="Card.TLabel"
        )
        label_profundidade.pack(side=tk.LEFT, padx=(0, 5))
        
        entrada_profundidade = ttk.Entry(
            frame_profundidade,
            width=5,
            textvariable=self.profundidade_maxima,
            font=("Segoe UI", 10)
        )
        entrada_profundidade.pack(side=tk.LEFT)
        
        dica_profundidade = ttk.Label(
            frame_profundidade,
            text="(0 = ilimitado)",
            style="Card.TLabel",
            foreground=self.cores["texto_secundario"]
        )
        dica_profundidade.pack(side=tk.LEFT, padx=(5, 0))
        
        # Opção de mostrar arquivos ocultos
        check_ocultos = ttk.Checkbutton(
            frame,
            text="Incluir Arquivos Ocultos",
            variable=self.incluir_ocultos,
            style="TCheckbutton"
        )
        check_ocultos.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Opção de mostrar tamanho dos arquivos
        check_tamanho = ttk.Checkbutton(
            frame,
            text="Mostrar Tamanho dos Arquivos",
            variable=self.mostrar_tamanho,
            style="TCheckbutton"
        )
        check_tamanho.grid(row=1, column=0, sticky=tk.W, pady=5)
        
    def configurar_opcoes_filtros(self, frame):
        """Configurar as opções de filtros"""
        # Pastas a ignorar
        frame_ignorar = ttk.Frame(frame, style="Card.TFrame")
        frame_ignorar.pack(fill=tk.X, pady=5)
        
        label_ignorar = ttk.Label(
            frame_ignorar,
            text="Pastas a Ignorar (separadas por vírgula):",
            style="Card.TLabel"
        )
        label_ignorar.pack(anchor=tk.W, pady=(0, 5))
        
        entrada_ignorar = ttk.Entry(
            frame_ignorar,
            textvariable=self.ignorar_padrao,
            font=("Segoe UI", 10)
        )
        entrada_ignorar.pack(fill=tk.X)
        
        # Filtro de extensões
        frame_extensoes = ttk.Frame(frame, style="Card.TFrame")
        frame_extensoes.pack(fill=tk.X, pady=(10, 5))
        
        check_extensoes = ttk.Checkbutton(
            frame_extensoes,
            text="Filtrar por Extensões",
            variable=self.filtrar_extensoes,
            style="TCheckbutton"
        )
        check_extensoes.pack(anchor=tk.W)
        
        label_extensoes = ttk.Label(
            frame_extensoes,
            text="Extensões a Incluir (ex: py,txt,md):",
            style="Card.TLabel"
        )
        label_extensoes.pack(anchor=tk.W, pady=(5, 5))
        
        entrada_extensoes = ttk.Entry(
            frame_extensoes,
            textvariable=self.extensoes_filtro,
            font=("Segoe UI", 10)
        )
        entrada_extensoes.pack(fill=tk.X)
        
    def configurar_opcoes_formatacao(self, frame):
        """Configurar as opções de formatação"""
        # Formato de saída
        frame_formato = ttk.Frame(frame, style="Card.TFrame")
        frame_formato.pack(fill=tk.X, pady=5)
        
        label_formato = ttk.Label(
            frame_formato,
            text="Formato de Saída:",
            style="Card.TLabel"
        )
        label_formato.pack(anchor=tk.W, pady=(0, 5))
        
        # Opções de formato
        frame_opcoes_formato = ttk.Frame(frame_formato, style="Card.TFrame")
        frame_opcoes_formato.pack(fill=tk.X)
        
        radio_markdown = ttk.Radiobutton(
            frame_opcoes_formato,
            text="Markdown",
            variable=self.formato_saida,
            value="markdown",
            style="TCheckbutton"
        )
        radio_markdown.pack(side=tk.LEFT, padx=(0, 10))
        
        radio_html = ttk.Radiobutton(
            frame_opcoes_formato,
            text="HTML",
            variable=self.formato_saida,
            value="html",
            style="TCheckbutton"
        )
        radio_html.pack(side=tk.LEFT, padx=(0, 10))
        
        radio_json = ttk.Radiobutton(
            frame_opcoes_formato,
            text="JSON",
            variable=self.formato_saida,
            value="json",
            style="TCheckbutton"
        )
        radio_json.pack(side=tk.LEFT)
        
    def criar_secao_saida(self):
        """Criar a seção de saída"""
        cartao_saida = ttk.Frame(
            self.frame_principal, 
            style="Card.TFrame", 
            padding=20
        )
        cartao_saida.pack(fill=tk.BOTH, expand=True)
        cartao_saida.configure(borderwidth=1, relief="solid")
        
        # Cabeçalho da seção
        frame_cabecalho_saida = ttk.Frame(cartao_saida, style="Card.TFrame")
        frame_cabecalho_saida.pack(fill=tk.X, pady=(0, 10))
        
        titulo_saida = ttk.Label(
            frame_cabecalho_saida,
            text="Visualização",
            font=("Segoe UI", 14, "bold"),
            style="Card.TLabel"
        )
        titulo_saida.pack(side=tk.LEFT)
        
        # Botões de ação
        frame_botoes_saida = ttk.Frame(frame_cabecalho_saida, style="Card.TFrame")
        frame_botoes_saida.pack(side=tk.RIGHT)
        
        botao_salvar = ttk.Button(
            frame_botoes_saida,
            text="Salvar",
            command=self.salvar_arquivo,
            style="TButton"
        )
        botao_salvar.pack(side=tk.LEFT, padx=(0, 5))
        
        botao_copiar = ttk.Button(
            frame_botoes_saida,
            text="Copiar",
            command=self.copiar_para_clipboard,
            style="TButton"
        )
        botao_copiar.pack(side=tk.LEFT, padx=(0, 5))
        
        botao_visualizar = ttk.Button(
            frame_botoes_saida,
            text="Visualizar no Navegador",
            command=self.visualizar_no_navegador,
            style="TButton"
        )
        botao_visualizar.pack(side=tk.LEFT)
        
        # Área de texto para a saída
        fonte_saida = font.Font(family="Consolas", size=10)
        
        self.area_saida = scrolledtext.ScrolledText(
            cartao_saida,
            wrap=tk.NONE,
            font=fonte_saida,
            background=self.cores["bg_saida"],
            foreground=self.cores["texto_principal"],
            borderwidth=1,
            relief="solid",
            padx=10,
            pady=10
        )
        self.area_saida.pack(fill=tk.BOTH, expand=True)
        
        # Barra de rolagem horizontal
        barra_rolagem_h = ttk.Scrollbar(
            cartao_saida,
            orient=tk.HORIZONTAL,
            command=self.area_saida.xview
        )
        self.area_saida.configure(xscrollcommand=barra_rolagem_h.set)
        barra_rolagem_h.pack(fill=tk.X)
        
    def criar_barra_status(self):
        """Criar a barra de status"""
        self.var_status = tk.StringVar()
        
        self.barra_status = ttk.Label(
            self.root,
            textvariable=self.var_status,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(10, 5)
        )
        self.barra_status.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Definir status inicial
        self.var_status.set("Pronto. Clique em 'Escolher Pasta' para começar.")
        
    def alternar_tema(self):
        """Alternar entre tema claro e escuro"""
        self.tema_atual = "escuro" if self.tema_escuro.get() else "claro"
        self.aplicar_tema()
        self.salvar_configuracoes()
        
    def selecionar_diretorio(self):
        """Abrir diálogo para selecionar diretório"""
        diretorio = filedialog.askdirectory(title="Selecionar Diretório")
        if diretorio:
            self.entrada_diretorio.delete(0, tk.END)
            self.entrada_diretorio.insert(0, diretorio)
            self.diretorio_atual = diretorio
            self.var_status.set(f"Diretório selecionado: {diretorio}")
            
            # Adicionar ao histórico
            self.adicionar_ao_historico(diretorio)
            
            # Gerar visualização automaticamente
            self.gerar_visualizacao()
            
    def selecionar_do_historico(self, event):
        """Selecionar diretório do histórico"""
        selecionado = self.combo_historico.get()
        if selecionado:
            self.entrada_diretorio.delete(0, tk.END)
            self.entrada_diretorio.insert(0, selecionado)
            self.diretorio_atual = selecionado
            self.var_status.set(f"Diretório selecionado: {selecionado}")
            
            # Gerar visualização automaticamente
            self.gerar_visualizacao()
            
    def adicionar_ao_historico(self, diretorio):
        """Adicionar diretório ao histórico"""
        # Remover se já existir
        if diretorio in self.historico_diretorios:
            self.historico_diretorios.remove(diretorio)
            
        # Adicionar ao início
        self.historico_diretorios.insert(0, diretorio)
        
        # Limitar tamanho
        if len(self.historico_diretorios) > self.max_historico:
            self.historico_diretorios = self.historico_diretorios[:self.max_historico]
            
        # Atualizar combobox
        self.combo_historico['values'] = self.historico_diretorios
        
        # Salvar configurações
        self.salvar_configuracoes()
        
    def gerar_visualizacao(self):
        """Gerar a visualização da estrutura de diretórios"""
        diretorio = self.entrada_diretorio.get().strip()
        if not diretorio:
            messagebox.showerror("Erro", "Por favor, selecione um diretório")
            return
            
        if not os.path.isdir(diretorio):
            messagebox.showerror("Erro", "Caminho de diretório inválido")
            return
            
        try:
            profundidade_maxima = int(self.profundidade_maxima.get())
            if profundidade_maxima < 0:
                raise ValueError("A profundidade máxima deve ser um número não negativo")
        except ValueError:
            messagebox.showerror("Erro", "A profundidade máxima deve ser um número não negativo")
            return
            
        # Evitar múltiplas gerações simultâneas
        if self.gerando_visualizacao:
            return
            
        self.gerando_visualizacao = True
        self.var_status.set("Gerando visualização...")
        self.root.update_idletasks()
        
        # Obter opções
        incluir_ocultos = self.incluir_ocultos.get()
        mostrar_tamanho = self.mostrar_tamanho.get()
        formato = self.formato_saida.get()
        
        # Obter lista de pastas a ignorar
        pastas_ignorar = [p.strip() for p in self.ignorar_padrao.get().split(',') if p.strip()]
        
        # Obter filtro de extensões
        filtrar_por_extensao = self.filtrar_extensoes.get()
        extensoes = [ext.strip().lower() for ext in self.extensoes_filtro.get().split(',') if ext.strip()]
        
        # Iniciar thread para não bloquear a interface
        threading.Thread(
            target=self._gerar_visualizacao_thread,
            args=(diretorio, incluir_ocultos, mostrar_tamanho, profundidade_maxima, 
                  pastas_ignorar, filtrar_por_extensao, extensoes, formato),
            daemon=True
        ).start()
        
    def _gerar_visualizacao_thread(self, diretorio, incluir_ocultos, mostrar_tamanho, 
                                  profundidade_maxima, pastas_ignorar, filtrar_por_extensao, 
                                  extensoes, formato):
        """Thread para gerar a visualização sem bloquear a interface"""
        try:
            # Gerar a visualização de acordo com o formato
            if formato == "markdown":
                resultado = self.gerar_arvore_diretorio_markdown(
                    diretorio, incluir_ocultos, mostrar_tamanho, profundidade_maxima,
                    pastas_ignorar, filtrar_por_extensao, extensoes
                )
            elif formato == "html":
                resultado = self.gerar_arvore_diretorio_html(
                    diretorio, incluir_ocultos, mostrar_tamanho, profundidade_maxima,
                    pastas_ignorar, filtrar_por_extensao, extensoes
                )
            elif formato == "json":
                resultado = self.gerar_arvore_diretorio_json(
                    diretorio, incluir_ocultos, mostrar_tamanho, profundidade_maxima,
                    pastas_ignorar, filtrar_por_extensao, extensoes
                )
            else:
                resultado = "Formato não suportado"
                
            # Atualizar a interface na thread principal
            self.root.after(0, self.atualizar_saida, resultado)
            
        except Exception as e:
            self.root.after(0, self.mostrar_erro, str(e))
        finally:
            self.root.after(0, self.finalizar_geracao)
            
    def atualizar_saida(self, resultado):
        """Atualizar a área de saída com o resultado"""
        self.area_saida.delete(1.0, tk.END)
        self.area_saida.insert(tk.END, resultado)
        self.ultima_saida = resultado
        self.var_status.set(f"Visualização gerada para: {self.diretorio_atual}")
        
    def mostrar_erro(self, mensagem):
        """Mostrar mensagem de erro"""
        messagebox.showerror("Erro", f"Ocorreu um erro: {mensagem}")
        self.var_status.set("Erro ao gerar visualização")
        
    def finalizar_geracao(self):
        """Finalizar o processo de geração"""
        self.gerando_visualizacao = False
        
    def gerar_arvore_diretorio_markdown(self, diretorio, incluir_ocultos, mostrar_tamanho, 
                                       profundidade_maxima, pastas_ignorar, filtrar_por_extensao, 
                                       extensoes):
        """Gerar representação em Markdown da estrutura de diretórios"""
        caminho_diretorio = pathlib.Path(diretorio)
        
        # Obter o nome do diretório para o cabeçalho
        nome_dir = caminho_diretorio.name or caminho_diretorio.anchor
        
        # Iniciar com o cabeçalho
        resultado = [f"# 📁 Estrutura do Diretório: {nome_dir}\n"]
        resultado.append(f"*Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*\n")
        
        # Adicionar estatísticas
        estatisticas = self.calcular_estatisticas(
            caminho_diretorio, incluir_ocultos, pastas_ignorar, 
            filtrar_por_extensao, extensoes
        )
        resultado.append("## Estatísticas\n")
        resultado.append(f"- **Total de Diretórios:** {estatisticas['total_diretorios']}")
        resultado.append(f"- **Total de Arquivos:** {estatisticas['total_arquivos']}")
        resultado.append(f"- **Tamanho Total:** {self.formatar_tamanho(estatisticas['tamanho_total'])}\n")
        
        # Adicionar o diretório raiz à árvore
        resultado.append(f"## Estrutura\n")
        resultado.append(f"📁 {nome_dir}/")
        
        # Gerar a árvore recursivamente
        self._gerar_arvore_markdown(
            caminho_diretorio, "", resultado, incluir_ocultos, mostrar_tamanho,
            profundidade_maxima, pastas_ignorar, filtrar_por_extensao, extensoes, 0
        )
        
        return "\n".join(resultado)
        
    def _gerar_arvore_markdown(self, caminho, prefixo, resultado, incluir_ocultos, 
                              mostrar_tamanho, profundidade_maxima, pastas_ignorar, 
                              filtrar_por_extensao, extensoes, profundidade_atual):
        """Gerar recursivamente a estrutura da árvore em formato Markdown"""
        if profundidade_maxima > 0 and profundidade_atual >= profundidade_maxima:
            return
            
        # Obter todos os itens no diretório
        try:
            itens = list(caminho.iterdir())
        except PermissionError:
            resultado.append(f"{prefixo}├── ⚠️ Permissão negada")
            return
        except Exception as e:
            resultado.append(f"{prefixo}├── ⚠️ Erro: {str(e)}")
            return
            
        # Filtrar itens
        itens_filtrados = []
        for item in itens:
            # Verificar se é um diretório a ser ignorado
            if item.is_dir() and item.name in pastas_ignorar:
                continue
                
            # Verificar se é um arquivo oculto
            if not incluir_ocultos and item.name.startswith('.'):
                continue
                
            # Verificar filtro de extensão para arquivos
            if filtrar_por_extensao and not item.is_dir():
                if not extensoes:  # Se a lista estiver vazia, não mostrar nenhum arquivo
                    continue
                    
                ext = item.suffix.lower().lstrip('.')
                if ext not in extensoes:
                    continue
                    
            itens_filtrados.append(item)
            
        # Ordenar itens: diretórios primeiro, depois arquivos, ambos em ordem alfabética
        itens_filtrados.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
        
        # Processar cada item
        for i, item in enumerate(itens_filtrados):
            eh_ultimo = i == len(itens_filtrados) - 1
            
            # Escolher o prefixo apropriado para o item atual
            prefixo_item = "└── " if eh_ultimo else "├── "
            
            # Escolher o ícone apropriado
            icone = "📁" if item.is_dir() else self.obter_icone_arquivo(item)
            
            # Adicionar informação de tamanho se necessário
            info_tamanho = ""
            if mostrar_tamanho and not item.is_dir():
                try:
                    tamanho = item.stat().st_size
                    info_tamanho = f" ({self.formatar_tamanho(tamanho)})"
                except:
                    info_tamanho = " (tamanho desconhecido)"
                    
            # Adicionar o item ao resultado
            resultado.append(f"{prefixo}{prefixo_item}{icone} {item.name}{info_tamanho}")
            
            # Se for um diretório, processar seu conteúdo
            if item.is_dir():
                # Escolher o prefixo apropriado para o próximo nível
                proximo_prefixo = prefixo + ("    " if eh_ultimo else "│   ")
                self._gerar_arvore_markdown(
                    item, proximo_prefixo, resultado, incluir_ocultos, mostrar_tamanho,
                    profundidade_maxima, pastas_ignorar, filtrar_por_extensao, extensoes,
                    profundidade_atual + 1
                )
                
    def gerar_arvore_diretorio_html(self, diretorio, incluir_ocultos, mostrar_tamanho, 
                                   profundidade_maxima, pastas_ignorar, filtrar_por_extensao, 
                                   extensoes):
        """Gerar representação em HTML da estrutura de diretórios"""
        caminho_diretorio = pathlib.Path(diretorio)
        nome_dir = caminho_diretorio.name or caminho_diretorio.anchor
        
        # Calcular estatísticas
        estatisticas = self.calcular_estatisticas(
            caminho_diretorio, incluir_ocultos, pastas_ignorar, 
            filtrar_por_extensao, extensoes
        )
        
        # Iniciar HTML
        html = [
            "<!DOCTYPE html>",
            "<html lang='pt-BR'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"    <title>Estrutura do Diretório: {nome_dir}</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }",
            "        h1 { color: #2c3e50; }",
            "        .timestamp { color: #7f8c8d; font-style: italic; margin-bottom: 20px; }",
            "        .stats { background-color: #f8f9fa; border-radius: 5px; padding: 15px; margin-bottom: 20px; }",
            "        .tree-container { font-family: 'Consolas', monospace; }",
            "        .tree-item { white-space: nowrap; }",
            "        .folder { color: #3498db; }",
            "        .file { color: #2c3e50; }",
            "        .size { color: #7f8c8d; font-size: 0.9em; }",
            "        .error { color: #e74c3c; }",
            "    </style>",
            "</head>",
            "<body>",
            f"    <h1>📁 Estrutura do Diretório: {nome_dir}</h1>",
            f"    <div class='timestamp'>Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>",
            "    <div class='stats'>",
            "        <h2>Estatísticas</h2>",
            f"        <p><strong>Total de Diretórios:</strong> {estatisticas['total_diretorios']}</p>",
            f"        <p><strong>Total de Arquivos:</strong> {estatisticas['total_arquivos']}</p>",
            f"        <p><strong>Tamanho Total:</strong> {self.formatar_tamanho(estatisticas['tamanho_total'])}</p>",
            "    </div>",
            "    <h2>Estrutura</h2>",
            "    <div class='tree-container'>"
        ]
        
        # Adicionar o diretório raiz
        html.append(f"        <div class='tree-item'><span class='folder'>📁 {nome_dir}/</span></div>")
        
        # Lista para armazenar os itens da árvore
        itens_arvore = []
        
        # Gerar a árvore recursivamente
        self._gerar_arvore_html(
            caminho_diretorio, "", itens_arvore, incluir_ocultos, mostrar_tamanho,
            profundidade_maxima, pastas_ignorar, filtrar_por_extensao, extensoes, 0
        )
        
        # Adicionar itens da árvore ao HTML
        html.extend(itens_arvore)
        
        # Finalizar HTML
        html.extend([
            "    </div>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html)
        
    def _gerar_arvore_html(self, caminho, prefixo, resultado, incluir_ocultos, 
                          mostrar_tamanho, profundidade_maxima, pastas_ignorar, 
                          filtrar_por_extensao, extensoes, profundidade_atual):
        """Gerar recursivamente a estrutura da árvore em formato HTML"""
        if profundidade_maxima > 0 and profundidade_atual >= profundidade_maxima:
            return
            
        # Obter todos os itens no diretório
        try:
            itens = list(caminho.iterdir())
        except PermissionError:
            resultado.append(f"        <div class='tree-item'>{prefixo}├── <span class='error'>⚠️ Permissão negada</span></div>")
            return
        except Exception as e:
            resultado.append(f"        <div class='tree-item'>{prefixo}├── <span class='error'>⚠️ Erro: {str(e)}</span></div>")
            return
            
        # Filtrar itens
        itens_filtrados = []
        for item in itens:
            # Verificar se é um diretório a ser ignorado
            if item.is_dir() and item.name in pastas_ignorar:
                continue
                
            # Verificar se é um arquivo oculto
            if not incluir_ocultos and item.name.startswith('.'):
                continue
                
            # Verificar filtro de extensão para arquivos
            if filtrar_por_extensao and not item.is_dir():
                if not extensoes:  # Se a lista estiver vazia, não mostrar nenhum arquivo
                    continue
                    
                ext = item.suffix.lower().lstrip('.')
                if ext not in extensoes:
                    continue
                    
            itens_filtrados.append(item)
            
        # Ordenar itens: diretórios primeiro, depois arquivos, ambos em ordem alfabética
        itens_filtrados.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
        
        # Processar cada item
        for i, item in enumerate(itens_filtrados):
            eh_ultimo = i == len(itens_filtrados) - 1
            
            # Escolher o prefixo apropriado para o item atual
            prefixo_item = "└── " if eh_ultimo else "├── "
            
            # Escolher o ícone apropriado
            icone = "📁" if item.is_dir() else self.obter_icone_arquivo(item)
            
            # Adicionar informação de tamanho se necessário
            info_tamanho = ""
            if mostrar_tamanho and not item.is_dir():
                try:
                    tamanho = item.stat().st_size
                    info_tamanho = f" <span class='size'>({self.formatar_tamanho(tamanho)})</span>"
                except:
                    info_tamanho = " <span class='size'>(tamanho desconhecido)</span>"
                    
            # Adicionar o item ao resultado
            classe = "folder" if item.is_dir() else "file"
            resultado.append(f"        <div class='tree-item'>{prefixo}{prefixo_item}<span class='{classe}'>{icone} {item.name}</span>{info_tamanho}</div>")
            
            # Se for um diretório, processar seu conteúdo
            if item.is_dir():
                # Escolher o prefixo apropriado para o próximo nível
                proximo_prefixo = prefixo + ("    " if eh_ultimo else "│   ")
                self._gerar_arvore_html(
                    item, proximo_prefixo, resultado, incluir_ocultos, mostrar_tamanho,
                    profundidade_maxima, pastas_ignorar, filtrar_por_extensao, extensoes,
                    profundidade_atual + 1
                )
                
    def gerar_arvore_diretorio_json(self, diretorio, incluir_ocultos, mostrar_tamanho, 
                                   profundidade_maxima, pastas_ignorar, filtrar_por_extensao, 
                                   extensoes):
        """Gerar representação em JSON da estrutura de diretórios"""
        caminho_diretorio = pathlib.Path(diretorio)
        nome_dir = caminho_diretorio.name or caminho_diretorio.anchor
        
        # Calcular estatísticas
        estatisticas = self.calcular_estatisticas(
            caminho_diretorio, incluir_ocultos, pastas_ignorar, 
            filtrar_por_extensao, extensoes
        )
        
        # Criar estrutura JSON
        estrutura = {
            "nome": nome_dir,
            "tipo": "diretorio",
            "caminho": str(caminho_diretorio),
            "timestamp": datetime.now().isoformat(),
            "estatisticas": {
                "total_diretorios": estatisticas["total_diretorios"],
                "total_arquivos": estatisticas["total_arquivos"],
                "tamanho_total": estatisticas["tamanho_total"],
                "tamanho_formatado": self.formatar_tamanho(estatisticas["tamanho_total"])
            },
            "conteudo": []
        }
        
        # Gerar a árvore recursivamente
        self._gerar_arvore_json(
            caminho_diretorio, estrutura["conteudo"], incluir_ocultos, mostrar_tamanho,
            profundidade_maxima, pastas_ignorar, filtrar_por_extensao, extensoes, 0
        )
        
        # Converter para string JSON formatada
        return json.dumps(estrutura, indent=2, ensure_ascii=False)
        
    def _gerar_arvore_json(self, caminho, resultado, incluir_ocultos, mostrar_tamanho, 
                          profundidade_maxima, pastas_ignorar, filtrar_por_extensao, 
                          extensoes, profundidade_atual):
        """Gerar recursivamente a estrutura da árvore em formato JSON"""
        if profundidade_maxima > 0 and profundidade_atual >= profundidade_maxima:
            return
            
        # Obter todos os itens no diretório
        try:
            itens = list(caminho.iterdir())
        except PermissionError:
            resultado.append({
                "nome": "Permissão negada",
                "tipo": "erro",
                "mensagem": "Acesso negado ao diretório"
            })
            return
        except Exception as e:
            resultado.append({
                "nome": "Erro",
                "tipo": "erro",
                "mensagem": str(e)
            })
            return
            
        # Filtrar itens
        itens_filtrados = []
        for item in itens:
            # Verificar se é um diretório a ser ignorado
            if item.is_dir() and item.name in pastas_ignorar:
                continue
                
            # Verificar se é um arquivo oculto
            if not incluir_ocultos and item.name.startswith('.'):
                continue
                
            # Verificar filtro de extensão para arquivos
            if filtrar_por_extensao and not item.is_dir():
                if not extensoes:  # Se a lista estiver vazia, não mostrar nenhum arquivo
                    continue
                    
                ext = item.suffix.lower().lstrip('.')
                if ext not in extensoes:
                    continue
                    
            itens_filtrados.append(item)
            
        # Ordenar itens: diretórios primeiro, depois arquivos, ambos em ordem alfabética
        itens_filtrados.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
        
        # Processar cada item
        for item in itens_filtrados:
            if item.is_dir():
                # Criar objeto para o diretório
                dir_obj = {
                    "nome": item.name,
                    "tipo": "diretorio",
                    "caminho": str(item),
                    "conteudo": []
                }
                
                # Adicionar ao resultado
                resultado.append(dir_obj)
                
                # Processar conteúdo do diretório
                self._gerar_arvore_json(
                    item, dir_obj["conteudo"], incluir_ocultos, mostrar_tamanho,
                    profundidade_maxima, pastas_ignorar, filtrar_por_extensao, extensoes,
                    profundidade_atual + 1
                )
            else:
                # Criar objeto para o arquivo
                arquivo_obj = {
                    "nome": item.name,
                    "tipo": "arquivo",
                    "caminho": str(item),
                    "extensao": item.suffix.lower().lstrip('.') if item.suffix else ""
                }
                
                # Adicionar informação de tamanho se necessário
                if mostrar_tamanho:
                    try:
                        tamanho = item.stat().st_size
                        arquivo_obj["tamanho"] = tamanho
                        arquivo_obj["tamanho_formatado"] = self.formatar_tamanho(tamanho)
                    except:
                        arquivo_obj["tamanho"] = -1
                        arquivo_obj["tamanho_formatado"] = "desconhecido"
                        
                # Adicionar ao resultado
                resultado.append(arquivo_obj)
                
    def calcular_estatisticas(self, caminho, incluir_ocultos, pastas_ignorar, 
                             filtrar_por_extensao, extensoes):
        """Calcular estatísticas do diretório"""
        total_diretorios = 0
        total_arquivos = 0
        tamanho_total = 0
        
        for raiz, diretorios, arquivos in os.walk(caminho):
            # Filtrar diretórios a ignorar
            diretorios_filtrados = []
            for d in diretorios:
                if d in pastas_ignorar:
                    continue
                if not incluir_ocultos and d.startswith('.'):
                    continue
                diretorios_filtrados.append(d)
                
            # Atualizar a lista de diretórios para não percorrer os ignorados
            diretorios[:] = diretorios_filtrados
            total_diretorios += len(diretorios_filtrados)
            
            # Processar arquivos
            for arquivo in arquivos:
                # Verificar se é um arquivo oculto
                if not incluir_ocultos and arquivo.startswith('.'):
                    continue
                    
                # Verificar filtro de extensão
                if filtrar_por_extensao:
                    if not extensoes:  # Se a lista estiver vazia, não contar nenhum arquivo
                        continue
                        
                    ext = os.path.splitext(arquivo)[1].lower().lstrip('.')
                    if ext not in extensoes:
                        continue
                        
                # Contar arquivo
                total_arquivos += 1
                
                # Calcular tamanho
                try:
                    caminho_arquivo = os.path.join(raiz, arquivo)
                    tamanho_total += os.path.getsize(caminho_arquivo)
                except:
                    pass
                    
        return {
            "total_diretorios": total_diretorios,
            "total_arquivos": total_arquivos,
            "tamanho_total": tamanho_total
        }
        
    def obter_icone_arquivo(self, caminho):
        """Obter ícone apropriado para o tipo de arquivo"""
        extensao = caminho.suffix.lower()
        
        # Mapeamento de extensões para ícones
        icones = {
            # Código
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📜',
            '.html': '🌐',
            '.css': '🎨',
            '.java': '☕',
            '.c': '🔧',
            '.cpp': '🔧',
            '.h': '📋',
            '.php': '🐘',
            '.rb': '💎',
            '.go': '🔹',
            '.rs': '🦀',
            '.swift': '🔶',
            '.kt': '🔷',
            
            # Documentos
            '.txt': '📄',
            '.md': '📝',
            '.pdf': '📕',
            '.doc': '📘',
            '.docx': '📘',
            '.xls': '📊',
            '.xlsx': '📊',
            '.ppt': '📊',
            '.pptx': '📊',
            
            # Imagens
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.svg': '🖼️',
            '.bmp': '🖼️',
            '.tiff': '🖼️',
            
            # Áudio/Vídeo
            '.mp3': '🎵',
            '.wav': '🎵',
            '.ogg': '🎵',
            '.mp4': '🎬',
            '.avi': '🎬',
            '.mov': '🎬',
            '.mkv': '🎬',
            
            # Compactados
            '.zip': '📦',
            '.rar': '📦',
            '.tar': '📦',
            '.gz': '📦',
            '.7z': '📦',
            
            # Configuração
            '.json': '⚙️',
            '.xml': '⚙️',
            '.yml': '⚙️',
            '.yaml': '⚙️',
            '.ini': '⚙️',
            '.conf': '⚙️',
            '.env': '⚙️',
            
            # Executáveis
            '.exe': '⚡',
            '.bat': '⚡',
            '.sh': '⚡',
            
            # Outros
            '.db': '🗃️',
            '.sql': '🗃️',
            '.log': '📋',
            '.gitignore': '🔍',
            '.dockerfile': '🐳',
        }
        
        return icones.get(extensao, '📄')  # Ícone padrão se não encontrar
        
    def formatar_tamanho(self, tamanho_bytes):
        """Formatar tamanho em bytes para uma representação legível"""
        if tamanho_bytes < 0:
            return "desconhecido"
            
        # Definir unidades
        unidades = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        
        # Converter para a unidade apropriada
        indice_unidade = 0
        tamanho = float(tamanho_bytes)
        
        while tamanho >= 1024 and indice_unidade < len(unidades) - 1:
            tamanho /= 1024
            indice_unidade += 1
            
        # Formatar com 2 casas decimais se não for bytes
        if indice_unidade == 0:
            return f"{int(tamanho)} {unidades[indice_unidade]}"
        else:
            return f"{tamanho:.2f} {unidades[indice_unidade]}"
            
    def salvar_arquivo(self):
        """Salvar a visualização em um arquivo"""
        if not self.ultima_saida:
            messagebox.showerror("Erro", "Não há conteúdo para salvar")
            return
            
        # Determinar a extensão padrão com base no formato
        formato = self.formato_saida.get()
        extensoes = {
            "markdown": ".md",
            "html": ".html",
            "json": ".json"
        }
        
        extensao_padrao = extensoes.get(formato, ".txt")
        
        # Abrir diálogo para salvar
        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=extensao_padrao,
            filetypes=[
                ("Markdown", "*.md"),
                ("HTML", "*.html"),
                ("JSON", "*.json"),
                ("Texto", "*.txt"),
                ("Todos os arquivos", "*.*")
            ],
            title="Salvar Visualização"
        )
        
        if caminho_arquivo:
            try:
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    f.write(self.ultima_saida)
                self.var_status.set(f"Arquivo salvo em: {caminho_arquivo}")
                messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso em:\n{caminho_arquivo}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar arquivo: {str(e)}")
                
    def copiar_para_clipboard(self):
        """Copiar a visualização para a área de transferência"""
        if not self.ultima_saida:
            messagebox.showerror("Erro", "Não há conteúdo para copiar")
            return
            
        self.root.clipboard_clear()
        self.root.clipboard_append(self.ultima_saida)
        self.var_status.set("Conteúdo copiado para a área de transferência")
        messagebox.showinfo("Sucesso", "Conteúdo copiado para a área de transferência")
        
    def visualizar_no_navegador(self):
        """Visualizar a saída no navegador"""
        if not self.ultima_saida:
            messagebox.showerror("Erro", "Não há conteúdo para visualizar")
            return
            
        formato = self.formato_saida.get()
        
        # Criar arquivo temporário
        try:
            import tempfile
            
            # Determinar extensão
            extensoes = {
                "markdown": ".md",
                "html": ".html",
                "json": ".json"
            }
            
            extensao = extensoes.get(formato, ".txt")
            
            # Criar arquivo temporário com a extensão correta
            with tempfile.NamedTemporaryFile(suffix=extensao, delete=False, mode='w', encoding='utf-8') as temp:
                temp.write(self.ultima_saida)
                caminho_temp = temp.name
                
            # Abrir no navegador
            webbrowser.open(f"file://{caminho_temp}")
            self.var_status.set("Visualização aberta no navegador")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir no navegador: {str(e)}")
            
    def mostrar_ajuda(self):
        """Mostrar janela de ajuda"""
        janela_ajuda = tk.Toplevel(self.root)
        janela_ajuda.title("Ajuda - Visualizador de Estrutura de Diretórios")
        janela_ajuda.geometry("600x500")
        janela_ajuda.configure(background=self.cores["bg_principal"])
        
        # Centralizar a janela
        janela_ajuda.update_idletasks()
        largura = janela_ajuda.winfo_width()
        altura = janela_ajuda.winfo_height()
        x = (janela_ajuda.winfo_screenwidth() // 2) - (largura // 2)
        y = (janela_ajuda.winfo_screenheight() // 2) - (altura // 2)
        janela_ajuda.geometry(f'{largura}x{altura}+{x}+{y}')
        
        # Conteúdo da ajuda
        frame_ajuda = ttk.Frame(janela_ajuda, style="TFrame", padding=20)
        frame_ajuda.pack(fill=tk.BOTH, expand=True)
        
        titulo = ttk.Label(
            frame_ajuda, 
            text="Ajuda do Visualizador de Estrutura de Diretórios",
            font=("Segoe UI", 14, "bold"),
            style="TLabel"
        )
        titulo.pack(anchor=tk.W, pady=(0, 15))
        
        # Área de texto para o conteúdo da ajuda
        texto_ajuda = scrolledtext.ScrolledText(
            frame_ajuda,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            background=self.cores["bg_cartao"],
            foreground=self.cores["texto_principal"],
            padx=10,
            pady=10
        )
        texto_ajuda.pack(fill=tk.BOTH, expand=True)
        
        # Conteúdo da ajuda
        conteudo_ajuda = """
# Visualizador de Estrutura de Diretórios

Este aplicativo permite gerar representações visuais da estrutura de diretórios em diferentes formatos.

## Funcionalidades Principais

1. **Seleção de Diretório**
   - Clique em "Escolher Pasta" para selecionar um diretório
   - O histórico mantém os últimos diretórios utilizados

2. **Opções de Visualização**
   - **Profundidade Máxima**: Limita a profundidade da árvore (0 = ilimitado)
   - **Incluir Arquivos Ocultos**: Mostra arquivos que começam com ponto (.)
   - **Mostrar Tamanho**: Exibe o tamanho dos arquivos
   - **Pastas a Ignorar**: Lista de pastas que serão ignoradas (node_modules, .git, etc.)
   - **Filtro de Extensões**: Permite filtrar arquivos por extensão

3. **Formatos de Saída**
   - **Markdown**: Formato de texto com ícones e estrutura visual
   - **HTML**: Visualização formatada para navegadores
   - **JSON**: Estrutura de dados para processamento

4. **Ações**
   - **Salvar**: Salva a visualização em um arquivo
   - **Copiar**: Copia o conteúdo para a área de transferência
   - **Visualizar no Navegador**: Abre a visualização no navegador padrão

## Atalhos de Teclado

- **Ctrl+O**: Abrir diálogo para selecionar diretório
- **Ctrl+G** ou **F5**: Gerar visualização
- **Ctrl+S**: Salvar visualização em arquivo
- **Ctrl+C**: Copiar para área de transferência
- **F1**: Mostrar esta ajuda

## Dicas

- O node_modules e outras pastas comuns são ignoradas por padrão
- Use o filtro de extensões para focar em tipos específicos de arquivos
- O tema escuro pode ser ativado pelo botão no canto superior direito
"""
        
        texto_ajuda.insert(tk.END, conteudo_ajuda)
        texto_ajuda.configure(state=tk.DISABLED)
        
        # Botão para fechar
        botao_fechar = ttk.Button(
            frame_ajuda,
            text="Fechar",
            command=janela_ajuda.destroy,
            style="Primary.TButton"
        )
        botao_fechar.pack(pady=(10, 0))
        
    def carregar_configuracoes(self):
        """Carregar configurações salvas"""
        try:
            caminho_config = os.path.join(os.path.expanduser("~"), ".visualizador_diretorios.json")
            
            if os.path.exists(caminho_config):
                with open(caminho_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Carregar tema
                if "tema_escuro" in config:
                    self.tema_escuro.set(config["tema_escuro"])
                    self.tema_atual = "escuro" if config["tema_escuro"] else "claro"
                    self.aplicar_tema()
                    
                # Carregar histórico
                if "historico" in config and isinstance(config["historico"], list):
                    self.historico_diretorios = [d for d in config["historico"] if os.path.isdir(d)]
                    if self.historico_diretorios:
                        self.combo_historico['values'] = self.historico_diretorios
                        
                # Carregar outras configurações
                if "incluir_ocultos" in config:
                    self.incluir_ocultos.set(config["incluir_ocultos"])
                    
                if "mostrar_tamanho" in config:
                    self.mostrar_tamanho.set(config["mostrar_tamanho"])
                    
                if "profundidade_maxima" in config:
                    self.profundidade_maxima.set(str(config["profundidade_maxima"]))
                    
                if "pastas_ignoradas" in config and isinstance(config["pastas_ignoradas"], list):
                    self.ignorar_padrao.set(",".join(config["pastas_ignoradas"]))
                    
                if "formato_saida" in config:
                    self.formato_saida.set(config["formato_saida"])
                    
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            
    def salvar_configuracoes(self):
        """Salvar configurações"""
        try:
            config = {
                "tema_escuro": self.tema_escuro.get(),
                "historico": self.historico_diretorios,
                "incluir_ocultos": self.incluir_ocultos.get(),
                "mostrar_tamanho": self.mostrar_tamanho.get(),
                "profundidade_maxima": int(self.profundidade_maxima.get()),
                "pastas_ignoradas": [p.strip() for p in self.ignorar_padrao.get().split(',') if p.strip()],
                "formato_saida": self.formato_saida.get()
            }
            
            caminho_config = os.path.join(os.path.expanduser("~"), ".visualizador_diretorios.json")
            
            with open(caminho_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

def main():
    root = tk.Tk()
    app = VisualizadorDiretorios(root)
    root.mainloop()

if __name__ == "__main__":
    main()