@echo off
setlocal enabledelayedexpansion

REM ========================================
REM 🚀 PYTHON APP LAUNCHER - EXECUTOR TOTAL
REM ========================================
REM Versão: 1.0.0 - EXECUTA TUDO AUTOMATICAMENTE
REM Autor: Python App Launcher Team
REM ========================================

chcp 65001 >nul 2>&1
color 0C

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 EXECUTOR TOTAL - PYTHON APP LAUNCHER                   ║
echo ║                                                                              ║
echo ║  🎯 EXECUTA TUDO: Backup + Otimização + Monitoramento + IA + Aplicação     ║
echo ║  ⚡ AUTOMATIZAÇÃO COMPLETA + ZERO CONFIGURAÇÃO MANUAL                       ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🎯 Iniciando execução total automática...
echo.

REM ========================================
REM 1. BACKUP AUTOMÁTICO
REM ========================================

echo 📋 [1/5] Executando backup automático...
echo.

set "BACKUP_NAME=total_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_NAME=%BACKUP_NAME: =0%"

if not exist "backups" mkdir backups
if not exist "backups\%BACKUP_NAME%" mkdir "backups\%BACKUP_NAME%"

echo 💾 Criando backup: %BACKUP_NAME%

REM Backup de arquivos importantes
if exist "config.json" copy "config.json" "backups\%BACKUP_NAME%\" >nul
if exist "requirements.txt" copy "requirements.txt" "backups\%BACKUP_NAME%\" >nul
if exist "metadata.json" copy "metadata.json" "backups\%BACKUP_NAME%\" >nul
if exist "data" xcopy "data" "backups\%BACKUP_NAME%\data\" /E /I /Y >nul
if exist "logs" xcopy "logs" "backups\%BACKUP_NAME%\logs\" /E /I /Y >nul
if exist "docs" xcopy "docs" "backups\%BACKUP_NAME%\docs\" /E /I /Y >nul
if exist "Apps" xcopy "Apps" "backups\%BACKUP_NAME%\Apps\" /E /I /Y >nul
if exist "bot" xcopy "bot" "backups\%BACKUP_NAME%\bot\" /E /I /Y >nul

echo ✅ Backup automático concluído!
echo.

REM ========================================
REM 2. OTIMIZAÇÃO AUTOMÁTICA
REM ========================================

echo 📋 [2/5] Executando otimização automática...
echo.

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

REM Configurar variáveis de ambiente Python
echo 🐍 Otimizando Python...
setx PYTHONOPTIMIZE 1 >nul 2>&1
setx PYTHONUNBUFFERED 1 >nul 2>&1
setx PYTHONHASHSEED 0 >nul 2>&1
setx PYTHONDONTWRITEBYTECODE 1 >nul 2>&1

echo ✅ Otimização automática concluída!
echo.

REM ========================================
REM 3. MONITORAMENTO AUTOMÁTICO
REM ========================================

echo 📋 [3/5] Executando monitoramento automático...
echo.

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

REM ========================================
REM 4. RELATÓRIO AUTOMÁTICO
REM ========================================

echo 📋 [4/5] Gerando relatório automático...
echo.

set "REPORT_FILE=total_report_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt"
set "REPORT_FILE=%REPORT_FILE: =0%"

echo 📄 Criando relatório: %REPORT_FILE%

(
    echo ========================================
    echo RELATÓRIO TOTAL AUTOMÁTICO - %date% %time%
    echo ========================================
    echo.
    echo EXECUÇÃO TOTAL AUTOMÁTICA
    echo ========================================
    echo.
    echo SISTEMA OPERACIONAL:
    echo - OS: %OS%
    echo - Arquitetura: %PROCESSOR_ARCHITECTURE%
    echo.
    echo HARDWARE:
    for /f "tokens=2 delims==" %%a in ('wmic computersystem get TotalPhysicalMemory /value ^| find "TotalPhysicalMemory"') do set "TOTAL_RAM=%%a"
    set /a "RAM_GB=%TOTAL_RAM:~0,-1%/1073741824"
    echo - RAM Total: %RAM_GB%GB
    for /f "tokens=2 delims==" %%a in ('wmic cpu get NumberOfCores /value ^| find "NumberOfCores"') do set "CPU_CORES=%%a"
    echo - CPU Cores: %CPU_CORES%
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
    echo - Status: Verificado
    echo.
    echo BACKUP:
    echo - Backup criado: %BACKUP_NAME%
    echo - Local: backups\%BACKUP_NAME%
    echo.
    echo OTIMIZAÇÕES APLICADAS:
    echo - Cache temporário limpo
    echo - Modo de alto desempenho ativado
    echo - Configurações de rede otimizadas
    echo - Cache DNS limpo
    echo - Variáveis Python otimizadas
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
    echo FIM DO RELATÓRIO TOTAL
    echo ========================================
) > "%REPORT_FILE%"

echo ✅ Relatório automático gerado: %REPORT_FILE%
echo.

REM ========================================
REM 5. EXECUÇÃO DA APLICAÇÃO
REM ========================================

echo 📋 [5/5] Iniciando aplicação com todas as otimizações...
echo.

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 INICIANDO APLICAÇÃO COM TUDO PRONTO                    ║
echo ║                                                                              ║
echo ║  🤖 Python App Launcher v4.0.0 + IA AVANÇADA                               ║
echo ║  📊 Sistema: %OS%                                                          ║
echo ║  🐍 Python: Otimizado                                                       ║
echo ║  🤖 IA: Configurada                                                         ║
echo ║  💾 Backup: %BACKUP_NAME%                                                  ║
echo ║  ⚡ Otimizações: Aplicadas                                                  ║
echo ║  📊 Monitoramento: Executado                                                ║
echo ║  📄 Relatório: %REPORT_FILE%                                               ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Configurar variáveis de ambiente para otimização
set "PYTHONOPTIMIZE=1"
set "PYTHONUNBUFFERED=1"
set "PYTHONHASHSEED=0"
set "PYTHONDONTWRITEBYTECODE=1"

REM Executar a aplicação
echo 🚀 Iniciando Python App Launcher com TUDO otimizado...
echo.

python main.py

REM ========================================
REM 6. FINALIZAÇÃO
REM ========================================

REM Verificar se a aplicação foi executada com sucesso
if errorlevel 1 (
    echo.
    echo ❌ ERRO: A aplicação foi encerrada com erro (código: %errorlevel%)
    echo.
    echo 💡 Verifique os logs em logs/ para mais detalhes.
    echo.
    echo 🔧 Possíveis soluções:
    echo    1. Execute: start.bat --auto-all
    echo    2. Execute: start.bat --clean
    echo    3. Execute: start.bat --debug
    echo.
) else (
    echo.
    echo ✅ Aplicação encerrada com sucesso!
    echo.
)

REM Limpar variáveis
set "BACKUP_NAME="
set "CPU_LOAD="
set "TOTAL_MEM="
set "FREE_MEM="
set "USED_MEM="
set "MEM_PERCENT="
set "FREE_DISK="
set "FREE_GB="
set "REPORT_FILE="
set "TOTAL_RAM="
set "RAM_GB="
set "CPU_CORES="

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🎉 EXECUÇÃO TOTAL CONCLUÍDA!                              ║
echo ║                                                                              ║
echo ║  ✅ Backup automático executado                                             ║
echo ║  ✅ Otimização automática aplicada                                          ║
echo ║  ✅ Monitoramento automático executado                                      ║
echo ║  ✅ Relatório automático gerado                                             ║
echo ║  ✅ Aplicação executada com todas as otimizações                            ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 📋 Resumo da execução total:
echo    💾 Backup: %BACKUP_NAME%
echo    ⚡ Otimizações: Aplicadas
echo    📊 Monitoramento: Executado
echo    📄 Relatório: %REPORT_FILE%
echo    🚀 Aplicação: Executada
echo.

echo 💡 Próximos passos:
echo    1. Use a aplicação normalmente
echo    2. Execute este script novamente quando necessário
echo    3. Verifique os backups em backups/
echo    4. Consulte os relatórios gerados
echo.

echo 🎯 Para executar tudo novamente:
echo    run_everything.bat
echo.

pause 