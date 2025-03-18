"""
Módulo para gerenciamento de temas da interface
Contém funções e constantes para configurar o tema da aplicação
Versão 2.1 - Design moderno e elegante
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

# Definição dos temas
LIGHT_THEME = {
    "bg_primary": "#f8f9fa",
    "bg_secondary": "#e9ecef",
    "bg_tertiary": "#dee2e6",
    "bg_accent": "#5c7cfa",
    "bg_card": "#ffffff",
    "text_primary": "#212529",
    "text_secondary": "#495057",
    "text_accent": "#4263eb",
    "text_muted": "#6c757d",
    "border": "#ced4da",
    "success": "#40c057",
    "warning": "#fab005",
    "danger": "#fa5252",
    "info": "#15aabf",
    "canvas_bg": "#f1f3f5",
    "highlight": "#4263eb",
    "shadow": "rgba(0, 0, 0, 0.1)",
    "button_bg": "#e9ecef",
    "button_hover": "#dee2e6",
    "button_active": "#ced4da",
    "button_accent_bg": "#5c7cfa",
    "button_accent_hover": "#4c6ef5",
    "button_accent_active": "#4263eb",
    "button_accent_text": "#f8f9fa",
    "input_bg": "#ffffff",
    "input_border": "#ced4da",
    "input_focus": "#4c6ef5",
    "scrollbar": "#ced4da",
    "scrollbar_hover": "#adb5bd",
    "tooltip_bg": "#343a40",
    "tooltip_text": "#f8f9fa"
}

DARK_THEME = {
    "bg_primary": "#212529",
    "bg_secondary": "#343a40",
    "bg_tertiary": "#495057",
    "bg_accent": "#5c7cfa",
    "bg_card": "#2b3035",
    "text_primary": "#f8f9fa",
    "text_secondary": "#e9ecef",
    "text_accent": "#748ffc",
    "text_muted": "#adb5bd",
    "border": "#495057",
    "success": "#51cf66",
    "warning": "#fcc419",
    "danger": "#ff6b6b",
    "info": "#22b8cf",
    "canvas_bg": "#343a40",
    "highlight": "#748ffc",
    "shadow": "rgba(0, 0, 0, 0.3)",
    "button_bg": "#343a40",
    "button_hover": "#495057",
    "button_active": "#6c757d",
    "button_accent_bg": "#5c7cfa",
    "button_accent_hover": "#4c6ef5",
    "button_accent_active": "#4263eb",
    "button_accent_text": "#f8f9fa",
    "input_bg": "#2b3035",
    "input_border": "#495057",
    "input_focus": "#748ffc",
    "scrollbar": "#495057",
    "scrollbar_hover": "#6c757d",
    "tooltip_bg": "#f8f9fa",
    "tooltip_text": "#212529"
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
        style.configure('Card.TFrame', background=self.current_theme["bg_card"], relief='flat')
        style.configure('Toolbar.TFrame', background=self.current_theme["bg_secondary"])
        
        # Estilos de label
        style.configure('TLabel', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 10))
        style.configure('Logo.TLabel', background=self.current_theme["bg_card"], foreground=self.current_theme["text_accent"], font=('Segoe UI', 28, 'bold'))
        style.configure('AppTitle.TLabel', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 20, 'bold'))
        style.configure('Subtitle.TLabel', background=self.current_theme["bg_card"], foreground=self.current_theme["text_secondary"], font=('Segoe UI', 14))
        style.configure('SectionTitle.TLabel', background=self.current_theme["bg_card"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 12, 'bold'))
        style.configure('Info.TLabel', background=self.current_theme["bg_card"], foreground=self.current_theme["text_secondary"], font=('Segoe UI', 10))
        style.configure('StatusBar.TLabel', background=self.current_theme["bg_secondary"], foreground=self.current_theme["text_secondary"], font=('Segoe UI', 9))
        
        # Estilos de botão
        style.configure('TButton', background=self.current_theme["button_bg"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 10))
        style.map('TButton',
                 background=[('active', self.current_theme["button_active"]), ('pressed', self.current_theme["button_active"])],
                 foreground=[('active', self.current_theme["text_primary"])])
        
        style.configure('Accent.TButton', background=self.current_theme["button_accent_bg"], foreground=self.current_theme["button_accent_text"], font=('Segoe UI', 10, 'bold'))
        style.map('Accent.TButton',
                 background=[('active', self.current_theme["button_accent_active"]), ('pressed', self.current_theme["button_accent_active"])],
                 foreground=[('active', self.current_theme["button_accent_text"])])
        
        style.configure('Success.TButton', background=self.current_theme["success"], foreground=self.current_theme["button_accent_text"], font=('Segoe UI', 10))
        style.configure('Danger.TButton', background=self.current_theme["danger"], foreground=self.current_theme["button_accent_text"], font=('Segoe UI', 10))
        style.configure('Tool.TButton', background=self.current_theme["bg_secondary"], foreground=self.current_theme["text_primary"], font=('Segoe UI', 10))
        
        # Estilos de escala
        style.configure('TScale', background=self.current_theme["bg_primary"], troughcolor=self.current_theme["bg_tertiary"])
        
        # Estilos de checkbox e radiobutton
        style.configure('TCheckbutton', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_primary"])
        style.configure('TRadiobutton', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_primary"])
        
        # Estilos de notebook
        style.configure('TNotebook', background=self.current_theme["bg_primary"])
        style.configure('TNotebook.Tab', background=self.current_theme["bg_secondary"], foreground=self.current_theme["text_primary"], padding=[10, 5])
        style.map('TNotebook.Tab',
                 background=[('selected', self.current_theme["bg_card"])],
                 foreground=[('selected', self.current_theme["text_accent"])])
        
        # Estilos de labelframe
        style.configure('TLabelframe', background=self.current_theme["bg_card"])
        style.configure('TLabelframe.Label', background=self.current_theme["bg_primary"], foreground=self.current_theme["text_accent"], font=('Segoe UI', 10, 'bold'))
        
        # Estilos de progressbar
        style.configure('TProgressbar', background=self.current_theme["bg_accent"], troughcolor=self.current_theme["bg_tertiary"])
        
        # Estilos de combobox
        style.configure('TCombobox', background=self.current_theme["input_bg"], foreground=self.current_theme["text_primary"], fieldbackground=self.current_theme["input_bg"])
        style.map('TCombobox',
                 fieldbackground=[('readonly', self.current_theme["input_bg"])],
                 background=[('readonly', self.current_theme["button_bg"])])
        
        # Estilos de spinbox
        style.configure('TSpinbox', background=self.current_theme["input_bg"], foreground=self.current_theme["text_primary"], fieldbackground=self.current_theme["input_bg"])
        
        # Configura as cores do canvas
        self.root.option_add("*Canvas.background", self.current_theme["canvas_bg"])
        
        # Configura as cores do menu
        self.root.option_add("*Menu.background", self.current_theme["bg_secondary"])
        self.root.option_add("*Menu.foreground", self.current_theme["text_primary"])
        self.root.option_add("*Menu.activeBackground", self.current_theme["bg_accent"])
        self.root.option_add("*Menu.activeForeground", self.current_theme["button_accent_text"])
    
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

