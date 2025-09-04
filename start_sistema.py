#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Automático para Iniciar o Sistema Libra Energia
Inicia API, Dashboard e verifica se tudo está funcionando
"""

import subprocess
import time
import requests
import webbrowser
import os
import sys
from pathlib import Path

def print_status(message, status="INFO"):
    """Imprime mensagem com status colorido"""
    colors = {
        "INFO": "\033[94m",      # Azul
        "SUCCESS": "\033[92m",   # Verde
        "WARNING": "\033[93m",   # Amarelo
        "ERROR": "\033[91m",     # Vermelho
        "RESET": "\033[0m"       # Reset
    }
    print(f"{colors.get(status, '')}[{status}] {message}{colors['RESET']}")

def check_port_available(port):
    """Verifica se uma porta está disponível"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        return True
    except:
        return False

def start_api():
    """Inicia a API FastAPI"""
    print_status("Iniciando API FastAPI...", "INFO")
    
    # Verifica se a API já está rodando
    if check_port_available(8000):
        print_status("API já está rodando na porta 8000", "WARNING")
        return True
    
    try:
        # Inicia a API em background
        api_process = subprocess.Popen(
            [sys.executable, "start_api.py"],
            cwd="api",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Aguarda a API inicializar
        print_status("Aguardando API inicializar...", "INFO")
        time.sleep(5)
        
        # Verifica se a API está funcionando
        if check_port_available(8000):
            print_status("✅ API iniciada com sucesso na porta 8000", "SUCCESS")
            return True
        else:
            print_status("❌ Falha ao iniciar API", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ Erro ao iniciar API: {e}", "ERROR")
        return False

def start_dashboard():
    """Inicia o servidor do dashboard"""
    print_status("Iniciando servidor do dashboard...", "INFO")
    
    # Verifica se o dashboard já está rodando
    if check_port_available(8080):
        print_status("Dashboard já está rodando na porta 8080", "WARNING")
        return True
    
    try:
        # Inicia o dashboard em background
        dashboard_process = subprocess.Popen(
            [sys.executable, "serve_dashboard_novo.py"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Aguarda o dashboard inicializar
        print_status("Aguardando dashboard inicializar...", "INFO")
        time.sleep(3)
        
        # Verifica se o dashboard está funcionando
        if check_port_available(8080):
            print_status("✅ Dashboard iniciado com sucesso na porta 8080", "SUCCESS")
            return True
        else:
            print_status("❌ Falha ao iniciar dashboard", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ Erro ao iniciar dashboard: {e}", "ERROR")
        return False

def test_api_endpoints():
    """Testa os endpoints da API"""
    print_status("Testando endpoints da API...", "INFO")
    
    endpoints = [
        ("/", "Página inicial"),
        ("/leads", "Lista de leads"),
        ("/api/leads", "API de leads"),
        ("/api/campaign/run", "Executar campanha")
    ]
    
    all_working = True
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print_status(f"✅ {description}: OK", "SUCCESS")
            else:
                print_status(f"⚠️ {description}: Status {response.status_code}", "WARNING")
                all_working = False
        except Exception as e:
            print_status(f"❌ {description}: Erro - {e}", "ERROR")
            all_working = False
    
    return all_working

def test_dashboard():
    """Testa se o dashboard está carregando corretamente"""
    print_status("Testando dashboard...", "INFO")
    
    try:
        response = requests.get("http://localhost:8080/dashboard_novo.html", timeout=10)
        if response.status_code == 200:
            print_status("✅ Dashboard carregando corretamente", "SUCCESS")
            return True
        else:
            print_status(f"❌ Dashboard com erro: Status {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Erro ao testar dashboard: {e}", "ERROR")
        return False

def open_dashboard():
    """Abre o dashboard no navegador"""
    print_status("Abrindo dashboard no navegador...", "INFO")
    
    try:
        webbrowser.open("http://localhost:8080/dashboard_novo.html")
        print_status("✅ Dashboard aberto no navegador", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Erro ao abrir navegador: {e}", "ERROR")
        return False

def main():
    """Função principal"""
    print_status("🚀 INICIANDO SISTEMA LIBRA ENERGIA", "INFO")
    print_status("=" * 50, "INFO")
    
    # Verifica se estamos no diretório correto
    if not os.path.exists("api") or not os.path.exists("frontend"):
        print_status("❌ Execute este script na raiz do projeto", "ERROR")
        sys.exit(1)
    
    # 1. Inicia a API
    if not start_api():
        print_status("❌ Falha ao iniciar API. Abortando...", "ERROR")
        sys.exit(1)
    
    # 2. Inicia o dashboard
    if not start_dashboard():
        print_status("❌ Falha ao iniciar dashboard. Abortando...", "ERROR")
        sys.exit(1)
    
    # 3. Testa os endpoints da API
    if not test_api_endpoints():
        print_status("⚠️ Alguns endpoints da API não estão funcionando", "WARNING")
    
    # 4. Testa o dashboard
    if not test_dashboard():
        print_status("❌ Dashboard não está funcionando corretamente", "ERROR")
        sys.exit(1)
    
    # 5. Abre o dashboard
    if not open_dashboard():
        print_status("⚠️ Não foi possível abrir o navegador automaticamente", "WARNING")
        print_status("Acesse manualmente: http://localhost:8080/dashboard_novo.html", "INFO")
    
    # 6. Resumo final
    print_status("=" * 50, "INFO")
    print_status("🎯 SISTEMA INICIADO COM SUCESSO!", "SUCCESS")
    print_status("📊 Dashboard: http://localhost:8080/dashboard_novo.html", "INFO")
    print_status("🔌 API: http://localhost:8000", "INFO")
    print_status("=" * 50, "INFO")
    
    # Mantém o script rodando para mostrar logs
    print_status("Pressione Ctrl+C para parar o sistema", "INFO")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_status("\n🛑 Parando sistema...", "INFO")
        print_status("✅ Sistema parado com sucesso", "SUCCESS")

if __name__ == "__main__":
    main()
