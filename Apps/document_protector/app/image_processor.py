"""
Módulo para processamento de imagens
Contém a classe ImageProcessor que gerencia operações de imagem
Versão 2.0 - Processamento otimizado e novas funcionalidades
"""

import cv2
import numpy as np
from PIL import Image, ImageTk
import re
from typing import List, Tuple, Optional, Union
import io

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
        
        # Verifica se o OCR está disponível
        self.ocr_available = self._check_ocr_available()
        
        # Cache para operações de blur
        self.blur_cache = {}
        
    def _check_ocr_available(self) -> bool:
        """Verifica se o OCR está disponível"""
        try:
            import pytesseract
            return True
        except ImportError:
            return False
    
    def is_ocr_available(self) -> bool:
        """Retorna se o OCR está disponível"""
        return self.ocr_available
        
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
            
            # Limpa o cache de blur
            self.blur_cache = {}
            
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
            
            # Limpa o cache de blur
            self.blur_cache = {}
            
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
            
        # Verifica se podemos usar o cache
        cache_key = f"{intensity}_{iterations}_{apply_to_temp}"
        if cache_key in self.blur_cache and not apply_to_temp:
            return self.blur_cache[cache_key]
            
        # Otimização: Encontra a região de interesse (ROI) para aplicar o blur
        # Isso evita processar a imagem inteira quando apenas uma pequena área está marcada
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Se não houver contornos, retorna a imagem sem alterações
        if not contours:
            return result
            
        # Encontra o retângulo delimitador que contém todos os contornos
        x_min, y_min = float('inf'), float('inf')
        x_max, y_max = 0, 0
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            x_max = max(x_max, x + w)
            y_max = max(y_max, y + h)
        
        # Adiciona uma margem para evitar artefatos
        margin = max(5, intensity * 2)
        x_min = max(0, x_min - margin)
        y_min = max(0, y_min - margin)
        x_max = min(self.original_image.shape[1], x_max + margin)
        y_max = min(self.original_image.shape[0], y_max + margin)
        
        # Extrai a região de interesse
        roi = result[y_min:y_max, x_min:x_max].copy()
        roi_mask = combined_mask[y_min:y_max, x_min:x_max].copy()
        
        # Aplica o blur apenas na região de interesse
        roi_blurred = roi.copy()
        for _ in range(iterations):
            kernel_size = intensity * 2 + 1
            roi_blurred = cv2.GaussianBlur(roi_blurred, (kernel_size, kernel_size), 0)
        
        # Cria uma máscara 3D para aplicar o blur apenas nas áreas marcadas
        roi_mask_3d = np.stack([roi_mask] * 3, axis=2) / 255.0
        
        # Combina a ROI original com as áreas borradas
        roi_result = roi * (1 - roi_mask_3d) + roi_blurred * roi_mask_3d
        
        # Coloca a ROI processada de volta
        result[y_min:y_max, x_min:x_max] = roi_result.astype(np.uint8)
        
        # Armazena no cache se não for uma operação temporária
        if not apply_to_temp:
            self.blur_cache[cache_key] = result.copy()
        
        return result.astype(np.uint8)
    
    def commit_temp_mask(self):
        """
        Transfere a máscara temporária para a máscara principal.
        Chamado quando uma operação de desenho é concluída.
        """
        if self.mask is not None and self.temp_mask is not None:
            self.mask = cv2.bitwise_or(self.mask, self.temp_mask)
            self.temp_mask = np.zeros_like(self.mask)
            
            # Limpa o cache de blur
            self.blur_cache = {}
    
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
        
        # Limpa o cache de blur se não for temporário
        if not temp:
            self.blur_cache = {}
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, brush_size: int):
        """
        Desenha uma linha na máscara temporária.
        
        Args:
            x1, y1: Coordenadas do ponto inicial
            x2, y2: Coordenadas do ponto final
            brush_size: Espessura da linha
        """
        if self.temp_mask is None:
            return
            
        cv2.line(
            self.temp_mask,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            255,
            brush_size
        )
    
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
        
        # Limpa o cache de blur se não for temporário
        if not temp:
            self.blur_cache = {}
    
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
        
        # Limpa o cache de blur se não for temporário
        if not temp:
            self.blur_cache = {}
    
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
            
            # Determina o formato com base na extensão
            _, ext = file_path.lower().rsplit('.', 1)
            
            if ext in ['jpg', 'jpeg']:
                # Converte de RGB para BGR para salvar com OpenCV
                final_image = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(file_path, final_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            elif ext == 'png':
                # Converte de RGB para BGR para salvar com OpenCV
                final_image = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(file_path, final_image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            else:
                # Para outros formatos, usa o padrão
                final_image = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(file_path, final_image)
                
            return True
        except Exception as e:
            print(f"Erro ao salvar imagem: {e}")
            return False
    
    def export_to_pdf(self, file_path: str, intensity: int, iterations: int) -> bool:
        """
        Exporta a imagem processada para PDF.
        
        Args:
            file_path: Caminho onde o PDF será salvo
            intensity: Intensidade do blur
            iterations: Número de iterações do blur
            
        Returns:
            True se o PDF foi salvo com sucesso, False caso contrário
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.pdfgen import canvas
            import io
            
            if self.current_image is None:
                return False
                
            # Aplica o blur final
            final_image = self.apply_blur(intensity, iterations)
            
            # Converte para PIL Image
            pil_img = self.array_to_pil(final_image)
            
            # Determina o tamanho da página
            img_width, img_height = pil_img.size
            aspect_ratio = img_width / img_height
            
            # Escolhe o tamanho da página
            if aspect_ratio > 1:  # Paisagem
                page_width, page_height = letter
            else:  # Retrato
                page_width, page_height = A4
            
            # Calcula o tamanho da imagem no PDF
            margin = 50  # Margem em pontos
            max_width = page_width - 2 * margin
            max_height = page_height - 2 * margin
            
            # Redimensiona a imagem para caber na página
            if img_width / max_width > img_height / max_height:
                # Limitado pela largura
                new_width = max_width
                new_height = img_height * (max_width / img_width)
            else:
                # Limitado pela altura
                new_height = max_height
                new_width = img_width * (max_height / img_height)
            
            # Cria o PDF
            c = canvas.Canvas(file_path, pagesize=(page_width, page_height))
            
            # Posiciona a imagem no centro da página
            x = (page_width - new_width) / 2
            y = (page_height - new_height) / 2
            
            # Salva a imagem em um buffer
            img_buffer = io.BytesIO()
            pil_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Adiciona a imagem ao PDF
            c.drawImage(img_buffer, x, y, width=new_width, height=new_height)
            
            # Adiciona informações de metadados
            c.setTitle("Documento Protegido - LGPD")
            c.setAuthor("Document Protector")
            c.setSubject("Documento com informações sensíveis protegidas")
            
            # Finaliza o PDF
            c.save()
            
            return True
        except Exception as e:
            print(f"Erro ao exportar para PDF: {e}")
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
            
            # Limpa o cache de blur
            self.blur_cache = {}
    
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
        pil_img = self.array_to_pil(img)
        
        # Redimensiona mantendo a proporção
        pil_img.thumbnail((width, height), Image.LANCZOS)
        
        # Converte para PhotoImage
        return ImageTk.PhotoImage(pil_img)
    
    def array_to_pil(self, img_array: np.ndarray) -> Image.Image:
        """
        Converte um array NumPy para uma imagem PIL.
        
        Args:
            img_array: Array NumPy contendo a imagem
            
        Returns:
            Imagem PIL
        """
        return Image.fromarray(img_array)
    
    def resize_image(self, img: Image.Image, width: int, height: int) -> Image.Image:
        """
        Redimensiona uma imagem PIL.
        
        Args:
            img: Imagem PIL
            width: Nova largura
            height: Nova altura
            
        Returns:
            Imagem redimensionada
        """
        return img.resize((width, height), Image.LANCZOS)
    
    def detect_sensitive_info(self) -> List[Tuple[int, int, int, int]]:
        """
        Detecta informações sensíveis na imagem usando OCR.
        
        Returns:
            Lista de tuplas (x, y, largura, altura) das regiões sensíveis detectadas
        """
        if self.original_image is None or not self.ocr_available:
            return []
            
        try:
            import pytesseract
            
            # Converte a imagem para PIL
            pil_img = self.array_to_pil(self.original_image)
            
            # Executa OCR na imagem
            ocr_result = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT, lang='por')
            
            # Padrões para informações sensíveis
            patterns = {
                'cpf': r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}',
                'rg': r'\d{1,2}\.?\d{3}\.?\d{3}-?[\dX]',
                'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                'telefone': r'(?:\+\d{2})?$$?\d{2}$$?\s*\d{4,5}-?\d{4}',
                'data': r'\d{2}/\d{2}/\d{4}',
                'cep': r'\d{5}-?\d{3}',
                'cartao': r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}'
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
            
        # Limpa o cache de blur
        self.blur_cache = {}

