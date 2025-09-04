#!/usr/bin/env python3
"""
Sistema de Banco de Dados para Libra Energia
Usa SQLite para armazenar campanhas e leads de forma estruturada
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class LibraEnergiaDB:
    """Classe para gerenciar o banco de dados SQLite"""
    
    def __init__(self, db_path: str = "libra_energia.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de campanhas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'executando',
                    leads_coletados INTEGER DEFAULT 0,
                    leads_qualificados INTEGER DEFAULT 0,
                    score_medio REAL DEFAULT 0.0,
                    taxa_qualificacao REAL DEFAULT 0.0,
                    parametros TEXT,  -- JSON com parâmetros da campanha
                    observacoes TEXT
                )
            """)
            
            # Tabela de leads
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER,
                    nome TEXT NOT NULL,
                    telefone TEXT,
                    website TEXT,
                    endereco TEXT,
                    email TEXT,
                    score REAL DEFAULT 0.0,
                    nivel TEXT DEFAULT 'C',
                    qualificado BOOLEAN DEFAULT FALSE,
                    fonte TEXT,
                    cnae TEXT,
                    redes_sociais TEXT,  -- JSON com redes sociais
                    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observacoes TEXT,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
                )
            """)
            
            # Índices para melhor performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_campaign ON leads(campaign_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_nivel ON leads(nivel)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_qualificado ON leads(qualificado)")
            
            conn.commit()
            print(f"✅ Banco de dados inicializado: {self.db_path}")
    
    def create_campaign(self, nome: str, parametros: Dict = None) -> int:
        """Cria uma nova campanha e retorna o ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO campaigns (nome, parametros)
                VALUES (?, ?)
            """, (nome, json.dumps(parametros) if parametros else None))
            
            campaign_id = cursor.lastrowid
            conn.commit()
            print(f"✅ Campanha criada: {nome} (ID: {campaign_id})")
            return campaign_id
    
    def update_campaign(self, campaign_id: int, **kwargs):
        """Atualiza dados de uma campanha"""
        if not kwargs:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [campaign_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE campaigns 
                SET {set_clause}
                WHERE id = ?
            """, values)
            conn.commit()
            print(f"✅ Campanha {campaign_id} atualizada")
    
    def add_leads(self, campaign_id: int, leads: List[Dict]) -> int:
        """Adiciona leads a uma campanha"""
        if not leads:
            return 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            leads_added = 0
            for lead in leads:
                cursor.execute("""
                    INSERT INTO leads (
                        campaign_id, nome, telefone, website, endereco, email,
                        score, nivel, qualificado, fonte, cnae, redes_sociais, observacoes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    campaign_id,
                    lead.get('nome', ''),
                    lead.get('telefone', ''),
                    lead.get('website', ''),
                    lead.get('endereco', ''),
                    lead.get('email', ''),
                    lead.get('score', 0.0),
                    lead.get('nivel', 'C'),
                    lead.get('qualificado', False),
                    lead.get('fonte', ''),
                    lead.get('cnae', ''),
                    json.dumps(lead.get('redes_sociais', {})),
                    lead.get('observacoes', '')
                ))
                leads_added += 1
            
            conn.commit()
            print(f"✅ {leads_added} leads adicionados à campanha {campaign_id}")
            return leads_added
    
    def get_campaigns(self, limit: int = 10) -> List[Dict]:
        """Retorna lista de campanhas"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM campaigns 
                ORDER BY data_execucao DESC 
                LIMIT ?
            """, (limit,))
            
            campaigns = []
            for row in cursor.fetchall():
                campaign = dict(row)
                campaign['parametros'] = json.loads(campaign['parametros']) if campaign['parametros'] else {}
                campaigns.append(campaign)
            
            return campaigns
    
    def get_campaign_leads(self, campaign_id: int, limit: int = 100) -> List[Dict]:
        """Retorna leads de uma campanha específica"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM leads 
                WHERE campaign_id = ?
                ORDER BY score DESC, nome ASC
                LIMIT ?
            """, (campaign_id, limit))
            
            leads = []
            for row in cursor.fetchall():
                lead = dict(row)
                lead['redes_sociais'] = json.loads(lead['redes_sociais']) if lead['redes_sociais'] else {}
                leads.append(lead)
            
            return leads
    
    def get_all_leads(self, limit: int = 100, offset: int = 0, 
                     score_min: float = None, nivel: str = None, 
                     qualificado: bool = None) -> List[Dict]:
        """Retorna todos os leads com filtros opcionais"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Construir query com filtros
            where_conditions = []
            params = []
            
            if score_min is not None:
                where_conditions.append("score >= ?")
                params.append(score_min)
            
            if nivel:
                where_conditions.append("nivel = ?")
                params.append(nivel)
            
            if qualificado is not None:
                where_conditions.append("qualificado = ?")
                params.append(qualificado)
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            query = f"""
                SELECT l.*, c.nome as campaign_nome, c.data_execucao as campaign_data
                FROM leads l
                LEFT JOIN campaigns c ON l.campaign_id = c.id
                {where_clause}
                ORDER BY l.score DESC, l.nome ASC
                LIMIT ? OFFSET ?
            """
            
            params.extend([limit, offset])
            cursor.execute(query, params)
            
            leads = []
            for row in cursor.fetchall():
                lead = dict(row)
                lead['redes_sociais'] = json.loads(lead['redes_sociais']) if lead['redes_sociais'] else {}
                leads.append(lead)
            
            return leads
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas gerais do sistema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Estatísticas de leads
            cursor.execute("SELECT COUNT(*) FROM leads")
            total_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM leads WHERE qualificado = 1")
            qualified_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(score) FROM leads")
            avg_score = cursor.fetchone()[0] or 0.0
            
            cursor.execute("SELECT COUNT(*) FROM campaigns")
            total_campaigns = cursor.fetchone()[0]
            
            # Distribuição por nível
            cursor.execute("""
                SELECT nivel, COUNT(*) 
                FROM leads 
                GROUP BY nivel 
                ORDER BY nivel
            """)
            nivel_distribution = dict(cursor.fetchall())
            
            return {
                'total_leads': total_leads,
                'qualified_leads': qualified_leads,
                'avg_score': round(avg_score, 2),
                'qualification_rate': round((qualified_leads / total_leads * 100) if total_leads > 0 else 0, 2),
                'total_campaigns': total_campaigns,
                'nivel_distribution': nivel_distribution
            }
    
    def migrate_json_files(self, json_files: List[str]):
        """Migra arquivos JSON existentes para o banco de dados"""
        print("🔄 Iniciando migração de arquivos JSON...")
        
        for json_file in json_files:
            if not Path(json_file).exists():
                print(f"⚠️ Arquivo não encontrado: {json_file}")
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    leads = json.load(f)
                
                if not isinstance(leads, list):
                    print(f"⚠️ Formato inválido em {json_file}")
                    continue
                
                # Extrair data do nome do arquivo
                filename = Path(json_file).stem
                if 'leads_coletados_' in filename:
                    date_str = filename.replace('leads_coletados_', '')
                    try:
                        campaign_date = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                        campaign_name = f"Campanha {date_str}"
                    except:
                        campaign_name = f"Campanha {filename}"
                else:
                    campaign_name = f"Campanha {filename}"
                
                # Criar campanha
                campaign_id = self.create_campaign(campaign_name, {
                    'source_file': json_file,
                    'migrated': True
                })
                
                # Adicionar leads
                leads_added = self.add_leads(campaign_id, leads)
                
                # Atualizar estatísticas da campanha
                qualified_count = sum(1 for lead in leads if lead.get('qualificado', False))
                avg_score = sum(lead.get('score', 0) for lead in leads) / len(leads) if leads else 0
                
                self.update_campaign(campaign_id, 
                    status='concluida',
                    leads_coletados=len(leads),
                    leads_qualificados=qualified_count,
                    score_medio=round(avg_score, 2),
                    taxa_qualificacao=round((qualified_count / len(leads) * 100) if leads else 0, 2)
                )
                
                print(f"✅ Migrado {json_file}: {leads_added} leads")
                
            except Exception as e:
                print(f"❌ Erro ao migrar {json_file}: {e}")
        
        print("🎉 Migração concluída!")

# Função utilitária para inicializar o banco
def init_database():
    """Inicializa o banco de dados e migra arquivos existentes"""
    db = LibraEnergiaDB()
    
    # Buscar arquivos JSON existentes
    json_files = []
    for file in Path('.').glob('leads_coletados_*.json'):
        json_files.append(str(file))
    
    if json_files:
        print(f"📁 Encontrados {len(json_files)} arquivos JSON para migrar")
        db.migrate_json_files(json_files)
    else:
        print("📁 Nenhum arquivo JSON encontrado para migrar")
    
    return db

if __name__ == "__main__":
    # Teste do banco de dados
    db = init_database()
    
    # Mostrar estatísticas
    stats = db.get_stats()
    print("\n📊 Estatísticas do Sistema:")
    print(f"Total de leads: {stats['total_leads']}")
    print(f"Leads qualificados: {stats['qualified_leads']}")
    print(f"Score médio: {stats['avg_score']}")
    print(f"Taxa de qualificação: {stats['qualification_rate']}%")
    print(f"Total de campanhas: {stats['total_campaigns']}")
    print(f"Distribuição por nível: {stats['nivel_distribution']}")
