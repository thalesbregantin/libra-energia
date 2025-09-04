# Script PowerShell para Libra Energia
# Resolve problemas de compatibilidade com PowerShell

Write-Host "========================================" -ForegroundColor Green
Write-Host "    LIBRA ENERGIA - SISTEMA DE PROSPECÇÃO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Verificar se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale o Python 3.8+ e tente novamente." -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar se o arquivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "AVISO: Arquivo .env não encontrado!" -ForegroundColor Yellow
    if (Test-Path "docs\config_example.env") {
        Write-Host "Copiando config_example.env para .env..." -ForegroundColor Yellow
        Copy-Item "docs\config_example.env" ".env"
        Write-Host "IMPORTANTE: Configure o arquivo .env com suas chaves de API!" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Executar script de inicialização
Write-Host "Executando script de inicialização..." -ForegroundColor Green
python scripts\start.py

Read-Host "Pressione Enter para sair"
