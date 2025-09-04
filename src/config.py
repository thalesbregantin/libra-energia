"""
Configurações do sistema de automação de prospecção
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    # API do Google Places
    GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
    GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    
    # Firebase
    FIREBASE_CREDENTIALS_FILE = os.getenv('FIREBASE_CREDENTIALS_FILE', 'firebase-credentials.json')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # E-mail
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # Scraping
    SCRAPING_DELAY = int(os.getenv('SCRAPING_DELAY', 2))
    MAX_RESULTS_PER_SEARCH = int(os.getenv('MAX_RESULTS_PER_SEARCH', 100))
    HEADLESS_BROWSER = os.getenv('HEADLESS_BROWSER', 'true').lower() == 'true'
    
    # Empresa
    EMPRESA_NOME = os.getenv('EMPRESA_NOME', 'Libra Energia')
    REPRESENTANTE_NOME = os.getenv('REPRESENTANTE_NOME', 'Seu Nome')
    REPRESENTANTE_TELEFONE = os.getenv('REPRESENTANTE_TELEFONE')
    
    # CNAEs de alto consumo de energia
    CNAES_ALTO_CONSUMO = [
        '4721-1/01',  # Supermercados
        '4721-1/02',  # Minimercados
        '4721-1/03',  # Lojas de conveniência
        '4722-0/00',  # Padarias
        '9311-5/01',  # Academias
        '8690-3/01',  # Clínicas médicas
        '1011-2/01',  # Frigoríficos
        '1011-2/02',  # Abatedouros
        '1012-1/00',  # Produtos de carne
        '1013-9/00',  # Produtos de aves
        '1020-1/00',  # Produtos de pescado
        '1031-7/00',  # Conservas de carne
        '1032-5/00',  # Conservas de pescado
        '1041-4/00',  # Óleos vegetais
        '1042-2/00',  # Margarina
        '1051-1/00',  # Laticínios
        '1061-9/00',  # Moagem de cereais
        '1062-7/00',  # Fabricação de farinhas
        '1063-5/00',  # Fabricação de amidos
        '1064-3/00',  # Fabricação de rações
        '1071-6/00',  # Fabricação de açúcar
        '1072-4/00',  # Fabricação de álcool
        '1081-3/00',  # Torrefação e moagem de café
        '1082-1/00',  # Fabricação de produtos à base de café
        '1091-0/00',  # Fabricação de produtos de panificação
        '1092-8/00',  # Fabricação de biscoitos e bolachas
        '1093-6/00',  # Fabricação de produtos derivados do cacau
        '1094-4/00',  # Fabricação de confeitos
        '1095-2/00',  # Fabricação de massas alimentícias
        '1096-1/00',  # Fabricação de especiarias
        '1097-9/00',  # Fabricação de temperos
        '1099-5/00',  # Fabricação de produtos alimentícios
        '1100-2/00',  # Fabricação de bebidas não alcoólicas
        '1101-1/00',  # Fabricação de cerveja
        '1102-9/00',  # Fabricação de vinhos
        '1103-7/00',  # Fabricação de malte
        '1104-5/00',  # Fabricação de cachaça
        '1105-3/00',  # Fabricação de outras bebidas alcoólicas
        '1200-7/00',  # Fabricação de produtos do fumo
        '1300-1/00',  # Fabricação de produtos têxteis
        '1400-4/00',  # Confecção de artigos do vestuário
        '1500-7/00',  # Curtimento e preparação de couros
        '1600-0/00',  # Fabricação de produtos de madeira
        '1700-3/00',  # Fabricação de papel e celulose
        '1800-6/00',  # Impressão e reprodução de gravações
        '1900-9/00',  # Fabricação de produtos de coque
        '2000-1/00',  # Fabricação de produtos químicos
        '2100-4/00',  # Fabricação de produtos farmoquímicos
        '2200-7/00',  # Fabricação de produtos de borracha
        '2300-0/00',  # Fabricação de produtos de plástico
        '2400-3/00',  # Fabricação de produtos de minerais não metálicos
        '2500-6/00',  # Fabricação de produtos metalúrgicos
        '2600-9/00',  # Fabricação de produtos de metal
        '2700-2/00',  # Fabricação de equipamentos de informática
        '2800-5/00',  # Fabricação de máquinas e equipamentos
        '2900-8/00',  # Fabricação de veículos automotores
        '3000-0/00',  # Fabricação de outros equipamentos de transporte
        '3100-3/00',  # Fabricação de móveis
        '3200-6/00',  # Fabricação de produtos diversos
        '3300-9/00',  # Manutenção e reparação de máquinas
        '3500-5/00',  # Geração de energia elétrica
        '3600-8/00',  # Distribuição de energia elétrica
        '3700-1/00',  # Comércio de energia elétrica
        '3800-4/00',  # Produção e distribuição de vapor
        '3900-7/00',  # Captação, tratamento e distribuição de água
        '4100-0/00',  # Construção de edifícios
        '4200-3/00',  # Obras de infraestrutura
        '4300-6/00',  # Serviços especializados para construção
        '4500-1/00',  # Comércio e reparação de veículos
        '4600-4/00',  # Comércio por atacado
        '4700-7/00',  # Comércio varejista
        '4900-1/00',  # Transporte terrestre
        '5000-4/00',  # Transporte aquaviário
        '5100-7/00',  # Transporte aéreo
        '5200-0/00',  # Armazenamento e atividades auxiliares
        '5300-3/00',  # Correio e outras atividades de entrega
        '5500-7/00',  # Alojamento
        '5600-0/00',  # Alimentação
        '5800-4/00',  # Edição
        '5900-7/00',  # Atividades cinematográficas
        '6000-0/00',  # Atividades de rádio e televisão
        '6100-3/00',  # Telecomunicações
        '6200-6/00',  # Atividades dos serviços de TI
        '6300-9/00',  # Atividades de prestação de serviços de informação
        '6400-2/00',  # Atividades dos serviços financeiros
        '6500-5/00',  # Seguros, previdência e planos de saúde
        '6600-8/00',  # Atividades auxiliares dos serviços financeiros
        '6800-2/00',  # Atividades imobiliárias
        '6900-5/00',  # Atividades jurídicas
        '7000-8/00',  # Atividades de contabilidade
        '7100-1/00',  # Atividades de consultoria em gestão empresarial
        '7200-4/00',  # Atividades de arquitetura e engenharia
        '7300-7/00',  # Pesquisa e desenvolvimento experimental
        '7400-0/00',  # Atividades veterinárias
        '7500-3/00',  # Atividades profissionais
        '7700-6/00',  # Atividades de aluguel
        '7800-9/00',  # Atividades de emprego
        '7900-2/00',  # Agências de viagens
        '8000-5/00',  # Atividades de segurança e investigação
        '8100-8/00',  # Atividades de serviços para edifícios
        '8200-1/00',  # Atividades de escritório
        '8500-9/00',  # Educação
        '8600-2/00',  # Atividades de atenção à saúde humana
        '8700-5/00',  # Atividades de atenção à saúde humana integrada
        '8800-8/00',  # Atividades de assistência social
        '9000-1/00',  # Atividades artísticas
        '9100-4/00',  # Atividades culturais
        '9200-7/00',  # Atividades de jogos de azar
        '9300-0/00',  # Atividades esportivas
        '9400-3/00',  # Atividades de organizações associativas
        '9500-6/00',  # Reparação e manutenção de equipamentos
        '9600-9/00',  # Outras atividades de serviços pessoais
        '9700-2/00',  # Serviços domésticos
        '9900-8/00',  # Atividades de organizações internacionais
    ]
    
    # Palavras-chave para busca
    PALAVRAS_CHAVE = [
        'supermercado', 'padaria', 'academia', 'clínica', 'frigorífico',
        'restaurante', 'hotel', 'pousada', 'farmácia', 'loja',
        'shopping', 'centro comercial', 'indústria', 'fábrica', 'armazém'
    ]
    
    # Cidades para busca inicial
    CIDADES_INICIAIS = [
        'São Paulo, SP',
        'Rio de Janeiro, RJ',
        'Belo Horizonte, MG',
        'Brasília, DF',
        'Salvador, BA'
    ]
