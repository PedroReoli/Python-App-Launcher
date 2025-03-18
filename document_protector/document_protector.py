import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import json
import threading
import time
import zlib
from typing import Dict, List, Tuple, Optional, Any, Union
import re
import io
import base64

# Tente importar as bibliotecas opcionais
try:
    import pytesseract
    # Configuração do Tesseract OCR - ajuste o caminho conforme sua instalação
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Descomente e ajuste para Windows
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Aviso: pytesseract não encontrado. A detecção automática de texto não estará disponível.")

try:
    from pdf2image import convert_from_path
    PDF_SUPPORT_AVAILABLE = True
except ImportError:
    PDF_SUPPORT_AVAILABLE = False
    print("Aviso: pdf2image não encontrado. O suporte a PDF não estará disponível.")


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
        self.compressed_data = zlib.compress(data.tobytes())
    
    def get_data(self) -> np.ndarray:
        """
        Descomprime e retorna os dados do patch.
        
        Returns:
            Array NumPy com os dados descomprimidos
        """
        # Descomprime os dados
        decompressed = zlib.decompress(self.compressed_data)
        # Reconstrói o array NumPy
        return np.frombuffer(decompressed, dtype=np.uint8).reshape(self.height, self.width)


class ImageProcessor:
    """
    Classe responsável pelo processamento de imagens, separada da interface gráfica.
    Gerencia operações como carregamento, aplicação de blur e detecção de texto.
    """
    
    def __init__(self):
        """Inicializa o processador de imagens"""
        self.original_image = None  # Imagem original sem modificações
        self.current_image = None   # Imagem atual com modificações
        self.mask = None            # Máscara para áreas de blur
        self.temp_mask = None       # Máscara temporária para operações em andamento
        self.sensitive_regions = [] # Regiões detectadas como sensíveis
        
    def load_image(self, file_path: str) -> bool:
        """
        Carrega uma imagem do disco.
        
        Args:
            file_path: Caminho do arquivo de imagem
            
        Returns:
            True se a imagem foi carregada com sucesso, False caso contrário
        """
        try:
            img_cv = cv2.imread(file_path)
            if img_cv is None:
                return False
                
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            
            # Armazena a imagem original e cria uma cópia para edição
            self.original_image = img_cv.copy()
            self.current_image = img_cv.copy()
            
            # Cria máscaras vazias
            self.mask = np.zeros((img_cv.shape[0], img_cv.shape[1]), dtype=np.uint8)
            self.temp_mask = np.zeros_like(self.mask)
            
            # Limpa as regiões sensíveis detectadas anteriormente
            self.sensitive_regions = []
            
            return True
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            return False
    
    def load_from_array(self, img_array: np.ndarray) -> bool:
        """
        Carrega uma imagem a partir de um array NumPy.
        Útil para carregar páginas de PDF convertidas.
        
        Args:
            img_array: Array NumPy contendo a imagem
            
        Returns:
            True se a imagem foi carregada com sucesso, False caso contrário
        """
        try:
            if img_array is None or img_array.size == 0:
                return False
                
            # Garante que a imagem está em RGB
            if len(img_array.shape) == 2:  # Imagem em escala de cinza
                img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            elif img_array.shape[2] == 4:  # Imagem com canal alpha
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
                
            # Armazena a imagem original e cria uma cópia para edição
            self.original_image = img_array.copy()
            self.current_image = img_array.copy()
            
            # Cria máscaras vazias
            self.mask = np.zeros((img_array.shape[0], img_array.shape[1]), dtype=np.uint8)
            self.temp_mask = np.zeros_like(self.mask)
            
            # Limpa as regiões sensíveis detectadas anteriormente
            self.sensitive_regions = []
            
            return True
        except Exception as e:
            print(f"Erro ao carregar imagem do array: {e}")
            return False
    
    def apply_blur(self, intensity: int, iterations: int, apply_to_temp: bool = False) -> np.ndarray:
        """
        Aplica o efeito de blur nas áreas marcadas pela máscara.
        
        Args:
            intensity: Intensidade do blur (tamanho do kernel)
            iterations: Número de iterações do blur
            apply_to_temp: Se True, aplica o blur também nas áreas da máscara temporária
            
        Returns:
            Imagem com o blur aplicado
        """
        if self.original_image is None:
            return None
            
        # Cria uma cópia da imagem original
        result = self.original_image.copy()
        
        # Determina qual máscara usar
        if apply_to_temp and self.temp_mask is not None:
            # Combina a máscara principal com a temporária para preview
            combined_mask = cv2.bitwise_or(self.mask, self.temp_mask)
        else:
            # Usa apenas a máscara principal
            combined_mask = self.mask
        
        # Se não houver áreas marcadas, retorna a imagem sem alterações
        if np.sum(combined_mask) == 0:
            return result
            
        # Cria uma versão borrada da imagem inteira
        blurred = result.copy()
        for _ in range(iterations):
            kernel_size = intensity * 2 + 1
            blurred = cv2.GaussianBlur(blurred, (kernel_size, kernel_size), 0)
        
        # Cria uma máscara 3D para aplicar o blur apenas nas áreas marcadas
        mask_3d = np.stack([combined_mask] * 3, axis=2) / 255.0
        
        # Combina a imagem original com as áreas borradas
        result = result * (1 - mask_3d) + blurred * mask_3d
        
        return result.astype(np.uint8)
    
    def commit_temp_mask(self):
        """
        Transfere a máscara temporária para a máscara principal.
        Chamado quando uma operação de desenho é concluída.
        """
        if self.mask is not None and self.temp_mask is not None:
            self.mask = cv2.bitwise_or(self.mask, self.temp_mask)
            self.temp_mask = np.zeros_like(self.mask)
    
    def clear_temp_mask(self):
        """Limpa a máscara temporária"""
        if self.temp_mask is not None:
            self.temp_mask = np.zeros_like(self.temp_mask)
    
    def add_to_mask(self, x: int, y: int, brush_size: int, temp: bool = False):
        """
        Adiciona um ponto à máscara.
        
        Args:
            x: Coordenada X do ponto
            y: Coordenada Y do ponto
            brush_size: Tamanho do pincel
            temp: Se True, adiciona à máscara temporária; se False, à máscara principal
        """
        if self.mask is None:
            return
            
        target_mask = self.temp_mask if temp else self.mask
        cv2.circle(target_mask, (int(x), int(y)), brush_size // 2, 255, -1)
    
    def add_rectangle_to_mask(self, x1: int, y1: int, x2: int, y2: int, temp: bool = False):
        """
        Adiciona um retângulo à máscara.
        
        Args:
            x1, y1: Coordenadas do primeiro canto do retângulo
            x2, y2: Coordenadas do segundo canto do retângulo
            temp: Se True, adiciona à máscara temporária; se False, à máscara principal
        """
        if self.mask is None:
            return
            
        # Garante que as coordenadas estão na ordem correta
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        target_mask = self.temp_mask if temp else self.mask
        cv2.rectangle(target_mask, (int(x1), int(y1)), (int(x2), int(y2)), 255, -1)
    
    def add_ellipse_to_mask(self, x1: int, y1: int, x2: int, y2: int, temp: bool = False):
        """
        Adiciona uma elipse à máscara.
        
        Args:
            x1, y1: Coordenadas do primeiro canto do retângulo que circunscreve a elipse
            x2, y2: Coordenadas do segundo canto do retângulo que circunscreve a elipse
            temp: Se True, adiciona à máscara temporária; se False, à máscara principal
        """
        if self.mask is None:
            return
            
        # Calcula o centro e os raios da elipse
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        radius_x = abs(x2 - x1) // 2
        radius_y = abs(y2 - y1) // 2
        
        target_mask = self.temp_mask if temp else self.mask
        cv2.ellipse(target_mask, (center_x, center_y), (radius_x, radius_y), 0, 0, 360, 255, -1)
    
    def get_current_image(self, intensity: int, iterations: int, preview: bool = False) -> np.ndarray:
        """
        Retorna a imagem atual com os efeitos aplicados.
        
        Args:
            intensity: Intensidade do blur
            iterations: Número de iterações do blur
            preview: Se True, inclui a máscara temporária no resultado
            
        Returns:
            Imagem processada
        """
        return self.apply_blur(intensity, iterations, apply_to_temp=preview)
    
    def save_image(self, file_path: str, intensity: int, iterations: int) -> bool:
        """
        Salva a imagem processada no disco.
        
        Args:
            file_path: Caminho onde a imagem será salva
            intensity: Intensidade do blur
            iterations: Número de iterações do blur
            
        Returns:
            True se a imagem foi salva com sucesso, False caso contrário
        """
        try:
            if self.current_image is None:
                return False
                
            # Aplica o blur final e salva
            final_image = self.apply_blur(intensity, iterations)
            
            # Converte de RGB para BGR para salvar com OpenCV
            final_image = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(file_path, final_image)
            return True
        except Exception as e:
            print(f"Erro ao salvar imagem: {e}")
            return False
    
    def get_dimensions(self) -> Tuple[int, int]:
        """
        Retorna as dimensões da imagem atual.
        
        Returns:
            Tupla (largura, altura) da imagem
        """
        if self.original_image is None:
            return (0, 0)
        return self.original_image.shape[1], self.original_image.shape[0]  # width, height
    
    def reset(self):
        """Reseta todas as edições"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.mask = np.zeros((self.original_image.shape[0], self.original_image.shape[1]), dtype=np.uint8)
            self.temp_mask = np.zeros_like(self.mask)
    
    def create_thumbnail(self, width: int = 100, height: int = 100) -> Optional[ImageTk.PhotoImage]:
        """
        Cria uma miniatura da imagem atual com o blur aplicado.
        
        Args:
            width: Largura desejada da miniatura
            height: Altura desejada da miniatura
            
        Returns:
            Miniatura da imagem como um objeto PhotoImage, ou None se não houver imagem
        """
        if self.original_image is None:
            return None
            
        # Aplica o blur com configurações padrão
        img = self.apply_blur(15, 5)
        
        # Converte para PIL Image
        pil_img = Image.fromarray(img)
        
        # Redimensiona mantendo a proporção
        pil_img.thumbnail((width, height), Image.LANCZOS)
        
        # Converte para PhotoImage
        return ImageTk.PhotoImage(pil_img)
    
    def detect_sensitive_info(self) -> List[Tuple[int, int, int, int]]:
        """
        Detecta informações sensíveis na imagem usando OCR.
        
        Returns:
            Lista de tuplas (x, y, largura, altura) das regiões sensíveis detectadas
        """
        if self.original_image is None or not TESSERACT_AVAILABLE:
            return []
            
        try:
            # Converte a imagem para PIL
            pil_img = Image.fromarray(self.original_image)
            
            # Executa OCR na imagem
            ocr_result = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT, lang='por')
            
            # Padrões para informações sensíveis
            patterns = {
                'cpf': r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}',
                'rg': r'\d{1,2}\.?\d{3}\.?\d{3}-?[\dX]',
                'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                'telefone': r'(?:\+\d{2})?$$?\d{2}$$?\s*\d{4,5}-?\d{4}',
                'data': r'\d{2}/\d{2}/\d{4}',
                'cep': r'\d{5}-?\d{3}'
            }
            
            # Lista para armazenar as regiões sensíveis
            regions = []
            
            # Verifica cada texto detectado
            for i in range(len(ocr_result['text'])):
                text = ocr_result['text'][i]
                if not text.strip():
                    continue
                    
                # Verifica se o texto corresponde a algum padrão sensível
                for pattern_type, pattern in patterns.items():
                    if re.search(pattern, text):
                        # Obtém as coordenadas da região
                        x = ocr_result['left'][i]
                        y = ocr_result['top'][i]
                        w = ocr_result['width'][i]
                        h = ocr_result['height'][i]
                        
                        # Adiciona uma margem para garantir que toda a informação seja coberta
                        x = max(0, x - 5)
                        y = max(0, y - 5)
                        w += 10
                        h += 10
                        
                        regions.append((x, y, w, h))
                        break
            
            # Armazena as regiões detectadas
            self.sensitive_regions = regions
            
            return regions
        except Exception as e:
            print(f"Erro na detecção de informações sensíveis: {e}")
            return []
    
    def apply_blur_to_sensitive_regions(self, intensity: int, iterations: int):
        """
        Aplica blur automaticamente às regiões sensíveis detectadas.
        
        Args:
            intensity: Intensidade do blur
            iterations: Número de iterações do blur
        """
        if not self.sensitive_regions or self.mask is None:
            return
            
        for x, y, w, h in self.sensitive_regions:
            # Adiciona um retângulo à máscara para cada região sensível
            cv2.rectangle(self.mask, (x, y), (x + w, y + h), 255, -1)


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
    
    def add(self, mask: np.ndarray, image_processor: ImageProcessor, intensity: int, iterations: int):
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


class UserPreferences:
    """
    Gerencia as preferências do usuário.
    Salva e carrega configurações como tamanho do pincel, intensidade do blur, etc.
    """
    
    def __init__(self, config_file: str = "document_protector_config.json"):
        """
        Inicializa o gerenciador de preferências.
        
        Args:
            config_file: Nome do arquivo de configuração
        """
        self.config_file = config_file
        self.preferences = self._get_default_preferences()
        self.load()
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """
        Retorna as preferências padrão.
        
        Returns:
            Dicionário com as preferências padrão
        """
        return {
            "brush_size": 20,
            "blur_intensity": 15,
            "blur_iterations": 5,
            "auto_save_enabled": False,
            "auto_save_interval": 5,
            "show_preview": True,
            "last_directory": "",
            "keyboard_shortcuts": {
                "save": "<Control-s>",
                "open": "<Control-o>",
                "undo": "<Control-z>",
                "redo": "<Control-y>",
                "clear": "<Control-r>",
                "zoom_in": "<Control-plus>",
                "zoom_out": "<Control-minus>",
                "zoom_reset": "<Control-0>"
            }
        }
    
    def load(self) -> bool:
        """
        Carrega as preferências do arquivo.
        
        Returns:
            True se as preferências foram carregadas com sucesso, False caso contrário
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_prefs = json.load(f)
                    
                    # Atualiza as preferências, mantendo os valores padrão para chaves ausentes
                    for key, value in loaded_prefs.items():
                        if key in self.preferences:
                            if isinstance(value, dict) and isinstance(self.preferences[key], dict):
                                # Para dicionários aninhados, atualiza as chaves individualmente
                                for subkey, subvalue in value.items():
                                    if subkey in self.preferences[key]:
                                        self.preferences[key][subkey] = subvalue
                            else:
                                self.preferences[key] = value
                                
                return True
        except Exception as e:
            print(f"Erro ao carregar preferências: {e}")
        return False
    
    def save(self) -> bool:
        """
        Salva as preferências no arquivo.
        
        Returns:
            True se as preferências foram salvas com sucesso, False caso contrário
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.preferences, f, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar preferências: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém uma preferência.
        
        Args:
            key: Chave da preferência
            default: Valor padrão caso a chave não exista
            
        Returns:
            Valor da preferência ou o valor padrão
        """
        # Suporta chaves aninhadas como "ui_colors.background"
        if "." in key:
            main_key, sub_key = key.split(".", 1)
            if main_key in self.preferences and isinstance(self.preferences[main_key], dict):
                return self.preferences[main_key].get(sub_key, default)
            return default
        return self.preferences.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Define uma preferência.
        
        Args:
            key: Chave da preferência
            value: Valor da preferência
        """
        # Suporta chaves aninhadas como "ui_colors.background"
        if "." in key:
            main_key, sub_key = key.split(".", 1)
            if main_key in self.preferences and isinstance(self.preferences[main_key], dict):
                self.preferences[main_key][sub_key] = value
            else:
                self.preferences[main_key] = {sub_key: value}
        else:
            self.preferences[key] = value


class PDFManager:
    """
    Gerencia a conversão de arquivos PDF para imagens.
    """
    
    @staticmethod
    def convert_pdf_to_images(pdf_path: str) -> List[np.ndarray]:
        """
        Converte um arquivo PDF em uma lista de imagens.
        
        Args:
            pdf_path: Caminho do arquivo PDF
            
        Returns:
            Lista de arrays NumPy contendo as imagens das páginas
        """
        if not PDF_SUPPORT_AVAILABLE:
            print("Suporte a PDF não disponível. Instale pdf2image.")
            return []
            
        try:
            # Converte o PDF em imagens
            pages = convert_from_path(pdf_path, 300)  # DPI de 300 para boa qualidade
            
            # Converte as imagens PIL para arrays NumPy
            images = []
            for page in pages:
                # Converte para RGB se necessário
                if page.mode != 'RGB':
                    page = page.convert('RGB')
                
                # Converte para array NumPy
                img_array = np.array(page)
                images.append(img_array)
            
            return images
        except Exception as e:
            print(f"Erro ao converter PDF: {e}")
            return []


class DocumentProtector:
    """
    Aplicação principal para proteção de documentos.
    Gerencia a interface gráfica e coordena as outras classes.
    """
    
    def __init__(self, root):
        """
        Inicializa a aplicação.
        
        Args:
            root: Janela principal do Tkinter
        """
        self.root = root
        self.user_prefs = UserPreferences()
        self.setup_variables()
        self.create_ui()
        self.setup_bindings()
        self.setup_auto_save()
        
    def setup_variables(self):
        """Inicializa todas as variáveis da aplicação"""
        # Processador de imagem
        self.image_processor = ImageProcessor()
        
        # Gerenciador de histórico otimizado
        self.history_manager = OptimizedHistoryManager()
        
        # Estado da aplicação
        self.drawing = False
        self.last_x, self.last_y = 0, 0
        self.start_x, self.start_y = 0, 0
        
        # Configurações da ferramenta
        self.current_tool = "brush"
        self.brush_size = self.user_prefs.get("brush_size", 20)
        self.blur_intensity = self.user_prefs.get("blur_intensity", 15)
        self.blur_iterations = self.user_prefs.get("blur_iterations", 5)
        
        # Configurações de visualização
        self.canvas_width = 800
        self.canvas_height = 600
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.drag_start_x, self.drag_start_y = 0, 0
        
        # Estado do arquivo
        self.file_path = None
        self.is_saved = True
        self.status_message = "Pronto"
        
        # Configurações de autosave
        self.auto_save_enabled = self.user_prefs.get("auto_save_enabled", False)
        self.auto_save_interval = self.user_prefs.get("auto_save_interval", 5)
        self.auto_save_path = None
        
        # PDF
        self.pdf_pages = []
        self.current_page_index = 0
        
        # Thread para processamento em segundo plano
        self.processing_thread = None
        
        # Debounce para otimização
        self.debounce_timer = None
        
        # Preview
        self.show_preview = self.user_prefs.get("show_preview", True)
        
    def create_ui(self):
        """Cria a interface do usuário"""
        self.root.title("Document Protector")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configura o tema
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Estilos personalizados
        self.style.configure('TButton', font=('Segoe UI', 10), padding=5)
        self.style.configure('TFrame', background='#f0f2f5')
        self.style.configure('TLabel', background='#f0f2f5', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        self.style.configure('Subheader.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('TScale', background='#f0f2f5')
        self.style.configure('TCheckbutton', background='#f0f2f5')
        self.style.configure('TRadiobutton', background='#f0f2f5')
        
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Document Protector", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Informações sobre LGPD
        info_button = ttk.Button(header_frame, text="Sobre LGPD", command=self.show_lgpd_info)
        info_button.pack(side=tk.RIGHT)
        
        # Área de conteúdo
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Painel lateral
        self.sidebar_frame = ttk.Frame(content_frame, width=250)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.sidebar_frame.pack_propagate(False)
        
        # Notebook para organizar as opções
        self.notebook = ttk.Notebook(self.sidebar_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de Arquivo
        file_tab = ttk.Frame(self.notebook)
        self.notebook.add(file_tab, text="Arquivo")
        
        # Operações de arquivo
        file_frame = ttk.LabelFrame(file_tab, text="Operações")
        file_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Button(file_frame, text="Abrir Imagem (Ctrl+O)", command=self.open_image).pack(fill=tk.X, pady=2)
        
        if PDF_SUPPORT_AVAILABLE:
            ttk.Button(file_frame, text="Abrir PDF", command=self.open_pdf).pack(fill=tk.X, pady=2)
        
        ttk.Button(file_frame, text="Salvar (Ctrl+S)", command=self.save_image).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Salvar Como...", command=self.save_image_as).pack(fill=tk.X, pady=2)
        
        # Navegação de PDF
        self.pdf_frame = ttk.LabelFrame(file_tab, text="Navegação PDF")
        self.pdf_frame.pack(fill=tk.X, pady=5, padx=5)
        
        pdf_nav_frame = ttk.Frame(self.pdf_frame)
        pdf_nav_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(pdf_nav_frame, text="< Anterior", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        self.page_label = ttk.Label(pdf_nav_frame, text="Página 0/0")
        self.page_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(pdf_nav_frame, text="Próxima >", command=self.next_page).pack(side=tk.RIGHT, padx=2)
        
        # Salvamento automático
        autosave_frame = ttk.LabelFrame(file_tab, text="Salvamento Automático")
        autosave_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.autosave_var = tk.BooleanVar(value=self.auto_save_enabled)
        ttk.Checkbutton(autosave_frame, text="Ativar salvamento automático", 
                       variable=self.autosave_var, command=self.toggle_autosave).pack(anchor=tk.W, pady=2)
        
        interval_frame = ttk.Frame(autosave_frame)
        interval_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(interval_frame, text="Intervalo (min):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value=str(self.auto_save_interval))
        interval_spinbox = ttk.Spinbox(interval_frame, from_=1, to=60, width=5, 
                                      textvariable=self.interval_var, command=self.update_autosave_interval)
        interval_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Aba de Edição
        edit_tab = ttk.Frame(self.notebook)
        self.notebook.add(edit_tab, text="Edição")
        
        # Operações de edição
        edit_frame = ttk.LabelFrame(edit_tab, text="Operações")
        edit_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Button(edit_frame, text="Desfazer (Ctrl+Z)", command=self.undo).pack(fill=tk.X, pady=2)
        ttk.Button(edit_frame, text="Refazer (Ctrl+Y)", command=self.redo).pack(fill=tk.X, pady=2)
        ttk.Button(edit_frame, text="Limpar Tudo (Ctrl+R)", command=self.clear_all).pack(fill=tk.X, pady=2)
        
        if TESSERACT_AVAILABLE:
            ttk.Button(edit_frame, text="Detectar Informações Sensíveis", 
                      command=self.detect_and_blur_sensitive_info).pack(fill=tk.X, pady=2)
        
        # Ferramentas
        tools_frame = ttk.LabelFrame(edit_tab, text="Ferramentas")
        tools_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.tool_var = tk.StringVar(value=self.current_tool)
        ttk.Radiobutton(tools_frame, text="Pincel", variable=self.tool_var, value="brush", 
                       command=lambda: self.change_tool("brush")).pack(anchor=tk.W)
        ttk.Radiobutton(tools_frame, text="Retângulo", variable=self.tool_var, value="rectangle", 
                       command=lambda: self.change_tool("rectangle")).pack(anchor=tk.W)
        ttk.Radiobutton(tools_frame, text="Elipse", variable=self.tool_var, value="ellipse", 
                       command=lambda: self.change_tool("ellipse")).pack(anchor=tk.W)
        
        # Aba de Configurações
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="Configurações")
        
        # Configurações de ferramenta
        tool_settings_frame = ttk.LabelFrame(settings_tab, text="Configurações de Ferramenta")
        tool_settings_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Tamanho do pincel
        brush_frame = ttk.Frame(tool_settings_frame)
        brush_frame.pack(fill=tk.X, pady=2)
        
        self.brush_size_label = ttk.Label(brush_frame, text=f"Tamanho do Pincel: {self.brush_size}")
        self.brush_size_label.pack(anchor=tk.W)
        self.brush_size_scale = ttk.Scale(brush_frame, from_=5, to=50, orient="horizontal", 
                                         command=self.update_brush_size)
        self.brush_size_scale.set(self.brush_size)
        self.brush_size_scale.pack(fill=tk.X)
        
        # Intensidade do blur
        blur_frame = ttk.Frame(tool_settings_frame)
        blur_frame.pack(fill=tk.X, pady=2)
        
        self.blur_intensity_label = ttk.Label(blur_frame, text=f"Intensidade do Blur: {self.blur_intensity}")
        self.blur_intensity_label.pack(anchor=tk.W)
        self.blur_intensity_scale = ttk.Scale(blur_frame, from_=5, to=50, orient="horizontal", 
                                             command=self.update_blur_intensity)
        self.blur_intensity_scale.set(self.blur_intensity)
        self.blur_intensity_scale.pack(fill=tk.X)
        
        # Iterações do blur
        iterations_frame = ttk.Frame(tool_settings_frame)
        iterations_frame.pack(fill=tk.X, pady=2)
        
        self.blur_iterations_label = ttk.Label(iterations_frame, text=f"Iterações do Blur: {self.blur_iterations}")
        self.blur_iterations_label.pack(anchor=tk.W)
        self.blur_iterations_scale = ttk.Scale(iterations_frame, from_=1, to=10, orient="horizontal", 
                                              command=self.update_blur_iterations)
        self.blur_iterations_scale.set(self.blur_iterations)
        self.blur_iterations_scale.pack(fill=tk.X)
        
        # Configurações de visualização
        view_settings_frame = ttk.LabelFrame(settings_tab, text="Configurações de Visualização")
        view_settings_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Preview
        self.preview_var = tk.BooleanVar(value=self.show_preview)
        ttk.Checkbutton(view_settings_frame, text="Mostrar prévia antes de aplicar", 
                       variable=self.preview_var, command=self.toggle_preview).pack(anchor=tk.W, pady=2)
        
        # Zoom
        zoom_frame = ttk.Frame(view_settings_frame)
        zoom_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(zoom_frame, text="Zoom + (Ctrl++)", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="Zoom - (Ctrl+-)", command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="Ajustar", command=self.zoom_fit).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="100% (Ctrl+0)", command=self.zoom_reset).pack(side=tk.LEFT, padx=2)
        
        # Atalhos de teclado
        shortcuts_frame = ttk.LabelFrame(settings_tab, text="Atalhos de Teclado")
        shortcuts_frame.pack(fill=tk.X, pady=5, padx=5)
        
        shortcuts_text = (
            "Ctrl+O: Abrir imagem\n"
            "Ctrl+S: Salvar\n"
            "Ctrl+Z: Desfazer\n"
            "Ctrl+Y: Refazer\n"
            "Ctrl+R: Limpar tudo\n"
            "Ctrl++: Aumentar zoom\n"
            "Ctrl+-: Diminuir zoom\n"
            "Ctrl+0: Zoom 100%"
        )
        ttk.Label(shortcuts_frame, text=shortcuts_text).pack(anchor=tk.W, pady=5)
        
        # Área de histórico
        self.history_frame = ttk.LabelFrame(self.sidebar_frame, text="Histórico")
        self.history_frame.pack(fill=tk.X, pady=5, padx=5, side=tk.BOTTOM)
        
        # Canvas para exibir miniaturas do histórico
        self.history_canvas = tk.Canvas(self.history_frame, height=100, bg="#e0e0e0")
        self.history_canvas.pack(fill=tk.X, pady=5)
        
        # Área de canvas principal
        canvas_frame = ttk.Frame(content_frame)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas para exibir a imagem
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height, 
                               bg="#e0e0e0", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mensagem inicial no canvas
        self.canvas_text_id = self.canvas.create_text(
            self.canvas_width//2, self.canvas_height//2, 
            text="Abra uma imagem para começar", 
            font=('Segoe UI', 14)
        )
        
        # Barra de status
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        self.status_bar = ttk.Label(status_frame, text=self.status_message, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.zoom_label = ttk.Label(status_frame, text="Zoom: 100%", relief=tk.SUNKEN, width=15)
        self.zoom_label.pack(side=tk.RIGHT)
        
    def setup_bindings(self):
        """Configura os eventos de teclado e mouse"""
        # Eventos do mouse no canvas
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        
        # Eventos para arrastar a imagem (botão do meio)
        self.canvas.bind("<ButtonPress-2>", self.start_drag)
        self.canvas.bind("<B2-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-2>", self.stop_drag)
        
        # Eventos para zoom (roda do mouse)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.mouse_wheel)    # Linux (roda para cima)
        self.canvas.bind("<Button-5>", self.mouse_wheel)    # Linux (roda para baixo)
        
        # Atalhos de teclado
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<Control-s>", lambda event: self.save_image())
        self.root.bind("<Control-o>", lambda event: self.open_image())
        self.root.bind("<Control-r>", lambda event: self.clear_all())
        self.root.bind("<Control-plus>", lambda event: self.zoom_in())
        self.root.bind("<Control-minus>", lambda event: self.zoom_out())
        self.root.bind("<Control-0>", lambda event: self.zoom_reset())
        
        # Eventos para o histórico
        self.history_canvas.bind("<Button-1>", self.select_history_thumbnail)
        
    def setup_auto_save(self):
        """Configura o salvamento automático"""
        self.auto_save_manager = AutoSaveManager(self.auto_save)
        if self.auto_save_enabled:
            self.auto_save_manager.start()
    
    def toggle_preview(self):
        """Ativa ou desativa a prévia do efeito"""
        self.show_preview = self.preview_var.get()
        self.user_prefs.set("show_preview", self.show_preview)
        self.user_prefs.save()
    
    def toggle_autosave(self):
        """Ativa ou desativa o salvamento automático"""
        self.auto_save_enabled = self.autosave_var.get()
        self.user_prefs.set("auto_save_enabled", self.auto_save_enabled)
        
        if self.auto_save_enabled:
            if not self.file_path:
                # Se não tiver um arquivo aberto, pede para salvar primeiro
                messagebox.showinfo("Salvamento Automático", 
                                   "Para ativar o salvamento automático, salve o arquivo primeiro.")
                self.autosave_var.set(False)
                self.auto_save_enabled = False
                return
                
            self.auto_save_path = self.file_path
            self.auto_save_manager.start()
            self.update_status("Salvamento automático ativado")
        else:
            self.auto_save_manager.stop()
            self.update_status("Salvamento automático desativado")
        
        self.user_prefs.save()
    
    def update_autosave_interval(self):
        """Atualiza o intervalo de salvamento automático"""
        try:
            interval = int(self.interval_var.get())
            if interval < 1:
                interval = 1
            self.auto_save_interval = interval
            self.auto_save_manager.set_interval(interval)
            self.user_prefs.set("auto_save_interval", interval)
            self.user_prefs.save()
            self.update_status(f"Intervalo de salvamento automático: {interval} minutos")
        except ValueError:
            pass
    
    def auto_save(self):
        """Executa o salvamento automático"""
        if not self.file_path or not self.auto_save_enabled:
            return
            
        # Cria um nome de arquivo para o autosave
        if not self.auto_save_path:
            dir_name, file_name = os.path.split(self.file_path)
            name, ext = os.path.splitext(file_name)
            self.auto_save_path = os.path.join(dir_name, f"{name}_autosave{ext}")
        
        # Salva o arquivo
        success = self.image_processor.save_image(self.auto_save_path, self.blur_intensity, self.blur_iterations)
        if success:
            self.update_status(f"Salvamento automático concluído: {os.path.basename(self.auto_save_path)}")
    
    def open_image(self):
        """Abre uma imagem para edição"""
        if not self.is_saved:
            response = messagebox.askyesnocancel("Imagem não salva", 
                                                "Deseja salvar as alterações antes de abrir uma nova imagem?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self.save_image():
                    return
        
        # Obtém o diretório inicial das preferências do usuário
        initial_dir = self.user_prefs.get("last_directory", "")
        
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Imagens", "*.jpg;*.jpeg;*.png;*.bmp"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_path:
            return
            
        # Salva o diretório para uso futuro
        self.user_prefs.set("last_directory", os.path.dirname(file_path))
        self.user_prefs.save()
        
        # Carrega a imagem usando o processador
        success = self.image_processor.load_image(file_path)
        
        if success:
            # Reseta o histórico
            self.history_manager.reset()
            
            # Limpa as páginas PDF
            self.pdf_pages = []
            self.current_page_index = 0
            self.update_page_label()
            
            # Adiciona o estado inicial ao histórico
            self.add_to_history()
            
            # Atualiza a visualização
            self.file_path = file_path
            self.is_saved = True
            self.update_status(f"Imagem aberta: {os.path.basename(file_path)}")
            
            # Ajusta o zoom para caber a imagem na tela
            self.zoom_fit()
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
        else:
            messagebox.showerror("Erro", "Não foi possível abrir a imagem.")
    
    def open_pdf(self):
        """Abre um arquivo PDF e converte suas páginas em imagens"""
        if not PDF_SUPPORT_AVAILABLE:
            messagebox.showinfo("Suporte a PDF não disponível", 
                               "Para usar esta funcionalidade, instale a biblioteca pdf2image.")
            return
            
        if not self.is_saved:
            response = messagebox.askyesnocancel("Imagem não salva", 
                                                "Deseja salvar as alterações antes de abrir um novo PDF?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self.save_image():
                    return
        
        # Obtém o diretório inicial das preferências do usuário
        initial_dir = self.user_prefs.get("last_directory", "")
        
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_path:
            return
            
        # Salva o diretório para uso futuro
        self.user_prefs.set("last_directory", os.path.dirname(file_path))
        self.user_prefs.save()
        
        # Mostra uma mensagem de carregamento
        self.update_status("Convertendo PDF para imagens... Isso pode levar alguns segundos.")
        self.root.update()
        
        # Converte o PDF em imagens em uma thread separada
        def convert_pdf():
            self.pdf_pages = PDFManager.convert_pdf_to_images(file_path)
            
            # Atualiza a interface na thread principal
            self.root.after(0, self.load_pdf_page)
        
        # Inicia a thread
        threading.Thread(target=convert_pdf, daemon=True).start()
    
    def load_pdf_page(self):
        """Carrega a página atual do PDF"""
        if not self.pdf_pages:
            self.update_status("Nenhuma página encontrada no PDF.")
            return
            
        # Carrega a primeira página
        self.current_page_index = 0
        
        # Carrega a imagem da página atual
        success = self.image_processor.load_from_array(self.pdf_pages[self.current_page_index])
        
        if success:
            # Reseta o histórico
            self.history_manager.reset()
            
            # Adiciona o estado inicial ao histórico
            self.add_to_history()
            
            # Atualiza a visualização
            self.file_path = None  # PDF não tem um arquivo de imagem associado
            self.is_saved = False
            self.update_status(f"PDF carregado - Página {self.current_page_index + 1}/{len(self.pdf_pages)}")
            
            # Atualiza o label de página
            self.update_page_label()
            
            # Ajusta o zoom para caber a imagem na tela
            self.zoom_fit()
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
        else:
            messagebox.showerror("Erro", "Não foi possível carregar a página do PDF.")
    
    def update_page_label(self):
        """Atualiza o label de navegação de páginas do PDF"""
        if self.pdf_pages:
            self.page_label.config(text=f"Página {self.current_page_index + 1}/{len(self.pdf_pages)}")
        else:
            self.page_label.config(text="Página 0/0")
    
    def next_page(self):
        """Avança para a próxima página do PDF"""
        if not self.pdf_pages or self.current_page_index >= len(self.pdf_pages) - 1:
            return
            
        # Verifica se há alterações não salvas
        if not self.is_saved:
            response = messagebox.askyesnocancel("Alterações não salvas", 
                                                "Deseja salvar as alterações antes de mudar de página?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self.save_image():
                    return
        
        # Avança para a próxima página
        self.current_page_index += 1
        
        # Carrega a nova página
        success = self.image_processor.load_from_array(self.pdf_pages[self.current_page_index])
        
        if success:
            # Reseta o histórico
            self.history_manager.reset()
            
            # Adiciona o estado inicial ao histórico
            self.add_to_history()
            
            # Atualiza a visualização
            self.is_saved = True
            self.update_status(f"Página {self.current_page_index + 1}/{len(self.pdf_pages)}")
            
            # Atualiza o label de página
            self.update_page_label()
            
            # Ajusta o zoom para caber a imagem na tela
            self.zoom_fit()
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
    
    def prev_page(self):
        """Volta para a página anterior do PDF"""
        if not self.pdf_pages or self.current_page_index <= 0:
            return
            
        # Verifica se há alterações não salvas
        if not self.is_saved:
            response = messagebox.askyesnocancel("Alterações não salvas", 
                                                "Deseja salvar as alterações antes de mudar de página?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self.save_image():
                    return
        
        # Volta para a página anterior
        self.current_page_index -= 1
        
        # Carrega a nova página
        success = self.image_processor.load_from_array(self.pdf_pages[self.current_page_index])
        
        if success:
            # Reseta o histórico
            self.history_manager.reset()
            
            # Adiciona o estado inicial ao histórico
            self.add_to_history()
            
            # Atualiza a visualização
            self.is_saved = True
            self.update_status(f"Página {self.current_page_index + 1}/{len(self.pdf_pages)}")
            
            # Atualiza o label de página
            self.update_page_label()
            
            # Ajusta o zoom para caber a imagem na tela
            self.zoom_fit()
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
    
    def save_image(self):
        """Salva a imagem atual"""
        if self.image_processor.current_image is None:
            messagebox.showinfo("Informação", "Nenhuma imagem para salvar.")
            return False
            
        if self.file_path:
            success = self.image_processor.save_image(self.file_path, self.blur_intensity, self.blur_iterations)
            if success:
                self.is_saved = True
                self.update_status(f"Imagem salva: {os.path.basename(self.file_path)}")
                return True
            else:
                messagebox.showerror("Erro", "Não foi possível salvar a imagem.")
                return False
        else:
            return self.save_image_as()
    
    def save_image_as(self):
        """Salva a imagem com um novo nome"""
        if self.image_processor.current_image is None:
            messagebox.showinfo("Informação", "Nenhuma imagem para salvar.")
            return False
            
        # Obtém o diretório inicial das preferências do usuário
        initial_dir = self.user_prefs.get("last_directory", "")
        
        # Sugere um nome baseado no original com sufixo "_protected"
        default_filename = ""
        if self.file_path:
            filename, ext = os.path.splitext(self.file_path)
            default_filename = f"{filename}_protected{ext}"
        elif self.pdf_pages:
            default_filename = f"pagina_{self.current_page_index + 1}_protegida.png"
        
        file_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            defaultextension=".png",
            initialfile=os.path.basename(default_filename) if default_filename else "",
            filetypes=[
                ("PNG", "*.png"), 
                ("JPEG", "*.jpg;*.jpeg"), 
                ("BMP", "*.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if not file_path:
            return False
            
        # Salva o diretório para uso futuro
        self.user_prefs.set("last_directory", os.path.dirname(file_path))
        self.user_prefs.save()
        
        success = self.image_processor.save_image(file_path, self.blur_intensity, self.blur_iterations)
        if success:
            self.file_path = file_path
            self.is_saved = True
            self.update_status(f"Imagem salva como: {os.path.basename(file_path)}")
            return True
        else:
            messagebox.showerror("Erro", "Não foi possível salvar a imagem.")
            return False
    
    def update_canvas(self):
        """Atualiza o canvas com a imagem atual"""
        if self.image_processor.current_image is None:
            return
            
        # Obtém a imagem atual com os efeitos aplicados
        img_array = self.image_processor.get_current_image(
            self.blur_intensity, 
            self.blur_iterations,
            preview=self.drawing and self.show_preview
        )
        
        if img_array is None:
            return
            
        # Converte para PIL Image
        img = Image.fromarray(img_array)
        
        # Aplica o zoom
        img_width, img_height = img.size
        new_width = int(img_width * self.scale_factor)
        new_height = int(img_height * self.scale_factor)
        
        if new_width > 0 and new_height > 0:
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img_resized)
            
            # Limpa o canvas
            self.canvas.delete("all")
            
            # Calcula a posição para centralizar a imagem
            pos_x = max(0, (self.canvas_width - new_width) // 2) + self.offset_x
            pos_y = max(0, (self.canvas_height - new_height) // 2) + self.offset_y
            
            # Exibe a imagem
            self.canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self.tk_image)
            
            # Atualiza o label de zoom
            self.zoom_label.config(text=f"Zoom: {int(self.scale_factor * 100)}%")
    
    def start_draw(self, event):
        """Inicia o desenho"""
        if self.image_processor.current_image is None:
            return
            
        self.drawing = True
        
        # Obtém as coordenadas do canvas
        canvas_x, canvas_y = event.x, event.y
        
        # Converte para coordenadas da imagem
        img_x, img_y = self.canvas_to_image_coords(canvas_x, canvas_y)
        
        # Armazena a posição inicial
        self.start_x, self.start_y = img_x, img_y
        self.last_x, self.last_y = img_x, img_y
        
        # Limpa a máscara temporária
        self.image_processor.clear_temp_mask()
        
        if self.current_tool == "brush":
            # Adiciona um ponto à máscara temporária
            self.image_processor.add_to_mask(img_x, img_y, self.brush_size, temp=True)
            self.update_canvas()
        
        self.is_saved = False
    
    def draw(self, event):
        """Continua o desenho conforme o mouse se move"""
        if not self.drawing or self.image_processor.current_image is None:
            return
            
        # Obtém as coordenadas do canvas
        canvas_x, canvas_y = event.x, event.y
        
        # Converte para coordenadas da imagem
        img_x, img_y = self.canvas_to_image_coords(canvas_x, canvas_y)
        
        # Cancela o timer de debounce anterior, se existir
        if self.debounce_timer:
            self.root.after_cancel(self.debounce_timer)
        
        if self.current_tool == "brush":
            # Desenha uma linha na máscara temporária
            cv2.line(
                self.image_processor.temp_mask,
                (int(self.last_x), int(self.last_y)),
                (int(img_x), int(img_y)),
                255,
                self.brush_size
            )
            self.last_x, self.last_y = img_x, img_y
            
            # Usa debounce para atualizar o canvas apenas quando o mouse parar de se mover
            self.debounce_timer = self.root.after(50, self.update_canvas)
            
        elif self.current_tool in ["rectangle", "ellipse"]:
            # Limpa a máscara temporária
            self.image_processor.clear_temp_mask()
            
            if self.current_tool == "rectangle":
                # Adiciona um retângulo à máscara temporária
                self.image_processor.add_rectangle_to_mask(
                    self.start_x, self.start_y, img_x, img_y, temp=True
                )
            else:  # ellipse
                # Adiciona uma elipse à máscara temporária
                self.image_processor.add_ellipse_to_mask(
                    self.start_x, self.start_y, img_x, img_y, temp=True
                )
            
            # Usa debounce para atualizar o canvas apenas quando o mouse parar de se mover
            self.debounce_timer = self.root.after(50, self.update_canvas)
    
    def stop_draw(self, event):
        """Finaliza o desenho"""
        if not self.drawing or self.image_processor.current_image is None:
            return
            
        # Transfere a máscara temporária para a máscara principal
        self.image_processor.commit_temp_mask()
        
        # Atualiza o canvas com a imagem final
        self.update_canvas()
        
        # Adiciona ao histórico
        self.add_to_history()
        
        # Atualiza as miniaturas do histórico
        self.update_history_thumbnails()
        
        self.drawing = False
    
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """Converte coordenadas do canvas para coordenadas da imagem"""
        if self.image_processor.current_image is None:
            return 0, 0
            
        # Obtém as dimensões da imagem
        img_width, img_height = self.image_processor.get_dimensions()
        
        # Calcula o tamanho da imagem com zoom
        zoomed_width = img_width * self.scale_factor
        zoomed_height = img_height * self.scale_factor
        
        # Calcula o offset para centralizar a imagem
        offset_x = max(0, (self.canvas_width - zoomed_width) // 2) + self.offset_x
        offset_y = max(0, (self.canvas_height - zoomed_height) // 2) + self.offset_y
        
        # Converte as coordenadas
        img_x = (canvas_x - offset_x) / self.scale_factor
        img_y = (canvas_y - offset_y) / self.scale_factor
        
        # Garante que as coordenadas estão dentro dos limites da imagem
        img_x = max(0, min(img_x, img_width - 1))
        img_y = max(0, min(img_y, img_height - 1))
        
        return img_x, img_y
    
    def start_drag(self, event):
        """Inicia o arrasto da imagem"""
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def drag(self, event):
        """Arrasta a imagem pelo canvas"""
        if not self.dragging:
            return
            
        # Calcula o deslocamento
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        # Atualiza o offset
        self.offset_x += dx
        self.offset_y += dy
        
        # Atualiza as coordenadas de início do arrasto
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # Atualiza o canvas
        self.update_canvas()
    
    def stop_drag(self, event):
        """Finaliza o arrasto da imagem"""
        self.dragging = False
    
    def mouse_wheel(self, event):
        """Processa eventos da roda do mouse para zoom"""
        if self.image_processor.current_image is None:
            return
            
        # Obtém as coordenadas do mouse
        mouse_x, mouse_y = event.x, event.y
        
        # Converte para coordenadas da imagem antes do zoom
        img_x, img_y = self.canvas_to_image_coords(mouse_x, mouse_y)
        
        # Determina a direção do zoom
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            # Zoom in
            self.scale_factor *= 1.1
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            # Zoom out
            self.scale_factor /= 1.1
        
        # Limita o fator de escala
        self.scale_factor = max(0.1, min(self.scale_factor, 5.0))
        
        # Converte de volta para coordenadas do canvas após o zoom
        new_img_width, new_img_height = self.image_processor.get_dimensions()
        new_zoomed_width = new_img_width * self.scale_factor
        new_zoomed_height = new_img_height * self.scale_factor
        
        # Calcula o novo offset para manter o ponto sob o cursor
        new_offset_x = mouse_x - img_x * self.scale_factor
        new_offset_y = mouse_y - img_y * self.scale_factor
        
        # Ajusta o offset
        self.offset_x = new_offset_x
        self.offset_y = new_offset_y
        
        # Atualiza o canvas
        self.update_canvas()
    
    def zoom_in(self):
        """Aumenta o zoom"""
        if self.image_processor.current_image is None:
            return
            
        # Obtém o centro da visualização atual
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        
        # Converte para coordenadas da imagem
        img_center_x, img_center_y = self.canvas_to_image_coords(center_x, center_y)
        
        # Aumenta o zoom
        self.scale_factor *= 1.2
        self.scale_factor = min(self.scale_factor, 5.0)
        
        # Recalcula o offset para manter o centro
        new_img_width, new_img_height = self.image_processor.get_dimensions()
        new_zoomed_width = new_img_width * self.scale_factor
        new_zoomed_height = new_img_height * self.scale_factor
        
        new_offset_x = center_x - img_center_x * self.scale_factor
        new_offset_y = center_y - img_center_y * self.scale_factor
        
        self.offset_x = new_offset_x
        self.offset_y = new_offset_y
        
        # Atualiza o canvas
        self.update_canvas()
    
    def zoom_out(self):
        """Diminui o zoom"""
        if self.image_processor.current_image is None:
            return
            
        # Obtém o centro da visualização atual
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        
        # Converte para coordenadas da imagem
        img_center_x, img_center_y = self.canvas_to_image_coords(center_x, center_y)
        
        # Diminui o zoom
        self.scale_factor /= 1.2
        self.scale_factor = max(self.scale_factor, 0.1)
        
        # Recalcula o offset para manter o centro
        new_img_width, new_img_height = self.image_processor.get_dimensions()
        new_zoomed_width = new_img_width * self.scale_factor
        new_zoomed_height = new_img_height * self.scale_factor
        
        new_offset_x = center_x - img_center_x * self.scale_factor
        new_offset_y = center_y - img_center_y * self.scale_factor
        
        self.offset_x = new_offset_x
        self.offset_y = new_offset_y
        
        # Atualiza o canvas
        self.update_canvas()
    
    def zoom_fit(self):
        """Ajusta o zoom para caber a imagem na tela"""
        if self.image_processor.current_image is None:
            return
            
        # Obtém as dimensões da imagem
        img_width, img_height = self.image_processor.get_dimensions()
        
        # Calcula o fator de escala para caber no canvas
        scale_x = self.canvas_width / img_width
        scale_y = self.canvas_height / img_height
        
        # Usa o menor fator para garantir que a imagem inteira seja visível
        self.scale_factor = min(scale_x, scale_y) * 0.9  # 90% para dar uma margem
        
        # Reseta o offset
        self.offset_x = 0
        self.offset_y = 0
        
        # Atualiza o canvas
        self.update_canvas()
    
    def zoom_reset(self):
        """Reseta o zoom para 100%"""
        if self.image_processor.current_image is None:
            return
            
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.update_canvas()
    
    def add_to_history(self):
        """Adiciona o estado atual ao histórico"""
        if self.image_processor.mask is None:
            return
            
        self.history_manager.add(
            self.image_processor.mask,
            self.image_processor,
            self.blur_intensity,
            self.blur_iterations
        )
    
    def update_history_thumbnails(self):
        """Atualiza as miniaturas do histórico"""
        # Limpa o canvas de histórico
        self.history_canvas.delete("all")
        
        # Obtém o número de miniaturas
        num_thumbnails = len(self.history_manager.thumbnails)
        if num_thumbnails == 0:
            return
            
        # Calcula o tamanho e posição das miniaturas
        thumb_width = 80
        thumb_height = 60
        spacing = 10
        total_width = num_thumbnails * (thumb_width + spacing)
        
        # Ajusta a largura do canvas de histórico
        self.history_canvas.config(scrollregion=(0, 0, total_width, thumb_height + 20))
        
        # Desenha as miniaturas
        for i, thumbnail in enumerate(self.history_manager.thumbnails):
            if thumbnail:
                x = i * (thumb_width + spacing) + spacing
                y = 10
                
                # Desenha um retângulo ao redor da miniatura atual
                if i == self.history_manager.position:
                    self.history_canvas.create_rectangle(
                        x - 2, y - 2, x + thumb_width + 2, y + thumb_height + 2,
                        outline="#ff0000", width=2
                    )
                
                # Desenha a miniatura
                self.history_canvas.create_image(x, y, anchor=tk.NW, image=thumbnail)
                
                # Adiciona o número do estado
                self.history_canvas.create_text(
                    x + thumb_width // 2, y + thumb_height + 10,
                    text=str(i + 1),
                    fill="#333333"
                )
    
    def select_history_thumbnail(self, event):
        """Seleciona uma miniatura do histórico"""
        # Calcula o índice da miniatura clicada
        thumb_width = 80
        spacing = 10
        index = event.x // (thumb_width + spacing)
        
        if 0 <= index < len(self.history_manager.thumbnails):
            # Restaura o estado
            if index != self.history_manager.position:
                # Obtém as dimensões da imagem
                img_height, img_width = self.image_processor.mask.shape
                
                # Restaura a máscara
                if index < self.history_manager.position:
                    # Desfaz até o estado desejado
                    while self.history_manager.position > index:
                        mask = self.history_manager.undo((img_height, img_width))
                        if mask is not None:
                            self.image_processor.mask = mask
                else:
                    # Refaz até o estado desejado
                    while self.history_manager.position < index:
                        mask = self.history_manager.redo((img_height, img_width))
                        if mask is not None:
                            self.image_processor.mask = mask
                
                # Atualiza o canvas
                self.update_canvas()
                
                # Atualiza as miniaturas do histórico
                self.update_history_thumbnails()
                
                self.is_saved = False
    
    def undo(self):
        """Desfaz a última ação"""
        if not self.history_manager.can_undo() or self.image_processor.mask is None:
            return
            
        # Obtém as dimensões da imagem
        img_height, img_width = self.image_processor.mask.shape
        
        # Obtém o estado anterior
        mask = self.history_manager.undo((img_height, img_width))
        if mask is not None:
            # Restaura o estado
            self.image_processor.mask = mask
            
            # Atualiza o canvas
            self.update_canvas()
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
            
            self.is_saved = False
            self.update_status("Ação desfeita")
    
    def redo(self):
        """Refaz a última ação desfeita"""
        if not self.history_manager.can_redo() or self.image_processor.mask is None:
            return
            
        # Obtém as dimensões da imagem
        img_height, img_width = self.image_processor.mask.shape
        
        # Obtém o próximo estado
        mask = self.history_manager.redo((img_height, img_width))
        if mask is not None:
            # Restaura o estado
            self.image_processor.mask = mask
            
            # Atualiza o canvas
            self.update_canvas()
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
            
            self.is_saved = False
            self.update_status("Ação refeita")
    
    def clear_all(self):
        """Limpa todas as edições"""
        if self.image_processor.current_image is None:
            return
            
        response = messagebox.askyesno("Limpar Tudo", 
                                      "Tem certeza que deseja remover todas as edições?")
        if not response:
            return
            
        # Reseta o processador de imagem
        self.image_processor.reset()
        
        # Reseta o histórico
        self.history_manager.reset()
        self.add_to_history()
        
        # Atualiza o canvas
        self.update_canvas()
        
        # Atualiza as miniaturas do histórico
        self.update_history_thumbnails()
        
        self.is_saved = False
        self.update_status("Todas as edições foram removidas")
    
    def detect_and_blur_sensitive_info(self):
        """Detecta e borra automaticamente informações sensíveis na imagem"""
        if not TESSERACT_AVAILABLE:
            messagebox.showinfo("OCR não disponível", 
                               "Para usar esta funcionalidade, instale a biblioteca pytesseract.")
            return
            
        if self.image_processor.current_image is None:
            return
            
        # Mostra uma mensagem de carregamento
        self.update_status("Detectando informações sensíveis... Isso pode levar alguns segundos.")
        self.root.update()
        
        # Executa a detecção em uma thread separada
        def detect_sensitive_info():
            # Detecta informações sensíveis
            regions = self.image_processor.detect_sensitive_info()
            
            # Atualiza a interface na thread principal
            self.root.after(0, lambda: self.apply_blur_to_detected_regions(regions))
        
        # Inicia a thread
        threading.Thread(target=detect_sensitive_info, daemon=True).start()
    
    def apply_blur_to_detected_regions(self, regions):
        """Aplica blur às regiões sensíveis detectadas"""
        if not regions:
            messagebox.showinfo("Detecção de Informações", "Nenhuma informação sensível detectada.")
            self.update_status("Nenhuma informação sensível detectada.")
            return
            
        # Aplica blur às regiões detectadas
        self.image_processor.apply_blur_to_sensitive_regions(self.blur_intensity, self.blur_iterations)
        
        # Atualiza o canvas
        self.update_canvas()
        
        # Adiciona ao histórico
        self.add_to_history()
        
        # Atualiza as miniaturas do histórico
        self.update_history_thumbnails()
        
        self.is_saved = False
        self.update_status(f"{len(regions)} regiões sensíveis detectadas e borradas.")
    
    def change_tool(self, tool):
        """Muda a ferramenta atual"""
        self.current_tool = tool
        self.update_status(f"Ferramenta selecionada: {tool}")
    
    def update_brush_size(self, value):
        """Atualiza o tamanho do pincel"""
        self.brush_size = int(float(value))
        self.brush_size_label.config(text=f"Tamanho do Pincel: {self.brush_size}")
        self.user_prefs.set("brush_size", self.brush_size)
        self.user_prefs.save()
        self.update_status(f"Tamanho do pincel: {self.brush_size}")
    
    def update_blur_intensity(self, value):
        """Atualiza a intensidade do blur"""
        self.blur_intensity = int(float(value))
        self.blur_intensity_label.config(text=f"Intensidade do Blur: {self.blur_intensity}")
        self.user_prefs.set("blur_intensity", self.blur_intensity)
        self.user_prefs.save()
        self.update_status(f"Intensidade do blur: {self.blur_intensity}")
    
    def update_blur_iterations(self, value):
        """Atualiza o número de iterações do blur"""
        self.blur_iterations = int(float(value))
        self.blur_iterations_label.config(text=f"Iterações do Blur: {self.blur_iterations}")
        self.user_prefs.set("blur_iterations", self.blur_iterations)
        self.user_prefs.save()
        self.update_status(f"Iterações do blur: {self.blur_iterations}")
    
    def update_status(self, message):
        """Atualiza a mensagem da barra de status"""
        self.status_message = message
        self.status_bar.config(text=message)
    
    def show_lgpd_info(self):
        """Exibe informações sobre a LGPD"""
        info = """
        Lei Geral de Proteção de Dados (LGPD) - Lei nº 13.709/2018
        
        A LGPD estabelece regras sobre coleta, armazenamento, tratamento e compartilhamento de dados pessoais, 
        impondo mais proteção e penalidades para o não cumprimento.
        
        Ao borrar informações sensíveis em documentos, você ajuda a:
        
        1. Proteger dados pessoais como CPF, RG, endereço, etc.
        2. Evitar o uso indevido de informações confidenciais
        3. Cumprir com as exigências legais da LGPD
        4. Proteger sua empresa de possíveis sanções
        
        Use esta ferramenta para proteger documentos antes de compartilhá-los.
        """
        
        messagebox.showinfo("Sobre a LGPD", info)
    
    def on_closing(self):
        """Manipula o evento de fechamento da janela"""
        if not self.is_saved and self.image_processor.current_image is not None:
            response = messagebox.askyesnocancel("Sair", 
                                               "Há alterações não salvas. Deseja salvar antes de sair?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self.save_image():
                    return
        
        # Para o salvamento automático
        if self.auto_save_enabled:
            self.auto_save_manager.stop()
            
        # Salva as preferências do usuário
        self.user_prefs.save()
            
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentProtector(root)
    root.mainloop()

