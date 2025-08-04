import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pyautogui
import keyboard
import threading
import time
import json
import os
from datetime import datetime

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker - Automatizador de Cliques")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configurações do PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Variáveis de controle
        self.is_running = False
        self.click_sequence = []
        self.current_sequence = []
        self.hotkey_stop = 'ctrl+alt+s'
        
        # Configurar hotkey para parar
        keyboard.add_hotkey(self.hotkey_stop, self.stop_automation)
        
        self.setup_ui()
        self.load_saved_sequences()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Auto Clicker - Automatizador de Cliques", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de configurações
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Delay entre cliques
        ttk.Label(config_frame, text="Delay entre cliques (segundos):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.delay_var = tk.StringVar(value="1.0")
        self.delay_entry = ttk.Entry(config_frame, textvariable=self.delay_var, width=10)
        self.delay_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Número de repetições
        ttk.Label(config_frame, text="Número de repetições:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.repetitions_var = tk.StringVar(value="1")
        self.repetitions_entry = ttk.Entry(config_frame, textvariable=self.repetitions_var, width=10)
        self.repetitions_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Delay entre repetições
        ttk.Label(config_frame, text="Delay entre repetições (segundos):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.repetition_delay_var = tk.StringVar(value="2.0")
        self.repetition_delay_entry = ttk.Entry(config_frame, textvariable=self.repetition_delay_var, width=10)
        self.repetition_delay_entry.grid(row=2, column=1, sticky=tk.W, pady=(10, 0))
        
        # Frame de captura de coordenadas
        capture_frame = ttk.LabelFrame(main_frame, text="Captura de Coordenadas", padding="10")
        capture_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        capture_frame.columnconfigure(1, weight=1)
        
        # Botão para capturar coordenadas
        self.capture_btn = ttk.Button(capture_frame, text="Iniciar Captura (F6)", 
                                     command=self.start_coordinate_capture)
        self.capture_btn.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Botão para parar captura
        self.stop_capture_btn = ttk.Button(capture_frame, text="Parar Captura", 
                                          command=self.stop_coordinate_capture, state=tk.DISABLED)
        self.stop_capture_btn.grid(row=0, column=2, columnspan=1, pady=(0, 10))
        
        # Lista de coordenadas capturadas
        ttk.Label(capture_frame, text="Coordenadas capturadas:").grid(row=1, column=0, sticky=tk.W)
        
        # Frame para a lista de coordenadas
        list_frame = ttk.Frame(capture_frame)
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview para mostrar coordenadas
        columns = ('index', 'x', 'y', 'delay')
        self.coordinates_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        
        self.coordinates_tree.heading('index', text='#')
        self.coordinates_tree.heading('x', text='X')
        self.coordinates_tree.heading('y', text='Y')
        self.coordinates_tree.heading('delay', text='Delay (s)')
        
        self.coordinates_tree.column('index', width=50)
        self.coordinates_tree.column('x', width=100)
        self.coordinates_tree.column('y', width=100)
        self.coordinates_tree.column('delay', width=100)
        
        self.coordinates_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para a lista
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.coordinates_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.coordinates_tree.configure(yscrollcommand=scrollbar.set)
        
        # Botões para gerenciar coordenadas
        btn_frame = ttk.Frame(capture_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Remover Selecionado", 
                  command=self.remove_selected_coordinate).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Limpar Todas", 
                  command=self.clear_coordinates).pack(side=tk.LEFT)
        
        # Frame de controle
        control_frame = ttk.LabelFrame(main_frame, text="Controle de Automação", padding="10")
        control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botões de controle
        self.start_btn = ttk.Button(control_frame, text="Iniciar Automação (F7)", 
                                   command=self.start_automation, style="Accent.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="Parar Automação (Ctrl+Alt+S)", 
                                  command=self.stop_automation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status
        self.status_var = tk.StringVar(value="Pronto para capturar coordenadas")
        self.status_label = ttk.Label(control_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Frame de sequências salvas
        sequences_frame = ttk.LabelFrame(main_frame, text="Sequências Salvas", padding="10")
        sequences_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        sequences_frame.columnconfigure(0, weight=1)
        sequences_frame.rowconfigure(1, weight=1)
        
        # Lista de sequências
        ttk.Label(sequences_frame, text="Sequências disponíveis:").grid(row=0, column=0, sticky=tk.W)
        
        self.sequences_listbox = tk.Listbox(sequences_frame, height=4)
        self.sequences_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        # Botões para sequências
        seq_btn_frame = ttk.Frame(sequences_frame)
        seq_btn_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(seq_btn_frame, text="Salvar Sequência", 
                  command=self.save_sequence).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(seq_btn_frame, text="Carregar Sequência", 
                  command=self.load_sequence).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(seq_btn_frame, text="Deletar Sequência", 
                  command=self.delete_sequence).pack(side=tk.LEFT)
        
        # Configurar hotkeys
        keyboard.add_hotkey('f6', self.start_coordinate_capture)
        keyboard.add_hotkey('f7', self.start_automation)
        
        # Configurar grid weights para expansão
        main_frame.rowconfigure(4, weight=1)
        
    def start_coordinate_capture(self):
        """Inicia o modo de captura de coordenadas"""
        if self.is_running:
            messagebox.showwarning("Aviso", "Pare a automação atual antes de capturar coordenadas")
            return
            
        self.status_var.set("Pressione F6 para capturar coordenadas. Clique com o mouse para capturar posições.")
        self.capture_btn.config(state=tk.DISABLED)
        self.stop_capture_btn.config(state=tk.NORMAL)
        
        # Configurar captura de cliques do mouse
        keyboard.add_hotkey('f6', self.capture_coordinate, suppress=True)
        
        # Variável para controlar se está capturando
        self.is_capturing = True
        
    def capture_coordinate(self):
        """Captura a posição atual do mouse"""
        # Verificar se já está capturando para evitar duplicatas
        if not hasattr(self, 'is_capturing') or not self.is_capturing:
            return
            
        # Desabilitar temporariamente para evitar múltiplas capturas
        self.is_capturing = False
        
        x, y = pyautogui.position()
        
        # Adicionar à lista
        index = len(self.current_sequence) + 1
        delay = float(self.delay_var.get())
        
        self.current_sequence.append({
            'index': index,
            'x': x,
            'y': y,
            'delay': delay
        })
        
        # Atualizar treeview
        self.coordinates_tree.insert('', 'end', values=(index, x, y, delay))
        
        self.status_var.set(f"Coordenada {index} capturada: ({x}, {y})")
        
        # Reabilitar captura após um pequeno delay
        self.root.after(500, self.enable_capture)
        
    def enable_capture(self):
        """Reabilita a captura de coordenadas"""
        self.is_capturing = True
        
    def stop_coordinate_capture(self):
        """Para o modo de captura de coordenadas"""
        self.is_capturing = False
        self.capture_btn.config(state=tk.NORMAL)
        self.stop_capture_btn.config(state=tk.DISABLED)
        self.status_var.set("Captura de coordenadas parada")
        
        # Remover hotkey
        try:
            keyboard.remove_hotkey('f6')
        except:
            pass
        
    def remove_selected_coordinate(self):
        """Remove a coordenada selecionada da lista"""
        selection = self.coordinates_tree.selection()
        if selection:
            item = self.coordinates_tree.item(selection[0])
            index = item['values'][0] - 1
            
            # Remover da lista
            if 0 <= index < len(self.current_sequence):
                self.current_sequence.pop(index)
            
            # Remover da treeview
            self.coordinates_tree.delete(selection[0])
            
            # Reindexar
            self.reindex_coordinates()
            
    def clear_coordinates(self):
        """Limpa todas as coordenadas"""
        self.current_sequence.clear()
        for item in self.coordinates_tree.get_children():
            self.coordinates_tree.delete(item)
            
    def reindex_coordinates(self):
        """Reindexa as coordenadas após remoção"""
        for i, coord in enumerate(self.current_sequence):
            coord['index'] = i + 1
            
        # Atualizar treeview
        for i, item in enumerate(self.coordinates_tree.get_children()):
            values = list(self.coordinates_tree.item(item)['values'])
            values[0] = i + 1
            self.coordinates_tree.item(item, values=values)
            
    def start_automation(self):
        """Inicia a automação de cliques"""
        if not self.current_sequence:
            messagebox.showwarning("Aviso", "Capture pelo menos uma coordenada antes de iniciar")
            return
            
        try:
            delay = float(self.delay_var.get())
            repetitions = int(self.repetitions_var.get())
            repetition_delay = float(self.repetition_delay_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos para delay ou repetições")
            return
            
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.capture_btn.config(state=tk.DISABLED)
        
        # Iniciar thread de automação
        self.automation_thread = threading.Thread(target=self.run_automation, 
                                               args=(delay, repetitions, repetition_delay))
        self.automation_thread.daemon = True
        self.automation_thread.start()
        
    def run_automation(self, delay, repetitions, repetition_delay):
        """Executa a automação em thread separada"""
        try:
            for rep in range(repetitions):
                if not self.is_running:
                    break
                    
                self.status_var.set(f"Executando repetição {rep + 1}/{repetitions}")
                
                for i, coord in enumerate(self.current_sequence):
                    if not self.is_running:
                        break
                        
                    # Mover mouse e clicar
                    pyautogui.click(coord['x'], coord['y'])
                    
                    # Aguardar delay (exceto no último clique)
                    if i < len(self.current_sequence) - 1:
                        time.sleep(delay)
                        
                # Aguardar entre repetições (exceto na última)
                if rep < repetitions - 1 and self.is_running:
                    time.sleep(repetition_delay)
                    
            if self.is_running:
                self.status_var.set("Automação concluída")
                self.root.after(0, self.automation_finished)
                
        except Exception as e:
            self.status_var.set(f"Erro na automação: {str(e)}")
            self.root.after(0, self.automation_finished)
            
    def stop_automation(self):
        """Para a automação"""
        self.is_running = False
        self.status_var.set("Automação interrompida")
        self.automation_finished()
        
    def automation_finished(self):
        """Chamado quando a automação termina"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.capture_btn.config(state=tk.NORMAL)
        self.stop_capture_btn.config(state=tk.DISABLED)
        
    def save_sequence(self):
        """Salva a sequência atual"""
        if not self.current_sequence:
            messagebox.showwarning("Aviso", "Não há coordenadas para salvar")
            return
            
        name = tk.simpledialog.askstring("Salvar Sequência", "Nome da sequência:")
        if name:
            sequence_data = {
                'name': name,
                'coordinates': self.current_sequence,
                'delay': self.delay_var.get(),
                'repetitions': self.repetitions_var.get(),
                'repetition_delay': self.repetition_delay_var.get(),
                'created': datetime.now().isoformat()
            }
            
            # Salvar no arquivo
            self.save_sequence_to_file(sequence_data)
            self.load_saved_sequences()
            
    def save_sequence_to_file(self, sequence_data):
        """Salva a sequência no arquivo JSON"""
        sequences = self.load_all_sequences()
        sequences[sequence_data['name']] = sequence_data
        
        with open('saved_sequences.json', 'w', encoding='utf-8') as f:
            json.dump(sequences, f, indent=2, ensure_ascii=False)
            
    def load_all_sequences(self):
        """Carrega todas as sequências salvas"""
        try:
            with open('saved_sequences.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def load_saved_sequences(self):
        """Carrega a lista de sequências salvas"""
        sequences = self.load_all_sequences()
        
        self.sequences_listbox.delete(0, tk.END)
        for name in sequences.keys():
            self.sequences_listbox.insert(tk.END, name)
            
    def load_sequence(self):
        """Carrega uma sequência salva"""
        selection = self.sequences_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma sequência para carregar")
            return
            
        name = self.sequences_listbox.get(selection[0])
        sequences = self.load_all_sequences()
        
        if name in sequences:
            sequence = sequences[name]
            
            # Carregar coordenadas
            self.current_sequence = sequence['coordinates']
            
            # Limpar e recarregar treeview
            for item in self.coordinates_tree.get_children():
                self.coordinates_tree.delete(item)
                
            for coord in self.current_sequence:
                self.coordinates_tree.insert('', 'end', values=(
                    coord['index'], coord['x'], coord['y'], coord['delay']
                ))
                
            # Carregar configurações
            self.delay_var.set(sequence.get('delay', '1.0'))
            self.repetitions_var.set(sequence.get('repetitions', '1'))
            self.repetition_delay_var.set(sequence.get('repetition_delay', '2.0'))
            
            self.status_var.set(f"Sequência '{name}' carregada")
            
    def delete_sequence(self):
        """Deleta uma sequência salva"""
        selection = self.sequences_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma sequência para deletar")
            return
            
        name = self.sequences_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirmar", f"Deseja deletar a sequência '{name}'?"):
            sequences = self.load_all_sequences()
            if name in sequences:
                del sequences[name]
                
                with open('saved_sequences.json', 'w', encoding='utf-8') as f:
                    json.dump(sequences, f, indent=2, ensure_ascii=False)
                    
                self.load_saved_sequences()
                self.status_var.set(f"Sequência '{name}' deletada")

def main():
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 