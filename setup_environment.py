#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuração do ambiente - Libra Energia
Configura ambiente virtual Python e instala dependências
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_header():
    """Imprime cabeçalho do sistema"""
    print("=" * 60)
    print("           LIBRA ENERGIA - CONFIGURAÇÃO DO AMBIENTE")
    print("=" * 60)
    print()

def check_python():
    """Verifica se Python está instalado"""
    print("[1/6] Verificando Python...")
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Python já está instalado: {result.stdout.strip()}")
            return True
        else:
            print("Python não encontrado!")
            return False
    except Exception as e:
        print(f"Erro ao verificar Python: {e}")
        return False

def check_nodejs():
    """Verifica se Node.js está instalado"""
    print("\n[2/6] Verificando Node.js...")
    try:
        result = subprocess.run(["node", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Node.js já está instalado: {result.stdout.strip()}")
            return True
        else:
            print("Node.js não encontrado!")
            return False
    except Exception as e:
        print(f"Erro ao verificar Node.js: {e}")
        return False

def create_virtual_env():
    """Cria ambiente virtual Python"""
    print("\n[3/6] Criando ambiente virtual Python...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("Ambiente virtual já existe!")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Ambiente virtual criado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar ambiente virtual: {e}")
        return False

def install_python_deps():
    """Instala dependências Python"""
            print("\n[4/6] Instalando dependências Python...")
    
    # Determinar comando de ativação baseado no sistema operacional
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate.bat"
        pip_path = "venv\\Scripts\\pip"
    else:
        activate_script = "venv/bin/activate"
        pip_path = "venv/bin/pip"
    
    try:
        # Ativar ambiente virtual
        if platform.system() == "Windows":
            # No Windows, usar cmd para executar o batch
            subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
            subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        else:
            # No Linux/Mac, usar source
            subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
            subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        
        print("Dependências Python instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar dependências Python: {e}")
        return False

def install_nodejs_deps():
    """Instala dependências Node.js"""
            print("\n[5/6] Instalando dependências Node.js...")
    
    app_dir = Path("app")
    if not app_dir.exists():
        print("Pasta 'app' não encontrada!")
        return False
    
    try:
        os.chdir(app_dir)
        subprocess.run(["npm", "install"], check=True)
        os.chdir("..")
        print("Dependências Node.js instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar dependências Node.js: {e}")
        os.chdir("..")
        return False

def check_env_file():
    """Verifica arquivo .env"""
            print("\n[6/6] Verificando configurações...")
    
    env_file = Path(".env")
    config_example = Path("docs/config_example.env")
    
    if env_file.exists():
        print("Arquivo .env encontrado!")
        return True
    
    if config_example.exists():
        try:
            shutil.copy(config_example, env_file)
            print("Arquivo .env não encontrado!")
            print("Copiando config_example.env para .env...")
            print("\nIMPORTANTE: Configure o arquivo .env com suas chaves de API!")
            return True
        except Exception as e:
            print(f"Erro ao copiar arquivo .env: {e}")
            return False
    else:
        print("Arquivo config_example.env não encontrado!")
        return False

def print_success():
    """Imprime mensagem de sucesso"""
    print("\n" + "=" * 60)
    print("           CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print()
            print("Python + Ambiente Virtual")
        print("Node.js + Dependências")
        print("Dependências Python instaladas")
        print("Dependências Node.js instaladas")
        print("Arquivo .env configurado")
    print()
            print("Para usar o sistema:")
    print()
    
    if platform.system() == "Windows":
        print("1. Ativar ambiente virtual:")
        print("   venv\\Scripts\\activate.bat")
    else:
        print("1. Ativar ambiente virtual:")
        print("   source venv/bin/activate")
    
    print()
    print("2. Executar sistema:")
    print("   python scripts/start.py")
    print()
    print("3. Dashboard React/Next.js:")
    print("   cd app")
    print("   npm run dev")
    print()

def main():
    """Função principal"""
    print_header()
    
    # Verificar Python
    if not check_python():
        print("\nPython é obrigatório! Instale-o primeiro.")
        print("Download: https://www.python.org/downloads/")
        return False
    
    # Verificar Node.js
    if not check_nodejs():
        print("\nNode.js é obrigatório! Instale-o primeiro.")
        print("Download: https://nodejs.org/")
        return False
    
    # Criar ambiente virtual
    if not create_virtual_env():
        return False
    
    # Instalar dependências Python
    if not install_python_deps():
        return False
    
    # Instalar dependências Node.js
    if not install_nodejs_deps():
        return False
    
    # Verificar arquivo .env
    if not check_env_file():
        return False
    
    # Sucesso
    print_success()
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\nConfiguração falhou! Verifique os erros acima.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Configuração cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        sys.exit(1)
