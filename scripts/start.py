#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicialização do Sistema de Prospecção - Libra Energia
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Imprime o cabeçalho do sistema"""
    print("=" * 50)
    print("    Libra Energia - Sistema de Prospecção")
    print("=" * 50)
    print()

def print_menu():
    """Imprime o menu de opções"""
    print("[1] Testar sistema")
    print("[2] Executar campanha completa")
    print("[3] Executar teste limitado")
    print("[4] Abrir dashboard HTML")
    print("[5] Executar testes TDD")
    print("[6] Iniciar API REST")
    print("[7] Servir Dashboard HTTP")
    print("[8] Servir NOVO Dashboard HTTP")
    print("[9] Testar Conectividade API")
    print("[10] Inicializar Banco de Dados")
    print("[11] Iniciar API com Banco de Dados")
    print("[12] Ver logs")
    print("[13] Ver estrutura do projeto")
    print("[0] Sair")
    print()

def test_system():
    """Testa o sistema básico"""
    print("\n🧪 Testando sistema...")
    try:
        os.chdir("src")
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Erros:", result.stderr)
        os.chdir("..")
    except Exception as e:
        print(f"Erro ao testar sistema: {e}")
    input("\nPressione Enter para continuar...")

def run_campaign():
    """Executa campanha completa"""
    print("\nExecutando campanha completa...")
    print("Usando configurações padrão: supermercado, padaria em São Paulo")
    try:
        os.chdir("src")
        subprocess.run([sys.executable, "main.py", "--keywords", "supermercado", "padaria", "--cidades", "São Paulo, SP", "--max-leads", "20"])
        os.chdir("..")
    except Exception as e:
        print(f"Erro ao executar campanha: {e}")
    input("\nPressione Enter para continuar...")

def run_test():
    """Executa teste limitado"""
    print("\nExecutando teste limitado...")
    try:
        os.chdir("src")
        subprocess.run([sys.executable, "main.py", "--teste"])
        os.chdir("..")
    except Exception as e:
        print(f"Erro ao executar teste: {e}")
    input("\nPressione Enter para continuar...")

def open_html_dashboard():
    """Abre o dashboard HTML"""
    print("\nAbrindo dashboard HTML...")
    try:
        # Tenta primeiro o dashboard da pasta raiz
        dashboard_path = Path("dashboard.html")
        if dashboard_path.exists():
            webbrowser.open(f"file://{dashboard_path.absolute()}")
            print("Dashboard HTML aberto no navegador!")
        else:
            # Fallback para o dashboard da pasta src
            dashboard_path = Path("src/dashboard_simples.html")
            if dashboard_path.exists():
                webbrowser.open(f"file://{dashboard_path.absolute()}")
                print("Dashboard HTML aberto no navegador!")
            else:
                print("Nenhum arquivo dashboard encontrado!")
    except Exception as e:
        print(f"Erro ao abrir dashboard: {e}")
    input("\nPressione Enter para continuar...")



def show_logs():
    """Mostra a pasta de logs"""
    print("\nAbrindo pasta de logs...")
    try:
        logs_path = Path("logs")
        if logs_path.exists():
            if os.name == 'nt':  # Windows
                os.startfile(logs_path)
            else:  # Linux/Mac
                subprocess.run(["xdg-open", str(logs_path)])
            print("Pasta de logs aberta!")
        else:
            print("Pasta de logs não encontrada!")
    except Exception as e:
        print(f"Erro ao abrir logs: {e}")
    input("\nPressione Enter para continuar...")

def run_tdd_tests():
    """Executa todos os testes TDD"""
    print("\nExecutando testes TDD...")
    try:
        os.chdir("tests")
        subprocess.run([sys.executable, "run_all_tests.py"])
        os.chdir("..")
    except Exception as e:
        print(f"Erro ao executar testes TDD: {e}")
    input("\nPressione Enter para continuar...")

def start_api():
    """Inicia a API REST"""
    print("\nIniciando API REST...")
    try:
        # Verificar se a pasta api existe
        if not Path("api").exists():
            print("Pasta 'api' não encontrada!")
            print("Execute primeiro: python api/start_api.py")
            input("\nPressione Enter para continuar...")
            return
        
        os.chdir("api")
        print("API iniciada em: http://localhost:8000")
        print("Documentação: http://localhost:8000/docs")
        print("Health Check: http://localhost:8000/api/health")
        print("\nPressione Ctrl+C para parar a API...")
        
        # Iniciar a API
        subprocess.run([sys.executable, "start_api.py"])
        os.chdir("..")
        
    except KeyboardInterrupt:
        print("\nAPI parada pelo usuário")
        os.chdir("..")
    except Exception as e:
        print(f"Erro ao iniciar API: {e}")
        os.chdir("..")
    input("\nPressione Enter para continuar...")

def serve_dashboard():
    """Serve o dashboard via HTTP"""
    print("\nIniciando servidor do Dashboard...")
    try:
        # Verificar se a pasta api existe
        if not Path("api").exists():
            print("Pasta 'api' não encontrada!")
            input("\nPressione Enter para continuar...")
            return
        
        os.chdir("api")
        print("Dashboard será servido em: http://localhost:8080")
        print("Acesse: http://localhost:8080/dashboard.html")
        print("\nPressione Ctrl+C para parar o servidor...")
        
        # Iniciar o servidor do dashboard
        subprocess.run([sys.executable, "serve_dashboard.py"])
        os.chdir("..")
        
    except KeyboardInterrupt:
        print("\nServidor parado pelo usuário")
        os.chdir("..")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        os.chdir("..")
    input("\nPressione Enter para continuar...")

def serve_dashboard_novo():
    """Serve o NOVO dashboard via HTTP"""
    print("\n🚀 Iniciando servidor do NOVO Dashboard...")
    try:
        print("Dashboard será servido em: http://localhost:8080")
        print("Acesse: http://localhost:8080/dashboard_novo.html")
        print("\nPressione Ctrl+C para parar o servidor...")
        
        # Iniciar o servidor do novo dashboard
        subprocess.run([sys.executable, "serve_dashboard_novo.py"])
        
    except KeyboardInterrupt:
        print("\nServidor parado pelo usuário")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
    input("\nPressione Enter para continuar...")

def test_api_connectivity():
    """Testa a conectividade com a API"""
    print("\n🔍 Testando conectividade com a API...")
    try:
        import webbrowser
        webbrowser.open('test_api_connection.html')
        print("✅ Página de teste aberta no navegador")
        print("📋 Verifique os resultados dos testes de conectividade")
    except Exception as e:
        print(f"❌ Erro ao abrir página de teste: {e}")
    input("\nPressione Enter para continuar...")

def init_database():
    """Inicializa o banco de dados SQLite"""
    print("\n🗄️ Inicializando banco de dados...")
    try:
        subprocess.run([sys.executable, "init_database.py"])
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
    input("\nPressione Enter para continuar...")

def start_api_with_db():
    """Inicia a API com banco de dados"""
    print("\n🚀 Iniciando API com banco de dados...")
    try:
        # Verificar se a pasta api existe
        if not Path("api").exists():
            print("Pasta 'api' não encontrada!")
            input("\nPressione Enter para continuar...")
            return
        
        os.chdir("api")
        print("API será servida em: http://localhost:8000")
        print("Documentação: http://localhost:8000/docs")
        print("\nPressione Ctrl+C para parar o servidor...")
        
        # Iniciar a API com banco de dados
        subprocess.run([sys.executable, "main_with_db.py"])
        os.chdir("..")
        
    except KeyboardInterrupt:
        print("\nServidor parado pelo usuário")
        os.chdir("..")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        os.chdir("..")
    input("\nPressione Enter para continuar...")

def show_project_structure():
    """Mostra a estrutura do projeto"""
    print("\nEstrutura do Projeto:")
    print("=" * 40)
    
    def print_tree(path, prefix="", is_last=True):
        """Imprime a árvore de diretórios"""
        items = list(path.iterdir())
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))
        
        for i, item in enumerate(items):
            if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules']:
                continue
                
            is_last_item = i == len(items) - 1
            current_prefix = "└── " if is_last_item else "├── "
            
            if item.is_dir():
                print(f"{prefix}{current_prefix}{item.name}/")
                new_prefix = prefix + ("    " if is_last_item else "│   ")
                print_tree(item, new_prefix, is_last_item)
            else:
                icon = "[Arq]" if item.suffix in ['.py', '.txt', '.md'] else "[Dir]"
                print(f"{prefix}{current_prefix}{icon} {item.name}")
    
    project_path = Path(".")
    print_tree(project_path)
    
    input("\nPressione Enter para continuar...")

def main():
    """Função principal"""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        try:
            choice = input("Escolha uma opção (1-9, 0 para sair): ").strip()
            
            if choice == "1":
                test_system()
            elif choice == "2":
                run_campaign()
            elif choice == "3":
                run_test()
            elif choice == "4":
                open_html_dashboard()
            elif choice == "5":
                run_tdd_tests()
            elif choice == "6":
                start_api()
            elif choice == "7":
                serve_dashboard()
            elif choice == "8":
                serve_dashboard_novo()
            elif choice == "9":
                test_api_connectivity()
            elif choice == "10":
                init_database()
            elif choice == "11":
                start_api_with_db()
            elif choice == "12":
                show_logs()
            elif choice == "13":
                show_project_structure()
            elif choice == "0":
                print("\nSaindo do sistema...")
                break
            else:
                print("\nOpção inválida!")
                input("Pressione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\nSaindo do sistema...")
            break
        except Exception as e:
            print(f"\nErro inesperado: {e}")
            input("Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
