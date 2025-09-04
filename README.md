# ⚡ Libra Energia - Sistema de Prospecção

Sistema automatizado de coleta, qualificação e gestão de leads para a Libra Energia.

## 🎯 Visão Geral

O sistema Libra Energia é uma solução completa para prospecção de clientes, oferecendo:

- **Coleta automática** de leads via Google Places API e Instagram
- **Qualificação inteligente** com sistema de scoring (0-6 pontos)
- **Dashboard interativo** com visualizações em tempo real
- **API REST** para integração com outros sistemas
- **Banco de dados SQLite** para armazenamento estruturado
- **Sistema de campanhas** para execução automatizada

## 🏗️ Arquitetura

```
libra-energia/
├── 📂 frontend/           # Interface do usuário
│   ├── dashboard_novo.html
│   ├── dashboard.js
│   └── serve_dashboard_novo.py
├── 📂 backend/            # API e lógica de negócio
│   └── api/
│       ├── main_simple.py
│       └── main_with_db.py
├── 📂 database/           # Gerenciamento de dados
│   ├── database.py
│   └── init_database.py
├── 📂 src/                # Código principal
│   ├── lead_collector.py
│   ├── lead_qualifier.py
│   └── sheets_manager.py
├── 📂 tests/              # Testes automatizados
├── 📂 scripts/            # Scripts utilitários
├── 📂 data/               # Dados coletados
├── 📂 docs/               # Documentação
└── 📂 logs/               # Logs do sistema
```

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- Google Places API Key
- Google Sheets API (opcional)

### 1. Clone o repositório

```bash
git clone <repository-url>
cd libra-energia
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
GOOGLE_PLACES_API_KEY=sua_chave_aqui
GOOGLE_SHEETS_CREDENTIALS=caminho_para_credentials.json
INSTAGRAM_CREDENTIALS=usuario:senha
RECEITA_WS_API_KEY=sua_chave_aqui
```

### 5. Inicialize o banco de dados (opcional)

```bash
python database/init_database.py
```

## 🎮 Como Usar

### Menu Interativo

```bash
python scripts/start.py
```

Opções disponíveis:
- `[1]` Testar sistema
- `[2]` Executar campanha completa
- `[6]` Iniciar API REST
- `[8]` Servir Dashboard HTTP
- `[10]` Inicializar Banco de Dados
- `[11]` Iniciar API com Banco de Dados

### Sistema Simples (JSON)

```bash
# Terminal 1: Iniciar API
python backend/api/start_api.py

# Terminal 2: Iniciar Dashboard
python frontend/serve_dashboard_novo.py

# Acesse: http://localhost:8080/dashboard_novo.html
```

### Sistema com Banco de Dados

```bash
# 1. Inicializar banco
python database/init_database.py

# 2. Iniciar API com banco
python backend/api/main_with_db.py

# 3. Iniciar Dashboard
python frontend/serve_dashboard_novo.py
```

## 📊 Funcionalidades

### Coleta de Leads

- **Google Places API**: Busca por palavra-chave + localização
- **Instagram Scraping**: Perfis comerciais verificados
- **Validação CNPJ**: Via ReceitaWS API

### Qualificação

- **Sistema de Scoring**: 0-6 pontos
  - CNAE relevante: +2 pontos
  - Telefone válido: +1 ponto
  - Website ativo: +1 ponto
  - Redes sociais: +1 ponto
  - Endereço completo: +1 ponto

- **Classificação por Nível**:
  - Nível A: 5-6 pontos (Alta prioridade)
  - Nível B: 3-4 pontos (Média prioridade)
  - Nível C: 0-2 pontos (Baixa prioridade)

### Dashboard

- **Métricas em tempo real**
- **Gráficos interativos**
- **Filtros avançados**
- **Execução de campanhas**
- **Exportação de dados**

## 🔧 API Endpoints

### Sistema Simples

```http
GET  /api/health          # Status da API
GET  /api/leads           # Lista todos os leads
GET  /api/leads/stats     # Estatísticas dos leads
POST /api/campaign/run    # Executa nova campanha
```

### Sistema com Banco de Dados

```http
GET  /api/health                    # Status da API
GET  /api/leads                     # Lista leads com filtros
GET  /api/campaigns                 # Lista campanhas
GET  /api/campaigns/{id}            # Detalhes da campanha
POST /api/campaign/run              # Executa nova campanha
GET  /api/stats                     # Estatísticas gerais
POST /api/migrate                   # Migra arquivos JSON
```

## 🧪 Testes

```bash
# Executar todos os testes
python tests/run_all_tests.py

# Testes específicos do frontend
python tests/run_frontend_tests.py

# Teste de conectividade da API
# Acesse: http://localhost:8080/test_api_connection.html
```

## 📈 Performance

- **Coleta**: ~20 leads em 30 segundos
- **Qualificação**: ~100% de taxa de sucesso
- **Score médio**: 5.0/6.0
- **Banco de dados**: Suporta milhares de leads
- **Cache**: localStorage para performance

## 🔒 Segurança

- **Variáveis de ambiente** para credenciais
- **CORS configurado** para desenvolvimento
- **Validação de dados** em todas as entradas
- **Logs detalhados** para auditoria

## 🚀 Deploy

### Desenvolvimento

```bash
# Sistema simples
python backend/api/main_simple.py

# Sistema com banco
python backend/api/main_with_db.py
```

### Produção

1. Configure variáveis de ambiente
2. Use PostgreSQL em vez de SQLite
3. Configure HTTPS
4. Implemente autenticação JWT
5. Use um servidor WSGI (Gunicorn)

## 📝 Logs

Os logs são salvos em:
- `logs/` - Logs do sistema
- Console - Logs em tempo real
- Browser DevTools - Logs do frontend

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte ou dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação em `docs/`
- Verifique os logs em `logs/`

## 🎯 Roadmap

- [ ] Autenticação JWT
- [ ] Integração com CRM
- [ ] Relatórios automáticos
- [ ] Notificações push
- [ ] API GraphQL
- [ ] Mobile app
- [ ] Machine Learning para scoring

---

**Desenvolvido com ❤️ para a Libra Energia**