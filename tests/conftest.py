#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração Global de Testes - Libra Energia
TDD Robusto inspirado nas Big Techs (Apple, Google, Meta)
"""

import pytest
import asyncio
import tempfile
import shutil
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Generator, Dict, Any
import json
import sqlite3
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ============================================================================
# FIXTURES DE CONFIGURAÇÃO
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Criar event loop para testes assíncronos"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_config():
    """Configuração de teste"""
    return {
        "TESTING": True,
        "DATABASE_URL": "sqlite:///test.db",
        "API_BASE_URL": "http://localhost:8000",
        "GOOGLE_PLACES_API_KEY": "test_key",
        "GOOGLE_SHEETS_CREDENTIALS": "test_credentials.json",
        "LOG_LEVEL": "DEBUG"
    }

# ============================================================================
# FIXTURES DE BANCO DE DADOS
# ============================================================================

@pytest.fixture(scope="function")
def temp_db():
    """Banco de dados temporário para testes"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    # Criar banco de teste
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabelas de teste
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            website TEXT,
            endereco TEXT,
            score REAL DEFAULT 0.0,
            nivel TEXT DEFAULT 'C',
            qualificado BOOLEAN DEFAULT FALSE,
            fonte TEXT DEFAULT 'Google Places',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            leads_coletados INTEGER DEFAULT 0,
            leads_qualificados INTEGER DEFAULT 0,
            score_medio REAL DEFAULT 0.0,
            status TEXT DEFAULT 'ativo'
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def clean_database(temp_db):
    """Limpar banco de dados antes de cada teste"""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads")
    cursor.execute("DELETE FROM campaigns")
    conn.commit()
    conn.close()
    yield temp_db

# ============================================================================
# FIXTURES DE DADOS DE TESTE
# ============================================================================

@pytest.fixture
def sample_leads():
    """Dados de exemplo de leads"""
    return [
        {
            "nome": "Supermercado Teste Ltda",
            "telefone": "(11) 99999-9999",
            "website": "https://teste.com",
            "endereco": "Rua Teste, 123 - São Paulo, SP",
            "score": 5.5,
            "nivel": "A",
            "qualificado": True,
            "fonte": "Google Places"
        },
        {
            "nome": "Padaria do João",
            "telefone": "(11) 88888-8888",
            "website": "https://padariadojoao.com",
            "endereco": "Av. Principal, 456 - São Paulo, SP",
            "score": 4.2,
            "nivel": "B",
            "qualificado": True,
            "fonte": "Instagram"
        },
        {
            "nome": "Academia Fitness",
            "telefone": "(11) 77777-7777",
            "website": "https://academiafitness.com",
            "endereco": "Rua da Saúde, 789 - São Paulo, SP",
            "score": 3.8,
            "nivel": "C",
            "qualificado": False,
            "fonte": "Google Places"
        }
    ]

@pytest.fixture
def sample_campaign():
    """Dados de exemplo de campanha"""
    return {
        "nome": "Campanha Teste",
        "data_execucao": datetime.now(),
        "leads_coletados": 20,
        "leads_qualificados": 15,
        "score_medio": 4.5,
        "status": "ativo"
    }

# ============================================================================
# FIXTURES DE MOCKING
# ============================================================================

@pytest.fixture
def mock_google_places_api():
    """Mock da API do Google Places"""
    with patch('src.lead_collector.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "name": "Supermercado Teste",
                    "formatted_address": "Rua Teste, 123 - São Paulo, SP",
                    "formatted_phone_number": "(11) 99999-9999",
                    "website": "https://teste.com",
                    "rating": 4.5,
                    "place_id": "test_place_id"
                }
            ],
            "status": "OK"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_instagram_scraper():
    """Mock do scraper do Instagram"""
    with patch('src.lead_collector.InstagramScraper') as mock_scraper:
        mock_instance = Mock()
        mock_instance.scrape_business_profile.return_value = {
            "username": "test_business",
            "followers": 1000,
            "posts": 50,
            "bio": "Supermercado de qualidade"
        }
        mock_scraper.return_value = mock_instance
        yield mock_scraper

@pytest.fixture
def mock_receita_ws_api():
    """Mock da API da ReceitaWS"""
    with patch('src.lead_qualifier.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "OK",
            "cnpj": "12345678000199",
            "nome": "Supermercado Teste Ltda",
            "fantasia": "Supermercado Teste",
            "situacao": "ATIVA",
            "cnae": "4711301"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_external_apis(mock_google_places_api, mock_instagram_scraper, mock_receita_ws_api):
    """Mock de todas as APIs externas"""
    return {
        "google_places": mock_google_places_api,
        "instagram": mock_instagram_scraper,
        "receita_ws": mock_receita_ws_api
    }

# ============================================================================
# FIXTURES DE API
# ============================================================================

@pytest.fixture
def api_client():
    """Cliente de teste para a API"""
    from fastapi.testclient import TestClient
    from api.main_simple import app
    return TestClient(app)

@pytest.fixture
def authenticated_api_client(api_client):
    """Cliente de API autenticado"""
    # Adicionar token de autenticação se necessário
    api_client.headers.update({"Authorization": "Bearer test_token"})
    return api_client

# ============================================================================
# FIXTURES DE FRONTEND
# ============================================================================

@pytest.fixture
def browser():
    """Navegador para testes E2E"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture
def dashboard_url():
    """URL do dashboard para testes"""
    return "http://localhost:8080/dashboard_novo.html"

# ============================================================================
# FIXTURES DE PERFORMANCE
# ============================================================================

@pytest.fixture
def performance_metrics():
    """Métricas de performance para testes"""
    return {
        "max_response_time": 2.0,  # segundos
        "max_memory_usage": 100,   # MB
        "max_cpu_usage": 80,       # %
        "max_concurrent_users": 100
    }

# ============================================================================
# FIXTURES DE SEGURANÇA
# ============================================================================

@pytest.fixture
def security_headers():
    """Headers de segurança para testes"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }

# ============================================================================
# FIXTURES DE LOGGING
# ============================================================================

@pytest.fixture
def test_logger():
    """Logger para testes"""
    import logging
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    return logger

# ============================================================================
# FIXTURES DE TEMPO
# ============================================================================

@pytest.fixture
def freeze_time():
    """Congelar tempo para testes determinísticos"""
    from freezegun import freeze_time
    with freeze_time("2025-09-04 15:00:00"):
        yield

# ============================================================================
# FIXTURES DE AMBIENTE
# ============================================================================

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, test_config):
    """Configurar ambiente de teste"""
    for key, value in test_config.items():
        monkeypatch.setenv(key, str(value))
    
    # Limpar cache de imports
    import importlib
    modules_to_reload = [
        'src.lead_collector',
        'src.lead_qualifier',
        'api.main_simple',
        'database.database'
    ]
    
    for module in modules_to_reload:
        if module in sys.modules:
            importlib.reload(sys.modules[module])

# ============================================================================
# FIXTURES DE CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Limpar arquivos de teste após cada teste"""
    yield
    
    # Limpar arquivos temporários
    temp_files = [
        "test.db",
        "test_leads.json",
        "test_campaign.json",
        "test_log.txt"
    ]
    
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)

# ============================================================================
# MARCADORES PERSONALIZADOS
# ============================================================================

def pytest_configure(config):
    """Configurar marcadores personalizados"""
    config.addinivalue_line("markers", "unit: Testes unitários")
    config.addinivalue_line("markers", "integration: Testes de integração")
    config.addinivalue_line("markers", "e2e: Testes end-to-end")
    config.addinivalue_line("markers", "performance: Testes de performance")
    config.addinivalue_line("markers", "slow: Testes lentos")
    config.addinivalue_line("markers", "api: Testes de API")
    config.addinivalue_line("markers", "database: Testes de banco de dados")
    config.addinivalue_line("markers", "frontend: Testes de frontend")
    config.addinivalue_line("markers", "security: Testes de segurança")
    config.addinivalue_line("markers", "regression: Testes de regressão")

# ============================================================================
# HOOKS DE TESTE
# ============================================================================

def pytest_runtest_setup(item):
    """Setup antes de cada teste"""
    print(f"\n🧪 Executando: {item.name}")

def pytest_runtest_teardown(item):
    """Teardown após cada teste"""
    print(f"✅ Concluído: {item.name}")

def pytest_collection_modifyitems(config, items):
    """Modificar itens de teste durante a coleta"""
    for item in items:
        # Adicionar marcador 'slow' para testes que demoram mais de 5 segundos
        if "slow" in item.name or "performance" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Adicionar marcador 'integration' para testes que usam banco de dados
        if "database" in item.name or "api" in item.name:
            item.add_marker(pytest.mark.integration)
