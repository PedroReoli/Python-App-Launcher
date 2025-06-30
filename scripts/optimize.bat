@echo off
REM ========================================
REM ⚡ PYTHON APP LAUNCHER - OTIMIZAÇÃO
REM ========================================

echo Executando otimização...
echo.
cd /d "%~dp0"
call scripts\optimize_system.bat %*
pause 