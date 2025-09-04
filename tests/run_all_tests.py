#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar todos os testes do sistema
Libra Energia - TDD Framework
"""
import unittest
import sys
from pathlib import Path

def run_all_tests():
    """Executa todos os testes do sistema"""
    print("🧪 INICIANDO TESTES TDD - LIBRA ENERGIA")
    print("=" * 60)
    
    # Adicionar pasta src ao path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Descobrir todos os testes
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        start_dir=str(Path(__file__).parent),
        pattern='test_*.py'
    )
    
    # Executar testes
    test_runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout
    )
    
    print(f"Diretório de testes: {Path(__file__).parent}")
    print(f"Diretório fonte: {src_path}")
    print(f"🔍 Padrão de busca: test_*.py")
    print()
    
    # Executar suite de testes
    result = test_runner.run(test_suite)
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Testes executados: {result.testsRun}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    
    if result.failures:
        print("\nFALHAS:")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n🚨 ERROS:")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback.split('Exception:')[-1].strip()}")
    
    if result.wasSuccessful():
        print("\nTODOS OS TESTES PASSARAM!")
        return True
    else:
        print(f"\n{len(result.failures) + len(result.errors)} TESTES FALHARAM!")
        return False

def run_specific_test(test_name):
    """Executa um teste específico"""
    print(f"🧪 EXECUTANDO TESTE ESPECÍFICO: {test_name}")
    print("=" * 60)
    
    # Adicionar pasta src ao path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Executar teste específico
    test_loader = unittest.TestLoader()
    test_suite = test_loader.loadTestsFromName(test_name)
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return result.wasSuccessful()

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        # Executar teste específico
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
        sys.exit(0 if success else 1)
    else:
        # Executar todos os testes
        success = run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
