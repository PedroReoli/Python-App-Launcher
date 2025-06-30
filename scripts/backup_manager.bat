@echo off
setlocal enabledelayedexpansion

REM ========================================
REM 💾 SISTEMA DE BACKUP E RESTAURAÇÃO AVANÇADO
REM ========================================
REM Versão: 1.0.0 - BACKUP INTELIGENTE
REM Autor: Python App Launcher Team
REM ========================================

chcp 65001 >nul 2>&1
color 0E

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    💾 SISTEMA DE BACKUP AVANÇADO                             ║
echo ║                                                                              ║
echo ║  🔒 Criptografia + Compressão + Backup Inteligente + Restauração Rápida    ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM ========================================
REM 1. VERIFICAÇÃO DE ARGUMENTOS
REM ========================================

set "BACKUP_MODE="
set "RESTORE_MODE="
set "AUTO_BACKUP="
set "ENCRYPTED_BACKUP="
set "COMPRESSED_BACKUP="
set "BACKUP_NAME="

for %%a in (%*) do (
    if "%%a"=="--backup" set "BACKUP_MODE=true"
    if "%%a"=="--restore" set "RESTORE_MODE=true"
    if "%%a"=="--auto" set "AUTO_BACKUP=true"
    if "%%a"=="--encrypt" set "ENCRYPTED_BACKUP=true"
    if "%%a"=="--compress" set "COMPRESSED_BACKUP=true"
    if "%%a:~0,2%"=="--" (
        set "BACKUP_NAME=%%a:~2%"
    )
)

REM Definir nome padrão se não especificado
if not defined BACKUP_NAME set "BACKUP_NAME=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_NAME=%BACKUP_NAME: =0%"

REM ========================================
REM 2. CRIAÇÃO DE BACKUP
REM ========================================

if defined BACKUP_MODE (
    echo 📋 [1/4] Iniciando backup avançado...
    echo.
    
    REM Criar diretório de backup se não existir
    if not exist "backups" mkdir backups
    if not exist "backups\%BACKUP_NAME%" mkdir "backups\%BACKUP_NAME%"
    
    echo 💾 Criando backup: %BACKUP_NAME%
    echo 📁 Local: backups\%BACKUP_NAME%
    echo.
    
    REM Backup de arquivos de configuração
    echo 📄 Backup de configurações...
    if exist "config.json" (
        copy "config.json" "backups\%BACKUP_NAME%\" >nul
        echo ✅ config.json
    )
    if exist "requirements.txt" (
        copy "requirements.txt" "backups\%BACKUP_NAME%\" >nul
        echo ✅ requirements.txt
    )
    if exist "metadata.json" (
        copy "metadata.json" "backups\%BACKUP_NAME%\" >nul
        echo ✅ metadata.json
    )
    
    REM Backup de dados
    echo 📊 Backup de dados...
    if exist "data" (
        xcopy "data" "backups\%BACKUP_NAME%\data\" /E /I /Y >nul
        echo ✅ Dados da aplicação
    )
    
    REM Backup de logs
    echo 📝 Backup de logs...
    if exist "logs" (
        xcopy "logs" "backups\%BACKUP_NAME%\logs\" /E /I /Y >nul
        echo ✅ Logs do sistema
    )
    
    REM Backup de documentação
    echo 📚 Backup de documentação...
    if exist "docs" (
        xcopy "docs" "backups\%BACKUP_NAME%\docs\" /E /I /Y >nul
        echo ✅ Documentação
    )
    
    REM Backup de aplicações
    echo 🚀 Backup de aplicações...
    if exist "Apps" (
        xcopy "Apps" "backups\%BACKUP_NAME%\Apps\" /E /I /Y >nul
        echo ✅ Aplicações Python
    )
    
    REM Backup de sistema de IA
    echo 🤖 Backup de sistema de IA...
    if exist "bot" (
        xcopy "bot" "backups\%BACKUP_NAME%\bot\" /E /I /Y >nul
        echo ✅ Sistema de IA
    )
    
    REM Criar arquivo de metadados do backup
    echo 📋 Criando metadados do backup...
    (
        echo ========================================
        echo METADADOS DO BACKUP - %date% %time%
        echo ========================================
        echo.
        echo NOME: %BACKUP_NAME%
        echo DATA: %date%
        echo HORA: %time%
        echo.
        echo ARQUIVOS INCLUÍDOS:
        echo - config.json
        echo - requirements.txt
        echo - metadata.json
        echo - data/ (dados da aplicação)
        echo - logs/ (logs do sistema)
        echo - docs/ (documentação)
        echo - Apps/ (aplicações Python)
        echo - bot/ (sistema de IA)
        echo.
        echo CONFIGURAÇÕES:
        echo - Criptografado: %ENCRYPTED_BACKUP%
        echo - Comprimido: %COMPRESSED_BACKUP%
        echo - Automático: %AUTO_BACKUP%
        echo.
        echo SISTEMA:
        echo - OS: %OS%
        echo - Arquitetura: %PROCESSOR_ARCHITECTURE%
        echo - Usuário: %USERNAME%
        echo.
        echo VERSÃO:
        echo - Python App Launcher: 4.0.0
        echo - Backup Manager: 1.0.0
    ) > "backups\%BACKUP_NAME%\backup_info.txt"
    
    REM Compressão se solicitada
    if defined COMPRESSED_BACKUP (
        echo 📦 Comprimindo backup...
        powershell -Command "& {Compress-Archive -Path 'backups\%BACKUP_NAME%' -DestinationPath 'backups\%BACKUP_NAME%.zip' -Force}" >nul 2>&1
        if exist "backups\%BACKUP_NAME%.zip" (
            rmdir /s /q "backups\%BACKUP_NAME%" >nul 2>&1
            echo ✅ Backup comprimido: %BACKUP_NAME%.zip
        )
    )
    
    REM Criptografia se solicitada
    if defined ENCRYPTED_BACKUP (
        echo 🔒 Criptografando backup...
        echo ⚠️  Funcionalidade de criptografia será implementada em versão futura
        echo 💡 Por enquanto, o backup está seguro no diretório local
    )
    
    echo.
    echo ✅ Backup criado com sucesso!
    echo 📁 Local: backups\%BACKUP_NAME%
    if defined COMPRESSED_BACKUP echo 📦 Arquivo: backups\%BACKUP_NAME%.zip
    echo.
)

REM ========================================
REM 3. RESTAURAÇÃO DE BACKUP
REM ========================================

if defined RESTORE_MODE (
    echo 📋 [2/4] Iniciando restauração de backup...
    echo.
    
    REM Listar backups disponíveis
    if exist "backups" (
        echo 📁 Backups disponíveis:
        echo.
        dir /B /AD backups
        echo.
        
        if not defined BACKUP_NAME (
            set /p "BACKUP_CHOICE=Digite o nome do backup para restaurar: "
        ) else (
            set "BACKUP_CHOICE=%BACKUP_NAME%"
        )
        
        REM Verificar se backup existe
        if exist "backups\%BACKUP_CHOICE%" (
            echo 🔄 Restaurando backup: %BACKUP_CHOICE%
            echo.
            
            REM Fazer backup do estado atual antes de restaurar
            echo 💾 Criando backup de segurança do estado atual...
            set "SAFETY_BACKUP=safety_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
            set "SAFETY_BACKUP=%SAFETY_BACKUP: =0%"
            mkdir "backups\%SAFETY_BACKUP%" >nul 2>&1
            
            REM Backup de segurança
            if exist "config.json" copy "config.json" "backups\%SAFETY_BACKUP%\" >nul
            if exist "data" xcopy "data" "backups\%SAFETY_BACKUP%\data\" /E /I /Y >nul
            echo ✅ Backup de segurança criado: %SAFETY_BACKUP%
            echo.
            
            REM Restaurar arquivos
            echo 🔄 Restaurando arquivos...
            
            if exist "backups\%BACKUP_CHOICE%\config.json" (
                copy "backups\%BACKUP_CHOICE%\config.json" "." >nul
                echo ✅ config.json restaurado
            )
            
            if exist "backups\%BACKUP_CHOICE%\requirements.txt" (
                copy "backups\%BACKUP_CHOICE%\requirements.txt" "." >nul
                echo ✅ requirements.txt restaurado
            )
            
            if exist "backups\%BACKUP_CHOICE%\metadata.json" (
                copy "backups\%BACKUP_CHOICE%\metadata.json" "." >nul
                echo ✅ metadata.json restaurado
            )
            
            if exist "backups\%BACKUP_CHOICE%\data" (
                if exist "data" rmdir /s /q "data" >nul 2>&1
                xcopy "backups\%BACKUP_CHOICE%\data" "data\" /E /I /Y >nul
                echo ✅ Dados restaurados
            )
            
            if exist "backups\%BACKUP_CHOICE%\logs" (
                if exist "logs" rmdir /s /q "logs" >nul 2>&1
                xcopy "backups\%BACKUP_CHOICE%\logs" "logs\" /E /I /Y >nul
                echo ✅ Logs restaurados
            )
            
            if exist "backups\%BACKUP_CHOICE%\docs" (
                if exist "docs" rmdir /s /q "docs" >nul 2>&1
                xcopy "backups\%BACKUP_CHOICE%\docs" "docs\" /E /I /Y >nul
                echo ✅ Documentação restaurada
            )
            
            if exist "backups\%BACKUP_CHOICE%\Apps" (
                if exist "Apps" rmdir /s /q "Apps" >nul 2>&1
                xcopy "backups\%BACKUP_CHOICE%\Apps" "Apps\" /E /I /Y >nul
                echo ✅ Aplicações restauradas
            )
            
            if exist "backups\%BACKUP_CHOICE%\bot" (
                if exist "bot" rmdir /s /q "bot" >nul 2>&1
                xcopy "backups\%BACKUP_CHOICE%\bot" "bot\" /E /I /Y >nul
                echo ✅ Sistema de IA restaurado
            )
            
            echo.
            echo ✅ Restauração concluída com sucesso!
            echo 💾 Backup de segurança: %SAFETY_BACKUP%
            echo.
            
        ) else (
            echo ❌ Backup '%BACKUP_CHOICE%' não encontrado!
            echo.
            echo 💡 Backups disponíveis:
            dir /B /AD backups
            echo.
        )
    ) else (
        echo ❌ Nenhum backup encontrado!
        echo.
    )
)

REM ========================================
REM 4. BACKUP AUTOMÁTICO
REM ========================================

if defined AUTO_BACKUP (
    echo 📋 [3/4] Configurando backup automático...
    echo.
    
    REM Criar script de backup automático
    echo 🔧 Criando script de backup automático...
    
    (
        echo @echo off
        echo REM Backup automático do Python App Launcher
        echo REM Executar: backup_manager.bat --backup --auto
        echo.
        echo set "BACKUP_NAME=auto_%%date:~-4,4%%%%date:~-10,2%%%%date:~-7,2%%_%%time:~0,2%%%%time:~3,2%%%%time:~6,2%%"
        echo set "BACKUP_NAME=%%BACKUP_NAME: =0%%"
        echo.
        echo if not exist "backups" mkdir backups
        echo if not exist "backups\%%BACKUP_NAME%%" mkdir "backups\%%BACKUP_NAME%%"
        echo.
        echo echo Backup automático: %%BACKUP_NAME%%
        echo.
        echo if exist "config.json" copy "config.json" "backups\%%BACKUP_NAME%%\" ^>nul
        echo if exist "data" xcopy "data" "backups\%%BACKUP_NAME%%\data\" /E /I /Y ^>nul
        echo if exist "logs" xcopy "logs" "backups\%%BACKUP_NAME%%\logs\" /E /I /Y ^>nul
        echo.
        echo echo Backup automático concluído: %%BACKUP_NAME%%
    ) > "auto_backup.bat"
    
    echo ✅ Script de backup automático criado: auto_backup.bat
    echo.
    echo 💡 Para agendar backup automático:
    echo    1. Abra o Agendador de Tarefas do Windows
    echo    2. Crie uma nova tarefa
    echo    3. Configure para executar auto_backup.bat
    echo    4. Defina frequência (diária, semanal, etc.)
    echo.
)

REM ========================================
REM 5. GERENCIAMENTO DE BACKUPS
REM ========================================

if not defined BACKUP_MODE if not defined RESTORE_MODE if not defined AUTO_BACKUP (
    echo 📋 [4/4] Gerenciamento de backups...
    echo.
    
    if exist "backups" (
        echo 📁 Backups existentes:
        echo.
        for /f "tokens=1,2,3,4" %%a in ('dir /T:C /O:D /B backups 2^>nul') do (
            echo 📄 %%a - %%b %%c %%d
        )
        echo.
        
        REM Estatísticas
        echo 📊 Estatísticas:
        for /f %%a in ('dir /B /AD backups 2^>nul ^| find /c /v ""') do set "BACKUP_COUNT=%%a"
        echo    Total de backups: %BACKUP_COUNT%
        
        REM Calcular tamanho total
        echo 🔍 Calculando tamanho total...
        powershell -Command "& {$size = (Get-ChildItem -Path 'backups' -Recurse -File | Measure-Object -Property Length -Sum).Sum; Write-Host ('Tamanho total: {0:N2} MB' -f ($size/1MB))}" 2>nul
        
        echo.
        echo 💡 Comandos disponíveis:
        echo    backup_manager.bat --backup [nome]     (criar backup)
        echo    backup_manager.bat --restore [nome]    (restaurar backup)
        echo    backup_manager.bat --auto              (configurar backup automático)
        echo    backup_manager.bat --compress          (backup comprimido)
        echo    backup_manager.bat --encrypt           (backup criptografado)
        echo.
    ) else (
        echo 📁 Nenhum backup encontrado.
        echo.
        echo 💡 Para criar seu primeiro backup:
        echo    backup_manager.bat --backup
        echo.
    )
)

REM ========================================
REM 6. FINALIZAÇÃO
REM ========================================

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    💾 SISTEMA DE BACKUP AVANÇADO                             ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 📋 Recursos disponíveis:
echo    💾 Backup completo da aplicação
echo    🔄 Restauração rápida e segura
echo    📦 Compressão automática
echo    🔒 Criptografia (em desenvolvimento)
echo    🤖 Backup automático agendado
echo    📊 Gerenciamento inteligente
echo    💡 Backup de segurança automático
echo.

echo 🎯 Próximos passos:
echo    1. Execute start.bat para usar a aplicação
echo    2. Configure backup automático se necessário
echo    3. Monitore o espaço em disco
echo    4. Faça backups regulares
echo.

pause 