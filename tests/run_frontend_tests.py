#!/usr/bin/env python3
"""
Script para executar testes TDD do Frontend
"""

import sys
import os
import subprocess
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def run_frontend_tests():
    """Executa todos os testes do frontend"""
    print("🧪 EXECUTANDO TESTES TDD DO FRONTEND")
    print("=" * 50)
    
    try:
        # Executar testes do frontend
        result = subprocess.run([
            sys.executable, "-m", "unittest", 
            "tests.test_frontend", "-v"
        ], capture_output=True, text=True, cwd=root_dir)
        
        print("SAÍDA DOS TESTES:")
        print(result.stdout)
        
        if result.stderr:
            print("ERROS:")
            print(result.stderr)
        
        print("=" * 50)
        print(f"STATUS DE SAÍDA: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ TODOS OS TESTES DO FRONTEND PASSARAM!")
        else:
            print("❌ ALGUNS TESTES DO FRONTEND FALHARAM!")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ ERRO AO EXECUTAR TESTES: {e}")
        return False

def run_specific_test_class(test_class):
    """Executa uma classe específica de testes"""
    print(f"🧪 EXECUTANDO TESTES: {test_class}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "unittest", 
            f"tests.test_frontend.{test_class}", "-v"
        ], capture_output=True, text=True, cwd=root_dir)
        
        print("SAÍDA DOS TESTES:")
        print(result.stdout)
        
        if result.stderr:
            print("ERROS:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ ERRO AO EXECUTAR TESTES: {e}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        # Executar classe específica
        test_class = sys.argv[1]
        success = run_specific_test_class(test_class)
    else:
        # Executar todos os testes
        success = run_frontend_tests()
    
    if success:
        print("\n🎉 TESTES DO FRONTEND CONCLUÍDOS COM SUCESSO!")
        sys.exit(0)
    else:
        print("\n💥 TESTES DO FRONTEND FALHARAM!")
        sys.exit(1)

if __name__ == "__main__":
    main()
