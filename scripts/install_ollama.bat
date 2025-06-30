@echo off
setlocal enabledelayedexpansion

REM ========================================
REM 🤖 INSTALADOR OLLAMA - Python App Launcher
REM ========================================
REM Versão: 1.0.0
REM ========================================

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🤖 INSTALADOR OLLAMA                      ║
echo ║                                                              ║
echo ║  Instalando Ollama para o sistema de IA...                  ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Verificar se Ollama já está instalado
ollama --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ Ollama já está instalado!
    ollama --version
    echo.
    goto :install_model
)

echo 📥 Baixando Ollama...
echo.

REM Baixar Ollama para Windows
set "OLLAMA_URL=https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.exe"
set "OLLAMA_FILE=ollama-installer.exe"

echo 🔗 URL: %OLLAMA_URL%
echo 📁 Arquivo: %OLLAMA_FILE%
echo.

REM Tentar baixar com PowerShell
powershell -Command "& {Invoke-WebRequest -Uri '%OLLAMA_URL%' -OutFile '%OLLAMA_FILE%'}" >nul 2>&1

if not exist "%OLLAMA_FILE%" (
    echo ❌ Falha ao baixar Ollama automaticamente.
    echo.
    echo 💡 Por favor, baixe manualmente:
    echo 🌐 https://ollama.ai/download
    echo.
    echo 📋 Instruções:
    echo 1. Acesse https://ollama.ai/download
    echo 2. Baixe a versão para Windows
    echo 3. Execute o instalador
    echo 4. Reinicie este script
    echo.
    pause
    exit /b 1
)

echo ✅ Download concluído!
echo.

echo 🚀 Instalando Ollama...
echo.

REM Executar instalador
start /wait "" "%OLLAMA_FILE%"

REM Verificar se a instalação foi bem-sucedida
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Falha na instalação do Ollama.
    echo.
    echo 💡 Tente instalar manualmente:
    echo 🌐 https://ollama.ai/download
    echo.
    pause
    exit /b 1
)

echo ✅ Ollama instalado com sucesso!
ollama --version
echo.

:install_model
echo 📦 Instalando modelo Llama2...
echo.

REM Instalar modelo Llama2
ollama pull llama2

if errorlevel 1 (
    echo ❌ Falha ao instalar modelo Llama2.
    echo.
    echo 💡 Tente instalar manualmente:
    echo ollama pull llama2
    echo.
    pause
    exit /b 1
)

echo ✅ Modelo Llama2 instalado com sucesso!
echo.

echo 🚀 Iniciando servidor Ollama...
echo.

REM Iniciar servidor em background
start /b "" ollama serve

REM Aguardar servidor iniciar
echo ⏳ Aguardando servidor iniciar...
timeout /t 10 /nobreak >nul

REM Verificar se servidor está rodando
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Servidor Ollama não está respondendo.
    echo.
    echo 💡 Tente iniciar manualmente:
    echo ollama serve
    echo.
    pause
    exit /b 1
)

echo ✅ Servidor Ollama iniciado com sucesso!
echo.

echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🎉 INSTALAÇÃO CONCLUÍDA!                  ║
echo ║                                                              ║
echo ║  ✅ Ollama instalado                                         ║
echo ║  ✅ Modelo Llama2 instalado                                  ║
echo ║  ✅ Servidor iniciado                                        ║
echo ║                                                              ║
echo ║  🚀 Agora você pode usar o sistema de IA!                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📋 Próximos passos:
echo 1. Execute start.bat para iniciar a aplicação
echo 2. Use os botões de IA na interface
echo 3. Experimente o chat com IA
echo 4. Analise aplicações com IA
echo.

pause 