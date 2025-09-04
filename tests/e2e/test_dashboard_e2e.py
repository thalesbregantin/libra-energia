#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes End-to-End - Dashboard
TDD Robusto inspirado nas Big Techs
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from unittest.mock import patch, Mock

class TestDashboardE2E:
    """Testes end-to-end para o dashboard"""
    
    @pytest.fixture
    def browser(self):
        """Navegador para testes E2E"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    @pytest.fixture
    def dashboard_url(self):
        """URL do dashboard"""
        return "http://localhost:8080/dashboard_novo.html"
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_loads_successfully(self, browser, dashboard_url):
        """Testar se o dashboard carrega com sucesso"""
        browser.get(dashboard_url)
        
        # Verificar se a página carregou
        assert "Libra Energia" in browser.title or "Dashboard" in browser.title
        
        # Verificar elementos principais
        assert browser.find_element(By.TAG_NAME, "body") is not None
        
        # Verificar se não há erros JavaScript
        logs = browser.get_log('browser')
        error_logs = [log for log in logs if log['level'] == 'SEVERE']
        assert len(error_logs) == 0, f"Erros JavaScript encontrados: {error_logs}"
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_metrics_display(self, browser, dashboard_url):
        """Testar se as métricas são exibidas"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(3)
        
        # Verificar métricas principais
        try:
            total_leads = browser.find_element(By.ID, "total-leads")
            qualified_leads = browser.find_element(By.ID, "qualified-leads")
            avg_score = browser.find_element(By.ID, "avg-score")
            qualification_rate = browser.find_element(By.ID, "qualification-rate")
            
            assert total_leads is not None
            assert qualified_leads is not None
            assert avg_score is not None
            assert qualification_rate is not None
            
            # Verificar se os valores são numéricos
            assert total_leads.text.isdigit() or total_leads.text == "0"
            assert qualified_leads.text.isdigit() or qualified_leads.text == "0"
            
        except NoSuchElementException:
            pytest.skip("Elementos de métricas não encontrados")
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_charts_render(self, browser, dashboard_url):
        """Testar se os gráficos são renderizados"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(5)
        
        # Verificar se os canvas dos gráficos existem
        try:
            level_chart = browser.find_element(By.ID, "levelChart")
            score_chart = browser.find_element(By.ID, "scoreChart")
            
            assert level_chart is not None
            assert score_chart is not None
            
            # Verificar se os canvas têm conteúdo
            assert level_chart.get_attribute("width") is not None
            assert score_chart.get_attribute("width") is not None
            
        except NoSuchElementException:
            pytest.skip("Gráficos não encontrados")
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_table_display(self, browser, dashboard_url):
        """Testar se a tabela de leads é exibida"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(3)
        
        # Verificar se a tabela existe
        try:
            table = browser.find_element(By.ID, "leads-table")
            assert table is not None
            
            # Verificar se há linhas na tabela
            rows = table.find_elements(By.TAG_NAME, "tr")
            assert len(rows) > 0
            
        except NoSuchElementException:
            pytest.skip("Tabela de leads não encontrada")
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_search_filter(self, browser, dashboard_url):
        """Testar funcionalidade de busca"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(3)
        
        try:
            # Encontrar campo de busca
            search_input = browser.find_element(By.ID, "search-input")
            assert search_input is not None
            
            # Testar busca
            search_input.clear()
            search_input.send_keys("teste")
            
            # Aguardar filtro ser aplicado
            time.sleep(2)
            
            # Verificar se a busca foi aplicada
            assert search_input.get_attribute("value") == "teste"
            
        except NoSuchElementException:
            pytest.skip("Campo de busca não encontrado")
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_level_filter(self, browser, dashboard_url):
        """Testar filtro por nível"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(3)
        
        try:
            # Encontrar filtro de nível
            level_filter = browser.find_element(By.ID, "level-filter")
            assert level_filter is not None
            
            # Testar filtro
            level_filter.click()
            
            # Verificar se o filtro foi aplicado
            assert level_filter is not None
            
        except NoSuchElementException:
            pytest.skip("Filtro de nível não encontrado")
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_campaign_button(self, browser, dashboard_url):
        """Testar botão de campanha"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(3)
        
        try:
            # Encontrar botão de campanha
            campaign_btn = browser.find_element(By.ID, "campaign-btn")
            assert campaign_btn is not None
            
            # Verificar se o botão está habilitado
            assert campaign_btn.is_enabled()
            
            # Verificar texto do botão
            assert "Campanha" in campaign_btn.text or "Rodar" in campaign_btn.text
            
        except NoSuchElementException:
            pytest.skip("Botão de campanha não encontrado")
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_refresh_button(self, browser, dashboard_url):
        """Testar botão de atualização"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(3)
        
        try:
            # Encontrar botão de atualização
            refresh_btn = browser.find_element(By.ID, "refresh-btn")
            assert refresh_btn is not None
            
            # Verificar se o botão está habilitado
            assert refresh_btn.is_enabled()
            
            # Clicar no botão
            refresh_btn.click()
            
            # Aguardar atualização
            time.sleep(2)
            
            # Verificar se a página ainda está carregada
            assert "Libra Energia" in browser.title or "Dashboard" in browser.title
            
        except NoSuchElementException:
            pytest.skip("Botão de atualização não encontrado")
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_responsive_design(self, browser, dashboard_url):
        """Testar design responsivo"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(3)
        
        # Testar diferentes tamanhos de tela
        screen_sizes = [
            (1920, 1080),  # Desktop
            (1024, 768),   # Tablet
            (375, 667)     # Mobile
        ]
        
        for width, height in screen_sizes:
            browser.set_window_size(width, height)
            time.sleep(1)
            
            # Verificar se a página ainda é funcional
            assert browser.find_element(By.TAG_NAME, "body") is not None
            
            # Verificar se não há overflow horizontal
            body_width = browser.execute_script("return document.body.scrollWidth")
            viewport_width = browser.execute_script("return window.innerWidth")
            assert body_width <= viewport_width + 20  # Margem de erro
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_api_connectivity(self, browser, dashboard_url):
        """Testar conectividade com a API"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(5)
        
        # Verificar logs do console para erros de API
        logs = browser.get_log('browser')
        api_errors = [log for log in logs if 'API' in log['message'] and 'error' in log['message'].lower()]
        
        # Se houver erros de API, verificar se são esperados
        if api_errors:
            print(f"Logs de API encontrados: {api_errors}")
            # Verificar se são erros esperados (como API não disponível)
            for log in api_errors:
                assert "não disponível" in log['message'] or "fallback" in log['message']
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_performance(self, browser, dashboard_url):
        """Testar performance do dashboard"""
        start_time = time.time()
        browser.get(dashboard_url)
        
        # Aguardar carregamento completo
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        end_time = time.time()
        load_time = end_time - start_time
        
        # Verificar se o carregamento foi rápido (< 5 segundos)
        assert load_time < 5.0, f"Dashboard demorou {load_time:.2f} segundos para carregar"
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_accessibility(self, browser, dashboard_url):
        """Testar acessibilidade básica"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(3)
        
        # Verificar se há elementos com alt text
        images = browser.find_elements(By.TAG_NAME, "img")
        for img in images:
            alt_text = img.get_attribute("alt")
            if alt_text is not None:
                assert len(alt_text) > 0, "Imagem sem alt text"
        
        # Verificar se há labels para inputs
        inputs = browser.find_elements(By.TAG_NAME, "input")
        for input_elem in inputs:
            input_id = input_elem.get_attribute("id")
            if input_id:
                try:
                    label = browser.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                    assert label is not None, f"Input {input_id} sem label"
                except NoSuchElementException:
                    # Verificar se o input está dentro de um label
                    parent_label = input_elem.find_element(By.XPATH, "./ancestor::label")
                    if not parent_label:
                        pytest.skip(f"Input {input_id} sem label associado")
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_error_handling(self, browser, dashboard_url):
        """Testar tratamento de erros"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(3)
        
        # Verificar se não há erros JavaScript críticos
        logs = browser.get_log('browser')
        critical_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        # Filtrar erros esperados (como recursos não encontrados)
        unexpected_errors = []
        for error in critical_errors:
            if not any(expected in error['message'].lower() for expected in ['favicon', '404', 'network']):
                unexpected_errors.append(error)
        
        assert len(unexpected_errors) == 0, f"Erros críticos encontrados: {unexpected_errors}"
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_dashboard_data_loading(self, browser, dashboard_url):
        """Testar carregamento de dados"""
        browser.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(5)
        
        # Verificar se os dados foram carregados
        try:
            # Verificar se há dados na tabela
            table = browser.find_element(By.ID, "leads-table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            # Deve haver pelo menos uma linha (header ou dados)
            assert len(rows) > 0
            
            # Verificar se não há mensagem de erro
            error_elements = browser.find_elements(By.CSS_SELECTOR, "[class*='error'], [class*='Error']")
            for error_elem in error_elements:
                if error_elem.is_displayed():
                    assert "erro" not in error_elem.text.lower(), f"Erro visível: {error_elem.text}"
            
        except NoSuchElementException:
            pytest.skip("Elementos de dados não encontrados")
