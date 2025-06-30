#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de IA para Python App Launcher
=====================================

Sistema de inteligência artificial local usando Ollama para:
- Análise de aplicações
- Sugestões de apps para problemas
- Geração de documentação
- Debugging inteligente
- Conversação contextual
"""

import os
import sys
import json
import time
import threading
import subprocess
import requests
from typing import Dict, List, Optional, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AISystem:
    """Sistema principal de IA usando Ollama"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.models = {
            "llama2": "llama2",
            "codellama": "codellama",
            "mistral": "mistral"
        }
        self.current_model = "llama2"
        self.conversation_history = []
        self.is_initialized = False
        
        # Inicializar em thread separada
        self.init_thread = threading.Thread(target=self._initialize_ai, daemon=True)
        self.init_thread.start()
    
    def _initialize_ai(self):
        """Inicializar sistema de IA em background"""
        try:
            # Verificar se Ollama está rodando
            if self._check_ollama_server():
                # Verificar modelos disponíveis
                available_models = self._get_available_models()
                if available_models:
                    self.current_model = available_models[0]
                    self.is_initialized = True
                    logger.info(f"✅ IA inicializada com modelo: {self.current_model}")
                else:
                    logger.warning("⚠️ Nenhum modelo de IA disponível")
            else:
                logger.error("❌ Servidor Ollama não está rodando")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar IA: {e}")
    
    def _check_ollama_server(self) -> bool:
        """Verificar se o servidor Ollama está rodando"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _get_available_models(self) -> List[str]:
        """Obter lista de modelos disponíveis"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                return [model["name"] for model in models_data.get("models", [])]
        except Exception as e:
            logger.error(f"Erro ao obter modelos: {e}")
        return []
    
    def _call_ollama(self, prompt: str, model: str = None, system_prompt: str = None) -> str:
        """Fazer chamada para o Ollama"""
        if not model:
            model = self.current_model
            
        try:
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                data["system"] = system_prompt
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Erro na chamada Ollama: {response.status_code}")
                return "Desculpe, não consegui processar sua solicitação."
                
        except Exception as e:
            logger.error(f"Erro ao chamar Ollama: {e}")
            return "Erro de conexão com o servidor de IA."
    
    def analyze_app(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisar uma aplicação e fornecer insights"""
        if not self.is_initialized:
            return {"error": "IA não inicializada"}
        
        prompt = f"""
        Analise esta aplicação Python e forneça insights úteis:
        
        Nome: {app_data.get('name', 'N/A')}
        Categoria: {app_data.get('category', 'N/A')}
        Descrição: {app_data.get('description', 'N/A')}
        Arquivo: {app_data.get('file', 'N/A')}
        Tags: {app_data.get('tags', [])}
        Dependências: {app_data.get('dependencies', [])}
        
        Forneça uma análise em JSON com:
        1. Complexidade estimada (baixa/média/alta)
        2. Possíveis melhorias
        3. Sugestões de otimização
        4. Categorização automática
        5. Tags sugeridas
        6. Dependências recomendadas
        """
        
        system_prompt = "Você é um analisador especializado em aplicações Python. Responda sempre em JSON válido."
        
        response = self._call_ollama(prompt, system_prompt=system_prompt)
        
        try:
            # Tentar extrair JSON da resposta
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "complexidade": "média",
                    "melhorias": ["Análise não disponível"],
                    "otimizacoes": ["Análise não disponível"],
                    "categoria_sugerida": app_data.get('category', 'Geral'),
                    "tags_sugeridas": app_data.get('tags', []),
                    "dependencias_recomendadas": app_data.get('dependencies', [])
                }
        except:
            return {
                "complexidade": "média",
                "melhorias": ["Análise não disponível"],
                "otimizacoes": ["Análise não disponível"],
                "categoria_sugerida": app_data.get('category', 'Geral'),
                "tags_sugeridas": app_data.get('tags', []),
                "dependencias_recomendadas": app_data.get('dependencies', [])
            }
    
    def suggest_app_for_problem(self, problem_description: str, available_apps: List[Dict]) -> Dict[str, Any]:
        """Sugerir qual app usar para resolver um problema"""
        if not self.is_initialized:
            return {"error": "IA não inicializada"}
        
        apps_info = "\n".join([
            f"- {app['name']}: {app.get('description', 'Sem descrição')} (Categoria: {app.get('category', 'Geral')})"
            for app in available_apps
        ])
        
        prompt = f"""
        Problema: {problem_description}
        
        Aplicações disponíveis:
        {apps_info}
        
        Analise o problema e sugira qual aplicação seria mais adequada para resolvê-lo.
        Responda em JSON com:
        1. app_recomendado: nome da aplicação
        2. razao: explicação da escolha
        3. alternativas: outras opções válidas
        4. confianca: nível de confiança (0-100)
        """
        
        system_prompt = "Você é um assistente especializado em recomendar ferramentas Python. Responda sempre em JSON válido."
        
        response = self._call_ollama(prompt, system_prompt=system_prompt)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "app_recomendado": available_apps[0]['name'] if available_apps else "Nenhuma",
                    "razao": "Análise não disponível",
                    "alternativas": [],
                    "confianca": 50
                }
        except:
            return {
                "app_recomendado": available_apps[0]['name'] if available_apps else "Nenhuma",
                "razao": "Análise não disponível",
                "alternativas": [],
                "confianca": 50
            }
    
    def generate_documentation(self, app_data: Dict[str, Any], code_content: str = "") -> str:
        """Gerar documentação para uma aplicação"""
        if not self.is_initialized:
            return "IA não inicializada"
        
        prompt = f"""
        Gere documentação completa para esta aplicação Python:
        
        Nome: {app_data.get('name', 'N/A')}
        Categoria: {app_data.get('category', 'N/A')}
        Descrição: {app_data.get('description', 'N/A')}
        Dependências: {app_data.get('dependencies', [])}
        
        Código (se disponível):
        {code_content[:1000] if code_content else 'Código não disponível'}
        
        Gere documentação em Markdown incluindo:
        1. Visão geral
        2. Instalação
        3. Uso
        4. Exemplos
        5. Dependências
        6. Troubleshooting
        """
        
        system_prompt = "Você é um especialista em documentação técnica Python. Gere documentação clara e completa em Markdown."
        
        return self._call_ollama(prompt, system_prompt=system_prompt)
    
    def debug_help(self, error_message: str, code_context: str = "") -> str:
        """Fornecer ajuda para debugging"""
        if not self.is_initialized:
            return "IA não inicializada"
        
        prompt = f"""
        Erro Python: {error_message}
        
        Contexto do código:
        {code_context}
        
        Analise o erro e forneça:
        1. Explicação do problema
        2. Possíveis soluções
        3. Código corrigido (se aplicável)
        4. Prevenção de erros similares
        """
        
        system_prompt = "Você é um especialista em debugging Python. Forneça soluções práticas e código corrigido quando possível."
        
        return self._call_ollama(prompt, system_prompt=system_prompt)
    
    def chat(self, message: str) -> str:
        """Conversação geral com IA"""
        if not self.is_initialized:
            return "IA não inicializada. Aguarde a inicialização completa."
        
        # Adicionar à história da conversa
        self.conversation_history.append({"user": message, "timestamp": time.time()})
        
        # Manter apenas as últimas 10 mensagens
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        # Construir contexto da conversa
        context = "\n".join([
            f"Usuário: {msg['user']}" 
            for msg in self.conversation_history[-5:]  # Últimas 5 mensagens
        ])
        
        prompt = f"""
        Contexto da conversa:
        {context}
        
        Nova mensagem: {message}
        
        Responda de forma útil e contextual, considerando que você é um assistente especializado em Python e desenvolvimento de software.
        """
        
        system_prompt = "Você é um assistente Python especializado em desenvolvimento de software, análise de código e resolução de problemas técnicos."
        
        response = self._call_ollama(prompt, system_prompt=system_prompt)
        
        # Adicionar resposta à história
        self.conversation_history.append({"assistant": response, "timestamp": time.time()})
        
        return response
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status do sistema de IA"""
        return {
            "initialized": self.is_initialized,
            "current_model": self.current_model,
            "server_online": self._check_ollama_server(),
            "available_models": self._get_available_models(),
            "conversation_history_length": len(self.conversation_history)
        }
    
    def switch_model(self, model_name: str) -> bool:
        """Trocar modelo de IA"""
        available_models = self._get_available_models()
        if model_name in available_models:
            self.current_model = model_name
            logger.info(f"Modelo trocado para: {model_name}")
            return True
        else:
            logger.warning(f"Modelo {model_name} não disponível")
            return False
    
    def clear_conversation_history(self):
        """Limpar histórico de conversa"""
        self.conversation_history = []
        logger.info("Histórico de conversa limpo") 