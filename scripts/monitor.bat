@echo off
REM ========================================
REM 📊 PYTHON APP LAUNCHER - MONITORAMENTO
REM ========================================

echo Executando monitoramento...
echo.
cd /d "%~dp0"
call scripts\system_monitor.bat %*
pause 