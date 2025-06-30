"""
Gerenciador de aplicativos - Detecta, infere linguagens e executa aplicativos
"""

import os
import json
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Optional
import threading
import sys

class AppManager:
    """Gerencia a detecção, inferência e execução de aplicativos"""
    
    def __init__(self, apps_directory: str = "apps"):
        self.apps_directory = apps_directory
        self.data_file = "data/app_data.json"
        self.user_config_file = "data/user_config.json"
        self.apps_data = self.load_apps_data()
        self.user_config = self.load_user_config()
        
        # Mapeamento de extensões para linguagens
        self.language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.java': 'Java',
            '.jar': 'Java',
            '.exe': 'Windows',
            '.app': 'macOS',
            '.sh': 'Shell',
            '.bat': 'Batch',
            '.ps1': 'PowerShell',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.pl': 'Perl',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.clj': 'Clojure',
            '.hs': 'Haskell',
            '.ml': 'OCaml',
            '.fs': 'F#',
            '.lua': 'Lua',
            '.r': 'R',
            '.m': 'MATLAB',
            '.scm': 'Scheme',
            '.lisp': 'Lisp',
            '.pro': 'Prolog'
        }
        
        # Comandos de execução por linguagem
        self.execution_commands = {
            'Python': 'python',
            'JavaScript': 'node',
            'Java': 'java -jar',
            'Shell': 'bash',
            'Batch': 'cmd /c',
            'PowerShell': 'powershell -ExecutionPolicy Bypass -File',
            'Ruby': 'ruby',
            'PHP': 'php',
            'Perl': 'perl',
            'Go': 'go run',
            'Rust': 'cargo run',
            'C++': 'g++ -o temp && ./temp',
            'C': 'gcc -o temp && ./temp',
            'C#': 'dotnet run',
            'Swift': 'swift',
            'Kotlin': 'kotlin',
            'Scala': 'scala',
            'Clojure': 'clojure',
            'Haskell': 'ghc -o temp && ./temp',
            'OCaml': 'ocaml',
            'F#': 'dotnet fsi',
            'Lua': 'lua',
            'R': 'Rscript',
            'MATLAB': 'matlab -batch',
            'Scheme': 'guile',
            'Lisp': 'sbcl',
            'Prolog': 'swipl'
        }
        
    def load_apps_data(self) -> Dict:
        """Carrega os dados dos aplicativos do arquivo JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar dados dos aplicativos: {e}")
        
        return {"apps": []}
        
    def save_apps_data(self):
        """Salva os dados dos aplicativos no arquivo JSON"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.apps_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar dados dos aplicativos: {e}")
            
    def load_user_config(self) -> Dict:
        """Carrega a configuração do usuário"""
        try:
            if os.path.exists(self.user_config_file):
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar configuração do usuário: {e}")
        
        return {
            "categories": [],
            "tags": [],
            "favorites": [],
            "app_categories": {},
            "app_tags": {},
            "settings": {
                "theme": "light",
                "sort_by": "name",
                "show_favorites_first": True
            }
        }
        
    def save_user_config(self):
        """Salva a configuração do usuário"""
        try:
            os.makedirs(os.path.dirname(self.user_config_file), exist_ok=True)
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuração do usuário: {e}")
            
    def scan_apps(self):
        """Escaneia o diretório de aplicativos (apenas arquivos diretos, sem subpastas)"""
        if not os.path.exists(self.apps_directory):
            os.makedirs(self.apps_directory, exist_ok=True)
            return
            
        # Obter lista atual de aplicativos (apenas arquivos diretos)
        current_apps = set()
        new_apps = []
        
        try:
            # Escanear apenas arquivos diretos na pasta apps
            for item in os.listdir(self.apps_directory):
                file_path = os.path.join(self.apps_directory, item)
                
                # Verificar se é arquivo (não pasta)
                if os.path.isfile(file_path):
                    # Verificar se é um arquivo executável ou script
                    if self.is_executable_file(file_path):
                        current_apps.add(item)
                        
                        # Verificar se é um novo aplicativo
                        if not self.app_exists(item):
                            app_data = self.analyze_app(file_path, item)
                            if app_data:
                                new_apps.append(app_data)
                                
                                # Instalar requirements automaticamente
                                self.install_requirements_for_app(file_path)
        except Exception as e:
            print(f"Erro ao escanear aplicativos: {e}")
        
        # Remover aplicativos que não existem mais
        existing_apps = [app for app in self.apps_data["apps"] 
                        if app["path"] in current_apps]
        
        # Adicionar novos aplicativos
        existing_apps.extend(new_apps)
        
        # Atualizar dados
        self.apps_data["apps"] = existing_apps
        self.save_apps_data()
        
    def install_requirements_for_app(self, app_path: str):
        """Instala requirements automaticamente para um aplicativo"""
        try:
            app_dir = os.path.dirname(app_path)
            
            # Verificar requirements.txt para Python
            requirements_file = os.path.join(app_dir, "requirements.txt")
            if os.path.exists(requirements_file):
                print(f"📦 Instalando requirements para: {os.path.basename(app_path)}")
                self.install_python_requirements(requirements_file)
            
            # Verificar package.json para Node.js
            package_file = os.path.join(app_dir, "package.json")
            if os.path.exists(package_file):
                print(f"📦 Instalando dependências Node.js para: {os.path.basename(app_path)}")
                self.install_node_dependencies(app_dir)
                
            # Verificar Gemfile para Ruby
            gemfile = os.path.join(app_dir, "Gemfile")
            if os.path.exists(gemfile):
                print(f"📦 Instalando gems para: {os.path.basename(app_path)}")
                self.install_ruby_gems(app_dir)
                
            # Verificar composer.json para PHP
            composer_file = os.path.join(app_dir, "composer.json")
            if os.path.exists(composer_file):
                print(f"📦 Instalando dependências PHP para: {os.path.basename(app_path)}")
                self.install_php_dependencies(app_dir)
                
        except Exception as e:
            print(f"❌ Erro ao instalar requirements para {app_path}: {e}")
            
    def install_python_requirements(self, requirements_file: str):
        """Instala requirements Python"""
        try:
            cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Requirements Python instalados com sucesso")
            else:
                print(f"⚠️ Aviso na instalação Python: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout na instalação de requirements Python")
        except Exception as e:
            print(f"❌ Erro na instalação Python: {e}")
            
    def install_node_dependencies(self, app_dir: str):
        """Instala dependências Node.js"""
        try:
            # Verificar se npm está disponível
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ npm não encontrado, pulando instalação Node.js")
                return
                
            cmd = ["npm", "install"]
            result = subprocess.run(cmd, cwd=app_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Dependências Node.js instaladas com sucesso")
            else:
                print(f"⚠️ Aviso na instalação Node.js: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout na instalação de dependências Node.js")
        except Exception as e:
            print(f"❌ Erro na instalação Node.js: {e}")
            
    def install_ruby_gems(self, app_dir: str):
        """Instala gems Ruby"""
        try:
            # Verificar se bundler está disponível
            result = subprocess.run(["bundle", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ Bundler não encontrado, pulando instalação Ruby")
                return
                
            cmd = ["bundle", "install"]
            result = subprocess.run(cmd, cwd=app_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Gems Ruby instaladas com sucesso")
            else:
                print(f"⚠️ Aviso na instalação Ruby: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout na instalação de gems Ruby")
        except Exception as e:
            print(f"❌ Erro na instalação Ruby: {e}")
            
    def install_php_dependencies(self, app_dir: str):
        """Instala dependências PHP"""
        try:
            # Verificar se composer está disponível
            result = subprocess.run(["composer", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ Composer não encontrado, pulando instalação PHP")
                return
                
            cmd = ["composer", "install"]
            result = subprocess.run(cmd, cwd=app_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Dependências PHP instaladas com sucesso")
            else:
                print(f"⚠️ Aviso na instalação PHP: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout na instalação de dependências PHP")
        except Exception as e:
            print(f"❌ Erro na instalação PHP: {e}")
        
    def is_executable_file(self, file_path: str) -> bool:
        """Verifica se um arquivo é executável ou script"""
        # Verificar extensões conhecidas
        ext = os.path.splitext(file_path)[1].lower()
        if ext in self.language_map:
            return True
            
        # Verificar se é executável no sistema
        if platform.system() == "Windows":
            return ext == '.exe' or ext == '.bat' or ext == '.ps1'
        else:
            return os.access(file_path, os.X_OK)
            
    def app_exists(self, relative_path: str) -> bool:
        """Verifica se um aplicativo já existe na base de dados"""
        return any(app["path"] == relative_path for app in self.apps_data["apps"])
        
    def analyze_app(self, file_path: str, relative_path: str) -> Optional[Dict]:
        """Analisa um aplicativo e extrai suas informações"""
        try:
            # Obter nome do aplicativo
            name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Inferir linguagem
            inferred_language = self.infer_language(file_path)
            
            # Obter comando de execução
            execution_command = self.get_execution_command(inferred_language, file_path)
            
            # Verificar se tem requirements
            has_requirements = self.check_requirements(file_path)
            
            # Criar dados do aplicativo
            app_data = {
                "name": name,
                "path": relative_path,
                "full_path": file_path,
                "inferred_language": inferred_language,
                "execution_command_prefix": execution_command,
                "has_requirements": has_requirements,
                "requirements_installed": False
            }
            
            return app_data
            
        except Exception as e:
            print(f"Erro ao analisar aplicativo {file_path}: {e}")
            return None
            
    def check_requirements(self, file_path: str) -> Dict:
        """Verifica se o aplicativo tem arquivos de requirements"""
        app_dir = os.path.dirname(file_path)
        requirements = {
            "python": os.path.exists(os.path.join(app_dir, "requirements.txt")),
            "node": os.path.exists(os.path.join(app_dir, "package.json")),
            "ruby": os.path.exists(os.path.join(app_dir, "Gemfile")),
            "php": os.path.exists(os.path.join(app_dir, "composer.json")),
            "go": os.path.exists(os.path.join(app_dir, "go.mod")),
            "rust": os.path.exists(os.path.join(app_dir, "Cargo.toml")),
            "java": os.path.exists(os.path.join(app_dir, "pom.xml")) or os.path.exists(os.path.join(app_dir, "build.gradle"))
        }
        return requirements
            
    def infer_language(self, file_path: str) -> str:
        """Inferir a linguagem de programação baseada na extensão e conteúdo"""
        ext = os.path.splitext(file_path)[1].lower()
        
        # Verificar mapeamento de extensões
        if ext in self.language_map:
            return self.language_map[ext]
            
        # Tentar inferir pelo conteúdo (para arquivos sem extensão)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()
                
                # Verificar shebang
                if first_line.startswith('#!'):
                    if 'python' in first_line:
                        return 'Python'
                    elif 'node' in first_line:
                        return 'JavaScript'
                    elif 'bash' in first_line or 'sh' in first_line:
                        return 'Shell'
                    elif 'ruby' in first_line:
                        return 'Ruby'
                    elif 'perl' in first_line:
                        return 'Perl'
                    elif 'php' in first_line:
                        return 'PHP'
                        
        except Exception:
            pass
            
        return "Desconhecida"
        
    def get_execution_command(self, language: str, file_path: str) -> str:
        """Obtém o comando de execução para uma linguagem"""
        if language in self.execution_commands:
            base_command = self.execution_commands[language]
            
            # Casos especiais
            if language == 'Java' and file_path.endswith('.jar'):
                return f"{base_command} \"{file_path}\""
            elif language in ['C++', 'C', 'Haskell']:
                return f"{base_command} \"{file_path}\""
            else:
                return f"{base_command} \"{file_path}\""
                
        return f"\"{file_path}\""
        
    def get_apps(self) -> List[Dict]:
        """Retorna a lista de aplicativos"""
        return self.apps_data.get("apps", [])
        
    def run_app(self, app_data: Dict):
        """Executa um aplicativo"""
        try:
            full_path = app_data.get('full_path', app_data['path'])
            execution_command = app_data.get('execution_command_prefix', '')
            
            # Verificar e instalar requirements antes de executar
            if app_data.get('has_requirements') and not app_data.get('requirements_installed'):
                print(f"🔧 Verificando requirements para {app_data['name']}...")
                self.install_requirements_for_app(full_path)
                app_data['requirements_installed'] = True
                self.save_apps_data()
            
            # Construir comando completo
            if execution_command:
                # Para comandos que precisam do caminho completo
                if execution_command.endswith('"'):
                    command = f"{execution_command[:-1]} \"{full_path}\""
                else:
                    command = f"{execution_command} \"{full_path}\""
            else:
                command = f"\"{full_path}\""
                
            # Executar aplicativo
            if platform.system() == "Windows":
                # No Windows, usar shell=True para executar arquivos .exe
                subprocess.Popen(command, shell=True, 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # No Linux/Mac, executar normalmente
                subprocess.Popen(command, shell=True)
                
        except Exception as e:
            raise Exception(f"Erro ao executar aplicativo: {str(e)}")
            
    def add_app_category(self, app_path: str, category: str):
        """Adiciona uma categoria a um aplicativo"""
        if category not in self.user_config["categories"]:
            self.user_config["categories"].append(category)
            
        self.user_config["app_categories"][app_path] = category
        self.save_user_config()
        
    def remove_app_category(self, app_path: str):
        """Remove a categoria de um aplicativo"""
        if app_path in self.user_config["app_categories"]:
            del self.user_config["app_categories"][app_path]
            self.save_user_config()
            
    def add_app_tag(self, app_path: str, tag: str):
        """Adiciona uma tag a um aplicativo"""
        if tag not in self.user_config["tags"]:
            self.user_config["tags"].append(tag)
            
        if app_path not in self.user_config["app_tags"]:
            self.user_config["app_tags"][app_path] = []
            
        if tag not in self.user_config["app_tags"][app_path]:
            self.user_config["app_tags"][app_path].append(tag)
            self.save_user_config()
            
    def remove_app_tag(self, app_path: str, tag: str):
        """Remove uma tag de um aplicativo"""
        if app_path in self.user_config["app_tags"] and tag in self.user_config["app_tags"][app_path]:
            self.user_config["app_tags"][app_path].remove(tag)
            self.save_user_config()
            
    def toggle_favorite(self, app_path: str):
        """Alterna o status de favorito de um aplicativo"""
        if app_path in self.user_config["favorites"]:
            self.user_config["favorites"].remove(app_path)
        else:
            self.user_config["favorites"].append(app_path)
        self.save_user_config()
        
    def is_favorite(self, app_path: str) -> bool:
        """Verifica se um aplicativo é favorito"""
        return app_path in self.user_config["favorites"]
        
    def get_app_by_path(self, app_path: str) -> Optional[Dict]:
        """Obtém um aplicativo pelo caminho"""
        for app in self.apps_data["apps"]:
            if app["path"] == app_path:
                return app
        return None
        
    def export_user_config(self, file_path: str):
        """Exporta a configuração do usuário"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao exportar configuração: {e}")
            return False
            
    def import_user_config(self, file_path: str):
        """Importa a configuração do usuário"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            self.user_config.update(imported_config)
            self.save_user_config()
            return True
        except Exception as e:
            print(f"Erro ao importar configuração: {e}")
            return False 