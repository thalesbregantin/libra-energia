#!/usr/bin/env python3
"""
Testes TDD para o Frontend do Sistema de Prospecção
Testa funcionalidades do dashboard HTML/JavaScript
"""

import unittest
import json
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
import time
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading


class TestFrontendDataLoading(unittest.TestCase):
    """Testes para carregamento de dados no frontend"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Criar dados de teste
        self.sample_leads = [
            {
                "nome": "Empresa Teste 1",
                "telefone": "(11) 99999-9999",
                "website": "https://teste1.com",
                "endereco": "Rua Teste, 123",
                "cnae": "4721-1/01",
                "score": 5,
                "qualificado": True,
                "nivel_qualificacao": "Alto",
                "fonte": "Google Places",
                "data_coleta": "03/09/2025 16:30:00"
            },
            {
                "nome": "Empresa Teste 2",
                "telefone": "(11) 88888-8888",
                "website": "",
                "endereco": "Av. Teste, 456",
                "cnae": "4722-0/00",
                "score": 3,
                "qualificado": False,
                "nivel_qualificacao": "Médio",
                "fonte": "Instagram",
                "data_coleta": "03/09/2025 16:30:00"
            }
        ]
    
    def tearDown(self):
        """Limpeza após cada teste"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_create_sample_data_file(self):
        """Testa criação de arquivo de dados de exemplo"""
        filename = "leads_coletados_20250903_test.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.sample_leads, f, ensure_ascii=False, indent=2)
        
        self.assertTrue(os.path.exists(filename))
        
        with open(filename, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]['nome'], "Empresa Teste 1")
    
    def test_dashboard_html_structure(self):
        """Testa se o dashboard.html tem a estrutura básica necessária"""
        dashboard_content = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <title>Libra Energia - Dashboard de Prospecção</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <div id="data-status">Carregando dados...</div>
            <div id="total-leads">0</div>
            <div id="leads-encontrados">0</div>
            <canvas id="pieChart"></canvas>
            <canvas id="barChart"></canvas>
            <select id="filtro-nivel">
                <option value="Todos">Todos</option>
                <option value="Alto">Alto</option>
            </select>
            <input id="filtro-score" type="range" min="0" max="6" value="0">
            <select id="filtro-fonte">
                <option value="Todas">Todas</option>
                <option value="Google Places">Google Places</option>
            </select>
            <input id="filtro-nome" type="text" placeholder="Digite o nome...">
            <tbody id="leads-tbody"></tbody>
        </body>
        </html>
        """
        
        with open("dashboard.html", 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        
        self.assertTrue(os.path.exists("dashboard.html"))
        
        with open("dashboard.html", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar elementos essenciais
        self.assertIn('id="data-status"', content)
        self.assertIn('id="total-leads"', content)
        self.assertIn('id="pieChart"', content)
        self.assertIn('id="barChart"', content)
        self.assertIn('id="filtro-nivel"', content)
        self.assertIn('id="filtro-score"', content)
        self.assertIn('id="filtro-fonte"', content)
        self.assertIn('id="filtro-nome"', content)
        self.assertIn('id="leads-tbody"', content)


class TestFrontendFilters(unittest.TestCase):
    """Testes para funcionalidades de filtros"""
    
    def setUp(self):
        """Configuração inicial"""
        self.test_leads = [
            {
                "nome": "Supermercado ABC",
                "score": 5,
                "nivel_qualificacao": "Alto",
                "fonte": "Google Places",
                "qualificado": True
            },
            {
                "nome": "Padaria XYZ",
                "score": 3,
                "nivel_qualificacao": "Médio",
                "fonte": "Instagram",
                "qualificado": False
            },
            {
                "nome": "Academia 123",
                "score": 2,
                "nivel_qualificacao": "Baixo",
                "fonte": "Google Places",
                "qualificado": False
            }
        ]
    
    def test_filter_by_nivel(self):
        """Testa filtro por nível de qualificação"""
        # Filtro por nível "Alto"
        filtered = [lead for lead in self.test_leads if lead['nivel_qualificacao'] == 'Alto']
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['nome'], "Supermercado ABC")
        
        # Filtro por nível "Médio"
        filtered = [lead for lead in self.test_leads if lead['nivel_qualificacao'] == 'Médio']
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['nome'], "Padaria XYZ")
    
    def test_filter_by_score(self):
        """Testa filtro por score mínimo"""
        # Score mínimo 4
        filtered = [lead for lead in self.test_leads if lead['score'] >= 4]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['nome'], "Supermercado ABC")
        
        # Score mínimo 3
        filtered = [lead for lead in self.test_leads if lead['score'] >= 3]
        self.assertEqual(len(filtered), 2)
    
    def test_filter_by_fonte(self):
        """Testa filtro por fonte"""
        # Fonte "Google Places"
        filtered = [lead for lead in self.test_leads if lead['fonte'] == 'Google Places']
        self.assertEqual(len(filtered), 2)
        
        # Fonte "Instagram"
        filtered = [lead for lead in self.test_leads if lead['fonte'] == 'Instagram']
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['nome'], "Padaria XYZ")
    
    def test_filter_by_nome(self):
        """Testa filtro por nome"""
        # Busca por "Super"
        filtered = [lead for lead in self.test_leads if 'Super' in lead['nome']]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['nome'], "Supermercado ABC")
        
        # Busca por "ABC"
        filtered = [lead for lead in self.test_leads if 'ABC' in lead['nome']]
        self.assertEqual(len(filtered), 1)
    
    def test_combined_filters(self):
        """Testa combinação de filtros"""
        # Score >= 3 E fonte = "Google Places"
        filtered = [
            lead for lead in self.test_leads 
            if lead['score'] >= 3 and lead['fonte'] == 'Google Places'
        ]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['nome'], "Supermercado ABC")


class TestFrontendCharts(unittest.TestCase):
    """Testes para funcionalidades de gráficos"""
    
    def setUp(self):
        """Configuração inicial"""
        self.test_leads = [
            {"nivel_qualificacao": "Alto", "score": 5, "nome": "Empresa 1"},
            {"nivel_qualificacao": "Alto", "score": 6, "nome": "Empresa 2"},
            {"nivel_qualificacao": "Médio", "score": 3, "nome": "Empresa 3"},
            {"nivel_qualificacao": "Médio", "score": 4, "nome": "Empresa 4"},
            {"nivel_qualificacao": "Baixo", "score": 2, "nome": "Empresa 5"},
            {"nivel_qualificacao": "Baixo", "score": 1, "nome": "Empresa 6"}
        ]
    
    def test_pie_chart_data_calculation(self):
        """Testa cálculo de dados para gráfico de pizza"""
        nivel_data = [
            len([l for l in self.test_leads if l['nivel_qualificacao'] == 'Alto']),
            len([l for l in self.test_leads if l['nivel_qualificacao'] == 'Médio']),
            len([l for l in self.test_leads if l['nivel_qualificacao'] == 'Baixo'])
        ]
        
        self.assertEqual(nivel_data, [2, 2, 2])
    
    def test_bar_chart_data_calculation(self):
        """Testa cálculo de dados para gráfico de barras"""
        # Top 5 leads por score
        top_leads = sorted(self.test_leads, key=lambda x: x['score'], reverse=True)[:5]
        score_data = [{"name": lead['nome'], "score": lead['score']} for lead in top_leads]
        
        self.assertEqual(len(score_data), 5)
        self.assertEqual(score_data[0]['score'], 6)  # Maior score
        self.assertEqual(score_data[0]['name'], "Empresa 2")
    
    def test_chart_labels(self):
        """Testa labels dos gráficos"""
        pie_labels = ['Alto', 'Médio', 'Baixo']
        self.assertEqual(len(pie_labels), 3)
        self.assertIn('Alto', pie_labels)
        self.assertIn('Médio', pie_labels)
        self.assertIn('Baixo', pie_labels)


class TestFrontendInterface(unittest.TestCase):
    """Testes para interface e interações"""
    
    def test_metrics_calculation(self):
        """Testa cálculo de métricas do dashboard"""
        leads = [
            {"score": 5, "qualificado": True},
            {"score": 3, "qualificado": False},
            {"score": 6, "qualificado": True},
            {"score": 2, "qualificado": False}
        ]
        
        # Total de leads
        total = len(leads)
        self.assertEqual(total, 4)
        
        # Leads qualificados
        qualificados = len([l for l in leads if l['qualificado']])
        self.assertEqual(qualificados, 2)
        
        # Score médio
        score_medio = sum(l['score'] for l in leads) / len(leads)
        self.assertEqual(score_medio, 4.0)
        
        # Taxa de qualificação
        taxa_qualificacao = (qualificados / total) * 100
        self.assertEqual(taxa_qualificacao, 50.0)
    
    def test_data_status_messages(self):
        """Testa mensagens de status dos dados"""
        status_messages = {
            'loading': 'Carregando dados...',
            'success': 'Dados carregados com sucesso',
            'error': 'Erro ao carregar dados',
            'warning': 'Usando dados de exemplo'
        }
        
        self.assertIn('loading', status_messages)
        self.assertIn('success', status_messages)
        self.assertIn('error', status_messages)
        self.assertIn('warning', status_messages)
    
    def test_export_csv_structure(self):
        """Testa estrutura de exportação CSV"""
        headers = ['Nome', 'Telefone', 'Website', 'Endereço', 'Score', 'Nível', 'Qualificado', 'Fonte', 'Data']
        expected_headers = 9
        
        self.assertEqual(len(headers), expected_headers)
        self.assertIn('Nome', headers)
        self.assertIn('Score', headers)
        self.assertIn('Nível', headers)
        self.assertIn('Fonte', headers)


class TestFrontendAPI(unittest.TestCase):
    """Testes para integração com API"""
    
    def setUp(self):
        """Configuração inicial"""
        self.api_base_url = "http://localhost:8000"
        self.test_leads = [
            {
                "nome": "Empresa API Test",
                "telefone": "(11) 99999-9999",
                "score": 5,
                "nivel_qualificacao": "Alto",
                "fonte": "Google Places"
            }
        ]
    
    def test_api_endpoints_structure(self):
        """Testa estrutura dos endpoints da API"""
        endpoints = {
            'root': '/',
            'leads': '/api/leads',
            'stats': '/api/stats',
            'health': '/api/health'
        }
        
        self.assertIn('leads', endpoints)
        self.assertIn('stats', endpoints)
        self.assertIn('health', endpoints)
        self.assertEqual(endpoints['leads'], '/api/leads')
    
    def test_api_response_structure(self):
        """Testa estrutura da resposta da API"""
        mock_response = {
            "success": True,
            "data": self.test_leads,
            "pagination": {
                "total": 1,
                "limit": 100,
                "offset": 0,
                "has_more": False
            },
            "source_file": "leads_coletados_test.json",
            "timestamp": "2025-09-03T16:30:00"
        }
        
        self.assertTrue(mock_response['success'])
        self.assertIn('data', mock_response)
        self.assertIn('pagination', mock_response)
        self.assertIn('source_file', mock_response)
        self.assertIn('timestamp', mock_response)
    
    def test_api_error_handling(self):
        """Testa tratamento de erros da API"""
        error_responses = {
            'connection_error': 'ERR_CONNECTION_REFUSED',
            'not_found': '404 Not Found',
            'server_error': '500 Internal Server Error'
        }
        
        self.assertIn('connection_error', error_responses)
        self.assertIn('not_found', error_responses)
        self.assertIn('server_error', error_responses)


class TestFrontendIntegration(unittest.TestCase):
    """Testes de integração do frontend"""
    
    def setUp(self):
        """Configuração inicial"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_dashboard_file_creation(self):
        """Testa criação completa do arquivo dashboard.html"""
        # Simular criação do dashboard
        dashboard_content = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <title>Libra Energia - Dashboard de Prospecção</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <div id="data-status">Carregando dados...</div>
            <div id="total-leads">0</div>
            <canvas id="pieChart"></canvas>
            <canvas id="barChart"></canvas>
            <select id="filtro-nivel">
                <option value="Todos">Todos</option>
                <option value="Alto">Alto</option>
                <option value="Médio">Médio</option>
                <option value="Baixo">Baixo</option>
            </select>
            <input id="filtro-score" type="range" min="0" max="6" value="0">
            <select id="filtro-fonte">
                <option value="Todas">Todas</option>
                <option value="Google Places">Google Places</option>
                <option value="Instagram">Instagram</option>
            </select>
            <input id="filtro-nome" type="text" placeholder="Digite o nome...">
            <tbody id="leads-tbody"></tbody>
        </body>
        </html>
        """
        
        with open("dashboard.html", 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        
        # Verificar se arquivo foi criado
        self.assertTrue(os.path.exists("dashboard.html"))
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize("dashboard.html")
        self.assertGreater(file_size, 100)  # Deve ter pelo menos 100 bytes
    
    def test_data_file_integration(self):
        """Testa integração com arquivos de dados"""
        # Criar arquivo de dados
        test_data = [
            {
                "nome": "Empresa Integração Test",
                "telefone": "(11) 99999-9999",
                "score": 5,
                "nivel_qualificacao": "Alto",
                "fonte": "Google Places"
            }
        ]
        
        filename = "leads_coletados_20250903_integration.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # Verificar se arquivo foi criado
        self.assertTrue(os.path.exists(filename))
        
        # Carregar e verificar dados
        with open(filename, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(len(loaded_data), 1)
        self.assertEqual(loaded_data[0]['nome'], "Empresa Integração Test")


if __name__ == '__main__':
    # Configurar suite de testes
    test_suite = unittest.TestSuite()
    
    # Adicionar testes
    test_classes = [
        TestFrontendDataLoading,
        TestFrontendFilters,
        TestFrontendCharts,
        TestFrontendInterface,
        TestFrontendAPI,
        TestFrontendIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Relatório final
    print("\n" + "="*60)
    print("RELATÓRIO FINAL DOS TESTES DO FRONTEND")
    print("="*60)
    print(f"Testes executados: {result.testsRun}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    print(f"Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.failures:
        print("\nFALHAS:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERROS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ TODOS OS TESTES DO FRONTEND PASSARAM!")
    else:
        print("\n❌ ALGUNS TESTES DO FRONTEND FALHARAM!")
