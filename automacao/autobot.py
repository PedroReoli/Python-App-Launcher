import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import time
from pynput import keyboard
import threading
import json
import os

class AutomacaoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automação de Tarefas")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Definir cores e estilos
        self.cores = {
            "primaria": "#3498db",
            "secundaria": "#2980b9",
            "destaque": "#e74c3c",
            "sucesso": "#2ecc71",
            "aviso": "#f39c12",
            "texto": "#2c3e50",
            "fundo": "#ecf0f1",
            "fundo_escuro": "#bdc3c7"
        }
        
        # Configurar tema
        self.configurar_tema()
        
        # Variáveis
        self.acoes = []
        self.capturando = False
        self.listener = None
        self.arquivo_atual = None
        self.modificado = False
        
        # Criar interface
        self.criar_interface()
        
        # Iniciar listener de teclado global
        self.iniciar_listener()
        
        # Configurar protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)
    
    def configurar_tema(self):
        # Configurar estilo
        self.style = ttk.Style()
        
        # Configurar tema claro
        self.style.theme_use('clam')
        
        # Configurar estilos dos widgets
        self.style.configure("TFrame", background=self.cores["fundo"])
        self.style.configure("TLabel", background=self.cores["fundo"], foreground=self.cores["texto"])
        self.style.configure("TLabelframe", background=self.cores["fundo"], foreground=self.cores["texto"])
        self.style.configure("TLabelframe.Label", background=self.cores["fundo"], foreground=self.cores["texto"])
        
        # Botões
        self.style.configure("TButton", 
                            background=self.cores["primaria"], 
                            foreground="white", 
                            padding=(10, 5),
                            font=('Arial', 9, 'bold'))
        self.style.map("TButton",
                      background=[('active', self.cores["secundaria"])],
                      foreground=[('active', 'white')])
        
        # Botões de ação
        self.style.configure("Acao.TButton", 
                            background=self.cores["destaque"], 
                            foreground="white")
        self.style.map("Acao.TButton",
                      background=[('active', "#c0392b")],
                      foreground=[('active', 'white')])
        
        # Botões de sucesso
        self.style.configure("Sucesso.TButton", 
                            background=self.cores["sucesso"], 
                            foreground="white")
        self.style.map("Sucesso.TButton",
                      background=[('active', "#27ae60")],
                      foreground=[('active', 'white')])
    
    def criar_interface(self):
        # Frame principal com padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Criar menu
        self.criar_menu()
        
        # Frame de título
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.pack(fill=tk.X, pady=(0, 10))
        
        titulo_label = ttk.Label(titulo_frame, text="Automação de Tarefas", 
                                font=('Arial', 16, 'bold'), foreground=self.cores["primaria"])
        titulo_label.pack(side=tk.LEFT)
        
        # Status do arquivo
        self.status_arquivo_var = tk.StringVar(value="Novo projeto")
        status_arquivo_label = ttk.Label(titulo_frame, textvariable=self.status_arquivo_var, 
                                        font=('Arial', 10, 'italic'))
        status_arquivo_label.pack(side=tk.RIGHT)
        
        # Frame de controles principais
        control_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        
        # Grid para botões de controle
        control_grid = ttk.Frame(control_frame)
        control_grid.pack(fill=tk.X)
        
        # Botões de controle com ícones (simulados com texto)
        ttk.Button(control_grid, text="▶ Iniciar Captura (F8)", 
                  command=self.iniciar_captura, style="Sucesso.TButton").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(control_grid, text="■ Parar Captura (F9)", 
                  command=self.parar_captura, style="Acao.TButton").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(control_grid, text="⚡ Executar Sequência (F10)", 
                  command=self.executar_sequencia).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(control_grid, text="🗑️ Limpar Tudo", 
                  command=self.limpar_acoes).grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Configurar pesos das colunas
        for i in range(4):
            control_grid.columnconfigure(i, weight=1)
        
        # Frame de ações de teclado
        keyboard_frame = ttk.LabelFrame(main_frame, text="Ações de Teclado", padding="10")
        keyboard_frame.pack(fill=tk.X, pady=10)
        
        # Grid para botões de ações de teclado
        keyboard_grid = ttk.Frame(keyboard_frame)
        keyboard_grid.pack(fill=tk.X)
        
        # Primeira linha de botões
        ttk.Button(keyboard_grid, text="Ctrl+A (Selecionar)", 
                  command=lambda: self.adicionar_acao("teclado", "ctrl+a")).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(keyboard_grid, text="Ctrl+C (Copiar)", 
                  command=lambda: self.adicionar_acao("teclado", "ctrl+c")).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(keyboard_grid, text="Ctrl+V (Colar)", 
                  command=lambda: self.adicionar_acao("teclado", "ctrl+v")).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(keyboard_grid, text="Delete", 
                  command=lambda: self.adicionar_acao("teclado", "delete")).grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Segunda linha de botões
        ttk.Button(keyboard_grid, text="Enter", 
                  command=lambda: self.adicionar_acao("teclado", "enter")).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(keyboard_grid, text="Tab", 
                  command=lambda: self.adicionar_acao("teclado", "tab")).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(keyboard_grid, text="Esc", 
                  command=lambda: self.adicionar_acao("teclado", "esc")).grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(keyboard_grid, text="Backspace", 
                  command=lambda: self.adicionar_acao("teclado", "backspace")).grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        
        # Configurar pesos das colunas
        for i in range(4):
            keyboard_grid.columnconfigure(i, weight=1)
        
        # Frame de texto personalizado
        text_frame = ttk.Frame(main_frame, padding="5")
        text_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(text_frame, text="Texto para digitar:").pack(side=tk.LEFT, padx=5)
        self.texto_var = tk.StringVar()
        texto_entry = ttk.Entry(text_frame, textvariable=self.texto_var, width=30)
        texto_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(text_frame, text="Adicionar Texto", 
                  command=self.adicionar_texto).pack(side=tk.LEFT, padx=5)
        
        # Frame de delay
        delay_frame = ttk.Frame(main_frame, padding="5")
        delay_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(delay_frame, text="Delay (segundos):").pack(side=tk.LEFT, padx=5)
        self.delay_var = tk.StringVar(value="0.5")
        delay_entry = ttk.Entry(delay_frame, textvariable=self.delay_var, width=5)
        delay_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(delay_frame, text="Adicionar Delay", 
                  command=self.adicionar_delay).pack(side=tk.LEFT, padx=5)
        
        # Frame de repetição
        repeat_frame = ttk.Frame(main_frame, padding="5")
        repeat_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(repeat_frame, text="Repetições:").pack(side=tk.LEFT, padx=5)
        self.repeticoes_var = tk.StringVar(value="1")
        repeticoes_entry = ttk.Entry(repeat_frame, textvariable=self.repeticoes_var, width=5)
        repeticoes_entry.pack(side=tk.LEFT, padx=5)
        
        # Frame de lista de ações
        list_frame = ttk.LabelFrame(main_frame, text="Sequência de Ações", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame para a lista e scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para a lista
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Lista de ações com cores alternadas
        self.acoes_listbox = tk.Listbox(list_container, height=10, 
                                       yscrollcommand=scrollbar.set, 
                                       selectmode=tk.SINGLE,
                                       font=('Arial', 10),
                                       bg=self.cores["fundo"],
                                       fg=self.cores["texto"],
                                       selectbackground=self.cores["primaria"],
                                       activestyle="none")
        self.acoes_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.acoes_listbox.yview)
        
        # Botões de edição
        edit_frame = ttk.Frame(list_frame)
        edit_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(edit_frame, text="↑ Mover Para Cima", 
                  command=self.mover_para_cima).pack(side=tk.LEFT, padx=5)
        ttk.Button(edit_frame, text="↓ Mover Para Baixo", 
                  command=self.mover_para_baixo).pack(side=tk.LEFT, padx=5)
        ttk.Button(edit_frame, text="✖ Remover Ação", 
                  command=self.remover_acao, style="Acao.TButton").pack(side=tk.LEFT, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, padding=(5, 2))
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value="Pronto")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Instruções
        instrucoes = """
        Durante a captura:
        • T: Capturar posição do mouse
        • A: Adicionar 'Selecionar Tudo'
        • C: Adicionar 'Copiar'
        • V: Adicionar 'Colar'
        • D: Adicionar 'Delete'
        """
        instrucoes_label = ttk.Label(main_frame, text=instrucoes, 
                                    font=('Arial', 9, 'italic'),
                                    foreground=self.cores["texto"],
                                    background=self.cores["fundo_escuro"],
                                    padding=10)
        instrucoes_label.pack(fill=tk.X, pady=(10, 0))
    
    def criar_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        arquivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=arquivo_menu)
        arquivo_menu.add_command(label="Novo", command=self.novo_arquivo)
        arquivo_menu.add_command(label="Abrir...", command=self.abrir_arquivo)
        arquivo_menu.add_command(label="Salvar", command=self.salvar_arquivo)
        arquivo_menu.add_command(label="Salvar Como...", command=self.salvar_como)
        arquivo_menu.add_separator()
        arquivo_menu.add_command(label="Sair", command=self.ao_fechar)
        
        # Menu Editar
        editar_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=editar_menu)
        editar_menu.add_command(label="Limpar Tudo", command=self.limpar_acoes)
        editar_menu.add_separator()
        editar_menu.add_command(label="Mover Para Cima", command=self.mover_para_cima)
        editar_menu.add_command(label="Mover Para Baixo", command=self.mover_para_baixo)
        editar_menu.add_command(label="Remover Ação", command=self.remover_acao)
        
        # Menu Executar
        executar_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Executar", menu=executar_menu)
        executar_menu.add_command(label="Iniciar Captura", command=self.iniciar_captura)
        executar_menu.add_command(label="Parar Captura", command=self.parar_captura)
        executar_menu.add_command(label="Executar Sequência", command=self.executar_sequencia)
        
        # Menu Ajuda
        ajuda_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=ajuda_menu)
        ajuda_menu.add_command(label="Sobre", command=self.mostrar_sobre)
    
    def iniciar_listener(self):
        def on_press(key):
            try:
                if self.capturando:
                    # Tecla T para capturar posição do mouse
                    if key.char.lower() == 't':
                        self.capturar_posicao_mouse()
                    # Tecla A para selecionar tudo
                    elif key.char.lower() == 'a':
                        self.adicionar_acao("teclado", "ctrl+a")
                        self.status_var.set("Adicionado: Selecionar Tudo (Ctrl+A)")
                    # Tecla C para copiar
                    elif key.char.lower() == 'c':
                        self.adicionar_acao("teclado", "ctrl+c")
                        self.status_var.set("Adicionado: Copiar (Ctrl+C)")
                    # Tecla V para colar
                    elif key.char.lower() == 'v':
                        self.adicionar_acao("teclado", "ctrl+v")
                        self.status_var.set("Adicionado: Colar (Ctrl+V)")
                    # Tecla D para delete
                    elif key.char.lower() == 'd':
                        self.adicionar_acao("teclado", "delete")
                        self.status_var.set("Adicionado: Delete")
                
                # Teclas de função para controle (funcionam sempre)
                if key == keyboard.Key.f8:
                    self.iniciar_captura()
                elif key == keyboard.Key.f9:
                    self.parar_captura()
                elif key == keyboard.Key.f10:
                    self.executar_sequencia()
            except (AttributeError, TypeError):
                pass
        
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
    
    def iniciar_captura(self):
        self.capturando = True
        self.status_var.set("Capturando... Use T para posição do mouse, A/C/V/D para ações de teclado")
        messagebox.showinfo("Captura Iniciada", 
                           "Captura iniciada!\n\n"
                           "- T: Capturar posição do mouse\n"
                           "- A: Adicionar 'Selecionar Tudo'\n"
                           "- C: Adicionar 'Copiar'\n"
                           "- V: Adicionar 'Colar'\n"
                           "- D: Adicionar 'Delete'")
    
    def parar_captura(self):
        self.capturando = False
        self.status_var.set("Captura parada")
    
    def capturar_posicao_mouse(self):
        if self.capturando:
            x, y = pyautogui.position()
            self.adicionar_acao("mouse", f"clique em ({x}, {y})")
            self.status_var.set(f"Posição capturada: ({x}, {y})")
    
    def adicionar_acao(self, tipo, valor):
        acao = {"tipo": tipo, "valor": valor}
        self.acoes.append(acao)
        self.atualizar_listbox()
        self.modificado = True
        
        # Selecionar a ação recém-adicionada na lista
        self.acoes_listbox.selection_clear(0, tk.END)
        self.acoes_listbox.selection_set(tk.END)
        self.acoes_listbox.see(tk.END)
    
    def adicionar_texto(self):
        texto = self.texto_var.get().strip()
        if texto:
            self.adicionar_acao("texto", texto)
            self.status_var.set(f"Texto adicionado: {texto}")
            self.texto_var.set("")  # Limpar o campo após adicionar
    
    def adicionar_delay(self):
        try:
            delay = float(self.delay_var.get())
            if delay > 0:
                self.adicionar_acao("delay", f"{delay} segundos")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor numérico válido para o delay.")
    
    def atualizar_listbox(self):
        self.acoes_listbox.delete(0, tk.END)
        for i, acao in enumerate(self.acoes):
            texto = ""
            if acao["tipo"] == "mouse":
                texto = f"{i+1}. Mouse: {acao['valor']}"
            elif acao["tipo"] == "teclado":
                texto = f"{i+1}. Teclado: {acao['valor']}"
            elif acao["tipo"] == "delay":
                texto = f"{i+1}. Delay: {acao['valor']}"
            elif acao["tipo"] == "texto":
                # Limitar o tamanho do texto mostrado
                texto_mostrado = acao["valor"]
                if len(texto_mostrado) > 30:
                    texto_mostrado = texto_mostrado[:27] + "..."
                texto = f"{i+1}. Texto: \"{texto_mostrado}\""
            
            self.acoes_listbox.insert(tk.END, texto)
            
            # Alternar cores das linhas para melhor visualização
            if i % 2 == 0:
                self.acoes_listbox.itemconfig(i, bg=self.cores["fundo"])
            else:
                self.acoes_listbox.itemconfig(i, bg=self.cores["fundo_escuro"])
    
    def mover_para_cima(self):
        selecionado = self.acoes_listbox.curselection()
        if selecionado and selecionado[0] > 0:
            idx = selecionado[0]
            self.acoes[idx], self.acoes[idx-1] = self.acoes[idx-1], self.acoes[idx]
            self.atualizar_listbox()
            self.acoes_listbox.selection_set(idx-1)
            self.modificado = True
    
    def mover_para_baixo(self):
        selecionado = self.acoes_listbox.curselection()
        if selecionado and selecionado[0] < len(self.acoes) - 1:
            idx = selecionado[0]
            self.acoes[idx], self.acoes[idx+1] = self.acoes[idx+1], self.acoes[idx]
            self.atualizar_listbox()
            self.acoes_listbox.selection_set(idx+1)
            self.modificado = True
    
    def remover_acao(self):
        selecionado = self.acoes_listbox.curselection()
        if selecionado:
            idx = selecionado[0]
            del self.acoes[idx]
            self.atualizar_listbox()
            self.modificado = True
            
            # Selecionar o próximo item após a remoção
            if idx < self.acoes_listbox.size():
                self.acoes_listbox.selection_set(idx)
            elif self.acoes_listbox.size() > 0:
                self.acoes_listbox.selection_set(idx-1)
    
    def limpar_acoes(self):
        if messagebox.askyesno("Limpar Tudo", "Tem certeza que deseja limpar todas as ações?"):
            self.acoes = []
            self.atualizar_listbox()
            self.modificado = True
    
    def executar_sequencia(self):
        if not self.acoes:
            messagebox.showinfo("Aviso", "Não há ações para executar.")
            return
        
        try:
            repeticoes = int(self.repeticoes_var.get())
            if repeticoes < 1:
                repeticoes = 1
        except ValueError:
            repeticoes = 1
            self.repeticoes_var.set("1")
        
        # Executar em uma thread separada para não congelar a interface
        threading.Thread(target=self._executar_sequencia_thread, args=(repeticoes,), daemon=True).start()
    
    def _executar_sequencia_thread(self, repeticoes=1):
        self.status_var.set(f"Executando sequência ({repeticoes} {'vez' if repeticoes == 1 else 'vezes'})...")
        
        # Dar um tempo para o usuário se preparar
        for i in range(3, 0, -1):
            self.status_var.set(f"Iniciando em {i}...")
            time.sleep(1)
        
        try:
            for rep in range(repeticoes):
                if rep > 0:
                    self.status_var.set(f"Repetição {rep+1} de {repeticoes}")
                    time.sleep(1)  # Pequena pausa entre repetições
                
                for i, acao in enumerate(self.acoes):
                    self.status_var.set(f"Executando ação {i+1} de {len(self.acoes)} (Repetição {rep+1}/{repeticoes})")
                    
                    if acao["tipo"] == "mouse":
                        # Extrair coordenadas do texto "clique em (x, y)"
                        coords = acao["valor"].replace("clique em (", "").replace(")", "").split(", ")
                        x, y = int(coords[0]), int(coords[1])
                        pyautogui.click(x, y)
                    
                    elif acao["tipo"] == "teclado":
                        if acao["valor"] == "ctrl+a":
                            pyautogui.hotkey('ctrl', 'a')
                        elif acao["valor"] == "ctrl+c":
                            pyautogui.hotkey('ctrl', 'c')
                        elif acao["valor"] == "ctrl+v":
                            pyautogui.hotkey('ctrl', 'v')
                        elif acao["valor"] == "enter":
                            pyautogui.press('enter')
                        elif acao["valor"] == "tab":
                            pyautogui.press('tab')
                        elif acao["valor"] == "esc":
                            pyautogui.press('escape')
                        elif acao["valor"] == "delete":
                            pyautogui.press('delete')
                        elif acao["valor"] == "backspace":
                            pyautogui.press('backspace')
                    
                    elif acao["tipo"] == "delay":
                        # Extrair segundos do texto "X segundos"
                        segundos = float(acao["valor"].replace(" segundos", ""))
                        time.sleep(segundos)
                    
                    elif acao["tipo"] == "texto":
                        pyautogui.write(acao["valor"])
                    
                    # Pequeno delay entre ações para evitar problemas
                    time.sleep(0.1)
            
            self.status_var.set(f"Sequência executada com sucesso! ({repeticoes} {'vez' if repeticoes == 1 else 'vezes'})")
        except Exception as e:
            self.status_var.set(f"Erro ao executar sequência: {str(e)}")
            messagebox.showerror("Erro", f"Ocorreu um erro ao executar a sequência: {str(e)}")
    
    def novo_arquivo(self):
        if self.modificado:
            resposta = messagebox.askyesnocancel("Alterações não salvas", 
                                               "Deseja salvar as alterações antes de criar um novo arquivo?")
            if resposta is None:  # Cancelar
                return
            if resposta:  # Sim
                if not self.salvar_arquivo():
                    return  # Se o salvamento falhar, não continua
        
        self.acoes = []
        self.arquivo_atual = None
        self.modificado = False
        self.atualizar_listbox()
        self.status_arquivo_var.set("Novo projeto")
        self.status_var.set("Novo arquivo criado")
    
    def abrir_arquivo(self):
        if self.modificado:
            resposta = messagebox.askyesnocancel("Alterações não salvas", 
                                               "Deseja salvar as alterações antes de abrir outro arquivo?")
            if resposta is None:  # Cancelar
                return
            if resposta:  # Sim
                if not self.salvar_arquivo():
                    return  # Se o salvamento falhar, não continua
        
        arquivo = filedialog.askopenfilename(
            title="Abrir Sequência",
            filetypes=[("Arquivos de Sequência", "*.seq"), ("Todos os Arquivos", "*.*")]
        )
        
        if not arquivo:
            return
        
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                self.acoes = dados.get('acoes', [])
            
            self.arquivo_atual = arquivo
            self.modificado = False
            self.atualizar_listbox()
            self.status_arquivo_var.set(f"Arquivo: {os.path.basename(arquivo)}")
            self.status_var.set(f"Arquivo aberto: {arquivo}")
        except Exception as e:
            messagebox.showerror("Erro ao Abrir", f"Não foi possível abrir o arquivo: {str(e)}")
    
    def salvar_arquivo(self):
        if not self.arquivo_atual:
            return self.salvar_como()
        
        try:
            dados = {
                'acoes': self.acoes
            }
            
            with open(self.arquivo_atual, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            
            self.modificado = False
            self.status_var.set(f"Arquivo salvo: {self.arquivo_atual}")
            return True
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo: {str(e)}")
            return False
    
    def salvar_como(self):
        arquivo = filedialog.asksaveasfilename(
            title="Salvar Sequência Como",
            defaultextension=".seq",
            filetypes=[("Arquivos de Sequência", "*.seq"), ("Todos os Arquivos", "*.*")]
        )
        
        if not arquivo:
            return False
        
        self.arquivo_atual = arquivo
        self.status_arquivo_var.set(f"Arquivo: {os.path.basename(arquivo)}")
        return self.salvar_arquivo()
    
    def ao_fechar(self):
        if self.modificado:
            resposta = messagebox.askyesnocancel("Alterações não salvas", 
                                               "Deseja salvar as alterações antes de sair?")
            if resposta is None:  # Cancelar
                return
            if resposta:  # Sim
                if not self.salvar_arquivo():
                    return  # Se o salvamento falhar, não fecha
        
        self.root.destroy()
    
    def mostrar_sobre(self):
        messagebox.showinfo("Sobre", 
                          "Automação de Tarefas\n\n"
                          "Um aplicativo para automatizar tarefas repetitivas com mouse e teclado.\n\n"
                          "Versão 1.2")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutomacaoApp(root)
    root.mainloop()