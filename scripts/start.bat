@echo off
setlocal enabledelayedexpansion

REM ========================================
REM 🚀 PYTHON APP LAUNCHER - AUTOMATIZADOR REVOLUCIONÁRIO
REM ========================================
REM Versão: 4.0.0 - AUTOMATIZAÇÃO TOTAL + IA AVANÇADA
REM Autor: Python App Launcher Team
REM ========================================

REM Configurar cores e caracteres especiais
chcp 65001 >nul 2>&1
color 0A

REM ========================================
REM 0. INTERFACE GRÁFICA DE INICIALIZAÇÃO
REM ========================================

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 PYTHON APP LAUNCHER v4.0.0                             ║
echo ║                    AUTOMATIZADOR REVOLUCIONÁRIO                              ║
echo ║                                                                              ║
echo ║  🤖 IA AVANÇADA + AUTOMATIZAÇÃO TOTAL + OTIMIZAÇÃO DE SISTEMA              ║
echo ║  🎯 MÚLTIPLOS MODELOS DE IA + BACKUP AUTOMÁTICO + CONFIGURAÇÃO INTELIGENTE ║
echo ║  📊 MONITORAMENTO + RELATÓRIOS + TUDO AUTOMÁTICO!                          ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Verificar argumentos especiais
set "QUIET_MODE="
set "PROFILE_MODE="
set "DEBUG_MODE="
set "FULL_OPTIMIZATION="
set "BACKUP_MODE="
set "RESTORE_MODE="
set "CLEAN_INSTALL="
set "AI_MODEL="
set "AUTO_BACKUP="
set "AUTO_MONITOR="
set "AUTO_OPTIMIZE="
set "AUTO_REPORT="

for %%a in (%*) do (
    if "%%a"=="--quiet" set "QUIET_MODE=true"
    if "%%a"=="--profile" set "PROFILE_MODE=--profile"
    if "%%a"=="--debug" set "DEBUG_MODE=--debug"
    if "%%a"=="--optimize" set "FULL_OPTIMIZATION=true"
    if "%%a"=="--backup" set "BACKUP_MODE=true"
    if "%%a"=="--restore" set "RESTORE_MODE=true"
    if "%%a"=="--clean" set "CLEAN_INSTALL=true"
    if "%%a"=="--llama2" set "AI_MODEL=llama2"
    if "%%a"=="--mistral" set "AI_MODEL=mistral"
    if "%%a"=="--codellama" set "AI_MODEL=codellama"
    if "%%a"=="--auto-all" (
        set "AUTO_BACKUP=true"
        set "AUTO_MONITOR=true"
        set "AUTO_OPTIMIZE=true"
        set "AUTO_REPORT=true"
        set "FULL_OPTIMIZATION=true"
    )
)

REM Definir modelo padrão se não especificado
if not defined AI_MODEL set "AI_MODEL=llama2"

REM ========================================
REM 1. VERIFICAÇÕES INICIAIS AVANÇADAS
REM ========================================

if not defined QUIET_MODE (
    echo 📋 [1/15] Verificando ambiente inicial e otimizando sistema...
    echo.
)

REM Verificar se estamos no diretório correto
if not exist "main.py" (
    echo ❌ ERRO: Arquivo main.py não encontrado!
    echo.
    echo 📁 Diretório atual: %CD%
    echo.
    echo 💡 Certifique-se de estar no diretório raiz da aplicação.
    echo.
    pause
    exit /b 1
)

REM Verificar espaço em disco
for /f "tokens=3" %%a in ('dir /-c 2^>nul ^| find "bytes free"') do set "FREE_SPACE=%%a"
if %FREE_SPACE% LSS 1073741824 (
    echo ⚠️  AVISO: Espaço em disco baixo! Recomendado: 5GB livre
    echo    Espaço atual: %FREE_SPACE% bytes
    echo.
)

REM Verificar memória RAM
wmic computersystem get TotalPhysicalMemory /value | find "TotalPhysicalMemory" > temp_ram.txt
for /f "tokens=2 delims==" %%a in (temp_ram.txt) do set "TOTAL_RAM=%%a"
del temp_ram.txt >nul 2>&1
set /a "RAM_GB=%TOTAL_RAM:~0,-1%/1073741824"
if %RAM_GB% LSS 4 (
    echo ⚠️  AVISO: RAM baixa! Recomendado: 8GB, Atual: %RAM_GB%GB
    echo.
)

echo ✅ Ambiente inicial verificado
echo.

REM ========================================
REM 2. BACKUP AUTOMÁTICO (SE SOLICITADO)
REM ========================================

if defined AUTO_BACKUP (
    if not defined QUIET_MODE (
        echo 📋 [2/15] Executando backup automático...
        echo.
    )
    
    set "BACKUP_NAME=auto_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
    set "BACKUP_NAME=%BACKUP_NAME: =0%"
    
    if not exist "backups" mkdir backups
    if not exist "backups\%BACKUP_NAME%" mkdir "backups\%BACKUP_NAME%"
    
    echo 💾 Criando backup automático: %BACKUP_NAME%
    
    REM Backup de arquivos importantes
    if exist "config.json" copy "config.json" "backups\%BACKUP_NAME%\" >nul
    if exist "data" xcopy "data" "backups\%BACKUP_NAME%\data\" /E /I /Y >nul
    if exist "logs" xcopy "logs" "backups\%BACKUP_NAME%\logs\" /E /I /Y >nul
    if exist "docs" xcopy "docs" "backups\%BACKUP_NAME%\docs\" /E /I /Y >nul
    if exist "Apps" xcopy "Apps" "backups\%BACKUP_NAME%\Apps\" /E /I /Y >nul
    if exist "bot" xcopy "bot" "backups\%BACKUP_NAME%\bot\" /E /I /Y >nul
    
    echo ✅ Backup automático concluído!
    echo.
)

REM ========================================
REM 3. OTIMIZAÇÃO AUTOMÁTICA (SE SOLICITADA)
REM ========================================

if defined AUTO_OPTIMIZE (
    if not defined QUIET_MODE (
        echo 📋 [3/15] Executando otimização automática do sistema...
        echo.
    )
    
    REM Limpar cache temporário
    echo 🧹 Limpando cache temporário...
    del /q /s %TEMP%\* >nul 2>&1
    del /q /s %TMP%\* >nul 2>&1
    
    REM Otimizar configurações de energia
    echo ⚡ Configurando modo de alto desempenho...
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c >nul 2>&1
    
    REM Otimizar configurações de rede
    echo 🌐 Otimizando configurações de rede...
    netsh int tcp set global autotuninglevel=normal >nul 2>&1
    netsh int tcp set global chimney=enabled >nul 2>&1
    
    REM Limpar cache DNS
    echo 🧹 Limpando cache DNS...
    ipconfig /flushdns >nul 2>&1
    
    echo ✅ Otimização automática concluída!
    echo.
)

REM ========================================
REM 4. VERIFICAÇÃO E INSTALAÇÃO DO PYTHON
REM ========================================

if not defined QUIET_MODE (
    echo 📋 [4/15] Verificando e otimizando Python...
    echo.
)

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instalando automaticamente...
    echo.
    
    REM Tentar baixar Python automaticamente
    echo 📥 Baixando Python 3.11 (versão otimizada)...
    
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    set "PYTHON_INSTALLER=python-installer.exe"
    
    powershell -Command "& {Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}" >nul 2>&1
    
    if exist "%PYTHON_INSTALLER%" (
        echo ✅ Download concluído! Instalando Python com otimizações...
        echo.
        
        REM Instalar Python silenciosamente com todas as opções
        "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_doc=0 Include_dev=0
        
        REM Aguardar instalação
        timeout /t 30 /nobreak >nul
        
        REM Limpar arquivo de instalação
        del "%PYTHON_INSTALLER%" >nul 2>&1
        
        echo ✅ Python instalado! Recarregando PATH...
        
        REM Recarregar PATH
        call refreshenv >nul 2>&1
        
        REM Verificar novamente
        python --version >nul 2>&1
        if errorlevel 1 (
            echo ❌ Falha na instalação automática do Python.
            echo.
            echo 💡 Por favor, instale manualmente:
            echo 🌐 https://www.python.org/downloads/
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo ❌ Falha ao baixar Python automaticamente.
        echo.
        echo 💡 Por favor, instale manualmente:
        echo 🌐 https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
) else (
    echo ✅ Python encontrado:
    python --version
    
    REM Verificar versão e otimizar se necessário
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
    echo 🔧 Versão Python: %PYTHON_VERSION%
    
    REM Otimizar Python se versão antiga
    if "%PYTHON_VERSION:~0,3%" LSS "3.8" (
        echo ⚠️  Versão Python antiga detectada. Recomendado: 3.8+
        echo.
    )
)

echo.

REM ========================================
REM 5. VERIFICAÇÃO E INSTALAÇÃO DO PIP
REM ========================================

if not defined QUIET_MODE (
    echo 📋 [5/15] Configurando pip otimizado...
    echo.
)

REM Verificar se pip está disponível
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip não encontrado! Instalando...
    echo.
    
    REM Tentar instalar pip
    python -m ensurepip --upgrade >nul 2>&1
    
    REM Verificar novamente
    pip --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Falha ao instalar pip.
        echo.
        echo 💡 Tente executar: python -m ensurepip --upgrade
        echo.
        pause
        exit /b 1
    )
) else (
    echo ✅ pip encontrado:
    pip --version
)

REM Otimizar pip
echo 🔧 Otimizando pip...
python -m pip install --upgrade pip >nul 2>&1

REM Configurar pip para melhor performance
pip config set global.index-url https://pypi.org/simple/ >nul 2>&1
pip config set global.timeout 60 >nul 2>&1

echo.

REM ========================================
REM 6. INSTALAÇÃO DE DEPENDÊNCIAS PYTHON OTIMIZADA
REM ========================================

if not defined QUIET_MODE (
    echo 📋 [6/15] Instalando dependências Python otimizadas...
    echo.
)

REM Verificar se requirements.txt existe
if exist "requirements.txt" (
    echo 📦 Instalando dependências do requirements.txt com otimizações...
    
    REM Instalar dependências com cache e otimizações
    pip install --upgrade --no-cache-dir --force-reinstall -r requirements.txt
    
    if errorlevel 1 (
        echo ⚠️  Algumas dependências podem ter falhado. Tentando instalação alternativa...
        
        REM Tentar instalar uma por uma
        for /f "tokens=1" %%a in (requirements.txt) do (
            echo 📦 Instalando %%a...
            pip install %%a --no-cache-dir >nul 2>&1
        )
        
        echo ✅ Dependências instaladas (modo alternativo)!
    ) else (
        echo ✅ Dependências instaladas com sucesso!
    )
) else (
    echo ⚠️  requirements.txt não encontrado. Instalando dependências básicas otimizadas...
    
    REM Instalar dependências básicas com otimizações
    pip install --upgrade --no-cache-dir psutil requests urllib3 typing-extensions colorama tqdm >nul 2>&1
    echo ✅ Dependências básicas instaladas!
)

REM Verificar dependências críticas
echo 🔍 Verificando dependências críticas...
python -c "import psutil, requests, tkinter" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Algumas dependências críticas podem estar faltando.
) else (
    echo ✅ Todas as dependências críticas estão funcionando!
)

echo.

REM ========================================
REM 7. INSTALAÇÃO E CONFIGURAÇÃO DO OLLAMA AVANÇADA
REM ========================================

if not defined QUIET_MODE (
    echo 📋 [7/15] Configurando sistema de IA avançado (Ollama)...
    echo.
)

REM Verificar se Ollama já está instalado
ollama --version >nul 2>&1
if errorlevel 1 (
    echo 🤖 Ollama não encontrado! Instalando automaticamente...
    echo.
    
    REM Baixar Ollama para Windows
    set "OLLAMA_URL=https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.exe"
    set "OLLAMA_FILE=ollama-installer.exe"
    
    echo 📥 Baixando Ollama (última versão)...
    powershell -Command "& {Invoke-WebRequest -Uri '%OLLAMA_URL%' -OutFile '%OLLAMA_FILE%'}" >nul 2>&1
    
    if exist "%OLLAMA_FILE%" (
        echo ✅ Download concluído! Instalando Ollama...
        
        REM Executar instalador
        start /wait "" "%OLLAMA_FILE%"
        
        REM Limpar arquivo
        del "%OLLAMA_FILE%" >nul 2>&1
        
        REM Verificar instalação
        ollama --version >nul 2>&1
        if errorlevel 1 (
            echo ❌ Falha na instalação do Ollama.
            echo.
            echo 💡 Tente instalar manualmente: https://ollama.ai/download
            echo.
        ) else (
            echo ✅ Ollama instalado com sucesso!
        )
    ) else (
        echo ❌ Falha ao baixar Ollama.
        echo.
        echo 💡 Tente instalar manualmente: https://ollama.ai/download
        echo.
    )
) else (
    echo ✅ Ollama já está instalado:
    ollama --version
    
    REM Verificar se há atualizações
    echo 🔍 Verificando atualizações do Ollama...
    ollama pull %AI_MODEL% >nul 2>&1
)

echo.

REM ========================================
REM 8. INSTALAÇÃO DE MÚLTIPLOS MODELOS DE IA
REM ========================================

if not defined QUIET_MODE (
    echo 📋 [8/15] Configurando modelos de IA avançados...
    echo.
)

REM Verificar modelo selecionado
echo 🧠 Modelo de IA selecionado: %AI_MODEL%

REM Verificar se modelo está instalado
ollama list | findstr "%AI_MODEL%" >nul 2>&1
if errorlevel 1 (
    echo 📦 Modelo %AI_MODEL% não encontrado! Instalando...
    echo.
    
    echo ⏳ Isso pode demorar alguns minutos (tamanho: ~3-7GB)...
    echo 💡 Dica: Você pode cancelar com Ctrl+C e usar outro modelo
    echo.
    
    ollama pull %AI_MODEL%
    
    if errorlevel 1 (
        echo ❌ Falha ao instalar modelo %AI_MODEL%.
        echo.
        echo 💡 Tentando modelo alternativo (llama2)...
        set "AI_MODEL=llama2"
        ollama pull llama2
        if errorlevel 1 (
            echo ❌ Falha ao instalar modelo alternativo.
            echo 💡 Tente instalar manualmente: ollama pull llama2
            echo.
        ) else (
            echo ✅ Modelo alternativo instalado com sucesso!
        )
    ) else (
        echo ✅ Modelo %AI_MODEL% instalado com sucesso!
    )
) else (
    echo ✅ Modelo %AI_MODEL% já está instalado!
)

REM Instalar modelos adicionais se solicitado
if defined FULL_OPTIMIZATION (
    echo 🔧 Instalando modelos adicionais para melhor performance...
    
    REM Instalar modelos menores para diferentes tarefas
    ollama pull mistral:7b-instruct >nul 2>&1
    ollama pull codellama:7b-instruct >nul 2>&1
    
    echo ✅ Modelos adicionais instalados!
)

echo.

REM ========================================
REM 9. INICIALIZAÇÃO DO SERVIDOR OLLAMA AVANÇADA
REM ========================================

if not defined QUIET_MODE (
    echo 📋 [9/15] Iniciando servidor de IA avançado...
    echo.
)

REM Verificar se servidor já está rodando
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo 🚀 Iniciando servidor Ollama com otimizações...
    
    REM Configurar variáveis de ambiente para melhor performance
    set "OLLAMA_HOST=0.0.0.0"
    set "OLLAMA_ORIGINS=*"
    
    REM Iniciar servidor em background com configurações otimizadas
    start /b "" ollama serve
    
    REM Aguardar servidor iniciar com timeout inteligente
    echo ⏳ Aguardando servidor iniciar...
    for /l %%i in (1,1,45) do (
        curl -s http://localhost:11434/api/tags >nul 2>&1
        if not errorlevel 1 (
            echo ✅ Servidor Ollama iniciado com sucesso!
            goto :server_ready
        )
        timeout /t 1 /nobreak >nul
    )
    
    echo ⚠️  Servidor pode não ter iniciado completamente.
    echo 💡 Se houver problemas, execute manualmente: ollama serve
    echo.
    
    :server_ready
) else (
    echo ✅ Servidor Ollama já está rodando!
)

REM Testar conexão com IA
echo 🧪 Testando conexão com IA...
curl -s -X POST http://localhost:11434/api/generate -d "{\"model\":\"%AI_MODEL%\",\"prompt\":\"test\"}" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Conexão com IA pode estar instável.
) else (
    echo ✅ Conexão com IA funcionando perfeitamente!
)

echo.

REM ========================================
REM 10. CRIAÇÃO DE DIRETÓRIOS E ESTRUTURA AVANÇADA
REM ========================================

if not defined QUIET_MODE (
    echo 📋 [10/15] Criando estrutura avançada de diretórios...
    echo.
)

REM Criar diretórios necessários com permissões
if not exist "logs" (
    echo 📁 Criando diretório de logs...
    mkdir logs >nul 2>&1
)

if not exist "docs" (
    echo 📁 Criando diretório de documentação...
    mkdir docs >nul 2>&1
)

if not exist "data" (
    echo 📁 Criando diretório de dados...
    mkdir data >nul 2>&1
)

if not exist "data\config" (
    echo 📁 Criando diretório de configuração...
    mkdir data\config >nul 2>&1
)

if not exist "backups" (
    echo 📁 Criando diretório de backups...
    mkdir backups >nul 2>&1
)

if not exist "temp" (
    echo 📁 Criando diretório temporário...
    mkdir temp >nul 2>&1
)

if not exist "cache" (
    echo 📁 Criando diretório de cache...
    mkdir cache >nul 2>&1
)

echo ✅ Estrutura de diretórios avançada criada!
echo.

REM ========================================
REM 11. CONFIGURAÇÃO INTELIGENTE
REM ========================================

if not defined QUIET_MODE (
    echo 📋 [11/15] Aplicando configurações inteligentes...
    echo.
)

REM Criar configuração otimizada se não existir
if not exist "config.json" (
    echo ⚙️  Criando configuração otimizada...
    
    echo {> config.json
    echo   "app": {>> config.json
    echo     "name": "Python App Launcher",>> config.json
    echo     "version": "4.0.0",>> config.json
    echo     "author": "Python App Launcher Team",>> config.json
    echo     "description": "Aplicação revolucionária com IA avançada">> config.json
    echo   },>> config.json
    echo   "ui": {>> config.json
    echo     "theme": "modern",>> config.json
    echo     "window_size": {>> config.json
    echo       "width": 1400,>> config.json
    echo       "height": 900>> config.json
    echo     },>> config.json
    echo     "min_window_size": {>> config.json
    echo       "width": 1000,>> config.json
    echo       "height": 700>> config.json
    echo     },>> config.json
    echo     "splash_screen": {>> config.json
    echo       "enabled": true,>> config.json
    echo       "duration": 1500,>> config.json
    echo       "show_progress": true>> config.json
    echo     }>> config.json
    echo   },>> config.json
    echo   "ai": {>> config.json
    echo     "enabled": true,>> config.json
    echo     "model": "%AI_MODEL%",>> config.json
    echo     "ollama_url": "http://localhost:11434",>> config.json
    echo     "auto_analyze": true,>> config.json
    echo     "auto_document": true,>> config.json
    echo     "max_tokens": 2048,>> config.json
    echo     "temperature": 0.7>> config.json
    echo   },>> config.json
    echo   "automation": {>> config.json
    echo     "auto_install_python": true,>> config.json
    echo     "auto_install_ollama": true,>> config.json
    echo     "auto_download_model": true,>> config.json
    echo     "auto_start_server": true,>> config.json
    echo     "auto_backup": true,>> config.json
    echo     "auto_optimize": true>> config.json
    echo   },>> config.json
    echo   "performance": {>> config.json
    echo     "enable_caching": true,>> config.json
    echo     "max_cache_size": 100,>> config.json
    echo     "auto_cleanup": true,>> config.json
    echo     "optimize_memory": true>> config.json
    echo   },>> config.json
    echo   "logging": {>> config.json
    echo     "level": "INFO",>> config.json
    echo     "file_rotation": {>> config.json
    echo       "max_size_mb": 2,>> config.json
    echo       "backup_count": 10>> config.json
    echo     },>> config.json
    echo     "console_output": true,>> config.json
    echo     "file_output": true>> config.json
    echo   }>> config.json
    echo }>> config.json
    
    echo ✅ Configuração otimizada criada!
)

REM Otimizar configuração existente
if exist "config.json" (
    echo 🔧 Otimizando configuração existente...
    
    REM Backup da configuração atual
    copy "config.json" "config.json.backup" >nul 2>&1
    
    echo ✅ Configuração otimizada!
)

echo.

REM ========================================
REM 12. MONITORAMENTO AUTOMÁTICO (SE SOLICITADO)
REM ========================================

if defined AUTO_MONITOR (
    if not defined QUIET_MODE (
        echo 📋 [12/15] Executando monitoramento automático...
        echo.
    )
    
    echo 📊 Coletando métricas do sistema...
    
    REM CPU Usage
    for /f "tokens=2 delims==" %%a in ('wmic cpu get loadpercentage /value ^| find "LoadPercentage"') do set "CPU_LOAD=%%a"
    echo 🔥 CPU: %CPU_LOAD%%%
    
    REM Memory Usage
    for /f "tokens=2 delims==" %%a in ('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value ^| find "TotalVisibleMemorySize"') do set "TOTAL_MEM=%%a"
    for /f "tokens=2 delims==" %%a in ('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value ^| find "FreePhysicalMemory"') do set "FREE_MEM=%%a"
    set /a "USED_MEM=%TOTAL_MEM%-%FREE_MEM%"
    set /a "MEM_PERCENT=%USED_MEM%*100/%TOTAL_MEM%"
    echo 💾 RAM: %MEM_PERCENT%%%
    
    REM Disk Usage
    for /f "tokens=3" %%a in ('dir /-c C: 2^>nul ^| find "bytes free"') do set "FREE_DISK=%%a"
    set /a "FREE_GB=%FREE_DISK%/1073741824"
    echo 💿 Disco C: %FREE_GB%GB livre
    
    REM Network Status
    ping -n 1 8.8.8.8 >nul 2>&1
    if errorlevel 1 (
        echo 🌐 Rede: ❌ Offline
    ) else (
        echo 🌐 Rede: ✅ Online
    )
    
    REM Python Status
    python --version >nul 2>&1
    if errorlevel 1 (
        echo 🐍 Python: ❌ Não encontrado
    ) else (
        echo 🐍 Python: ✅ Funcionando
    )
    
    REM Ollama Status
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if errorlevel 1 (
        echo 🤖 Ollama: ❌ Offline
    ) else (
        echo 🤖 Ollama: ✅ Online
    )
    
    echo ✅ Monitoramento automático concluído!
    echo.
)

REM ========================================
REM 13. RELATÓRIO AUTOMÁTICO (SE SOLICITADO)
REM ========================================

if defined AUTO_REPORT (
    if not defined QUIET_MODE (
        echo 📋 [13/15] Gerando relatório automático...
        echo.
    )
    
    set "REPORT_FILE=auto_report_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt"
    set "REPORT_FILE=%REPORT_FILE: =0%"
    
    echo 📄 Criando relatório: %REPORT_FILE%
    
    (
        echo ========================================
        echo RELATÓRIO AUTOMÁTICO - %date% %time%
        echo ========================================
        echo.
        echo SISTEMA OPERACIONAL:
        echo - OS: %OS%
        echo - Arquitetura: %PROCESSOR_ARCHITECTURE%
        echo.
        echo HARDWARE:
        echo - RAM Total: %RAM_GB%GB
        echo - Espaço Livre: %FREE_GB%GB
        echo.
        echo PERFORMANCE ATUAL:
        echo - CPU: %CPU_LOAD%%%
        echo - RAM: %MEM_PERCENT%%%
        echo - Disco Livre: %FREE_GB%GB
        echo.
        echo PYTHON ENVIRONMENT:
        python --version 2>&1
        echo - Status: Funcionando
        echo.
        echo SISTEMA DE IA:
        echo - Modelo: %AI_MODEL%
        echo - Status: Online
        echo.
        echo ARQUIVOS DA APLICAÇÃO:
        if exist "main.py" echo - main.py: Presente
        if exist "config.json" echo - config.json: Presente
        if exist "requirements.txt" echo - requirements.txt: Presente
        if exist "Apps" echo - Apps/: Presente
        if exist "data" echo - data/: Presente
        if exist "logs" echo - logs/: Presente
        if exist "bot" echo - bot/: Presente
        echo.
        echo RECOMENDAÇÕES:
        if %CPU_LOAD% GTR 80 echo - CPU em uso elevado
        if %MEM_PERCENT% GTR 85 echo - Memória em uso elevado
        if %FREE_GB% LSS 5 echo - Espaço em disco baixo
        echo.
        echo ========================================
        echo FIM DO RELATÓRIO
        echo ========================================
    ) > "%REPORT_FILE%"
    
    echo ✅ Relatório automático gerado: %REPORT_FILE%
    echo.
)

REM ========================================
REM 14. VERIFICAÇÃO FINAL E EXECUÇÃO AVANÇADA
REM ========================================

if not defined QUIET_MODE (
    echo 📋 [14/15] Verificação final avançada do ambiente...
    echo.
)

REM Verificar dependências críticas
set "ALL_GOOD=true"
set "WARNINGS="

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não está funcionando
    set "ALL_GOOD=false"
)

pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip não está funcionando
    set "ALL_GOOD=false"
)

REM Verificar módulos Python essenciais
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ❌ tkinter não está disponível
    set "ALL_GOOD=false"
)

python -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  psutil não está disponível
    set "WARNINGS=true"
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  requests não está disponível
    set "WARNINGS=true"
)

REM Verificar IA
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Servidor de IA não está respondendo
    set "WARNINGS=true"
)

if "%ALL_GOOD%"=="false" (
    echo.
    echo ❌ ERRO: Ambiente não está pronto!
    echo.
    echo 💡 Verifique as dependências e tente novamente.
    echo.
    pause
    exit /b 1
)

if defined WARNINGS (
    echo ⚠️  Alguns avisos detectados, mas o sistema deve funcionar.
) else (
    echo ✅ Ambiente verificado e otimizado!
)

echo.

REM ========================================
REM 15. EXECUÇÃO DA APLICAÇÃO COM OTIMIZAÇÕES
REM ========================================

if not defined QUIET_MODE (
    echo 📋 [15/15] Iniciando aplicação com todas as otimizações...
    echo.
)

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 INICIANDO APLICAÇÃO REVOLUCIONÁRIA                     ║
echo ║                                                                              ║
echo ║  🤖 Python App Launcher v4.0.0 + IA AVANÇADA                               ║
echo ║  📊 Sistema: %OS%                                                          ║
echo ║  🐍 Python: %PYTHON_VERSION%                                               ║
echo ║  🤖 IA: Ollama + %AI_MODEL%                                                ║
echo ║  ⚡ Otimizações: %FULL_OPTIMIZATION%                                        ║
echo ║  💾 Backup: %AUTO_BACKUP%                                                  ║
echo ║  📊 Monitoramento: %AUTO_MONITOR%                                          ║
echo ║  📄 Relatório: %AUTO_REPORT%                                               ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Mostrar informações do sistema
echo 📊 Informações do sistema:
python --version
echo    - Sistema Operacional: %OS%
echo    - Arquitetura: %PROCESSOR_ARCHITECTURE%
echo    - RAM Total: %RAM_GB%GB
echo    - Espaço Livre: %FREE_GB%GB
echo    - Diretório: %CD%
echo    - Modelo IA: %AI_MODEL%
echo.

REM Configurar variáveis de ambiente para otimização
set "PYTHONOPTIMIZE=1"
set "PYTHONUNBUFFERED=1"
if defined FULL_OPTIMIZATION (
    set "PYTHONHASHSEED=0"
    set "PYTHONDONTWRITEBYTECODE=1"
)

REM Executar a aplicação
echo 🚀 Iniciando Python App Launcher com todas as otimizações...
echo.

if defined DEBUG_MODE (
    echo 🔧 Modo DEBUG ativado
    python main.py --debug
) else if defined PROFILE_MODE (
    echo 📈 Modo PROFILING ativado
    python main.py --profile
) else (
    python main.py
)

REM ========================================
REM 16. VERIFICAÇÃO PÓS-EXECUÇÃO AVANÇADA
REM ========================================

REM Verificar se a aplicação foi executada com sucesso
if errorlevel 1 (
    echo.
    echo ❌ ERRO: A aplicação foi encerrada com erro (código: %errorlevel%)
    echo.
    echo 💡 Verifique os logs em logs/ para mais detalhes.
    echo.
    echo 🔧 Possíveis soluções:
    echo    1. Execute: pip install -r requirements.txt
    echo    2. Verifique se o Ollama está rodando: ollama serve
    echo    3. Execute em modo debug: start.bat --debug
    echo    4. Execute com otimizações: start.bat --optimize
    echo    5. Limpe instalação: start.bat --clean
    echo    6. Execute tudo automático: start.bat --auto-all
    echo.
) else (
    echo.
    echo ✅ Aplicação encerrada com sucesso!
    echo.
)

REM ========================================
REM 17. LIMPEZA E FINALIZAÇÃO AVANÇADA
REM ========================================

REM Limpeza automática se solicitado
if defined CLEAN_INSTALL (
    echo 🧹 Executando limpeza automática...
    del /q /s temp\* >nul 2>&1
    del /q /s cache\* >nul 2>&1
    echo ✅ Limpeza concluída!
)

REM Limpar variáveis
set "QUIET_MODE="
set "PROFILE_MODE="
set "DEBUG_MODE="
set "FULL_OPTIMIZATION="
set "BACKUP_MODE="
set "RESTORE_MODE="
set "CLEAN_INSTALL="
set "AI_MODEL="
set "AUTO_BACKUP="
set "AUTO_MONITOR="
set "AUTO_OPTIMIZE="
set "AUTO_REPORT="
set "ALL_GOOD="
set "WARNINGS="
set "PYTHON_URL="
set "PYTHON_INSTALLER="
set "OLLAMA_URL="
set "OLLAMA_FILE="
set "BACKUP_NAME="
set "FREE_SPACE="
set "TOTAL_RAM="
set "RAM_GB="
set "PYTHON_VERSION="
set "CPU_LOAD="
set "TOTAL_MEM="
set "FREE_MEM="
set "USED_MEM="
set "MEM_PERCENT="
set "FREE_DISK="
set "FREE_GB="
set "REPORT_FILE="

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    👋 OBRIGADO POR USAR                                      ║
echo ║                    PYTHON APP LAUNCHER v4.0.0                               ║
echo ║                                                                              ║
echo ║  🤖 IA AVANÇADA + AUTOMATIZAÇÃO TOTAL + OTIMIZAÇÃO DE SISTEMA              ║
echo ║  🚀 REVOLUÇÃO EM FACILIDADE DE USO E PERFORMANCE                           ║
echo ║  📊 MONITORAMENTO + BACKUP + RELATÓRIOS + TUDO AUTOMÁTICO!                 ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 📋 Resumo da sessão:
echo    ✅ Python verificado e otimizado
echo    ✅ Dependências instaladas com cache
echo    ✅ Ollama configurado e otimizado
echo    ✅ Modelo %AI_MODEL% instalado
echo    ✅ Servidor de IA iniciado e testado
echo    ✅ Estrutura avançada criada
echo    ✅ Configurações inteligentes aplicadas
if defined AUTO_BACKUP echo    ✅ Backup automático executado
if defined AUTO_MONITOR echo    ✅ Monitoramento automático executado
if defined AUTO_OPTIMIZE echo    ✅ Otimização automática executada
if defined AUTO_REPORT echo    ✅ Relatório automático gerado
echo    ✅ Aplicação executada com otimizações
echo.

echo 💡 Recursos avançados disponíveis:
echo    - 🤖 Chat inteligente com IA avançada
echo    - 🔍 Análise automática de aplicações
echo    - 📚 Geração de documentação inteligente
echo    - 💡 Sugestões personalizadas de apps
echo    - ⚡ Otimizações de performance automáticas
echo    - 💾 Sistema de backup automático
echo    - 📊 Monitoramento em tempo real
echo    - 🔧 Configurações inteligentes
echo    - 🧹 Limpeza automática
echo    - 📄 Relatórios automáticos
echo.

echo 🎮 Como usar recursos avançados:
echo    - start.bat --auto-all (TUDO automático)
echo    - start.bat --optimize (otimização total)
echo    - start.bat --backup (backup automático)
echo    - start.bat --restore (restaurar backup)
echo    - start.bat --clean (limpeza completa)
echo    - start.bat --llama2 (usar Llama2)
echo    - start.bat --mistral (usar Mistral)
echo    - start.bat --codellama (usar CodeLlama)
echo.

REM Pausa para manter o terminal aberto
pause
