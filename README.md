# 📊 Relatório Esportivo Artplan - Gmail API

Sistema automático que envia relatórios esportivos diários por email usando **Gmail API oficial** (mais seguro que App Password!).

## 🚀 **Novidades v2.0 - Gmail API**

✅ **Autenticação OAuth2** (mais segura)  
✅ **Rate limits maiores** (1 bilhão requests/dia)  
✅ **100% GRATUITO** (sem custos)  
✅ **API oficial do Google**  
✅ **TOP 10 oportunidades com IA**  

## 📋 **Funcionalidades**

- 🏆 **Jogos de futebol** (ontem, hoje, amanhã)
- 🎮 **E-sports eventos** (CBLOL, CS2, Valorant, Free Fire)
- 📅 **Feriados brasileiros** e eventos especiais
- 📰 **Notícias esportivas** relevantes
- 💡 **TOP 10 oportunidades de mídia** com insights de IA
- 📧 **Email HTML profissional** com visual Artplan
- ⏰ **Agendamento automático** (8h diário)

## 🔧 **Configuração - 3 Passos**

### **PASSO 1: Instalar Dependências**
```bash
pip3 install -r requirements.txt
```

### **PASSO 2: Configurar Gmail API**
```bash
python3 setup_gmail_oauth.py
```

O script vai te guiar para:
1. 🌐 Criar credenciais OAuth no Google Cloud
2. 🔐 Fazer login com analytics.artplan@gmail.com  
3. ✅ Testar Gmail API
4. 📝 Gerar configuração para Cloud Functions

### **PASSO 3: Deploy**
```bash
./deploy.sh
```

## 🧪 **Teste Local**

### Teste Básico (sem credenciais):
```bash
python3 -c "
from gmail_api_reporter import GmailAPISportsReport
reporter = GmailAPISportsReport({'recipients': ['caio.castro@artplan.com.br']})
print(reporter.generate_report())
"
```

### Teste Completo (com credenciais):
```bash
python3 test_gmail_api.py
```

## 📊 **Exemplo de Relatório**

```
📊 RELATÓRIO ESPORTIVO DIÁRIO ARTPLAN - 09/06/2025

🏆 JOGOS DE ONTEM (08/06):
- 16:00 - Flamengo vs Vasco - Brasileirão (Audiência: 8M)

⚽ JOGOS DE HOJE (09/06):
- 16:00 - Flamengo vs Vasco - Brasileirão (Audiência: 8M)

🔮 JOGOS DE AMANHÃ (10/06):
- 18:30 - Corinthians vs Palmeiras - Brasileirão (Audiência: 10M)

🎮 E-SPORTS HOJE:
- 20:00 - CBLOL: LOUD vs paiN Gaming (League of Legends) - Audiência: 800K

📅 EVENTOS ESPECIAIS:
- Corpus Christi (19/06) - em 9 dias - Monitorar campanhas

📰 NOTÍCIAS RELEVANTES:
- CBLOL: LOUD anuncia novo patrocinador principal
- Mercado esportivo brasileiro cresce 15% em 2024
- Copa do Mundo 2026: Brasil confirma participação

💡 TOP 10 OPORTUNIDADES DE MÍDIA:
 1. 📺 Flamengo vs Vasco (16:00) - Audiência esperada: 8M
 2. 🎮 CBLOL: LOUD vs paiN Gaming (20:00) - Público jovem: 800K
 3. ⏰ Prime time: 20h-22h - maior CPM e engajamento
 4. 📱 Mobile gaming: 70% audiência feminina 16-35 anos
 5. 🏟️ Temporada indoor: e-sports e futebol de salão
 6. 📈 Live streaming: crescimento 300% ano/ano
 7. 🎯 Retargeting pós-jogo: janela de 2h ideal para conversão
 8. 🤝 Parcerias influencers: jogadores brasileiros trending

---
🎯 Relatório Automático Artplan via Gmail API
📧 analytics.artplan@gmail.com
⏰ Próximo envio: amanhã às 08:00h
🔗 Dados em tempo real via APIs esportivas + IA
```

## ⚙️ **Configuração Google Cloud**

### Credenciais OAuth:
1. Acesse: https://console.cloud.google.com
2. APIs & Services → Credentials
3. CREATE CREDENTIALS → OAuth 2.0 Client IDs
4. Application type: Desktop application
5. Download JSON → execute setup_gmail_oauth.py

### Cloud Function:
- **Projeto**: peak-service-461120-h8 
- **Região**: us-central1
- **Runtime**: Python 3.9
- **Entry point**: daily_sports_report
- **Schedule**: 0 8 * * * (8h diário)

## 🔒 **Segurança Gmail API vs App Password**

| **Gmail API (Recomendado)** | **App Password (Antigo)** |
|------------------------------|---------------------------|
| ✅ OAuth2 seguro           | ❌ Password em texto      |
| ✅ Tokens expiram          | ❌ Password permanente    |
| ✅ Escopos limitados       | ❌ Acesso total           |
| ✅ Rate limits altos       | ❌ Rate limits baixos     |
| ✅ API oficial Google      | ❌ SMTP genérico          |

## 🏗️ **Arquitetura**

```
gmail_api_reporter.py    # Reporter principal com Gmail API
├── get_football_games() # TheSportsDB API
├── get_esports_events() # Eventos por dia da semana  
├── get_holidays_events() # Nager.Date API
├── get_sports_news()    # Notícias curadas
├── generate_opportunities() # IA para insights
└── send_email()         # Gmail API

main.py                  # Entry point Cloud Function
setup_gmail_oauth.py     # Configuração OAuth interativa
test_gmail_api.py       # Testes locais
deploy.sh               # Deploy automatizado
```

## 📦 **Arquivos**

- `gmail_api_reporter.py` - Classe principal com Gmail API
- `main.py` - Entry point para Cloud Function  
- `requirements.txt` - Dependências (inclui Google APIs)
- `env.yaml` - Variáveis de ambiente 
- `setup_gmail_oauth.py` - Configuração OAuth interativa
- `test_gmail_api.py` - Testes locais completos
- `deploy.sh` - Script de deploy automatizado

## 💰 **Custos**

- **Gmail API**: 100% GRATUITO (até 1 bilhão de requests/dia)
- **Cloud Functions**: GRATUITO (até 2M invocações/mês)
- **Cloud Scheduler**: GRATUITO (até 3 jobs)
- **APIs Esportivas**: GRATUITAS

**Total mensal**: R$ 0,00 ✅

## 🔧 **Troubleshooting**

### Erro de autenticação:
```bash
python3 setup_gmail_oauth.py  # Reconfigurar OAuth
```

### Testar apenas geração:
```bash
python3 test_gmail_api.py
```

### Verificar deployment:
```bash
gcloud functions describe daily-sports-report --region=us-central1
```

## 📞 **Suporte**

- **Email**: caio.castro@artplan.com.br
- **Projeto**: peak-service-461120-h8
- **Function**: daily-sports-report
- **Horário**: 8h diário (UTC-3)

---

🎯 **Artplan Analytics** | Powered by Gmail API + Google Cloud  
📧 analytics.artplan@gmail.com | Relatórios automatizados 