#!/bin/bash
# Script de deploy automático para Google Cloud Functions
# Relatório Esportivo Artplan

echo "🚀 DEPLOY RELATÓRIO ESPORTIVO ARTPLAN"
echo "======================================"

# Verificar se o Google Cloud CLI está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI não encontrado!"
    echo "📥 Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Configurar projeto
echo "📋 Configurando projeto Google Cloud..."
gcloud config set project peak-service-461120-h8

# Verificar se os arquivos necessários existem
required_files=("main.py" "sports_reporter.py" "requirements.txt" "env.yaml")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Arquivo obrigatório não encontrado: $file"
        exit 1
    fi
done

echo "✅ Todos os arquivos encontrados!"

# Verificar se o App Password foi configurado
if grep -q "COLOQUE_APP_PASSWORD_AQUI" env.yaml; then
    echo "⚠️  ATENÇÃO: App Password não configurado!"
    echo "📧 Configure o App Password do Gmail no arquivo env.yaml"
    echo "🔗 Tutorial: https://support.google.com/accounts/answer/185833"
    
    read -p "🤔 Continuar mesmo assim? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "⏹️  Deploy cancelado"
        exit 1
    fi
fi

# Habilitar APIs necessárias
echo "🔧 Habilitando APIs do Google Cloud..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com

# Deploy da Cloud Function
echo "☁️  Fazendo deploy da Cloud Function..."
gcloud functions deploy daily-sports-report \
    --runtime python311 \
    --trigger-http \
    --entry-point daily_sports_report \
    --env-vars-file env.yaml \
    --memory 256MB \
    --timeout 300s \
    --region us-central1 \
    --allow-unauthenticated

if [ $? -eq 0 ]; then
    echo "✅ Cloud Function deploy concluído!"
    
    # Obter URL da função
    FUNCTION_URL=$(gcloud functions describe daily-sports-report --region=us-central1 --format="value(httpsTrigger.url)")
    echo "🔗 URL da função: $FUNCTION_URL"
    
    # Configurar agendamento (Cloud Scheduler)
    echo "⏰ Configurando agendamento diário..."
    
    # Verificar se já existe o job
    if gcloud scheduler jobs describe daily-sports-artplan --location=us-central1 &> /dev/null; then
        echo "📅 Job do scheduler já existe, atualizando..."
        gcloud scheduler jobs update http daily-sports-artplan \
            --location=us-central1 \
            --schedule="0 8 * * *" \
            --uri="$FUNCTION_URL" \
            --time-zone="America/Sao_Paulo"
    else
        echo "📅 Criando novo job do scheduler..."
        gcloud scheduler jobs create http daily-sports-artplan \
            --location=us-central1 \
            --schedule="0 8 * * *" \
            --uri="$FUNCTION_URL" \
            --time-zone="America/Sao_Paulo" \
            --description="Relatório esportivo diário Artplan"
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ Agendamento configurado!"
        echo ""
        echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
        echo "================================"
        echo "📧 Emails serão enviados todos os dias às 08:00 (horário de Brasília)"
        echo "📬 Destinatários: caio.castro@artplan.com.br, analytics.artplan@gmail.com"
        echo ""
        echo "🔧 COMANDOS ÚTEIS:"
        echo "• Testar manualmente: curl '$FUNCTION_URL'"
        echo "• Ver logs: gcloud functions logs read daily-sports-report"
        echo "• Ver agendamentos: gcloud scheduler jobs list"
        echo ""
        echo "🔗 Monitoramento:"
        echo "• Cloud Functions: https://console.cloud.google.com/functions"
        echo "• Cloud Scheduler: https://console.cloud.google.com/cloudscheduler"
    else
        echo "⚠️  Função deployada, mas erro no agendamento"
    fi
    
else
    echo "❌ Erro no deploy da Cloud Function"
    exit 1
fi

echo ""
echo "✨ Deploy finalizado!" 