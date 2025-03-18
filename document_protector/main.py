"""
Document Protector - Aplicação principal
Protege documentos sensíveis borrando informações confidenciais
Versão 2.0 - Interface moderna e processamento otimizado
"""

import tkinter as tk
from app.document_protector import DocumentProtector
import sys
import os

def resource_path(relative_path):
    """Obtém o caminho absoluto para recursos, funciona em desenvolvimento e quando empacotado"""
    try:
        # PyInstaller cria um diretório temporário e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # Configura a aplicação
    root = tk.Tk()
    root.title("Document Protector - LGPD")
    
    # Configura o ícone da aplicação se disponível
    try:
        icon_path = resource_path("app/assets/icon.ico")
        root.iconbitmap(icon_path)
    except Exception:
        pass
    
    # Define o tamanho mínimo da janela
    root.minsize(1100, 750)
    
    # Inicia a aplicação em tela cheia
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f"{width}x{height}")
    
    # Configura o DPI awareness no Windows para melhor renderização
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    # Inicia a aplicação
    app = DocumentProtector(root)
    
    # Inicia o loop principal
    root.mainloop()

