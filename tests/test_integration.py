"""
Testes de integração para o sistema completo
TDD: Sistema deve funcionar de ponta a ponta corretamente
"""
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
import tempfile
import shutil

# Importar módulos do sistema
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

class TestSystemIntegration(unittest.TestCase):
    """Testes de integração para o sistema completo"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = [
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
            }
        ]
    
    def tearDown(self):
        """Limpeza após cada teste"""
        shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """Teste: Fluxo completo deve funcionar de ponta a ponta"""
        # Arrange
        from lead_collector import LeadCollector
        from lead_qualifier import LeadQualifier
        
        collector = LeadCollector()
        qualifier = LeadQualifier()
        
        # Act - Simular coleta
        collected_leads = self.test_data.copy()
        
        # Act - Qualificar leads
        qualified_leads = qualifier.qualify_leads_batch(collected_leads)
        
        # Act - Salvar resultados
        json_file = collector.save_leads_to_json(qualified_leads)
        csv_file = collector.save_leads_to_csv(qualified_leads)
        
        # Assert
        self.assertEqual(len(qualified_leads), len(collected_leads))
        
        # Verificar se todos os leads foram qualificados
        for lead in qualified_leads:
            self.assertIn('score', lead)
            self.assertIn('qualificado', lead)
            self.assertIn('nivel_qualificacao', lead)
            self.assertIn('criterios_atingidos', lead)
        
        # Verificar arquivos salvos (se retornaram nomes válidos)
        if json_file:
            self.assertTrue(Path(json_file).exists())
            Path(json_file).unlink()  # Limpar arquivo de teste
        if csv_file:
            self.assertTrue(Path(csv_file).exists())
            Path(csv_file).unlink()  # Limpar arquivo de teste
    
    def test_data_consistency(self):
        """Teste: Dados devem ser consistentes em todo o fluxo"""
        # Arrange
        from lead_collector import LeadCollector
        from lead_qualifier import LeadQualifier
        
        collector = LeadCollector()
        qualifier = LeadQualifier()
        
        # Act
        collected_leads = self.test_data.copy()
        qualified_leads = qualifier.qualify_leads_batch(collected_leads)
        
        # Assert - Dados originais devem ser preservados
        for i, original in enumerate(collected_leads):
            qualified = qualified_leads[i]
            
            # Campos originais devem ser mantidos
            self.assertEqual(original['nome'], qualified['nome'])
            self.assertEqual(original['telefone'], qualified['telefone'])
            self.assertEqual(original['website'], qualified['website'])
            self.assertEqual(original['endereco'], qualified['endereco'])
            self.assertEqual(original['cnae'], qualified['cnae'])
            self.assertEqual(original['fonte'], qualified['fonte'])
            self.assertEqual(original['data_coleta'], qualified['data_coleta'])
            
            # Novos campos devem ser adicionados
            self.assertIn('score', qualified)
            self.assertIn('qualificado', qualified)
            self.assertIn('nivel_qualificacao', qualified)
            self.assertIn('criterios_atingidos', qualified)
    
    def test_error_handling_integration(self):
        """Teste: Tratamento de erros deve funcionar em todo o sistema"""
        # Arrange
        from lead_collector import LeadCollector
        from lead_qualifier import LeadQualifier
        
        collector = LeadCollector()
        qualifier = LeadQualifier()
        
        # Act - Testar com dados inválidos
        invalid_leads = [
            {
                'nome': '',  # Nome vazio
                'telefone': 'invalid_phone',
                'website': 'not_a_url',
                'endereco': '',
                'cnae': 'invalid_cnae',
                'fonte': 'Teste',
                'data_coleta': '03/09/2025 17:17:09'
            }
        ]
        
        # Act - Sistema deve processar sem quebrar
        try:
            qualified_leads = qualifier.qualify_leads_batch(invalid_leads)
            
            # Assert - Sistema deve continuar funcionando
            self.assertEqual(len(qualified_leads), 1)
            self.assertIn('score', qualified_leads[0])
            
        except Exception as e:
            self.fail(f"Sistema quebrou com dados inválidos: {e}")
    
    def test_performance_integration(self):
        """Teste: Sistema deve processar múltiplos leads eficientemente"""
        # Arrange
        from lead_collector import LeadCollector
        from lead_qualifier import LeadQualifier
        import time
        
        collector = LeadCollector()
        qualifier = LeadQualifier()
        
        # Criar muitos leads para teste de performance
        many_leads = []
        for i in range(100):
            lead = self.test_data[0].copy()
            lead['nome'] = f"Empresa Teste {i}"
            lead['telefone'] = f"(11) 99999-{i:04d}"
            many_leads.append(lead)
        
        # Act - Medir tempo de processamento
        start_time = time.time()
        qualified_leads = qualifier.qualify_leads_batch(many_leads)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Assert
        self.assertEqual(len(qualified_leads), 100)
        
        # Performance deve ser aceitável (menos de 5 segundos para 100 leads)
        self.assertLess(processing_time, 5.0)
        
        print(f"Processamento de 100 leads em {processing_time:.2f} segundos")
    
    def test_file_formats_integration(self):
        """Teste: Diferentes formatos de arquivo devem ser compatíveis"""
        # Arrange
        from lead_collector import LeadCollector
        from lead_qualifier import LeadQualifier
        
        collector = LeadCollector()
        qualifier = LeadQualifier()
        
        # Act
        qualified_leads = qualifier.qualify_leads_batch(self.test_data)
        
        # Salvar em diferentes formatos
        json_file = collector.save_leads_to_json(qualified_leads)
        csv_file = collector.save_leads_to_csv(qualified_leads)
        
        # Assert - Verificar se arquivos são válidos (se retornaram nomes)
        if json_file:
            self.assertTrue(Path(json_file).exists())
            # Verificar JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                self.assertEqual(len(json_data), len(qualified_leads))
            Path(json_file).unlink()  # Limpar arquivo de teste
        
        if csv_file:
            self.assertTrue(Path(csv_file).exists())
            # Verificar CSV
            with open(csv_file, 'r', encoding='utf-8') as f:
                csv_content = f.read()
                self.assertIn('nome', csv_content)
                self.assertIn('score', csv_content)
                self.assertIn('Supermercado Exemplo', csv_content)
            Path(csv_file).unlink()  # Limpar arquivo de teste

if __name__ == '__main__':
    unittest.main()
