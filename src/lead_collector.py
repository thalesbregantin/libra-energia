"""
Módulo principal para coleta de leads
"""
import time
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

from config import Config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lead_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LeadCollector:
    """Classe principal para coleta de leads"""
    
    def __init__(self):
        self.config = Config()
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def setup_driver(self):
        """Configura o driver do Selenium"""
        try:
            chrome_options = Options()
            if self.config.HEADLESS_BROWSER:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            logger.info("Driver do Selenium configurado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao configurar driver: {e}")
            raise
    
    def close_driver(self):
        """Fecha o driver do Selenium"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver do Selenium fechado")
    
    def search_google_places(self, keyword: str, city: str, max_results: int = 20) -> List[Dict]:
        """
        Coleta leads usando Google Places API (alias para compatibilidade com testes)
        """
        return self.collect_from_google_places(keyword, city, max_results)
    
    def collect_from_google_places(self, keyword: str, city: str, max_results: int = 20) -> List[Dict]:
        """
        Coleta leads usando Google Places API
        """
        if not self.config.GOOGLE_PLACES_API_KEY:
            logger.warning("API key do Google Places não configurada")
            return []
        
        leads = []
        search_query = f"{keyword} {city}"
        
        try:
            # Busca por texto
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': search_query,
                'key': self.config.GOOGLE_PLACES_API_KEY,
                'language': 'pt-BR',
                'region': 'BR'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'OK':
                logger.warning(f"Status da API não OK: {data['status']}")
                return []
            
            for place in data['results'][:max_results]:
                lead = self._extract_place_data(place)
                if lead:
                    leads.append(lead)
                
                # Busca detalhes adicionais
                if place.get('place_id'):
                    details = self._get_place_details(place['place_id'])
                    if details:
                        lead.update(details)
                
                time.sleep(self.config.SCRAPING_DELAY)
            
            logger.info(f"Coletados {len(leads)} leads para '{search_query}'")
            
        except Exception as e:
            logger.error(f"Erro ao coletar do Google Places: {e}")
        
        return leads
    
    def _process_google_places_results(self, places: List[Dict]) -> List[Dict]:
        """Processa resultados da API do Google Places para compatibilidade com testes"""
        leads = []
        for place in places:
            lead = self._extract_place_data(place)
            if lead:
                leads.append(lead)
        return leads
    
    def _extract_place_data(self, place: Dict) -> Optional[Dict]:
        """Extrai dados básicos de um lugar"""
        try:
            return {
                'nome': place.get('name', ''),
                'endereco': place.get('formatted_address', ''),
                'telefone': '',
                'website': '',
                'categoria': place.get('types', []),
                'nota': place.get('rating', 0),
                'reviews': place.get('user_ratings_total', 0),
                'latitude': place.get('geometry', {}).get('location', {}).get('lat', 0),
                'longitude': place.get('geometry', {}).get('location', {}).get('lng', 0),
                'place_id': place.get('place_id', ''),
                'fonte': 'Google Places',
                'data_coleta': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Erro ao extrair dados do lugar: {e}")
            return None
    
    def _get_place_details(self, place_id: str) -> Optional[Dict]:
        """Busca detalhes adicionais de um lugar"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                'place_id': place_id,
                'key': self.config.GOOGLE_PLACES_API_KEY,
                'fields': 'formatted_phone_number,website,opening_hours,price_level',
                'language': 'pt-BR'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'OK':
                return None
            
            result = data.get('result', {})
            return {
                'telefone': result.get('formatted_phone_number', ''),
                'website': result.get('website', ''),
                'horario_funcionamento': result.get('opening_hours', {}).get('weekday_text', []),
                'nivel_preco': result.get('price_level', 0)
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes do lugar: {e}")
            return None
    
    def collect_from_instagram(self, hashtag: str, max_results: int = 50) -> List[Dict]:
        """
        Coleta leads do Instagram (requer login)
        """
        if not self.driver:
            self.setup_driver()
        
        leads = []
        
        try:
            # Navega para a hashtag
            url = f"https://www.instagram.com/explore/tags/{hashtag}/"
            self.driver.get(url)
            time.sleep(3)
            
            # Aceita cookies se necessário
            try:
                cookie_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceitar')]"))
                )
                cookie_button.click()
                time.sleep(2)
            except:
                pass
            
            # Rola para carregar mais posts
            for _ in range(max_results // 12):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extrai dados dos posts
            posts = self.driver.find_elements(By.CSS_SELECTOR, "article a")
            
            for post in posts[:max_results]:
                try:
                    href = post.get_attribute('href')
                    if href and '/p/' in href:
                        lead = self._extract_instagram_post_data(href)
                        if lead:
                            leads.append(lead)
                        time.sleep(self.config.SCRAPING_DELAY)
                except Exception as e:
                    logger.error(f"Erro ao processar post do Instagram: {e}")
            
            logger.info(f"Coletados {len(leads)} leads do Instagram para #{hashtag}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar do Instagram: {e}")
        
        return leads
    
    def _extract_instagram_post_data(self, post_url: str) -> Optional[Dict]:
        """Extrai dados de um post do Instagram"""
        try:
            self.driver.get(post_url)
            time.sleep(2)
            
            # Extrai informações do perfil
            profile_link = self.driver.find_element(By.CSS_SELECTOR, "header a")
            profile_url = profile_link.get_attribute('href')
            profile_name = profile_link.text
            
            # Navega para o perfil
            self.driver.get(profile_url)
            time.sleep(2)
            
            # Extrai bio e informações
            try:
                bio_element = self.driver.find_element(By.CSS_SELECTOR, "div[data-testid='user-bio']")
                bio = bio_element.text
            except:
                bio = ""
            
            # Busca por links na bio
            website = ""
            whatsapp = ""
            if bio:
                if "http" in bio:
                    website = bio.split("http")[1].split()[0]
                    website = "http" + website
                if "whatsapp" in bio.lower() or "wa.me" in bio.lower():
                    whatsapp = bio
            
            return {
                'nome': profile_name,
                'instagram': profile_url,
                'bio': bio,
                'website': website,
                'whatsapp': whatsapp,
                'fonte': 'Instagram',
                'data_coleta': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do post: {e}")
            return None
    
    def collect_from_receita_ws(self, cnpj: str) -> Optional[Dict]:
        """
        Busca informações da Receita Federal (API pública)
        """
        try:
            # Remove caracteres especiais
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
            
            # API pública da Receita
            url = f"https://receitaws.com.br/v1/cnpj/{cnpj_limpo}"
            
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ERROR':
                logger.warning(f"CNPJ {cnpj} não encontrado ou erro na API")
                return None
            
            return {
                'cnpj': cnpj_limpo,
                'razao_social': data.get('nome', ''),
                'nome_fantasia': data.get('fantasia', ''),
                'cnae': data.get('atividade_principal', [{}])[0].get('code', ''),
                'descricao_cnae': data.get('atividade_principal', [{}])[0].get('text', ''),
                'endereco_receita': {
                    'logradouro': data.get('logradouro', ''),
                    'numero': data.get('numero', ''),
                    'complemento': data.get('complemento', ''),
                    'bairro': data.get('bairro', ''),
                    'municipio': data.get('municipio', ''),
                    'uf': data.get('uf', ''),
                    'cep': data.get('cep', '')
                },
                'situacao': data.get('situacao', ''),
                'data_abertura': data.get('abertura', ''),
                'porte': data.get('porte', ''),
                'fonte': 'Receita Federal',
                'data_coleta': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar CNPJ {cnpj}: {e}")
            return None
    
    def run_collection_campaign(self, keywords: List[str] = None, cities: List[str] = None) -> List[Dict]:
        """
        Executa campanha completa de coleta
        """
        if not keywords:
            keywords = self.config.PALAVRAS_CHAVE[:5]  # Primeiras 5 palavras-chave
        
        if not cities:
            cities = self.config.CIDADES_INICIAIS[:1]  # Primeira cidade para teste
        
        all_leads = []
        
        logger.info(f"Iniciando campanha de coleta com {len(keywords)} keywords e {len(cities)} cidades")
        
        for city in cities:
            for keyword in keywords:
                logger.info(f"Coletando leads para '{keyword}' em {city}")
                
                # Coleta do Google Places
                leads_places = self.collect_from_google_places(keyword, city, max_results=20)
                all_leads.extend(leads_places)
                
                # Coleta do Instagram (opcional)
                try:
                    hashtag = f"{keyword.replace(' ', '')}{city.split(',')[0].lower()}"
                    leads_instagram = self.collect_from_instagram(hashtag, max_results=10)
                    all_leads.extend(leads_instagram)
                except Exception as e:
                    logger.warning(f"Instagram não disponível para {keyword}: {e}")
                
                time.sleep(self.config.SCRAPING_DELAY * 2)
        
        # Remove duplicatas
        unique_leads = self._remove_duplicates(all_leads)
        
        logger.info(f"Campanha concluída. Total de leads únicos: {len(unique_leads)}")
        
        return unique_leads
    
    def _remove_duplicates(self, leads: List[Dict]) -> List[Dict]:
        """Remove leads duplicados baseado no nome e endereço"""
        seen = set()
        unique_leads = []
        
        for lead in leads:
            # Cria chave única baseada no nome e endereço
            key = f"{lead.get('nome', '')}_{lead.get('endereco', '')}"
            
            if key not in seen:
                seen.add(key)
                unique_leads.append(lead)
        
        return unique_leads
    
    def save_leads_to_csv(self, leads: List[Dict], filename: str = None):
        """Salva leads em arquivo CSV"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"leads_coletados_{timestamp}.csv"
        
        try:
            df = pd.DataFrame(leads)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"Leads salvos em {filename}")
            return filename
        except Exception as e:
            logger.error(f"Erro ao salvar CSV: {e}")
            return None
    
    def save_leads_to_json(self, leads: List[Dict], filename: str = None):
        """Salva leads em arquivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"leads_coletados_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(leads, f, ensure_ascii=False, indent=2)
            logger.info(f"Leads salvos em {filename}")
            return filename
        except Exception as e:
            logger.error(f"Erro ao salvar JSON: {e}")
            return None

if __name__ == "__main__":
    # Exemplo de uso
    collector = LeadCollector()
    
    try:
        # Executa campanha de teste
        leads = collector.run_collection_campaign(
            keywords=['supermercado', 'padaria'],
            cities=['São Paulo, SP']
        )
        
        # Salva resultados
        collector.save_leads_to_csv(leads)
        collector.save_leads_to_json(leads)
        
        print(f"Coleta concluída! {len(leads)} leads coletados.")
        
    except Exception as e:
        logger.error(f"Erro na execução: {e}")
    finally:
        collector.close_driver()
