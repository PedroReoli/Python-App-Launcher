@echo off
REM ========================================
REM 💾 PYTHON APP LAUNCHER - BACKUP
REM ========================================

echo Executando backup...
echo.
cd /d "%~dp0"
call scripts\backup_manager.bat %*
pause 