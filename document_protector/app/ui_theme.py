"""
Módulo para gerenciamento de temas da interface
Contém funções e constantes para configurar o tema da aplicação
"""

import tkinter as tk
from tkinter import ttk

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
    "highlight": "#4a6fa5"
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
    "highlight": "#5a8ac5"
}

def set_theme(root, theme):
    """
    Configura o tema da aplicação.
    
    Args:
        root: Janela principal do Tkinter
        theme: Dicionário com as cores do tema
    """
    style = ttk.Style()
    
    # Configura as cores do tema
    style.configure('TFrame', background=theme["bg_primary"])
    style.configure('Main.TFrame', background=theme["bg_primary"])
    style.configure('Header.TFrame', background=theme["bg_primary"])
    style.configure('Content.TFrame', background=theme["bg_primary"])
    style.configure('Sidebar.TFrame', background=theme["bg_secondary"])
    style.configure('Canvas.TFrame', background=theme["bg_primary"])
    style.configure('Card.TFrame', background=theme["bg_secondary"], relief='solid', borderwidth=1)
    style.configure('Toolbar.TFrame', background=theme["bg_tertiary"])
    
    # Estilos de label
    style.configure('TLabel', background=theme["bg_primary"], foreground=theme["text_primary"], font=('Segoe UI', 10))
    style.configure('Logo.TLabel', background=theme["bg_primary"], foreground=theme["text_primary"], font=('Segoe UI', 28, 'bold'))
    style.configure('AppTitle.TLabel', background=theme["bg_primary"], foreground=theme["text_primary"], font=('Segoe UI', 20, 'bold'))
    style.configure('Subtitle.TLabel', background=theme["bg_primary"], foreground=theme["text_secondary"], font=('Segoe UI', 14))
    style.configure('SectionTitle.TLabel', background=theme["bg_secondary"], foreground=theme["text_primary"], font=('Segoe UI', 12, 'bold'))
    style.configure('Info.TLabel', background=theme["bg_secondary"], foreground=theme["text_secondary"], font=('Segoe UI', 10))
    
    # Estilos de botão
    style.configure('TButton', background=theme["bg_tertiary"], foreground=theme["text_primary"], font=('Segoe UI', 10))
    style.configure('Accent.TButton', background=theme["bg_accent"], foreground=theme["text_accent"], font=('Segoe UI', 10, 'bold'))
    style.configure('Success.TButton', background=theme["success"], foreground=theme["text_accent"], font=('Segoe UI', 10))
    style.configure('Danger.TButton', background=theme["danger"], foreground=theme["text_accent"], font=('Segoe UI', 10))
    style.configure('Tool.TButton', background=theme["bg_secondary"], foreground=theme["text_primary"], font=('Segoe UI', 10))
    
    # Estilos de escala
    style.configure('TScale', background=theme["bg_primary"], troughcolor=theme["bg_tertiary"])
    
    # Estilos de checkbox e radiobutton
    style.configure('TCheckbutton', background=theme["bg_primary"], foreground=theme["text_primary"])
    style.configure('TRadiobutton', background=theme["bg_primary"], foreground=theme["text_primary"])
    
    # Estilos de notebook
    style.configure('TNotebook', background=theme["bg_primary"])
    style.configure('TNotebook.Tab', background=theme["bg_secondary"], foreground=theme["text_primary"], padding=[10, 5])
    
    # Estilos de labelframe
    style.configure('TLabelframe', background=theme["bg_primary"])
    style.configure('TLabelframe.Label', background=theme["bg_primary"], foreground=theme["text_primary"], font=('Segoe UI', 10, 'bold'))
    
    # Configura as cores do canvas
    root.option_add("*Canvas.background", theme["canvas_bg"])
    
    # Configura as cores do menu
    root.option_add("*Menu.background", theme["bg_secondary"])
    root.option_add("*Menu.foreground", theme["text_primary"])
    root.option_add("*Menu.activeBackground", theme["bg_accent"])
    root.option_add("*Menu.activeForeground", theme["text_accent"])

