import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import time
from pynput import keyboard
import threading

class AutomacaoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automação de Tarefas")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Configuração de estilo
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50")
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabel", background="#f5f5f5", font=('Arial', 10))
        
        # Variáveis
        self.acoes = []
        self.capturando = False
        self.listener = None
        
        # Criar interface
        self.criar_interface()
        
        # Iniciar listener de teclado global
        self.iniciar_listener()
    
    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de controles
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.pack(fill=tk.X, pady=5)
        
        # Botões de controle
        ttk.Button(control_frame, text="Iniciar Captura (F8)", command=self.iniciar_captura).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Parar Captura (F9)", command=self.parar_captura).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Executar Sequência (F10)", command=self.executar_sequencia).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Limpar Tudo", command=self.limpar_acoes).pack(side=tk.LEFT, padx=5)
        
        # Frame de ações de teclado
        keyboard_frame = ttk.LabelFrame(main_frame, text="Adicionar Ações de Teclado", padding="5")
        keyboard_frame.pack(fill=tk.X, pady=5)
        
        # Botões de ações de teclado
        ttk.Button(keyboard_frame, text="Ctrl+A (Selecionar Tudo)", 
                  command=lambda: self.adicionar_acao("teclado", "ctrl+a")).pack(side=tk.LEFT, padx=5)
        ttk.Button(keyboard_frame, text="Ctrl+C (Copiar)", 
                  command=lambda: self.adicionar_acao("teclado", "ctrl+c")).pack(side=tk.LEFT, padx=5)
        ttk.Button(keyboard_frame, text="Ctrl+V (Colar)", 
                  command=lambda: self.adicionar_acao("teclado", "ctrl+v")).pack(side=tk.LEFT, padx=5)
        ttk.Button(keyboard_frame, text="Enter", 
                  command=lambda: self.adicionar_acao("teclado", "enter")).pack(side=tk.LEFT, padx=5)
        ttk.Button(keyboard_frame, text="Tab", 
                  command=lambda: self.adicionar_acao("teclado", "tab")).pack(side=tk.LEFT, padx=5)
        
        # Frame de delay
        delay_frame = ttk.Frame(main_frame, padding="5")
        delay_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(delay_frame, text="Adicionar Delay (segundos):").pack(side=tk.LEFT, padx=5)
        self.delay_var = tk.StringVar(value="0.5")
        delay_entry = ttk.Entry(delay_frame, textvariable=self.delay_var, width=5)
        delay_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(delay_frame, text="Adicionar Delay", 
                  command=self.adicionar_delay).pack(side=tk.LEFT, padx=5)
        
        # Frame de lista de ações
        list_frame = ttk.LabelFrame(main_frame, text="Sequência de Ações", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar para a lista
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Lista de ações
        self.acoes_listbox = tk.Listbox(list_frame, height=15, width=70, 
                                       yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
        self.acoes_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.acoes_listbox.yview)
        
        # Botões de edição
        edit_frame = ttk.Frame(main_frame, padding="5")
        edit_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(edit_frame, text="Mover Para Cima", 
                  command=self.mover_para_cima).pack(side=tk.LEFT, padx=5)
        ttk.Button(edit_frame, text="Mover Para Baixo", 
                  command=self.mover_para_baixo).pack(side=tk.LEFT, padx=5)
        ttk.Button(edit_frame, text="Remover Ação", 
                  command=self.remover_acao).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Instruções
        instrucoes = """
        Durante a captura:
        - Pressione T para capturar a posição atual do mouse
        - Pressione A para adicionar ação 'Selecionar Tudo'
        - Pressione C para adicionar ação 'Copiar'
        - Pressione V para adicionar ação 'Colar'
        """
        ttk.Label(main_frame, text=instrucoes, font=('Arial', 9, 'italic')).pack(pady=5)
    
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
        self.status_var.set("Capturando... Use T para posição do mouse, A/C/V para ações de teclado")
        messagebox.showinfo("Captura Iniciada", 
                           "Captura iniciada!\n\n"
                           "- Pressione T para capturar a posição atual do mouse\n"
                           "- Pressione A para adicionar ação 'Selecionar Tudo'\n"
                           "- Pressione C para adicionar ação 'Copiar'\n"
                           "- Pressione V para adicionar ação 'Colar'")
    
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
        
        # Selecionar a ação recém-adicionada na lista
        self.acoes_listbox.selection_clear(0, tk.END)
        self.acoes_listbox.selection_set(tk.END)
        self.acoes_listbox.see(tk.END)
    
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
            if acao["tipo"] == "mouse":
                self.acoes_listbox.insert(tk.END, f"{i+1}. Mouse: {acao['valor']}")
            elif acao["tipo"] == "teclado":
                self.acoes_listbox.insert(tk.END, f"{i+1}. Teclado: {acao['valor']}")
            elif acao["tipo"] == "delay":
                self.acoes_listbox.insert(tk.END, f"{i+1}. Delay: {acao['valor']}")
    
    def mover_para_cima(self):
        selecionado = self.acoes_listbox.curselection()
        if selecionado and selecionado[0] > 0:
            idx = selecionado[0]
            self.acoes[idx], self.acoes[idx-1] = self.acoes[idx-1], self.acoes[idx]
            self.atualizar_listbox()
            self.acoes_listbox.selection_set(idx-1)
    
    def mover_para_baixo(self):
        selecionado = self.acoes_listbox.curselection()
        if selecionado and selecionado[0] < len(self.acoes) - 1:
            idx = selecionado[0]
            self.acoes[idx], self.acoes[idx+1] = self.acoes[idx+1], self.acoes[idx]
            self.atualizar_listbox()
            self.acoes_listbox.selection_set(idx+1)
    
    def remover_acao(self):
        selecionado = self.acoes_listbox.curselection()
        if selecionado:
            idx = selecionado[0]
            del self.acoes[idx]
            self.atualizar_listbox()
            
            # Selecionar o próximo item após a remoção
            if idx < self.acoes_listbox.size():
                self.acoes_listbox.selection_set(idx)
            elif self.acoes_listbox.size() > 0:
                self.acoes_listbox.selection_set(idx-1)
    
    def limpar_acoes(self):
        if messagebox.askyesno("Limpar Tudo", "Tem certeza que deseja limpar todas as ações?"):
            self.acoes = []
            self.atualizar_listbox()
    
    def executar_sequencia(self):
        if not self.acoes:
            messagebox.showinfo("Aviso", "Não há ações para executar.")
            return
        
        # Executar em uma thread separada para não congelar a interface
        threading.Thread(target=self._executar_sequencia_thread, daemon=True).start()
    
    def _executar_sequencia_thread(self):
        self.status_var.set("Executando sequência...")
        
        # Dar um tempo para o usuário se preparar
        for i in range(3, 0, -1):
            self.status_var.set(f"Iniciando em {i}...")
            time.sleep(1)
        
        try:
            for i, acao in enumerate(self.acoes):
                self.status_var.set(f"Executando ação {i+1} de {len(self.acoes)}")
                
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
                
                elif acao["tipo"] == "delay":
                    # Extrair segundos do texto "X segundos"
                    segundos = float(acao["valor"].replace(" segundos", ""))
                    time.sleep(segundos)
                
                # Pequeno delay entre ações para evitar problemas
                time.sleep(0.1)
            
            self.status_var.set("Sequência executada com sucesso!")
        except Exception as e:
            self.status_var.set(f"Erro ao executar sequência: {str(e)}")
            messagebox.showerror("Erro", f"Ocorreu um erro ao executar a sequência: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutomacaoApp(root)
    root.mainloop()