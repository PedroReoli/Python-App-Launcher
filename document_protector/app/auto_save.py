"""
Módulo para gerenciamento de salvamento automático
Contém a classe AutoSaveManager que gerencia o salvamento automático
"""

import threading
import time

class AutoSaveManager:
    """
    Gerenciador de salvamento automático.
    Salva a imagem em intervalos regulares.
    """
    
    def __init__(self, callback, interval_minutes: int = 5):
        """
        Inicializa o gerenciador de salvamento automático.
        
        Args:
            callback: Função a ser chamada para salvar a imagem
            interval_minutes: Intervalo entre salvamentos em minutos
        """
        self.callback = callback
        self.interval = interval_minutes * 60  # Converte para segundos
        self.enabled = False
        self.last_save = time.time()
        self.thread = None
        self.running = False
    
    def start(self):
        """Inicia o salvamento automático"""
        self.enabled = True
        self.running = True
        self.last_save = time.time()
        self.thread = threading.Thread(target=self._auto_save_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Para o salvamento automático"""
        self.enabled = False
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _auto_save_loop(self):
        """Loop de salvamento automático"""
        while self.running:
            time.sleep(1)  # Verifica a cada segundo
            if not self.enabled:
                continue
                
            current_time = time.time()
            if current_time - self.last_save >= self.interval:
                self.callback()
                self.last_save = current_time
    
    def set_interval(self, minutes: int):
        """
        Define o intervalo de salvamento.
        
        Args:
            minutes: Intervalo em minutos
        """
        self.interval = max(1, minutes) * 60  # Mínimo de 1 minuto

