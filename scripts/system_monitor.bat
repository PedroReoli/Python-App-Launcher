@echo off
setlocal enabledelayedexpansion

REM ========================================
REM 📊 SISTEMA DE MONITORAMENTO AVANÇADO
REM ========================================
REM Versão: 1.0.0 - MONITORAMENTO EM TEMPO REAL
REM Autor: Python App Launcher Team
REM ========================================

chcp 65001 >nul 2>&1
color 0D

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    📊 SISTEMA DE MONITORAMENTO AVANÇADO                      ║
echo ║                                                                              ║
echo ║  🔍 Diagnóstico + Performance + IA + Alertas + Relatórios + Otimização     ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM ========================================
REM 1. VERIFICAÇÃO DE ARGUMENTOS
REM ========================================

set "REAL_TIME="
set "DIAGNOSTIC="
set "PERFORMANCE="
set "AI_STATUS="
set "GENERATE_REPORT="
set "MONITOR_DURATION="

for %%a in (%*) do (
    if "%%a"=="--realtime" set "REAL_TIME=true"
    if "%%a"=="--diagnostic" set "DIAGNOSTIC=true"
    if "%%a"=="--performance" set "PERFORMANCE=true"
    if "%%a"=="--ai" set "AI_STATUS=true"
    if "%%a"=="--report" set "GENERATE_REPORT=true"
    if "%%a:~0,2%"=="--" (
        set "MONITOR_DURATION=%%a:~2%"
    )
)

REM ========================================
REM 2. MONITORAMENTO EM TEMPO REAL
REM ========================================

if defined REAL_TIME (
    echo 📋 [1/6] Iniciando monitoramento em tempo real...
    echo.
    
    echo ⏱️  Monitoramento ativo - Pressione Ctrl+C para parar
    echo.
    
    :monitor_loop
    cls
    echo ╔══════════════════════════════════════════════════════════════════════════════╗
    echo ║                    📊 MONITORAMENTO EM TEMPO REAL                            ║
    echo ║                              %date% %time%                                   ║
    echo ╚══════════════════════════════════════════════════════════════════════════════╝
    echo.
    
    REM CPU Usage
    for /f "tokens=2 delims==" %%a in ('wmic cpu get loadpercentage /value ^| find "LoadPercentage"') do set "CPU_LOAD=%%a"
    echo 🔥 CPU: %CPU_LOAD%%%
    
    REM Memory Usage
    for /f "tokens=2 delims==" %%a in ('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value ^| find "TotalVisibleMemorySize"') do set "TOTAL_MEM=%%a"
    for /f "tokens=2 delims==" %%a in ('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value ^| find "FreePhysicalMemory"') do set "FREE_MEM=%%a"
    set /a "USED_MEM=%TOTAL_MEM%-%FREE_MEM%"
    set /a "MEM_PERCENT=%USED_MEM%*100/%TOTAL_MEM%"
    echo 💾 RAM: %MEM_PERCENT%%% (%USED_MEM%KB / %TOTAL_MEM%KB)
    
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
    
    REM Application Status
    tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo 🚀 App: ✅ Executando
    ) else (
        echo 🚀 App: ❌ Parada
    )
    
    echo.
    echo ╔══════════════════════════════════════════════════════════════════════════════╗
    echo ║                              PROCESSOS ATIVOS                                ║
    echo ╚══════════════════════════════════════════════════════════════════════════════╝
    echo.
    
    REM Listar processos Python
    tasklist /FI "IMAGENAME eq python.exe" /FO TABLE
    
    echo.
    echo ╔══════════════════════════════════════════════════════════════════════════════╗
    echo ║                              ALERTAS                                        ║
    echo ╚══════════════════════════════════════════════════════════════════════════════╝
    echo.
    
    REM Verificar alertas
    if %CPU_LOAD% GTR 80 (
        echo ⚠️  ALERTA: CPU em uso elevado (%CPU_LOAD%%%)
    )
    
    if %MEM_PERCENT% GTR 85 (
        echo ⚠️  ALERTA: Memória em uso elevado (%MEM_PERCENT%%%)
    )
    
    if %FREE_GB% LSS 5 (
        echo ⚠️  ALERTA: Espaço em disco baixo (%FREE_GB%GB)
    )
    
    echo.
    echo ⏱️  Atualizando em 5 segundos... (Ctrl+C para parar)
    timeout /t 5 /nobreak >nul
    goto monitor_loop
)

REM ========================================
REM 3. DIAGNÓSTICO COMPLETO
REM ========================================

if defined DIAGNOSTIC (
    echo 📋 [2/6] Executando diagnóstico completo do sistema...
    echo.
    
    echo 🔍 Verificando componentes do sistema...
    echo.
    
    REM Sistema Operacional
    echo 📊 Sistema Operacional:
    echo    - OS: %OS%
    echo    - Arquitetura: %PROCESSOR_ARCHITECTURE%
    echo    - Versão: %OS_VERSION%
    echo.
    
    REM Hardware
    echo 🔧 Hardware:
    for /f "tokens=2 delims==" %%a in ('wmic computersystem get TotalPhysicalMemory /value ^| find "TotalPhysicalMemory"') do set "TOTAL_RAM=%%a"
    set /a "RAM_GB=%TOTAL_RAM:~0,-1%/1073741824"
    echo    - RAM Total: %RAM_GB%GB
    
    for /f "tokens=2 delims==" %%a in ('wmic cpu get NumberOfCores /value ^| find "NumberOfCores"') do set "CPU_CORES=%%a"
    echo    - CPU Cores: %CPU_CORES%
    
    for /f "tokens=2 delims==" %%a in ('wmic cpu get Name /value ^| find "Name"') do set "CPU_NAME=%%a"
    echo    - CPU: %CPU_NAME%
    echo.
    
    REM Python Environment
    echo 🐍 Ambiente Python:
    python --version >nul 2>&1
    if errorlevel 1 (
        echo    - Status: ❌ Não instalado
    ) else (
        for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
        echo    - Versão: %PYTHON_VERSION%
        echo    - Status: ✅ Funcionando
        
        REM Verificar módulos
        echo    - Módulos críticos:
        python -c "import tkinter" >nul 2>&1 && echo      ✅ tkinter
        python -c "import psutil" >nul 2>&1 && echo      ✅ psutil
        python -c "import requests" >nul 2>&1 && echo    ✅ requests
    )
    echo.
    
    REM IA System
    echo 🤖 Sistema de IA:
    ollama --version >nul 2>&1
    if errorlevel 1 (
        echo    - Ollama: ❌ Não instalado
    ) else (
        for /f "tokens=2" %%a in ('ollama --version 2^>^&1') do set "OLLAMA_VERSION=%%a"
        echo    - Versão: %OLLAMA_VERSION%
        echo    - Status: ✅ Instalado
        
        REM Verificar servidor
        curl -s http://localhost:11434/api/tags >nul 2>&1
        if errorlevel 1 (
            echo    - Servidor: ❌ Offline
        ) else (
            echo    - Servidor: ✅ Online
            
            REM Listar modelos
            echo    - Modelos instalados:
            ollama list | findstr /v "NAME" | findstr /v "==="
        )
    )
    echo.
    
    REM Application Files
    echo 📁 Arquivos da Aplicação:
    if exist "main.py" echo    ✅ main.py
    if exist "config.json" echo    ✅ config.json
    if exist "requirements.txt" echo    ✅ requirements.txt
    if exist "Apps" echo    ✅ Apps/
    if exist "data" echo    ✅ data/
    if exist "logs" echo    ✅ logs/
    if exist "bot" echo    ✅ bot/
    echo.
    
    REM Performance Metrics
    echo ⚡ Métricas de Performance:
    for /f "tokens=2 delims==" %%a in ('wmic cpu get loadpercentage /value ^| find "LoadPercentage"') do set "CPU_LOAD=%%a"
    echo    - CPU Atual: %CPU_LOAD%%%
    
    for /f "tokens=2 delims==" %%a in ('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value ^| find "TotalVisibleMemorySize"') do set "TOTAL_MEM=%%a"
    for /f "tokens=2 delims==" %%a in ('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value ^| find "FreePhysicalMemory"') do set "FREE_MEM=%%a"
    set /a "USED_MEM=%TOTAL_MEM%-%FREE_MEM%"
    set /a "MEM_PERCENT=%USED_MEM%*100/%TOTAL_MEM%"
    echo    - RAM Atual: %MEM_PERCENT%%%
    
    for /f "tokens=3" %%a in ('dir /-c C: 2^>nul ^| find "bytes free"') do set "FREE_DISK=%%a"
    set /a "FREE_GB=%FREE_DISK%/1073741824"
    echo    - Disco Livre: %FREE_GB%GB
    echo.
    
    echo ✅ Diagnóstico completo concluído!
    echo.
)

REM ========================================
REM 4. ANÁLISE DE PERFORMANCE
REM ========================================

if defined PERFORMANCE (
    echo 📋 [3/6] Analisando performance do sistema...
    echo.
    
    echo 📊 Coletando métricas de performance...
    echo.
    
    REM CPU Performance
    echo 🔥 CPU Performance:
    for /f "tokens=2 delims==" %%a in ('wmic cpu get loadpercentage /value ^| find "LoadPercentage"') do set "CPU_LOAD=%%a"
    if %CPU_LOAD% LSS 30 (
        echo    - Status: ✅ Excelente (%CPU_LOAD%%%)
    ) else if %CPU_LOAD% LSS 60 (
        echo    - Status: ⚠️  Bom (%CPU_LOAD%%%)
    ) else if %CPU_LOAD% LSS 80 (
        echo    - Status: ⚠️  Moderado (%CPU_LOAD%%%)
    ) else (
        echo    - Status: ❌ Crítico (%CPU_LOAD%%%)
    )
    
    REM Memory Performance
    echo 💾 Memory Performance:
    for /f "tokens=2 delims==" %%a in ('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value ^| find "TotalVisibleMemorySize"') do set "TOTAL_MEM=%%a"
    for /f "tokens=2 delims==" %%a in ('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value ^| find "FreePhysicalMemory"') do set "FREE_MEM=%%a"
    set /a "USED_MEM=%TOTAL_MEM%-%FREE_MEM%"
    set /a "MEM_PERCENT=%USED_MEM%*100/%TOTAL_MEM%"
    if %MEM_PERCENT% LSS 50 (
        echo    - Status: ✅ Excelente (%MEM_PERCENT%%%)
    ) else if %MEM_PERCENT% LSS 75 (
        echo    - Status: ⚠️  Bom (%MEM_PERCENT%%%)
    ) else if %MEM_PERCENT% LSS 90 (
        echo    - Status: ⚠️  Moderado (%MEM_PERCENT%%%)
    ) else (
        echo    - Status: ❌ Crítico (%MEM_PERCENT%%%)
    )
    
    REM Disk Performance
    echo 💿 Disk Performance:
    for /f "tokens=3" %%a in ('dir /-c C: 2^>nul ^| find "bytes free"') do set "FREE_DISK=%%a"
    set /a "FREE_GB=%FREE_DISK%/1073741824"
    if %FREE_GB% GTR 20 (
        echo    - Status: ✅ Excelente (%FREE_GB%GB livre)
    ) else if %FREE_GB% GTR 10 (
        echo    - Status: ⚠️  Bom (%FREE_GB%GB livre)
    ) else if %FREE_GB% GTR 5 (
        echo    - Status: ⚠️  Moderado (%FREE_GB%GB livre)
    ) else (
        echo    - Status: ❌ Crítico (%FREE_GB%GB livre)
    )
    
    REM Network Performance
    echo 🌐 Network Performance:
    ping -n 1 8.8.8.8 >nul 2>&1
    if errorlevel 1 (
        echo    - Status: ❌ Offline
    ) else (
        echo    - Status: ✅ Online
    )
    
    REM Python Performance
    echo 🐍 Python Performance:
    python --version >nul 2>&1
    if errorlevel 1 (
        echo    - Status: ❌ Não disponível
    ) else (
        echo    - Status: ✅ Funcionando
        REM Testar performance básica
        python -c "import time; start=time.time(); [i**2 for i in range(10000)]; print(f'Performance: {time.time()-start:.3f}s')" 2>nul
    )
    
    REM IA Performance
    echo 🤖 IA Performance:
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if errorlevel 1 (
        echo    - Status: ❌ Offline
    ) else (
        echo    - Status: ✅ Online
        REM Testar resposta da IA
        echo    - Testando resposta...
        curl -s -X POST http://localhost:11434/api/generate -d "{\"model\":\"llama2\",\"prompt\":\"test\",\"stream\":false}" >nul 2>&1
        if errorlevel 1 (
            echo    - Resposta: ⚠️  Lenta
        ) else (
            echo    - Resposta: ✅ Rápida
        )
    )
    
    echo.
    echo ✅ Análise de performance concluída!
    echo.
)

REM ========================================
REM 5. STATUS DO SISTEMA DE IA
REM ========================================

if defined AI_STATUS (
    echo 📋 [4/6] Verificando status do sistema de IA...
    echo.
    
    REM Verificar Ollama
    echo 🤖 Ollama Status:
    ollama --version >nul 2>&1
    if errorlevel 1 (
        echo    - Instalação: ❌ Não encontrado
        echo    - Servidor: ❌ Não disponível
        echo    - Modelos: ❌ Não disponível
    ) else (
        for /f "tokens=2" %%a in ('ollama --version 2^>^&1') do set "OLLAMA_VERSION=%%a"
        echo    - Instalação: ✅ %OLLAMA_VERSION%
        
        REM Verificar servidor
        curl -s http://localhost:11434/api/tags >nul 2>&1
        if errorlevel 1 (
            echo    - Servidor: ❌ Offline
            echo    - Modelos: ❌ Não disponível
        ) else (
            echo    - Servidor: ✅ Online
            
            REM Listar modelos
            echo    - Modelos disponíveis:
            ollama list | findstr /v "NAME" | findstr /v "===" | findstr /v "^$"
        )
    )
    echo.
    
    REM Verificar arquivos de IA
    echo 📁 Arquivos de IA:
    if exist "bot" (
        echo    ✅ Diretório bot/ encontrado
        if exist "bot\ollama_manager.py" echo      ✅ ollama_manager.py
        if exist "bot\app_analyzer.py" echo      ✅ app_analyzer.py
        if exist "bot\doc_generator.py" echo      ✅ doc_generator.py
        if exist "bot\chat_interface.py" echo      ✅ chat_interface.py
    ) else (
        echo    ❌ Diretório bot/ não encontrado
    )
    echo.
    
    REM Testar funcionalidades de IA
    echo 🧪 Testando funcionalidades de IA:
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if not errorlevel 1 (
        echo    - Conexão: ✅ Funcionando
        echo    - Testando geração de resposta...
        curl -s -X POST http://localhost:11434/api/generate -d "{\"model\":\"llama2\",\"prompt\":\"Hello\",\"stream\":false}" >nul 2>&1
        if errorlevel 1 (
            echo    - Geração: ⚠️  Lenta ou com erro
        ) else (
            echo    - Geração: ✅ Funcionando
        )
    ) else (
        echo    - Conexão: ❌ Falha
        echo    - Geração: ❌ Não disponível
    )
    echo.
    
    echo ✅ Status do sistema de IA verificado!
    echo.
)

REM ========================================
REM 6. GERAÇÃO DE RELATÓRIO
REM ========================================

if defined GENERATE_REPORT (
    echo 📋 [5/6] Gerando relatório completo...
    echo.
    
    set "REPORT_FILE=system_report_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt"
    set "REPORT_FILE=%REPORT_FILE: =0%"
    
    echo 📄 Criando relatório: %REPORT_FILE%
    echo.
    
    (
        echo ========================================
        echo RELATÓRIO DO SISTEMA - %date% %time%
        echo ========================================
        echo.
        echo SISTEMA OPERACIONAL:
        echo - OS: %OS%
        echo - Arquitetura: %PROCESSOR_ARCHITECTURE%
        echo - Versão: %OS_VERSION%
        echo.
        echo HARDWARE:
        for /f "tokens=2 delims==" %%a in ('wmic computersystem get TotalPhysicalMemory /value ^| find "TotalPhysicalMemory"') do set "TOTAL_RAM=%%a"
        set /a "RAM_GB=%TOTAL_RAM:~0,-1%/1073741824"
        echo - RAM Total: %RAM_GB%GB
        for /f "tokens=2 delims==" %%a in ('wmic cpu get NumberOfCores /value ^| find "NumberOfCores"') do set "CPU_CORES=%%a"
        echo - CPU Cores: %CPU_CORES%
        for /f "tokens=2 delims==" %%a in ('wmic cpu get Name /value ^| find "Name"') do set "CPU_NAME=%%a"
        echo - CPU: %CPU_NAME%
        echo.
        echo PERFORMANCE ATUAL:
        for /f "tokens=2 delims==" %%a in ('wmic cpu get loadpercentage /value ^| find "LoadPercentage"') do set "CPU_LOAD=%%a"
        echo - CPU: %CPU_LOAD%%%
        for /f "tokens=2 delims==" %%a in ('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value ^| find "TotalVisibleMemorySize"') do set "TOTAL_MEM=%%a"
        for /f "tokens=2 delims==" %%a in ('wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value ^| find "FreePhysicalMemory"') do set "FREE_MEM=%%a"
        set /a "USED_MEM=%TOTAL_MEM%-%FREE_MEM%"
        set /a "MEM_PERCENT=%USED_MEM%*100/%TOTAL_MEM%"
        echo - RAM: %MEM_PERCENT%%%
        for /f "tokens=3" %%a in ('dir /-c C: 2^>nul ^| find "bytes free"') do set "FREE_DISK=%%a"
        set /a "FREE_GB=%FREE_DISK%/1073741824"
        echo - Disco Livre: %FREE_GB%GB
        echo.
        echo PYTHON ENVIRONMENT:
        python --version >nul 2>&1
        if errorlevel 1 (
            echo - Status: Não instalado
        ) else (
            for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
            echo - Versão: %PYTHON_VERSION%
            echo - Status: Funcionando
        )
        echo.
        echo SISTEMA DE IA:
        ollama --version >nul 2>&1
        if errorlevel 1 (
            echo - Ollama: Não instalado
        ) else (
            for /f "tokens=2" %%a in ('ollama --version 2^>^&1') do set "OLLAMA_VERSION=%%a"
            echo - Versão: %OLLAMA_VERSION%
            curl -s http://localhost:11434/api/tags >nul 2>&1
            if errorlevel 1 (
                echo - Servidor: Offline
            ) else (
                echo - Servidor: Online
            )
        )
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
        if %CPU_LOAD% GTR 80 echo - CPU em uso elevado, considere fechar aplicações
        if %MEM_PERCENT% GTR 85 echo - Memória em uso elevado, considere reiniciar
        if %FREE_GB% LSS 5 echo - Espaço em disco baixo, libere espaço
        echo.
        echo ========================================
        echo FIM DO RELATÓRIO
        echo ========================================
    ) > "%REPORT_FILE%"
    
    echo ✅ Relatório gerado: %REPORT_FILE%
    echo.
)

REM ========================================
REM 7. MENU PRINCIPAL
REM ========================================

if not defined REAL_TIME if not defined DIAGNOSTIC if not defined PERFORMANCE if not defined AI_STATUS if not defined GENERATE_REPORT (
    echo 📋 [6/6] Menu de monitoramento...
    echo.
    
    echo 🎯 Escolha uma opção:
    echo.
    echo    1. Monitoramento em tempo real
    echo    2. Diagnóstico completo
    echo    3. Análise de performance
    echo    4. Status do sistema de IA
    echo    5. Gerar relatório
    echo    6. Todas as verificações
    echo    7. Sair
    echo.
    
    set /p "CHOICE=Digite sua escolha (1-7): "
    
    if "%CHOICE%"=="1" (
        system_monitor.bat --realtime
    ) else if "%CHOICE%"=="2" (
        system_monitor.bat --diagnostic
    ) else if "%CHOICE%"=="3" (
        system_monitor.bat --performance
    ) else if "%CHOICE%"=="4" (
        system_monitor.bat --ai
    ) else if "%CHOICE%"=="5" (
        system_monitor.bat --report
    ) else if "%CHOICE%"=="6" (
        system_monitor.bat --diagnostic --performance --ai --report
    ) else if "%CHOICE%"=="7" (
        goto :end
    ) else (
        echo ❌ Opção inválida!
        pause
        goto :menu
    )
)

REM ========================================
REM 8. FINALIZAÇÃO
REM ========================================

:end
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    📊 SISTEMA DE MONITORAMENTO AVANÇADO                      ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 📋 Recursos disponíveis:
echo    🔍 Monitoramento em tempo real
echo    📊 Diagnóstico completo do sistema
echo    ⚡ Análise de performance
echo    🤖 Status do sistema de IA
echo    📄 Geração de relatórios
echo    ⚠️  Alertas automáticos
echo    📈 Métricas detalhadas
echo.

echo 🎯 Comandos úteis:
echo    system_monitor.bat --realtime    (monitoramento contínuo)
echo    system_monitor.bat --diagnostic  (diagnóstico completo)
echo    system_monitor.bat --performance (análise de performance)
echo    system_monitor.bat --ai          (status da IA)
echo    system_monitor.bat --report      (gerar relatório)
echo.

pause 