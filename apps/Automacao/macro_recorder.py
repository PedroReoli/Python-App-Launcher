#!/usr/bin/env python3
"""
Macro Recorder - Aplicativo de Automação de Cliques e Macros
Captura e reproduz rotinas de cliques, teclas e movimentos do mouse
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import time
import threading
import os
from datetime import datetime
from typing import List, Dict, Any
import pyautogui
import keyboard
import mouse
from dataclasses import dataclass, asdict
import pickle

# Configurar PyAutoGUI para ser mais seguro
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

@dataclass
class MacroAction:
    """Representa uma ação da macro"""
    action_type: str  # 'click', 'key', 'move', 'scroll', 'wait'
    x: int = 0
    y: int = 0
    button: str = 'left'
    key: str = ''
    text: str = ''
    duration: float = 0.0
    timestamp: float = 0.0
    description: str = ''

class MacroRecorder:
    """Gravador e reprodutor de macros"""
    
    def __init__(self):
        self.recording = False
        self.playing = False
        self.actions: List[MacroAction] = []
        self.recording_thread = None
        self.playing_thread = None
        self.start_time = 0
        
    def start_recording(self):
        """Inicia a gravação de macro"""
        if self.recording:
            return False
            
        self.recording = True
        self.actions = []
        self.start_time = time.time()
        
        # Iniciar thread de gravação
        self.recording_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.recording_thread.start()
        
        return True
        
    def stop_recording(self):
        """Para a gravação de macro"""
        self.recording = False
        if self.recording_thread:
            self.recording_thread.join(timeout=1)
            
    def _record_loop(self):
        """Loop principal de gravação"""
        try:
            # Configurar hooks para capturar eventos
            mouse.hook(self._on_mouse_event)
            keyboard.hook(self._on_keyboard_event)
            
            # Aguardar até parar a gravação
            while self.recording:
                time.sleep(0.01)
                
        except Exception as e:
            print(f"Erro na gravação: {e}")
        finally:
            # Remover hooks
            mouse.unhook_all()
            keyboard.unhook_all()
            
    def _on_mouse_event(self, event):
        """Captura eventos do mouse"""
        if not self.recording:
            return
            
        current_time = time.time() - self.start_time
        
        if hasattr(event, 'event_type'):
            if event.event_type == 'down':
                if hasattr(event, 'button'):
                    action = MacroAction(
                        action_type='click',
                        x=event.x,
                        y=event.y,
                        button=event.button,
                        timestamp=current_time,
                        description=f"Clique {event.button} em ({event.x}, {event.y})"
                    )
                    self.actions.append(action)
                    
            elif event.event_type == 'move':
                # Capturar movimento apenas se for significativo
                if self.actions and self.actions[-1].action_type == 'move':
                    last_action = self.actions[-1]
                    if abs(event.x - last_action.x) < 5 and abs(event.y - last_action.y) < 5:
                        return
                        
                action = MacroAction(
                    action_type='move',
                    x=event.x,
                    y=event.y,
                    timestamp=current_time,
                    description=f"Movimento para ({event.x}, {event.y})"
                )
                self.actions.append(action)
                
            elif event.event_type == 'wheel':
                action = MacroAction(
                    action_type='scroll',
                    x=event.x,
                    y=event.y,
                    duration=event.delta,
                    timestamp=current_time,
                    description=f"Scroll {event.delta} em ({event.x}, {event.y})"
                )
                self.actions.append(action)
                
    def _on_keyboard_event(self, event):
        """Captura eventos do teclado"""
        if not self.recording:
            return
            
        current_time = time.time() - self.start_time
        
        if event.event_type == 'down':
            # Ignorar teclas especiais de controle
            if event.name in ['esc', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12']:
                return
                
            action = MacroAction(
                action_type='key',
                key=event.name,
                timestamp=current_time,
                description=f"Tecla {event.name}"
            )
            self.actions.append(action)
            
    def play_macro(self, repeat_count: int = 1, delay: float = 0.0):
        """Reproduz a macro gravada"""
        if self.playing or not self.actions:
            return False
            
        self.playing = True
        
        # Iniciar thread de reprodução
        self.playing_thread = threading.Thread(
            target=self._play_loop, 
            args=(repeat_count, delay),
            daemon=True
        )
        self.playing_thread.start()
        
        return True
        
    def stop_playing(self):
        """Para a reprodução da macro"""
        self.playing = False
        if self.playing_thread:
            self.playing_thread.join(timeout=1)
            
    def _play_loop(self, repeat_count: int, delay: float):
        """Loop principal de reprodução"""
        try:
            for repeat in range(repeat_count):
                if not self.playing:
                    break
                    
                print(f"Reproduzindo macro - Repetição {repeat + 1}/{repeat_count}")
                
                for i, action in enumerate(self.actions):
                    if not self.playing:
                        break
                        
                    # Aguardar tempo entre ações
                    if i > 0:
                        wait_time = action.timestamp - self.actions[i-1].timestamp
                        if wait_time > 0:
                            time.sleep(wait_time)
                            
                    # Executar ação
                    self._execute_action(action)
                    
                # Aguardar delay entre repetições
                if repeat < repeat_count - 1 and delay > 0:
                    time.sleep(delay)
                    
        except Exception as e:
            print(f"Erro na reprodução: {e}")
        finally:
            self.playing = False
            
    def _execute_action(self, action: MacroAction):
        """Executa uma ação específica"""
        try:
            if action.action_type == 'click':
                pyautogui.click(action.x, action.y, button=action.button)
                
            elif action.action_type == 'move':
                pyautogui.moveTo(action.x, action.y)
                
            elif action.action_type == 'key':
                pyautogui.press(action.key)
                
            elif action.action_type == 'scroll':
                pyautogui.scroll(int(action.duration))
                
            elif action.action_type == 'wait':
                time.sleep(action.duration)
                
        except Exception as e:
            print(f"Erro ao executar ação {action.description}: {e}")
            
    def save_macro(self, filename: str):
        """Salva a macro em arquivo"""
        try:
            data = {
                'name': os.path.splitext(os.path.basename(filename))[0],
                'created': datetime.now().isoformat(),
                'actions': [asdict(action) for action in self.actions],
                'total_actions': len(self.actions)
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Erro ao salvar macro: {e}")
            return False
            
    def load_macro(self, filename: str):
        """Carrega macro de arquivo"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.actions = []
            for action_data in data.get('actions', []):
                action = MacroAction(**action_data)
                self.actions.append(action)
                
            return True
            
        except Exception as e:
            print(f"Erro ao carregar macro: {e}")
            return False
            
    def clear_macro(self):
        """Limpa a macro atual"""
        self.actions = []
        
    def get_action_count(self) -> int:
        """Retorna o número de ações na macro"""
        return len(self.actions)
        
    def get_duration(self) -> float:
        """Retorna a duração total da macro"""
        if not self.actions:
            return 0.0
        return self.actions[-1].timestamp

class MacroRecorderGUI:
    """Interface gráfica do gravador de macros"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Macro Recorder - Gravador de Automação")
        self.root.geometry("800x600")
        
        self.recorder = MacroRecorder()
        self.setup_ui()
        self.update_status()
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Macro Recorder - Gravador de Automação",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botões de gravação
        recording_frame = ttk.Frame(controls_frame)
        recording_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.record_button = ttk.Button(
            recording_frame,
            text="🔴 Iniciar Gravação",
            command=self.start_recording,
            style="Accent.TButton"
        )
        self.record_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_record_button = ttk.Button(
            recording_frame,
            text="⏹️ Parar Gravação",
            command=self.stop_recording,
            state=tk.DISABLED
        )
        self.stop_record_button.pack(side=tk.LEFT)
        
        # Botões de reprodução
        playback_frame = ttk.Frame(controls_frame)
        playback_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(playback_frame, text="Repetições:").pack(side=tk.LEFT)
        
        self.repeat_var = tk.StringVar(value="1")
        repeat_spinbox = ttk.Spinbox(
            playback_frame,
            from_=1,
            to=100,
            width=5,
            textvariable=self.repeat_var
        )
        repeat_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(playback_frame, text="Delay (s):").pack(side=tk.LEFT)
        
        self.delay_var = tk.StringVar(value="0.0")
        delay_spinbox = ttk.Spinbox(
            playback_frame,
            from_=0.0,
            to=60.0,
            increment=0.1,
            width=5,
            textvariable=self.delay_var
        )
        delay_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        self.play_button = ttk.Button(
            playback_frame,
            text="▶️ Reproduzir Macro",
            command=self.play_macro
        )
        self.play_button.pack(side=tk.LEFT, padx=(10, 0))
        
        self.stop_play_button = ttk.Button(
            playback_frame,
            text="⏹️ Parar Reprodução",
            command=self.stop_playing,
            state=tk.DISABLED
        )
        self.stop_play_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Botões de arquivo
        file_frame = ttk.Frame(controls_frame)
        file_frame.pack(fill=tk.X)
        
        self.save_button = ttk.Button(
            file_frame,
            text="💾 Salvar Macro",
            command=self.save_macro
        )
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.load_button = ttk.Button(
            file_frame,
            text="📂 Carregar Macro",
            command=self.load_macro
        )
        self.load_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(
            file_frame,
            text="🗑️ Limpar Macro",
            command=self.clear_macro
        )
        self.clear_button.pack(side=tk.LEFT)
        
        # Frame de informações
        info_frame = ttk.LabelFrame(main_frame, text="Informações da Macro", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_inner_frame = ttk.Frame(info_frame)
        info_inner_frame.pack(fill=tk.X)
        
        self.action_count_label = ttk.Label(info_inner_frame, text="Ações: 0")
        self.action_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.duration_label = ttk.Label(info_inner_frame, text="Duração: 0.0s")
        self.duration_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.status_label = ttk.Label(info_inner_frame, text="Status: Pronto")
        self.status_label.pack(side=tk.LEFT)
        
        # Lista de ações
        actions_frame = ttk.LabelFrame(main_frame, text="Ações Gravadas", padding="10")
        actions_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para mostrar ações
        columns = ('timestamp', 'type', 'description')
        self.actions_tree = ttk.Treeview(actions_frame, columns=columns, show='headings')
        
        self.actions_tree.heading('timestamp', text='Tempo (s)')
        self.actions_tree.heading('type', text='Tipo')
        self.actions_tree.heading('description', text='Descrição')
        
        self.actions_tree.column('timestamp', width=80)
        self.actions_tree.column('type', width=100)
        self.actions_tree.column('description', width=400)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(actions_frame, orient=tk.VERTICAL, command=self.actions_tree.yview)
        self.actions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.actions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Barra de status
        self.status_bar = ttk.Label(
            self.root,
            text="Pronto para gravar macros",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def start_recording(self):
        """Inicia a gravação"""
        if self.recorder.start_recording():
            self.record_button.config(state=tk.DISABLED)
            self.stop_record_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Gravando...")
            self.status_bar.config(text="Gravando macro... Pressione 'Parar Gravação' para finalizar")
            
            # Atualizar lista de ações em tempo real
            self.update_actions_list()
            
    def stop_recording(self):
        """Para a gravação"""
        self.recorder.stop_recording()
        self.record_button.config(state=tk.NORMAL)
        self.stop_record_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Pronto")
        self.status_bar.config(text="Gravação finalizada")
        
        self.update_status()
        self.update_actions_list()
        
    def play_macro(self):
        """Reproduz a macro"""
        if not self.recorder.actions:
            messagebox.showwarning("Aviso", "Nenhuma macro para reproduzir")
            return
            
        try:
            repeat_count = int(self.repeat_var.get())
            delay = float(self.delay_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos para repetições ou delay")
            return
            
        if self.recorder.play_macro(repeat_count, delay):
            self.play_button.config(state=tk.DISABLED)
            self.stop_play_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Reproduzindo...")
            self.status_bar.config(text=f"Reproduzindo macro ({repeat_count} repetições)")
            
            # Atualizar status durante reprodução
            self.update_playback_status()
            
    def stop_playing(self):
        """Para a reprodução"""
        self.recorder.stop_playing()
        self.play_button.config(state=tk.NORMAL)
        self.stop_play_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Pronto")
        self.status_bar.config(text="Reprodução interrompida")
        
    def save_macro(self):
        """Salva a macro"""
        if not self.recorder.actions:
            messagebox.showwarning("Aviso", "Nenhuma macro para salvar")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".macro",
            filetypes=[
                ("Arquivos Macro", "*.macro"),
                ("Arquivos JSON", "*.json"),
                ("Todos os arquivos", "*.*")
            ],
            title="Salvar Macro"
        )
        
        if filename:
            if self.recorder.save_macro(filename):
                messagebox.showinfo("Sucesso", f"Macro salva em:\n{filename}")
                self.status_bar.config(text=f"Macro salva: {os.path.basename(filename)}")
            else:
                messagebox.showerror("Erro", "Falha ao salvar macro")
                
    def load_macro(self):
        """Carrega uma macro"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Arquivos Macro", "*.macro"),
                ("Arquivos JSON", "*.json"),
                ("Todos os arquivos", "*.*")
            ],
            title="Carregar Macro"
        )
        
        if filename:
            if self.recorder.load_macro(filename):
                messagebox.showinfo("Sucesso", f"Macro carregada de:\n{filename}")
                self.status_bar.config(text=f"Macro carregada: {os.path.basename(filename)}")
                self.update_status()
                self.update_actions_list()
            else:
                messagebox.showerror("Erro", "Falha ao carregar macro")
                
    def clear_macro(self):
        """Limpa a macro atual"""
        if self.recorder.actions:
            if messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar a macro atual?"):
                self.recorder.clear_macro()
                self.update_status()
                self.update_actions_list()
                self.status_bar.config(text="Macro limpa")
                
    def update_status(self):
        """Atualiza as informações de status"""
        action_count = self.recorder.get_action_count()
        duration = self.recorder.get_duration()
        
        self.action_count_label.config(text=f"Ações: {action_count}")
        self.duration_label.config(text=f"Duração: {duration:.2f}s")
        
    def update_actions_list(self):
        """Atualiza a lista de ações"""
        # Limpar lista atual
        for item in self.actions_tree.get_children():
            self.actions_tree.delete(item)
            
        # Adicionar ações
        for action in self.recorder.actions:
            self.actions_tree.insert('', tk.END, values=(
                f"{action.timestamp:.2f}",
                action.action_type,
                action.description
            ))
            
    def update_playback_status(self):
        """Atualiza o status durante reprodução"""
        if self.recorder.playing:
            self.root.after(100, self.update_playback_status)
        else:
            self.play_button.config(state=tk.NORMAL)
            self.stop_play_button.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Pronto")
            self.status_bar.config(text="Reprodução finalizada")

def main():
    """Função principal"""
    root = tk.Tk()
    app = MacroRecorderGUI(root)
    
    # Configurar tecla de emergência
    def emergency_stop():
        app.recorder.stop_recording()
        app.recorder.stop_playing()
        app.record_button.config(state=tk.NORMAL)
        app.stop_record_button.config(state=tk.DISABLED)
        app.play_button.config(state=tk.NORMAL)
        app.stop_play_button.config(state=tk.DISABLED)
        app.status_label.config(text="Status: Parado de Emergência")
        app.status_bar.config(text="Parado de emergência (F12)")
        
    # Bind F12 para parada de emergência
    root.bind('<F12>', lambda e: emergency_stop())
    
    # Mostrar informações de uso
    print("=== Macro Recorder ===")
    print("🔴 Inicie a gravação e execute suas ações")
    print("⏹️ Pare a gravação quando terminar")
    print("▶️ Reproduza a macro quantas vezes quiser")
    print("💾 Salve suas macros para uso futuro")
    print("⚠️ Pressione F12 para parada de emergência")
    print("=====================")
    
    root.mainloop()

if __name__ == "__main__":
    main() 