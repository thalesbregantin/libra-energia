#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simples - Verificar se o TDD está funcionando
"""

import pytest
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestSimple:
    """Testes simples para verificar se o TDD está funcionando"""
    
    @pytest.mark.unit
    def test_basic_math(self):
        """Teste básico de matemática"""
        assert 2 + 2 == 4
        assert 3 * 3 == 9
        assert 10 / 2 == 5
    
    @pytest.mark.unit
    def test_string_operations(self):
        """Teste básico de strings"""
        text = "Libra Energia"
        assert len(text) == 13  # Corrigido: "Libra Energia" tem 13 caracteres
        assert "Energia" in text
        assert text.upper() == "LIBRA ENERGIA"
    
    @pytest.mark.unit
    def test_list_operations(self):
        """Teste básico de listas"""
        items = [1, 2, 3, 4, 5]
        assert len(items) == 5
        assert sum(items) == 15
        assert max(items) == 5
        assert min(items) == 1
    
    @pytest.mark.unit
    def test_dict_operations(self):
        """Teste básico de dicionários"""
        data = {
            "nome": "Supermercado Teste",
            "telefone": "(11) 99999-9999",
            "score": 5.0
        }
        assert "nome" in data
        assert data["score"] == 5.0
        assert len(data) == 3
    
    @pytest.mark.unit
    def test_file_operations(self):
        """Teste básico de operações de arquivo"""
        from pathlib import Path
        
        # Verificar se o diretório do projeto existe
        project_dir = Path(__file__).parent.parent.parent
        assert project_dir.exists()
        assert project_dir.is_dir()
        
        # Verificar se os diretórios principais existem
        assert (project_dir / "src").exists()
        assert (project_dir / "api").exists()
        assert (project_dir / "frontend").exists()
        assert (project_dir / "tests").exists()
    
    @pytest.mark.unit
    def test_import_modules(self):
        """Teste de importação de módulos"""
        import os
        import json
        import datetime
        import sqlite3
        
        # Verificar se os módulos foram importados
        assert os is not None
        assert json is not None
        assert datetime is not None
        assert sqlite3 is not None
    
    @pytest.mark.unit
    def test_environment_variables(self):
        """Teste de variáveis de ambiente"""
        import os
        
        # Verificar se estamos no ambiente virtual
        assert "venv" in os.environ.get("VIRTUAL_ENV", "")
    
    @pytest.mark.unit
    def test_pytest_functionality(self):
        """Teste de funcionalidade do pytest"""
        # Verificar se o pytest está funcionando
        assert pytest is not None
        
        # Verificar se os marcadores estão funcionando
        assert hasattr(pytest.mark, 'unit')
        assert hasattr(pytest.mark, 'integration')
        assert hasattr(pytest.mark, 'e2e')
    
    @pytest.mark.unit
    def test_project_structure(self):
        """Teste da estrutura do projeto"""
        from pathlib import Path
        
        project_dir = Path(__file__).parent.parent.parent
        
        # Verificar arquivos principais
        required_files = [
            "README.md",
            "requirements.txt",
            "pytest.ini",
            "run_tests.py"
        ]
        
        for file in required_files:
            assert (project_dir / file).exists(), f"Arquivo {file} não encontrado"
        
        # Verificar diretórios principais
        required_dirs = [
            "src",
            "api", 
            "frontend",
            "tests",
            "database"
        ]
        
        for dir_name in required_dirs:
            assert (project_dir / dir_name).exists(), f"Diretório {dir_name} não encontrado"
            assert (project_dir / dir_name).is_dir(), f"{dir_name} não é um diretório"
    
    @pytest.mark.unit
    def test_test_structure(self):
        """Teste da estrutura de testes"""
        from pathlib import Path
        
        tests_dir = Path(__file__).parent.parent
        
        # Verificar diretórios de teste
        test_dirs = [
            "unit",
            "integration", 
            "e2e",
            "performance",
            "fixtures"
        ]
        
        for dir_name in test_dirs:
            assert (tests_dir / dir_name).exists(), f"Diretório de teste {dir_name} não encontrado"
            assert (tests_dir / dir_name).is_dir(), f"{dir_name} não é um diretório"
        
        # Verificar arquivos de teste
        assert (tests_dir / "conftest.py").exists(), "conftest.py não encontrado"
        assert (tests_dir / "unit" / "test_simple.py").exists(), "test_simple.py não encontrado"
