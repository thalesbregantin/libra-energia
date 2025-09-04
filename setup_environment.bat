@echo off
title Libra Energia - Configuração do Ambiente
color 0A

echo.
echo ========================================
echo    LIBRA ENERGIA - CONFIGURAÇÃO DO AMBIENTE
echo ========================================
echo.
echo Iniciando configuração completa...
echo.

REM Verificar se Python está instalado
echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado!
    echo.
    echo Instalando Python via winget...
    winget install Python.Python.3.11
    if errorlevel 1 (
        echo ❌ Falha na instalacao do Python!
        echo Baixe manualmente de: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo ✅ Python instalado com sucesso!
) else (
    echo ✅ Python ja esta instalado!
)

REM Verificar se Node.js está instalado
echo.
echo [2/6] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js nao encontrado!
    echo.
    echo Instalando Node.js via winget...
    winget install OpenJS.NodeJS
    if errorlevel 1 (
        echo ❌ Falha na instalacao do Node.js!
        echo Baixe manualmente de: https://nodejs.org/
        pause
        exit /b 1
    )
    echo ✅ Node.js instalado com sucesso!
) else (
    echo ✅ Node.js ja esta instalado!
)

REM Criar ambiente virtual Python
echo.
echo [3/6] Criando ambiente virtual Python...
if not exist "venv" (
    python -m venv venv
    echo ✅ Ambiente virtual criado!
) else (
    echo ✅ Ambiente virtual ja existe!
)

REM Ativar ambiente virtual e instalar dependências Python
echo.
echo [4/6] Instalando dependencias Python...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erro ao instalar dependencias Python!
    pause
    exit /b 1
)
echo ✅ Dependencias Python instaladas!

REM Instalar dependências Node.js
echo.
echo [5/6] Instalando dependencias Node.js...
cd app
npm install
if errorlevel 1 (
    echo ❌ Erro ao instalar dependencias Node.js!
    cd ..
    pause
    exit /b 1
)
echo ✅ Dependencias Node.js instaladas!
cd ..

REM Verificar arquivo .env
echo.
echo [6/6] Verificando configuracoes...
if not exist ".env" (
    echo ⚠️  Arquivo .env nao encontrado!
    echo Copiando config_example.env para .env...
    copy "docs\config_example.env" ".env"
    echo.
    echo ⚠️  IMPORTANTE: Configure o arquivo .env com suas chaves de API!
    echo.
) else (
    echo ✅ Arquivo .env encontrado!
)

echo.
echo ========================================
echo    CONFIGURACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo ✅ Python + Ambiente Virtual
echo ✅ Node.js + Dependencias
echo ✅ Dependencias Python instaladas
echo ✅ Dependencias Node.js instaladas
echo ✅ Arquivo .env configurado
echo.
echo 🚀 Para usar o sistema:
echo.
echo 1. Ativar ambiente virtual:
echo    venv\Scripts\activate.bat
echo.
echo 2. Executar sistema:
echo    python scripts\start.py
echo.
echo 3. Dashboard React/Next.js:
echo    cd app
echo    npm run dev
echo.
pause
