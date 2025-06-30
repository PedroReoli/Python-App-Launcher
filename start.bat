@echo off
chcp 65001 >nul
title Python App Launcher - Inicialização

echo.
echo ========================================
echo    Python App Launcher - Setup
echo ========================================
echo.

:: Verificar se Python está instalado
echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo Por favor, instale Python 3.7+ de: https://python.org
    echo.
    pause
    exit /b 1
)
echo ✅ Python encontrado!

:: Verificar se pip está disponível
echo.
echo [2/5] Verificando pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip não encontrado!
    echo Instalando pip...
    python -m ensurepip --upgrade
)

:: Instalar dependências
echo.
echo [3/5] Instalando dependências...
echo Instalando PyQt5...
python -m pip install PyQt5==5.15.9 PyQt5-Qt5==5.15.2 PyQt5-sip==12.12.2 --quiet
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar PyQt5!
    echo Tentando instalação alternativa...
    python -m pip install PyQt5 --quiet
)

:: Criar diretórios necessários
echo.
echo [4/5] Criando estrutura de diretórios...
if not exist "apps" mkdir apps
if not exist "data" mkdir data
if not exist "config" mkdir config
if not exist "assets" mkdir assets
echo ✅ Diretórios criados!

:: Verificar se há aplicativos de exemplo
echo.
echo [5/5] Verificando aplicativos de exemplo...
if not exist "apps\exemplo.py" (
    echo ⚠️  Nenhum aplicativo encontrado na pasta apps/
    echo    Adicione seus aplicativos na pasta apps/ para testar o sistema
)

echo.
echo ========================================
echo    Iniciando Python App Launcher...
echo ========================================
echo.

:: Executar a aplicação
python main.py

:: Se houver erro, mostrar mensagem
if %errorlevel% neq 0 (
    echo.
    echo ❌ Erro ao executar a aplicação!
    echo Verifique se todas as dependências foram instaladas corretamente.
    echo.
    pause
) 