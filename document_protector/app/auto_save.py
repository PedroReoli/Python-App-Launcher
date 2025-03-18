"""
Módulo para gerenciamento de salvamento automático
Contém a classe AutoSaveManager que gerencia o salvamento automático
Versão 2.0 - Melhor gerenciamento de threads e opções de configuração
"""

import threading
import time
from typing import Callable, Optional

class AutoSaveManager:
    """
    Gerenciador de salvamento automático.
    Salva a imagem em intervalos regulares.
    """
    
    def __init__(self, callback: Callable, interval_minutes: int = 5):
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
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self._lock = threading.Lock()  # Para acesso thread-safe às variáveis
    
    def start(self):
        """Inicia o salvamento automático"""
        with self._lock:
            self.enabled = True
            self.running = True
            self.last_save = time.time()
            
            # Cria uma nova thread apenas se não houver uma em execução
            if self.thread is None or not self.thread.is_alive():
                self.thread = threading.Thread(target=self._auto_save_loop)
                self.thread.daemon = True
                self.thread.start()
    
    def stop(self):
        """Para o salvamento automático"""
        with self._lock:
            self.enabled = False
            self.running = False
            
            # Aguarda a thread terminar
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=1)
                self.thread = None
    
    def _auto_save_loop(self):
        """Loop de salvamento automático"""
        while True:
            # Verifica se deve continuar executando
            with self._lock:
                if not self.running:
                    break
                
                current_time = time.time()
                should_save = self.enabled and (current_time - self.last_save >= self.interval)
            
            # Executa o salvamento fora do lock para não bloquear outras operações
            if should_save:
                try:
                    self.callback()
                    with self._lock:
                        self.last_save = time.time()
                except Exception as e:
                    print(f"Erro no salvamento automático: {e}")
            
            # Aguarda um pouco antes de verificar novamente
            time.sleep(1)
    
    def set_interval(self, minutes: int):
        """
        Define o intervalo de salvamento.
        
        Args:
            minutes: Intervalo em minutos
        """
        with self._lock:
            self.interval = max(1, minutes) * 60  # Mínimo de 1 minuto
    
    def is_enabled(self) -> bool:
        """
        Verifica se o salvamento automático está ativado.
        
        Returns:
            True se o salvamento automático estiver ativado, False caso contrário
        """
        with self._lock:
            return self.enabled
    
    def get_interval(self) -> int:
        """
        Obtém o intervalo de salvamento em minutos.
        
        Returns:
            Intervalo de salvamento em minutos
        """
        with self._lock:
            return self.interval // 60
    
    def get_time_until_next_save(self) -> int:
        """
        Obtém o tempo restante até o próximo salvamento em segundos.
        
        Returns:
            Tempo restante em segundos
        """
        with self._lock:
            if not self.enabled:
                return -1
            
            elapsed = time.time() - self.last_save
            remaining = max(0, self.interval - elapsed)
            return int(remaining)

