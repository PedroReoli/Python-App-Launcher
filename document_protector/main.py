"""
Document Protector - Aplicação principal
Protege documentos sensíveis borrando informações confidenciais
"""

import tkinter as tk
from app.document_protector import DocumentProtector

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Document Protector")
    
    # Configura o ícone da aplicação se disponível
    try:
        root.iconbitmap("app/assets/icon.ico")
    except:
        pass
        
    # Define o tamanho mínimo da janela
    root.minsize(1000, 700)
    
    # Inicia a aplicação em tela cheia
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f"{width}x{height}")
    
    app = DocumentProtector(root)
    root.mainloop()

