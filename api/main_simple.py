from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import json
import os
from pathlib import Path
from datetime import datetime

# Configuração da API
app = FastAPI(
    title="Libra Energia - API de Prospecção",
    description="API para sistema de coleta, qualificação e gestão de leads",
    version="1.0.0"
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENDPOINTS DE LEADS
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Libra Energia - API de Prospecção",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "leads": "/api/leads",
            "stats": "/api/stats",
            "docs": "/docs"
        }
    }

@app.get("/leads")
async def get_leads_simple():
    """Endpoint simplificado para leads (compatibilidade com frontend)"""
    try:
        # Buscar arquivo mais recente
        lead_files = []
        for file in os.listdir(".."):
            if file.startswith("leads_coletados_") and file.endswith(".json"):
                lead_files.append(file)
        
        if not lead_files:
            return {"leads": [], "message": "Nenhum lead encontrado"}
        
        # Ordenar por data (mais recente primeiro)
        lead_files.sort(reverse=True)
        latest_file = lead_files[0]
        
        with open(f"../{latest_file}", "r", encoding="utf-8") as f:
            leads = json.load(f)
        
        return {
            "success": True,
            "data": leads,
            "total": len(leads),
            "source": latest_file,
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
    score_min: Optional[int] = Query(None, description="Score mínimo"),
    nivel: Optional[str] = Query(None, description="Nível de qualificação (Alto/Médio/Baixo)"),
    fonte: Optional[str] = Query(None, description="Fonte dos leads"),
    search: Optional[str] = Query(None, description="Busca por nome")
):
    """
    Retorna lista de leads com filtros opcionais
    """
    try:
        # Buscar arquivo mais recente de leads na pasta raiz
        root_path = Path(__file__).parent.parent
        lead_files = list(root_path.glob("leads_coletados_*.json"))
        
        if not lead_files:
            raise HTTPException(status_code=404, detail="Nenhum arquivo de leads encontrado")
        
        # Ordenar por data de modificação (mais recente primeiro)
        latest_file = max(lead_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            leads = json.load(f)
        
        # Aplicar filtros
        filtered_leads = leads
        
        if score_min is not None:
            filtered_leads = [l for l in filtered_leads if (l.get('score', 0) or 0) >= score_min]
        
        if nivel:
            filtered_leads = [l for l in filtered_leads if l.get('nivel_qualificacao') == nivel]
        
        if fonte:
            filtered_leads = [l for l in filtered_leads if l.get('fonte') == fonte]
        
        if search:
            search_lower = search.lower()
            filtered_leads = [l for l in filtered_leads if search_lower in (l.get('nome', '') or '').lower()]
        
        # Aplicar paginação
        total = len(filtered_leads)
        paginated_leads = filtered_leads[offset:offset + limit]
        
        return {
            "success": True,
            "data": paginated_leads,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            },
            "source_file": latest_file.name,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar leads: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """
    Retorna estatísticas gerais do sistema
    """
    try:
        # Buscar arquivo mais recente na pasta raiz
        root_path = Path(__file__).parent.parent
        lead_files = list(root_path.glob("leads_coletados_*.json"))
        
        if not lead_files:
            raise HTTPException(status_code=404, detail="Nenhum arquivo de leads encontrado")
        
        latest_file = max(lead_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            leads = json.load(f)
        
        # Calcular estatísticas
        total_leads = len(leads)
        leads_qualificados = len([l for l in leads if l.get('qualificado', False)])
        score_medio = sum(l.get('score', 0) or 0 for l in leads) / total_leads if total_leads > 0 else 0
        
        # Distribuição por nível
        niveis = {}
        for lead in leads:
            nivel = lead.get('nivel_qualificacao', 'Baixo')
            niveis[nivel] = niveis.get(nivel, 0) + 1
        
        # Distribuição por fonte
        fontes = {}
        for lead in leads:
            fonte = lead.get('fonte', 'Desconhecida')
            fontes[fonte] = fontes.get(fonte, 0) + 1
        
        return {
            "success": True,
            "data": {
                "total_leads": total_leads,
                "leads_qualificados": leads_qualificados,
                "score_medio": round(score_medio, 2),
                "taxa_qualificacao": round((leads_qualificados / total_leads * 100), 1) if total_leads > 0 else 0,
                "distribuicao_niveis": niveis,
                "distribuicao_fontes": fontes
            },
            "source_file": latest_file.name,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")

@app.get("/api/health")
async def health_check():
    """
    Verificação de saúde da API
    """
    try:
        # Verificar se os arquivos principais existem na pasta raiz
        root_path = Path(__file__).parent.parent
        lead_files = list(root_path.glob("leads_coletados_*.json"))
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "online",
                "data_files": {
                    "leads": len(lead_files)
                }
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/campaign/run")
async def run_campaign():
    """
    Executa uma nova campanha de coleta de leads
    """
    try:
        # Importar módulos necessários
        import sys
        from pathlib import Path
        
        # Adicionar src ao path
        src_path = Path(__file__).parent.parent / "src"
        sys.path.insert(0, str(src_path))
        
        from lead_collector import LeadCollector
        from lead_qualifier import LeadQualifier
        
        # Executar campanha
        collector = LeadCollector()
        qualifier = LeadQualifier()
        
        # Coletar leads
        leads = collector.collect_from_google_places("supermercado", "São Paulo, SP", max_results=20)
        
        # Qualificar leads
        qualified_leads = qualifier.qualify_leads_batch(leads)
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leads_coletados_{timestamp}.json"
        
        root_path = Path(__file__).parent.parent
        filepath = root_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(qualified_leads, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": "Campanha executada com sucesso",
            "data": {
                "leads_collected": len(leads),
                "leads_qualified": len(qualified_leads),
                "filename": filename,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao executar campanha: {str(e)}",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
