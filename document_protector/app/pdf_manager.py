"""
Módulo para gerenciamento de arquivos PDF
Contém a classe PDFManager que gerencia a conversão de PDF para imagens
Versão 2.0 - Suporte a mais opções de conversão e melhor qualidade
"""

from typing import List, Optional
import numpy as np
import os
import tempfile

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
    def convert_pdf_to_images(pdf_path: str, dpi: int = 300) -> List[np.ndarray]:
        """
        Converte um arquivo PDF em uma lista de imagens.
        
        Args:
            pdf_path: Caminho do arquivo PDF
            dpi: Resolução em DPI para a conversão
            
        Returns:
            Lista de arrays NumPy contendo as imagens das páginas
        """
        if not PDFManager.is_available():
            print("Suporte a PDF não disponível. Instale pdf2image.")
            return []
            
        try:
            from pdf2image import convert_from_path
            
            # Cria um diretório temporário para armazenar as imagens
            with tempfile.TemporaryDirectory() as temp_dir:
                # Converte o PDF em imagens
                pages = convert_from_path(
                    pdf_path, 
                    dpi=dpi,
                    output_folder=temp_dir,
                    fmt="png",
                    thread_count=os.cpu_count() or 1,
                    use_pdftocairo=True
                )
                
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
    
    @staticmethod
    def get_pdf_info(pdf_path: str) -> Optional[dict]:
        """
        Obtém informações sobre um arquivo PDF.
        
        Args:
            pdf_path: Caminho do arquivo PDF
            
        Returns:
            Dicionário com informações sobre o PDF ou None se ocorrer um erro
        """
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                
                info = {
                    'num_pages': len(pdf.pages),
                    'metadata': {}
                }
                
                # Extrai os metadados
                if pdf.metadata:
                    for key, value in pdf.metadata.items():
                        if key.startswith('/'):
                            key = key[1:]
                        info['metadata'][key] = value
                
                # Obtém as dimensões da primeira página
                if len(pdf.pages) > 0:
                    page = pdf.pages[0]
                    if '/MediaBox' in page:
                        media_box = page['/MediaBox']
                        info['width'] = float(media_box[2])
                        info['height'] = float(media_box[3])
                
                return info
        except Exception as e:
            print(f"Erro ao obter informações do PDF: {e}")
            return None

