"""
Módulo para gerenciamento de temas da interface
Contém funções e constantes para configurar o tema da aplicação
Versão 2.0 - Suporte a temas personalizados e melhor organização
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

# Definição dos temas
LIGHT_THEME = {
    "bg_primary": "#ffffff",
    "bg_secondary": "#f8f9fa",
    "bg_tertiary": "#e9ecef",
    "bg_accent": "#4a6fa5",
    "text_primary": "#212529",
    "text_secondary": "#495057",
    "text_accent": "#ffffff",
    "border": "#dee2e6",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
    "canvas_bg": "#f0f2f5",
    "highlight": "#4a6fa5",
    "shadow": "rgba(0, 0, 0, 0.1)"
}

DARK_THEME = {
    "bg_primary": "#212529",
    "bg_secondary": "#343a40",
    "bg_tertiary": "#495057",
    "bg_accent": "#4a6fa5",
    "text_primary": "#f8f9fa",
    "text_secondary": "#e9ecef",
    "text_accent": "#ffffff",
    "border": "#6c757d",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
    "canvas_bg": "#2c3034",
    "highlight": "#5a8ac5",
    "shadow": "rgba(0, 0, 0, 0.3)"
}

class ThemeManager:
    """
    Gerencia o tema da aplicação.
    """
    
    def __init__(self, root):
        """
        Inicializa o gerenciador de tema.
        
        Args:
            root: Janela principal do Tkinter
        """
        self.root = root
        self.current_theme = LIGHT_THEME
    
    def set_theme(self, theme: Dict[str, str]):
        """
        Configura o tema da aplicação.
        
        Args:
            theme: Dicionário com as cores do tema
        """
        self.current_theme = theme
        self._apply_theme(self.root)
    
    def _apply_theme(self, widget):
        """
        Aplica o tema a um widget e seus filhos.
        
        Args:
            widget: Widget a receber o tema
        """
        style = ttk.Style()
        
        # Configura as cores do tema
        style.configure('TFrame', background=self.current_theme["bg_primary"])
        style.configure('Main.TFrame', background=self.current_theme["bg_primary"])
        style.configure('Header.TFrame', background=self.current_theme["bg_primary"])
        style.configure('Content.TFrame', background=self.current_theme["bg_primary"])
        style.configure('Sidebar.TFrame', background=self.current_theme["bg_secondary"])
        style.configure('Canvas.TFrame', background=self.current_theme["bg_primary"])
        style.configure('Card.TFrame', background=self.current_theme["bg_secondary"], relief='solid', borderwidth=1)
        style.configure('Toolbar.TFrame', background=self.current_theme["bg_tertiary"])
        
        # Estilos de label
        style.configure('TLabel', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 10))
        style.configure('Logo.TLabel', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 28, 'bold'))
        style.configure('AppTitle.TLabel', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 20, 'bold'))
        style.configure('Subtitle.TLabel', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_secondary"], font=('Segoe UI', 14))
        style.configure('SectionTitle.TLabel', background=self.current_theme["bg_secondary"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 12, 'bold'))
        style.configure('Info.TLabel', background=self.current_theme["bg_secondary"], foreground=self.current_theme["text_secondary"], font=('Segoe UI', 10))
        
        # Estilos de botão
        style.configure('TButton', background=self.current_theme["bg_tertiary"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 10))
        style.configure('Accent.TButton', background=self.current_theme["bg_accent"], foreground=self.current_theme["text_accent"], font=('Segoe UI', 10, 'bold'))
        style.configure('Success.TButton', background=self.current_theme["success"], foreground=self.current_theme["text_accent"], font=('Segoe UI', 10))
        style.configure('Danger.TButton', background=self.current_theme["danger"], foreground=self.current_theme["text_accent"], font=('Segoe UI', 10))
        style.configure('Tool.TButton', background=self.current_theme["bg_secondary"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 10))
        
        # Estilos de escala
        style.configure('TScale', background=self.current_theme["bg_primary"], troughcolor=self.current_theme["bg_tertiary"])
        
        # Estilos de checkbox e radiobutton
        style.configure('TCheckbutton', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_primary"])
        style.configure('TRadiobutton', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_primary"])
        
        # Estilos de notebook
        style.configure('TNotebook', background=self.current_theme["bg_primary"])
        style.configure('TNotebook.Tab', background=self.current_theme["bg_secondary"], foreground=self.current_theme["text_primary"], padding=[10, 5])
        
        # Estilos de labelframe
        style.configure('TLabelframe', background=self.current_theme["bg_primary"])
        style.configure('TLabelframe.Label', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 10, 'bold'))
        
        # Configura as cores do canvas
        self.root.option_add("*Canvas.background", self.current_theme["canvas_bg"])
        
        # Configura as cores do menu
        self.root.option_add("*Menu.background", self.current_theme["bg_secondary"])
        self.root.option_add("*Menu.foreground", self.current_theme["text_primary"])
        self.root.option_add("*Menu.activeBackground", self.current_theme["bg_accent"])
        self.root.option_add("*Menu.activeForeground", self.current_theme["text_accent"])
    
    def apply_to_window(self, window):
        """
        Aplica o tema a uma janela específica.
        
        Args:
            window: Janela a receber o tema
        """
        self._apply_theme(window)
    
    def get_color(self, key: str) -> str:
        """
        Obtém uma cor do tema atual.
        
        Args:
            key: Chave da cor
            
        Returns:
            Cor correspondente à chave
        """
        return self.current_theme.get(key, "#000000")

