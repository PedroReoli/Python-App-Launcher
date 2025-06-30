#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python App Launcher - Arquivo Principal (UI Moderna)
===================================================

Este é o arquivo principal que inicia apenas a interface moderna (gui.py)
sem backend, sem lógica, apenas UI para customização visual.
"""

import sys
import os

# Adicionar a pasta python/ ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

def main():
    try:
        from gui import ModernAppUI
        import tkinter as tk
        root = tk.Tk()
        app = ModernAppUI(root)
        root.mainloop()
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("💡 Certifique-se de que ttkbootstrap está instalado: pip install ttkbootstrap")
        input("Pressione Enter para sair...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao executar a interface: {e}")
        input("Pressione Enter para sair...")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 PYTHON APP LAUNCHER - UI MODERNA (SOMENTE INTERFACE)")
    print("=" * 60)
    print()
    main()