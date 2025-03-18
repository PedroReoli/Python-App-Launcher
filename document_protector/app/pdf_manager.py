"""
Módulo para gerenciamento de arquivos PDF
Contém a classe PDFManager que gerencia a conversão de PDF para imagens
"""

from typing import List
import numpy as np

class PDFManager:
    """
    Gerencia a conversão de arquivos PDF para imagens.
    """
    
    @staticmethod
    def is_available() -> bool:
        """
        Verifica se o suporte a PDF está disponível.
        
        Returns:
            True se o suporte a PDF estiver disponível, False caso contrário
        """
        try:
            from pdf2image import convert_from_path
            return True
        except ImportError:
            return False
    
    @staticmethod
    def convert_pdf_to_images(pdf_path: str) -> List[np.ndarray]:
        """
        Converte um arquivo PDF em uma lista de imagens.
        
        Args:
            pdf_path: Caminho do arquivo PDF
            
        Returns:
            Lista de arrays NumPy contendo as imagens das páginas
        """
        if not PDFManager.is_available():
            print("Suporte a PDF não disponível. Instale pdf2image.")
            return []
            
        try:
            from pdf2image import convert_from_path
            
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

