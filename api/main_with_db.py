#!/usr/bin/env python3
"""
API FastAPI com Banco de Dados SQLite
Libra Energia - Sistema de Prospecção
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import sys
import os
from pathlib import Path

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from database import LibraEnergiaDB
from src.lead_collector import LeadCollector
from src.lead_qualifier import LeadQualifier
from datetime import datetime

# Configuração da API
app = FastAPI(
    title="Libra Energia - API de Prospecção",
    description="API para sistema de coleta, qualificação e gestão de leads com banco de dados",
    version="2.0.0"
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância global do banco de dados
db = None

def get_database():
    """Dependency para obter instância do banco de dados"""
    global db
    if db is None:
        db = LibraEnergiaDB()
    return db

# ============================================================================
# ENDPOINTS BÁSICOS
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Libra Energia - API de Prospecção v2.0",
        "version": "2.0.0",
        "status": "online",
        "database": "SQLite",
        "endpoints": {
            "health": "/api/health",
            "leads": "/api/leads",
            "campaigns": "/api/campaigns",
            "stats": "/api/stats",
            "campaign_run": "/api/campaign/run"
        }
    }

@app.get("/api/health")
async def health_check():
    """Verificação de saúde da API"""
    try:
        database = get_database()
        stats = database.get_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# ENDPOINTS DE LEADS
# ============================================================================

@app.get("/leads")
async def get_leads_simple(database: LibraEnergiaDB = Depends(get_database)):
    """Endpoint simplificado para leads (compatibilidade com frontend)"""
    try:
        leads = database.get_all_leads(limit=100)
        
        return {
            "success": True,
            "data": leads,
            "total": len(leads),
            "source": "database",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "total": 0
        }

@app.get("/api/leads")
async def get_leads(
    limit: Optional[int] = Query(100, description="Número máximo de leads"),
    offset: Optional[int] = Query(0, description="Offset para paginação"),
    score_min: Optional[float] = Query(None, description="Score mínimo"),
    nivel: Optional[str] = Query(None, description="Nível de qualificação (A/B/C)"),
    qualificado: Optional[bool] = Query(None, description="Filtrar apenas qualificados"),
    campaign_id: Optional[int] = Query(None, description="ID da campanha específica"),
    database: LibraEnergiaDB = Depends(get_database)
):
    """Endpoint completo para leads com filtros avançados"""
    try:
        if campaign_id:
            leads = database.get_campaign_leads(campaign_id, limit)
        else:
            leads = database.get_all_leads(
                limit=limit,
                offset=offset,
                score_min=score_min,
                nivel=nivel,
                qualificado=qualificado
            )
        
        return {
            "success": True,
            "data": leads,
            "total": len(leads),
            "filters": {
                "limit": limit,
                "offset": offset,
                "score_min": score_min,
                "nivel": nivel,
                "qualificado": qualificado,
                "campaign_id": campaign_id
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS DE CAMPANHAS
# ============================================================================

@app.get("/api/campaigns")
async def get_campaigns(
    limit: Optional[int] = Query(10, description="Número máximo de campanhas"),
    database: LibraEnergiaDB = Depends(get_database)
):
    """Lista todas as campanhas"""
    try:
        campaigns = database.get_campaigns(limit=limit)
        
        return {
            "success": True,
            "data": campaigns,
            "total": len(campaigns),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: int,
    database: LibraEnergiaDB = Depends(get_database)
):
    """Obtém detalhes de uma campanha específica"""
    try:
        campaigns = database.get_campaigns(limit=1000)  # Buscar todas para encontrar a específica
        campaign = next((c for c in campaigns if c['id'] == campaign_id), None)
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campanha não encontrada")
        
        # Adicionar leads da campanha
        leads = database.get_campaign_leads(campaign_id)
        campaign['leads'] = leads
        
        return {
            "success": True,
            "data": campaign,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/campaign/run")
async def run_campaign(
    keyword: str = "supermercado",
    city: str = "São Paulo, SP",
    max_results: int = 20,
    database: LibraEnergiaDB = Depends(get_database)
):
    """Executa uma nova campanha de coleta de leads"""
    try:
        # Criar nova campanha
        campaign_name = f"Campanha {keyword} - {city} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        campaign_id = database.create_campaign(campaign_name, {
            "keyword": keyword,
            "city": city,
            "max_results": max_results
        })
        
        # Coletar leads
        collector = LeadCollector()
        qualifier = LeadQualifier()
        
        leads = collector.collect_from_google_places(keyword, city, max_results=max_results)
        qualified_leads = qualifier.qualify_leads_batch(leads)
        
        # Salvar leads no banco
        leads_added = database.add_leads(campaign_id, qualified_leads)
        
        # Calcular estatísticas
        qualified_count = sum(1 for lead in qualified_leads if lead.get('qualificado', False))
        avg_score = sum(lead.get('score', 0) for lead in qualified_leads) / len(qualified_leads) if qualified_leads else 0
        
        # Atualizar campanha
        database.update_campaign(campaign_id,
            status='concluida',
            leads_coletados=len(qualified_leads),
            leads_qualificados=qualified_count,
            score_medio=round(avg_score, 2),
            taxa_qualificacao=round((qualified_count / len(qualified_leads) * 100) if qualified_leads else 0, 2)
        )
        
        return {
            "success": True,
            "message": "Campanha executada com sucesso",
            "data": {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "leads_collected": len(qualified_leads),
                "leads_qualified": qualified_count,
                "leads_added": leads_added,
                "avg_score": round(avg_score, 2),
                "qualification_rate": round((qualified_count / len(qualified_leads) * 100) if qualified_leads else 0, 2),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        # Se houve erro, marcar campanha como falhou
        if 'campaign_id' in locals():
            database.update_campaign(campaign_id, status='falhou', observacoes=str(e))
        
        raise HTTPException(status_code=500, detail=f"Erro ao executar campanha: {str(e)}")

# ============================================================================
# ENDPOINTS DE ESTATÍSTICAS
# ============================================================================

@app.get("/api/stats")
async def get_stats(database: LibraEnergiaDB = Depends(get_database)):
    """Retorna estatísticas gerais do sistema"""
    try:
        stats = database.get_stats()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads/stats")
async def get_leads_stats(database: LibraEnergiaDB = Depends(get_database)):
    """Alias para /api/stats (compatibilidade)"""
    return await get_stats(database)

# ============================================================================
# ENDPOINTS DE MIGRAÇÃO
# ============================================================================

@app.post("/api/migrate")
async def migrate_json_files(database: LibraEnergiaDB = Depends(get_database)):
    """Migra arquivos JSON existentes para o banco de dados"""
    try:
        # Buscar arquivos JSON
        json_files = []
        for file in Path('.').glob('leads_coletados_*.json'):
            json_files.append(str(file))
        
        if not json_files:
            return {
                "success": True,
                "message": "Nenhum arquivo JSON encontrado para migrar",
                "files_migrated": 0
            }
        
        # Migrar arquivos
        database.migrate_json_files(json_files)
        
        return {
            "success": True,
            "message": f"Migração concluída: {len(json_files)} arquivos processados",
            "files_migrated": len(json_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
