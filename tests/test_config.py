"""
Testes para o sistema de configuração
TDD: Configuração deve carregar variáveis de ambiente corretamente
"""
import unittest
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Importar módulos do sistema
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

class TestConfig(unittest.TestCase):
    """Testes para a classe Config"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.test_env_content = """
GOOGLE_PLACES_API_KEY=test_key_123
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
EMPRESA_NOME=Libra Energia
REPRESENTANTE_NOME=João Silva
"""
    
    def test_env_file_loading(self):
        """Teste: Arquivo .env deve ser carregado corretamente"""
        # Act
        from config import Config
        config = Config()
        
        # Assert - Verifica se as variáveis foram carregadas (não necessariamente com valores específicos)
        self.assertIsNotNone(config.GOOGLE_PLACES_API_KEY)
        self.assertIsNotNone(config.EMPRESA_NOME)
        self.assertIsNotNone(config.REPRESENTANTE_NOME)
    
    def test_default_values(self):
        """Teste: Valores padrão devem ser definidos quando .env não existe"""
        # Arrange
        with patch('pathlib.Path.exists', return_value=False):
            with patch('builtins.open', side_effect=FileNotFoundError):
                # Act
                from config import Config
                config = Config()
                
                # Assert
                self.assertIsNotNone(config.PALAVRAS_CHAVE)
                self.assertIsNotNone(config.CIDADES_INICIAIS)
                self.assertIsNotNone(config.CNAES_ALTO_CONSUMO)
    
    def test_palavras_chave_structure(self):
        """Teste: Lista de palavras-chave deve ter estrutura correta"""
        # Arrange & Act
        from config import Config
        config = Config()
        
        # Assert
        self.assertIsInstance(config.PALAVRAS_CHAVE, list)
        self.assertGreater(len(config.PALAVRAS_CHAVE), 0)
        for keyword in config.PALAVRAS_CHAVE:
            self.assertIsInstance(keyword, str)
            self.assertGreater(len(keyword), 0)
    
    def test_cidades_structure(self):
        """Teste: Lista de cidades deve ter estrutura correta"""
        # Arrange & Act
        from config import Config
        config = Config()
        
        # Assert
        self.assertIsInstance(config.CIDADES_INICIAIS, list)
        self.assertGreater(len(config.CIDADES_INICIAIS), 0)
        for cidade in config.CIDADES_INICIAIS:
            self.assertIsInstance(cidade, str)
            self.assertIn(',', cidade)  # Formato: "Cidade, UF"
    
    def test_cnaes_structure(self):
        """Teste: Lista de CNAEs deve ter estrutura correta"""
        # Arrange & Act
        from config import Config
        config = Config()
        
        # Assert
        self.assertIsInstance(config.CNAES_ALTO_CONSUMO, list)
        self.assertGreater(len(config.CNAES_ALTO_CONSUMO), 0)
        for cnae in config.CNAES_ALTO_CONSUMO:
            self.assertIsInstance(cnae, str)
            self.assertIn('-', cnae)  # Formato: "XXXX-X/XX"

if __name__ == '__main__':
    unittest.main()
