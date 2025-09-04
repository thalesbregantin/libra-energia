@echo off
title Libra Energia - Sistema de Prospecção
color 0A

echo.
echo ========================================
echo    LIBRA ENERGIA - SISTEMA DE PROSPECÇÃO
echo ========================================
echo.
echo Iniciando sistema...
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale o Python 3.8+ e tente novamente.
    echo.
    pause
    exit /b 1
)

REM Verificar se o arquivo .env existe
if not exist ".env" (
    echo AVISO: Arquivo .env nao encontrado!
    echo Copiando config_example.env para .env...
    copy "docs\config_example.env" ".env"
    echo.
    echo IMPORTANTE: Configure o arquivo .env com suas chaves de API!
    echo.
    pause
)

REM Executar script de inicialização
echo Executando script de inicialização...
python scripts\start.py

pause
