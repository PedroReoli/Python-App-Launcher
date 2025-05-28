import os
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox, font
import pathlib
from datetime import datetime
import json
import webbrowser
import threading
import tempfile
import locale

# Configurar localização para português
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

class VisualizadorDiretorios:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Estrutura de Diretórios")
        self.root.geometry("900x650")
        
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
        self.temas = {
            "claro": {
                "bg_principal": "#f8f9fa",
                "bg_cartao": "#ffffff",
                "texto_principal": "#212529",
                "texto_secundario": "#6c757d",
                "cor_destaque": "#0d6efd",
                "bg_entrada": "#ffffff",
                "bg_saida": "#f8f9fa",
                "bg_botao_primario": "#0d6efd",
                "texto_botao_primario": "#ffffff",
                "bg_botao_secundario": "#e9ecef",
                "texto_botao_secundario": "#212529",
                "bg_status": "#f8f9fa"
            },
            "escuro": {
                "bg_principal": "#212529",
                "bg_cartao": "#343a40",
                "texto_principal": "#f8f9fa",
                "texto_secundario": "#adb5bd",
                "cor_destaque": "#0d6efd",
                "bg_entrada": "#2b3035",
                "bg_saida": "#2b3035",
                "bg_botao_primario": "#0d6efd",
                "texto_botao_primario": "#ffffff",
                "bg_botao_secundario": "#495057",
                "texto_botao_secundario": "#f8f9fa",
                "bg_status": "#343a40"
            }
        }
        
        self.tema_atual = "claro"
        self.cores = self.temas[self.tema_atual]
        
        self.estilo = ttk.Style()
        self.estilo.theme_use("clam")
        self.aplicar_tema()
        
    def aplicar_tema(self):
        """Aplicar o tema atual aos widgets"""
        self.cores = self.temas[self.tema_atual]
        
        self.estilo.configure("TFrame", background=self.cores["bg_principal"])
        self.estilo.configure("Card.TFrame", background=self.cores["bg_cartao"])
        
        self.estilo.configure("TLabel", 
                             background=self.cores["bg_principal"],
                             foreground=self.cores["texto_principal"])
        self.estilo.configure("Card.TLabel", 
                             background=self.cores["bg_cartao"],
                             foreground=self.cores["texto_principal"])
        
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
        
        self.root.configure(background=self.cores["bg_principal"])
        
        if hasattr(self, 'frame_principal'):
            self.frame_principal.configure(background=self.cores["bg_principal"])
            
            if hasattr(self, 'area_saida'):
                self.area_saida.configure(
                    background=self.cores["bg_saida"],
                    foreground=self.cores["texto_principal"],
                    insertbackground=self.cores["texto_principal"]
                )
                
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
        self.frame_principal = ttk.Frame(self.root, style="TFrame", padding=10)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        self.frame_principal.columnconfigure(0, weight=1)
        self.frame_principal.rowconfigure(3, weight=1)
        
        self.criar_cabecalho()
        self.criar_painel_controle()
        self.criar_secao_saida()
        self.criar_barra_status()
        
    def criar_cabecalho(self):
        """Criar a seção de cabeçalho compacta"""
        frame_cabecalho = ttk.Frame(self.frame_principal, style="TFrame")
        frame_cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        frame_cabecalho.columnconfigure(0, weight=1)
        frame_cabecalho.columnconfigure(1, weight=0)
        
        frame_titulo = ttk.Frame(frame_cabecalho, style="TFrame")
        frame_titulo.grid(row=0, column=0, sticky="w")
        
        titulo = ttk.Label(
            frame_titulo, 
            text="Visualizador de Estrutura de Diretórios",
            font=("Segoe UI", 14, "bold"),
            style="TLabel"
        )
        titulo.pack(anchor=tk.W)
        
        self.botao_tema = ttk.Checkbutton(
            frame_cabecalho,
            text="Tema Escuro",
            variable=self.tema_escuro,
            command=self.alternar_tema,
            style="TCheckbutton"
        )
        self.botao_tema.grid(row=0, column=1, sticky="e")
        
    def criar_painel_controle(self):
        """Criar painel de controle compacto"""
        self.notebook_controle = ttk.Notebook(self.frame_principal)
        self.notebook_controle.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        self.aba_diretorio = ttk.Frame(self.notebook_controle, style="Card.TFrame", padding=8)
        self.notebook_controle.add(self.aba_diretorio, text="Diretório")
        self.configurar_aba_diretorio()
        
        self.aba_opcoes = ttk.Frame(self.notebook_controle, style="Card.TFrame", padding=8)
        self.notebook_controle.add(self.aba_opcoes, text="Opções")
        self.configurar_aba_opcoes()
        
        self.aba_filtros = ttk.Frame(self.notebook_controle, style="Card.TFrame", padding=8)
        self.notebook_controle.add(self.aba_filtros, text="Filtros")
        self.configurar_aba_filtros()
        
        self.criar_barra_acoes()
        
    def configurar_aba_diretorio(self):
        """Configurar aba de seleção de diretório"""
        self.aba_diretorio.columnconfigure(1, weight=1)
        
        botao_selecionar = ttk.Button(
            self.aba_diretorio,
            text="Escolher Pasta",
            command=self.selecionar_diretorio,
            style="Primary.TButton",
            width=15
        )
        botao_selecionar.grid(row=0, column=0, padx=(0, 5))
        
        self.entrada_diretorio = ttk.Entry(
            self.aba_diretorio,
            font=("Segoe UI", 9)
        )
        self.entrada_diretorio.grid(row=0, column=1, sticky="ew")
        
        ttk.Label(
            self.aba_diretorio,
            text="Histórico:",
            style="Card.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        self.combo_historico = ttk.Combobox(
            self.aba_diretorio,
            font=("Segoe UI", 9),
            state="readonly"
        )
        self.combo_historico.grid(row=1, column=1, sticky="ew", pady=(5, 0))
        self.combo_historico.bind("<<ComboboxSelected>>", self.selecionar_do_historico)
        
    def configurar_aba_opcoes(self):
        """Configurar aba de opções básicas"""
        self.aba_opcoes.columnconfigure(0, weight=1)
        self.aba_opcoes.columnconfigure(1, weight=1)
        
        ttk.Label(
            self.aba_opcoes,
            text="Profundidade Máxima:",
            style="Card.TLabel"
        ).grid(row=0, column=0, sticky="w")
        
        frame_profundidade = ttk.Frame(self.aba_opcoes, style="Card.TFrame")
        frame_profundidade.grid(row=0, column=1, sticky="w")
        
        entrada_profundidade = ttk.Entry(
            frame_profundidade,
            width=5,
            textvariable=self.profundidade_maxima,
            font=("Segoe UI", 9)
        )
        entrada_profundidade.pack(side=tk.LEFT)
        
        ttk.Label(
            frame_profundidade,
            text="(0 = ilimitado)",
            style="Card.TLabel"
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(
            self.aba_opcoes,
            text="Formato de Saída:",
            style="Card.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        frame_formato = ttk.Frame(self.aba_opcoes, style="Card.TFrame")
        frame_formato.grid(row=1, column=1, sticky="w", pady=(5, 0))
        
        ttk.Radiobutton(
            frame_formato,
            text="Markdown",
            variable=self.formato_saida,
            value="markdown",
            style="TCheckbutton"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Radiobutton(
            frame_formato,
            text="HTML",
            variable=self.formato_saida,
            value="html",
            style="TCheckbutton"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Radiobutton(
            frame_formato,
            text="JSON",
            variable=self.formato_saida,
            value="json",
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
        
        ttk.Checkbutton(
            self.aba_opcoes,
            text="Incluir Arquivos Ocultos",
            variable=self.incluir_ocultos,
            style="TCheckbutton"
        ).grid(row=2, column=0, sticky="w", pady=(5, 0))
        
        ttk.Checkbutton(
            self.aba_opcoes,
            text="Mostrar Tamanho dos Arquivos",
            variable=self.mostrar_tamanho,
            style="TCheckbutton"
        ).grid(row=2, column=1, sticky="w", pady=(5, 0))
        
    def configurar_aba_filtros(self):
        """Configurar aba de filtros"""
        self.aba_filtros.columnconfigure(0, weight=1)
        
        ttk.Label(
            self.aba_filtros,
            text="Pastas a Ignorar (separadas por vírgula):",
            style="Card.TLabel"
        ).grid(row=0, column=0, sticky="w")
        
        entrada_ignorar = ttk.Entry(
            self.aba_filtros,
            textvariable=self.ignorar_padrao,
            font=("Segoe UI", 9)
        )
        entrada_ignorar.grid(row=1, column=0, sticky="ew")
        
        ttk.Checkbutton(
            self.aba_filtros,
            text="Filtrar por Extensões",
            variable=self.filtrar_extensoes,
            style="TCheckbutton"
        ).grid(row=2, column=0, sticky="w", pady=(5, 0))
        
        ttk.Label(
            self.aba_filtros,
            text="Extensões a Incluir (ex: py,txt,md):",
            style="Card.TLabel"
        ).grid(row=3, column=0, sticky="w")
        
        entrada_extensoes = ttk.Entry(
            self.aba_filtros,
            textvariable=self.extensoes_filtro,
            font=("Segoe UI", 9)
        )
        entrada_extensoes.grid(row=4, column=0, sticky="ew")
        
    def criar_barra_acoes(self):
        """Criar barra de botões de ação"""
        frame_acoes = ttk.Frame(self.frame_principal, style="TFrame")
        frame_acoes.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        
        botao_gerar = ttk.Button(
            frame_acoes,
            text="Gerar Visualização (F5)",
            command=self.gerar_visualizacao,
            style="Primary.TButton"
        )
        botao_gerar.pack(side=tk.LEFT)
        
        botao_salvar = ttk.Button(
            frame_acoes,
            text="Salvar",
            command=self.salvar_arquivo,
            style="TButton"
        )
        botao_salvar.pack(side=tk.RIGHT)
        
        botao_visualizar = ttk.Button(
            frame_acoes,
            text="Visualizar",
            command=self.visualizar_no_navegador,
            style="TButton"
        )
        botao_visualizar.pack(side=tk.RIGHT, padx=5)
        
        botao_copiar = ttk.Button(
            frame_acoes,
            text="Copiar",
            command=self.copiar_para_clipboard,
            style="TButton"
        )
        botao_copiar.pack(side=tk.RIGHT)
        
    def criar_secao_saida(self):
        """Criar a seção de saída"""
        frame_saida = ttk.Frame(self.frame_principal, style="Card.TFrame")
        frame_saida.grid(row=3, column=0, sticky="nsew")
        frame_saida.columnconfigure(0, weight=1)
        frame_saida.rowconfigure(1, weight=1)
        
        ttk.Label(
            frame_saida,
            text="Visualização",
            font=("Segoe UI", 10, "bold"),
            style="Card.TLabel"
        ).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        fonte_saida = font.Font(family="Consolas", size=9)
        
        self.area_saida = scrolledtext.ScrolledText(
            frame_saida,
            wrap=tk.NONE,
            font=fonte_saida,
            background=self.cores["bg_saida"],
            foreground=self.cores["texto_principal"],
            borderwidth=1,
            relief="solid"
        )
        self.area_saida.grid(row=1, column=0, sticky="nsew")
        
        barra_rolagem_h = ttk.Scrollbar(
            frame_saida,
            orient=tk.HORIZONTAL,
            command=self.area_saida.xview
        )
        barra_rolagem_h.grid(row=2, column=0, sticky="ew")
        self.area_saida.configure(xscrollcommand=barra_rolagem_h.set)
        
    def criar_barra_status(self):
        """Criar a barra de status"""
        self.var_status = tk.StringVar()
        
        self.barra_status = ttk.Label(
            self.root,
            textvariable=self.var_status,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.barra_status.pack(side=tk.BOTTOM, fill=tk.X)
        
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
            
            self.adicionar_ao_historico(diretorio)
            self.gerar_visualizacao()
            
    def selecionar_do_historico(self, event):
        """Selecionar diretório do histórico"""
        selecionado = self.combo_historico.get()
        if selecionado:
            self.entrada_diretorio.delete(0, tk.END)
            self.entrada_diretorio.insert(0, selecionado)
            self.diretorio_atual = selecionado
            self.var_status.set(f"Diretório selecionado: {selecionado}")
            
            self.gerar_visualizacao()
            
    def adicionar_ao_historico(self, diretorio):
        """Adicionar diretório ao histórico"""
        if diretorio in self.historico_diretorios:
            self.historico_diretorios.remove(diretorio)
            
        self.historico_diretorios.insert(0, diretorio)
        
        if len(self.historico_diretorios) > self.max_historico:
            self.historico_diretorios = self.historico_diretorios[:self.max_historico]
            
        self.combo_historico['values'] = self.historico_diretorios
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
            
        if self.gerando_visualizacao:
            return
            
        self.gerando_visualizacao = True
        self.var_status.set("Gerando visualização...")
        self.root.update_idletasks()
        
        incluir_ocultos = self.incluir_ocultos.get()
        mostrar_tamanho = self.mostrar_tamanho.get()
        formato = self.formato_saida.get()
        
        pastas_ignorar = [p.strip() for p in self.ignorar_padrao.get().split(',') if p.strip()]
        
        filtrar_por_extensao = self.filtrar_extensoes.get()
        extensoes = [ext.strip().lower() for ext in self.extensoes_filtro.get().split(',') if ext.strip()]
        
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
        nome_dir = caminho_diretorio.name or caminho_diretorio.anchor
        
        resultado = [f"# 📁 Estrutura do Diretório: {nome_dir}\n"]
        resultado.append(f"*Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*\n")
        
        estatisticas = self.calcular_estatisticas(
            caminho_diretorio, incluir_ocultos, pastas_ignorar, 
            filtrar_por_extensao, extensoes
        )
        resultado.append("## Estatísticas\n")
        resultado.append(f"- **Total de Diretórios:** {estatisticas['total_diretorios']}")
        resultado.append(f"- **Total de Arquivos:** {estatisticas['total_arquivos']}")
        resultado.append(f"- **Tamanho Total:** {self.formatar_tamanho(estatisticas['tamanho_total'])}\n")
        
        resultado.append(f"## Estrutura\n")
        resultado.append(f"📁 {nome_dir}/")
        
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
            
        try:
            itens = list(caminho.iterdir())
        except PermissionError:
            resultado.append(f"{prefixo}├── ⚠️ Permissão negada")
            return
        except Exception as e:
            resultado.append(f"{prefixo}├── ⚠️ Erro: {str(e)}")
            return
            
        itens_filtrados = []
        for item in itens:
            if item.is_dir() and item.name in pastas_ignorar:
                continue
                
            if not incluir_ocultos and item.name.startswith('.'):
                continue
                
            if filtrar_por_extensao and not item.is_dir():
                if not extensoes:
                    continue
                    
                ext = item.suffix.lower().lstrip('.')
                if ext not in extensoes:
                    continue
                    
            itens_filtrados.append(item)
            
        itens_filtrados.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
        
        for i, item in enumerate(itens_filtrados):
            eh_ultimo = i == len(itens_filtrados) - 1
            
            prefixo_item = "└── " if eh_ultimo else "├── "
            
            icone = "📁" if item.is_dir() else self.obter_icone_arquivo(item)
            
            info_tamanho = ""
            if mostrar_tamanho and not item.is_dir():
                try:
                    tamanho = item.stat().st_size
                    info_tamanho = f" ({self.formatar_tamanho(tamanho)})"
                except:
                    info_tamanho = " (tamanho desconhecido)"
                    
            resultado.append(f"{prefixo}{prefixo_item}{icone} {item.name}{info_tamanho}")
            
            if item.is_dir():
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
        
        estatisticas = self.calcular_estatisticas(
            caminho_diretorio, incluir_ocultos, pastas_ignorar, 
            filtrar_por_extensao, extensoes
        )
        
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
        
        html.append(f"        <div class='tree-item'><span class='folder'>📁 {nome_dir}/</span></div>")
        
        itens_arvore = []
        
        self._gerar_arvore_html(
            caminho_diretorio, "", itens_arvore, incluir_ocultos, mostrar_tamanho,
            profundidade_maxima, pastas_ignorar, filtrar_por_extensao, extensoes, 0
        )
        
        html.extend(itens_arvore)
        
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
            
        try:
            itens = list(caminho.iterdir())
        except PermissionError:
            resultado.append(f"        <div class='tree-item'>{prefixo}├── <span class='error'>⚠️ Permissão negada</span></div>")
            return
        except Exception as e:
            resultado.append(f"        <div class='tree-item'>{prefixo}├── <span class='error'>⚠️ Erro: {str(e)}</span></div>")
            return
            
        itens_filtrados = []
        for item in itens:
            if item.is_dir() and item.name in pastas_ignorar:
                continue
                
            if not incluir_ocultos and item.name.startswith('.'):
                continue
                
            if filtrar_por_extensao and not item.is_dir():
                if not extensoes:
                    continue
                    
                ext = item.suffix.lower().lstrip('.')
                if ext not in extensoes:
                    continue
                    
            itens_filtrados.append(item)
            
        itens_filtrados.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
        
        for i, item in enumerate(itens_filtrados):
            eh_ultimo = i == len(itens_filtrados) - 1
            
            prefixo_item = "└── " if eh_ultimo else "├── "
            
            icone = "📁" if item.is_dir() else self.obter_icone_arquivo(item)
            
            info_tamanho = ""
            if mostrar_tamanho and not item.is_dir():
                try:
                    tamanho = item.stat().st_size
                    info_tamanho = f" <span class='size'>({self.formatar_tamanho(tamanho)})</span>"
                except:
                    info_tamanho = " <span class='size'>(tamanho desconhecido)</span>"
                    
            classe = "folder" if item.is_dir() else "file"
            resultado.append(f"        <div class='tree-item'>{prefixo}{prefixo_item}<span class='{classe}'>{icone} {item.name}</span>{info_tamanho}</div>")
            
            if item.is_dir():
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
        
        estatisticas = self.calcular_estatisticas(
            caminho_diretorio, incluir_ocultos, pastas_ignorar, 
            filtrar_por_extensao, extensoes
        )
        
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
        
        self._gerar_arvore_json(
            caminho_diretorio, estrutura["conteudo"], incluir_ocultos, mostrar_tamanho,
            profundidade_maxima, pastas_ignorar, filtrar_por_extensao, extensoes, 0
        )
        
        return json.dumps(estrutura, indent=2, ensure_ascii=False)
        
    def _gerar_arvore_json(self, caminho, resultado, incluir_ocultos, mostrar_tamanho, 
                          profundidade_maxima, pastas_ignorar, filtrar_por_extensao, 
                          extensoes, profundidade_atual):
        """Gerar recursivamente a estrutura da árvore em formato JSON"""
        if profundidade_maxima > 0 and profundidade_atual >= profundidade_maxima:
            return
            
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
            
        itens_filtrados = []
        for item in itens:
            if item.is_dir() and item.name in pastas_ignorar:
                continue
                
            if not incluir_ocultos and item.name.startswith('.'):
                continue
                
            if filtrar_por_extensao and not item.is_dir():
                if not extensoes:
                    continue
                    
                ext = item.suffix.lower().lstrip('.')
                if ext not in extensoes:
                    continue
                    
            itens_filtrados.append(item)
            
        itens_filtrados.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
        
        for item in itens_filtrados:
            if item.is_dir():
                dir_obj = {
                    "nome": item.name,
                    "tipo": "diretorio",
                    "caminho": str(item),
                    "conteudo": []
                }
                
                resultado.append(dir_obj)
                
                self._gerar_arvore_json(
                    item, dir_obj["conteudo"], incluir_ocultos, mostrar_tamanho,
                    profundidade_maxima, pastas_ignorar, filtrar_por_extensao, extensoes,
                    profundidade_atual + 1
                )
            else:
                arquivo_obj = {
                    "nome": item.name,
                    "tipo": "arquivo",
                    "caminho": str(item),
                    "extensao": item.suffix.lower().lstrip('.') if item.suffix else ""
                }
                
                if mostrar_tamanho:
                    try:
                        tamanho = item.stat().st_size
                        arquivo_obj["tamanho"] = tamanho
                        arquivo_obj["tamanho_formatado"] = self.formatar_tamanho(tamanho)
                    except:
                        arquivo_obj["tamanho"] = -1
                        arquivo_obj["tamanho_formatado"] = "desconhecido"
                        
                resultado.append(arquivo_obj)
                
    def calcular_estatisticas(self, caminho, incluir_ocultos, pastas_ignorar, 
                             filtrar_por_extensao, extensoes):
        """Calcular estatísticas do diretório"""
        total_diretorios = 0
        total_arquivos = 0
        tamanho_total = 0
        
        for raiz, diretorios, arquivos in os.walk(caminho):
            diretorios_filtrados = []
            for d in diretorios:
                if d in pastas_ignorar:
                    continue
                if not incluir_ocultos and d.startswith('.'):
                    continue
                diretorios_filtrados.append(d)
                
            diretorios[:] = diretorios_filtrados
            total_diretorios += len(diretorios_filtrados)
            
            for arquivo in arquivos:
                if not incluir_ocultos and arquivo.startswith('.'):
                    continue
                    
                if filtrar_por_extensao:
                    if not extensoes:
                        continue
                        
                    ext = os.path.splitext(arquivo)[1].lower().lstrip('.')
                    if ext not in extensoes:
                        continue
                        
                total_arquivos += 1
                
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
        
        icones = {
            '.py': '🐍', '.js': '📜', '.ts': '📜', '.html': '🌐', '.css': '🎨',
            '.java': '☕', '.c': '🔧', '.cpp': '🔧', '.h': '📋', '.php': '🐘',
            '.rb': '💎', '.go': '🔹', '.rs': '🦀', '.swift': '🔶', '.kt': '🔷',
            '.txt': '📄', '.md': '📝', '.pdf': '📕', '.doc': '📘', '.docx': '📘',
            '.xls': '📊', '.xlsx': '📊', '.ppt': '📊', '.pptx': '📊',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
            '.bmp': '🖼️', '.tiff': '🖼️', '.mp3': '🎵', '.wav': '🎵', '.ogg': '🎵',
            '.mp4': '🎬', '.avi': '🎬', '.mov': '🎬', '.mkv': '🎬',
            '.zip': '📦', '.rar': '📦', '.tar': '📦', '.gz': '📦', '.7z': '📦',
            '.json': '⚙️', '.xml': '⚙️', '.yml': '⚙️', '.yaml': '⚙️',
            '.ini': '⚙️', '.conf': '⚙️', '.env': '⚙️', '.exe': '⚡',
            '.bat': '⚡', '.sh': '⚡', '.db': '🗃️', '.sql': '🗃️',
            '.log': '📋', '.gitignore': '🔍', '.dockerfile': '🐳'
        }
        
        return icones.get(extensao, '📄')
        
    def formatar_tamanho(self, tamanho_bytes):
        """Formatar tamanho em bytes para uma representação legível"""
        if tamanho_bytes < 0:
            return "desconhecido"
            
        unidades = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        
        indice_unidade = 0
        tamanho = float(tamanho_bytes)
        
        while tamanho >= 1024 and indice_unidade < len(unidades) - 1:
            tamanho /= 1024
            indice_unidade += 1
            
        if indice_unidade == 0:
            return f"{int(tamanho)} {unidades[indice_unidade]}"
        else:
            return f"{tamanho:.2f} {unidades[indice_unidade]}"
            
    def salvar_arquivo(self):
        """Salvar a visualização em um arquivo"""
        if not self.ultima_saida:
            messagebox.showerror("Erro", "Não há conteúdo para salvar")
            return
            
        formato = self.formato_saida.get()
        extensoes = {
            "markdown": ".md",
            "html": ".html",
            "json": ".json"
        }
        
        extensao_padrao = extensoes.get(formato, ".txt")
        
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
        
        try:
            extensoes = {
                "markdown": ".md",
                "html": ".html",
                "json": ".json"
            }
            
            extensao = extensoes.get(formato, ".txt")
            
            with tempfile.NamedTemporaryFile(suffix=extensao, delete=False, mode='w', encoding='utf-8') as temp:
                temp.write(self.ultima_saida)
                caminho_temp = temp.name
                
            webbrowser.open(f"file://{caminho_temp}")
            self.var_status.set("Visualização aberta no navegador")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir no navegador: {str(e)}")
            
    def mostrar_ajuda(self):
        """Mostrar janela de ajuda"""
        janela_ajuda = tk.Toplevel(self.root)
        janela_ajuda.title("Ajuda - Visualizador de Estrutura de Diretórios")
        janela_ajuda.geometry("500x400")
        janela_ajuda.configure(background=self.cores["bg_principal"])
        
        janela_ajuda.update_idletasks()
        largura = janela_ajuda.winfo_width()
        altura = janela_ajuda.winfo_height()
        x = (janela_ajuda.winfo_screenwidth() // 2) - (largura // 2)
        y = (janela_ajuda.winfo_screenheight() // 2) - (altura // 2)
        janela_ajuda.geometry(f'{largura}x{altura}+{x}+{y}')
        
        frame_ajuda = ttk.Frame(janela_ajuda, style="TFrame", padding=10)
        frame_ajuda.pack(fill=tk.BOTH, expand=True)
        
        titulo = ttk.Label(
            frame_ajuda, 
            text="Ajuda do Visualizador",
            font=("Segoe UI", 12, "bold"),
            style="TLabel"
        )
        titulo.pack(anchor=tk.W, pady=(0, 10))
        
        texto_ajuda = scrolledtext.ScrolledText(
            frame_ajuda,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            background=self.cores["bg_cartao"],
            foreground=self.cores["texto_principal"]
        )
        texto_ajuda.pack(fill=tk.BOTH, expand=True)
        
        conteudo_ajuda = """# Visualizador de Estrutura de Diretórios

Este aplicativo permite gerar representações visuais da estrutura de diretórios.

## Funcionalidades Principais

1. **Seleção de Diretório**
   - Clique em "Escolher Pasta" para selecionar um diretório
   - O histórico mantém os últimos diretórios utilizados

2. **Opções de Visualização**
   - **Profundidade Máxima**: Limita a profundidade da árvore (0 = ilimitado)
   - **Incluir Arquivos Ocultos**: Mostra arquivos que começam com ponto (.)
   - **Mostrar Tamanho**: Exibe o tamanho dos arquivos

3. **Formatos de Saída**
   - **Markdown**: Formato de texto com ícones e estrutura visual
   - **HTML**: Visualização formatada para navegadores
   - **JSON**: Estrutura de dados para processamento

4. **Ações**
   - **Salvar**: Salva a visualização em um arquivo
   - **Copiar**: Copia o conteúdo para a área de transferência
   - **Visualizar**: Abre a visualização no navegador padrão

## Atalhos de Teclado

- **Ctrl+O**: Abrir diálogo para selecionar diretório
- **Ctrl+G** ou **F5**: Gerar visualização
- **Ctrl+S**: Salvar visualização em arquivo
- **Ctrl+C**: Copiar para área de transferência
- **F1**: Mostrar esta ajuda

## Dicas

- O node_modules e outras pastas comuns são ignoradas por padrão
- Use o filtro de extensões para focar em tipos específicos de arquivos
- O tema escuro pode ser ativado pelo botão no canto superior direito"""
        
        texto_ajuda.insert(tk.END, conteudo_ajuda)
        texto_ajuda.configure(state=tk.DISABLED)
        
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
                    
                if "tema_escuro" in config:
                    self.tema_escuro.set(config["tema_escuro"])
                    self.tema_atual = "escuro" if config["tema_escuro"] else "claro"
                    self.aplicar_tema()
                    
                if "historico" in config and isinstance(config["historico"], list):
                    self.historico_diretorios = [d for d in config["historico"] if os.path.isdir(d)]
                    if self.historico_diretorios:
                        self.combo_historico['values'] = self.historico_diretorios
                        
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