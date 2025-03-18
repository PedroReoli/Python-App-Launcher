"""
Módulo para gerenciamento de preferências do usuário
Contém a classe UserPreferences que gerencia as configurações do usuário
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
            "keyboard_shortcuts": {
                "save": "<Control-s>",
                "open": "<Control-o>",
                "undo": "<Control-z>",
                "redo": "<Control-y>",
                "clear": "<Control-r>",
                "zoom_in": "<Control-plus>",
                "zoom_out": "<Control-minus>",
                "zoom_reset": "<Control-0>"
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
                    for key, value in loaded_prefs.items():
                        if key in self.preferences:
                            if isinstance(value, dict) and isinstance(self.preferences[key], dict):
                                # Para dicionários aninhados, atualiza as chaves individualmente
                                for subkey, subvalue in value.items():
                                    if subkey in self.preferences[key]:
                                        self.preferences[key][subkey] = subvalue
                            else:
                                self.preferences[key] = value
                                
                return True
        except Exception as e:
            print(f"Erro ao carregar preferências: {e}")
        return False
    
    def save(self) -> bool:
        """
        Salva as preferências no arquivo.
        
        Returns:
            True se as preferências foram salvas com sucesso, False caso contrário
        """
        try:
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
        # Suporta chaves aninhadas como "keyboard_shortcuts.save"
        if "." in key:
            main_key, sub_key = key.split(".", 1)
            if main_key in self.preferences and isinstance(self.preferences[main_key], dict):
                return self.preferences[main_key].get(sub_key, default)
            return default
        return self.preferences.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Define uma preferência.
        
        Args:
            key: Chave da preferência
            value: Valor da preferência
        """
        # Suporta chaves aninhadas como "keyboard_shortcuts.save"
        if "." in key:
            main_key, sub_key = key.split(".", 1)
            if main_key in self.preferences and isinstance(self.preferences[main_key], dict):
                self.preferences[main_key][sub_key] = value
            else:
                self.preferences[main_key] = {sub_key: value}
        else:
            self.preferences[key] = value

