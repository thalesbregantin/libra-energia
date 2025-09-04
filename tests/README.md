# 🧪 Framework de Testes TDD - Libra Energia

## 📋 **Visão Geral**

Este diretório contém um framework completo de **Test-Driven Development (TDD)** para o sistema de automação de prospecção da Libra Energia. Os testes seguem a metodologia **Arrange-Act-Assert** e cobrem todas as funcionalidades principais do sistema.

## 🏗️ **Estrutura dos Testes**

```
tests/
├── __init__.py                 # Pacote de testes
├── test_config.py             # Testes de configuração
├── test_lead_qualifier.py     # Testes de qualificação de leads
├── test_lead_collector.py     # Testes de coleta de leads
├── test_integration.py        # Testes de integração
├── run_all_tests.py           # Script principal de execução
└── README.md                  # Esta documentação
```

## 🎯 **Metodologia TDD**

### **1. Arrange-Act-Assert (AAA)**
- **Arrange**: Preparar dados e configurações
- **Act**: Executar a funcionalidade testada
- **Assert**: Verificar se o resultado é o esperado

### **2. Testes Unitários**
- Testam funcionalidades isoladas
- Usam mocks para dependências externas
- Execução rápida e determinística

### **3. Testes de Integração**
- Testam fluxos completos do sistema
- Verificam compatibilidade entre módulos
- Validam persistência de dados

## 🚀 **Como Executar os Testes**

### **Executar Todos os Testes**
```bash
# No diretório raiz do projeto
python tests/run_all_tests.py
```

### **Executar Teste Específico**
```bash
# Teste de configuração
python tests/run_all_tests.py tests.test_config.TestConfig

# Teste de qualificação
python tests/run_all_tests.py tests.test_lead_qualifier.TestLeadQualifier

# Teste de coleta
python tests/run_all_tests.py tests.test_lead_collector.TestLeadCollector

# Teste de integração
python tests/run_all_tests.py tests.test_integration.TestSystemIntegration
```

### **Executar Teste Individual**
```bash
# Teste específico
python tests/run_all_tests.py tests.test_config.TestConfig.test_env_file_loading
```

## 📊 **Cobertura de Testes**

### **Configuração (test_config.py)**
- ✅ Carregamento de variáveis de ambiente
- ✅ Valores padrão quando .env não existe
- ✅ Estrutura de palavras-chave
- ✅ Estrutura de cidades
- ✅ Estrutura de CNAEs

### **Qualificação de Leads (test_lead_qualifier.py)**
- ✅ Inicialização do qualificador
- ✅ Qualificação individual de leads
- ✅ Qualificação em lote
- ✅ Sistema de pontuação (website, telefone, CNAE)
- ✅ Níveis de qualificação
- ✅ Geração de relatórios

### **Coleta de Leads (test_lead_collector.py)**
- ✅ Inicialização do coletor
- ✅ Chamadas para API do Google Places
- ✅ Tratamento de erros da API
- ✅ Estrutura dos dados coletados
- ✅ Limpeza e validação de dados
- ✅ Salvamento em JSON e CSV
- ✅ Execução de campanhas

### **Integração (test_integration.py)**
- ✅ Fluxo completo de ponta a ponta
- ✅ Consistência de dados
- ✅ Tratamento de erros
- ✅ Performance com múltiplos leads
- ✅ Compatibilidade de formatos de arquivo

## 🔧 **Configuração do Ambiente**

### **Pré-requisitos**
- Python 3.8+
- Ambiente virtual ativado
- Dependências instaladas (`pip install -r requirements.txt`)

### **Estrutura de Diretórios**
```
projeto/
├── src/                    # Código fonte
├── tests/                  # Testes TDD
├── requirements.txt        # Dependências Python
└── .env                   # Variáveis de ambiente
```

## 📈 **Métricas de Qualidade**

### **Indicadores de Sucesso**
- **Cobertura**: 100% das funcionalidades principais
- **Performance**: < 5 segundos para 100 leads
- **Robustez**: Sistema não quebra com dados inválidos
- **Consistência**: Dados preservados em todo o fluxo

### **Critérios de Aceitação**
- ✅ Todos os testes passam
- ✅ Sem falhas ou erros
- ✅ Performance dentro dos limites
- ✅ Tratamento de erros adequado

## 🐛 **Debugging e Troubleshooting**

### **Problemas Comuns**

#### **1. ImportError: No module named 'config'**
```bash
# Verificar se está no diretório correto
cd /caminho/para/projeto
python tests/run_all_tests.py
```

#### **2. Testes falhando com dados reais**
```bash
# Usar dados de teste mockados
# Verificar se APIs externas estão funcionando
```

#### **3. Problemas de encoding**
```bash
# Verificar se arquivos estão em UTF-8
# Usar encoding='utf-8' ao abrir arquivos
```

### **Logs e Debug**
```bash
# Executar com verbosidade máxima
python -m unittest discover tests/ -v

# Executar teste específico com debug
python -m unittest tests.test_config.TestConfig.test_env_file_loading -v
```

## 🚀 **Próximos Passos**

### **Melhorias Planejadas**
1. **Cobertura de Código**: Adicionar `coverage.py`
2. **Testes de Performance**: Benchmarks automatizados
3. **Testes de Segurança**: Validação de inputs
4. **Testes de UI**: Selenium para dashboard
5. **CI/CD**: Integração com GitHub Actions

### **Novos Testes**
- Validação de CNPJ via ReceitaWS
- Integração com Google Sheets
- Sistema de logging
- Tratamento de timeouts
- Validação de formatos de dados

## 📞 **Suporte**

Para dúvidas sobre os testes:
1. Verificar esta documentação
2. Executar testes com `-v` para mais detalhes
3. Verificar logs de erro
4. Consultar código fonte dos testes

---

**🎯 Lembre-se**: TDD não é apenas sobre escrever testes, mas sobre **projetar melhor software** através de testes que guiam o desenvolvimento!
