"""
Módulo para gerenciar integração com Google Sheets como CRM inicial
"""
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from config import Config

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """Classe para gerenciar integração com Google Sheets"""
    
    def __init__(self):
        self.config = Config()
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        
        # Escopo necessário para Google Sheets
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
    
    def authenticate(self) -> bool:
        """
        Autentica com Google Sheets usando credenciais OAuth2
        """
        try:
            if not self.config.GOOGLE_SHEETS_CREDENTIALS_FILE:
                logger.error("Arquivo de credenciais do Google Sheets não configurado")
                return False
            
            # Carrega credenciais
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.config.GOOGLE_SHEETS_CREDENTIALS_FILE,
                self.scope
            )
            
            # Autentica cliente
            self.client = gspread.authorize(credentials)
            logger.info("Autenticação com Google Sheets realizada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na autenticação com Google Sheets: {e}")
            return False
    
    def open_spreadsheet(self, spreadsheet_id: str = None) -> bool:
        """
        Abre uma planilha específica
        """
        try:
            if not self.client:
                logger.error("Cliente não autenticado")
                return False
            
            # Usa ID da configuração se não fornecido
            if not spreadsheet_id:
                spreadsheet_id = self.config.GOOGLE_SHEETS_SPREADSHEET_ID
            
            if not spreadsheet_id:
                logger.error("ID da planilha não configurado")
                return False
            
            # Abre planilha
            self.spreadsheet = self.client.open_by_key(spreadsheet_id)
            logger.info(f"Planilha '{self.spreadsheet.title}' aberta com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao abrir planilha: {e}")
            return False
    
    def create_or_open_worksheet(self, worksheet_name: str = "Leads") -> bool:
        """
        Cria ou abre uma planilha de trabalho
        """
        try:
            if not self.spreadsheet:
                logger.error("Planilha não aberta")
                return False
            
            # Tenta abrir planilha existente
            try:
                self.worksheet = self.spreadsheet.worksheet(worksheet_name)
                logger.info(f"Planilha '{worksheet_name}' aberta")
            except gspread.WorksheetNotFound:
                # Cria nova planilha se não existir
                self.worksheet = self.spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=1000,
                    cols=20
                )
                logger.info(f"Planilha '{worksheet_name}' criada")
                
                # Configura cabeçalhos
                self._setup_headers()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar/abrir planilha: {e}")
            return False
    
    def _setup_headers(self):
        """
        Configura cabeçalhos da planilha
        """
        try:
            headers = [
                'ID',
                'Nome da Empresa',
                'CNPJ',
                'Telefone',
                'WhatsApp',
                'E-mail',
                'Website',
                'Instagram',
                'Endereço',
                'Cidade',
                'Estado',
                'CNAE',
                'Descrição CNAE',
                'Score',
                'Status',
                'Fonte',
                'Data Coleta',
                'Data Qualificação',
                'Observações',
                'Última Atualização'
            ]
            
            # Insere cabeçalhos
            self.worksheet.update('A1:T1', [headers])
            
            # Formata cabeçalhos (negrito)
            self.worksheet.format('A1:T1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
            })
            
            logger.info("Cabeçalhos configurados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar cabeçalhos: {e}")
    
    def add_lead(self, lead: Dict) -> bool:
        """
        Adiciona um lead à planilha
        """
        try:
            if not self.worksheet:
                logger.error("Planilha de trabalho não aberta")
                return False
            
            # Prepara dados do lead
            lead_data = self._prepare_lead_data(lead)
            
            # Adiciona à planilha
            self.worksheet.append_row(lead_data)
            
            logger.info(f"Lead '{lead.get('nome', 'N/A')}' adicionado à planilha")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar lead: {e}")
            return False
    
    def add_leads_batch(self, leads: List[Dict]) -> int:
        """
        Adiciona múltiplos leads em lote
        """
        if not self.worksheet:
            logger.error("Planilha de trabalho não aberta")
            return 0
        
        try:
            # Prepara dados de todos os leads
            leads_data = []
            for lead in leads:
                lead_data = self._prepare_lead_data(lead)
                leads_data.append(lead_data)
            
            # Adiciona em lote
            if leads_data:
                self.worksheet.append_rows(leads_data)
                logger.info(f"{len(leads_data)} leads adicionados em lote")
                return len(leads_data)
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao adicionar leads em lote: {e}")
            return 0
    
    def _prepare_lead_data(self, lead: Dict) -> List:
        """
        Prepara dados do lead para inserção na planilha
        """
        try:
            # Gera ID único baseado no timestamp
            lead_id = f"L{int(datetime.now().timestamp())}"
            
            # Mapeia campos do lead para colunas da planilha
            return [
                lead_id,  # ID
                lead.get('nome', ''),  # Nome da Empresa
                lead.get('cnpj', ''),  # CNPJ
                lead.get('telefone', ''),  # Telefone
                lead.get('whatsapp', ''),  # WhatsApp
                lead.get('email', ''),  # E-mail
                lead.get('website', ''),  # Website
                lead.get('instagram', ''),  # Instagram
                lead.get('endereco', ''),  # Endereço
                self._extract_city(lead.get('endereco', '')),  # Cidade
                self._extract_state(lead.get('endereco', '')),  # Estado
                lead.get('cnae', ''),  # CNAE
                lead.get('descricao_cnae', ''),  # Descrição CNAE
                lead.get('score', 0),  # Score
                self._get_initial_status(lead),  # Status
                lead.get('fonte', ''),  # Fonte
                lead.get('data_coleta', ''),  # Data Coleta
                lead.get('data_qualificacao', ''),  # Data Qualificação
                lead.get('observacoes_qualificacao', ''),  # Observações
                datetime.now().strftime('%d/%m/%Y %H:%M:%S')  # Última Atualização
            ]
            
        except Exception as e:
            logger.error(f"Erro ao preparar dados do lead: {e}")
            return []
    
    def _extract_city(self, address: str) -> str:
        """Extrai cidade do endereço"""
        if not address:
            return ""
        
        # Tenta extrair cidade (última parte antes da vírgula ou após a última vírgula)
        parts = address.split(',')
        if len(parts) >= 2:
            # Pega a penúltima parte (geralmente a cidade)
            city = parts[-2].strip()
            # Remove números e caracteres especiais
            city = ''.join(c for c in city if c.isalpha() or c.isspace()).strip()
            return city
        
        return ""
    
    def _extract_state(self, address: str) -> str:
        """Extrai estado do endereço"""
        if not address:
            return ""
        
        # Tenta extrair estado (última parte após a última vírgula)
        parts = address.split(',')
        if len(parts) >= 1:
            state = parts[-1].strip()
            # Remove números e caracteres especiais, mantém apenas letras
            state = ''.join(c for c in state if c.isalpha()).strip()
            return state
        
        return ""
    
    def _get_initial_status(self, lead: Dict) -> str:
        """Define status inicial do lead baseado na qualificação"""
        if lead.get('qualificado', False):
            return "Qualificado"
        elif lead.get('score', 0) >= 1:
            return "Parcialmente Qualificado"
        else:
            return "Não Qualificado"
    
    def update_lead_status(self, lead_id: str, new_status: str, notes: str = "") -> bool:
        """
        Atualiza status de um lead específico
        """
        try:
            if not self.worksheet:
                logger.error("Planilha de trabalho não aberta")
                return False
            
            # Busca lead pelo ID
            cell = self.worksheet.find(lead_id)
            if not cell:
                logger.warning(f"Lead com ID {lead_id} não encontrado")
                return False
            
            # Atualiza status (coluna O) e observações (coluna S)
            row = cell.row
            self.worksheet.update(f'O{row}', new_status)
            if notes:
                self.worksheet.update(f'S{row}', notes)
            
            # Atualiza última atualização
            self.worksheet.update(f'T{row}', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            
            logger.info(f"Status do lead {lead_id} atualizado para '{new_status}'")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do lead: {e}")
            return False
    
    def get_leads_by_status(self, status: str) -> List[Dict]:
        """
        Busca leads por status
        """
        try:
            if not self.worksheet:
                logger.error("Planilha de trabalho não aberta")
                return []
            
            # Busca todas as linhas
            all_values = self.worksheet.get_all_values()
            if len(all_values) <= 1:  # Apenas cabeçalhos
                return []
            
            # Filtra por status (coluna O)
            status_col = 14  # Coluna O (0-indexed)
            leads = []
            
            for i, row in enumerate(all_values[1:], start=2):  # Pula cabeçalhos
                if len(row) > status_col and row[status_col] == status:
                    lead = self._row_to_lead_dict(row, i)
                    leads.append(lead)
            
            logger.info(f"Encontrados {len(leads)} leads com status '{status}'")
            return leads
            
        except Exception as e:
            logger.error(f"Erro ao buscar leads por status: {e}")
            return []
    
    def _row_to_lead_dict(self, row: List, row_number: int) -> Dict:
        """Converte linha da planilha para dicionário"""
        return {
            'row_number': row_number,
            'id': row[0] if len(row) > 0 else '',
            'nome': row[1] if len(row) > 1 else '',
            'cnpj': row[2] if len(row) > 2 else '',
            'telefone': row[3] if len(row) > 3 else '',
            'whatsapp': row[4] if len(row) > 4 else '',
            'email': row[5] if len(row) > 5 else '',
            'website': row[6] if len(row) > 6 else '',
            'instagram': row[7] if len(row) > 7 else '',
            'endereco': row[8] if len(row) > 8 else '',
            'cidade': row[9] if len(row) > 9 else '',
            'estado': row[10] if len(row) > 10 else '',
            'cnae': row[11] if len(row) > 11 else '',
            'descricao_cnae': row[12] if len(row) > 12 else '',
            'score': int(row[13]) if len(row) > 13 and row[13].isdigit() else 0,
            'status': row[14] if len(row) > 14 else '',
            'fonte': row[15] if len(row) > 15 else '',
            'data_coleta': row[16] if len(row) > 16 else '',
            'data_qualificacao': row[17] if len(row) > 17 else '',
            'observacoes': row[18] if len(row) > 18 else '',
            'ultima_atualizacao': row[19] if len(row) > 19 else ''
        }
    
    def export_to_csv(self, filename: str = None) -> str:
        """
        Exporta dados da planilha para CSV
        """
        try:
            if not self.worksheet:
                logger.error("Planilha de trabalho não aberta")
                return ""
            
            # Busca todos os dados
            all_values = self.worksheet.get_all_values()
            if len(all_values) <= 1:
                logger.warning("Planilha vazia ou apenas com cabeçalhos")
                return ""
            
            # Cria DataFrame
            df = pd.DataFrame(all_values[1:], columns=all_values[0])
            
            # Gera nome do arquivo
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"leads_export_{timestamp}.csv"
            
            # Salva CSV
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"Dados exportados para {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Erro ao exportar para CSV: {e}")
            return ""
    
    def get_statistics(self) -> Dict:
        """
        Gera estatísticas da planilha
        """
        try:
            if not self.worksheet:
                logger.error("Planilha de trabalho não aberta")
                return {}
            
            # Busca todos os dados
            all_values = self.worksheet.get_all_values()
            if len(all_values) <= 1:
                return {'total_leads': 0}
            
            # Conta por status
            status_col = 14  # Coluna O
            status_count = {}
            total_leads = len(all_values) - 1  # Exclui cabeçalhos
            
            for row in all_values[1:]:
                if len(row) > status_col:
                    status = row[status_col] or "Sem Status"
                    status_count[status] = status_count.get(status, 0) + 1
            
            # Calcula score médio
            score_col = 13  # Coluna N
            scores = []
            for row in all_values[1:]:
                if len(row) > score_col and row[score_col].isdigit():
                    scores.append(int(row[score_col]))
            
            avg_score = sum(scores) / len(scores) if scores else 0
            
            stats = {
                'total_leads': total_leads,
                'status_distribution': status_count,
                'score_medio': round(avg_score, 2),
                'leads_por_status': status_count,
                'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
            logger.info(f"Estatísticas geradas: {total_leads} leads totais")
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas: {e}")
            return {}

if __name__ == "__main__":
    # Exemplo de uso
    sheets_manager = GoogleSheetsManager()
    
    # Autentica
    if sheets_manager.authenticate():
        # Abre planilha
        if sheets_manager.open_spreadsheet():
            # Cria/abre planilha de trabalho
            if sheets_manager.create_or_open_worksheet("Leads"):
                # Exemplo de lead
                sample_lead = {
                    'nome': 'Supermercado Exemplo',
                    'telefone': '(11) 99999-9999',
                    'website': 'https://www.exemplo.com.br',
                    'endereco': 'Rua das Flores, 123, Centro, São Paulo, SP',
                    'cnae': '4721-1/01',
                    'score': 4,
                    'qualificado': True,
                    'fonte': 'Google Places',
                    'data_coleta': '15/12/2024 10:30:00',
                    'data_qualificacao': '15/12/2024 10:35:00',
                    'observacoes_qualificacao': 'Lead altamente qualificado!'
                }
                
                # Adiciona lead
                sheets_manager.add_lead(sample_lead)
                
                # Gera estatísticas
                stats = sheets_manager.get_statistics()
                print(f"Estatísticas: {stats}")
                
                # Exporta para CSV
                csv_file = sheets_manager.export_to_csv()
                if csv_file:
                    print(f"Exportado para: {csv_file}")
