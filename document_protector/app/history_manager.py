"""
Módulo para gerenciamento de histórico
Contém a classe OptimizedHistoryManager que gerencia o histórico de edições
"""

import time
import cv2
import numpy as np
from PIL import ImageTk
from typing import List, Dict, Tuple, Optional, Any

class CompressedPatch:
    """
    Classe para armazenar patches comprimidos de áreas modificadas da imagem.
    Economiza memória armazenando apenas as regiões alteradas em vez da imagem inteira.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, data: np.ndarray):
        """
        Inicializa um patch comprimido.
        
        Args:
            x: Coordenada X do canto superior esquerdo do patch
            y: Coordenada Y do canto superior esquerdo do patch
            width: Largura do patch
            height: Altura do patch
            data: Dados do patch (array NumPy)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # Comprime os dados usando zlib para economizar memória
        import zlib
        self.compressed_data = zlib.compress(data.tobytes())
    
    def get_data(self) -> np.ndarray:
        """
        Descomprime e retorna os dados do patch.
        
        Returns:
            Array NumPy com os dados descomprimidos
        """
        # Descomprime os dados
        import zlib
        decompressed = zlib.decompress(self.compressed_data)
        # Reconstrói o array NumPy
        return np.frombuffer(decompressed, dtype=np.uint8).reshape(self.height, self.width)


class OptimizedHistoryManager:
    """
    Gerenciador de histórico otimizado que armazena apenas as áreas modificadas.
    Usa compressão para reduzir o consumo de memória.
    """
    
    def __init__(self, max_history: int = 20):
        """
        Inicializa o gerenciador de histórico.
        
        Args:
            max_history: Número máximo de estados a serem armazenados
        """
        self.history: List[Dict[str, Any]] = []
        self.position: int = -1
        self.max_history: int = max_history
        self.thumbnails: List[Optional[ImageTk.PhotoImage]] = []
    
    def add(self, mask: np.ndarray, image_processor, intensity: int, iterations: int):
        """
        Adiciona um novo estado ao histórico, armazenando apenas as áreas modificadas.
        
        Args:
            mask: Máscara atual
            image_processor: Processador de imagem para criar miniaturas
            intensity: Intensidade do blur
            iterations: Número de iterações do blur
        """
        # Se não estamos no final do histórico, trunca-o
        if self.position < len(self.history) - 1:
            self.history = self.history[:self.position + 1]
            self.thumbnails = self.thumbnails[:self.position + 1]
        
        # Encontra as áreas modificadas (patches)
        patches = self._find_patches(mask)
        
        # Adiciona o novo estado
        self.history.append({
            'patches': patches,
            'timestamp': time.time()
        })
        
        # Cria uma miniatura para este estado
        thumbnail = image_processor.create_thumbnail(100, 75)
        self.thumbnails.append(thumbnail)
        
        # Limita o tamanho do histórico
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.thumbnails.pop(0)
        
        self.position = len(self.history) - 1
    
    def _find_patches(self, mask: np.ndarray) -> List[CompressedPatch]:
        """
        Encontra as áreas modificadas na máscara e as comprime.
        
        Args:
            mask: Máscara atual
            
        Returns:
            Lista de patches comprimidos
        """
        if mask is None:
            return []
            
        # Encontra os contornos na máscara
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        patches = []
        for contour in contours:
            # Obtém o retângulo delimitador
            x, y, w, h = cv2.boundingRect(contour)
            
            # Extrai o patch da máscara
            patch_data = mask[y:y+h, x:x+w]
            
            # Cria um patch comprimido
            compressed_patch = CompressedPatch(x, y, w, h, patch_data)
            patches.append(compressed_patch)
        
        return patches
    
    def reconstruct_mask(self, image_shape: Tuple[int, int]) -> Optional[np.ndarray]:
        """
        Reconstrói a máscara a partir dos patches armazenados.
        
        Args:
            image_shape: Forma da imagem (altura, largura)
            
        Returns:
            Máscara reconstruída ou None se não houver histórico
        """
        if self.position < 0 or self.position >= len(self.history):
            return None
            
        # Cria uma máscara vazia
        mask = np.zeros((image_shape[0], image_shape[1]), dtype=np.uint8)
        
        # Obtém os patches do estado atual
        patches = self.history[self.position]['patches']
        
        # Reconstrói a máscara a partir dos patches
        for patch in patches:
            # Obtém os dados do patch
            patch_data = patch.get_data()
            
            # Coloca o patch na posição correta na máscara
            mask[patch.y:patch.y+patch.height, patch.x:patch.x+patch.width] = patch_data
        
        return mask
    
    def can_undo(self) -> bool:
        """
        Verifica se é possível desfazer.
        
        Returns:
            True se for possível desfazer, False caso contrário
        """
        return self.position > 0
    
    def can_redo(self) -> bool:
        """
        Verifica se é possível refazer.
        
        Returns:
            True se for possível refazer, False caso contrário
        """
        return self.position < len(self.history) - 1
    
    def undo(self, image_shape: Tuple[int, int]) -> Optional[np.ndarray]:
        """
        Desfaz a última ação.
        
        Args:
            image_shape: Forma da imagem (altura, largura)
            
        Returns:
            Máscara do estado anterior ou None se não for possível desfazer
        """
        if not self.can_undo():
            return None
        
        self.position -= 1
        return self.reconstruct_mask(image_shape)
    
    def redo(self, image_shape: Tuple[int, int]) -> Optional[np.ndarray]:
        """
        Refaz a última ação desfeita.
        
        Args:
            image_shape: Forma da imagem (altura, largura)
            
        Returns:
            Máscara do próximo estado ou None se não for possível refazer
        """
        if not self.can_redo():
            return None
        
        self.position += 1
        return self.reconstruct_mask(image_shape)
    
    def reset(self):
        """Reseta o histórico"""
        self.history = []
        self.thumbnails = []
        self.position = -1
    
    def get_thumbnail(self, index: int) -> Optional[ImageTk.PhotoImage]:
        """
        Retorna a miniatura de um estado específico.
        
        Args:
            index: Índice do estado
            
        Returns:
            Miniatura do estado ou None se o índice for inválido
        """
        if 0 <= index < len(self.thumbnails):
            return self.thumbnails[index]
        return None
    
    def get_current_thumbnail(self) -> Optional[ImageTk.PhotoImage]:
        """
        Retorna a miniatura do estado atual.
        
        Returns:
            Miniatura do estado atual ou None se não houver estado atual
        """
        return self.get_thumbnail(self.position)

