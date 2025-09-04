#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes Unitários - Lead Collector
TDD Robusto inspirado nas Big Techs
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.lead_collector import LeadCollector

class TestLeadCollector:
    """Testes unitários para LeadCollector"""
    
    @pytest.fixture
    def lead_collector(self):
        """Instância do LeadCollector para testes"""
        return LeadCollector()
    
    @pytest.mark.unit
    def test_lead_collector_initialization(self, lead_collector):
        """Testar inicialização do LeadCollector"""
        assert lead_collector is not None
        assert hasattr(lead_collector, 'collect_from_google_places')
        assert hasattr(lead_collector, 'collect_from_instagram')
        assert hasattr(lead_collector, 'save_leads')
    
    @pytest.mark.unit
    @patch('src.lead_collector.requests.get')
    def test_collect_from_google_places_success(self, mock_get, lead_collector):
        """Testar coleta bem-sucedida do Google Places"""
        # Mock da resposta da API
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
        
        # Executar teste
        leads = lead_collector.collect_from_google_places("supermercado", "São Paulo, SP", max_results=1)
        
        # Verificações
        assert len(leads) == 1
        assert leads[0]["nome"] == "Supermercado Teste"
        assert leads[0]["endereco"] == "Rua Teste, 123 - São Paulo, SP"
        assert leads[0]["telefone"] == "(11) 99999-9999"
        assert leads[0]["website"] == "https://teste.com"
        assert leads[0]["fonte"] == "Google Places"
        
        # Verificar se a API foi chamada corretamente
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "supermercado" in call_args[1]["params"]["query"]
        assert "São Paulo, SP" in call_args[1]["params"]["query"]
    
    @pytest.mark.unit
    @patch('src.lead_collector.requests.get')
    def test_collect_from_google_places_api_error(self, mock_get, lead_collector):
        """Testar erro na API do Google Places"""
        # Mock de erro da API
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_get.return_value = mock_response
        
        # Executar teste
        leads = lead_collector.collect_from_google_places("supermercado", "São Paulo, SP")
        
        # Verificações
        assert len(leads) == 0
    
    @pytest.mark.unit
    @patch('src.lead_collector.requests.get')
    def test_collect_from_google_places_network_error(self, mock_get, lead_collector):
        """Testar erro de rede na API do Google Places"""
        # Mock de erro de rede
        mock_get.side_effect = Exception("Network error")
        
        # Executar teste
        leads = lead_collector.collect_from_google_places("supermercado", "São Paulo, SP")
        
        # Verificações
        assert len(leads) == 0
    
    @pytest.mark.unit
    def test_collect_from_google_places_invalid_parameters(self, lead_collector):
        """Testar parâmetros inválidos"""
        with pytest.raises(ValueError):
            lead_collector.collect_from_google_places("", "São Paulo, SP")
        
        with pytest.raises(ValueError):
            lead_collector.collect_from_google_places("supermercado", "")
        
        with pytest.raises(ValueError):
            lead_collector.collect_from_google_places("supermercado", "São Paulo, SP", max_results=0)
    
    @pytest.mark.unit
    @patch('src.lead_collector.InstagramScraper')
    def test_collect_from_instagram_success(self, mock_scraper, lead_collector):
        """Testar coleta bem-sucedida do Instagram"""
        # Mock do scraper
        mock_instance = Mock()
        mock_instance.scrape_business_profile.return_value = {
            "username": "test_business",
            "followers": 1000,
            "posts": 50,
            "bio": "Supermercado de qualidade",
            "contact_info": {
                "phone": "(11) 88888-8888",
                "email": "contato@teste.com"
            }
        }
        mock_scraper.return_value = mock_instance
        
        # Executar teste
        leads = lead_collector.collect_from_instagram(["test_business"])
        
        # Verificações
        assert len(leads) == 1
        assert leads[0]["nome"] == "test_business"
        assert leads[0]["telefone"] == "(11) 88888-8888"
        assert leads[0]["fonte"] == "Instagram"
    
    @pytest.mark.unit
    @patch('src.lead_collector.InstagramScraper')
    def test_collect_from_instagram_error(self, mock_scraper, lead_collector):
        """Testar erro na coleta do Instagram"""
        # Mock de erro
        mock_scraper.side_effect = Exception("Instagram API error")
        
        # Executar teste
        leads = lead_collector.collect_from_instagram(["test_business"])
        
        # Verificações
        assert len(leads) == 0
    
    @pytest.mark.unit
    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_save_leads_success(self, mock_json_dump, mock_open, lead_collector):
        """Testar salvamento bem-sucedido de leads"""
        # Dados de teste
        leads = [
            {
                "nome": "Supermercado Teste",
                "telefone": "(11) 99999-9999",
                "fonte": "Google Places"
            }
        ]
        
        # Executar teste
        filename = lead_collector.save_leads(leads)
        
        # Verificações
        assert filename is not None
        assert "leads_coletados_" in filename
        assert filename.endswith(".json")
        
        # Verificar se o arquivo foi aberto e os dados salvos
        mock_open.assert_called_once()
        mock_json_dump.assert_called_once()
    
    @pytest.mark.unit
    def test_save_leads_empty_list(self, lead_collector):
        """Testar salvamento de lista vazia"""
        with pytest.raises(ValueError):
            lead_collector.save_leads([])
    
    @pytest.mark.unit
    def test_save_leads_invalid_data(self, lead_collector):
        """Testar salvamento de dados inválidos"""
        with pytest.raises(ValueError):
            lead_collector.save_leads(None)
        
        with pytest.raises(ValueError):
            lead_collector.save_leads("invalid_data")
    
    @pytest.mark.unit
    @patch('src.lead_collector.requests.get')
    def test_collect_from_google_places_max_results(self, mock_get, lead_collector):
        """Testar limite de resultados"""
        # Mock da resposta com múltiplos resultados
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"name": f"Supermercado {i}", "formatted_address": f"Rua {i}"}
                for i in range(10)
            ],
            "status": "OK"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Executar teste com limite
        leads = lead_collector.collect_from_google_places("supermercado", "São Paulo, SP", max_results=5)
        
        # Verificações
        assert len(leads) == 5
    
    @pytest.mark.unit
    def test_lead_collector_data_validation(self, lead_collector):
        """Testar validação de dados"""
        # Dados válidos
        valid_lead = {
            "nome": "Supermercado Teste",
            "telefone": "(11) 99999-9999",
            "endereco": "Rua Teste, 123",
            "fonte": "Google Places"
        }
        
        # Dados inválidos
        invalid_lead = {
            "nome": "",  # Nome vazio
            "telefone": "invalid_phone",
            "endereco": "Rua Teste, 123",
            "fonte": "Google Places"
        }
        
        # Testar validação (assumindo que existe método de validação)
        if hasattr(lead_collector, 'validate_lead'):
            assert lead_collector.validate_lead(valid_lead) == True
            assert lead_collector.validate_lead(invalid_lead) == False
    
    @pytest.mark.unit
    @patch('src.lead_collector.requests.get')
    def test_collect_from_google_places_rate_limiting(self, mock_get, lead_collector):
        """Testar rate limiting da API"""
        # Mock de rate limiting
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_get.return_value = mock_response
        
        # Executar teste
        leads = lead_collector.collect_from_google_places("supermercado", "São Paulo, SP")
        
        # Verificações
        assert len(leads) == 0
    
    @pytest.mark.unit
    @patch('src.lead_collector.requests.get')
    def test_collect_from_google_places_partial_data(self, mock_get, lead_collector):
        """Testar coleta com dados parciais"""
        # Mock com dados parciais
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "name": "Supermercado Teste",
                    "formatted_address": "Rua Teste, 123 - São Paulo, SP",
                    # Sem telefone e website
                    "rating": 4.5,
                    "place_id": "test_place_id"
                }
            ],
            "status": "OK"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Executar teste
        leads = lead_collector.collect_from_google_places("supermercado", "São Paulo, SP", max_results=1)
        
        # Verificações
        assert len(leads) == 1
        assert leads[0]["nome"] == "Supermercado Teste"
        assert leads[0]["telefone"] is None or leads[0]["telefone"] == ""
        assert leads[0]["website"] is None or leads[0]["website"] == ""
        assert leads[0]["endereco"] == "Rua Teste, 123 - São Paulo, SP"
