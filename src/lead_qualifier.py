"""
Módulo para qualificação automática dos leads
"""
import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
import requests
from config import Config

logger = logging.getLogger(__name__)

class LeadQualifier:
    """Classe para qualificação automática dos leads"""
    
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def qualify_lead(self, lead: Dict) -> Dict:
        """
        Qualifica um lead individual aplicando critérios automáticos
        """
        try:
            qualified_lead = lead.copy()
            
            # Aplica critérios de qualificação
            score = 0
            criterios_atingidos = []
            
            # Critério 1: Tem telefone ativo (+1 ponto)
            if self._has_valid_phone(lead):
                score += 1
                criterios_atingidos.append("Telefone válido")
            
            # Critério 2: Tem site ativo (+1 ponto)
            if self._has_valid_website(lead):
                score += 1
                criterios_atingidos.append("Site ativo")
            
            # Critério 3: CNAE compatível (+2 pontos)
            if self._has_compatible_cnae(lead):
                score += 2
                criterios_atingidos.append("CNAE compatível")
            
            # Critério 4: Tem WhatsApp ou Instagram (+1 ponto)
            if self._has_social_media(lead):
                score += 1
                criterios_atingidos.append("Mídia social")
            
            # Critério 5: Endereço válido (+1 ponto)
            if self._has_valid_address(lead):
                score += 1
                criterios_atingidos.append("Endereço válido")
            
            # Critério 6: Nome da empresa válido (+1 ponto)
            if self._has_valid_company_name(lead):
                score += 1
                criterios_atingidos.append("Nome válido")
            
            # Adiciona informações de qualificação
            qualified_lead.update({
                'score': score,
                'criterios_atingidos': criterios_atingidos,
                'qualificado': score >= 3,  # Mínimo 3 pontos para ser qualificado
                'nivel_qualificacao': self._get_qualification_level(score),
                'data_qualificacao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'observacoes_qualificacao': self._generate_qualification_notes(score, criterios_atingidos)
            })
            
            logger.info(f"Lead '{lead.get('nome', 'N/A')}' qualificado com score {score}")
            
            return qualified_lead
            
        except Exception as e:
            logger.error(f"Erro ao qualificar lead: {e}")
            return lead
    
    def qualify_leads_batch(self, leads: List[Dict]) -> List[Dict]:
        """
        Qualifica uma lista de leads em lote
        """
        qualified_leads = []
        
        logger.info(f"Iniciando qualificação de {len(leads)} leads")
        
        for i, lead in enumerate(leads):
            try:
                qualified_lead = self.qualify_lead(lead)
                qualified_leads.append(qualified_lead)
                
                # Log de progresso
                if (i + 1) % 10 == 0:
                    logger.info(f"Qualificados {i + 1}/{len(leads)} leads")
                
            except Exception as e:
                logger.error(f"Erro ao qualificar lead {i + 1}: {e}")
                qualified_leads.append(lead)  # Adiciona lead não qualificado
        
        # Estatísticas da qualificação
        total_qualified = sum(1 for lead in qualified_leads if lead.get('qualificado', False))
        avg_score = sum(lead.get('score', 0) for lead in qualified_leads) / len(qualified_leads)
        
        logger.info(f"Qualificação concluída: {total_qualified}/{len(qualified_leads)} leads qualificados")
        logger.info(f"Score médio: {avg_score:.2f}")
        
        return qualified_leads
    
    def _has_valid_phone(self, lead: Dict) -> bool:
        """Verifica se o lead tem telefone válido"""
        phone = lead.get('telefone', '')
        if not phone:
            return False
        
        # Remove caracteres especiais e espaços
        phone_clean = re.sub(r'[^\d]', '', phone)
        
        # Telefone deve ter pelo menos 10 dígitos (DDD + número)
        return len(phone_clean) >= 10
    
    def _has_valid_website(self, lead: Dict) -> bool:
        """Verifica se o lead tem site válido"""
        website = lead.get('website', '')
        if not website:
            return False
        
        # Verifica formato básico de URL
        if not re.match(r'^https?://', website):
            return False
        
        # Tenta fazer requisição para verificar se o site está ativo
        try:
            response = self.session.head(website, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _has_compatible_cnae(self, lead: Dict) -> bool:
        """Verifica se o CNAE é compatível com alto consumo de energia"""
        cnae = lead.get('cnae', '')
        if not cnae:
            return False
        
        # Remove caracteres especiais
        cnae_clean = re.sub(r'[^\d]', '', cnae)
        
        # Verifica se está na lista de CNAEs de alto consumo
        for cnae_alto in self.config.CNAES_ALTO_CONSUMO:
            cnae_alto_clean = re.sub(r'[^\d]', '', cnae_alto)
            if cnae_clean.startswith(cnae_alto_clean[:4]):  # Primeiros 4 dígitos
                return True
        
        return False
    
    def _has_social_media(self, lead: Dict) -> bool:
        """Verifica se o lead tem mídia social"""
        # Verifica Instagram
        if lead.get('instagram'):
            return True
        
        # Verifica WhatsApp
        whatsapp = lead.get('whatsapp', '')
        if whatsapp and ('whatsapp' in whatsapp.lower() or 'wa.me' in whatsapp):
            return True
        
        return False
    
    def _has_valid_address(self, lead: Dict) -> bool:
        """Verifica se o lead tem endereço válido"""
        address = lead.get('endereco', '')
        if not address:
            return False
        
        # Endereço deve ter pelo menos 20 caracteres e conter elementos básicos
        if len(address) < 20:
            return False
        
        # Deve conter pelo menos uma vírgula (separador comum em endereços)
        if ',' not in address:
            return False
        
        return True
    
    def _has_valid_company_name(self, lead: Dict) -> bool:
        """Verifica se o nome da empresa é válido"""
        name = lead.get('nome', '')
        if not name:
            return False
        
        # Nome deve ter pelo menos 3 caracteres
        if len(name) < 3:
            return False
        
        # Não deve ser apenas números
        if name.isdigit():
            return False
        
        # Não deve conter palavras comuns que indicam dados inválidos
        invalid_words = ['n/a', 'null', 'undefined', 'sem nome', 'sem título']
        if any(word in name.lower() for word in invalid_words):
            return False
        
        return True
    
    def _get_qualification_level(self, score: int) -> str:
        """Retorna o nível de qualificação baseado no score"""
        if score >= 5:
            return "Alto"
        elif score >= 3:
            return "Médio"
        elif score >= 1:
            return "Baixo"
        else:
            return "Não qualificado"
    
    def _generate_qualification_notes(self, score: int, criterios: List[str]) -> str:
        """Gera observações sobre a qualificação"""
        if score >= 5:
            return f"Lead altamente qualificado! Critérios atingidos: {', '.join(criterios)}"
        elif score >= 3:
            return f"Lead qualificado. Critérios atingidos: {', '.join(criterios)}"
        elif score >= 1:
            return f"Lead com baixa qualificação. Critérios atingidos: {', '.join(criterios)}"
        else:
            return "Lead não qualificado. Nenhum critério atendido."
    
    def enrich_lead_with_cnpj(self, lead: Dict) -> Dict:
        """
        Enriquece o lead com informações da Receita Federal
        """
        try:
            # Busca CNPJ se não existir
            if not lead.get('cnpj'):
                # Tenta extrair CNPJ do nome ou endereço (implementação básica)
                cnpj = self._extract_cnpj_from_text(lead.get('nome', '') + ' ' + lead.get('endereco', ''))
                if cnpj:
                    lead['cnpj'] = cnpj
            
            # Se tem CNPJ, busca informações da Receita
            if lead.get('cnpj'):
                receita_info = self._get_receita_info(lead['cnpj'])
                if receita_info:
                    lead.update(receita_info)
                    logger.info(f"Lead '{lead.get('nome')}' enriquecido com dados da Receita")
            
            return lead
            
        except Exception as e:
            logger.error(f"Erro ao enriquecer lead: {e}")
            return lead
    
    def _extract_cnpj_from_text(self, text: str) -> Optional[str]:
        """Extrai CNPJ de um texto"""
        # Padrão de CNPJ: XX.XXX.XXX/XXXX-XX
        cnpj_pattern = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
        match = re.search(cnpj_pattern, text)
        
        if match:
            return match.group()
        
        # Padrão sem pontuação: XXXXXXXXXXXXXX
        cnpj_pattern_clean = r'\d{14}'
        match = re.search(cnpj_pattern_clean, text)
        
        if match:
            cnpj = match.group()
            # Formata o CNPJ
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        
        return None
    
    def _get_receita_info(self, cnpj: str) -> Optional[Dict]:
        """
        Busca informações da Receita Federal
        """
        try:
            # Remove caracteres especiais
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
            
            # API pública da Receita
            url = f"https://receitaws.com.br/v1/cnpj/{cnpj_limpo}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ERROR':
                return None
            
            return {
                'razao_social': data.get('nome', ''),
                'nome_fantasia': data.get('fantasia', ''),
                'cnae': data.get('atividade_principal', [{}])[0].get('code', ''),
                'descricao_cnae': data.get('atividade_principal', [{}])[0].get('text', ''),
                'situacao': data.get('situacao', ''),
                'data_abertura': data.get('abertura', ''),
                'porte': data.get('porte', ''),
                'capital_social': data.get('capital_social', ''),
                'quadro_socios': data.get('qsa', [])
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar CNPJ {cnpj}: {e}")
            return None
    
    def generate_qualification_report(self, leads: List[Dict]) -> Dict:
        """
        Gera relatório de qualificação dos leads
        """
        try:
            total_leads = len(leads)
            qualified_leads = sum(1 for lead in leads if lead.get('qualificado', False))
            unqualified_leads = total_leads - qualified_leads
            
            # Distribuição por score
            score_distribution = {}
            for lead in leads:
                score = lead.get('score', 0)
                score_distribution[score] = score_distribution.get(score, 0) + 1
            
            # Distribuição por nível de qualificação
            level_distribution = {}
            for lead in leads:
                level = lead.get('nivel_qualificacao', 'Não qualificado')
                level_distribution[level] = level_distribution.get(level, 0) + 1
            
            # Critérios mais atingidos
            criterios_count = {}
            for lead in leads:
                for criterio in lead.get('criterios_atingidos', []):
                    criterios_count[criterio] = criterios_count.get(criterio, 0) + 1
            
            # Top critérios
            top_criterios = sorted(criterios_count.items(), key=lambda x: x[1], reverse=True)[:5]
            
            report = {
                'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'total_leads': total_leads,
                'leads_qualificados': qualified_leads,
                'leads_nao_qualificados': unqualified_leads,
                'taxa_qualificacao': (qualified_leads / total_leads * 100) if total_leads > 0 else 0,
                'score_medio': sum(lead.get('score', 0) for lead in leads) / total_leads if total_leads > 0 else 0,
                'score_distribuicao': score_distribution,
                'nivel_distribuicao': level_distribution,
                'top_criterios': top_criterios,
                'resumo': f"De {total_leads} leads, {qualified_leads} foram qualificados ({qualified_leads/total_leads*100:.1f}%)"
            }
            
            logger.info(f"Relatório de qualificação gerado: {report['resumo']}")
            
            return report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return {}

if __name__ == "__main__":
    # Exemplo de uso
    qualifier = LeadQualifier()
    
    # Lead de exemplo
    sample_lead = {
        'nome': 'Supermercado Exemplo',
        'telefone': '(11) 99999-9999',
        'website': 'https://www.exemplo.com.br',
        'endereco': 'Rua das Flores, 123, Centro, São Paulo, SP',
        'cnae': '4721-1/01'
    }
    
    # Qualifica o lead
    qualified_lead = qualifier.qualify_lead(sample_lead)
    print(f"Lead qualificado: {qualified_lead}")
    
    # Gera relatório
    report = qualifier.generate_qualification_report([qualified_lead])
    print(f"Relatório: {report}")
