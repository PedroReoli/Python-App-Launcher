"""
Módulo para componentes da interface do usuário
Contém funções para criar componentes da interface
Versão 2.1 - Design moderno e elegante com PyTabler Icons
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Tuple, Callable
import os
import sys
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io
import base64
import json
import importlib.resources as pkg_resources

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
    # Carrega os ícones do PyTabler
    icons = load_tabler_icons()
    
    # Frame principal
    main_frame = ttk.Frame(root, style='Main.TFrame')
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Barra de ferramentas superior
    toolbar_frame = ttk.Frame(main_frame, style='Toolbar.TFrame')
    toolbar_frame.pack(fill=tk.X, side=tk.TOP, padx=0, pady=0)
    
    # Cria um frame para o logo e título
    header_frame = ttk.Frame(toolbar_frame, style='Toolbar.TFrame')
    header_frame.pack(side=tk.LEFT, padx=10, pady=5)
    
    # Logo e título
    app_title = ttk.Label(header_frame, text="Document Protector", style='AppTitle.TLabel')
    app_title.pack(side=tk.LEFT, padx=5)
    
    # Separador
    ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
    
    # Botões da barra de ferramentas - Arquivo
    file_frame = ttk.Frame(toolbar_frame, style='Toolbar.TFrame')
    file_frame.pack(side=tk.LEFT, padx=5, pady=5)
    
    file_btn = ttk.Button(file_frame, image=icons["file"], style='Tool.TButton', 
                         command=open_image_callback, padding=5)
    file_btn.image = icons["file"]  # Mantém uma referência para evitar coleta de lixo
    file_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(file_btn, "Abrir Imagem (Ctrl+O)")
    
    save_btn = ttk.Button(file_frame, image=icons["device-floppy"], style='Tool.TButton', 
                         command=save_callback, padding=5)
    save_btn.image = icons["device-floppy"]
    save_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(save_btn, "Salvar (Ctrl+S)")
    
    export_btn = ttk.Button(file_frame, image=icons["file-export"], style='Tool.TButton', 
                           command=export_to_pdf_callback, padding=5)
    export_btn.image = icons["file-export"]
    export_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(export_btn, "Exportar para PDF")
    
    # Separador
    ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
    
    # Botões da barra de ferramentas - Edição
    edit_frame = ttk.Frame(toolbar_frame, style='Toolbar.TFrame')
    edit_frame.pack(side=tk.LEFT, padx=5, pady=5)
    
    undo_btn = ttk.Button(edit_frame, image=icons["arrow-back-up"], style='Tool.TButton', 
                         command=undo_callback, padding=5)
    undo_btn.image = icons["arrow-back-up"]
    undo_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(undo_btn, "Desfazer (Ctrl+Z)")
    
    redo_btn = ttk.Button(edit_frame, image=icons["arrow-forward-up"], style='Tool.TButton', 
                         command=redo_callback, padding=5)
    redo_btn.image = icons["arrow-forward-up"]
    redo_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(redo_btn, "Refazer (Ctrl+Y)")
    
    clear_btn = ttk.Button(edit_frame, image=icons["eraser"], style='Tool.TButton', 
                          command=clear_all_callback, padding=5)
    clear_btn.image = icons["eraser"]
    clear_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(clear_btn, "Limpar Tudo (Ctrl+R)")
    
    # Separador
    ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
    
    # Ferramentas de desenho
    tools_frame = ttk.Frame(toolbar_frame, style='Toolbar.TFrame')
    tools_frame.pack(side=tk.LEFT, padx=5, pady=5)
    
    tool_var = tk.StringVar(value=current_tool)
    
    brush_btn = ttk.Radiobutton(tools_frame, image=icons["brush"], variable=tool_var, value="brush", 
                               command=lambda: change_tool_callback("brush"), padding=5)
    brush_btn.image = icons["brush"]
    brush_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(brush_btn, "Ferramenta Pincel")
    
    rect_btn = ttk.Radiobutton(tools_frame, image=icons["square"], variable=tool_var, value="rectangle", 
                              command=lambda: change_tool_callback("rectangle"), padding=5)
    rect_btn.image = icons["square"]
    rect_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(rect_btn, "Ferramenta Retângulo")
    
    ellipse_btn = ttk.Radiobutton(tools_frame, image=icons["circle"], variable=tool_var, value="ellipse", 
                                 command=lambda: change_tool_callback("ellipse"), padding=5)
    ellipse_btn.image = icons["circle"]
    ellipse_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(ellipse_btn, "Ferramenta Elipse")
    
    # Separador
    ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
    
    # Botão de detecção automática
    detect_frame = ttk.Frame(toolbar_frame, style='Toolbar.TFrame')
    detect_frame.pack(side=tk.LEFT, padx=5, pady=5)
    
    detect_btn = ttk.Button(detect_frame, image=icons["search"], style='Accent.TButton', 
                           command=detect_sensitive_info_callback, padding=5)
    detect_btn.image = icons["search"]
    detect_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(detect_btn, "Detectar Informações Sensíveis")
    
    # Botões de zoom
    zoom_frame = ttk.Frame(toolbar_frame, style='Toolbar.TFrame')
    zoom_frame.pack(side=tk.LEFT, padx=5, pady=5)
    
    zoom_in_btn = ttk.Button(zoom_frame, image=icons["zoom-in"], style='Tool.TButton', 
                            command=zoom_in_callback, padding=5)
    zoom_in_btn.image = icons["zoom-in"]
    zoom_in_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(zoom_in_btn, "Aumentar Zoom (Ctrl++)")
    
    zoom_out_btn = ttk.Button(zoom_frame, image=icons["zoom-out"], style='Tool.TButton', 
                             command=zoom_out_callback, padding=5)
    zoom_out_btn.image = icons["zoom-out"]
    zoom_out_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(zoom_out_btn, "Diminuir Zoom (Ctrl+-)")
    
    zoom_fit_btn = ttk.Button(zoom_frame, image=icons["zoom-scan"], style='Tool.TButton', 
                             command=zoom_fit_callback, padding=5)
    zoom_fit_btn.image = icons["zoom-scan"]
    zoom_fit_btn.pack(side=tk.LEFT, padx=2)
    add_tooltip(zoom_fit_btn, "Ajustar à Tela")
    
    # Botões de ajuda e informações
    help_frame = ttk.Frame(toolbar_frame, style='Toolbar.TFrame')
    help_frame.pack(side=tk.RIGHT, padx=10, pady=5)
    
    help_btn = ttk.Button(help_frame, image=icons["help"], style='Tool.TButton', 
                         command=open_help_callback, padding=5)
    help_btn.image = icons["help"]
    help_btn.pack(side=tk.RIGHT, padx=2)
    add_tooltip(help_btn, "Ajuda (F1)")
    
    info_btn = ttk.Button(help_frame, image=icons["info-circle"], style='Tool.TButton', 
                         command=show_lgpd_info_callback, padding=5)
    info_btn.image = icons["info-circle"]
    info_btn.pack(side=tk.RIGHT, padx=2)
    add_tooltip(info_btn, "Sobre LGPD")
    
    # Área de conteúdo principal
    content_frame = ttk.Frame(main_frame, style='Content.TFrame')
    content_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    # Painel lateral
    sidebar_frame = ttk.Frame(content_frame, style='Sidebar.TFrame', width=280)
    sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
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
    
    # Cria botões com ícones
    open_btn = ttk.Button(file_frame, text="Abrir Imagem", image=icons["file"], compound=tk.LEFT,
                         command=open_image_callback)
    open_btn.image = icons["file"]
    open_btn.pack(fill=tk.X, pady=5, padx=5)
    
    pdf_btn = ttk.Button(file_frame, text="Abrir PDF", image=icons["file-type-pdf"], compound=tk.LEFT,
                        command=open_pdf_callback)
    pdf_btn.image = icons["file-type-pdf"]
    pdf_btn.pack(fill=tk.X, pady=5, padx=5)
    
    save_btn = ttk.Button(file_frame, text="Salvar", image=icons["device-floppy"], compound=tk.LEFT,
                         command=save_callback)
    save_btn.image = icons["device-floppy"]
    save_btn.pack(fill=tk.X, pady=5, padx=5)
    
    save_as_btn = ttk.Button(file_frame, text="Salvar Como...", image=icons["file-plus"], compound=tk.LEFT,
                            command=save_as_callback)
    save_as_btn.image = icons["file-plus"]
    save_as_btn.pack(fill=tk.X, pady=5, padx=5)
    
    export_pdf_btn = ttk.Button(file_frame, text="Exportar para PDF", image=icons["file-export"], compound=tk.LEFT,
                               command=export_to_pdf_callback)
    export_pdf_btn.image = icons["file-export"]
    export_pdf_btn.pack(fill=tk.X, pady=5, padx=5)
    
    # Navegação de PDF
    pdf_frame = ttk.LabelFrame(file_tab, text="Navegação PDF")
    pdf_frame.pack(fill=tk.X, pady=10, padx=10)
    
    pdf_nav_frame = ttk.Frame(pdf_frame)
    pdf_nav_frame.pack(fill=tk.X, pady=5, padx=5)
    
    prev_btn = ttk.Button(pdf_nav_frame, image=icons["chevron-left"], command=prev_page_callback)
    prev_btn.image = icons["chevron-left"]
    prev_btn.pack(side=tk.LEFT, padx=5)
    
    page_label = ttk.Label(pdf_nav_frame, text="Página 0/0")
    page_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    next_btn = ttk.Button(pdf_nav_frame, image=icons["chevron-right"], command=next_page_callback)
    next_btn.image = icons["chevron-right"]
    next_btn.pack(side=tk.RIGHT, padx=5)
    
    # Salvamento automático
    autosave_frame = ttk.LabelFrame(file_tab, text="Salvamento Automático")
    autosave_frame.pack(fill=tk.X, pady=10, padx=10)
    
    autosave_var = tk.BooleanVar(value=auto_save_enabled)
    autosave_check = ttk.Checkbutton(autosave_frame, text="Ativar salvamento automático", 
                                    variable=autosave_var, command=toggle_autosave_callback)
    autosave_check.pack(anchor=tk.W, pady=5, padx=5)
    
    interval_frame = ttk.Frame(autosave_frame)
    interval_frame.pack(fill=tk.X, pady=5, padx=5)
    
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
    
    undo_btn = ttk.Button(edit_frame, text="Desfazer", image=icons["arrow-back-up"], compound=tk.LEFT,
                         command=undo_callback)
    undo_btn.image = icons["arrow-back-up"]
    undo_btn.pack(fill=tk.X, pady=5, padx=5)
    
    redo_btn = ttk.Button(edit_frame, text="Refazer", image=icons["arrow-forward-up"], compound=tk.LEFT,
                         command=redo_callback)
    redo_btn.image = icons["arrow-forward-up"]
    redo_btn.pack(fill=tk.X, pady=5, padx=5)
    
    clear_btn = ttk.Button(edit_frame, text="Limpar Tudo", image=icons["eraser"], compound=tk.LEFT,
                          command=clear_all_callback)
    clear_btn.image = icons["eraser"]
    clear_btn.pack(fill=tk.X, pady=5, padx=5)
    
    detect_btn = ttk.Button(edit_frame, text="Detectar Informações Sensíveis", 
                           image=icons["search"], compound=tk.LEFT,
                           command=detect_sensitive_info_callback)
    detect_btn.image = icons["search"]
    detect_btn.pack(fill=tk.X, pady=5, padx=5)
    
    # Ferramentas
    tools_frame = ttk.LabelFrame(edit_tab, text="Ferramentas")
    tools_frame.pack(fill=tk.X, pady=10, padx=10)
    
    brush_radio = ttk.Radiobutton(tools_frame, text="Pincel", image=icons["brush"], compound=tk.LEFT,
                                 variable=tool_var, value="brush", 
                                 command=lambda: change_tool_callback("brush"))
    brush_radio.image = icons["brush"]
    brush_radio.pack(anchor=tk.W, pady=3, padx=5)
    
    rect_radio = ttk.Radiobutton(tools_frame, text="Retângulo", image=icons["square"], compound=tk.LEFT,
                                variable=tool_var, value="rectangle", 
                                command=lambda: change_tool_callback("rectangle"))
    rect_radio.image = icons["square"]
    rect_radio.pack(anchor=tk.W, pady=3, padx=5)
    
    ellipse_radio = ttk.Radiobutton(tools_frame, text="Elipse", image=icons["circle"], compound=tk.LEFT,
                                   variable=tool_var, value="ellipse", 
                                   command=lambda: change_tool_callback("ellipse"))
    ellipse_radio.image = icons["circle"]
    ellipse_radio.pack(anchor=tk.W, pady=3, padx=5)
    
    # Aba de Configurações
    settings_tab = ttk.Frame(notebook, style='Card.TFrame')
    notebook.add(settings_tab, text="Configurações")
    
    # Configurações de ferramenta
    tool_settings_frame = ttk.LabelFrame(settings_tab, text="Configurações de Ferramenta")
    tool_settings_frame.pack(fill=tk.X, pady=10, padx=10)
    
    # Tamanho do pincel
    brush_frame = ttk.Frame(tool_settings_frame)
    brush_frame.pack(fill=tk.X, pady=5, padx=5)
    
    brush_size_label = ttk.Label(brush_frame, text=f"Tamanho do Pincel: {brush_size}")
    brush_size_label.pack(anchor=tk.W)
    brush_size_scale = ttk.Scale(brush_frame, from_=5, to=50, orient="horizontal", 
                               command=update_brush_size_callback)
    brush_size_scale.set(brush_size)
    brush_size_scale.pack(fill=tk.X)
    
    # Intensidade do blur
    blur_frame = ttk.Frame(tool_settings_frame)
    blur_frame.pack(fill=tk.X, pady=5, padx=5)
    
    blur_intensity_label = ttk.Label(blur_frame, text=f"Intensidade do Blur: {blur_intensity}")
    blur_intensity_label.pack(anchor=tk.W)
    blur_intensity_scale = ttk.Scale(blur_frame, from_=5, to=50, orient="horizontal", 
                                   command=update_blur_intensity_callback)
    blur_intensity_scale.set(blur_intensity)
    blur_intensity_scale.pack(fill=tk.X)
    
    # Iterações do blur
    iterations_frame = ttk.Frame(tool_settings_frame)
    iterations_frame.pack(fill=tk.X, pady=5, padx=5)
    
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
    preview_check = ttk.Checkbutton(view_settings_frame, text="Mostrar prévia antes de aplicar", 
                                   variable=preview_var, command=toggle_preview_callback)
    preview_check.pack(anchor=tk.W, pady=5, padx=5)
    
    # Zoom
    zoom_frame = ttk.Frame(view_settings_frame)
    zoom_frame.pack(fill=tk.X, pady=5, padx=5)
    
    zoom_in_btn = ttk.Button(zoom_frame, text="Zoom +", image=icons["zoom-in"], compound=tk.LEFT,
                            command=zoom_in_callback)
    zoom_in_btn.image = icons["zoom-in"]
    zoom_in_btn.pack(side=tk.LEFT, padx=2)
    
    zoom_out_btn = ttk.Button(zoom_frame, text="Zoom -", image=icons["zoom-out"], compound=tk.LEFT,
                             command=zoom_out_callback)
    zoom_out_btn.image = icons["zoom-out"]
    zoom_out_btn.pack(side=tk.LEFT, padx=2)
    
    zoom_fit_btn = ttk.Button(zoom_frame, text="Ajustar", image=icons["zoom-scan"], compound=tk.LEFT,
                             command=zoom_fit_callback)
    zoom_fit_btn.image = icons["zoom-scan"]
    zoom_fit_btn.pack(side=tk.LEFT, padx=2)
    
    zoom_reset_btn = ttk.Button(zoom_frame, text="100%", image=icons["zoom-reset"], compound=tk.LEFT,
                               command=zoom_reset_callback)
    zoom_reset_btn.image = icons["zoom-reset"]
    zoom_reset_btn.pack(side=tk.LEFT, padx=2)
    
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
    ttk.Label(shortcuts_frame, text=shortcuts_text).pack(anchor=tk.W, pady=5, padx=5)
    
    # Área de canvas principal
    canvas_container = ttk.Frame(content_frame, style='Canvas.TFrame')
    canvas_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Canvas para exibir a imagem
    canvas = tk.Canvas(canvas_container, bg="#f1f3f5" if current_theme == "light" else "#343a40", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Área de histórico
    history_frame = ttk.LabelFrame(main_frame, text="Histórico")
    history_frame.pack(fill=tk.X, pady=5, padx=10, side=tk.BOTTOM)
    
    # Canvas para exibir miniaturas do histórico
    history_canvas = tk.Canvas(history_frame, height=100, bg="#f1f3f5" if current_theme == "light" else "#343a40", highlightthickness=0)
    history_canvas.pack(fill=tk.X, pady=5, padx=5)
    
    # Barra de status
    status_frame = ttk.Frame(main_frame, style='Toolbar.TFrame')
    status_frame.pack(fill=tk.X, side=tk.BOTTOM)
    
    status_bar = ttk.Label(status_frame, text="Pronto", relief=tk.SUNKEN, anchor=tk.W, style='StatusBar.TLabel')
    status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
    
    zoom_label = ttk.Label(status_frame, text="Zoom: 100%", relief=tk.SUNKEN, width=15, style='StatusBar.TLabel')
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

def load_tabler_icons():
    """
    Carrega os ícones do PyTabler.
    
    Returns:
        Dicionário com os ícones
    """
    icons = {}
    
    # Tamanho dos ícones
    icon_size = (24, 24)
    
    # Lista de ícones necessários
    icon_names = [
        "file", "device-floppy", "file-export", "arrow-back-up", "arrow-forward-up",
        "brush", "square", "circle", "search", "zoom-in", "zoom-out", "zoom-scan",
        "zoom-reset", "help", "info-circle", "file-type-pdf", "file-plus",
        "chevron-left", "chevron-right", "eraser", "eye", "eye-off"
    ]
    
    # Cores dos ícones
    icon_color = "#4263eb"  # Cor principal para ícones
    
    # Cria os ícones do PyTabler
    for name in icon_names:
        # Cria uma imagem em branco
        img = Image.new('RGBA', icon_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Desenha o ícone baseado no nome
        draw_tabler_icon(draw, name, icon_color, icon_size)
        
        # Converte para PhotoImage
        icons[name] = ImageTk.PhotoImage(img)
    
    return icons

def draw_tabler_icon(draw, name, color, size):
    """
    Desenha um ícone do PyTabler.
    
    Args:
        draw: Objeto ImageDraw
        name: Nome do ícone
        color: Cor do ícone
        size: Tamanho do ícone
    """
    width, height = size
    
    # Desenha o ícone baseado no nome
    if name == "file":
        # Desenha um ícone de arquivo
        draw.rectangle([6, 2, 18, 22], outline=color, width=1)
        draw.polygon([6, 2, 14, 2, 18, 6, 18, 22, 6, 22], outline=color, width=1)
        draw.line([14, 2, 14, 6, 18, 6], fill=color, width=1)
    elif name == "device-floppy":
        # Desenha um ícone de disquete
        draw.rectangle([4, 4, 20, 20], outline=color, width=1)
        draw.rectangle([7, 4, 17, 10], outline=color, width=1)
        draw.rectangle([7, 14, 17, 20], outline=color, width=1)
    elif name == "file-export":
        # Desenha um ícone de exportação
        draw.rectangle([4, 6, 14, 18], outline=color, width=1)
        draw.line([16, 12, 22, 12], fill=color, width=1)
        draw.polygon([19, 8, 19, 16, 22, 12], fill=color)
    elif name == "arrow-back-up":
        # Desenha uma seta para desfazer
        draw.line([12, 8, 12, 16], fill=color, width=1)
        draw.line([8, 12, 16, 12], fill=color, width=1)
        draw.arc([8, 4, 16, 12], 90, 180, fill=color, width=1)
    elif name == "arrow-forward-up":
        # Desenha uma seta para refazer
        draw.line([12, 8, 12, 16], fill=color, width=1)
        draw.line([8, 12, 16, 12], fill=color, width=1)
        draw.arc([8, 4, 16, 12], 0, 90, fill=color, width=1)
    elif name == "brush":
        # Desenha um pincel
        draw.line([8, 8, 16, 16], fill=color, width=2)
        draw.line([8, 16, 16, 8], fill=color, width=2)
    elif name == "square":
        # Desenha um quadrado
        draw.rectangle([6, 6, 18, 18], outline=color, width=1)
    elif name == "circle":
        # Desenha um círculo
        draw.ellipse([6, 6, 18, 18], outline=color, width=1)
    elif name == "search":
        # Desenha uma lupa
        draw.ellipse([6, 6, 16, 16], outline=color, width=1)
        draw.line([15, 15, 19, 19], fill=color, width=2)
    elif name == "zoom-in":
        # Desenha uma lupa com +
        draw.ellipse([6, 6, 16, 16], outline=color, width=1)
        draw.line([15, 15, 19, 19], fill=color, width=2)
        draw.line([9, 11, 13, 11], fill=color, width=1)
        draw.line([11, 9, 11, 13], fill=color, width=1)
    elif name == "zoom-out":
        # Desenha uma lupa com -
        draw.ellipse([6, 6, 16, 16], outline=color, width=1)
        draw.line([15, 15, 19, 19], fill=color, width=2)
        draw.line([9, 11, 13, 11], fill=color, width=1)
    elif name == "zoom-scan":
        # Desenha uma lupa com moldura
        draw.ellipse([6, 6, 16, 16], outline=color, width=1)
        draw.line([15, 15, 19, 19], fill=color, width=2)
        draw.rectangle([4, 4, 20, 20], outline=color, width=1)
    elif name == "zoom-reset":
        # Desenha uma lupa com círculo
        draw.ellipse([6, 6, 16, 16], outline=color, width=1)
        draw.line([15, 15, 19, 19], fill=color, width=2)
        draw.ellipse([9, 9, 13, 13], outline=color, width=1)
    elif name == "help":
        # Desenha um ponto de interrogação
        draw.ellipse([4, 4, 20, 20], outline=color, width=1)
        draw.arc([8, 8, 16, 14], 0, 180, fill=color, width=1)
        draw.line([12, 14, 12, 16], fill=color, width=1)
        draw.ellipse([11, 17, 13, 19], fill=color)
    elif name == "info-circle":
        # Desenha um círculo de informação
        draw.ellipse([4, 4, 20, 20], outline=color, width=1)
        draw.line([12, 10, 12, 16], fill=color, width=1)
        draw.ellipse([11, 7, 13, 9], fill=color)
    elif name == "file-type-pdf":
        # Desenha um ícone de PDF
        draw.rectangle([6, 2, 18, 22], outline=color, width=1)
        draw.polygon([6, 2, 14, 2, 18, 6, 18, 22, 6, 22], outline=color, width=1)
        draw.line([14, 2, 14, 6, 18, 6], fill=color, width=1)
        draw.text((12, 14), "PDF", fill=color, anchor="mm")
    elif name == "file-plus":
        # Desenha um ícone de arquivo com +
        draw.rectangle([6, 2, 18, 22], outline=color, width=1)
        draw.polygon([6, 2, 14, 2, 18, 6, 18, 22, 6, 22], outline=color, width=1)
        draw.line([14, 2, 14, 6, 18, 6], fill=color, width=1)
        draw.line([9, 14, 15, 14], fill=color, width=1)
        draw.line([12, 11, 12, 17], fill=color, width=1)
    elif name == "chevron-left":
        # Desenha uma seta para a esquerda
        draw.line([14, 8, 10, 12, 14, 16], fill=color, width=1)
    elif name == "chevron-right":
        # Desenha uma seta para a direita
        draw.line([10, 8, 14, 12, 10, 16], fill=color, width=1)
    elif name == "eraser":
        # Desenha uma borracha
        draw.rectangle([6, 10, 18, 16], outline=color, width=1)
        draw.line([6, 13, 18, 13], fill=color, width=1)
    elif name == "eye":
        # Desenha um olho
        draw.ellipse([4, 8, 20, 16], outline=color, width=1)
        draw.ellipse([10, 10, 14, 14], fill=color)
    elif name == "eye-off":
        # Desenha um olho fechado
        draw.line([4, 4, 20, 20], fill=color, width=1)
        draw.arc([4, 8, 20, 16], 0, 180, fill=color, width=1)

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
    theme_frame = ttk.Frame(parent, style='Toolbar.TFrame')
    theme_frame.pack(side=tk.RIGHT, padx=10, pady=5)
    
    # Carrega ícones para o tema
    icon_size = (24, 24)
    
    # Cria ícones para os temas
    light_icon = Image.new('RGBA', icon_size, (0, 0, 0, 0))
    light_draw = ImageDraw.Draw(light_icon)
    light_draw.ellipse([4, 4, 20, 20], outline="#4263eb", width=1)
    light_draw.ellipse([8, 8, 16, 16], fill="#4263eb")
    
    dark_icon = Image.new('RGBA', icon_size, (0, 0, 0, 0))
    dark_draw = ImageDraw.Draw(dark_icon)
    dark_draw.arc([4, 4, 20, 20], 0, 180, fill="#4263eb", width=1)
    dark_draw.arc([4, 4, 20, 20], 180, 360, fill="#4263eb", width=1)
    
    light_icon_img = ImageTk.PhotoImage(light_icon)
    dark_icon_img = ImageTk.PhotoImage(dark_icon)
    
    # Determina qual ícone usar
    icon_img = dark_icon_img if current_theme == "light" else light_icon_img
    theme_text = "Modo Escuro" if current_theme == "light" else "Modo Claro"
    
    theme_button = ttk.Button(theme_frame, text=theme_text, image=icon_img, compound=tk.LEFT,
                             command=toggle_callback, padding=(5, 2))
    theme_button.image = icon_img
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
    # Cria um frame para a tela de boas-vindas com bordas arredondadas
    welcome_frame = ttk.Frame(parent, style='Card.TFrame')
    
    # Carrega os ícones
    icons = load_tabler_icons()
    
    # Adiciona o conteúdo da tela de boas-vindas
    logo_label = ttk.Label(welcome_frame, text="Document Protector", style='Logo.TLabel')
    logo_label.pack(pady=(20, 10))
    
    subtitle = ttk.Label(welcome_frame, text="Proteja seus documentos sensíveis", style='Subtitle.TLabel')
    subtitle.pack(pady=(0, 20))
    
    # Botões de ação
    button_frame = ttk.Frame(welcome_frame, style='Card.TFrame')
    button_frame.pack(pady=20)
    
    open_image_btn = ttk.Button(button_frame, text="Abrir Imagem", image=icons["file"], compound=tk.LEFT,
                               style='Accent.TButton', command=open_image_callback, width=20)
    open_image_btn.image = icons["file"]
    open_image_btn.pack(side=tk.LEFT, padx=10)
    
    if pdf_available:
        open_pdf_btn = ttk.Button(button_frame, text="Abrir PDF", image=icons["file-type-pdf"], compound=tk.LEFT,
                                 style='Accent.TButton', command=open_pdf_callback, width=20)
        open_pdf_btn.image = icons["file-type-pdf"]
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

def add_tooltip(widget, text):
    """
    Adiciona uma dica de ferramenta a um widget.
    
    Args:
        widget: Widget que receberá a dica
        text: Texto da dica
    """
    tooltip = None
    
    def enter(event):
        nonlocal tooltip
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Cria uma janela de dica
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(tooltip, text=text, background="#343a40", foreground="#f8f9fa",
                         relief="solid", borderwidth=1, padding=(5, 3))
        label.pack()
    
    def leave(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None
    
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

