# 🏆 Sistema de Relatório Esportivo Artplan - Dados Reais

Sistema avançado de coleta e análise de dados esportivos com arquitetura de duas camadas para inteligência em apostas esportivas.

## 🎯 Visão Geral

Este sistema resolve o problema de **dados fictícios** em relatórios esportivos, implementando uma solução robusta com:

- ✅ **100% dados reais** via APIs oficiais
- ✅ **Web scraping** de sites brasileiros 
- ✅ **IA curatorial** com Gemini para análise inteligente
- ✅ **Arquitetura de duas camadas** para máxima eficiência

## 🏗️ Arquitetura

### 🧱 Camada 1: Coleta e Armazenamento Bruto
**Execução**: Diária às 9h30 via agendamento
**Objetivo**: Coletar TUDO que seja relevante e armazenar separadamente

```
📊 Dados coletados:
├── noticias_brutas_ultimas_24h.json
├── resultados_recentes.json
├── jogos_proximas_24h.json
├── eventos_esports.json
└── programacao_semanal.json
```

### 🔍 Camada 2: Curadoria Inteligente com IA
**Execução**: Após coleta bruta
**Objetivo**: Filtrar conteúdo estratégico para apostas esportivas

**Critérios de seleção**:
- 🎯 Impacto direto em apostas (lesões, clima, mudanças técnicas)
- 🏢 Relacionados com concorrentes BetMGM  
- 🇧🇷 Alta atratividade para público brasileiro
- 📊 Priorização: Brasileiros > Sul-Americanos > Europeus > E-gaming

## 🚀 Funcionalidades

### ✅ Versão Atual (v1.0 - Dados Reais)
- [x] API TheSportsDB integrada
- [x] Web scraping de 6 sites brasileiros
- [x] Gmail API para envio automático
- [x] Interface HTML moderna
- [x] Sistema de badges (API REAL, WEB SCRAPING)
- [x] Tratamento robusto de erros
- [x] Logging detalhado

### 🔄 Próximas Versões (v2.0 - IA Curatorial)
- [ ] Sistema de coleta bruta automatizada
- [ ] Integração Gemini API para curadoria
- [ ] Armazenamento estruturado (JSON/BigQuery)
- [ ] Dashboard de análise de tendências
- [ ] Sistema de alertas personalizados

## 📁 Estrutura do Projeto

```
painel-noticias/
├── 📄 real_sports_data.py      # Coleta via TheSportsDB API
├── 📰 real_news_scraper.py     # Web scraping notícias
├── 📧 gmail_api_reporter.py    # Sistema principal Gmail
├── 🔧 env.yaml                 # Configurações
├── 🔑 credentials.json         # Credenciais Gmail OAuth2
├── 📋 requirements.txt         # Dependências Python
└── 📖 README.md               # Documentação
```

## ⚙️ Configuração

### 1. Dependências
```bash
pip install requests beautifulsoup4 feedparser google-auth google-auth-oauthlib google-api-python-client pyyaml
```

### 2. Configuração Gmail API
1. Criar projeto no Google Cloud Console
2. Habilitar Gmail API
3. Baixar `credentials.json`
4. Configurar `env.yaml`

### 3. Configuração env.yaml
```yaml
gmail:
  sender_email: "analytics.artplan@gmail.com"
  recipient_email: "caio.castro@artplan.com.br"

gemini:
  api_key: "SUA_CHAVE_GEMINI_API"

config:
  timezone: "America/Sao_Paulo"
  max_news: 15
  max_events: 20
```

## 🎯 Uso

### Relatório Básico (v1.0)
```bash
python gmail_api_reporter.py
```

### Coleta Bruta (v2.0 - em desenvolvimento)
```bash
python data_collector.py --mode=bruto
```

### Curadoria IA (v2.0 - em desenvolvimento)  
```bash
python ai_curator.py --source=data/bruto/ --output=data/curado/
```

## 📊 Fontes de Dados

### 🏟️ Dados Esportivos (API)
- **TheSportsDB**: Eventos, resultados, programação
- **Filtros**: Times brasileiros, ligas relevantes
- **Cobertura**: Futebol, e-sports, eventos internacionais

### 📰 Notícias (Web Scraping)
- **GloboEsporte**: https://ge.globo.com/rss/ge/futebol/
- **ESPN Brasil**: https://www.espn.com.br/rss/futebol
- **Lance!**: https://www.lance.com.br/rss.xml
- **UOL Esporte**: https://rss.uol.com.br/feed/esporte.xml
- **Mais Esports**: https://maisesports.com.br/feed/
- **Transfermarkt**: https://www.transfermarkt.com.br/rss/news

## 🤖 IA Curatorial (v2.0)

### Prompt Gemini
```
Você é um especialista em apostas esportivas e marketing de cassinos. 
Receberá arquivos com notícias e jogos das últimas 24h. 

Filtrar conteúdos que:
- Possuem impacto direto em apostas (lesão, clima, mudança técnica)
- Relacionam-se com concorrentes da BetMGM
- Têm alta atratividade para público apostador brasileiro
- Priorizam: Brasileiros > Sul-Americanos > Europeus > E-gaming

Output:
1. Máximo 10 notícias relevantes
2. 10 jogos mais importantes (hoje + amanhã)
3. Análise de impacto BetMGM (1 parágrafo ou 5 bullets)
```

## 📈 Resultados Testados

### ✅ Coleta de Dados
- **5 eventos hoje** coletados via API
- **5 eventos amanhã** programados
- **8 resultados recentes** de times brasileiros
- **2 eventos e-sports** (LOUD vs paiN, FURIA vs MIBR)
- **15 notícias únicas** de 6 fontes

### ✅ Qualidade dos Dados
- **0% dados fictícios** - 100% fontes reais
- **Links funcionais** para todas as notícias
- **Badges indicativos** de fonte (API/Scraping)
- **Categorização automática** por relevância
- **Tratamento de duplicatas** baseado em títulos

### ✅ Entrega
- **Email HTML responsivo** enviado automaticamente
- **Interface moderna** com gradientes e cards
- **Estatísticas em tempo real** no cabeçalho
- **Logging detalhado** para debugging

## 🛠️ Tecnologias

- **Python 3.8+**
- **Requests** - Requisições HTTP
- **BeautifulSoup4** - Web scraping
- **Feedparser** - Parsing RSS
- **Google APIs** - Gmail automation
- **PyYAML** - Configurações
- **Logging** - Monitoramento

## 🔧 Troubleshooting

### Problema: Gmail API não autentica
```bash
# Verificar credenciais
ls -la credentials.json
# Reautenticar
rm token.json && python gmail_api_reporter.py
```

### Problema: Web scraping retorna poucos dados
```bash
# Testar isoladamente
python real_news_scraper.py
# Verificar logs
tail -f logs/scraper.log
```

### Problema: API TheSportsDB lenta
```bash
# Testar conexão
python real_sports_data.py
# Ajustar timeouts em real_sports_data.py
```

## 📝 Changelog

### v1.0.0 (Atual) - Dados Reais
- ✅ Substituição completa de dados fictícios
- ✅ Integração TheSportsDB API
- ✅ Web scraping 6 sites brasileiros
- ✅ Sistema Gmail API funcional
- ✅ Interface HTML moderna

### v2.0.0 (Planejado) - IA Curatorial
- 🔄 Arquitetura duas camadas
- 🔄 Coleta bruta automatizada
- 🔄 Curadoria Gemini AI
- 🔄 Armazenamento estruturado
- 🔄 Dashboard análise

## 👥 Contribuição

1. Fork do projeto
2. Criar branch feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit das mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abrir Pull Request

## 📄 Licença

Este projeto é propriedade da **Artplan** e destina-se ao uso interno para análise de mercado esportivo e otimização de estratégias de marketing digital.

## 📞 Contato

**Desenvolvido para**: Artplan - Agência de Marketing Digital
**Contato**: caio.castro@artplan.com.br
**Versão**: 1.0.0 (Dados Reais)

---

*Sistema desenvolvido para substituir completamente dados fictícios por informações reais coletadas de APIs oficiais e sites brasileiros, com foco em inteligência para mercado de apostas esportivas.*