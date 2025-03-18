"""
Módulo para gerenciamento de preferências do usuário
Contém a classe UserPreferences que gerencia as configurações do usuário
Versão 2.0 - Suporte a mais configurações e melhor organização
"""

import os
import json
from typing import Dict, Any

class UserPreferences:
    """
    Gerencia as preferências do usuário.
    Salva e carrega configurações como tamanho do pincel, intensidade do blur, etc.
    """
    
    def __init__(self, config_file: str = "document_protector_config.json"):
        """
        Inicializa o gerenciador de preferências.
        
        Args:
            config_file: Nome do arquivo de configuração
        """
        self.config_file = config_file
        self.preferences = self._get_default_preferences()
        self.load()
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """
        Retorna as preferências padrão.
        
        Returns:
            Dicionário com as preferências padrão
        """
        return {
            "brush_size": 20,
            "blur_intensity": 15,
            "blur_iterations": 5,
            "auto_save_enabled": False,
            "auto_save_interval": 5,
            "show_preview": True,
            "last_directory": "",
            "theme": "light",
            "ui_settings": {
                "show_toolbar": True,
                "show_statusbar": True,
                "show_history": True
            },
            "keyboard_shortcuts": {
                "save": "<Control-s>",
                "open": "<Control-o>",
                "undo": "<Control-z>",
                "redo": "<Control-y>",
                "clear": "<Control-r>",
                "zoom_in": "<Control-plus>",
                "zoom_out": "<Control-minus>",
                "zoom_reset": "<Control-0>",
                "help": "<F1>"
            },
            "export_settings": {
                "default_format": "png",
                "jpeg_quality": 95,
                "png_compression": 9
            }
        }
    
    def load(self) -> bool:
        """
        Carrega as preferências do arquivo.
        
        Returns:
            True se as preferências foram carregadas com sucesso, False caso contrário
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_prefs = json.load(f)
                    
                    # Atualiza as preferências, mantendo os valores padrão para chaves ausentes
                    self._update_preferences_recursive(self.preferences, loaded_prefs)
                    
                return True
        except Exception as e:
            print(f"Erro ao carregar preferências: {e}")
        return False
    
    def _update_preferences_recursive(self, target: Dict[str, Any], source: Dict[str, Any]):
        """
        Atualiza as preferências recursivamente, mantendo os valores padrão para chaves ausentes.
        
        Args:
            target: Dicionário de destino (preferências padrão)
            source: Dicionário de origem (preferências carregadas)
        """
        for key, value in source.items():
            if key in target:
                if isinstance(value, dict) and isinstance(target[key], dict):
                    # Para dicionários aninhados, atualiza as chaves individualmente
                    self._update_preferences_recursive(target[key], value)
                else:
                    target[key] = value
    
    def save(self) -> bool:
        """
        Salva as preferências no arquivo.
        
        Returns:
            True se as preferências foram salvas com sucesso, False caso contrário
        """
        try:
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(os.path.abspath(self.config_file)), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.preferences, f, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar preferências: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém uma preferência.
        
        Args:
            key: Chave da preferência
            default: Valor padrão caso a chave não exista
            
        Returns:
            Valor da preferência ou o valor padrão
        """
        # Suporta chaves aninhadas como "ui_settings.show_toolbar"
        if "." in key:
            parts = key.split(".")
            current = self.preferences
            
            for part in parts[:-1]:
                if part in current and isinstance(current[part], dict):
                    current = current[part]
                else:
                    return default
            
            return current.get(parts[-1], default)
        
        return self.preferences.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Define uma preferência.
        
        Args:
            key: Chave da preferência
            value: Valor da preferência
        """
        # Suporta chaves aninhadas como "ui_settings.show_toolbar"
        if "." in key:
            parts = key.split(".")
            current = self.preferences
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = value
        else:
            self.preferences[key] = value

