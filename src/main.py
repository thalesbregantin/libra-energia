"""
Módulo principal do sistema de automação de prospecção
Orquestra todo o processo: coleta, qualificação e armazenamento
"""
import logging
import time
from typing import List, Dict
from datetime import datetime
import argparse
import json

from lead_collector import LeadCollector
from lead_qualifier import LeadQualifier
from sheets_manager import GoogleSheetsManager
from config import Config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('prospeccao_automatica.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProspeccaoAutomatica:
    """Classe principal que orquestra todo o processo de prospecção"""
    
    def __init__(self):
        self.config = Config()
        self.collector = LeadCollector()
        self.qualifier = LeadQualifier()
        self.sheets_manager = GoogleSheetsManager()
        
        # Estatísticas da execução
        self.stats = {
            'inicio_execucao': None,
            'fim_execucao': None,
            'leads_coletados': 0,
            'leads_qualificados': 0,
            'leads_armazenados': 0,
            'erros': [],
            'tempo_total': 0
        }
    
    def executar_campanha_completa(self, 
                                  keywords: List[str] = None,
                                  cities: List[str] = None,
                                  max_leads_por_busca: int = 20,
                                  usar_google_sheets: bool = True) -> Dict:
        """
        Executa campanha completa de prospecção
        """
        start_time = time.time()
        self.stats['inicio_execucao'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        logger.info("Iniciando campanha completa de prospecção automática")
        
        try:
            # Etapa 1: Coleta de leads
            logger.info("Etapa 1: Coletando leads...")
            leads_coletados = self._coletar_leads(keywords, cities, max_leads_por_busca)
            
            if not leads_coletados:
                logger.warning("Nenhum lead foi coletado")
                return self._finalizar_execucao(start_time)
            
            # Etapa 2: Qualificação automática
            logger.info("Etapa 2: Qualificando leads...")
            leads_qualificados = self._qualificar_leads(leads_coletados)
            
            # Etapa 3: Armazenamento
            logger.info("Etapa 3: Armazenando leads...")
            if usar_google_sheets:
                leads_armazenados = self._armazenar_leads_sheets(leads_qualificados)
            else:
                leads_armazenados = self._armazenar_leads_local(leads_qualificados)
            
            # Etapa 4: Geração de relatório
            logger.info("Etapa 4: Gerando relatório...")
            relatorio = self._gerar_relatorio_final(leads_qualificados)
            
            # Finaliza execução
            return self._finalizar_execucao(start_time, relatorio)
            
        except Exception as e:
            error_msg = f"Erro na execução da campanha: {e}"
            logger.error(error_msg)
            self.stats['erros'].append(error_msg)
            return self._finalizar_execucao(start_time)
    
    def _coletar_leads(self, keywords: List[str], cities: List[str], max_leads: int) -> List[Dict]:
        """
        Coleta leads usando múltiplas fontes
        """
        try:
            # Usa configurações padrão se não fornecidas
            if not keywords:
                keywords = self.config.PALAVRAS_CHAVE[:5]  # Primeiras 5 palavras-chave
            
            if not cities:
                cities = self.config.CIDADES_INICIAIS[:1]  # Primeira cidade para teste
            
            logger.info(f"Coletando leads para {len(keywords)} keywords em {len(cities)} cidades")
            
            # Executa campanha de coleta
            leads = self.collector.run_collection_campaign(
                keywords=keywords,
                cities=cities
            )
            
            self.stats['leads_coletados'] = len(leads)
            logger.info(f"Coleta concluída: {len(leads)} leads coletados")
            
            return leads
            
        except Exception as e:
            error_msg = f"Erro na coleta de leads: {e}"
            logger.error(error_msg)
            self.stats['erros'].append(error_msg)
            return []
    
    def _qualificar_leads(self, leads: List[Dict]) -> List[Dict]:
        """
        Qualifica leads automaticamente
        """
        try:
            logger.info(f"Qualificando {len(leads)} leads...")
            
            # Qualifica leads em lote
            leads_qualificados = self.qualifier.qualify_leads_batch(leads)
            
            # Enriquece com dados da Receita (opcional)
            logger.info("Enriquecendo leads com dados da Receita...")
            for i, lead in enumerate(leads_qualificados):
                try:
                    lead_enriquecido = self.qualifier.enrich_lead_with_cnpj(lead)
                    leads_qualificados[i] = lead_enriquecido
                    
                    # Log de progresso
                    if (i + 1) % 10 == 0:
                        logger.info(f"Enriquecidos {i + 1}/{len(leads_qualificados)} leads")
                        
                except Exception as e:
                    logger.warning(f"Erro ao enriquecer lead {i + 1}: {e}")
                
                # Delay para evitar sobrecarga da API da Receita
                time.sleep(0.5)
            
            self.stats['leads_qualificados'] = len(leads_qualificados)
            logger.info(f"Qualificação concluída: {len(leads_qualificados)} leads processados")
            
            return leads_qualificados
            
        except Exception as e:
            error_msg = f"Erro na qualificação de leads: {e}"
            logger.error(error_msg)
            self.stats['erros'].append(error_msg)
            return leads
    
    def _armazenar_leads_sheets(self, leads: List[Dict]) -> int:
        """
        Armazena leads no Google Sheets
        """
        try:
            logger.info("Autenticando com Google Sheets...")
            
            # Autentica com Google Sheets
            if not self.sheets_manager.authenticate():
                raise Exception("Falha na autenticação com Google Sheets")
            
            # Abre planilha
            if not self.sheets_manager.open_spreadsheet():
                raise Exception("Falha ao abrir planilha")
            
            # Cria/abre planilha de trabalho
            if not self.sheets_manager.create_or_open_worksheet("Leads"):
                raise Exception("Falha ao criar/abrir planilha de trabalho")
            
            # Adiciona leads em lote
            logger.info(f"Armazenando {len(leads)} leads no Google Sheets...")
            leads_armazenados = self.sheets_manager.add_leads_batch(leads)
            
            self.stats['leads_armazenados'] = leads_armazenados
            logger.info(f"Armazenamento concluído: {leads_armazenados} leads salvos")
            
            return leads_armazenados
            
        except Exception as e:
            error_msg = f"Erro no armazenamento no Google Sheets: {e}"
            logger.error(error_msg)
            self.stats['erros'].append(error_msg)
            
            # Fallback para armazenamento local
            logger.info("Fallback para armazenamento local...")
            return self._armazenar_leads_local(leads)
    
    def _armazenar_leads_local(self, leads: List[Dict]) -> int:
        """
        Armazena leads localmente (fallback)
        """
        try:
            logger.info(f"Armazenando {len(leads)} leads localmente...")
            
            # Salva em CSV
            csv_file = self.collector.save_leads_to_csv(leads)
            
            # Salva em JSON
            json_file = self.collector.save_leads_to_json(leads)
            
            self.stats['leads_armazenados'] = len(leads)
            logger.info(f"Armazenamento local concluído: {len(leads)} leads salvos")
            logger.info(f"Arquivos: {csv_file}, {json_file}")
            
            return len(leads)
            
        except Exception as e:
            error_msg = f"Erro no armazenamento local: {e}"
            logger.error(error_msg)
            self.stats['erros'].append(error_msg)
            return 0
    
    def _gerar_relatorio_final(self, leads: List[Dict]) -> Dict:
        """
        Gera relatório final da campanha
        """
        try:
            logger.info("Gerando relatório final...")
            
            # Relatório de qualificação
            relatorio_qualificacao = self.qualifier.generate_qualification_report(leads)
            
            # Estatísticas do Google Sheets (se disponível)
            stats_sheets = {}
            if self.sheets_manager.worksheet:
                try:
                    stats_sheets = self.sheets_manager.get_statistics()
                except Exception as e:
                    logger.warning(f"Erro ao obter estatísticas do Sheets: {e}")
            
            # Relatório consolidado
            relatorio = {
                'campanha': {
                    'data_inicio': self.stats['inicio_execucao'],
                    'data_fim': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'keywords_utilizadas': self.config.PALAVRAS_CHAVE[:5],
                    'cidades_utilizadas': self.config.CIDADES_INICIAIS[:1]
                },
                'resultados': {
                    'leads_coletados': self.stats['leads_coletados'],
                    'leads_qualificados': self.stats['leads_qualificados'],
                    'leads_armazenados': self.stats['leads_armazenados'],
                    'taxa_qualificacao': (self.stats['leads_qualificados'] / self.stats['leads_coletados'] * 100) if self.stats['leads_coletados'] > 0 else 0
                },
                'qualificacao': relatorio_qualificacao,
                'sheets_stats': stats_sheets,
                'erros': self.stats['erros'],
                'resumo': f"Campanha executada com sucesso! {self.stats['leads_qualificados']}/{self.stats['leads_coletados']} leads qualificados"
            }
            
            # Salva relatório
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            relatorio_file = f"relatorio_campanha_{timestamp}.json"
            
            with open(relatorio_file, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Relatório salvo em: {relatorio_file}")
            logger.info(f"Resumo: {relatorio['resumo']}")
            
            return relatorio
            
        except Exception as e:
            error_msg = f"Erro na geração do relatório: {e}"
            logger.error(error_msg)
            self.stats['erros'].append(error_msg)
            return {}
    
    def _finalizar_execucao(self, start_time: float, relatorio: Dict = None) -> Dict:
        """
        Finaliza execução e retorna estatísticas
        """
        end_time = time.time()
        self.stats['fim_execucao'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.stats['tempo_total'] = round(end_time - start_time, 2)
        
        # Fecha recursos
        try:
            self.collector.close_driver()
        except:
            pass
        
        # Log final
        logger.info(f"Campanha finalizada em {self.stats['tempo_total']} segundos")
        logger.info(f"Total: {self.stats['leads_coletados']} coletados, {self.stats['leads_qualificados']} qualificados, {self.stats['leads_armazenados']} armazenados")
        
        if self.stats['erros']:
            logger.warning(f"{len(self.stats['erros'])} erros encontrados durante a execução")
        
        return {
            'estatisticas': self.stats,
            'relatorio': relatorio
        }
    
    def executar_teste_rapido(self) -> Dict:
        """
        Executa teste rápido com configurações mínimas
        """
        logger.info("Executando teste rápido...")
        
        return self.executar_campanha_completa(
            keywords=['supermercado', 'padaria'],
            cities=['São Paulo, SP'],
            max_leads_por_busca=5,
            usar_google_sheets=False
        )

def main():
    """
    Função principal com interface de linha de comando
    """
    parser = argparse.ArgumentParser(description='Sistema de Automação de Prospecção')
    parser.add_argument('--teste', action='store_true', help='Executa teste rápido')
    parser.add_argument('--keywords', nargs='+', help='Palavras-chave para busca')
    parser.add_argument('--cidades', nargs='+', help='Cidades para busca')
    parser.add_argument('--max-leads', type=int, default=20, help='Máximo de leads por busca')
    parser.add_argument('--sem-sheets', action='store_true', help='Não usar Google Sheets')
    
    args = parser.parse_args()
    
    # Inicializa sistema
    sistema = ProspeccaoAutomatica()
    
    try:
        if args.teste:
            # Executa teste rápido
            resultado = sistema.executar_teste_rapido()
        else:
            # Executa campanha completa
            resultado = sistema.executar_campanha_completa(
                keywords=args.keywords,
                cities=args.cidades,
                max_leads_por_busca=args.max_leads,
                usar_google_sheets=not args.sem_sheets
            )
        
        # Exibe resultado
        print("\n" + "="*60)
        print("RESULTADO DA CAMPANHA DE PROSPECÇÃO")
        print("="*60)
        print(f"Tempo total: {resultado['estatisticas']['tempo_total']} segundos")
        print(f"Leads coletados: {resultado['estatisticas']['leads_coletados']}")
        print(f"Leads qualificados: {resultado['estatisticas']['leads_qualificados']}")
        print(f"Leads armazenados: {resultado['estatisticas']['leads_armazenados']}")
        
        if resultado['estatisticas']['erros']:
            print(f"Erros: {len(resultado['estatisticas']['erros'])}")
        
        if resultado['relatorio']:
            print(f"Relatório: {resultado['relatorio']['resumo']}")
        
        print("="*60)
        
    except KeyboardInterrupt:
        logger.info("Campanha interrompida pelo usuário")
        print("\nCampanha interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro na execução principal: {e}")
        print(f"\nErro na execução: {e}")

if __name__ == "__main__":
    main()
