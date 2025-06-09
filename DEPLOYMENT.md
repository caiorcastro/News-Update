# 🚀 Guia de Deploy - Sistema de Relatório Esportivo ARTPLAN

## ✅ Status Atual
- **Sistema funcionando localmente:** ✅ 100%
- **Gmail API configurada:** ✅ OAuth2 ativo
- **Email teste enviado:** ✅ Sucesso
- **Repositório GitHub:** ✅ https://github.com/caiorcastro/News-Update

## 📋 Pré-requisitos

### 1. Gmail API Habilitada
- Acesse: https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=583662722025
- Clique em **ENABLE**

### 2. Google Cloud CLI
```bash
# Instalar (macOS)
curl https://sdk.cloud.google.com | bash
source ~/.bashrc

# Autenticar
gcloud auth login
gcloud config set project peak-service-461120-h8
```

## 🚀 Deploy para Google Cloud Functions

### 1. Configurar credenciais
```bash
# Copiar o arquivo de exemplo
cp env.yaml.example env.yaml

# Executar OAuth (gera as credenciais)
python oauth_simple.py
```

### 2. Deploy
```bash
# Executar script de deploy
./deploy.sh
```

### 3. Testar no Cloud
```bash
# Testar função deployada
gcloud functions call daily-sports-report
```

## 📧 Configuração de Email

### Gmail API (Recomendado) ✅
- **Método:** OAuth2
- **Rate Limit:** 1 bilhão requests/dia
- **Custo:** R$ 0,00
- **Segurança:** ⭐⭐⭐⭐⭐

### App Password (Alternativo)
- **Método:** SMTP
- **Rate Limit:** Padrão Gmail
- **Custo:** R$ 0,00
- **Segurança:** ⭐⭐⭐

## 🎯 Funcionalidades

- 📊 **Coleta de dados esportivos** (futebol, e-sports, feriados)
- 🤖 **TOP 10 oportunidades** geradas com IA (Gemini)
- 📧 **Envio automático** de relatórios HTML
- ⚡ **Rate limits altos** (1 bilhão requests/dia)
- 🔒 **Autenticação OAuth2** segura
- 💰 **Custo:** R$ 0,00 (100% gratuito)

## 📈 Monitoramento

### Logs do Cloud Functions
```bash
gcloud functions logs read daily-sports-report
```

### Métricas
- Acessar: https://console.cloud.google.com/functions
- Selecionar: daily-sports-report
- Aba: Metrics

## 🔧 Troubleshooting

### Erro: "Gmail API not enabled"
- Solução: Habilitar Gmail API no Google Cloud Console

### Erro: "Insufficient authentication scopes"
- Solução: Recriar token OAuth com `python oauth_simple.py`

### Erro: "Invalid request"
- Solução: Verificar credenciais no env.yaml

## 📞 Suporte

**Repositório:** https://github.com/caiorcastro/News-Update
**Email:** analytics.artplan@gmail.com 