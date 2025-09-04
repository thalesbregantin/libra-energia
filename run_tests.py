#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Execução de Testes - Libra Energia
TDD Robusto inspirado nas Big Techs
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def run_command(command, description):
    """Executar comando e mostrar resultado"""
    print(f"\n🚀 {description}")
    print(f"📝 Comando: {command}")
    print("=" * 60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCESSO")
            if result.stdout:
                print("📤 Saída:")
                print(result.stdout)
        else:
            print(f"❌ {description} - ERRO")
            if result.stderr:
                print("📤 Erro:")
                print(result.stderr)
            if result.stdout:
                print("📤 Saída:")
                print(result.stdout)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ {description} - EXCEÇÃO: {e}")
        return False

def install_dependencies():
    """Instalar dependências de teste"""
    print("📦 Instalando dependências de teste...")
    
    commands = [
        ("pip install -r requirements.txt", "Instalando dependências principais"),
        ("pip install pytest-xdist", "Instalando pytest-xdist para paralelização"),
        ("pip install pytest-html", "Instalando pytest-html para relatórios"),
        ("pip install pytest-cov", "Instalando pytest-cov para coverage"),
        ("pip install pytest-selenium", "Instalando pytest-selenium para E2E"),
        ("pip install playwright", "Instalando playwright para testes de frontend"),
        ("playwright install", "Instalando navegadores do playwright")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"⚠️ Falha ao instalar: {description}")
            return False
    
    return True

def run_unit_tests():
    """Executar testes unitários"""
    print("\n🧪 EXECUTANDO TESTES UNITÁRIOS")
    print("=" * 60)
    
    command = "pytest tests/unit/ -v --tb=short --cov=src --cov-report=term-missing"
    return run_command(command, "Testes Unitários")

def run_integration_tests():
    """Executar testes de integração"""
    print("\n🔗 EXECUTANDO TESTES DE INTEGRAÇÃO")
    print("=" * 60)
    
    command = "pytest tests/integration/ -v --tb=short --cov=api --cov-report=term-missing"
    return run_command(command, "Testes de Integração")

def run_e2e_tests():
    """Executar testes end-to-end"""
    print("\n🌐 EXECUTANDO TESTES END-TO-END")
    print("=" * 60)
    
    command = "pytest tests/e2e/ -v --tb=short --html=test-report-e2e.html"
    return run_command(command, "Testes End-to-End")

def run_performance_tests():
    """Executar testes de performance"""
    print("\n⚡ EXECUTANDO TESTES DE PERFORMANCE")
    print("=" * 60)
    
    command = "pytest tests/performance/ -v --tb=short --benchmark-only"
    return run_command(command, "Testes de Performance")

def run_all_tests():
    """Executar todos os testes"""
    print("\n🎯 EXECUTANDO TODOS OS TESTES")
    print("=" * 60)
    
    command = "pytest tests/ -v --tb=short --cov=src --cov=api --cov=database --cov-report=html:htmlcov --cov-report=term-missing --html=test-report.html --self-contained-html"
    return run_command(command, "Todos os Testes")

def run_tests_parallel():
    """Executar testes em paralelo"""
    print("\n🚀 EXECUTANDO TESTES EM PARALELO")
    print("=" * 60)
    
    command = "pytest tests/ -v --tb=short -n auto --cov=src --cov=api --cov=database --cov-report=html:htmlcov --cov-report=term-missing"
    return run_command(command, "Testes em Paralelo")

def run_specific_test(test_path):
    """Executar teste específico"""
    print(f"\n🎯 EXECUTANDO TESTE ESPECÍFICO: {test_path}")
    print("=" * 60)
    
    command = f"pytest {test_path} -v --tb=short"
    return run_command(command, f"Teste Específico: {test_path}")

def run_tests_by_marker(marker):
    """Executar testes por marcador"""
    print(f"\n🏷️ EXECUTANDO TESTES COM MARCADOR: {marker}")
    print("=" * 60)
    
    command = f"pytest tests/ -v --tb=short -m {marker}"
    return run_command(command, f"Testes com Marcador: {marker}")

def generate_coverage_report():
    """Gerar relatório de coverage"""
    print("\n📊 GERANDO RELATÓRIO DE COVERAGE")
    print("=" * 60)
    
    commands = [
        ("coverage run -m pytest tests/", "Executando testes com coverage"),
        ("coverage report", "Gerando relatório de coverage"),
        ("coverage html", "Gerando relatório HTML de coverage"),
        ("coverage xml", "Gerando relatório XML de coverage")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"⚠️ Falha ao gerar coverage: {description}")
            return False
    
    return True

def lint_code():
    """Executar linting do código"""
    print("\n🔍 EXECUTANDO LINTING")
    print("=" * 60)
    
    commands = [
        ("black --check src/ api/ database/ tests/", "Verificando formatação com Black"),
        ("isort --check-only src/ api/ database/ tests/", "Verificando imports com isort"),
        ("flake8 src/ api/ database/ tests/", "Verificando estilo com flake8"),
        ("mypy src/ api/ database/", "Verificando tipos com mypy"),
        ("bandit -r src/ api/ database/", "Verificando segurança com bandit")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"⚠️ Falha no linting: {description}")
            return False
    
    return True

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Script de Testes - Libra Energia")
    parser.add_argument("--install", action="store_true", help="Instalar dependências")
    parser.add_argument("--unit", action="store_true", help="Executar testes unitários")
    parser.add_argument("--integration", action="store_true", help="Executar testes de integração")
    parser.add_argument("--e2e", action="store_true", help="Executar testes end-to-end")
    parser.add_argument("--performance", action="store_true", help="Executar testes de performance")
    parser.add_argument("--all", action="store_true", help="Executar todos os testes")
    parser.add_argument("--parallel", action="store_true", help="Executar testes em paralelo")
    parser.add_argument("--coverage", action="store_true", help="Gerar relatório de coverage")
    parser.add_argument("--lint", action="store_true", help="Executar linting")
    parser.add_argument("--test", type=str, help="Executar teste específico")
    parser.add_argument("--marker", type=str, help="Executar testes por marcador")
    
    args = parser.parse_args()
    
    print("🎯 LIBRA ENERGIA - SCRIPT DE TESTES")
    print("=" * 60)
    print("TDD Robusto inspirado nas Big Techs")
    print("=" * 60)
    
    success = True
    
    if args.install:
        success &= install_dependencies()
    
    if args.lint:
        success &= lint_code()
    
    if args.unit:
        success &= run_unit_tests()
    
    if args.integration:
        success &= run_integration_tests()
    
    if args.e2e:
        success &= run_e2e_tests()
    
    if args.performance:
        success &= run_performance_tests()
    
    if args.all:
        success &= run_all_tests()
    
    if args.parallel:
        success &= run_tests_parallel()
    
    if args.coverage:
        success &= generate_coverage_report()
    
    if args.test:
        success &= run_specific_test(args.test)
    
    if args.marker:
        success &= run_tests_by_marker(args.marker)
    
    # Se nenhum argumento foi fornecido, executar todos os testes
    if not any(vars(args).values()):
        print("🚀 Nenhum argumento fornecido. Executando todos os testes...")
        success &= run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TODOS OS TESTES EXECUTADOS COM SUCESSO!")
        print("📊 Relatórios gerados:")
        print("   - HTML: test-report.html")
        print("   - Coverage: htmlcov/index.html")
        print("   - XML: test-results.xml")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("🔍 Verifique os logs acima para detalhes")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == "__main__":
    main()
