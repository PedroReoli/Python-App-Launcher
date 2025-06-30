#!/usr/bin/env python3
"""
Python App Launcher - Main Entry Point
Aplicação principal para lançamento de aplicativos com interface PyQt profissional
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from gui.main_window import MainWindow
from core.app_manager import AppManager
from config.settings_manager import SettingsManager

def setup_environment():
    """Configura o ambiente da aplicação"""
    # Criar diretórios necessários se não existirem
    directories = ['apps', 'data', 'assets', 'config']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Configurar o diretório de trabalho
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)

def main():
    """Função principal da aplicação"""
    # Configurar o ambiente
    setup_environment()
    
    # Criar aplicação PyQt
    app = QApplication(sys.argv)
    app.setApplicationName("Python App Launcher")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AppLauncher")
    
    # Configurar ícone da aplicação (se existir)
    icon_path = os.path.join('assets', 'app_icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Configurar estilo da aplicação
    app.setStyle('Fusion')  # Estilo moderno e consistente
    
    # Carregar configurações
    settings_manager = SettingsManager()
    settings = settings_manager.load_settings()
    
    # Inicializar gerenciador de aplicativos
    app_manager = AppManager(settings.get('apps_directory', 'apps'))
    
    # Criar e exibir janela principal
    main_window = MainWindow(app_manager, settings_manager)
    main_window.show()
    
    # Executar loop principal da aplicação
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 