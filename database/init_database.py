#!/usr/bin/env python3
"""
Script de Inicialização do Banco de Dados
Libra Energia - Sistema de Prospecção
"""

import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from database import init_database

def main():
    """Função principal para inicializar o banco de dados"""
    print("🚀 Inicializando Banco de Dados - Libra Energia")
    print("=" * 50)
    
    try:
        # Inicializar banco e migrar arquivos
        db = init_database()
        
        # Mostrar estatísticas finais
        stats = db.get_stats()
        print("\n📊 Estatísticas Finais:")
        print(f"✅ Total de leads: {stats['total_leads']}")
        print(f"✅ Leads qualificados: {stats['qualified_leads']}")
        print(f"✅ Score médio: {stats['avg_score']}")
        print(f"✅ Taxa de qualificação: {stats['qualification_rate']}%")
        print(f"✅ Total de campanhas: {stats['total_campaigns']}")
        print(f"✅ Distribuição por nível: {stats['nivel_distribution']}")
        
        print("\n🎉 Banco de dados inicializado com sucesso!")
        print("💡 Agora você pode usar a API com banco de dados:")
        print("   python api/main_with_db.py")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
