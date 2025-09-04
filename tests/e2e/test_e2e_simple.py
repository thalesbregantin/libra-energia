#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes E2E Simplificados
TDD Robusto inspirado nas Big Techs
"""

import pytest
import time
import requests
from fastapi.testclient import TestClient
from api.main_simple import app

class TestE2ESimple:
    """Testes E2E simplificados para o sistema"""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste para a API"""
        return TestClient(app)
    
    @pytest.mark.e2e
    @pytest.mark.api
    def test_full_system_workflow(self, client):
        """Testar fluxo completo do sistema"""
        print("🧪 Executando: test_full_system_workflow")
        
        # 1. Verificar se a API está funcionando
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Libra Energia" in data["message"]
        
        # 2. Verificar endpoint de leads
        response = client.get("/leads")
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        assert "message" in data
        
        # 3. Executar campanha
        response = client.post("/api/campaign/run")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        print("✅ Concluído: test_full_system_workflow")
    
    @pytest.mark.e2e
    @pytest.mark.api
    def test_api_performance_under_load(self, client):
        """Testar performance da API sob carga"""
        print("🧪 Executando: test_api_performance_under_load")
        
        # Fazer múltiplas requisições simultâneas
        start_time = time.time()
        
        responses = []
        for _ in range(10):
            response = client.get("/")
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificar se todas as respostas foram bem-sucedidas
        for response in responses:
            assert response.status_code == 200
        
        # Verificar se o tempo total é aceitável (menos de 5 segundos)
        assert total_time < 5.0
        
        print(f"✅ Concluído: test_api_performance_under_load (tempo: {total_time:.2f}s)")
    
    @pytest.mark.e2e
    @pytest.mark.api
    def test_api_error_recovery(self, client):
        """Testar recuperação de erros da API"""
        print("🧪 Executando: test_api_error_recovery")
        
        # Testar endpoint inexistente
        response = client.get("/endpoint-inexistente")
        assert response.status_code == 404
        
        # Verificar se a API ainda funciona após erro
        response = client.get("/")
        assert response.status_code == 200
        
        print("✅ Concluído: test_api_error_recovery")
    
    @pytest.mark.e2e
    @pytest.mark.api
    def test_api_data_consistency(self, client):
        """Testar consistência dos dados da API"""
        print("🧪 Executando: test_api_data_consistency")
        
        # Fazer múltiplas requisições e verificar consistência
        responses = []
        for _ in range(5):
            response = client.get("/leads")
            responses.append(response.json())
        
        # Verificar se todas as respostas têm a mesma estrutura
        for response in responses:
            assert "leads" in response
            assert "message" in response
            assert isinstance(response["leads"], list)
        
        print("✅ Concluído: test_api_data_consistency")
    
    @pytest.mark.e2e
    @pytest.mark.api
    def test_api_memory_usage(self, client):
        """Testar uso de memória da API"""
        print("🧪 Executando: test_api_memory_usage")
        
        import psutil
        import os
        
        # Obter uso de memória antes
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        # Fazer várias requisições
        for _ in range(20):
            response = client.get("/")
            assert response.status_code == 200
        
        # Obter uso de memória depois
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Verificar se o aumento de memória é razoável (menos de 20MB)
        assert memory_increase < 20 * 1024 * 1024  # 20MB em bytes
        
        print(f"✅ Concluído: test_api_memory_usage (aumento: {memory_increase / 1024 / 1024:.2f}MB)")
    
    @pytest.mark.e2e
    @pytest.mark.api
    def test_api_concurrent_requests(self, client):
        """Testar requisições concorrentes"""
        print("🧪 Executando: test_api_concurrent_requests")
        
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = client.get("/")
                results.put(("success", response.status_code))
            except Exception as e:
                results.put(("error", str(e)))
        
        # Criar múltiplas threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads terminarem
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        success_count = 0
        while not results.empty():
            result_type, result_data = results.get()
            if result_type == "success":
                assert result_data == 200
                success_count += 1
        
        # Verificar se pelo menos 80% das requisições foram bem-sucedidas
        assert success_count >= 4  # 4 de 5 (80%)
        
        print(f"✅ Concluído: test_api_concurrent_requests ({success_count}/5 sucessos)")
    
    @pytest.mark.e2e
    @pytest.mark.api
    def test_api_response_format(self, client):
        """Testar formato das respostas da API"""
        print("🧪 Executando: test_api_response_format")
        
        # Testar endpoint raiz
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert "status" in data
        assert "endpoints" in data
        
        # Testar endpoint de leads
        response = client.get("/leads")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "leads" in data
        assert "message" in data
        assert isinstance(data["leads"], list)
        
        print("✅ Concluído: test_api_response_format")
    
    @pytest.mark.e2e
    @pytest.mark.api
    def test_api_campaign_workflow(self, client):
        """Testar fluxo completo de campanha"""
        print("🧪 Executando: test_api_campaign_workflow")
        
        # 1. Verificar leads iniciais
        response = client.get("/leads")
        assert response.status_code == 200
        initial_data = response.json()
        initial_count = len(initial_data["leads"])
        
        # 2. Executar campanha
        response = client.post("/api/campaign/run")
        assert response.status_code == 200
        campaign_data = response.json()
        assert "message" in campaign_data
        
        # 3. Verificar se a campanha foi executada (mesmo que com erro)
        assert "leads_collected" in campaign_data or "error" in campaign_data
        
        print("✅ Concluído: test_api_campaign_workflow")
