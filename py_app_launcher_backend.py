import os
import sys
import subprocess
import threading
import datetime
import json
import shutil
import psutil
import signal
import re
import time
import importlib
import pkg_resources
import platform
import random
from collections import defaultdict
import traceback

# Para notificações no Windows
if platform.system() == "Windows":
    try:
        from win10toast import ToastNotifier
    except ImportError:
        pass

class PyAppLauncherBackend:
    def __init__(self):
        # Diretórios
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.apps_dir = os.path.join(self.base_dir, "apps")
        self.data_dir = os.path.join(self.base_dir, "data")
        self.config_dir = os.path.join(self.data_dir, "config")
        
        # Criar diretórios se não existirem
        for directory in [self.apps_dir, self.data_dir, self.config_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # Arquivos de dados
        self.metadata_file = os.path.join(self.base_dir, "metadata.json")
        self.runtime_file = os.path.join(self.data_dir, "runtime_data.json")
        self.groups_file = os.path.join(self.data_dir, "groups.json")
        self.kanban_file = os.path.join(self.data_dir, "kanban.json")
        self.stats_file = os.path.join(self.data_dir, "statistics.json")
        self.config_file = os.path.join(self.config_dir, "settings.json")
        
        # Variáveis
        self.apps = []
        self.running_processes = {}  # Armazenar processos em execução {file: process}
        self.process_metrics = {}    # Armazenar métricas de processos {file: {cpu: [], memory: [], timestamps: []}}
        self.groups = {}  # Grupos de aplicativos {group_name: [app_files]}
        self.kanban_states = {}  # Estados kanban {file: state}
        self.kanban_columns = []  # Colunas personalizadas do kanban
        
        # Carregar dados
        self.load_metadata()
        self.load_runtime_data()
        self.load_groups()
        self.load_kanban_states()
        self.load_config()
        
        # Inicializar notificador para Windows
        self.notifier = None
        if platform.system() == "Windows":
            try:
                self.notifier = ToastNotifier()
            except:
                print("Não foi possível inicializar o notificador do Windows. Instale o pacote win10toast.")
        
        # Inicializar monitoramento
        self.monitoring_active = True
        
    def load_metadata(self):
        """Carregar metadados das aplicações"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.app_metadata = json.load(f)
            except:
                self.app_metadata = {}
        else:
            self.app_metadata = {}
    
    def save_metadata(self):
        """Salvar metadados das aplicações"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.app_metadata, f, indent=2, ensure_ascii=False)
    
    def load_runtime_data(self):
        """Carregar dados de execução"""
        if os.path.exists(self.runtime_file):
            try:
                with open(self.runtime_file, 'r', encoding='utf-8') as f:
                    self.runtime_data = json.load(f)
            except:
                self.runtime_data = {}
        else:
            self.runtime_data = {}
    
    def save_runtime_data(self):
        """Salvar dados de execução"""
        with open(self.runtime_file, 'w', encoding='utf-8') as f:
            json.dump(self.runtime_data, f, indent=2, ensure_ascii=False)
    
    def load_groups(self):
        """Carregar grupos de aplicações"""
        if os.path.exists(self.groups_file):
            try:
                with open(self.groups_file, 'r', encoding='utf-8') as f:
                    self.groups = json.load(f)
            except:
                self.groups = {"Todos": []}
        else:
            self.groups = {"Todos": []}
    
    def save_groups(self):
        """Salvar grupos de aplicações"""
        with open(self.groups_file, 'w', encoding='utf-8') as f:
            json.dump(self.groups, f, indent=2, ensure_ascii=False)
    
    def load_kanban_states(self):
        """Carregar estados do kanban"""
        if os.path.exists(self.kanban_file):
            try:
                with open(self.kanban_file, 'r', encoding='utf-8') as f:
                    kanban_data = json.load(f)
                    self.kanban_states = kanban_data.get("states", {})
                    self.kanban_columns = kanban_data.get("columns", ["A Fazer", "Em Progresso", "Concluído"])
            except:
                self.kanban_states = {}
                self.kanban_columns = ["A Fazer", "Em Progresso", "Concluído"]
        else:
            self.kanban_states = {}
            self.kanban_columns = ["A Fazer", "Em Progresso", "Concluído"]
    
    def save_kanban_states(self):
        """Salvar estados do kanban"""
        kanban_data = {
            "states": self.kanban_states,
            "columns": self.kanban_columns
        }
        with open(self.kanban_file, 'w', encoding='utf-8') as f:
            json.dump(kanban_data, f, indent=2, ensure_ascii=False)
    
    def load_config(self):
        """Carregar configurações"""
        default_config = {
            "theme": "light",
            "colors": {
                "light": {
                    "primary": "#4a6baf",
                    "primary_light": "#7590d5",
                    "secondary": "#00b894",
                    "accent": "#fdcb6e",
                    "danger": "#e74c3c",
                    "background": "#f8f9fa",
                    "card": "#ffffff",
                    "text": "#2d3436",
                    "text_light": "#636e72",
                    "border": "#e0e0e0",
                    "kanban_todo": "#f8d7da",
                    "kanban_doing": "#fff3cd",
                    "kanban_done": "#d4edda"
                },
                "dark": {
                    "primary": "#5c7cbe",
                    "primary_light": "#8ba3e0",
                    "secondary": "#00d1a0",
                    "accent": "#ffd87f",
                    "danger": "#ff6b6b",
                    "background": "#1e272e",
                    "card": "#2d3436",
                    "text": "#f5f6fa",
                    "text_light": "#dfe6e9",
                    "border": "#485460",
                    "kanban_todo": "#6b2d2d",
                    "kanban_doing": "#6b5d2d",
                    "kanban_done": "#2d6b41"
                }
            },
            "font": {
                "family": "Arial",
                "size": {
                    "small": 9,
                    "normal": 10,
                    "large": 12,
                    "title": 16
                }
            },
            "layout": {
                "card_size": 160,
                "max_columns": 5,
                "show_description_in_grid": True,
                "compact_list_view": False,
                "show_tags_in_list": True,
                "show_metrics_in_list": True
            },
            "behavior": {
                "confirm_app_close": True,
                "auto_check_dependencies": True,
                "show_notifications": True,
                "auto_refresh_interval": 0,  # 0 = desativado, em segundos
                "default_view": "grid",  # grid, list, kanban
                "default_sort": "name",  # name, last_run, run_count
                "default_sort_direction": "asc"  # asc, desc
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    
                    # Garantir que todas as chaves existam
                    for key in default_config:
                        if key not in self.config:
                            self.config[key] = default_config[key]
                    
                    # Garantir que todas as cores existam
                    for theme in ["light", "dark"]:
                        if theme not in self.config["colors"]:
                            self.config["colors"][theme] = default_config["colors"][theme]
                        else:
                            for color in default_config["colors"][theme]:
                                if color not in self.config["colors"][theme]:
                                    self.config["colors"][theme][color] = default_config["colors"][theme][color]
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Salvar configurações"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_colors(self):
        """Obter cores do tema atual"""
        theme = self.config["theme"]
        return self.config["colors"][theme]
    
    def scan_apps(self):
        """Escanear diretório de aplicações"""
        self.apps = []
        categories = set(["Todos"])
        
        # Listar arquivos Python na pasta apps
        for file in os.listdir(self.apps_dir):
            if file.endswith(".py") and file != "__init__.py":
                app_path = os.path.join(self.apps_dir, file)
                app_name = os.path.splitext(file)[0].replace("_", " ").title()
                
                # Verificar se há metadados para este app
                if file in self.app_metadata:
                    metadata = self.app_metadata[file]
                    app_name = metadata.get("name", app_name)
                    description = metadata.get("description", "")
                    category = metadata.get("category", "Outros")
                    color = metadata.get("color", self.get_random_color())
                    icon = metadata.get("icon", "")
                    tags = metadata.get("tags", [])
                    dependencies = metadata.get("dependencies", [])
                else:
                    # Criar metadados padrão
                    description = self.extract_description(app_path)
                    category = "Outros"
                    color = self.get_random_color()
                    icon = ""
                    tags = []
                    dependencies = self.extract_dependencies(app_path)
                    
                    self.app_metadata[file] = {
                        "name": app_name,
                        "description": description,
                        "category": category,
                        "color": color,
                        "icon": icon,
                        "tags": tags,
                        "dependencies": dependencies
                    }
                
                # Adicionar categoria
                categories.add(category)
                
                # Verificar dados de execução
                if file in self.runtime_data:
                    runtime = self.runtime_data[file]
                    last_run = runtime.get("last_run", "Nunca")
                    run_count = runtime.get("run_count", 0)
                    total_runtime = runtime.get("total_runtime", 0)
                    avg_cpu = runtime.get("avg_cpu", 0)
                    avg_memory = runtime.get("avg_memory", 0)
                else:
                    last_run = "Nunca"
                    run_count = 0
                    total_runtime = 0
                    avg_cpu = 0
                    avg_memory = 0
                    
                    self.runtime_data[file] = {
                        "last_run": last_run,
                        "run_count": run_count,
                        "total_runtime": total_runtime,
                        "avg_cpu": avg_cpu,
                        "avg_memory": avg_memory,
                        "run_history": []
                    }
                
                # Verificar estado kanban
                kanban_state = self.kanban_states.get(file, self.kanban_columns[0] if self.kanban_columns else "A Fazer")
                if file not in self.kanban_states:
                    self.kanban_states[file] = kanban_state
                
                # Adicionar app à lista
                self.apps.append({
                    "file": file,
                    "path": app_path,
                    "name": app_name,
                    "description": description,
                    "category": category,
                    "color": color,
                    "icon": icon,
                    "tags": tags,
                    "dependencies": dependencies,
                    "last_run": last_run,
                    "run_count": run_count,
                    "total_runtime": total_runtime,
                    "avg_cpu": avg_cpu,
                    "avg_memory": avg_memory,
                    "kanban_state": kanban_state
                })
                
                # Adicionar ao grupo "Todos" se não estiver em nenhum grupo
                in_any_group = False
                for group_name, group_files in self.groups.items():
                    if file in group_files:
                        in_any_group = True
                        break
                
                if not in_any_group and "Todos" in self.groups:
                    self.groups["Todos"].append(file)
        
        # Ordenar apps conforme configuração
        sort_key = self.config["behavior"]["default_sort"]
        reverse = self.config["behavior"]["default_sort_direction"] == "desc"
        
        if sort_key == "name":
            self.apps.sort(key=lambda x: x["name"].lower(), reverse=reverse)
        elif sort_key == "last_run":
            # Colocar "Nunca" no final
            def last_run_key(app):
                if app["last_run"] == "Nunca":
                    return "9999-99-99"
                return app["last_run"]
            self.apps.sort(key=last_run_key, reverse=reverse)
        elif sort_key == "run_count":
            self.apps.sort(key=lambda x: x["run_count"], reverse=reverse)
        
        # Salvar metadados atualizados
        self.save_metadata()
        self.save_runtime_data()
        self.save_groups()
        self.save_kanban_states()
        
        return self.apps, list(categories)
    
    def extract_description(self, file_path):
        """Extrair descrição do arquivo Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Ler apenas o início do arquivo
                
                # Procurar por docstring
                import re
                docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if docstring_match:
                    return docstring_match.group(1).strip()
                
                # Procurar por comentários
                comment_lines = []
                for line in content.split('\n')[:10]:  # Primeiras 10 linhas
                    if line.strip().startswith('#'):
                        comment_lines.append(line.strip()[1:].strip())
                
                if comment_lines:
                    return ' '.join(comment_lines)
                
                return "Aplicação Python"
        except:
            return "Aplicação Python"
    
    def extract_dependencies(self, file_path):
        """Extrair dependências do arquivo Python"""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Procurar por imports
                import_patterns = [
                    r'import\s+(\w+)',
                    r'from\s+(\w+)\s+import',
                    r'import\s+(\w+)\s+as',
                ]
                
                for pattern in import_patterns:
                    for match in re.finditer(pattern, content):
                        module = match.group(1)
                        if module not in ['os', 'sys', 'time', 're', 'json', 'datetime', 'math', 'random', 'tkinter', 'threading']:
                            dependencies.append(module)
                
                # Remover duplicatas
                dependencies = list(set(dependencies))
                
                return dependencies
        except:
            return []
    
    def get_random_color(self):
        """Gerar uma cor aleatória para o card"""
        colors = [
            "#4a6baf", "#00b894", "#fdcb6e", "#e17055", "#74b9ff",
            "#a29bfe", "#55efc4", "#fab1a0", "#81ecec", "#ff7675"
        ]
        return random.choice(colors)
    
    def run_app(self, app_file):
        """Executar uma aplicação"""
        if app_file in self.running_processes:
            return False, "Aplicação já está em execução"
        
        app = None
        for a in self.apps:
            if a["file"] == app_file:
                app = a
                break
        
        if not app:
            return False, "Aplicação não encontrada"
        
        # Verificar dependências se configurado
        if self.config["behavior"]["auto_check_dependencies"]:
            missing_deps = self.check_dependencies(app["dependencies"])
            if missing_deps:
                return False, f"Dependências faltando: {', '.join(missing_deps)}"
        
        try:
            # Registrar hora de início
            start_time = time.time()
            
            # Executar o processo
            app_path = os.path.join(self.apps_dir, app_file)
            process = subprocess.Popen([sys.executable, app_path])
            
            # Armazenar o processo
            self.running_processes[app_file] = process
            
            # Inicializar métricas para este processo
            self.process_metrics[app_file] = {
                "cpu": [],
                "memory": [],
                "timestamps": [],
                "start_time": start_time
            }
            
            # Atualizar última execução
            now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            
            if app_file in self.runtime_data:
                self.runtime_data[app_file]["last_run"] = now
                self.runtime_data[app_file]["run_count"] += 1
            else:
                self.runtime_data[app_file] = {
                    "last_run": now,
                    "run_count": 1,
                    "total_runtime": 0,
                    "avg_cpu": 0,
                    "avg_memory": 0,
                    "run_history": []
                }
            
            # Salvar dados de execução
            self.save_runtime_data()
            
            # Mostrar notificação
            if self.config["behavior"]["show_notifications"]:
                self.show_notification(f"Aplicação Iniciada", f"{app['name']} foi iniciada com sucesso.")
            
            return True, "Aplicação iniciada com sucesso"
            
        except Exception as e:
            return False, f"Erro ao executar aplicação: {str(e)}"
    
    def stop_app(self, app_file):
        """Parar uma aplicação em execução"""
        if app_file not in self.running_processes:
            return False, "Aplicação não está em execução"
        
        app = None
        for a in self.apps:
            if a["file"] == app_file:
                app = a
                break
        
        if not app:
            return False, "Aplicação não encontrada"
        
        process = self.running_processes[app_file]
        
        # Confirmar encerramento se configurado
        if self.config["behavior"]["confirm_app_close"]:
            # Esta verificação será feita na interface
            pass
        
        try:
            # Registrar métricas finais
            if app_file in self.process_metrics:
                metrics = self.process_metrics[app_file]
                start_time = metrics["start_time"]
                end_time = time.time()
                runtime = end_time - start_time
                
                # Calcular médias
                avg_cpu = sum(metrics["cpu"]) / len(metrics["cpu"]) if metrics["cpu"] else 0
                avg_memory = sum(metrics["memory"]) / len(metrics["memory"]) if metrics["memory"] else 0
                
                # Atualizar dados de execução
                if app_file in self.runtime_data:
                    self.runtime_data[app_file]["total_runtime"] += runtime
                    self.runtime_data[app_file]["avg_cpu"] = avg_cpu
                    self.runtime_data[app_file]["avg_memory"] = avg_memory
                    
                    # Adicionar ao histórico
                    run_record = {
                        "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "runtime": runtime,
                        "avg_cpu": avg_cpu,
                        "avg_memory": avg_memory
                    }
                    self.runtime_data[app_file]["run_history"].append(run_record)
                    
                    # Limitar histórico a 20 entradas
                    if len(self.runtime_data[app_file]["run_history"]) > 20:
                        self.runtime_data[app_file]["run_history"] = self.runtime_data[app_file]["run_history"][-20:]
                
                # Limpar métricas
                del self.process_metrics[app_file]
            
            # Encerrar o processo
            self.terminate_process(process)
            
            # Remover da lista de processos
            del self.running_processes[app_file]
            
            # Salvar dados de execução
            self.save_runtime_data()
            
            # Mostrar notificação
            if self.config["behavior"]["show_notifications"]:
                self.show_notification(f"Aplicação Encerrada", f"{app['name']} foi encerrada.")
            
            return True, "Aplicação encerrada com sucesso"
            
        except Exception as e:
            return False, f"Erro ao encerrar aplicação: {str(e)}"
    
    def terminate_process(self, process):
        """Encerrar um processo de forma segura"""
        try:
            # Tentar encerrar o processo principal
            if process.poll() is None:  # Se o processo ainda estiver em execução
                if sys.platform == "win32":
                    # No Windows, usamos taskkill para encerrar a árvore de processos
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
                else:
                    # No Linux/Mac, usamos psutil para encerrar a árvore de processos
                    parent = psutil.Process(process.pid)
                    for child in parent.children(recursive=True):
                        child.terminate()
                    parent.terminate()
        except:
            # Se falhar, tentar matar o processo
            try:
                process.kill()
            except:
                pass
    
    def monitor_processes(self):
        """Monitorar processos em execução para coletar métricas"""
        while self.monitoring_active:
            try:
                for file, process in list(self.running_processes.items()):
                    # Verificar se o processo ainda está em execução
                    if process.poll() is not None:
                        # Processo terminou
                        
                        # Registrar métricas finais
                        if file in self.process_metrics:
                            metrics = self.process_metrics[file]
                            start_time = metrics["start_time"]
                            end_time = time.time()
                            runtime = end_time - start_time
                            
                            # Calcular médias
                            avg_cpu = sum(metrics["cpu"]) / len(metrics["cpu"]) if metrics["cpu"] else 0
                            avg_memory = sum(metrics["memory"]) / len(metrics["memory"]) if metrics["memory"] else 0
                            
                            # Atualizar dados de execução
                            if file in self.runtime_data:
                                self.runtime_data[file]["total_runtime"] += runtime
                                self.runtime_data[file]["avg_cpu"] = avg_cpu
                                self.runtime_data[file]["avg_memory"] = avg_memory
                                
                                # Adicionar ao histórico
                                run_record = {
                                    "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                                    "runtime": runtime,
                                    "avg_cpu": avg_cpu,
                                    "avg_memory": avg_memory
                                }
                                self.runtime_data[file]["run_history"].append(run_record)
                                
                                # Limitar histórico a 20 entradas
                                if len(self.runtime_data[file]["run_history"]) > 20:
                                    self.runtime_data[file]["run_history"] = self.runtime_data[file]["run_history"][-20:]
                            
                            # Limpar métricas
                            del self.process_metrics[file]
                        
                        # Remover da lista de processos
                        del self.running_processes[file]
                        
                        # Salvar dados de execução
                        self.save_runtime_data()
                        
                        continue
                    
                    try:
                        # Obter métricas do processo
                        proc = psutil.Process(process.pid)
                        
                        # CPU e memória
                        cpu_percent = proc.cpu_percent(interval=0.1)
                        memory_info = proc.memory_info()
                        memory_mb = memory_info.rss / (1024 * 1024)  # Converter para MB
                        
                        # Armazenar métricas
                        if file in self.process_metrics:
                            self.process_metrics[file]["cpu"].append(cpu_percent)
                            self.process_metrics[file]["memory"].append(memory_mb)
                            self.process_metrics[file]["timestamps"].append(time.time())
                    except:
                        # Processo pode ter terminado entre as verificações
                        pass
            except Exception as e:
                print(f"Erro no monitoramento: {str(e)}")
            
            # Aguardar antes da próxima verificação
            time.sleep(2)
    
    def update_app_metadata(self, app_file, name=None, description=None, category=None, color=None, tags=None, dependencies=None):
        """Atualizar metadados de uma aplicação"""
        if app_file not in self.app_metadata:
            return False, "Aplicação não encontrada"
        
        try:
            # Atualizar campos fornecidos
            if name is not None:
                self.app_metadata[app_file]["name"] = name
            
            if description is not None:
                self.app_metadata[app_file]["description"] = description
            
            if category is not None:
                self.app_metadata[app_file]["category"] = category
            
            if color is not None:
                self.app_metadata[app_file]["color"] = color
            
            if tags is not None:
                self.app_metadata[app_file]["tags"] = tags
            
            if dependencies is not None:
                self.app_metadata[app_file]["dependencies"] = dependencies
            
            # Salvar metadados
            self.save_metadata()
            
            # Atualizar app na lista
            for app in self.apps:
                if app["file"] == app_file:
                    if name is not None:
                        app["name"] = name
                    if description is not None:
                        app["description"] = description
                    if category is not None:
                        app["category"] = category
                    if color is not None:
                        app["color"] = color
                    if tags is not None:
                        app["tags"] = tags
                    if dependencies is not None:
                        app["dependencies"] = dependencies
                    break
            
            return True, "Metadados atualizados com sucesso"
        except Exception as e:
            return False, f"Erro ao atualizar metadados: {str(e)}"
    
    def update_kanban_state(self, app_file, state):
        """Atualizar estado kanban de uma aplicação"""
        if state not in self.kanban_columns:
            return False, "Estado kanban inválido"
        
        try:
            # Atualizar estado
            self.kanban_states[app_file] = state
            
            # Salvar estados
            self.save_kanban_states()
            
            # Atualizar app na lista
            for app in self.apps:
                if app["file"] == app_file:
                    app["kanban_state"] = state
                    break
            
            return True, "Estado kanban atualizado com sucesso"
        except Exception as e:
            return False, f"Erro ao atualizar estado kanban: {str(e)}"
    
    def update_kanban_columns(self, columns):
        """Atualizar colunas do kanban"""
        if not columns or len(columns) < 1:
            return False, "É necessário pelo menos uma coluna"
        
        try:
            old_columns = self.kanban_columns.copy()
            self.kanban_columns = columns
            
            # Mapear estados antigos para novos
            if len(old_columns) > 0:
                for app_file, state in self.kanban_states.items():
                    if state not in columns:
                        # Se o estado não existe mais, usar o primeiro
                        self.kanban_states[app_file] = columns[0]
            
            # Salvar estados
            self.save_kanban_states()
            
            # Atualizar apps na lista
            for app in self.apps:
                if app["kanban_state"] not in columns:
                    app["kanban_state"] = columns[0]
            
            return True, "Colunas kanban atualizadas com sucesso"
        except Exception as e:
            return False, f"Erro ao atualizar colunas kanban: {str(e)}"
    
    def create_group(self, group_name):
        """Criar um novo grupo"""
        if not group_name or group_name in self.groups:
            return False, "Nome de grupo inválido ou já existe"
        
        try:
            self.groups[group_name] = []
            self.save_groups()
            return True, "Grupo criado com sucesso"
        except Exception as e:
            return False, f"Erro ao criar grupo: {str(e)}"
    
    def delete_group(self, group_name):
        """Excluir um grupo"""
        if group_name not in self.groups or group_name == "Todos":
            return False, "Grupo não encontrado ou não pode ser excluído"
        
        try:
            del self.groups[group_name]
            self.save_groups()
            return True, "Grupo excluído com sucesso"
        except Exception as e:
            return False, f"Erro ao excluir grupo: {str(e)}"
    
    def rename_group(self, old_name, new_name):
        """Renomear um grupo"""
        if old_name not in self.groups or old_name == "Todos":
            return False, "Grupo não encontrado ou não pode ser renomeado"
        
        if not new_name or new_name in self.groups:
            return False, "Nome de grupo inválido ou já existe"
        
        try:
            self.groups[new_name] = self.groups[old_name]
            del self.groups[old_name]
            self.save_groups()
            return True, "Grupo renomeado com sucesso"
        except Exception as e:
            return False, f"Erro ao renomear grupo: {str(e)}"
    
    def add_app_to_group(self, app_file, group_name):
        """Adicionar aplicação a um grupo"""
        if group_name not in self.groups:
            return False, "Grupo não encontrado"
        
        try:
            if app_file not in self.groups[group_name]:
                self.groups[group_name].append(app_file)
                self.save_groups()
            return True, "Aplicação adicionada ao grupo com sucesso"
        except Exception as e:
            return False, f"Erro ao adicionar aplicação ao grupo: {str(e)}"
    
    def remove_app_from_group(self, app_file, group_name):
        """Remover aplicação de um grupo"""
        if group_name not in self.groups:
            return False, "Grupo não encontrado"
        
        try:
            if app_file in self.groups[group_name]:
                self.groups[group_name].remove(app_file)
                self.save_groups()
            return True, "Aplicação removida do grupo com sucesso"
        except Exception as e:
            return False, f"Erro ao remover aplicação do grupo: {str(e)}"
    
    def check_dependencies(self, dependencies):
        """Verificar dependências faltantes"""
        missing = []
        for dep in dependencies:
            if dep.strip():
                try:
                    importlib.import_module(dep)
                except ImportError:
                    missing.append(dep)
        return missing
    
    def install_dependencies(self, dependencies, callback=None):
        """Instalar dependências faltantes"""
        if not dependencies:
            if callback:
                callback("Todas as dependências já estão instaladas", True)
            return True, "Todas as dependências já estão instaladas"
        
        def install_thread():
            results = []
            success = True
            
            for i, dep in enumerate(dependencies):
                if callback:
                    callback(f"Instalando {dep} ({i+1}/{len(dependencies)})...", None)
                
                try:
                    # Instalar usando pip
                    process = subprocess.Popen(
                        [sys.executable, "-m", "pip", "install", dep],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Capturar saída
                    stdout, stderr = process.communicate()
                    
                    if process.returncode == 0:
                        results.append(f"Instalado com sucesso: {dep}")
                        if callback:
                            callback(f"Instalado com sucesso: {dep}", None)
                    else:
                        results.append(f"Erro ao instalar {dep}: {stderr}")
                        if callback:
                            callback(f"Erro ao instalar {dep}: {stderr}", None)
                        success = False
                    
                except Exception as e:
                    results.append(f"Erro: {str(e)}")
                    if callback:
                        callback(f"Erro: {str(e)}", None)
                    success = False
            
            if callback:
                callback("Instalação concluída", success)
            
            return success, "\n".join(results)
        
        # Iniciar thread de instalação
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
        
        return True, "Instalação iniciada"
    
    def get_installed_packages(self):
        """Obter lista de pacotes instalados"""
        try:
            packages = []
            for package in pkg_resources.working_set:
                packages.append({
                    "name": package.key,
                    "version": package.version
                })
            return sorted(packages, key=lambda p: p["name"])
        except Exception as e:
            print(f"Erro ao listar pacotes: {str(e)}")
            return []
    
    def install_package(self, package_name, callback=None):
        """Instalar pacote via pip"""
        if not package_name:
            if callback:
                callback("Nome do pacote é obrigatório", False)
            return False, "Nome do pacote é obrigatório"
        
        def install_thread():
            try:
                if callback:
                    callback(f"Instalando {package_name}...", None)
                
                process = subprocess.Popen(
                    [sys.executable, "-m", "pip", "install", package_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    if callback:
                        callback(f"Pacote {package_name} instalado com sucesso", True)
                    return True, f"Pacote {package_name} instalado com sucesso"
                else:
                    if callback:
                        callback(f"Erro ao instalar {package_name}: {stderr}", False)
                    return False, f"Erro ao instalar {package_name}: {stderr}"
            except Exception as e:
                if callback:
                    callback(f"Erro ao instalar pacote: {str(e)}", False)
                return False, f"Erro ao instalar pacote: {str(e)}"
        
        # Iniciar thread de instalação
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
        
        return True, "Instalação iniciada"
    
    def uninstall_package(self, package_name, callback=None):
        """Desinstalar pacote via pip"""
        if not package_name:
            if callback:
                callback("Nome do pacote é obrigatório", False)
            return False, "Nome do pacote é obrigatório"
        
        def uninstall_thread():
            try:
                if callback:
                    callback(f"Desinstalando {package_name}...", None)
                
                process = subprocess.Popen(
                    [sys.executable, "-m", "pip", "uninstall", "-y", package_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    if callback:
                        callback(f"Pacote {package_name} desinstalado com sucesso", True)
                    return True, f"Pacote {package_name} desinstalado com sucesso"
                else:
                    if callback:
                        callback(f"Erro ao desinstalar {package_name}: {stderr}", False)
                    return False, f"Erro ao desinstalar {package_name}: {stderr}"
            except Exception as e:
                if callback:
                    callback(f"Erro ao desinstalar pacote: {str(e)}", False)
                return False, f"Erro ao desinstalar pacote: {str(e)}"
        
        # Iniciar thread de desinstalação
        thread = threading.Thread(target=uninstall_thread)
        thread.daemon = True
        thread.start()
        
        return True, "Desinstalação iniciada"
    
    def create_new_app(self, name, filename, category, description, template, group="Todos"):
        """Criar uma nova aplicação"""
        if not name or not filename:
            return False, "Nome e nome do arquivo são obrigatórios"
        
        # Garantir que o nome do arquivo tenha extensão .py
        if not filename.endswith(".py"):
            filename += ".py"
        
        # Verificar se o arquivo já existe
        file_path = os.path.join(self.apps_dir, filename)
        if os.path.exists(file_path):
            return False, f"O arquivo {filename} já existe"
        
        try:
            # Criar arquivo com modelo
            with open(file_path, 'w', encoding='utf-8') as f:
                if template == "Básico":
                    f.write(f'"""\n{name}\n{description}\n"""\n\n')
                    f.write('def main():\n    print("Olá de ' + name + '")\n\n')
                    f.write('if __name__ == "__main__":\n    main()\n')
                elif template == "Aplicação GUI":
                    f.write(f'"""\n{name}\n{description}\n"""\n')
                    f.write('import tkinter as tk\nfrom tkinter import ttk\n\n')
                    f.write('def main():\n    root = tk.Tk()\n    root.title("' + name + '")\n')
                    f.write('    root.geometry("600x400")\n\n')
                    f.write('    # Seu código GUI aqui\n    label = ttk.Label(root, text="' + name + '")\n')
                    f.write('    label.pack(pady=20)\n\n')
                    f.write('    root.mainloop()\n\n')
                    f.write('if __name__ == "__main__":\n    main()\n')
                elif template == "Aplicação Console":
                    f.write(f'"""\n{name}\n{description}\n"""\n\n')
                    f.write('def main():\n    print("Bem-vindo ao ' + name + '")\n')
                    f.write('    # Seu código aqui\n    entrada = input("Digite algo: ")\n')
                    f.write('    print(f"Você digitou: {entrada}")\n\n')
                    f.write('if __name__ == "__main__":\n    main()\n')
                else:  # Vazio
                    f.write(f'"""\n{name}\n{description}\n"""\n\n')
                    f.write('# Seu código aqui\n')
            
            # Criar metadados
            color = self.get_random_color()
            dependencies = []
            
            self.app_metadata[filename] = {
                "name": name,
                "description": description,
                "category": category,
                "color": color,
                "icon": "",
                "tags": [],
                "dependencies": dependencies
            }
            
            # Criar dados de execução
            self.runtime_data[filename] = {
                "last_run": "Nunca",
                "run_count": 0,
                "total_runtime": 0,
                "avg_cpu": 0,
                "avg_memory": 0,
                "run_history": []
            }
            
            # Definir estado kanban
            self.kanban_states[filename] = self.kanban_columns[0] if self.kanban_columns else "A Fazer"
            
            # Adicionar ao grupo
            if group in self.groups:
                self.groups[group].append(filename)
            
            # Salvar dados
            self.save_metadata()
            self.save_runtime_data()
            self.save_kanban_states()
            self.save_groups()
            
            return True, f"Aplicação {name} criada com sucesso"
            
        except Exception as e:
            return False, f"Não foi possível criar o arquivo: {str(e)}"
    
    def open_code(self, app_file):
        """Abrir código da aplicação no editor padrão"""
        app_path = os.path.join(self.apps_dir, app_file)
        if not os.path.exists(app_path):
            return False, "Arquivo não encontrado"
        
        try:
            if sys.platform == "win32":
                os.startfile(app_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.call(["open", app_path])
            else:  # Linux
                subprocess.call(["xdg-open", app_path])
            return True, "Arquivo aberto com sucesso"
        except Exception as e:
            return False, f"Não foi possível abrir o arquivo: {str(e)}"
    
    def show_notification(self, title, message):
        """Mostrar notificação no Windows"""
        if platform.system() == "Windows" and self.notifier:
            try:
                self.notifier.show_toast(
                    title,
                    message,
                    duration=5,
                    threaded=True
                )
                return True
            except Exception as e:
                print(f"Erro ao mostrar notificação: {str(e)}")
                return False
        return False
    
    def get_app_statistics(self):
        """Obter estatísticas gerais das aplicações"""
        total_apps = len(self.apps)
        total_runs = sum(app["run_count"] for app in self.apps)
        total_runtime = sum(app["total_runtime"] for app in self.apps)
        
        # Aplicações mais usadas
        top_apps = sorted(self.apps, key=lambda x: x["run_count"], reverse=True)[:5]
        
        # Aplicações por categoria
        categories = defaultdict(int)
        for app in self.apps:
            categories[app["category"]] += 1
        
        # Execuções por dia
        executions_by_day = defaultdict(int)
        for app_file, runtime_data in self.runtime_data.items():
            for run in runtime_data.get("run_history", []):
                date = run.get("date", "").split()[0]  # Pegar apenas a data
                if date:
                    executions_by_day[date] += 1
        
        # Ordenar por data
        dates = sorted(executions_by_day.keys())
        executions = [executions_by_day[date] for date in dates]
        
        return {
            "total_apps": total_apps,
            "total_runs": total_runs,
            "total_runtime": total_runtime,
            "top_apps": top_apps,
            "categories": dict(categories),
            "executions_by_day": {
                "dates": dates,
                "executions": executions
            }
        }
    
    def get_app_metrics(self, app_file):
        """Obter métricas detalhadas de uma aplicação"""
        app = None
        for a in self.apps:
            if a["file"] == app_file:
                app = a
                break
        
        if not app:
            return None
        
        # Histórico de execução
        history = []
        if app_file in self.runtime_data:
            history = self.runtime_data[app_file].get("run_history", [])
        
        # Métricas em tempo real
        realtime_metrics = None
        if app_file in self.process_metrics:
            metrics = self.process_metrics[app_file]
            realtime_metrics = {
                "cpu": metrics["cpu"],
                "memory": metrics["memory"],
                "timestamps": metrics["timestamps"]
            }
        
        return {
            "app": app,
            "history": history,
            "realtime_metrics": realtime_metrics
        }
    
    def shutdown(self):
        """Encerrar o backend"""
        self.monitoring_active = False
        
        # Encerrar processos em execução
        for process in self.running_processes.values():
            self.terminate_process(process)
        
        # Salvar dados
        self.save_metadata()
        self.save_runtime_data()
        self.save_groups()
        self.save_kanban_states()
        self.save_config()