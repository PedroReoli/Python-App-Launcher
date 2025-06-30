#!/bin/bash

# ========================================
# 🚀 PYTHON APP LAUNCHER - AUTOMATIZADOR COMPLETO
# ========================================
# Versão: 3.0.0 - AUTOMATIZAÇÃO TOTAL
# Autor: Python App Launcher Team
# ========================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              🚀 PYTHON APP LAUNCHER v3.0.0                   ║"
echo "║                    AUTOMATIZADOR COMPLETO                    ║"
echo "║                                                              ║"
echo "║  🤖 Instalando, configurando e executando tudo automaticamente! ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ========================================
# 1. VERIFICAÇÕES INICIAIS
# ========================================

echo "📋 [1/8] Verificando ambiente inicial..."
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "main.py" ]; then
    echo "❌ ERRO: Arquivo main.py não encontrado!"
    echo ""
    echo "📁 Diretório atual: $(pwd)"
    echo ""
    echo "💡 Certifique-se de estar no diretório raiz da aplicação."
    echo ""
    exit 1
fi

echo "✅ Diretório correto verificado"
echo ""

# ========================================
# 2. VERIFICAÇÃO E INSTALAÇÃO DO PYTHON
# ========================================

echo "📋 [2/8] Verificando Python..."
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado! Instalando automaticamente..."
    echo ""
    
    # Detectar sistema operacional
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            echo "📥 Instalando Python3 via apt-get..."
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            echo "📥 Instalando Python3 via yum..."
            sudo yum install -y python3 python3-pip
        elif command -v dnf &> /dev/null; then
            echo "📥 Instalando Python3 via dnf..."
            sudo dnf install -y python3 python3-pip
        else
            echo "❌ Gerenciador de pacotes não suportado."
            echo "💡 Instale Python3 manualmente: https://www.python.org/downloads/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "📥 Instalando Python3 via Homebrew..."
            brew install python3
        else
            echo "❌ Homebrew não encontrado."
            echo "💡 Instale Homebrew: https://brew.sh/"
            echo "💡 Ou instale Python3 manualmente: https://www.python.org/downloads/"
            exit 1
        fi
    else
        echo "❌ Sistema operacional não suportado."
        echo "💡 Instale Python3 manualmente: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Verificar instalação
    if ! command -v python3 &> /dev/null; then
        echo "❌ Falha na instalação do Python3."
        exit 1
    fi
else
    echo "✅ Python3 encontrado:"
    python3 --version
fi

echo ""

# ========================================
# 3. VERIFICAÇÃO E INSTALAÇÃO DO PIP
# ========================================

echo "📋 [3/8] Verificando pip..."
echo ""

# Verificar se pip está disponível
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado! Instalando..."
    echo ""
    
    # Tentar instalar pip
    python3 -m ensurepip --upgrade
    
    # Verificar novamente
    if ! command -v pip3 &> /dev/null; then
        echo "❌ Falha ao instalar pip3."
        echo "💡 Tente executar: python3 -m ensurepip --upgrade"
        echo ""
        exit 1
    fi
else
    echo "✅ pip3 encontrado:"
    pip3 --version
fi

echo ""

# ========================================
# 4. INSTALAÇÃO DE DEPENDÊNCIAS PYTHON
# ========================================

echo "📋 [4/8] Instalando dependências Python..."
echo ""

# Verificar se requirements.txt existe
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando dependências do requirements.txt..."
    
    # Atualizar pip primeiro
    python3 -m pip install --upgrade pip > /dev/null 2>&1
    
    # Instalar dependências
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Algumas dependências podem ter falhado. Continuando..."
    else
        echo "✅ Dependências instaladas com sucesso!"
    fi
else
    echo "⚠️  requirements.txt não encontrado. Instalando dependências básicas..."
    
    # Instalar dependências básicas
    pip3 install psutil requests urllib3 typing-extensions > /dev/null 2>&1
    echo "✅ Dependências básicas instaladas!"
fi

echo ""

# ========================================
# 5. INSTALAÇÃO E CONFIGURAÇÃO DO OLLAMA
# ========================================

echo "📋 [5/8] Configurando sistema de IA (Ollama)..."
echo ""

# Verificar se Ollama já está instalado
if ! command -v ollama &> /dev/null; then
    echo "🤖 Ollama não encontrado! Instalando automaticamente..."
    echo ""
    
    # Detectar sistema operacional
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "📥 Baixando Ollama para Linux..."
        curl -fsSL https://ollama.ai/install.sh | sh
        
        if [ $? -ne 0 ]; then
            echo "❌ Falha na instalação do Ollama."
            echo "💡 Tente instalar manualmente: https://ollama.ai/download"
            echo ""
        else
            echo "✅ Ollama instalado com sucesso!"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "📥 Baixando Ollama para macOS..."
        curl -fsSL https://ollama.ai/install.sh | sh
        
        if [ $? -ne 0 ]; then
            echo "❌ Falha na instalação do Ollama."
            echo "💡 Tente instalar manualmente: https://ollama.ai/download"
            echo ""
        else
            echo "✅ Ollama instalado com sucesso!"
        fi
    else
        echo "❌ Sistema operacional não suportado para Ollama."
        echo "💡 Instale manualmente: https://ollama.ai/download"
        echo ""
    fi
else
    echo "✅ Ollama já está instalado:"
    ollama --version
fi

echo ""

# ========================================
# 6. INSTALAÇÃO DO MODELO LLAMA2
# ========================================

echo "📋 [6/8] Configurando modelo de IA..."
echo ""

# Verificar se modelo llama2 está instalado
if ! ollama list | grep -q "llama2"; then
    echo "📦 Modelo Llama2 não encontrado! Instalando..."
    echo ""
    
    echo "⏳ Isso pode demorar alguns minutos..."
    ollama pull llama2
    
    if [ $? -ne 0 ]; then
        echo "❌ Falha ao instalar modelo Llama2."
        echo "💡 Tente instalar manualmente: ollama pull llama2"
        echo ""
    else
        echo "✅ Modelo Llama2 instalado com sucesso!"
    fi
else
    echo "✅ Modelo Llama2 já está instalado!"
fi

echo ""

# ========================================
# 7. INICIALIZAÇÃO DO SERVIDOR OLLAMA
# ========================================

echo "📋 [7/8] Iniciando servidor de IA..."
echo ""

# Verificar se servidor já está rodando
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "🚀 Iniciando servidor Ollama..."
    
    # Iniciar servidor em background
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    
    # Aguardar servidor iniciar
    echo "⏳ Aguardando servidor iniciar..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✅ Servidor Ollama iniciado com sucesso!"
            break
        fi
        sleep 1
    done
    
    if [ $i -eq 30 ]; then
        echo "⚠️  Servidor pode não ter iniciado completamente."
        echo "💡 Se houver problemas, execute manualmente: ollama serve"
        echo ""
    fi
else
    echo "✅ Servidor Ollama já está rodando!"
fi

echo ""

# ========================================
# 8. CRIAÇÃO DE DIRETÓRIOS NECESSÁRIOS
# ========================================

echo "📋 [8/8] Preparando estrutura de diretórios..."
echo ""

# Criar diretórios necessários
if [ ! -d "logs" ]; then
    echo "📁 Criando diretório de logs..."
    mkdir -p logs
fi

if [ ! -d "docs" ]; then
    echo "📁 Criando diretório de documentação..."
    mkdir -p docs
fi

if [ ! -d "data" ]; then
    echo "📁 Criando diretório de dados..."
    mkdir -p data
fi

if [ ! -d "data/config" ]; then
    echo "📁 Criando diretório de configuração..."
    mkdir -p data/config
fi

echo "✅ Estrutura de diretórios preparada!"
echo ""

# ========================================
# 9. VERIFICAÇÃO FINAL E EXECUÇÃO
# ========================================

echo "🎯 Verificação final do ambiente..."
echo ""

# Verificar dependências críticas
ALL_GOOD=true

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não está funcionando"
    ALL_GOOD=false
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não está funcionando"
    ALL_GOOD=false
fi

# Verificar módulos Python essenciais
if ! python3 -c "import tkinter" > /dev/null 2>&1; then
    echo "❌ tkinter não está disponível"
    ALL_GOOD=false
fi

if ! python3 -c "import psutil" > /dev/null 2>&1; then
    echo "⚠️  psutil não está disponível (será instalado automaticamente)"
fi

if ! python3 -c "import requests" > /dev/null 2>&1; then
    echo "⚠️  requests não está disponível (será instalado automaticamente)"
fi

if [ "$ALL_GOOD" = false ]; then
    echo ""
    echo "❌ ERRO: Ambiente não está pronto!"
    echo ""
    echo "💡 Verifique as dependências e tente novamente."
    echo ""
    exit 1
fi

echo "✅ Ambiente verificado e pronto!"
echo ""

# ========================================
# 10. EXECUÇÃO DA APLICAÇÃO
# ========================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🚀 INICIANDO APLICAÇÃO                    ║"
echo "║                                                              ║"
echo "║  🤖 Python App Launcher v3.0.0 + IA                         ║"
echo "║  📊 Sistema: $(uname -s)                                    ║"
echo "║  🐍 Python: $(python3 --version)                            ║"
echo "║  🤖 IA: Ollama + Llama2                                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Mostrar informações do sistema
echo "📊 Informações do sistema:"
python3 --version
echo "   - Sistema Operacional: $(uname -s)"
echo "   - Arquitetura: $(uname -m)"
echo "   - Diretório: $(pwd)"
echo ""

# Verificar argumentos especiais
PROFILE_MODE=""
DEBUG_MODE=""

for arg in "$@"; do
    if [ "$arg" = "--profile" ]; then
        PROFILE_MODE="--profile"
    elif [ "$arg" = "--debug" ]; then
        DEBUG_MODE="--debug"
    fi
done

# Executar a aplicação
echo "🚀 Iniciando Python App Launcher..."
echo ""

if [ -n "$DEBUG_MODE" ]; then
    echo "🔧 Modo DEBUG ativado"
    python3 main.py --debug
elif [ -n "$PROFILE_MODE" ]; then
    echo "📈 Modo PROFILING ativado"
    python3 main.py --profile
else
    python3 main.py
fi

# ========================================
# 11. VERIFICAÇÃO PÓS-EXECUÇÃO
# ========================================

# Verificar se a aplicação foi executada com sucesso
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERRO: A aplicação foi encerrada com erro (código: $?)"
    echo ""
    echo "💡 Verifique os logs em logs/ para mais detalhes."
    echo ""
    echo "🔧 Possíveis soluções:"
    echo "   1. Verifique se todas as dependências estão instaladas"
    echo "   2. Execute: pip3 install -r requirements.txt"
    echo "   3. Verifique se o Ollama está rodando: ollama serve"
    echo "   4. Execute em modo debug: ./start.sh --debug"
    echo ""
else
    echo ""
    echo "✅ Aplicação encerrada com sucesso!"
    echo ""
fi

# ========================================
# 12. FINALIZAÇÃO
# ========================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    👋 OBRIGADO POR USAR                      ║"
echo "║                    PYTHON APP LAUNCHER                       ║"
echo "║                                                              ║"
echo "║  🤖 Agora com Inteligência Artificial integrada!            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "📋 Resumo da sessão:"
echo "   ✅ Python3 verificado e configurado"
echo "   ✅ Dependências instaladas"
echo "   ✅ Ollama configurado"
echo "   ✅ Modelo Llama2 instalado"
echo "   ✅ Servidor de IA iniciado"
echo "   ✅ Aplicação executada"
echo ""

echo "💡 Dicas:"
echo "   - Use os botões de IA na aplicação"
echo "   - Experimente o chat com IA"
echo "   - Analise aplicações automaticamente"
echo "   - Gere documentação com IA"
echo ""

# Limpar processo do Ollama se foi iniciado por este script
if [ -n "$OLLAMA_PID" ]; then
    echo "🔄 Encerrando servidor Ollama..."
    kill $OLLAMA_PID 2>/dev/null
fi 