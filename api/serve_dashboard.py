#!/usr/bin/env python3
"""
Servidor HTTP simples para servir o dashboard
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from pathlib import Path

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Mudar para a pasta raiz do projeto
        root_path = Path(__file__).parent.parent
        os.chdir(root_path)
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # Adicionar headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    PORT = 8080
    print(f"🚀 Servidor do Dashboard iniciado!")
    print(f"📍 Endereço: http://localhost:{PORT}")
    print(f"📱 Dashboard: http://localhost:{PORT}/dashboard.html")
    print(f"🔍 API: http://localhost:8000")
    print("=" * 50)
    
    try:
        server = HTTPServer(('localhost', PORT), DashboardHandler)
        print(f"✅ Servidor rodando em http://localhost:{PORT}")
        print("🛑 Pressione Ctrl+C para parar")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
