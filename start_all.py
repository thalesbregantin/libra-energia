#!/usr/bin/env python3
"""
Script para iniciar todos os serviços
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def start_api():
    """Inicia a API"""
    print("🚀 Iniciando API...")
    try:
        api_process = subprocess.Popen([
            sys.executable, "-c", 
            "import uvicorn; uvicorn.run('api.main_simple:app', host='0.0.0.0', port=8000)"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar um pouco
        time.sleep(3)
        
        if api_process.poll() is None:
            print("✅ API iniciada em http://localhost:8000")
            return api_process
        else:
            print("❌ Erro ao iniciar API")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")
        return None

def start_dashboard():
    """Inicia o servidor do dashboard"""
    print("📱 Iniciando servidor do dashboard...")
    try:
        dashboard_process = subprocess.Popen([
            sys.executable, "-c",
            "from http.server import HTTPServer, SimpleHTTPRequestHandler; import os; os.chdir('.'); server = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler); print('Dashboard rodando em http://localhost:8080'); server.serve_forever()"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar um pouco
        time.sleep(2)
        
        if dashboard_process.poll() is None:
            print("✅ Dashboard iniciado em http://localhost:8080")
            return dashboard_process
        else:
            print("❌ Erro ao iniciar dashboard")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")
        return None

def main():
    """Função principal"""
    print("🎯 Iniciando todos os serviços da Libra Energia...")
    print("=" * 50)
    
    # Iniciar API
    api_process = start_api()
    
    # Iniciar Dashboard
    dashboard_process = start_dashboard()
    
    if api_process and dashboard_process:
        print("\n🎉 Todos os serviços iniciados com sucesso!")
        print("📍 API: http://localhost:8000")
        print("📱 Dashboard: http://localhost:8080/dashboard.html")
        print("🔍 Health Check: http://localhost:8000/api/health")
        print("\n🛑 Pressione Ctrl+C para parar todos os serviços...")
        
        # Abrir dashboard no navegador
        try:
            webbrowser.open("http://localhost:8080/dashboard.html")
        except:
            pass
        
        try:
            # Manter rodando
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Parando serviços...")
            api_process.terminate()
            dashboard_process.terminate()
            print("✅ Serviços parados!")
    else:
        print("❌ Erro ao iniciar serviços!")
        sys.exit(1)

if __name__ == "__main__":
    main()
