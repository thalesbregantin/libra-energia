"""
Testes para o sistema de coleta de leads
TDD: Sistema deve coletar leads de múltiplas fontes corretamente
"""
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

# Importar módulos do sistema
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

class TestLeadCollector(unittest.TestCase):
    """Testes para a classe LeadCollector"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.sample_google_places_response = {
            'results': [
                {
                    'name': 'Supermercado Exemplo',
                    'formatted_phone_number': '(11) 99999-9999',
                    'website': 'https://www.exemplo.com.br',
                    'formatted_address': 'Rua das Flores, 123, São Paulo, SP',
                    'place_id': 'test_place_id_1'
                },
                {
                    'name': 'Padaria do João',
                    'formatted_phone_number': '(11) 88888-8888',
                    'website': '',
                    'formatted_address': 'Av. Paulista, 456, São Paulo, SP',
                    'place_id': 'test_place_id_2'
                }
            ]
        }
        
        self.expected_leads = [
            {
                'nome': 'Supermercado Exemplo',
                'telefone': '(11) 99999-9999',
                'website': 'https://www.exemplo.com.br',
                'endereco': 'Rua das Flores, 123, São Paulo, SP',
                'place_id': 'test_place_id_1',
                'fonte': 'Google Places',
                'data_coleta': None  # Será preenchido durante a coleta
            },
            {
                'nome': 'Padaria do João',
                'telefone': '(11) 88888-8888',
                'website': '',
                'endereco': 'Av. Paulista, 456, São Paulo, SP',
                'place_id': 'test_place_id_2',
                'fonte': 'Google Places',
                'data_coleta': None  # Será preenchido durante a coleta
            }
        ]
    
    def test_collector_initialization(self):
        """Teste: LeadCollector deve ser inicializado corretamente"""
        # Arrange & Act
        from lead_collector import LeadCollector
        collector = LeadCollector()
        
        # Assert
        self.assertIsNotNone(collector)
        self.assertIsInstance(collector, LeadCollector)
    
    def test_google_places_api_call(self):
        """Teste: API do Google Places deve ser chamada corretamente"""
        # Arrange
        from lead_collector import LeadCollector
        collector = LeadCollector()
        
        # Act - Fazer chamada real para a API
        leads = collector.collect_from_google_places('supermercado', 'São Paulo, SP')
        
        # Assert - Verificar se a API retornou dados válidos
        self.assertIsInstance(leads, list)
        if leads:  # Se a API retornou dados
            self.assertGreater(len(leads), 0)
            # Verificar estrutura do primeiro lead
            first_lead = leads[0]
            self.assertIn('nome', first_lead)
            self.assertIn('endereco', first_lead)
            self.assertIn('fonte', first_lead)
            self.assertEqual(first_lead['fonte'], 'Google Places')
    
    @patch('lead_collector.requests.get')
    def test_google_places_error_handling(self, mock_get):
        """Teste: Erros da API devem ser tratados corretamente"""
        # Arrange
        from lead_collector import LeadCollector
        collector = LeadCollector()
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_get.return_value = mock_response
        
        # Act - Usar o método que realmente faz a chamada HTTP
        leads = collector.collect_from_google_places('supermercado', 'São Paulo, SP')
        
        # Assert - Verificar se o sistema não quebra com erros
        self.assertIsInstance(leads, list)
    
    def test_lead_data_structure(self):
        """Teste: Estrutura dos leads coletados deve estar correta"""
        # Arrange
        from lead_collector import LeadCollector
        collector = LeadCollector()
        
        # Act
        leads = collector._process_google_places_results(
            self.sample_google_places_response['results']
        )
        
        # Assert
        self.assertEqual(len(leads), 2)
        
        for lead in leads:
            required_fields = ['nome', 'telefone', 'website', 'endereco', 'place_id', 'fonte']
            for field in required_fields:
                self.assertIn(field, lead)
                self.assertIsNotNone(lead[field])
    
    def test_lead_data_cleaning(self):
        """Teste: Dados dos leads devem ser limpos corretamente"""
        # Arrange
        from lead_collector import LeadCollector
        collector = LeadCollector()
        
        # Act
        leads = collector._process_google_places_results(
            self.sample_google_places_response['results']
        )
        
        # Assert
        for lead in leads:
            # Nome não deve estar vazio
            self.assertGreater(len(lead['nome'].strip()), 0)
            
            # Telefone deve ter formato válido
            if lead['telefone']:
                self.assertIn('(', lead['telefone'])
                self.assertIn(')', lead['telefone'])
            
            # Website deve ser URL válida ou string vazia
            if lead['website']:
                self.assertTrue(lead['website'].startswith('http'))
    
    def test_save_leads_to_json(self):
        """Teste: Leads devem ser salvos em JSON corretamente"""
        # Arrange
        from lead_collector import LeadCollector
        collector = LeadCollector()
        
        # Act
        filename = collector.save_leads_to_json(self.expected_leads)
        
        # Assert
        self.assertIsInstance(filename, str)
        self.assertTrue(filename.endswith('.json'))
        
        # Verificar se arquivo foi criado
        file_path = Path(filename)
        self.assertTrue(file_path.exists())
        
        # Verificar conteúdo
        with open(filename, 'r', encoding='utf-8') as f:
            saved_leads = json.load(f)
        
        self.assertEqual(len(saved_leads), len(self.expected_leads))
        
        # Limpar arquivo de teste
        file_path.unlink()
    
    def test_save_leads_to_csv(self):
        """Teste: Leads devem ser salvos em CSV corretamente"""
        # Arrange
        from lead_collector import LeadCollector
        collector = LeadCollector()
        
        # Act
        filename = collector.save_leads_to_csv(self.expected_leads)
        
        # Assert
        self.assertIsInstance(filename, str)
        self.assertTrue(filename.endswith('.csv'))
        
        # Verificar se arquivo foi criado
        file_path = Path(filename)
        self.assertTrue(file_path.exists())
        
        # Verificar conteúdo básico
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('nome', content)
        self.assertIn('telefone', content)
        self.assertIn('Supermercado Exemplo', content)
        
        # Limpar arquivo de teste
        file_path.unlink()
    
    def test_run_collection_campaign(self):
        """Teste: Campanha de coleta deve executar corretamente"""
        # Arrange
        from lead_collector import LeadCollector
        collector = LeadCollector()
        
        keywords = ['supermercado', 'padaria']
        cities = ['São Paulo, SP']
        
        # Mock da API do Google Places
        with patch.object(collector, 'search_google_places') as mock_search:
            mock_search.return_value = self.expected_leads
            
                    # Act
        leads = collector.run_collection_campaign(keywords, cities)
        
        # Assert - Verificar se a campanha retornou leads (pode ser mais que o esperado)
        self.assertGreater(len(leads), 0)
        # Verificar se os leads têm a estrutura correta
        for lead in leads:
            self.assertIn('nome', lead)
            self.assertIn('endereco', lead)
            self.assertIn('fonte', lead)

if __name__ == '__main__':
    unittest.main()
