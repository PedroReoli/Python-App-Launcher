"""
🤖 BOT MODULE - Python App Launcher
===================================

Módulo de Inteligência Artificial para o Python App Launcher.
Integra Ollama local para análise, documentação e assistência inteligente.

Módulos:
- ai_system.py: Sistema principal de IA
- ai_integration.py: Integração com aplicação principal

Autor: Python App Launcher Team
Versão: 1.0.0
"""

from .ai_system import AISystem, OllamaManager, AppAnalyzer, DocumentationGenerator
from .ai_integration import AIButtonManager, AIStatusBar, integrate_ai_with_main_app

__version__ = "1.0.0"
__author__ = "Python App Launcher Team"

__all__ = [
    "AISystem",
    "OllamaManager", 
    "AppAnalyzer",
    "DocumentationGenerator",
    "AIButtonManager",
    "AIStatusBar",
    "integrate_ai_with_main_app"
] 