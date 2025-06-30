"""
Gerenciador de configurações - Carrega e salva configurações do usuário
"""

import os
import json
from typing import Dict, Any

class SettingsManager:
    """Gerencia as configurações da aplicação"""
    
    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = config_file
        self.default_settings = {
            "apps_directory": "apps",
            "theme": "light",
            "window_size": [1000, 700],
            "window_position": [100, 100],
            "auto_scan": True,
            "scan_interval": 30,  # segundos
            "show_language": True,
            "show_tags": True,
            "sort_by": "name",  # name, language, date
            "sort_order": "asc",  # asc, desc
            "recent_apps_count": 10,
            "favorites": [],
            "shortcuts": {},
            "ui": {
                "font_size": 10,
                "font_family": "Arial",
                "list_item_height": 30,
                "show_icons": True,
                "alternating_colors": True
            },
            "execution": {
                "wait_for_completion": False,
                "show_output": False,
                "max_output_lines": 100,
                "timeout": 30
            },
            "advanced": {
                "debug_mode": False,
                "log_level": "INFO",
                "backup_data": True,
                "auto_update": False
            }
        }
        
    def load_settings(self) -> Dict[str, Any]:
        """Carrega as configurações do arquivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    
                # Mesclar com configurações padrão
                return self.merge_settings(self.default_settings, loaded_settings)
            else:
                # Criar arquivo com configurações padrão
                self.save_settings(self.default_settings)
                return self.default_settings
                
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            return self.default_settings
            
    def save_settings(self, settings: Dict[str, Any]):
        """Salva as configurações no arquivo JSON"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            
    def merge_settings(self, default: Dict, loaded: Dict) -> Dict:
        """Mescla configurações carregadas com as padrão"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key].update(value)
            else:
                result[key] = value
        return result
        
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Obtém uma configuração específica"""
        settings = self.load_settings()
        
        # Suporte para chaves aninhadas (ex: "ui.font_size")
        keys = key.split('.')
        value = settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set_setting(self, key: str, value: Any):
        """Define uma configuração específica"""
        settings = self.load_settings()
        
        # Suporte para chaves aninhadas
        keys = key.split('.')
        current = settings
        
        # Navegar até o nível anterior ao último
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
            
        # Definir o valor
        current[keys[-1]] = value
        
        # Salvar configurações
        self.save_settings(settings)
        
    def reset_settings(self):
        """Reseta as configurações para os valores padrão"""
        self.save_settings(self.default_settings)
        
    def get_apps_directory(self) -> str:
        """Obtém o diretório de aplicativos configurado"""
        return self.get_setting("apps_directory", "apps")
        
    def set_apps_directory(self, directory: str):
        """Define o diretório de aplicativos"""
        self.set_setting("apps_directory", directory)
        
    def get_theme(self) -> str:
        """Obtém o tema configurado"""
        return self.get_setting("theme", "light")
        
    def set_theme(self, theme: str):
        """Define o tema"""
        self.set_setting("theme", theme)
        
    def get_window_size(self) -> list:
        """Obtém o tamanho da janela"""
        return self.get_setting("window_size", [1000, 700])
        
    def set_window_size(self, width: int, height: int):
        """Define o tamanho da janela"""
        self.set_setting("window_size", [width, height])
        
    def get_window_position(self) -> list:
        """Obtém a posição da janela"""
        return self.get_setting("window_position", [100, 100])
        
    def set_window_position(self, x: int, y: int):
        """Define a posição da janela"""
        self.set_setting("window_position", [x, y])
        
    def add_favorite(self, app_path: str):
        """Adiciona um aplicativo aos favoritos"""
        favorites = self.get_setting("favorites", [])
        if app_path not in favorites:
            favorites.append(app_path)
            self.set_setting("favorites", favorites)
            
    def remove_favorite(self, app_path: str):
        """Remove um aplicativo dos favoritos"""
        favorites = self.get_setting("favorites", [])
        if app_path in favorites:
            favorites.remove(app_path)
            self.set_setting("favorites", favorites)
            
    def is_favorite(self, app_path: str) -> bool:
        """Verifica se um aplicativo é favorito"""
        favorites = self.get_setting("favorites", [])
        return app_path in favorites
        
    def add_shortcut(self, key: str, app_path: str):
        """Adiciona um atalho de teclado"""
        shortcuts = self.get_setting("shortcuts", {})
        shortcuts[key] = app_path
        self.set_setting("shortcuts", shortcuts)
        
    def remove_shortcut(self, key: str):
        """Remove um atalho de teclado"""
        shortcuts = self.get_setting("shortcuts", {})
        if key in shortcuts:
            del shortcuts[key]
            self.set_setting("shortcuts", shortcuts)
            
    def get_shortcuts(self) -> Dict[str, str]:
        """Obtém todos os atalhos configurados"""
        return self.get_setting("shortcuts", {})
        
    def export_settings(self, file_path: str):
        """Exporta as configurações para um arquivo"""
        try:
            settings = self.load_settings()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao exportar configurações: {e}")
            
    def import_settings(self, file_path: str):
        """Importa configurações de um arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            self.save_settings(settings)
        except Exception as e:
            print(f"Erro ao importar configurações: {e}")
            
    def validate_settings(self) -> bool:
        """Valida as configurações carregadas"""
        try:
            settings = self.load_settings()
            
            # Verificar campos obrigatórios
            required_fields = ["apps_directory", "theme", "window_size", "window_position"]
            for field in required_fields:
                if field not in settings:
                    print(f"Campo obrigatório ausente: {field}")
                    return False
                    
            # Validar tipos
            if not isinstance(settings["window_size"], list) or len(settings["window_size"]) != 2:
                print("window_size deve ser uma lista com 2 elementos")
                return False
                
            if not isinstance(settings["window_position"], list) or len(settings["window_position"]) != 2:
                print("window_position deve ser uma lista com 2 elementos")
                return False
                
            return True
            
        except Exception as e:
            print(f"Erro ao validar configurações: {e}")
            return False 