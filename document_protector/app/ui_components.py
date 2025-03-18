"""
Módulo para componentes da interface do usuário
Contém funções para criar componentes da interface
Versão 2.0 - Interface moderna e responsiva
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Tuple, Callable
import os
import sys
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io

def create_modern_ui(
    root,
    open_image_callback,
    open_pdf_callback,
    save_callback,
    save_as_callback,
    prev_page_callback,
    next_page_callback,
    toggle_autosave_callback,
    update_autosave_interval_callback,
    undo_callback,
    redo_callback,
    clear_all_callback,
    detect_sensitive_info_callback,
    change_tool_callback,
    update_brush_size_callback,
    update_blur_intensity_callback,
    update_blur_iterations_callback,
    toggle_preview_callback,
    zoom_in_callback,
    zoom_out_callback,
    zoom_fit_callback,
    zoom_reset_callback,
    show_lgpd_info_callback,
    brush_size,
    blur_intensity,
    blur_iterations,
    auto_save_enabled,
    auto_save_interval,
    show_preview,
    current_tool,
    current_theme,
    export_to_pdf_callback,
    open_help_callback
) -> Dict[str, Any]:
    """
    Cria a interface moderna da aplicação.
    
    Args:
        root: Janela principal do Tkinter
        callbacks: Callbacks para as ações
        
    Returns:
        Dicionário com referências para os componentes importantes
    """
    # Frame principal
    main_frame = ttk.Frame(root, style='Main.TFrame')
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Barra de ferramentas superior
    toolbar_frame = ttk.Frame(main_frame, style='Toolbar.TFrame')
    toolbar_frame.pack(fill=tk.X, side=tk.TOP)
    
    # Cria ícones para a barra de ferramentas
    icons = create_toolbar_icons()
    
    # Botões da barra de ferramentas
    file_btn = ttk.Button(toolbar_frame, text="Abrir", image=icons["open"], compound=tk.LEFT,
                         style='Tool.TButton', command=open_image_callback)
    file_btn.image = icons["open"]  # Mantém uma referência para evitar coleta de lixo
    file_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    save_btn = ttk.Button(toolbar_frame, text="Salvar", image=icons["save"], compound=tk.LEFT,
                         style='Tool.TButton', command=save_callback)
    save_btn.image = icons["save"]
    save_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    export_btn = ttk.Button(toolbar_frame, text="Exportar PDF", image=icons["pdf"], compound=tk.LEFT,
                           style='Tool.TButton', command=export_to_pdf_callback)
    export_btn.image = icons["pdf"]
    export_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Separador
    ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, pady=5, fill=tk.Y)
    
    undo_btn = ttk.Button(toolbar_frame, text="Desfazer", image=icons["undo"], compound=tk.LEFT,
                         style='Tool.TButton', command=undo_callback)
    undo_btn.image = icons["undo"]
    undo_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    redo_btn = ttk.Button(toolbar_frame, text="Refazer", image=icons["redo"], compound=tk.LEFT,
                         style='Tool.TButton', command=redo_callback)
    redo_btn.image = icons["redo"]
    redo_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Separador
    ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, pady=5, fill=tk.Y)
    
    # Ferramentas de  orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, pady=5, fill=tk.Y)
    
    # Ferramentas de desenho
    tool_var = tk.StringVar(value=current_tool)
    
    brush_btn = ttk.Radiobutton(toolbar_frame, text="Pincel", image=icons["brush"], compound=tk.LEFT,
                               variable=tool_var, value="brush", 
                               command=lambda: change_tool_callback("brush"))
    brush_btn.image = icons["brush"]
    brush_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    rect_btn = ttk.Radiobutton(toolbar_frame, text="Retângulo", image=icons["rectangle"], compound=tk.LEFT,
                              variable=tool_var, value="rectangle", 
                              command=lambda: change_tool_callback("rectangle"))
    rect_btn.image = icons["rectangle"]
    rect_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    ellipse_btn = ttk.Radiobutton(toolbar_frame, text="Elipse", image=icons["ellipse"], compound=tk.LEFT,
                                 variable=tool_var, value="ellipse", 
                                 command=lambda: change_tool_callback("ellipse"))
    ellipse_btn.image = icons["ellipse"]
    ellipse_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Separador
    ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, pady=5, fill=tk.Y)
    
    # Botão de detecção automática
    detect_btn = ttk.Button(toolbar_frame, text="Detectar Informações Sensíveis", 
                           image=icons["detect"], compound=tk.LEFT,
                           style='Accent.TButton', 
                           command=detect_sensitive_info_callback)
    detect_btn.image = icons["detect"]
    detect_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Botão de ajuda
    help_btn = ttk.Button(toolbar_frame, text="Ajuda", image=icons["help"], compound=tk.LEFT,
                         style='Tool.TButton', command=open_help_callback)
    help_btn.image = icons["help"]
    help_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    # Botão de informações sobre LGPD
    info_btn = ttk.Button(toolbar_frame, text="Sobre LGPD", image=icons["info"], compound=tk.LEFT,
                         style='Tool.TButton', command=show_lgpd_info_callback)
    info_btn.image = icons["info"]
    info_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    # Área de conteúdo principal
    content_frame = ttk.Frame(main_frame, style='Content.TFrame')
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Painel lateral
    sidebar_frame = ttk.Frame(content_frame, style='Sidebar.TFrame', width=280)
    sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0)
    sidebar_frame.pack_propagate(False)
    
    # Notebook para organizar as opções
    notebook = ttk.Notebook(sidebar_frame)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Aba de Arquivo
    file_tab = ttk.Frame(notebook, style='Card.TFrame')
    notebook.add(file_tab, text="Arquivo")
    
    # Operações de arquivo
    file_frame = ttk.LabelFrame(file_tab, text="Operações")
    file_frame.pack(fill=tk.X, pady=10, padx=10)
    
    ttk.Button(file_frame, text="Abrir Imagem (Ctrl+O)", style='Accent.TButton', 
              command=open_image_callback).pack(fill=tk.X, pady=5)
    
    ttk.Button(file_frame, text="Abrir PDF", command=open_pdf_callback).pack(fill=tk.X, pady=5)
    ttk.Button(file_frame, text="Salvar (Ctrl+S)", command=save_callback).pack(fill=tk.X, pady=5)
    ttk.Button(file_frame, text="Salvar Como...", command=save_as_callback).pack(fill=tk.X, pady=5)
    ttk.Button(file_frame, text="Exportar para PDF", command=export_to_pdf_callback).pack(fill=tk.X, pady=5)
    
    # Navegação de PDF
    pdf_frame = ttk.LabelFrame(file_tab, text="Navegação PDF")
    pdf_frame.pack(fill=tk.X, pady=10, padx=10)
    
    pdf_nav_frame = ttk.Frame(pdf_frame)
    pdf_nav_frame.pack(fill=tk.X, pady=5)
    
    ttk.Button(pdf_nav_frame, text="< Anterior", command=prev_page_callback).pack(side=tk.LEFT, padx=5)
    page_label = ttk.Label(pdf_nav_frame, text="Página 0/0")
    page_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    ttk.Button(pdf_nav_frame, text="Próxima >", command=next_page_callback).pack(side=tk.RIGHT, padx=5)
    
    # Salvamento automático
    autosave_frame = ttk.LabelFrame(file_tab, text="Salvamento Automático")
    autosave_frame.pack(fill=tk.X, pady=10, padx=10)
    
    autosave_var = tk.BooleanVar(value=auto_save_enabled)
    ttk.Checkbutton(autosave_frame, text="Ativar salvamento automático", 
                   variable=autosave_var, command=toggle_autosave_callback).pack(anchor=tk.W, pady=5)
    
    interval_frame = ttk.Frame(autosave_frame)
    interval_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(interval_frame, text="Intervalo (min):").pack(side=tk.LEFT)
    interval_var = tk.StringVar(value=str(auto_save_interval))
    interval_spinbox = ttk.Spinbox(interval_frame, from_=1, to=60, width=5, 
                                  textvariable=interval_var, command=update_autosave_interval_callback)
    interval_spinbox.pack(side=tk.LEFT, padx=5)
    
    # Aba de Edição
    edit_tab = ttk.Frame(notebook, style='Card.TFrame')
    notebook.add(edit_tab, text="Edição")
    
    # Operações de edição
    edit_frame = ttk.LabelFrame(edit_tab, text="Operações")
    edit_frame.pack(fill=tk.X, pady=10, padx=10)
    
    ttk.Button(edit_frame, text="Desfazer (Ctrl+Z)", command=undo_callback).pack(fill=tk.X, pady=5)
    ttk.Button(edit_frame, text="Refazer (Ctrl+Y)", command=redo_callback).pack(fill=tk.X, pady=5)
    ttk.Button(edit_frame, text="Limpar Tudo (Ctrl+R)", command=clear_all_callback).pack(fill=tk.X, pady=5)
    ttk.Button(edit_frame, text="Detectar Informações Sensíveis", 
              command=detect_sensitive_info_callback).pack(fill=tk.X, pady=5)
    
    # Ferramentas
    tools_frame = ttk.LabelFrame(edit_tab, text="Ferramentas")
    tools_frame.pack(fill=tk.X, pady=10, padx=10)
    
    ttk.Radiobutton(tools_frame, text="Pincel", variable=tool_var, value="brush", 
                   command=lambda: change_tool_callback("brush")).pack(anchor=tk.W, pady=3)
    ttk.Radiobutton(tools_frame, text="Retângulo", variable=tool_var, value="rectangle", 
                   command=lambda: change_tool_callback("rectangle")).pack(anchor=tk.W, pady=3)
    ttk.Radiobutton(tools_frame, text="Elipse", variable=tool_var, value="ellipse", 
                   command=lambda: change_tool_callback("ellipse")).pack(anchor=tk.W, pady=3)
    
    # Aba de Configurações
    settings_tab = ttk.Frame(notebook, style='Card.TFrame')
    notebook.add(settings_tab, text="Configurações")
    
    # Configurações de ferramenta
    tool_settings_frame = ttk.LabelFrame(settings_tab, text="Configurações de Ferramenta")
    tool_settings_frame.pack(fill=tk.X, pady=10, padx=10)
    
    # Tamanho do pincel
    brush_frame = ttk.Frame(tool_settings_frame)
    brush_frame.pack(fill=tk.X, pady=5)
    
    brush_size_label = ttk.Label(brush_frame, text=f"Tamanho do Pincel: {brush_size}")
    brush_size_label.pack(anchor=tk.W)
    brush_size_scale = ttk.Scale(brush_frame, from_=5, to=50, orient="horizontal", 
                               command=update_brush_size_callback)
    brush_size_scale.set(brush_size)
    brush_size_scale.pack(fill=tk.X)
    
    # Intensidade do blur
    blur_frame = ttk.Frame(tool_settings_frame)
    blur_frame.pack(fill=tk.X, pady=5)
    
    blur_intensity_label = ttk.Label(blur_frame, text=f"Intensidade do Blur: {blur_intensity}")
    blur_intensity_label.pack(anchor=tk.W)
    blur_intensity_scale = ttk.Scale(blur_frame, from_=5, to=50, orient="horizontal", 
                                   command=update_blur_intensity_callback)
    blur_intensity_scale.set(blur_intensity)
    blur_intensity_scale.pack(fill=tk.X)
    
    # Iterações do blur
    iterations_frame = ttk.Frame(tool_settings_frame)
    iterations_frame.pack(fill=tk.X, pady=5)
    
    blur_iterations_label = ttk.Label(iterations_frame, text=f"Iterações do Blur: {blur_iterations}")
    blur_iterations_label.pack(anchor=tk.W)
    blur_iterations_scale = ttk.Scale(iterations_frame, from_=1, to=10, orient="horizontal", 
                                    command=update_blur_iterations_callback)
    blur_iterations_scale.set(blur_iterations)
    blur_iterations_scale.pack(fill=tk.X)
    
    # Configurações de visualização
    view_settings_frame = ttk.LabelFrame(settings_tab, text="Configurações de Visualização")
    view_settings_frame.pack(fill=tk.X, pady=10, padx=10)
    
    # Preview
    preview_var = tk.BooleanVar(value=show_preview)
    ttk.Checkbutton(view_settings_frame, text="Mostrar prévia antes de aplicar", 
                   variable=preview_var, command=toggle_preview_callback).pack(anchor=tk.W, pady=5)
    
    # Zoom
    zoom_frame = ttk.Frame(view_settings_frame)
    zoom_frame.pack(fill=tk.X, pady=5)
    
    ttk.Button(zoom_frame, text="Zoom + (Ctrl++)", command=zoom_in_callback).pack(side=tk.LEFT, padx=2)
    ttk.Button(zoom_frame, text="Zoom - (Ctrl+-)", command=zoom_out_callback).pack(side=tk.LEFT, padx=2)
    ttk.Button(zoom_frame, text="Ajustar", command=zoom_fit_callback).pack(side=tk.LEFT, padx=2)
    ttk.Button(zoom_frame, text="100% (Ctrl+0)", command=zoom_reset_callback).pack(side=tk.LEFT, padx=2)
    
    # Atalhos de teclado
    shortcuts_frame = ttk.LabelFrame(settings_tab, text="Atalhos de Teclado")
    shortcuts_frame.pack(fill=tk.X, pady=10, padx=10)
    
    shortcuts_text = (
        "Ctrl+O: Abrir imagem\n"
        "Ctrl+S: Salvar\n"
        "Ctrl+Z: Desfazer\n"
        "Ctrl+Y: Refazer\n"
        "Ctrl+R: Limpar tudo\n"
        "Ctrl++: Aumentar zoom\n"
        "Ctrl+-: Diminuir zoom\n"
        "Ctrl+0: Zoom 100%\n"
        "F1: Ajuda"
    )
    ttk.Label(shortcuts_frame, text=shortcuts_text).pack(anchor=tk.W, pady=5)
    
    # Área de canvas principal
    canvas_container = ttk.Frame(content_frame, style='Canvas.TFrame')
    canvas_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Canvas para exibir a imagem
    canvas = tk.Canvas(canvas_container, bg="#e0e0e0", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Área de histórico
    history_frame = ttk.LabelFrame(main_frame, text="Histórico")
    history_frame.pack(fill=tk.X, pady=5, padx=10, side=tk.BOTTOM)
    
    # Canvas para exibir miniaturas do histórico
    history_canvas = tk.Canvas(history_frame, height=100, bg="#e0e0e0", highlightthickness=0)
    history_canvas.pack(fill=tk.X, pady=5)
    
    # Barra de status
    status_frame = ttk.Frame(main_frame, style='Toolbar.TFrame')
    status_frame.pack(fill=tk.X, side=tk.BOTTOM)
    
    status_bar = ttk.Label(status_frame, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
    
    zoom_label = ttk.Label(status_frame, text="Zoom: 100%", relief=tk.SUNKEN, width=15)
    zoom_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    # Retorna referências para componentes importantes
    return {
        'main_frame': main_frame,
        'toolbar_frame': toolbar_frame,
        'canvas': canvas,
        'canvas_container': canvas_container,
        'history_canvas': history_canvas,
        'status_bar': status_bar,
        'zoom_label': zoom_label,
        'page_label': page_label,
        'autosave_var': autosave_var,
        'interval_var': interval_var,
        'preview_var': preview_var,
        'tool_var': tool_var,
        'brush_size_label': brush_size_label,
        'blur_intensity_label': blur_intensity_label,
        'blur_iterations_label': blur_iterations_label,
        'brush_size_scale': brush_size_scale,
        'blur_intensity_scale': blur_intensity_scale,
        'blur_iterations_scale': blur_iterations_scale,
        'icons': icons
    }

def create_toolbar_icons():
    """
    Cria ícones para a barra de ferramentas.
    
    Returns:
        Dicionário com os ícones
    """
    icons = {}
    
    # Tamanho dos ícones
    icon_size = (24, 24)
    
    # Cria ícones simples usando PIL
    for name, color, shape in [
        ("open", "#4a6fa5", "folder"),
        ("save", "#4a6fa5", "disk"),
        ("pdf", "#d9534f", "document"),
        ("undo", "#5bc0de", "arrow_left"),
        ("redo", "#5bc0de", "arrow_right"),
        ("brush", "#5cb85c", "brush"),
        ("rectangle", "#5cb85c", "rectangle"),
        ("ellipse", "#5cb85c", "ellipse"),
        ("detect", "#f0ad4e", "search"),
        ("help", "#5bc0de", "question"),
        ("info", "#5bc0de", "info")
    ]:
        # Cria uma imagem em branco
        img = Image.new('RGBA', icon_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Desenha o ícone
        if shape == "folder":
            # Desenha uma pasta
            draw.rectangle([2, 7, 22, 22], fill=color)
            draw.rectangle([7, 2, 17, 7], fill=color)
        elif shape == "disk":
            # Desenha um disco
            draw.rectangle([2, 2, 22, 22], fill=color)
            draw.rectangle([7, 7, 17, 17], fill="white")
        elif shape == "document":
            # Desenha um documento
            draw.rectangle([4, 2, 20, 22], fill=color)
            draw.rectangle([8, 8, 16, 10], fill="white")
            draw.rectangle([8, 12, 16, 14], fill="white")
            draw.rectangle([8, 16, 16, 18], fill="white")
        elif shape == "arrow_left":
            # Desenha uma seta para a esquerda
            draw.polygon([20, 4, 20, 20, 4, 12], fill=color)
        elif shape == "arrow_right":
            # Desenha uma seta para a direita
            draw.polygon([4, 4, 4, 20, 20, 12], fill=color)
        elif shape == "brush":
            # Desenha um pincel
            draw.rectangle([8, 2, 16, 8], fill=color)
            draw.line([12, 8, 12, 22], fill=color, width=2)
        elif shape == "rectangle":
            # Desenha um retângulo
            draw.rectangle([4, 4, 20, 20], outline=color, width=2)
        elif shape == "ellipse":
            # Desenha uma elipse
            draw.ellipse([4, 4, 20, 20], outline=color, width=2)
        elif shape == "search":
            # Desenha uma lupa
            draw.ellipse([4, 4, 16, 16], outline=color, width=2)
            draw.line([14, 14, 20, 20], fill=color, width=2)
        elif shape == "question":
            # Desenha um ponto de interrogação
            draw.ellipse([4, 4, 20, 20], outline=color, width=2)
            draw.text((12, 8), "?", fill=color, anchor="mm")
        elif shape == "info":
            # Desenha um ícone de informação
            draw.ellipse([4, 4, 20, 20], outline=color, width=2)
            draw.text((12, 12), "i", fill=color, anchor="mm")
        
        # Converte para PhotoImage
        icons[name] = ImageTk.PhotoImage(img)
    
    return icons

def create_theme_switcher(parent, toggle_callback, current_theme):
    """
    Cria o alternador de tema.
    
    Args:
        parent: Frame pai
        toggle_callback: Função a ser chamada quando o tema for alternado
        current_theme: Tema atual
        
    Returns:
        Frame contendo o alternador de tema
    """
    theme_frame = ttk.Frame(parent)
    theme_frame.pack(side=tk.RIGHT, padx=10, pady=5)
    
    theme_label = ttk.Label(theme_frame, text="Tema:")
    theme_label.pack(side=tk.LEFT, padx=(0, 5))
    
    theme_text = "Escuro" if current_theme == "light" else "Claro"
    theme_button = ttk.Button(theme_frame, text=theme_text, command=toggle_callback)
    theme_button.pack(side=tk.LEFT)
    
    return theme_frame

def create_welcome_screen(parent, open_image_callback, open_pdf_callback, pdf_available, current_theme):
    """
    Cria a tela de boas-vindas.
    
    Args:
        parent: Frame pai
        open_image_callback: Função para abrir imagem
        open_pdf_callback: Função para abrir PDF
        pdf_available: Se o suporte a PDF está disponível
        current_theme: Tema atual
        
    Returns:
        Frame contendo a tela de boas-vindas
    """
    # Determina as cores com base no tema
    bg_color = "#ffffff" if current_theme == "light" else "#343a40"
    text_color = "#212529" if current_theme == "light" else "#f8f9fa"
    accent_color = "#4a6fa5"
    
    # Cria um frame para a tela de boas-vindas
    welcome_frame = ttk.Frame(parent, style='Card.TFrame')
    
    # Adiciona o conteúdo da tela de boas-vindas
    logo_label = ttk.Label(welcome_frame, text="Document Protector", style='Logo.TLabel')
    logo_label.pack(pady=(20, 10))
    
    subtitle = ttk.Label(welcome_frame, text="Proteja seus documentos sensíveis", style='Subtitle.TLabel')
    subtitle.pack(pady=(0, 20))
    
    # Botões de ação
    button_frame = ttk.Frame(welcome_frame)
    button_frame.pack(pady=20)
    
    open_image_btn = ttk.Button(button_frame, text="Abrir Imagem", style='Accent.TButton', 
                               command=open_image_callback, width=20)
    open_image_btn.pack(side=tk.LEFT, padx=10)
    
    if pdf_available:
        open_pdf_btn = ttk.Button(button_frame, text="Abrir PDF", style='Accent.TButton', 
                                 command=open_pdf_callback, width=20)
        open_pdf_btn.pack(side=tk.LEFT, padx=10)
    
    # Informações sobre a LGPD
    info_frame = ttk.Frame(welcome_frame, style='Card.TFrame')
    info_frame.pack(pady=20, padx=30, fill=tk.X)
    
    info_title = ttk.Label(info_frame, text="Lei Geral de Proteção de Dados (LGPD)", style='SectionTitle.TLabel')
    info_title.pack(pady=(10, 5), padx=10)
    
    info_text = (
        "A LGPD estabelece regras sobre coleta, armazenamento, tratamento e compartilhamento de dados pessoais.\n\n"
        "Ao borrar informações sensíveis em documentos, você ajuda a:\n"
        "• Proteger dados pessoais como CPF, RG, endereço, etc.\n"
        "• Evitar o uso indevido de informações confidenciais\n"
        "• Cumprir com as exigências legais da LGPD\n"
        "• Proteger sua empresa de possíveis sanções"
    )
    info_label = ttk.Label(info_frame, text=info_text, style='Info.TLabel', justify=tk.LEFT, wraplength=500)
    info_label.pack(pady=10, padx=20)
    
    return welcome_frame

