#!/bin/bash
# Aplicativo Shell de Exemplo para o Python App Launcher
# Demonstra como o sistema detecta e executa scripts shell

echo "=================================================="
echo "Python App Launcher - Aplicativo Shell de Exemplo"
echo "=================================================="
echo "Data e hora: $(date '+%d/%m/%Y %H:%M:%S')"
echo "Sistema operacional: $(uname -s) $(uname -r)"
echo "Arquitetura: $(uname -m)"
echo "Shell atual: $SHELL"
echo "Diretório atual: $(pwd)"
echo "=================================================="

echo ""
echo "Este é um script shell que demonstra:"
echo "✓ Detecção automática de linguagem Shell"
echo "✓ Execução segura pelo App Launcher"
echo "✓ Funcionamento correto do sistema bash"

echo ""
echo "Informações do sistema:"
echo "- Hostname: $(hostname)"
echo "- Usuário: $(whoami)"
echo "- Processos ativos: $(ps aux | wc -l)"
echo "- Memória total: $(free -h | grep Mem | awk '{print $2}')"
echo "- Espaço em disco: $(df -h / | tail -1 | awk '{print $4}') disponível"

echo ""
echo "Testando comandos básicos:"
echo "- ls: $(ls | wc -l) arquivos no diretório atual"
echo "- who: $(who | wc -l) usuários logados"
echo "- uptime: $(uptime -p)"

echo ""
echo "✅ Script shell executado com sucesso!"
echo "O Python App Launcher está funcionando perfeitamente com bash!" 