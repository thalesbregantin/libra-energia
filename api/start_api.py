#!/usr/bin/env python3
"""
Script para iniciar a API da Libra Energia
"""

import uvicorn
import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent.parent / "src"))

if __name__ == "__main__":
    print("🚀 Iniciando API da Libra Energia...")
    print("📍 Endereço: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/health")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "main_simple:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Auto-reload em desenvolvimento
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 API parada pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")
        sys.exit(1)
