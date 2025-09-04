from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path
from datetime import datetime
import sys

# Adicionar o diretório src ao path para importar os módulos
sys.path.append(str(Path(__file__).parent.parent / "src"))

from lead_collector import LeadCollector
from lead_qualifier import LeadQualifier
from config import Config

# Configuração da API
app = FastAPI(
    title="Libra Energia - API de Prospecção",
    description="API para sistema de coleta, qualificação e gestão de leads",
    version="1.0.0"
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciar classes principais
config = Config()
collector = LeadCollector()
qualifier = LeadQualifier()

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
            "campaigns": "/api/campaigns",
            "stats": "/api/stats",
            "docs": "/docs"
        }
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
        # Buscar arquivo mais recente de leads
        lead_files = list(Path(".").glob("leads_coletados_*.json"))
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

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    """
    Retorna um lead específico por ID
    """
    try:
        # Buscar arquivo mais recente
        lead_files = list(Path(".").glob("leads_coletados_*.json"))
        if not lead_files:
            raise HTTPException(status_code=404, detail="Nenhum arquivo de leads encontrado")
        
        latest_file = max(lead_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            leads = json.load(f)
        
        # Buscar lead por ID (pode ser nome, place_id, etc.)
        lead = None
        for l in leads:
            if (l.get('place_id') == lead_id or 
                l.get('nome') == lead_id or 
                str(l.get('id', '')) == lead_id):
                lead = l
                break
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead não encontrado")
        
        return {
            "success": True,
            "data": lead,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar lead: {str(e)}")

@app.get("/api/leads/export/csv")
async def export_leads_csv():
    """
    Exporta todos os leads em formato CSV
    """
    try:
        # Buscar arquivo mais recente
        lead_files = list(Path(".").glob("leads_coletados_*.csv"))
        if not lead_files:
            raise HTTPException(status_code=404, detail="Nenhum arquivo CSV de leads encontrado")
        
        latest_file = max(lead_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        return JSONResponse(
            content={
                "success": True,
                "message": "CSV exportado com sucesso",
                "filename": latest_file.name,
                "content": csv_content,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar CSV: {str(e)}")

# ============================================================================
# ENDPOINTS DE ESTATÍSTICAS
# ============================================================================

@app.get("/api/stats")
async def get_stats():
    """
    Retorna estatísticas gerais do sistema
    """
    try:
        # Buscar arquivo mais recente
        lead_files = list(Path(".").glob("leads_coletados_*.json"))
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
        
        # Top leads por score
        top_leads = sorted(leads, key=lambda x: x.get('score', 0) or 0, reverse=True)[:10]
        
        return {
            "success": True,
            "data": {
                "total_leads": total_leads,
                "leads_qualificados": leads_qualificados,
                "score_medio": round(score_medio, 2),
                "taxa_qualificacao": round((leads_qualificados / total_leads * 100), 1) if total_leads > 0 else 0,
                "distribuicao_niveis": niveis,
                "distribuicao_fontes": fontes,
                "top_leads": [
                    {
                        "nome": l.get('nome', 'N/A'),
                        "score": l.get('score', 0),
                        "nivel": l.get('nivel_qualificacao', 'Baixo'),
                        "fonte": l.get('fonte', 'N/A')
                    } for l in top_leads
                ]
            },
            "source_file": latest_file.name,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")

@app.get("/api/stats/charts")
async def get_chart_data():
    """
    Retorna dados formatados para gráficos
    """
    try:
        # Buscar arquivo mais recente
        lead_files = list(Path(".").glob("leads_coletados_*.json"))
        if not lead_files:
            raise HTTPException(status_code=404, detail="Nenhum arquivo de leads encontrado")
        
        latest_file = max(lead_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            leads = json.load(f)
        
        # Dados para gráfico de pizza (distribuição por nível)
        nivel_data = {
            "labels": [],
            "data": [],
            "backgroundColor": ["#10b981", "#f59e0b", "#ef4444"]
        }
        
        niveis = {}
        for lead in leads:
            nivel = lead.get('nivel_qualificacao', 'Baixo')
            niveis[nivel] = niveis.get(nivel, 0) + 1
        
        for nivel, count in niveis.items():
            nivel_data["labels"].append(nivel)
            nivel_data["data"].append(count)
        
        # Dados para gráfico de barras (score por lead)
        score_data = {
            "labels": [],
            "data": []
        }
        
        # Top 10 leads por score
        top_leads = sorted(leads, key=lambda x: x.get('score', 0) or 0, reverse=True)[:10]
        for lead in top_leads:
            score_data["labels"].append(lead.get('nome', 'N/A')[:20] + '...' if len(lead.get('nome', '')) > 20 else lead.get('nome', 'N/A'))
            score_data["data"].append(lead.get('score', 0))
        
        return {
            "success": True,
            "data": {
                "pie_chart": nivel_data,
                "bar_chart": score_data
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados dos gráficos: {str(e)}")

# ============================================================================
# ENDPOINTS DE CAMPANHAS
# ============================================================================

@app.get("/api/campaigns")
async def get_campaigns():
    """
    Retorna lista de campanhas executadas
    """
    try:
        # Buscar relatórios de campanhas
        campaign_files = list(Path(".").glob("relatorio_campanha_*.json"))
        campaigns = []
        
        for file in sorted(campaign_files, key=lambda x: x.stat().st_mtime, reverse=True):
            with open(file, 'r', encoding='utf-8') as f:
                campaign_data = json.load(f)
                campaigns.append({
                    "filename": file.name,
                    "data": campaign_data,
                    "execution_date": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
        
        return {
            "success": True,
            "data": campaigns,
            "total": len(campaigns),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar campanhas: {str(e)}")

@app.get("/api/campaigns/latest")
async def get_latest_campaign():
    """
    Retorna dados da campanha mais recente
    """
    try:
        # Buscar relatório mais recente
        campaign_files = list(Path(".").glob("relatorio_campanha_*.json"))
        if not campaign_files:
            raise HTTPException(status_code=404, detail="Nenhuma campanha encontrada")
        
        latest_file = max(campaign_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            campaign_data = json.load(f)
        
        return {
            "success": True,
            "data": campaign_data,
            "filename": latest_file.name,
            "execution_date": datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar campanha: {str(e)}")

# ============================================================================
# ENDPOINTS DE EXECUÇÃO
# ============================================================================

@app.post("/api/execute/campaign")
async def execute_campaign(
    keywords: List[str] = ["supermercado", "padaria"],
    cities: List[str] = ["São Paulo, SP"],
    max_leads: int = 20
):
    """
    Executa uma nova campanha de coleta
    """
    try:
        # Executar campanha
        leads = collector.run_collection_campaign(keywords, cities)
        
        # Qualificar leads
        qualified_leads = qualifier.qualify_leads_batch(leads)
        
        # Salvar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = collector.save_leads_to_json(qualified_leads, f"leads_coletados_{timestamp}.json")
        csv_file = collector.save_leads_to_csv(qualified_leads, f"leads_coletados_{timestamp}.csv")
        
        # Gerar relatório
        report = qualifier.generate_qualification_report(qualified_leads)
        report_file = f"relatorio_campanha_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": "Campanha executada com sucesso",
            "data": {
                "leads_coletados": len(leads),
                "leads_qualificados": len(qualified_leads),
                "score_medio": report.get('score_medio', 0),
                "arquivos_gerados": {
                    "json": json_file,
                    "csv": csv_file,
                    "relatorio": report_file
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao executar campanha: {str(e)}")

@app.post("/api/execute/test")
async def execute_test_campaign():
    """
    Executa uma campanha de teste rápida
    """
    try:
        # Executar teste
        leads = collector.run_collection_campaign(
            keywords=["supermercado", "padaria"],
            cities=["São Paulo, SP"],
            max_leads=20
        )
        
        # Qualificar leads
        qualified_leads = qualifier.qualify_leads_batch(leads)
        
        # Salvar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = collector.save_leads_to_json(qualified_leads, f"teste_sistema_{timestamp}.json")
        
        return {
            "success": True,
            "message": "Teste executado com sucesso",
            "data": {
                "leads_coletados": len(leads),
                "leads_qualificados": len(qualified_leads),
                "arquivo_gerado": json_file
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao executar teste: {str(e)}")

# ============================================================================
# ENDPOINTS DE CONFIGURAÇÃO
# ============================================================================

@app.get("/api/config")
async def get_config():
    """
    Retorna configurações do sistema
    """
    try:
        return {
            "success": True,
            "data": {
                "palavras_chave": config.PALAVRAS_CHAVE,
                "cidades_iniciais": config.CIDADES_INICIAIS,
                "cnaes_alto_consumo": config.CNAES_ALTO_CONSUMO,
                "empresa_nome": config.EMPRESA_NOME,
                "representante_nome": config.REPRESENTANTE_NOME
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar configurações: {str(e)}")

@app.get("/api/health")
async def health_check():
    """
    Verificação de saúde da API
    """
    try:
        # Verificar se os arquivos principais existem
        lead_files = list(Path(".").glob("leads_coletados_*.json"))
        campaign_files = list(Path(".").glob("relatorio_campanha_*.json"))
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "online",
                "lead_collector": "available",
                "lead_qualifier": "available",
                "data_files": {
                    "leads": len(lead_files),
                    "campaigns": len(campaign_files)
                }
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
