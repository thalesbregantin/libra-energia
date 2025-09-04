@echo off
echo ========================================
echo    Libra Energia - Sistema de Prospecção
echo ========================================
echo.

echo [1] Testar sistema
echo [2] Executar campanha completa
echo [3] Executar teste limitado
       echo [4] Abrir dashboard HTML
       echo [5] Abrir dashboard React/Next.js
       echo [6] Ver logs
       echo [7] Sair
echo.

set /p choice="Escolha uma opção (1-7): "

if "%choice%"=="1" (
    echo.
    echo Testando sistema...
    cd src
    python test_system.py
    pause
    goto :eof
)

if "%choice%"=="2" (
    echo.
    echo Executando campanha completa...
    cd src
    python main.py --campanha
    pause
    goto :eof
)

if "%choice%"=="3" (
    echo.
    echo Executando teste limitado...
    cd src
    python main.py --teste
    pause
    goto :eof
)

if "%choice%"=="4" (
    echo.
    echo Abrindo dashboard HTML...
    start src\dashboard_simples.html
    goto :eof
)

       if "%choice%"=="5" (
           echo.
           echo Abrindo dashboard React/Next.js...
           cd app
           npm run dev
           goto :eof
       )

if "%choice%"=="6" (
    echo.
    echo Abrindo pasta de logs...
    explorer logs
    goto :eof
)

if "%choice%"=="7" (
    echo.
    echo Saindo...
    exit
)

echo Opção inválida!
pause
