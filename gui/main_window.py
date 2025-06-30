"""
Interface gráfica principal do Python App Launcher
Janela principal com design simples e compacto usando cards
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QLabel, QComboBox,
    QScrollArea, QFrame, QGridLayout, QMessageBox,
    QFileDialog, QAction, QMenu, QToolBar, QStatusBar,
    QCheckBox, QButtonGroup, QRadioButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor, QPainter, QBrush

class AppCard(QFrame):
    """Card de aplicativo individual"""
    
    def __init__(self, app_data, app_manager, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.app_manager = app_manager
        self.setup_card()
        
    def setup_card(self):
        """Configura o card do aplicativo"""
        self.setFixedSize(200, 120)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        self.setMidLineWidth(1)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Cabeçalho com ícone e nome
        header_layout = QHBoxLayout()
        
        # Ícone da linguagem
        language_icon = QLabel()
        icon_path = self.get_language_icon(self.app_data.get('inferred_language', 'Desconhecida'))
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            language_icon.setPixmap(pixmap)
        else:
            language_icon.setText("📄")
        language_icon.setFixedSize(24, 24)
        header_layout.addWidget(language_icon)
        
        # Nome do aplicativo
        name_label = QLabel(self.app_data['name'])
        name_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        header_layout.addWidget(name_label, 1)
        
        # Botão favorito
        self.favorite_btn = QPushButton()
        self.favorite_btn.setFixedSize(20, 20)
        self.favorite_btn.setStyleSheet("QPushButton { border: none; background: transparent; }")
        self.update_favorite_icon()
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        header_layout.addWidget(self.favorite_btn)
        
        layout.addLayout(header_layout)
        
        # Linguagem
        language_label = QLabel(self.app_data.get('inferred_language', 'Desconhecida'))
        language_label.setFont(QFont("Segoe UI", 8))
        language_label.setStyleSheet("color: #666;")
        layout.addWidget(language_label)
        
        # Categoria (se existir)
        category = self.app_manager.user_config.get("app_categories", {}).get(self.app_data['path'], "")
        if category:
            category_label = QLabel(f"Categoria: {category}")
            category_label.setFont(QFont("Segoe UI", 8))
            category_label.setStyleSheet("color: #888;")
            layout.addWidget(category_label)
        
        # Tags (se existirem)
        tags = self.app_manager.user_config.get("app_tags", {}).get(self.app_data['path'], [])
        if tags:
            tags_text = ", ".join(tags[:3])  # Mostrar apenas as 3 primeiras tags
            if len(tags) > 3:
                tags_text += "..."
            tags_label = QLabel(f"Tags: {tags_text}")
            tags_label.setFont(QFont("Segoe UI", 8))
            tags_label.setStyleSheet("color: #888;")
            layout.addWidget(tags_label)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        run_btn = QPushButton("▶ Executar")
        run_btn.setFixedHeight(25)
        run_btn.clicked.connect(self.run_app)
        buttons_layout.addWidget(run_btn)
        
        config_btn = QPushButton("⚙")
        config_btn.setFixedSize(25, 25)
        config_btn.setToolTip("Configurar app")
        config_btn.clicked.connect(self.configure_app)
        buttons_layout.addWidget(config_btn)
        
        layout.addLayout(buttons_layout)
        
        # Aplicar estilo
        self.apply_card_style()
        
    def get_language_icon(self, language):
        """Obtém o caminho do ícone da linguagem"""
        icon_map = {
            'Python': 'assets/icons/python.svg',
            'JavaScript': 'assets/icons/javascript.svg',
            'Java': 'assets/icons/java.svg',
            'C++': 'assets/icons/cpp.svg',
            'C': 'assets/icons/c.svg',
            'C#': 'assets/icons/csharp.svg',
            'Go': 'assets/icons/go.svg',
            'Rust': 'assets/icons/rust.svg',
            'Ruby': 'assets/icons/ruby.svg',
            'PHP': 'assets/icons/php.svg',
            'Swift': 'assets/icons/swift.svg',
            'Kotlin': 'assets/icons/kotlin.svg',
            'Shell': 'assets/icons/bash.svg',
            'PowerShell': 'assets/icons/powershell.svg',
            'Windows': 'assets/icons/windows.svg',
            'macOS': 'assets/icons/apple.svg'
        }
        return icon_map.get(language, 'assets/icons/file.svg')
        
    def apply_card_style(self):
        """Aplica o estilo do card"""
        is_favorite = self.app_manager.is_favorite(self.app_data['path'])
        
        if is_favorite:
            self.setStyleSheet("""
                QFrame {
                    background-color: #fff3cd;
                    border: 2px solid #ffc107;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: #fff8e1;
                    border: 2px solid #ffb300;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: #f5f5f5;
                    border: 2px solid #bdbdbd;
                }
            """)
            
    def update_favorite_icon(self):
        """Atualiza o ícone de favorito"""
        is_favorite = self.app_manager.is_favorite(self.app_data['path'])
        if is_favorite:
            self.favorite_btn.setText("★")
            self.favorite_btn.setStyleSheet("color: #ffc107; font-size: 16px;")
        else:
            self.favorite_btn.setText("☆")
            self.favorite_btn.setStyleSheet("color: #ccc; font-size: 16px;")
            
    def toggle_favorite(self):
        """Alterna o status de favorito"""
        self.app_manager.toggle_favorite(self.app_data['path'])
        self.update_favorite_icon()
        self.apply_card_style()
        
    def run_app(self):
        """Executa o aplicativo"""
        try:
            self.app_manager.run_app(self.app_data)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao executar {self.app_data['name']}: {str(e)}")
            
    def configure_app(self):
        """Abre diálogo de configuração do app"""
        dialog = AppConfigDialog(self.app_data, self.app_manager, self)
        dialog.exec_()

class AppConfigDialog(QFrame):
    """Diálogo de configuração do aplicativo"""
    
    def __init__(self, app_data, app_manager, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.app_manager = app_manager
        self.setup_dialog()
        
    def setup_dialog(self):
        """Configura o diálogo"""
        self.setWindowTitle(f"Configurar: {self.app_data['name']}")
        self.setFixedSize(400, 300)
        self.setFrameStyle(QFrame.Box)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel(f"Configurar: {self.app_data['name']}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Categoria
        layout.addWidget(QLabel("Categoria:"))
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(self.app_manager.user_config.get("categories", []))
        current_category = self.app_manager.user_config.get("app_categories", {}).get(self.app_data['path'], "")
        if current_category:
            self.category_combo.setCurrentText(current_category)
        layout.addWidget(self.category_combo)
        
        # Tags
        layout.addWidget(QLabel("Tags (separadas por vírgula):"))
        self.tags_edit = QLineEdit()
        current_tags = self.app_manager.user_config.get("app_tags", {}).get(self.app_data['path'], [])
        self.tags_edit.setText(", ".join(current_tags))
        layout.addWidget(self.tags_edit)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Salvar")
        save_btn.clicked.connect(self.save_config)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.close)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
    def save_config(self):
        """Salva a configuração"""
        # Salvar categoria
        category = self.category_combo.currentText().strip()
        if category:
            self.app_manager.add_app_category(self.app_data['path'], category)
        else:
            self.app_manager.remove_app_category(self.app_data['path'])
            
        # Salvar tags
        tags_text = self.tags_edit.text().strip()
        if tags_text:
            tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
            # Limpar tags antigas
            current_tags = self.app_manager.user_config.get("app_tags", {}).get(self.app_data['path'], [])
            for tag in current_tags:
                self.app_manager.remove_app_tag(self.app_data['path'], tag)
            # Adicionar novas tags
            for tag in tags:
                self.app_manager.add_app_tag(self.app_data['path'], tag)
        else:
            # Remover todas as tags
            current_tags = self.app_manager.user_config.get("app_tags", {}).get(self.app_data['path'], [])
            for tag in current_tags:
                self.app_manager.remove_app_tag(self.app_data['path'], tag)
                
        self.close()

class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self, app_manager, settings_manager):
        super().__init__()
        self.app_manager = app_manager
        self.settings_manager = settings_manager
        self.current_apps = []
        self.filtered_apps = []
        self.app_cards = []
        
        self.init_ui()
        self.setup_connections()
        self.load_apps()
        
    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Python App Launcher")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Configurar widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Barra de ferramentas
        self.create_toolbar()
        
        # Barra de pesquisa e filtros
        self.create_search_bar(main_layout)
        
        # Área de cards
        self.create_cards_area(main_layout)
        
        # Barra de status
        self.create_status_bar()
        
        # Aplicar tema
        self.apply_theme()
        
    def create_toolbar(self):
        """Cria a barra de ferramentas"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Ação de atualizar
        refresh_action = QAction("🔄 Atualizar", self)
        refresh_action.setStatusTip("Atualizar lista de aplicativos")
        refresh_action.triggered.connect(self.load_apps)
        toolbar.addAction(refresh_action)
        
        # Ação de configurações
        settings_action = QAction("⚙ Configurações", self)
        settings_action.setStatusTip("Abrir configurações")
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
        
        toolbar.addSeparator()
        
        # Ação de exportar config
        export_action = QAction("📤 Exportar Config", self)
        export_action.setStatusTip("Exportar configurações")
        export_action.triggered.connect(self.export_config)
        toolbar.addAction(export_action)
        
        # Ação de importar config
        import_action = QAction("📥 Importar Config", self)
        import_action.setStatusTip("Importar configurações")
        import_action.triggered.connect(self.import_config)
        toolbar.addAction(import_action)
        
    def create_search_bar(self, parent_layout):
        """Cria a barra de pesquisa e filtros"""
        search_frame = QFrame()
        search_frame.setFrameStyle(QFrame.StyledPanel)
        search_layout = QHBoxLayout(search_frame)
        
        # Campo de pesquisa
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Pesquisar aplicativos...")
        self.search_input.textChanged.connect(self.filter_apps)
        search_layout.addWidget(self.search_input)
        
        # Filtro por linguagem
        self.language_filter = QComboBox()
        self.language_filter.addItem("Todas as linguagens")
        self.language_filter.currentTextChanged.connect(self.filter_apps)
        search_layout.addWidget(QLabel("Linguagem:"))
        search_layout.addWidget(self.language_filter)
        
        # Filtro por favoritos
        self.favorites_filter = QCheckBox("Apenas favoritos")
        self.favorites_filter.toggled.connect(self.filter_apps)
        search_layout.addWidget(self.favorites_filter)
        
        parent_layout.addWidget(search_frame)
        
    def create_cards_area(self, parent_layout):
        """Cria a área de cards dos aplicativos"""
        # Scroll area para os cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget container para os cards
        self.cards_widget = QWidget()
        self.cards_layout = QGridLayout(self.cards_widget)
        self.cards_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.cards_widget)
        parent_layout.addWidget(self.scroll_area)
        
    def create_status_bar(self):
        """Cria a barra de status"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
    def apply_theme(self):
        """Aplica o tema da aplicação"""
        # Configurar paleta de cores
        palette = self.palette()
        
        # Cores principais
        palette.setColor(QPalette.Window, QColor(248, 249, 250))
        palette.setColor(QPalette.WindowText, QColor(33, 37, 41))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(33, 37, 41))
        palette.setColor(QPalette.Text, QColor(33, 37, 41))
        palette.setColor(QPalette.Button, QColor(248, 249, 250))
        palette.setColor(QPalette.ButtonText, QColor(33, 37, 41))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Highlight, QColor(13, 110, 253))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(palette)
        
    def setup_connections(self):
        """Configura as conexões de sinais"""
        pass
        
    def load_apps(self):
        """Carrega a lista de aplicativos"""
        self.status_bar.showMessage("Carregando aplicativos...")
        
        try:
            # Atualizar aplicativos
            self.app_manager.scan_apps()
            self.current_apps = self.app_manager.get_apps()
            
            # Atualizar filtros
            self.update_filters()
            
            # Aplicar filtros atuais
            self.filter_apps()
            
            self.status_bar.showMessage(f"Carregados {len(self.current_apps)} aplicativos", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar aplicativos: {str(e)}")
            self.status_bar.showMessage("Erro ao carregar aplicativos")
            
    def update_filters(self):
        """Atualiza os filtros disponíveis"""
        # Linguagens
        languages = set()
        
        for app in self.current_apps:
            lang = app.get('inferred_language', 'Desconhecida')
            languages.add(lang)
        
        # Atualizar combobox de linguagens
        current_lang = self.language_filter.currentText()
        self.language_filter.clear()
        self.language_filter.addItem("Todas as linguagens")
        self.language_filter.addItems(sorted(languages))
        
        if current_lang in [self.language_filter.itemText(i) for i in range(self.language_filter.count())]:
            self.language_filter.setCurrentText(current_lang)
            
    def filter_apps(self):
        """Filtra os aplicativos baseado nos critérios"""
        search_text = self.search_input.text().lower()
        selected_language = self.language_filter.currentText()
        show_favorites_only = self.favorites_filter.isChecked()
        
        self.filtered_apps = []
        
        for app in self.current_apps:
            # Verificar pesquisa
            name_match = search_text in app['name'].lower()
            
            # Verificar linguagem
            lang_match = (selected_language == "Todas as linguagens" or 
                         app.get('inferred_language', 'Desconhecida') == selected_language)
            
            # Verificar favoritos
            favorite_match = not show_favorites_only or self.app_manager.is_favorite(app['path'])
            
            # Adicionar se passar em todos os filtros
            if name_match and lang_match and favorite_match:
                self.filtered_apps.append(app)
        
        # Ordenar aplicativos (favoritos primeiro, depois por nome)
        self.filtered_apps.sort(key=lambda x: (
            not self.app_manager.is_favorite(x['path']),
            x['name'].lower()
        ))
        
        # Atualizar cards
        self.update_cards()
        
    def update_cards(self):
        """Atualiza os cards dos aplicativos"""
        # Limpar cards existentes
        for card in self.app_cards:
            card.deleteLater()
        self.app_cards.clear()
        
        # Criar novos cards
        row = 0
        col = 0
        max_cols = 4  # 4 cards por linha
        
        for app in self.filtered_apps:
            card = AppCard(app, self.app_manager, self.cards_widget)
            self.cards_layout.addWidget(card, row, col)
            self.app_cards.append(card)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Atualizar status
        self.status_bar.showMessage(f"Mostrando {len(self.filtered_apps)} aplicativos")
        
    def open_settings(self):
        """Abre as configurações"""
        QMessageBox.information(self, "Configurações", "Configurações serão implementadas em breve")
        
    def export_config(self):
        """Exporta a configuração do usuário"""
        filename = QFileDialog.getSaveFileName(
            self,
            "Exportar Configuração",
            "app_launcher_config.json",
            "Arquivos JSON (*.json)"
        )[0]
        
        if filename:
            if self.app_manager.export_user_config(filename):
                QMessageBox.information(self, "Sucesso", f"Configuração exportada para:\n{filename}")
            else:
                QMessageBox.critical(self, "Erro", "Falha ao exportar configuração")
                
    def import_config(self):
        """Importa a configuração do usuário"""
        filename = QFileDialog.getOpenFileName(
            self,
            "Importar Configuração",
            "",
            "Arquivos JSON (*.json)"
        )[0]
        
        if filename:
            if self.app_manager.import_user_config(filename):
                QMessageBox.information(self, "Sucesso", f"Configuração importada de:\n{filename}")
                # Recarregar aplicativos para atualizar as configurações
                self.load_apps()
            else:
                QMessageBox.critical(self, "Erro", "Falha ao importar configuração") 