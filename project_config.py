#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração centralizada do projeto Libra Energia
"""

import os
from pathlib import Path

class ProjectConfig:
    """Configurações centralizadas do projeto"""
    
    # Diretórios do projeto
    PROJECT_ROOT = Path(__file__).parent
    SRC_DIR = PROJECT_ROOT / "src"
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    DOCS_DIR = PROJECT_ROOT / "docs"
    SCRIPTS_DIR = PROJECT_ROOT / "scripts"
    APP_DIR = PROJECT_ROOT / "app"
    
    # Arquivos importantes
    ENV_FILE = PROJECT_ROOT / ".env"
    REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
    README_FILE = PROJECT_ROOT / "README.md"
    
    # Configurações de dados
    DATA_FORMATS = ['.json', '.csv', '.xlsx']
    LOG_FORMATS = ['.log', '.txt']
    
    # Configurações de backup
    BACKUP_DIR = DATA_DIR / "backups"
    BACKUP_FORMAT = "backup_%Y%m%d_%H%M%S"
    
    @classmethod
    def ensure_directories(cls):
        """Garante que todos os diretórios necessários existam"""
        directories = [
            cls.SRC_DIR,
            cls.DATA_DIR,
            cls.LOGS_DIR,
            cls.DOCS_DIR,
            cls.SCRIPTS_DIR,
            cls.APP_DIR,
            cls.BACKUP_DIR
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
                           print(f"Diretório verificado: {directory}")
    
    @classmethod
    def get_project_structure(cls):
        """Retorna a estrutura atual do projeto"""
        structure = {
            "src": list(cls.SRC_DIR.glob("*.py")) + list(cls.SRC_DIR.glob("*.html")),
            "data": list(cls.DATA_DIR.glob("*")),
            "logs": list(cls.LOGS_DIR.glob("*.log")),
            "docs": list(cls.DOCS_DIR.glob("*")),
            "scripts": list(cls.SCRIPTS_DIR.glob("*")),
            "app": list(cls.APP_DIR.glob("*"))
        }
        return structure
    
    @classmethod
    def print_project_info(cls):
        """Imprime informações sobre o projeto"""
        print("\n" + "="*60)
        print("           LIBRA ENERGIA - INFORMAÇÕES DO PROJETO")
        print("="*60)
        
        print(f"\nDiretório raiz: {cls.PROJECT_ROOT}")
        print(f"🐍 Python: {cls.SRC_DIR}")
        print(f"Dados: {cls.DATA_DIR}")
        print(f"Logs: {cls.LOGS_DIR}")
        print(f"Documentação: {cls.DOCS_DIR}")
        print(f"Scripts: {cls.SCRIPTS_DIR}")
        print(f"Frontend: {cls.APP_DIR}")
        
        # Verificar arquivos importantes
        print(f"\nArquivos importantes:")
                       print(f"   .env: {'OK' if cls.ENV_FILE.exists() else 'FALTANDO'}")
               print(f"   requirements.txt: {'OK' if cls.REQUIREMENTS_FILE.exists() else 'FALTANDO'}")
               print(f"   README.md: {'OK' if cls.README_FILE.exists() else 'FALTANDO'}")
        
        # Contar arquivos por tipo
        structure = cls.get_project_structure()
        print(f"\nEstatísticas:")
        for category, files in structure.items():
            print(f"   {category}: {len(files)} arquivos")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    # Testar a configuração
    ProjectConfig.ensure_directories()
    ProjectConfig.print_project_info()
