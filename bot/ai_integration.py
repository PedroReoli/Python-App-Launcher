#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AI INTEGRATION - Python App Launcher
=======================================

Módulo de integração da IA com a aplicação principal.
Conecta o sistema de IA com a interface do usuário e funcionalidades existentes.

Características:
- ✅ Integração com interface principal
- ✅ Botões de IA na interface
- ✅ Análise automática de apps
- ✅ Sugestões inteligentes
- ✅ Documentação automática
- ✅ Chat integrado

Autor: Python App Launcher Team
Versão: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import os

from .ai_system import AISystem, OllamaManager, AppAnalyzer, DocumentationGenerator

class AIButtonManager:
    """Gerenciador de botões de IA na interface principal."""
    
    def __init__(self, parent_frame: tk.Frame, ai_system: AISystem, logger: logging.Logger):
        self.parent_frame = parent_frame
        self.ai_system = ai_system
        self.logger = logger
        self.buttons = {}
        
    def create_ai_buttons(self):
        """Cria botões de IA na interface."""
        # Frame para botões de IA
        ai_frame = tk.LabelFrame(self.parent_frame, text="🤖 Inteligência Artificial", 
                                font=("Arial", 10, "bold"), fg="#2c3e50")
        ai_frame.pack(fill="x", padx=10, pady=5)
        
        # Botões
        buttons_config = [
            ("chat", "💬 Chat com IA", "#3498db", self.open_chat),
            ("analyze", "🔍 Analisar App", "#27ae60", self.analyze_current_app),
            ("suggest", "💡 Sugerir App", "#f39c12", self.suggest_app),
            ("docs", "📚 Gerar Docs", "#9b59b6", self.generate_docs),
            ("analyze_all", "📊 Analisar Todos", "#e67e22", self.analyze_all_apps),
            ("docs_all", "📖 Docs Completas", "#1abc9c", self.generate_all_docs)
        ]
        
        for i, (key, text, color, command) in enumerate(buttons_config):
            btn = tk.Button(
                ai_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 9, "bold"),
                relief="flat",
                padx=15,
                pady=5
            )
            btn.pack(side="left", padx=5, pady=5)
            self.buttons[key] = btn
    
    def open_chat(self):
        """Abre interface de chat."""
        try:
            chat_interface = self.ai_system.create_chat_interface(self.parent_frame.winfo_toplevel())
            chat_interface.show_chat_interface()
        except Exception as e:
            self.logger.error(f"❌ Erro ao abrir chat: {e}")
            messagebox.showerror("Erro", f"Não foi possível abrir o chat: {e}")
    
    def analyze_current_app(self):
        """Analisa a aplicação atualmente selecionada."""
        # Esta função será conectada com a aplicação principal
        self.logger.info("🔍 Análise de app solicitada")
        messagebox.showinfo("Análise", "Funcionalidade será implementada na integração completa")
    
    def suggest_app(self):
        """Abre diálogo para sugerir app."""
        dialog = tk.Toplevel(self.parent_frame.winfo_toplevel())
        dialog.title("💡 Sugerir Aplicação")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Interface
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(
            main_frame,
            text="💡 Descreva seu problema ou necessidade:",
            font=("Arial", 12, "bold"),
            fg="#2c3e50"
        ).pack(pady=(0, 10))
        
        problem_text = tk.Text(main_frame, height=10, width=50, font=("Arial", 10))
        problem_text.pack(fill="both", expand=True, pady=(0, 15))
        problem_text.focus()
        
        def get_suggestion():
            problem = problem_text.get("1.0", tk.END).strip()
            if not problem:
                messagebox.showwarning("Aviso", "Por favor, descreva seu problema.")
                return
            
            dialog.destroy()
            
            # Processa em thread separada
            def process():
                try:
                    suggestion = self.ai_system.app_analyzer.suggest_app_for_problem(problem)
                    
                    # Mostra resultado
                    result_dialog = tk.Toplevel(self.parent_frame.winfo_toplevel())
                    result_dialog.title("💡 Sugestão de Aplicação")
                    result_dialog.geometry("600x500")
                    
                    # Centralizar
                    result_dialog.update_idletasks()
                    x = (result_dialog.winfo_screenwidth() // 2) - (600 // 2)
                    y = (result_dialog.winfo_screenheight() // 2) - (500 // 2)
                    result_dialog.geometry(f"600x500+{x}+{y}")
                    
                    # Interface do resultado
                    result_frame = tk.Frame(result_dialog, padx=20, pady=20)
                    result_frame.pack(fill="both", expand=True)
                    
                    tk.Label(
                        result_frame,
                        text="💡 Sugestão de Aplicação",
                        font=("Arial", 14, "bold"),
                        fg="#2c3e50"
                    ).pack(pady=(0, 15))
                    
                    # Área de texto com scroll
                    text_frame = tk.Frame(result_frame)
                    text_frame.pack(fill="both", expand=True)
                    
                    suggestion_text = tk.Text(
                        text_frame,
                        wrap=tk.WORD,
                        font=("Arial", 10),
                        bg="#f8f9fa"
                    )
                    suggestion_text.pack(side="left", fill="both", expand=True)
                    
                    scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=suggestion_text.yview)
                    scrollbar.pack(side="right", fill="y")
                    suggestion_text.config(yscrollcommand=scrollbar.set)
                    
                    suggestion_text.insert("1.0", suggestion)
                    suggestion_text.config(state="disabled")
                    
                    tk.Button(
                        result_frame,
                        text="Fechar",
                        command=result_dialog.destroy,
                        bg="#3498db",
                        fg="white",
                        font=("Arial", 10, "bold"),
                        relief="flat",
                        padx=20
                    ).pack(pady=(15, 0))
                    
                except Exception as e:
                    self.logger.error(f"❌ Erro ao gerar sugestão: {e}")
                    messagebox.showerror("Erro", f"Erro ao gerar sugestão: {e}")
            
            threading.Thread(target=process, daemon=True).start()
        
        # Botões
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        tk.Button(
            button_frame,
            text="💡 Sugerir",
            command=get_suggestion,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10),
            relief="flat",
            padx=20
        ).pack(side="left")
    
    def generate_docs(self):
        """Gera documentação da aplicação atual."""
        # Esta função será conectada com a aplicação principal
        self.logger.info("📚 Geração de docs solicitada")
        messagebox.showinfo("Documentação", "Funcionalidade será implementada na integração completa")
    
    def analyze_all_apps(self):
        """Analisa todas as aplicações."""
        def process():
            try:
                self.logger.info("🔍 Iniciando análise de todas as aplicações...")
                
                # Mostra progresso
                progress_dialog = tk.Toplevel(self.parent_frame.winfo_toplevel())
                progress_dialog.title("🔍 Analisando Aplicações")
                progress_dialog.geometry("400x150")
                progress_dialog.resizable(False, False)
                
                # Centralizar
                progress_dialog.update_idletasks()
                x = (progress_dialog.winfo_screenwidth() // 2) - (400 // 2)
                y = (progress_dialog.winfo_screenheight() // 2) - (150 // 2)
                progress_dialog.geometry(f"400x150+{x}+{y}")
                
                progress_frame = tk.Frame(progress_dialog, padx=20, pady=20)
                progress_frame.pack(fill="both", expand=True)
                
                tk.Label(
                    progress_frame,
                    text="🔍 Analisando todas as aplicações...",
                    font=("Arial", 12, "bold")
                ).pack(pady=(0, 10))
                
                progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
                progress_bar.pack(fill="x", pady=(0, 10))
                progress_bar.start()
                
                status_label = tk.Label(progress_frame, text="Iniciando análise...")
                status_label.pack()
                
                # Analisa apps
                results = self.ai_system.analyze_all_apps()
                
                progress_dialog.destroy()
                
                # Mostra resultados
                self.show_analysis_results(results)
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao analisar apps: {e}")
                messagebox.showerror("Erro", f"Erro ao analisar aplicações: {e}")
        
        threading.Thread(target=process, daemon=True).start()
    
    def generate_all_docs(self):
        """Gera documentação para todas as aplicações."""
        def process():
            try:
                self.logger.info("📚 Iniciando geração de documentação completa...")
                
                # Mostra progresso
                progress_dialog = tk.Toplevel(self.parent_frame.winfo_toplevel())
                progress_dialog.title("📚 Gerando Documentação")
                progress_dialog.geometry("400x150")
                progress_dialog.resizable(False, False)
                
                # Centralizar
                progress_dialog.update_idletasks()
                x = (progress_dialog.winfo_screenwidth() // 2) - (400 // 2)
                y = (progress_dialog.winfo_screenheight() // 2) - (150 // 2)
                progress_dialog.geometry(f"400x150+{x}+{y}")
                
                progress_frame = tk.Frame(progress_dialog, padx=20, pady=20)
                progress_frame.pack(fill="both", expand=True)
                
                tk.Label(
                    progress_frame,
                    text="📚 Gerando documentação...",
                    font=("Arial", 12, "bold")
                ).pack(pady=(0, 10))
                
                progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
                progress_bar.pack(fill="x", pady=(0, 10))
                progress_bar.start()
                
                status_label = tk.Label(progress_frame, text="Iniciando geração...")
                status_label.pack()
                
                # Gera docs
                generated_docs = self.ai_system.generate_all_documentation()
                
                progress_dialog.destroy()
                
                # Mostra resultado
                messagebox.showinfo(
                    "Documentação Gerada",
                    f"✅ Documentação gerada com sucesso!\n\n"
                    f"Arquivos criados: {len(generated_docs)}\n"
                    f"Local: pasta 'docs/'\n\n"
                    f"Arquivos:\n" + "\n".join([f"• {Path(doc).name}" for doc in generated_docs])
                )
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao gerar docs: {e}")
                messagebox.showerror("Erro", f"Erro ao gerar documentação: {e}")
        
        threading.Thread(target=process, daemon=True).start()
    
    def show_analysis_results(self, results: Dict[str, Any]):
        """Mostra resultados da análise."""
        result_dialog = tk.Toplevel(self.parent_frame.winfo_toplevel())
        result_dialog.title("📊 Resultados da Análise")
        result_dialog.geometry("800x600")
        
        # Centralizar
        result_dialog.update_idletasks()
        x = (result_dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (result_dialog.winfo_screenheight() // 2) - (600 // 2)
        result_dialog.geometry(f"800x600+{x}+{y}")
        
        # Interface
        main_frame = tk.Frame(result_dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(
            main_frame,
            text="📊 Análise de Aplicações",
            font=("Arial", 14, "bold"),
            fg="#2c3e50"
        ).pack(pady=(0, 15))
        
        # Notebook para organizar resultados
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)
        
        for app_name, analysis in results.items():
            # Frame para cada app
            app_frame = tk.Frame(notebook)
            notebook.add(app_frame, text=app_name)
            
            # Área de texto com scroll
            text_frame = tk.Frame(app_frame)
            text_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(
                text_frame,
                wrap=tk.WORD,
                font=("Consolas", 9),
                bg="#f8f9fa"
            )
            text_widget.pack(side="left", fill="both", expand=True)
            
            scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            scrollbar.pack(side="right", fill="y")
            text_widget.config(yscrollcommand=scrollbar.set)
            
            # Insere análise formatada
            if isinstance(analysis, dict):
                formatted_text = f"📊 Análise de {app_name}\n"
                formatted_text += "=" * 50 + "\n\n"
                
                for key, value in analysis.items():
                    formatted_text += f"🔹 {key.upper()}:\n"
                    if isinstance(value, (dict, list)):
                        formatted_text += str(value) + "\n\n"
                    else:
                        formatted_text += f"{value}\n\n"
            else:
                formatted_text = str(analysis)
            
            text_widget.insert("1.0", formatted_text)
            text_widget.config(state="disabled")
        
        # Botão fechar
        tk.Button(
            main_frame,
            text="Fechar",
            command=result_dialog.destroy,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20
        ).pack(pady=(15, 0))

class AIStatusBar:
    """Barra de status da IA."""
    
    def __init__(self, parent_frame: tk.Frame, ai_system: AISystem, logger: logging.Logger):
        self.parent_frame = parent_frame
        self.ai_system = ai_system
        self.logger = logger
        self.status_frame = None
        
    def create_status_bar(self):
        """Cria barra de status da IA."""
        self.status_frame = tk.Frame(self.parent_frame, bg="#34495e", height=30)
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)
        
        # Status da IA
        self.ai_status_label = tk.Label(
            self.status_frame,
            text="🤖 IA: Inicializando...",
            bg="#34495e",
            fg="#ecf0f1",
            font=("Arial", 9)
        )
        self.ai_status_label.pack(side="left", padx=10, pady=5)
        
        # Status do modelo
        self.model_status_label = tk.Label(
            self.status_frame,
            text="📦 Modelo: Verificando...",
            bg="#34495e",
            fg="#ecf0f1",
            font=("Arial", 9)
        )
        self.model_status_label.pack(side="left", padx=10, pady=5)
        
        # Botão de status
        self.status_button = tk.Button(
            self.status_frame,
            text="🔄 Verificar IA",
            command=self.check_ai_status,
            bg="#3498db",
            fg="white",
            font=("Arial", 8),
            relief="flat",
            padx=10
        )
        self.status_button.pack(side="right", padx=10, pady=5)
        
        # Verifica status inicial
        self.update_status()
    
    def update_status(self):
        """Atualiza status da IA."""
        try:
            # Verifica se Ollama está rodando
            if self.ai_system.ollama_manager.is_running:
                self.ai_status_label.config(text="🤖 IA: Ativa", fg="#27ae60")
                self.model_status_label.config(text="📦 Modelo: Llama2", fg="#27ae60")
            else:
                self.ai_status_label.config(text="🤖 IA: Inativa", fg="#e74c3c")
                self.model_status_label.config(text="📦 Modelo: Não disponível", fg="#e74c3c")
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar status: {e}")
            self.ai_status_label.config(text="🤖 IA: Erro", fg="#e74c3c")
    
    def check_ai_status(self):
        """Verifica status da IA."""
        def check():
            try:
                self.logger.info("🔍 Verificando status da IA...")
                
                # Tenta reconectar
                if not self.ai_system.ollama_manager.is_running:
                    success = self.ai_system.ollama_manager.start_ollama()
                    if success:
                        messagebox.showinfo("Status", "✅ IA reconectada com sucesso!")
                    else:
                        messagebox.showerror("Status", "❌ Falha ao reconectar IA")
                
                self.update_status()
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao verificar status: {e}")
                messagebox.showerror("Erro", f"Erro ao verificar status: {e}")
        
        threading.Thread(target=check, daemon=True).start()

class AIInterface:
    """Interface de IA integrada ao PyAppLauncher"""
    
    def __init__(self, parent_frame, ai_system: AISystem, apps_data: List[Dict]):
        self.parent_frame = parent_frame
        self.ai_system = ai_system
        self.apps_data = apps_data
        self.chat_history = []
        
        # Criar interface
        self.create_ai_interface()
        
        # Inicializar em thread separada
        self.init_thread = threading.Thread(target=self._wait_for_ai_ready, daemon=True)
        self.init_thread.start()
    
    def _wait_for_ai_ready(self):
        """Aguardar IA estar pronta"""
        while not self.ai_system.is_initialized:
            time.sleep(0.5)
        
        # Atualizar interface quando IA estiver pronta
        self.parent_frame.after(0, self._on_ai_ready)
    
    def _on_ai_ready(self):
        """Callback quando IA estiver pronta"""
        self.status_label.config(text="🤖 IA Pronta", foreground="green")
        self.chat_button.config(state="normal")
        self.analyze_button.config(state="normal")
        self.suggest_button.config(state="normal")
        self.docs_button.config(state="normal")
    
    def create_ai_interface(self):
        """Criar interface de IA compacta"""
        # Frame principal da IA
        self.ai_frame = ttk.Frame(self.parent_frame)
        self.ai_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cabeçalho da IA
        header_frame = ttk.Frame(self.ai_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Status da IA
        self.status_label = ttk.Label(header_frame, text="🤖 Inicializando IA...", 
                                     font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.LEFT)
        
        # Botões de ação rápida
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side=tk.RIGHT)
        
        # Botão de chat
        self.chat_button = ttk.Button(actions_frame, text="💬 Chat", 
                                     command=self.show_chat, state="disabled")
        self.chat_button.pack(side=tk.LEFT, padx=2)
        
        # Botão de análise
        self.analyze_button = ttk.Button(actions_frame, text="🔍 Analisar", 
                                       command=self.show_analyzer, state="disabled")
        self.analyze_button.pack(side=tk.LEFT, padx=2)
        
        # Botão de sugestões
        self.suggest_button = ttk.Button(actions_frame, text="💡 Sugerir", 
                                        command=self.show_suggestions, state="disabled")
        self.suggest_button.pack(side=tk.LEFT, padx=2)
        
        # Botão de documentação
        self.docs_button = ttk.Button(actions_frame, text="📚 Docs", 
                                     command=self.show_docs_generator, state="disabled")
        self.docs_button.pack(side=tk.LEFT, padx=2)
        
        # Área de conteúdo da IA
        self.content_frame = ttk.Frame(self.ai_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar tela inicial
        self.show_welcome_screen()
    
    def show_welcome_screen(self):
        """Mostrar tela de boas-vindas da IA"""
        # Limpar conteúdo anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Mensagem de boas-vindas
        welcome_text = """
🤖 ASSISTENTE DE IA INTEGRADO

Este assistente de IA local pode ajudar você com:

💬 CHAT INTELIGENTE
   - Perguntas sobre Python
   - Dúvidas de programação
   - Explicações técnicas

🔍 ANÁLISE DE APPS
   - Análise automática de aplicações
   - Sugestões de melhorias
   - Identificação de problemas

💡 SUGESTÕES INTELIGENTES
   - Qual app usar para cada problema
   - Recomendações baseadas em contexto
   - Alternativas e comparações

📚 GERAÇÃO DE DOCUMENTAÇÃO
   - Documentação automática
   - README personalizados
   - Guias de uso

🛠️ DEBUGGING INTELIGENTE
   - Análise de erros
   - Sugestões de correção
   - Prevenção de problemas

Clique em qualquer botão acima para começar!
        """
        
        welcome_label = ttk.Label(self.content_frame, text=welcome_text, 
                                 font=("Consolas", 9), justify=tk.LEFT)
        welcome_label.pack(padx=20, pady=20)
    
    def show_chat(self):
        """Mostrar interface de chat"""
        # Limpar conteúdo anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Frame do chat
        chat_frame = ttk.Frame(self.content_frame)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Área de histórico do chat
        self.chat_display = scrolledtext.ScrolledText(chat_frame, height=15, 
                                                     font=("Consolas", 9))
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Frame de entrada
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X)
        
        # Campo de entrada
        self.chat_input = ttk.Entry(input_frame, font=("Consolas", 9))
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_input.bind("<Return>", self.send_chat_message)
        
        # Botão de enviar
        send_button = ttk.Button(input_frame, text="Enviar", 
                                command=self.send_chat_message)
        send_button.pack(side=tk.RIGHT)
        
        # Botão de limpar
        clear_button = ttk.Button(input_frame, text="Limpar", 
                                 command=self.clear_chat)
        clear_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Mensagem inicial
        self.add_chat_message("IA", "Olá! Sou seu assistente de IA. Como posso ajudar?")
    
    def send_chat_message(self, event=None):
        """Enviar mensagem do chat"""
        message = self.chat_input.get().strip()
        if not message:
            return
        
        # Adicionar mensagem do usuário
        self.add_chat_message("Você", message)
        self.chat_input.delete(0, tk.END)
        
        # Processar em thread separada
        threading.Thread(target=self._process_chat_message, args=(message,), daemon=True).start()
    
    def _process_chat_message(self, message: str):
        """Processar mensagem do chat em background"""
        try:
            response = self.ai_system.chat(message)
            self.parent_frame.after(0, lambda: self.add_chat_message("IA", response))
        except Exception as e:
            error_msg = f"Erro ao processar mensagem: {str(e)}"
            self.parent_frame.after(0, lambda: self.add_chat_message("Sistema", error_msg))
    
    def add_chat_message(self, sender: str, message: str):
        """Adicionar mensagem ao chat"""
        timestamp = time.strftime("%H:%M")
        formatted_message = f"[{timestamp}] {sender}: {message}\n\n"
        
        self.chat_display.insert(tk.END, formatted_message)
        self.chat_display.see(tk.END)
        
        # Adicionar ao histórico
        self.chat_history.append({
            "sender": sender,
            "message": message,
            "timestamp": timestamp
        })
    
    def clear_chat(self):
        """Limpar chat"""
        self.chat_display.delete(1.0, tk.END)
        self.chat_history = []
        self.add_chat_message("IA", "Chat limpo. Como posso ajudar?")
    
    def show_analyzer(self):
        """Mostrar analisador de apps"""
        # Limpar conteúdo anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Frame do analisador
        analyzer_frame = ttk.Frame(self.content_frame)
        analyzer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Título
        title_label = ttk.Label(analyzer_frame, text="🔍 ANALISADOR DE APPS", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Frame de seleção
        selection_frame = ttk.Frame(analyzer_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(selection_frame, text="Selecione um app para analisar:").pack(side=tk.LEFT)
        
        # Combobox de apps
        self.app_var = tk.StringVar()
        app_names = [app.get('name', 'App sem nome') for app in self.apps_data]
        self.app_combo = ttk.Combobox(selection_frame, textvariable=self.app_var, 
                                     values=app_names, state="readonly", width=30)
        self.app_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Botão de análise
        analyze_btn = ttk.Button(selection_frame, text="Analisar", 
                                command=self.analyze_selected_app)
        analyze_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Área de resultados
        self.analysis_display = scrolledtext.ScrolledText(analyzer_frame, height=20, 
                                                         font=("Consolas", 9))
        self.analysis_display.pack(fill=tk.BOTH, expand=True)
    
    def analyze_selected_app(self):
        """Analisar app selecionado"""
        app_name = self.app_var.get()
        if not app_name:
            messagebox.showwarning("Aviso", "Selecione um app para analisar")
            return
        
        # Encontrar app
        selected_app = None
        for app in self.apps_data:
            if app.get('name') == app_name:
                selected_app = app
                break
        
        if not selected_app:
            messagebox.showerror("Erro", "App não encontrado")
            return
        
        # Limpar área de resultados
        self.analysis_display.delete(1.0, tk.END)
        self.analysis_display.insert(tk.END, "🔍 Analisando app...\n\n")
        
        # Processar em thread separada
        threading.Thread(target=self._process_analysis, args=(selected_app,), daemon=True).start()
    
    def _process_analysis(self, app: Dict):
        """Processar análise em background"""
        try:
            analysis = self.ai_system.analyze_app(app)
            
            # Formatar resultado
            result = f"📊 ANÁLISE: {app.get('name', 'App')}\n"
            result += "=" * 50 + "\n\n"
            
            for key, value in analysis.items():
                if key != "error":
                    result += f"🔹 {key.replace('_', ' ').title()}: {value}\n\n"
            
            self.parent_frame.after(0, lambda: self.analysis_display.delete(1.0, tk.END))
            self.parent_frame.after(0, lambda: self.analysis_display.insert(tk.END, result))
            
        except Exception as e:
            error_msg = f"Erro na análise: {str(e)}"
            self.parent_frame.after(0, lambda: self.analysis_display.delete(1.0, tk.END))
            self.parent_frame.after(0, lambda: self.analysis_display.insert(tk.END, error_msg))
    
    def show_suggestions(self):
        """Mostrar interface de sugestões"""
        # Limpar conteúdo anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Frame de sugestões
        suggest_frame = ttk.Frame(self.content_frame)
        suggest_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Título
        title_label = ttk.Label(suggest_frame, text="💡 SUGESTÕES INTELIGENTES", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Frame de entrada
        input_frame = ttk.Frame(suggest_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Descreva seu problema:").pack(anchor=tk.W)
        
        # Campo de entrada do problema
        self.problem_input = scrolledtext.ScrolledText(input_frame, height=4, 
                                                      font=("Consolas", 9))
        self.problem_input.pack(fill=tk.X, pady=(5, 0))
        
        # Botão de sugestão
        suggest_btn = ttk.Button(input_frame, text="Obter Sugestões", 
                                command=self.get_suggestions)
        suggest_btn.pack(pady=(10, 0))
        
        # Área de resultados
        self.suggestions_display = scrolledtext.ScrolledText(suggest_frame, height=15, 
                                                            font=("Consolas", 9))
        self.suggestions_display.pack(fill=tk.BOTH, expand=True)
    
    def get_suggestions(self):
        """Obter sugestões para o problema"""
        problem = self.problem_input.get(1.0, tk.END).strip()
        if not problem:
            messagebox.showwarning("Aviso", "Descreva o problema primeiro")
            return
        
        # Limpar área de resultados
        self.suggestions_display.delete(1.0, tk.END)
        self.suggestions_display.insert(tk.END, "💡 Analisando problema...\n\n")
        
        # Processar em thread separada
        threading.Thread(target=self._process_suggestions, args=(problem,), daemon=True).start()
    
    def _process_suggestions(self, problem: str):
        """Processar sugestões em background"""
        try:
            suggestions = self.ai_system.suggest_app_for_problem(problem, self.apps_data)
            
            # Formatar resultado
            result = f"💡 SUGESTÕES PARA: {problem}\n"
            result += "=" * 50 + "\n\n"
            
            result += f"🎯 APP RECOMENDADO: {suggestions.get('app_recomendado', 'N/A')}\n"
            result += f"📝 RAZÃO: {suggestions.get('razao', 'N/A')}\n"
            result += f"🎯 CONFIANÇA: {suggestions.get('confianca', 0)}%\n\n"
            
            if suggestions.get('alternativas'):
                result += "🔄 ALTERNATIVAS:\n"
                for alt in suggestions['alternativas']:
                    result += f"  • {alt}\n"
            
            self.parent_frame.after(0, lambda: self.suggestions_display.delete(1.0, tk.END))
            self.parent_frame.after(0, lambda: self.suggestions_display.insert(tk.END, result))
            
        except Exception as e:
            error_msg = f"Erro ao gerar sugestões: {str(e)}"
            self.parent_frame.after(0, lambda: self.suggestions_display.delete(1.0, tk.END))
            self.parent_frame.after(0, lambda: self.suggestions_display.insert(tk.END, error_msg))
    
    def show_docs_generator(self):
        """Mostrar gerador de documentação"""
        # Limpar conteúdo anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Frame do gerador
        docs_frame = ttk.Frame(self.content_frame)
        docs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Título
        title_label = ttk.Label(docs_frame, text="📚 GERADOR DE DOCUMENTAÇÃO", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Frame de seleção
        selection_frame = ttk.Frame(docs_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(selection_frame, text="Selecione um app para documentar:").pack(side=tk.LEFT)
        
        # Combobox de apps
        self.docs_app_var = tk.StringVar()
        app_names = [app.get('name', 'App sem nome') for app in self.apps_data]
        self.docs_app_combo = ttk.Combobox(selection_frame, textvariable=self.docs_app_var, 
                                          values=app_names, state="readonly", width=30)
        self.docs_app_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Botão de geração
        generate_btn = ttk.Button(selection_frame, text="Gerar Docs", 
                                 command=self.generate_docs)
        generate_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Área de documentação
        self.docs_display = scrolledtext.ScrolledText(docs_frame, height=20, 
                                                     font=("Consolas", 9))
        self.docs_display.pack(fill=tk.BOTH, expand=True)
    
    def generate_docs(self):
        """Gerar documentação para app selecionado"""
        app_name = self.docs_app_var.get()
        if not app_name:
            messagebox.showwarning("Aviso", "Selecione um app para documentar")
            return
        
        # Encontrar app
        selected_app = None
        for app in self.apps_data:
            if app.get('name') == app_name:
                selected_app = app
                break
        
        if not selected_app:
            messagebox.showerror("Erro", "App não encontrado")
            return
        
        # Limpar área de documentação
        self.docs_display.delete(1.0, tk.END)
        self.docs_display.insert(tk.END, "📚 Gerando documentação...\n\n")
        
        # Processar em thread separada
        threading.Thread(target=self._process_docs_generation, args=(selected_app,), daemon=True).start()
    
    def _process_docs_generation(self, app: Dict):
        """Processar geração de documentação em background"""
        try:
            # Tentar ler código do arquivo
            code_content = ""
            app_file = app.get('file', '')
            if app_file and os.path.exists(app_file):
                try:
                    with open(app_file, 'r', encoding='utf-8') as f:
                        code_content = f.read()
                except:
                    pass
            
            docs = self.ai_system.generate_documentation(app, code_content)
            
            self.parent_frame.after(0, lambda: self.docs_display.delete(1.0, tk.END))
            self.parent_frame.after(0, lambda: self.docs_display.insert(tk.END, docs))
            
        except Exception as e:
            error_msg = f"Erro ao gerar documentação: {str(e)}"
            self.parent_frame.after(0, lambda: self.docs_display.delete(1.0, tk.END))
            self.parent_frame.after(0, lambda: self.docs_display.insert(tk.END, error_msg))

def integrate_ai_with_main_app(main_window: tk.Tk, logger: logging.Logger) -> Optional[AISystem]:
    """Integra o sistema de IA com a aplicação principal."""
    try:
        logger.info("🤖 Iniciando integração da IA...")
        
        # Cria sistema de IA
        ai_system = AISystem(logger)
        
        # Inicializa IA
        if not ai_system.initialize():
            logger.error("❌ Falha ao inicializar IA")
            messagebox.showwarning(
                "IA Indisponível",
                "O sistema de IA não pôde ser inicializado.\n\n"
                "Certifique-se de que o Ollama está instalado:\n"
                "https://ollama.ai/download"
            )
            return None
        
        logger.info("✅ IA integrada com sucesso!")
        return ai_system
        
    except Exception as e:
        logger.error(f"❌ Erro na integração da IA: {e}")
        messagebox.showerror("Erro", f"Erro ao integrar IA: {e}")
        return None 