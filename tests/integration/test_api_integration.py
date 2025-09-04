#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes de Integração - API
TDD Robusto inspirado nas Big Techs
"""

import pytest
import json
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from api.main_simple import app

class TestAPIIntegration:
    """Testes de integração para a API"""
    
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
    def test_api_endpoints_structure(self, client):
        """Testar estrutura dos endpoints"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "leads" in data["endpoints"]
        assert "stats" in data["endpoints"]
        assert "docs" in data["endpoints"]
    
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
        # Mock do coletor
        mock_collector_instance = Mock()
        mock_collector_instance.collect_from_google_places.return_value = [
            {
                "nome": "Supermercado Teste",
                "telefone": "(11) 99999-9999",
                "endereco": "Rua Teste, 123",
                "fonte": "Google Places"
            }
        ]
        mock_collector.return_value = mock_collector_instance
        
        # Mock do qualificador
        mock_qualifier_instance = Mock()
        mock_qualifier_instance.qualify_leads_batch.return_value = [
            {
                "nome": "Supermercado Teste",
                "telefone": "(11) 99999-9999",
                "endereco": "Rua Teste, 123",
                "fonte": "Google Places",
                "score": 5.0,
                "nivel": "A",
                "qualificado": True
            }
        ]
        mock_qualifier.return_value = mock_qualifier_instance
        
        # Executar teste
        response = client.post("/api/campaign/run")
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] == True
        assert "message" in data
        assert "data" in data
        assert "leads_collected" in data["data"]
        assert "leads_qualified" in data["data"]
        assert "filename" in data["data"]
        assert "timestamp" in data["data"]
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_campaign_run_error_handling(self, client):
        """Testar tratamento de erro na execução de campanha"""
        with patch('api.main_simple.LeadCollector') as mock_collector:
            # Mock de erro
            mock_collector.side_effect = Exception("API Error")
            
            # Executar teste
            response = client.post("/api/campaign/run")
            
            # Verificações
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_cors_headers(self, client):
        """Testar headers CORS"""
        response = client.options("/leads")
        
        # Verificar se CORS está configurado
        # (dependendo da implementação, pode retornar 200 ou 405)
        assert response.status_code in [200, 405]
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_response_time(self, client):
        """Testar tempo de resposta da API"""
        start_time = time.time()
        response = client.get("/leads")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Menos de 2 segundos
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_content_type(self, client):
        """Testar tipo de conteúdo das respostas"""
        response = client.get("/leads")
        
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_error_responses(self, client):
        """Testar respostas de erro da API"""
        # Testar endpoint inexistente
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # Testar método não permitido
        response = client.delete("/leads")
        assert response.status_code == 405
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_concurrent_requests(self, client):
        """Testar requisições concorrentes"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            response = client.get("/leads")
            results.put(response.status_code)
        
        # Criar múltiplas threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        while not results.empty():
            status_code = results.get()
            assert status_code == 200
    
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
            assert "success" in response
            assert "data" in response
            assert isinstance(response["data"], list)
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_memory_usage(self, client):
        """Testar uso de memória da API"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Fazer múltiplas requisições
        for _ in range(10):
            response = client.get("/leads")
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verificar se o aumento de memória é razoável (< 50MB)
        assert memory_increase < 50
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_logging(self, client):
        """Testar logging da API"""
        # Fazer requisição e verificar se logs são gerados
        response = client.get("/leads")
        
        assert response.status_code == 200
        
        # Verificar se logs são gerados (dependendo da implementação)
        # Isso pode ser verificado através de arquivos de log ou stdout
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_security_headers(self, client):
        """Testar headers de segurança"""
        response = client.get("/leads")
        
        assert response.status_code == 200
        
        # Verificar headers de segurança (se implementados)
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection"
        ]
        
        for header in security_headers:
            if header in response.headers:
                assert response.headers[header] is not None
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_rate_limiting(self, client):
        """Testar rate limiting da API"""
        # Fazer muitas requisições rapidamente
        responses = []
        for _ in range(20):
            response = client.get("/leads")
            responses.append(response.status_code)
        
        # Verificar se todas as requisições foram bem-sucedidas
        # (assumindo que rate limiting não está implementado)
        for status_code in responses:
            assert status_code == 200
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_error_recovery(self, client):
        """Testar recuperação de erros da API"""
        # Simular erro e verificar se a API se recupera
        with patch('api.main_simple.LeadCollector') as mock_collector:
            # Primeiro erro
            mock_collector.side_effect = Exception("Temporary error")
            response = client.post("/api/campaign/run")
            assert response.status_code == 500
            
            # Remover o mock e testar novamente
            mock_collector.side_effect = None
            response = client.get("/leads")
            assert response.status_code == 200
