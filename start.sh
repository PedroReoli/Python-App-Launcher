#!/bin/bash

# Python App Launcher - Script de Inicialização para Linux/Mac

echo ""
echo "========================================"
echo "    Python App Launcher - Setup"
echo "========================================"
echo ""

# Verificar se Python está instalado
echo "[1/5] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    echo "Por favor, instale Python 3.7+ usando seu gerenciador de pacotes"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi
echo "✅ Python encontrado!"

# Verificar se pip está disponível
echo ""
echo "[2/5] Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado!"
    echo "Instalando pip..."
    python3 -m ensurepip --upgrade
fi

# Instalar dependências
echo ""
echo "[3/5] Instalando dependências..."
echo "Instalando PyQt5..."
pip3 install PyQt5==5.15.9 PyQt5-Qt5==5.15.2 PyQt5-sip==12.12.2 --quiet
if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar PyQt5!"
    echo "Tentando instalação alternativa..."
    pip3 install PyQt5 --quiet
fi

# Criar diretórios necessários
echo ""
echo "[4/5] Criando estrutura de diretórios..."
mkdir -p apps data config assets
echo "✅ Diretórios criados!"

# Verificar se há aplicativos de exemplo
echo ""
echo "[5/5] Verificando aplicativos de exemplo..."
if [ ! -f "apps/exemplo.py" ]; then
    echo "⚠️  Nenhum aplicativo encontrado na pasta apps/"
    echo "   Adicione seus aplicativos na pasta apps/ para testar o sistema"
fi

# Tornar scripts shell executáveis
if [ -f "apps/Shell/exemplo.sh" ]; then
    chmod +x apps/Shell/exemplo.sh
fi

echo ""
echo "========================================"
echo "    Iniciando Python App Launcher..."
echo "========================================"
echo ""

# Executar a aplicação
python3 main.py

# Se houver erro, mostrar mensagem
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Erro ao executar a aplicação!"
    echo "Verifique se todas as dependências foram instaladas corretamente."
    echo ""
    read -p "Pressione Enter para continuar..."
fi 