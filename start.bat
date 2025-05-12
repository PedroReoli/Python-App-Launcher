@echo off
REM Verifica se o arquivo main.py existe
if exist main.py (
    echo Executando main.py...
    python main.py
) else (
    echo O arquivo main.py não foi encontrado.
)

REM Pausa para manter o terminal aberto após a execução
pause
