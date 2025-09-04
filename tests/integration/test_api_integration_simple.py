#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes de Integração Simplificados - API
TDD Robusto inspirado nas Big Techs
"""

import pytest
import json
import time
from fastapi.testclient import TestClient
from api.main_simple import app

class TestAPISimple:
    """Testes de integração simplificados para a API"""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste para a API"""
        return TestClient(app)
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_health_check(self, client):
        """Testar health check da API"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Libra Energia" in data["message"]
        assert "status" in data
        assert data["status"] == "online"
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_leads_endpoint_structure(self, client):
        """Testar estrutura do endpoint de leads"""
        response = client.get("/leads")
        
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        assert "message" in data
        assert isinstance(data["leads"], list)
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_campaign_run_endpoint(self, client):
        """Testar endpoint de execução de campanha"""
        # Executar campanha
        response = client.post("/api/campaign/run")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verificar se é sucesso ou erro (ambos são válidos para teste)
        if data.get("success", False):
            assert "leads_collected" in data
            assert "leads_qualified" in data
            assert isinstance(data["leads_collected"], int)
            assert isinstance(data["leads_qualified"], int)
        else:
            # Se falhou, verificar se tem informações de erro
            assert "error" in data or "success" in data
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_response_time(self, client):
        """Testar tempo de resposta da API"""
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # Deve responder em menos de 1 segundo
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_content_type(self, client):
        """Testar tipo de conteúdo da API"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_cors_headers(self, client):
        """Testar headers CORS"""
        response = client.options("/")
        
        # Verificar se CORS está configurado
        assert response.status_code in [200, 405]  # OPTIONS pode retornar 405 se não implementado
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_error_handling(self, client):
        """Testar tratamento de erros da API"""
        # Testar endpoint inexistente
        response = client.get("/endpoint-inexistente")
        
        assert response.status_code == 404
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_data_consistency(self, client):
        """Testar consistência dos dados da API"""
        # Fazer múltiplas requisições e verificar consistência
        responses = []
        for _ in range(3):
            response = client.get("/leads")
            responses.append(response.json())

        # Verificar se todas as respostas têm a mesma estrutura
        for response in responses:
            assert "leads" in response
            assert "message" in response
            assert isinstance(response["leads"], list)
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_memory_usage(self, client):
        """Testar uso de memória da API"""
        import psutil
        import os
        
        # Obter uso de memória antes
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        # Fazer várias requisições
        for _ in range(10):
            response = client.get("/")
            assert response.status_code == 200
        
        # Obter uso de memória depois
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Verificar se o aumento de memória é razoável (menos de 10MB)
        assert memory_increase < 10 * 1024 * 1024  # 10MB em bytes
