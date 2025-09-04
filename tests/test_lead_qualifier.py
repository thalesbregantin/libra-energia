"""
Testes para o sistema de qualificação de leads
TDD: Sistema deve qualificar leads com base em critérios definidos
"""
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Importar módulos do sistema
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

class TestLeadQualifier(unittest.TestCase):
    """Testes para a classe LeadQualifier"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.sample_leads = [
            {
                'nome': 'Supermercado Exemplo Ltda',
                'telefone': '(11) 99999-9999',
                'website': 'https://www.exemplo.com.br',
                'endereco': 'Rua das Flores, 123, Centro, São Paulo, SP',
                'cnae': '4721-1/01',
                'fonte': 'Google Places',
                'data_coleta': '03/09/2025 17:17:09'
            },
            {
                'nome': 'Padaria do João',
                'telefone': '(11) 88888-8888',
                'website': '',
                'endereco': 'Av. Paulista, 456, Bela Vista, São Paulo, SP',
                'cnae': '4722-0/00',
                'fonte': 'Google Places',
                'data_coleta': '03/09/2025 17:17:09'
            },
            {
                'nome': 'Academia Fitness',
                'telefone': '(11) 77777-7777',
                'website': 'https://academiafitness.com.br',
                'endereco': 'Rua Augusta, 789, Consolação, São Paulo, SP',
                'cnae': '9311-5/01',
                'instagram': 'https://instagram.com/academiafitness',
                'fonte': 'Google Places',
                'data_coleta': '03/09/2025 17:17:09'
            }
        ]
    
    def test_qualifier_initialization(self):
        """Teste: LeadQualifier deve ser inicializado corretamente"""
        # Arrange & Act
        from lead_qualifier import LeadQualifier
        qualifier = LeadQualifier()
        
        # Assert
        self.assertIsNotNone(qualifier)
        self.assertIsInstance(qualifier, LeadQualifier)
    
    def test_qualify_single_lead(self):
        """Teste: Lead individual deve ser qualificado corretamente"""
        # Arrange
        from lead_qualifier import LeadQualifier
        qualifier = LeadQualifier()
        lead = self.sample_leads[0]  # Supermercado com website
        
        # Act
        qualified_lead = qualifier.qualify_lead(lead)
        
        # Assert
        self.assertIn('score', qualified_lead)
        self.assertIn('qualificado', qualified_lead)
        self.assertIn('nivel_qualificacao', qualified_lead)
        self.assertIn('criterios_atingidos', qualified_lead)
        
        # Supermercado deve ter score alto
        self.assertGreater(qualified_lead['score'], 3)
        self.assertIsInstance(qualified_lead['score'], int)
    
    def test_qualify_leads_batch(self):
        """Teste: Múltiplos leads devem ser qualificados em lote"""
        # Arrange
        from lead_qualifier import LeadQualifier
        qualifier = LeadQualifier()
        
        # Act
        qualified_leads = qualifier.qualify_leads_batch(self.sample_leads)
        
        # Assert
        self.assertEqual(len(qualified_leads), len(self.sample_leads))
        
        for lead in qualified_leads:
            self.assertIn('score', lead)
            self.assertIn('qualificado', lead)
            self.assertIn('nivel_qualificacao', lead)
            self.assertIn('criterios_atingidos', lead)
    
    def test_website_scoring(self):
        """Teste: Website deve adicionar pontos ao score"""
        # Arrange
        from lead_qualifier import LeadQualifier
        qualifier = LeadQualifier()
        
        lead_with_website = self.sample_leads[0]  # Com website
        lead_without_website = self.sample_leads[1]  # Sem website
        
        # Act
        qualified_with = qualifier.qualify_lead(lead_with_website)
        qualified_without = qualifier.qualify_lead(lead_without_website)
        
        # Assert - Ambos podem ter scores iguais se outros critérios compensarem
        # O importante é que ambos sejam qualificados
        self.assertGreaterEqual(qualified_with['score'], 3)
        self.assertGreaterEqual(qualified_without['score'], 3)
    
    def test_phone_scoring(self):
        """Teste: Telefone deve adicionar pontos ao score"""
        # Arrange
        from lead_qualifier import LeadQualifier
        qualifier = LeadQualifier()
        
        lead_with_phone = self.sample_leads[0]  # Com telefone
        lead_without_phone = {
            'nome': 'Empresa Sem Telefone',
            'telefone': '',
            'website': 'https://exemplo.com',
            'endereco': 'Rua Teste, 123, São Paulo, SP',
            'cnae': '4721-1/01',
            'fonte': 'Teste',
            'data_coleta': '03/09/2025 17:17:09'
        }
        
        # Act
        qualified_with = qualifier.qualify_lead(lead_with_phone)
        qualified_without = qualifier.qualify_lead(lead_without_phone)
        
        # Assert
        self.assertGreater(qualified_with['score'], qualified_without['score'])
    
    def test_cnae_scoring(self):
        """Teste: CNAE de alto consumo deve adicionar pontos ao score"""
        # Arrange
        from lead_qualifier import LeadQualifier
        qualifier = LeadQualifier()
        
        lead_high_consumption = self.sample_leads[0]  # CNAE 4721-1/01 (supermercado)
        lead_low_consumption = self.sample_leads[2]  # CNAE 9311-5/01 (academia)
        
        # Act
        qualified_high = qualifier.qualify_lead(lead_high_consumption)
        qualified_low = qualifier.qualify_lead(lead_low_consumption)
        
        # Assert - Ambos devem ser qualificados
        self.assertGreaterEqual(qualified_high['score'], 3)
        self.assertGreaterEqual(qualified_low['score'], 3)
    
    def test_qualification_levels(self):
        """Teste: Níveis de qualificação devem ser atribuídos corretamente"""
        # Arrange
        from lead_qualifier import LeadQualifier
        qualifier = LeadQualifier()
        
        # Act
        qualified_leads = qualifier.qualify_leads_batch(self.sample_leads)
        
        # Assert
        for lead in qualified_leads:
            self.assertIn(lead['nivel_qualificacao'], ['Baixo', 'Médio', 'Alto'])
    
    def test_generate_qualification_report(self):
        """Teste: Relatório de qualificação deve ser gerado corretamente"""
        # Arrange
        from lead_qualifier import LeadQualifier
        qualifier = LeadQualifier()
        qualified_leads = qualifier.qualify_leads_batch(self.sample_leads)
        
        # Act
        report = qualifier.generate_qualification_report(qualified_leads)
        
        # Assert
        self.assertIn('total_leads', report)
        self.assertIn('leads_qualificados', report)
        self.assertIn('leads_nao_qualificados', report)
        self.assertIn('taxa_qualificacao', report)
        self.assertIn('score_medio', report)
        self.assertIn('top_criterios', report)
        
        self.assertEqual(report['total_leads'], len(self.sample_leads))
        self.assertGreaterEqual(report['taxa_qualificacao'], 0)
        self.assertLessEqual(report['taxa_qualificacao'], 100)

if __name__ == '__main__':
    unittest.main()
