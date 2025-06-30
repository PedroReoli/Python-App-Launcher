#!/usr/bin/env python3
"""
Aplicativo de Exemplo para o Python App Launcher
Demonstra como o sistema detecta e executa aplicativos Python
"""

import sys
import time
from datetime import datetime

def main():
    """Função principal do aplicativo de exemplo"""
    print("=" * 50)
    print("Python App Launcher - Aplicativo de Exemplo")
    print("=" * 50)
    print(f"Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Python versão: {sys.version}")
    print(f"Executado a partir de: {sys.executable}")
    print("=" * 50)
    
    print("\nEste é um aplicativo de exemplo que demonstra:")
    print("✓ Detecção automática de linguagem Python")
    print("✓ Execução segura pelo App Launcher")
    print("✓ Funcionamento correto do sistema")
    
    print("\nAguardando 3 segundos para demonstração...")
    for i in range(3, 0, -1):
        print(f"Fechando em {i}...")
        time.sleep(1)
    
    print("\n✅ Aplicativo executado com sucesso!")
    print("O Python App Launcher está funcionando perfeitamente!")

if __name__ == "__main__":
    main() 