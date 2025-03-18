"""
Classe principal da aplicação Document Protector
Gerencia a interface gráfica e coordena os outros componentes
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import threading
import time
from PIL import Image, ImageTk
import sys

from .image_processor import ImageProcessor
from .history_manager import OptimizedHistoryManager
from .preferences import UserPreferences
from .pdf_manager import PDFManager
from .auto_save import AutoSaveManager
from .ui_components import create_modern_ui, create_theme_switcher
from .ui_theme import set_theme, LIGHT_THEME, DARK_THEME

class DocumentProtector:
    """
    Aplicação principal para proteção de documentos.
    Gerencia a interface gráfica e coordena as outras classes.
    """
    
    def __init__(self, root):
        """
        Inicializa a aplicação.
        
        Args:
            root: Janela principal do Tkinter
        """
        self.root = root
        self.user_prefs = UserPreferences()
        
        # Configura o tema
        self.current_theme = self.user_prefs.get("theme", "light")
        set_theme(self.root, LIGHT_THEME if self.current_theme == "light" else DARK_THEME)
        
        self.setup_variables()
        self.create_ui()
        self.setup_bindings()
        self.setup_auto_save()
        
        # Exibe a tela de boas-vindas
        self.show_welcome_screen()
        
    def setup_variables(self):
        """Inicializa todas as variáveis da aplicação"""
        # Processador de imagem
        self.image_processor = ImageProcessor()
        
        # Gerenciador de histórico otimizado
        self.history_manager = OptimizedHistoryManager()
        
        # Estado da aplicação
        self.drawing = False
        self.last_x, self.last_y = 0, 0
        self.start_x, self.start_y = 0, 0
        
        # Configurações da ferramenta
        self.current_tool = "brush"
        self.brush_size = self.user_prefs.get("brush_size", 20)
        self.blur_intensity = self.user_prefs.get("blur_intensity", 15)
        self.blur_iterations = self.user_prefs.get("blur_iterations", 5)
        
        # Configurações de visualização
        self.canvas_width = 800
        self.canvas_height = 600
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.drag_start_x, self.drag_start_y = 0, 0
        
        # Estado do arquivo
        self.file_path = None
        self.is_saved = True
        self.status_message = "Pronto"
        
        # Configurações de autosave
        self.auto_save_enabled = self.user_prefs.get("auto_save_enabled", False)
        self.auto_save_interval = self.user_prefs.get("auto_save_interval", 5)
        self.auto_save_path = None
        
        # PDF
        self.pdf_pages = []
        self.current_page_index = 0
        
        # Thread para processamento em segundo plano
        self.processing_thread = None
        
        # Debounce para otimização
        self.debounce_timer = None
        self.preview_update_interval = 150  # ms - Aumentado para reduzir a frequência de atualização
        
        # Preview
        self.show_preview = self.user_prefs.get("show_preview", True)
        
        # Cache para a imagem processada
        self.processed_image_cache = None
        self.cache_valid = False
        
        # Referências para componentes da UI
        self.ui_components = {}
        
        # Imagem atual no canvas
        self.tk_image = None
        
    def create_ui(self):
        """Cria a interface do usuário"""
        # Configura o protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Cria a interface moderna
        self.ui_components = create_modern_ui(
            self.root,
            self.open_image,
            self.open_pdf,
            self.save_image,
            self.save_image_as,
            self.prev_page,
            self.next_page,
            self.toggle_autosave,
            self.update_autosave_interval,
            self.undo,
            self.redo,
            self.clear_all,
            self.detect_and_blur_sensitive_info,
            self.change_tool,
            self.update_brush_size,
            self.update_blur_intensity,
            self.update_blur_iterations,
            self.toggle_preview,
            self.zoom_in,
            self.zoom_out,
            self.zoom_fit,
            self.zoom_reset,
            self.show_lgpd_info,
            self.brush_size,
            self.blur_intensity,
            self.blur_iterations,
            self.auto_save_enabled,
            self.auto_save_interval,
            self.show_preview,
            self.current_tool,
            self.current_theme
        )
        
        # Adiciona o alternador de tema
        self.theme_switcher = create_theme_switcher(
            self.ui_components['toolbar_frame'],
            self.toggle_theme,
            self.current_theme
        )
        
        # Atualiza as referências para componentes importantes
        self.canvas = self.ui_components['canvas']
        self.history_canvas = self.ui_components['history_canvas']
        self.status_bar = self.ui_components['status_bar']
        self.zoom_label = self.ui_components['zoom_label']
        self.page_label = self.ui_components['page_label']
        self.autosave_var = self.ui_components['autosave_var']
        self.interval_var = self.ui_components['interval_var']
        self.preview_var = self.ui_components['preview_var']
        self.tool_var = self.ui_components['tool_var']
        self.brush_size_label = self.ui_components['brush_size_label']
        self.blur_intensity_label = self.ui_components['blur_intensity_label']
        self.blur_iterations_label = self.ui_components['blur_iterations_label']
        self.brush_size_scale = self.ui_components['brush_size_scale']
        self.blur_intensity_scale = self.ui_components['blur_intensity_scale']
        self.blur_iterations_scale = self.ui_components['blur_iterations_scale']
        self.canvas_container = self.ui_components['canvas_container']
        
        # Atualiza as dimensões do canvas
        self.update_canvas_dimensions()
        
    def update_canvas_dimensions(self, event=None):
        """Atualiza as dimensões do canvas quando a janela é redimensionada"""
        if hasattr(self, 'canvas_container'):
            self.canvas_width = self.canvas_container.winfo_width()
            self.canvas_height = self.canvas_container.winfo_height()
            self.canvas.config(width=self.canvas_width, height=self.canvas_height)
            
            # Reposiciona a mensagem de boas-vindas
            if hasattr(self, 'welcome_frame') and self.welcome_frame:
                self.position_welcome_screen()
            
            # Atualiza a imagem se houver uma carregada
            if self.image_processor.current_image is not None:
                self.update_canvas(force_update=True)
        
    def toggle_theme(self):
        """Alterna entre os temas claro e escuro"""
        if self.current_theme == "light":
            self.current_theme = "dark"
            set_theme(self.root, DARK_THEME)
        else:
            self.current_theme = "light"
            set_theme(self.root, LIGHT_THEME)
            
        # Salva a preferência
        self.user_prefs.set("theme", self.current_theme)
        self.user_prefs.save()
        
        # Atualiza o canvas se houver uma imagem
        if self.image_processor.current_image is not None:
            self.update_canvas(force_update=True)
        
    def show_welcome_screen(self):
        """Exibe a tela de boas-vindas"""
        # Cria um frame para a tela de boas-vindas
        self.welcome_frame = ttk.Frame(self.canvas_container, style='Card.TFrame')
        
        # Adiciona o conteúdo da tela de boas-vindas
        logo_label = ttk.Label(self.welcome_frame, text="Document Protector", style='Logo.TLabel')
        logo_label.pack(pady=(20, 10))
        
        subtitle = ttk.Label(self.welcome_frame, text="Proteja seus documentos sensíveis", style='Subtitle.TLabel')
        subtitle.pack(pady=(0, 20))
        
        # Botões de ação
        button_frame = ttk.Frame(self.welcome_frame)
        button_frame.pack(pady=20)
        
        open_image_btn = ttk.Button(button_frame, text="Abrir Imagem", style='Accent.TButton', 
                                   command=self.open_image, width=20)
        open_image_btn.pack(side=tk.LEFT, padx=10)
        
        if PDFManager.is_available():
            open_pdf_btn = ttk.Button(button_frame, text="Abrir PDF", style='Accent.TButton', 
                                     command=self.open_pdf, width=20)
            open_pdf_btn.pack(side=tk.LEFT, padx=10)
        
        # Informações sobre a LGPD
        info_frame = ttk.Frame(self.welcome_frame, style='Card.TFrame')
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
        
        # Posiciona o frame no centro do canvas
        self.position_welcome_screen()
        
    def position_welcome_screen(self):
        """Posiciona a tela de boas-vindas no centro do canvas"""
        if hasattr(self, 'welcome_frame') and self.welcome_frame:
            self.welcome_frame.update_idletasks()  # Atualiza as dimensões
            width = self.welcome_frame.winfo_width()
            height = self.welcome_frame.winfo_height()
            
            # Calcula a posição central
            x = (self.canvas_width - width) // 2
            y = (self.canvas_height - height) // 2
            
            # Posiciona o frame
            self.welcome_frame.place(x=x, y=y)
        
    def hide_welcome_screen(self):
        """Esconde a tela de boas-vindas"""
        if hasattr(self, 'welcome_frame') and self.welcome_frame:
            self.welcome_frame.place_forget()
            self.welcome_frame = None
        
    def setup_bindings(self):
        """Configura os eventos de teclado e mouse"""
        # Eventos do mouse no canvas
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        
        # Eventos para arrastar a imagem (botão do meio ou direito)
        self.canvas.bind("<ButtonPress-2>", self.start_drag)  # Botão do meio
        self.canvas.bind("<B2-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-2>", self.stop_drag)
        
        self.canvas.bind("<ButtonPress-3>", self.start_drag)  # Botão direito
        self.canvas.bind("<B3-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-3>", self.stop_drag)
        
        # Eventos para zoom (roda do mouse)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.mouse_wheel)    # Linux (roda para cima)
        self.canvas.bind("<Button-5>", self.mouse_wheel)    # Linux (roda para baixo)
        
        # Atalhos de teclado
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<Control-s>", lambda event: self.save_image())
        self.root.bind("<Control-o>", lambda event: self.open_image())
        self.root.bind("<Control-r>", lambda event: self.clear_all())
        self.root.bind("<Control-plus>", lambda event: self.zoom_in())
        self.root.bind("<Control-minus>", lambda event: self.zoom_out())
        self.root.bind("<Control-0>", lambda event: self.zoom_reset())
        
        # Eventos para o histórico
        self.history_canvas.bind("<Button-1>", self.select_history_thumbnail)
        
        # Evento de redimensionamento da janela
        self.root.bind("<Configure>", self.update_canvas_dimensions)
        
    def setup_auto_save(self):
        """Configura o salvamento automático"""
        self.auto_save_manager = AutoSaveManager(self.auto_save)
        if self.auto_save_enabled:
            self.auto_save_manager.start()
    
    def toggle_preview(self):
        """Ativa ou desativa a prévia do efeito"""
        self.show_preview = self.preview_var.get()
        self.user_prefs.set("show_preview", self.show_preview)
        self.user_prefs.save()
    
    def toggle_autosave(self):
        """Ativa ou desativa o salvamento automático"""
        self.auto_save_enabled = self.autosave_var.get()
        self.user_prefs.set("auto_save_enabled", self.auto_save_enabled)
        
        if self.auto_save_enabled:
            if not self.file_path:
                # Se não tiver um arquivo aberto, pede para salvar primeiro
                messagebox.showinfo("Salvamento Automático", 
                                   "Para ativar o salvamento automático, salve o arquivo primeiro.")
                self.autosave_var.set(False)
                self.auto_save_enabled = False
                return
                
            self.auto_save_path = self.file_path
            self.auto_save_manager.start()
            self.update_status("Salvamento automático ativado")
        else:
            self.auto_save_manager.stop()
            self.update_status("Salvamento automático desativado")
        
        self.user_prefs.save()
    
    def update_autosave_interval(self):
        """Atualiza o intervalo de salvamento automático"""
        try:
            interval = int(self.interval_var.get())
            if interval < 1:
                interval = 1
            self.auto_save_interval = interval
            self.auto_save_manager.set_interval(interval)
            self.user_prefs.set("auto_save_interval", interval)
            self.user_prefs.save()
            self.update_status(f"Intervalo de salvamento automático: {interval} minutos")
        except ValueError:
            pass
    
    def auto_save(self):
        """Executa o salvamento automático"""
        if not self.file_path or not self.auto_save_enabled:
            return
            
        # Cria um nome de arquivo para o autosave
        if not self.auto_save_path:
            dir_name, file_name = os.path.split(self.file_path)
            name, ext = os.path.splitext(file_name)
            self.auto_save_path = os.path.join(dir_name, f"{name}_autosave{ext}")
        
        # Salva o arquivo
        success = self.image_processor.save_image(self.auto_save_path, self.blur_intensity, self.blur_iterations)
        if success:
            self.update_status(f"Salvamento automático concluído: {os.path.basename(self.auto_save_path)}")
    
    def open_image(self):
        """Abre uma imagem para edição"""
        if not self.is_saved and self.image_processor.current_image is not None:
            response = messagebox.askyesnocancel("Imagem não salva", 
                                                "Deseja salvar as alterações antes de abrir uma nova imagem?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self.save_image():
                    return
        
        # Obtém o diretório inicial das preferências do usuário
        initial_dir = self.user_prefs.get("last_directory", "")
        
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Imagens", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.tif"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_path:
            return
            
        # Salva o diretório para uso futuro
        self.user_prefs.set("last_directory", os.path.dirname(file_path))
        self.user_prefs.save()
        
        # Esconde a tela de boas-vindas
        self.hide_welcome_screen()
        
        # Mostra uma mensagem de carregamento
        self.update_status("Carregando imagem...")
        self.root.update()
        
        # Carrega a imagem em uma thread separada para não travar a interface
        def load_image_thread():
            # Carrega a imagem usando o processador
            success = self.image_processor.load_image(file_path)
            
            # Atualiza a interface na thread principal
            self.root.after(0, lambda: self.finish_image_loading(success, file_path))
        
        # Inicia a thread
        threading.Thread(target=load_image_thread, daemon=True).start()
    
    def finish_image_loading(self, success, file_path):
        """Finaliza o carregamento da imagem após a thread terminar"""
        if success:
            # Reseta o histórico
            self.history_manager.reset()
            
            # Limpa as páginas PDF
            self.pdf_pages = []
            self.current_page_index = 0
            self.update_page_label()
            
            # Adiciona o estado inicial ao histórico
            self.add_to_history()
            
            # Atualiza a visualização
            self.file_path = file_path
            self.is_saved = True
            self.update_status(f"Imagem aberta: {os.path.basename(file_path)}")
            
            # Invalida o cache
            self.cache_valid = False
            
            # Ajusta o zoom para caber a imagem na tela
            self.zoom_fit()
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
        else:
            messagebox.showerror("Erro", "Não foi possível abrir a imagem.")
            self.update_status("Erro ao abrir a imagem")
    
    def open_pdf(self):
        """Abre um arquivo PDF e converte suas páginas em imagens"""
        if not PDFManager.is_available():
            messagebox.showinfo("Suporte a PDF não disponível", 
                               "Para usar esta funcionalidade, instale a biblioteca pdf2image.")
            return
            
        if not self.is_saved and self.image_processor.current_image is not None:
            response = messagebox.askyesnocancel("Imagem não salva", 
                                                "Deseja salvar as alterações antes de abrir um novo PDF?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self.save_image():
                    return
        
        # Obtém o diretório inicial das preferências do usuário
        initial_dir = self.user_prefs.get("last_directory", "")
        
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_path:
            return
            
        # Salva o diretório para uso futuro
        self.user_prefs.set("last_directory", os.path.dirname(file_path))
        self.user_prefs.save()
        
        # Esconde a tela de boas-vindas
        self.hide_welcome_screen()
        
        # Mostra uma mensagem de carregamento
        self.update_status("Convertendo PDF para imagens... Isso pode levar alguns segundos.")
        self.root.update()
        
        # Converte o PDF em imagens em uma thread separada
        def convert_pdf():
            self.pdf_pages = PDFManager.convert_pdf_to_images(file_path)
            
            # Atualiza a interface na thread principal
            self.root.after(0, self.load_pdf_page)
        
        # Inicia a thread
        threading.Thread(target=convert_pdf, daemon=True).start()
    
    def load_pdf_page(self):
        """Carrega a página atual do PDF"""
        if not self.pdf_pages:
            self.update_status("Nenhuma página encontrada no PDF.")
            return
            
        # Carrega a primeira página
        self.current_page_index = 0
        
        # Carrega a imagem da página atual
        success = self.image_processor.load_from_array(self.pdf_pages[self.current_page_index])
        
        if success:
            # Reseta o histórico
            self.history_manager.reset()
            
            # Adiciona o estado inicial ao histórico
            self.add_to_history()
            
            # Atualiza a visualização
            self.file_path = None  # PDF não tem um arquivo de imagem associado
            self.is_saved = False
            self.update_status(f"PDF carregado - Página {self.current_page_index + 1}/{len(self.pdf_pages)}")
            
            # Invalida o cache
            self.cache_valid = False
            
            # Atualiza o label de página
            self.update_page_label()
            
            # Ajusta o zoom para caber a imagem na tela
            self.zoom_fit()
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
        else:
            messagebox.showerror("Erro", "Não foi possível carregar a página do PDF.")
    
    def update_page_label(self):
        """Atualiza o label de navegação de páginas do PDF"""
        if self.pdf_pages:
            self.page_label.config(text=f"Página {self.current_page_index + 1}/{len(self.pdf_pages)}")
        else:
            self.page_label.config(text="Página 0/0")
    
    def next_page(self):
        """Avança para a próxima página do PDF"""
        if not self.pdf_pages or self.current_page_index >= len(self.pdf_pages) - 1:
            return
            
        # Verifica se há alterações não salvas
        if not self.is_saved:
            response = messagebox.askyesnocancel("Alterações não salvas", 
                                                "Deseja salvar as alterações antes de mudar de página?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self.save_image():
                    return
        
        # Avança para a próxima página
        self.current_page_index += 1
        
        # Carrega a nova página
        success = self.image_processor.load_from_array(self.pdf_pages[self.current_page_index])
        
        if success:
            # Reseta o histórico
            self.history_manager.reset()
            
            # Adiciona o estado inicial ao histórico
            self.add_to_history()
            
            # Atualiza a visualização
            self.is_saved = True
            self.update_status(f"Página {self.current_page_index + 1}/{len(self.pdf_pages)}")
            
            # Invalida o cache
            self.cache_valid = False
            
            # Atualiza o label de página
            self.update_page_label()
            
            # Ajusta o zoom para caber a imagem na tela
            self.zoom_fit()
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
    
    def prev_page(self):
        """Volta para a página anterior do PDF"""
        if not self.pdf_pages or self.current_page_index <= 0:
            return
            
        # Verifica se há alterações não salvas
        if not self.is_saved:
            response = messagebox.askyesnocancel("Alterações não salvas", 
                                                "Deseja salvar as alterações antes de mudar de página?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self.save_image():
                    return
        
        # Volta para a página anterior
        self.current_page_index -= 1
        
        # Carrega a nova página
        success = self.image_processor.load_from_array(self.pdf_pages[self.current_page_index])
        
        if success:
            # Reseta o histórico
            self.history_manager.reset()
            
            # Adiciona o estado inicial ao histórico
            self.add_to_history()
            
            # Atualiza a visualização
            self.is_saved = True
            self.update_status(f"Página {self.current_page_index + 1}/{len(self.pdf_pages)}")
            
            # Invalida o cache
            self.cache_valid = False
            
            # Atualiza o label de página
            self.update_page_label()
            
            # Ajusta o zoom para caber a imagem na tela
            self.zoom_fit()
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
    
    def save_image(self):
        """Salva a imagem atual"""
        if self.image_processor.current_image is None:
            messagebox.showinfo("Informação", "Nenhuma imagem para salvar.")
            return False
            
        if self.file_path:
            success = self.image_processor.save_image(self.file_path, self.blur_intensity, self.blur_iterations)
            if success:
                self.is_saved = True
                self.update_status(f"Imagem salva: {os.path.basename(self.file_path)}")
                return True
            else:
                messagebox.showerror("Erro", "Não foi possível salvar a imagem.")
                return False
        else:
            return self.save_image_as()
    
    def save_image_as(self):
        """Salva a imagem com um novo nome"""
        if self.image_processor.current_image is None:
            messagebox.showinfo("Informação", "Nenhuma imagem para salvar.")
            return False
            
        # Obtém o diretório inicial das preferências do usuário
        initial_dir = self.user_prefs.get("last_directory", "")
        
        # Sugere um nome baseado no original com sufixo "_protected"
        default_filename = ""
        if self.file_path:
            filename, ext = os.path.splitext(self.file_path)
            default_filename = f"{filename}_protected{ext}"
        elif self.pdf_pages:
            default_filename = f"pagina_{self.current_page_index + 1}_protegida.png"
        
        file_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            defaultextension=".png",
            initialfile=os.path.basename(default_filename) if default_filename else "",
            filetypes=[
                ("PNG", "*.png"), 
                ("JPEG", "*.jpg;*.jpeg"), 
                ("BMP", "*.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if not file_path:
            return False
            
        # Salva o diretório para uso futuro
        self.user_prefs.set("last_directory", os.path.dirname(file_path))
        self.user_prefs.save()
        
        success = self.image_processor.save_image(file_path, self.blur_intensity, self.blur_iterations)
        if success:
            self.file_path = file_path
            self.is_saved = True
            self.update_status(f"Imagem salva como: {os.path.basename(file_path)}")
            return True
        else:
            messagebox.showerror("Erro", "Não foi possível salvar a imagem.")
            return False
    
    def update_canvas(self, force_update=False):
        """
        Atualiza o canvas com a imagem atual.
        
        Args:
            force_update: Se True, força a atualização mesmo que o cache seja válido
        """
        if self.image_processor.current_image is None:
            return
        
        # Verifica se podemos usar o cache
        if not force_update and self.cache_valid and self.processed_image_cache is not None:
            img_array = self.processed_image_cache
        else:
            # Obtém a imagem atual com os efeitos aplicados
            img_array = self.image_processor.get_current_image(
                self.blur_intensity, 
                self.blur_iterations,
                preview=self.drawing and self.show_preview
            )
            
            # Atualiza o cache
            if not self.drawing:
                self.processed_image_cache = img_array
                self.cache_valid = True
        
        if img_array is None:
            return
            
        # Converte para PIL Image
        img = self.image_processor.array_to_pil(img_array)
        
        # Aplica o zoom
        img_width, img_height = img.size
        new_width = int(img_width * self.scale_factor)
        new_height = int(img_height * self.scale_factor)
        
        if new_width > 0 and new_height > 0:
            # Redimensiona a imagem para o zoom atual
            img_resized = self.image_processor.resize_image(img, new_width, new_height)
            self.tk_image = ImageTk.PhotoImage(img_resized)
            
            # Limpa o canvas
            self.canvas.delete("all")
            
            # Calcula a posição para centralizar a imagem
            pos_x = max(0, (self.canvas_width - new_width) // 2) + self.offset_x
            pos_y = max(0, (self.canvas_height - new_height) // 2) + self.offset_y
            
            # Exibe a imagem
            self.canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self.tk_image)
            
            # Atualiza o label de zoom
            self.zoom_label.config(text=f"Zoom: {int(self.scale_factor * 100)}%")
    
    def start_draw(self, event):
        """Inicia o desenho"""
        if self.image_processor.current_image is None:
            return
            
        self.drawing = True
        
        # Obtém as coordenadas do canvas
        canvas_x, canvas_y = event.x, event.y
        
        # Converte para coordenadas da imagem
        img_x, img_y = self.canvas_to_image_coords(canvas_x, canvas_y)
        
        # Armazena a posição inicial
        self.start_x, self.start_y = img_x, img_y
        self.last_x, self.last_y = img_x, img_y
        
        # Limpa a máscara temporária
        self.image_processor.clear_temp_mask()
        
        if self.current_tool == "brush":
            # Adiciona um ponto à máscara temporária
            self.image_processor.add_to_mask(img_x, img_y, self.brush_size, temp=True)
            # Atualiza o canvas com menor frequência durante o desenho
            self.update_canvas()
        
        self.is_saved = False
        # Invalida o cache
        self.cache_valid = False
    
    def draw(self, event):
        """Continua o desenho conforme o mouse se move"""
        if not self.drawing or self.image_processor.current_image is None:
            return
            
        # Obtém as coordenadas do canvas
        canvas_x, canvas_y = event.x, event.y
        
        # Converte para coordenadas da imagem
        img_x, img_y = self.canvas_to_image_coords(canvas_x, canvas_y)
        
        # Cancela o timer de debounce anterior, se existir
        if self.debounce_timer:
            self.root.after_cancel(self.debounce_timer)
        
        if self.current_tool == "brush":
            # Desenha uma linha na máscara temporária
            self.image_processor.draw_line(
                self.last_x, self.last_y,
                img_x, img_y,
                self.brush_size
            )
            self.last_x, self.last_y = img_x, img_y
            
            # Usa debounce para atualizar o canvas apenas quando o mouse parar de se mover
            # Aumentado o intervalo para melhorar a performance
            self.debounce_timer = self.root.after(self.preview_update_interval, self.update_canvas)
            
        elif self.current_tool in ["rectangle", "ellipse"]:
            # Limpa a máscara temporária
            self.image_processor.clear_temp_mask()
            
            if self.current_tool == "rectangle":
                # Adiciona um retângulo à máscara temporária
                self.image_processor.add_rectangle_to_mask(
                    self.start_x, self.start_y, img_x, img_y, temp=True
                )
            else:  # ellipse
                # Adiciona uma elipse à máscara temporária
                self.image_processor.add_ellipse_to_mask(
                    self.start_x, self.start_y, img_x, img_y, temp=True
                )
            
            # Usa debounce para atualizar o canvas apenas quando o mouse parar de se mover
            self.debounce_timer = self.root.after(self.preview_update_interval, self.update_canvas)
    
    def stop_draw(self, event):
        """Finaliza o desenho"""
        if not self.drawing or self.image_processor.current_image is None:
            return
            
        # Transfere a máscara temporária para a máscara principal
        self.image_processor.commit_temp_mask()
        
        # Invalida o cache
        self.cache_valid = False
        
        # Atualiza o canvas com a imagem final
        self.update_canvas(force_update=True)
        
        # Adiciona ao histórico
        self.add_to_history()
        
        # Atualiza as miniaturas do histórico
        self.update_history_thumbnails()
        
        self.drawing = False
    
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """Converte coordenadas do canvas para coordenadas da imagem"""
        if self.image_processor.current_image is None:
            return 0, 0
            
        # Obtém as dimensões da imagem
        img_width, img_height = self.image_processor.get_dimensions()
        
        # Calcula o tamanho da imagem com zoom
        zoomed_width = img_width * self.scale_factor
        zoomed_height = img_height * self.scale_factor
        
        # Calcula o offset para centralizar a imagem
        offset_x = max(0, (self.canvas_width - zoomed_width) // 2) + self.offset_x
        offset_y = max(0, (self.canvas_height - zoomed_height) // 2) + self.offset_y
        
        # Converte as coordenadas
        img_x = (canvas_x - offset_x) / self.scale_factor
        img_y = (canvas_y - offset_y) / self.scale_factor
        
        # Garante que as coordenadas estão dentro dos limites da imagem
        img_x = max(0, min(img_x, img_width - 1))
        img_y = max(0, min(img_y, img_height - 1))
        
        return img_x, img_y
    
    def start_drag(self, event):
        """Inicia o arrasto da imagem"""
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def drag(self, event):
        """Arrasta a imagem pelo canvas"""
        if not self.dragging:
            return
            
        # Calcula o deslocamento
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        # Atualiza o offset
        self.offset_x += dx
        self.offset_y += dy
        
        # Atualiza as coordenadas de início do arrasto
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # Atualiza o canvas
        self.update_canvas()
    
    def stop_drag(self, event):
        """Finaliza o arrasto da imagem"""
        self.dragging = False
    
    def mouse_wheel(self, event):
        """Processa eventos da roda do mouse para zoom"""
        if self.image_processor.current_image is None:
            return
            
        # Obtém as coordenadas do mouse
        mouse_x, mouse_y = event.x, event.y
        
        # Converte para coordenadas da imagem antes do zoom
        img_x, img_y = self.canvas_to_image_coords(mouse_x, mouse_y)
        
        # Determina a direção do zoom
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            # Zoom in
            self.scale_factor *= 1.1
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            # Zoom out
            self.scale_factor /= 1.1
        
        # Limita o fator de escala
        self.scale_factor = max(0.1, min(self.scale_factor, 5.0))
        
        # Calcula o novo offset para manter o ponto sob o cursor
        new_offset_x = mouse_x - img_x * self.scale_factor
        new_offset_y = mouse_y - img_y * self.scale_factor
        
        # Ajusta o offset
        self.offset_x = new_offset_x
        self.offset_y = new_offset_y
        
        # Atualiza o canvas
        self.update_canvas()
    
    def zoom_in(self):
        """Aumenta o zoom"""
        if self.image_processor.current_image is None:
            return
            
        # Obtém o centro da visualização atual
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        
        # Converte para coordenadas da imagem
        img_center_x, img_center_y = self.canvas_to_image_coords(center_x, center_y)
        
        # Aumenta o zoom
        self.scale_factor *= 1.2
        self.scale_factor = min(self.scale_factor, 5.0)
        
        # Recalcula o offset para manter o centro
        new_offset_x = center_x - img_center_x * self.scale_factor
        new_offset_y = center_y - img_center_y * self.scale_factor
        
        self.offset_x = new_offset_x
        self.offset_y = new_offset_y
        
        # Atualiza o canvas
        self.update_canvas()
    
    def zoom_out(self):
        """Diminui o zoom"""
        if self.image_processor.current_image is None:
            return
            
        # Obtém o centro da visualização atual
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        
        # Converte para coordenadas da imagem
        img_center_x, img_center_y = self.canvas_to_image_coords(center_x, center_y)
        
        # Diminui o zoom
        self.scale_factor /= 1.2
        self.scale_factor = max(self.scale_factor, 0.1)
        
        # Recalcula o offset para manter o centro
        new_offset_x = center_x - img_center_x * self.scale_factor
        new_offset_y = center_y - img_center_y * self.scale_factor
        
        self.offset_x = new_offset_x
        self.offset_y = new_offset_y
        
        # Atualiza o canvas
        self.update_canvas()
    
    def zoom_fit(self):
        """Ajusta o zoom para caber a imagem na tela"""
        if self.image_processor.current_image is None:
            return
            
        # Obtém as dimensões da imagem
        img_width, img_height = self.image_processor.get_dimensions()
        
        # Calcula o fator de escala para caber no canvas
        scale_x = self.canvas_width / img_width
        scale_y = self.canvas_height / img_height
        
        # Usa o menor fator para garantir que a imagem inteira seja visível
        self.scale_factor = min(scale_x, scale_y) * 0.9  # 90% para dar uma margem
        
        # Reseta o offset
        self.offset_x = 0
        self.offset_y = 0
        
        # Atualiza o canvas
        self.update_canvas()
    
    def zoom_reset(self):
        """Reseta o zoom para 100%"""
        if self.image_processor.current_image is None:
            return
            
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.update_canvas()
    
    def add_to_history(self):
        """Adiciona o estado atual ao histórico"""
        if self.image_processor.mask is None:
            return
            
        self.history_manager.add(
            self.image_processor.mask,
            self.image_processor,
            self.blur_intensity,
            self.blur_iterations
        )
    
    def update_history_thumbnails(self):
        """Atualiza as miniaturas do histórico"""
        # Limpa o canvas de histórico
        self.history_canvas.delete("all")
        
        # Obtém o número de miniaturas
        num_thumbnails = len(self.history_manager.thumbnails)
        if num_thumbnails == 0:
            return
            
        # Calcula o tamanho e posição das miniaturas
        thumb_width = 80
        thumb_height = 60
        spacing = 10
        total_width = num_thumbnails * (thumb_width + spacing)
        
        # Ajusta a largura do canvas de histórico
        self.history_canvas.config(scrollregion=(0, 0, total_width, thumb_height + 20))
        
        # Desenha as miniaturas
        for i, thumbnail in enumerate(self.history_manager.thumbnails):
            if thumbnail:
                x = i * (thumb_width + spacing) + spacing
                y = 10
                
                # Desenha um retângulo ao redor da miniatura atual
                if i == self.history_manager.position:
                    self.history_canvas.create_rectangle(
                        x - 2, y - 2, x + thumb_width + 2, y + thumb_height + 2,
                        outline="#ff0000", width=2
                    )
                
                # Desenha a miniatura
                self.history_canvas.create_image(x, y, anchor=tk.NW, image=thumbnail)
                
                # Adiciona o número do estado
                self.history_canvas.create_text(
                    x + thumb_width // 2, y + thumb_height + 10,
                    text=str(i + 1),
                    fill="#333333"
                )
    
    def select_history_thumbnail(self, event):
        """Seleciona uma miniatura do histórico"""
        # Calcula o índice da miniatura clicada
        thumb_width = 80
        spacing = 10
        index = event.x // (thumb_width + spacing)
        
        if 0 <= index < len(self.history_manager.thumbnails):
            # Restaura o estado
            if index != self.history_manager.position:
                # Obtém as dimensões da imagem
                img_height, img_width = self.image_processor.mask.shape
                
                # Restaura a máscara
                if index < self.history_manager.position:
                    # Desfaz até o estado desejado
                    while self.history_manager.position > index:
                        mask = self.history_manager.undo((img_height, img_width))
                        if mask is not None:
                            self.image_processor.mask = mask
                else:
                    # Refaz até o estado desejado
                    while self.history_manager.position < index:
                        mask = self.history_manager.redo((img_height, img_width))
                        if mask is not None:
                            self.image_processor.mask = mask
                
                # Invalida o cache
                self.cache_valid = False
                
                # Atualiza o canvas
                self.update_canvas(force_update=True)
                
                # Atualiza as miniaturas do histórico
                self.update_history_thumbnails()
                
                self.is_saved = False
    
    def undo(self):
        """Desfaz a última ação"""
        if not self.history_manager.can_undo() or self.image_processor.mask is None:
            return
            
        # Obtém as dimensões da imagem
        img_height, img_width = self.image_processor.mask.shape
        
        # Obtém o estado anterior
        mask = self.history_manager.undo((img_height, img_width))
        if mask is not None:
            # Restaura o estado
            self.image_processor.mask = mask
            
            # Invalida o cache
            self.cache_valid = False
            
            # Atualiza o canvas
            self.update_canvas(force_update=True)
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
            
            self.is_saved = False
            self.update_status("Ação desfeita")
    
    def redo(self):
        """Refaz a última ação desfeita"""
        if not self.history_manager.can_redo() or self.image_processor.mask is None:
            return
            
        # Obtém as dimensões da imagem
        img_height, img_width = self.image_processor.mask.shape
        
        # Obtém o próximo estado
        mask = self.history_manager.redo((img_height, img_width))
        if mask is not None:
            # Restaura o estado
            self.image_processor.mask = mask
            
            # Invalida o cache
            self.cache_valid = False
            
            # Atualiza o canvas
            self.update_canvas(force_update=True)
            
            # Atualiza as miniaturas do histórico
            self.update_history_thumbnails()
            
            self.is_saved = False
            self.update_status("Ação refeita")
    
    def clear_all(self):
        """Limpa todas as edições"""
        if self.image_processor.current_image is None:
            return
            
        response = messagebox.askyesno("Limpar Tudo", 
                                      "Tem certeza que deseja remover todas as edições?")
        if not response:
            return
            
        # Reseta o processador de imagem
        self.image_processor.reset()
        
        # Reseta o histórico
        self.history_manager.reset()
        self.add_to_history()
        
        # Invalida o cache
        self.cache_valid = False
        
        # Atualiza o canvas
        self.update_canvas(force_update=True)
        
        # Atualiza as miniaturas do histórico
        self.update_history_thumbnails()
        
        self.is_saved = False
        self.update_status("Todas as edições foram removidas")
    
    def detect_and_blur_sensitive_info(self):
        """Detecta e borra automaticamente informações sensíveis na imagem"""
        if not self.image_processor.is_ocr_available():
            messagebox.showinfo("OCR não disponível", 
                               "Para usar esta funcionalidade, instale a biblioteca pytesseract.")
            return
            
        if self.image_processor.current_image is None:
            return
            
        # Mostra uma mensagem de carregamento
        self.update_status("Detectando informações sensíveis... Isso pode levar alguns segundos.")
        self.root.update()
        
        # Executa a detecção em uma thread separada
        def detect_sensitive_info():
            # Detecta informações sensíveis
            regions = self.image_processor.detect_sensitive_info()
            
            # Atualiza a interface na thread principal
            self.root.after(0, lambda: self.apply_blur_to_detected_regions(regions))
        
        # Inicia a thread
        threading.Thread(target=detect_sensitive_info, daemon=True).start()
    
    def apply_blur_to_detected_regions(self, regions):
        """Aplica blur às regiões sensíveis detectadas"""
        if not regions:
            messagebox.showinfo("Detecção de Informações", "Nenhuma informação sensível detectada.")
            self.update_status("Nenhuma informação sensível detectada.")
            return
            
        # Aplica blur às regiões detectadas
        self.image_processor.apply_blur_to_sensitive_regions(self.blur_intensity, self.blur_iterations)
        
        # Invalida o cache
        self.cache_valid = False
        
        # Atualiza o canvas
        self.update_canvas(force_update=True)
        
        # Adiciona ao histórico
        self.add_to_history()
        
        # Atualiza as miniaturas do histórico
        self.update_history_thumbnails()
        
        self.is_saved = False
        self.update_status(f"{len(regions)} regiões sensíveis detectadas e borradas.")
    
    def change_tool(self, tool):
        """Muda a ferramenta atual"""
        self.current_tool = tool
        self.update_status(f"Ferramenta selecionada: {tool}")
    
    def update_brush_size(self, value):
        """Atualiza o tamanho do pincel"""
        self.brush_size = int(float(value))
        self.brush_size_label.config(text=f"Tamanho do Pincel: {self.brush_size}")
        self.user_prefs.set("brush_size", self.brush_size)
        self.user_prefs.save()
        self.update_status(f"Tamanho do pincel: {self.brush_size}")
    
    def update_blur_intensity(self, value):
        """Atualiza a intensidade do blur"""
        self.blur_intensity = int(float(value))
        self.blur_intensity_label.config(text=f"Intensidade do Blur: {self.blur_intensity}")
        self.user_prefs.set("blur_intensity", self.blur_intensity)
        self.user_prefs.save()
        self.update_status(f"Intensidade do blur: {self.blur_intensity}")
        
        # Invalida o cache quando as configurações de blur mudam
        self.cache_valid = False
    
    def update_blur_iterations(self, value):
        """Atualiza o número de iterações do blur"""
        self.blur_iterations = int(float(value))
        self.blur_iterations_label.config(text=f"Iterações do Blur: {self.blur_iterations}")
        self.user_prefs.set("blur_iterations", self.blur_iterations)
        self.user_prefs.save()
        self.update_status(f"Iterações do blur: {self.blur_iterations}")
        
        # Invalida o cache quando as configurações de blur mudam
        self.cache_valid = False
    
    def update_status(self, message):
        """Atualiza a mensagem da barra de status"""
        self.status_message = message
        self.status_bar.config(text=message)
    
    def show_lgpd_info(self):
        """Exibe informações sobre a LGPD"""
        info = """
        Lei Geral de Proteção de Dados (LGPD) - Lei nº 13.709/2018
        
        A LGPD estabelece regras sobre coleta, armazenamento, tratamento e compartilhamento de dados pessoais, 
        impondo mais proteção e penalidades para o não cumprimento.
        
        Ao borrar informações sensíveis em documentos, você ajuda a:
        
        1. Proteger dados pessoais como CPF, RG, endereço, etc.
        2. Evitar o uso indevido de informações confidenciais
        3. Cumprir com as exigências legais da LGPD
        4. Proteger sua empresa de possíveis sanções
        
        Use esta ferramenta para proteger documentos antes de compartilhá-los.
        """
        
        messagebox.showinfo("Sobre a LGPD", info)
    
    def on_closing(self):
        """Manipula o evento de fechamento da janela"""
        if not self.is_saved and self.image_processor.current_image is not None:
            response = messagebox.askyesnocancel("Sair", 
                                               "Há alterações não salvas. Deseja salvar antes de sair?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self.save_image():
                    return
        
        # Para o salvamento automático
        if self.auto_save_enabled:
            self.auto_save_manager.stop()
            
        # Salva as preferências do usuário
        self.user_prefs.save()
            
        self.root.destroy()

