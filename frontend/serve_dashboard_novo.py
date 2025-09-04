#!/usr/bin/env python3
"""
Servidor HTTP para servir o novo dashboard
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

def serve_dashboard():
    """Inicia o servidor HTTP para o dashboard"""
    
    # Configurações
    PORT = 8080
    HOST = 'localhost'
    
    # Mudar para o diretório do projeto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Configurar o servidor
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Adicionar headers CORS
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def do_OPTIONS(self):
            # Responder a requisições OPTIONS (CORS preflight)
            self.send_response(200)
            self.end_headers()
    
    try:
        with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
            print(f"🚀 Servidor do Dashboard rodando em http://{HOST}:{PORT}")
            print(f"📁 Diretório: {project_dir}")
            print(f"🌐 Dashboard: http://{HOST}:{PORT}/dashboard_novo.html")
            print("⏹️  Pressione Ctrl+C para parar")
            
            # Abrir o dashboard no navegador
            webbrowser.open(f'http://{HOST}:{PORT}/dashboard_novo.html')
            
            # Iniciar o servidor
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n⏹️  Servidor parado pelo usuário")
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print(f"❌ Porta {PORT} já está em uso. Tente parar outros servidores.")
        else:
            print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    serve_dashboard()
