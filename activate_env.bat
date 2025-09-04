@echo off
title Libra Energia - Ativar Ambiente Virtual
color 0B

echo.
echo ========================================
echo    LIBRA ENERGIA - ATIVAR AMBIENTE
echo ========================================
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv" (
    echo ❌ Ambiente virtual nao encontrado!
    echo.
    echo Execute primeiro: setup_environment.bat
    echo.
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo 🚀 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verificar se foi ativado
if "%VIRTUAL_ENV%"=="" (
    echo ❌ Falha ao ativar ambiente virtual!
    pause
    exit /b 1
)

echo ✅ Ambiente virtual ativado!
echo.
echo 🐍 Python: %VIRTUAL_ENV%
echo 📦 Pip: %VIRTUAL_ENV%\Scripts\pip
echo.
echo 🚀 Comandos disponiveis:
echo.
echo • Executar sistema: python scripts/start.py
echo • Dashboard HTML: start src\dashboard_simples.html
echo • Dashboard React: cd app && npm run dev
echo • Instalar pacotes: pip install nome_do_pacote
echo • Desativar: deactivate
echo.
echo 💡 Para desativar o ambiente, digite: deactivate
echo.

REM Manter terminal aberto
cmd /k
