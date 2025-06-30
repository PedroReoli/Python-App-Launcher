@echo off
REM ============================================
REM         PYTHON APP LAUNCHER
REM        COM INTELIGENCIA ARTIFICIAL
REM ============================================

echo ============================================
echo         PYTHON APP LAUNCHER
echo        COM INTELIGENCIA ARTIFICIAL
echo ============================================
echo.

cd /d "%~dp0"

REM 1. Verificar Python
echo [1/8] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado. Baixando e instalando...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python_installer.exe'}"
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python_installer.exe
    echo Python instalado com sucesso!
    call refreshenv
) else (
    echo Python ja esta instalado
)

REM 2. Verificar pip
echo.
echo [2/8] Verificando pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip nao encontrado. Instalando...
    python -m ensurepip --upgrade
    echo pip instalado com sucesso!
) else (
    echo pip ja esta instalado
)

REM 3. Instalar dependencias Python
echo.
echo [3/8] Instalando dependencias Python...
if exist requirements.txt (
    echo Instalando pacotes do requirements.txt...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    echo Dependencias instaladas!
) else (
    echo Criando requirements.txt padrao...
    echo tkinter > requirements.txt
    echo pillow >> requirements.txt
    echo matplotlib >> requirements.txt
    echo numpy >> requirements.txt
    echo requests >> requirements.txt
    echo psutil >> requirements.txt
    echo colorama >> requirements.txt
    echo tqdm >> requirements.txt
    echo python-dotenv >> requirements.txt
    echo openai >> requirements.txt
    echo ollama >> requirements.txt
    echo langchain >> requirements.txt
    echo langchain-community >> requirements.txt
    python -m pip install -r requirements.txt
    echo Dependencias instaladas!
)

REM 4. Instalar Ollama (IA Local)
echo.
echo [4/8] Verificando Ollama (IA Local)...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama nao encontrado. Baixando e instalando...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.exe' -OutFile 'ollama.exe'}"
    move ollama.exe "%USERPROFILE%\AppData\Local\Microsoft\WinGet\Packages\ollama.exe"
    echo Ollama instalado!
) else (
    echo Ollama ja esta instalado
)

REM 5. Baixar modelos de IA
echo.
echo [5/8] Baixando modelos de IA...
echo Baixando Llama2 (modelo principal)...
ollama pull llama2 >nul 2>&1
if %errorlevel% equ 0 (
    echo Llama2 baixado com sucesso!
) else (
    echo Erro ao baixar Llama2, tentando modelo alternativo...
    ollama pull llama2:7b >nul 2>&1
    echo Modelo alternativo baixado!
)
echo Baixando CodeLlama (para programacao)...
ollama pull codellama >nul 2>&1
if %errorlevel% equ 0 (
    echo CodeLlama baixado com sucesso!
) else (
    echo CodeLlama nao disponivel, usando Llama2 para codigo
)

REM 6. Iniciar servidor Ollama
echo.
echo [6/8] Iniciando servidor Ollama...
start /B ollama serve
timeout /t 3 /nobreak >nul
echo Verificando se o servidor esta ativo...
ollama list >nul 2>&1
if %errorlevel% equ 0 (
    echo Servidor Ollama ativo!
) else (
    echo Aguardando servidor Ollama...
    timeout /t 5 /nobreak >nul
)

REM 7. Criar diretorios necessarios
echo.
echo [7/8] Criando estrutura de diretorios...
if not exist logs mkdir logs
if not exist docs mkdir docs
if not exist data mkdir data
if not exist backups mkdir backups
if not exist temp mkdir temp
if not exist cache mkdir cache
if not exist bot mkdir bot
echo Estrutura de diretorios criada!

REM 8. Executar o app
echo.
echo [8/8] Iniciando Python App Launcher...
python main.py

echo.
echo Encerrando servidor Ollama...
taskkill /f /im ollama.exe >nul 2>&1
echo Aplicacao encerrada com sucesso!
pause 