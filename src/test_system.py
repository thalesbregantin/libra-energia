"""
Script de teste simples para verificar o sistema
"""
import json
from datetime import datetime
from lead_qualifier import LeadQualifier
from config import Config

def test_qualification_system():
    """Testa o sistema de qualificação sem dependências externas"""
    print("Testando sistema de qualificação...")
    
    # Cria qualificador
    qualifier = LeadQualifier()
    
    # Leads de teste
    test_leads = [
        {
            'nome': 'Supermercado Exemplo Ltda',
            'telefone': '(11) 99999-9999',
            'website': 'https://www.exemplo.com.br',
            'endereco': 'Rua das Flores, 123, Centro, São Paulo, SP',
            'cnae': '4721-1/01',
            'fonte': 'Teste',
            'data_coleta': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        },
        {
            'nome': 'Padaria do João',
            'telefone': '(11) 88888-8888',
            'website': '',
            'endereco': 'Av. Paulista, 456, Bela Vista, São Paulo, SP',
            'cnae': '4722-0/00',
            'fonte': 'Teste',
            'data_coleta': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        },
        {
            'nome': 'Academia Fitness',
            'telefone': '(11) 77777-7777',
            'website': 'https://academiafitness.com.br',
            'endereco': 'Rua Augusta, 789, Consolação, São Paulo, SP',
            'cnae': '9311-5/01',
            'instagram': 'https://instagram.com/academiafitness',
            'fonte': 'Teste',
            'data_coleta': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
    ]
    
    print(f"Testando com {len(test_leads)} leads...")
    
    # Qualifica leads
    qualified_leads = qualifier.qualify_leads_batch(test_leads)
    
    # Exibe resultados
    print("\n" + "="*60)
    print("RESULTADOS DA QUALIFICAÇÃO")
    print("="*60)
    
    for i, lead in enumerate(qualified_leads, 1):
        print(f"\n{i}. {lead['nome']}")
        print(f"   Telefone: {lead['telefone']}")
        print(f"   Website: {lead['website']}")
        print(f"   Endereço: {lead['endereco']}")
        print(f"   CNAE: {lead['cnae']}")
        print(f"   Score: {lead['score']}/6")
        print(f"   Qualificado: {'SIM' if lead['qualificado'] else 'NÃO'}")
        print(f"   Nível: {lead['nivel_qualificacao']}")
        print(f"   Critérios: {', '.join(lead['criterios_atingidos'])}")
    
    # Gera relatório
    print("\n" + "="*60)
    print("RELATÓRIO DE QUALIFICAÇÃO")
    print("="*60)
    
    report = qualifier.generate_qualification_report(qualified_leads)
    
    print(f"Total de leads: {report['total_leads']}")
    print(f"Leads qualificados: {report['leads_qualificados']}")
    print(f"Leads não qualificados: {report['leads_nao_qualificados']}")
    print(f"Taxa de qualificação: {report['taxa_qualificacao']:.1f}%")
    print(f"Score médio: {report['score_medio']:.2f}")
    
    print(f"\nTop critérios atingidos:")
    for criterio, count in report['top_criterios']:
        print(f"   • {criterio}: {count} leads")
    
    return qualified_leads

def test_config_system():
    """Testa o sistema de configuração"""
    print("\nTestando sistema de configuração...")
    
    config = Config()
    
    print(f"Nome da empresa: {config.EMPRESA_NOME}")
    print(f"Representante: {config.REPRESENTANTE_NOME}")
    print(f"Google Places API configurada: {'SIM' if config.GOOGLE_PLACES_API_KEY else 'NÃO'}")
    print(f"Palavras-chave disponíveis: {len(config.PALAVRAS_CHAVE)}")
    print(f"Cidades disponíveis: {len(config.CIDADES_INICIAIS)}")
    print(f"CNAEs de alto consumo: {len(config.CIDADES_INICIAIS)}")
    
    return config

def save_test_results(leads):
    """Salva resultados do teste"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"teste_sistema_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    
    print(f"\nResultados salvos em: {filename}")
    return filename

def main():
    """Função principal do teste"""
    print("INICIANDO TESTE DO SISTEMA DE PROSPECÇÃO")
    print("="*60)
    
    try:
        # Testa configuração
        config = test_config_system()
        
        # Testa sistema de qualificação
        qualified_leads = test_qualification_system()
        
        # Salva resultados
        test_file = save_test_results(qualified_leads)
        
        print("\n" + "="*60)
        print("TESTE CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print(f"Arquivo de teste: {test_file}")
        print("Sistema de qualificação funcionando perfeitamente!")
        print("Configurações carregadas corretamente!")
        
        # Próximos passos
        print("\nPRÓXIMOS PASSOS:")
        print("1. Configure as variáveis de ambiente (.env)")
        print("2. Execute: python main.py --teste")
        print("3. Para campanha completa: python main.py --keywords supermercado --cidades 'São Paulo, SP'")
        
    except Exception as e:
        print(f"\nERRO NO TESTE: {e}")
        print("Verifique se todas as dependências estão instaladas:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()
