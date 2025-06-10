import functions_framework
import os
from gmail_api_reporter import GmailAPISportsReport

@functions_framework.http
def daily_sports_report(request):
    """Entry point para Cloud Function - Relatório Esportivo Artplan via Gmail API"""
    try:
        # Configurações para Gmail API
        config = {
            'recipients': os.environ.get('RECIPIENTS', 'caio.castro@artplan.com.br').split(',')
        }
        
        print(f"🚀 Iniciando relatório esportivo via Gmail API")
        
        reporter = GmailAPISportsReport(config)
        report = reporter.generate_report()
        success = reporter.send_email(report)
        
        if success:
            print("✅ Relatório enviado com sucesso via Gmail API!")
            return {
                "status": "success", 
                "timestamp": reporter.today.isoformat(), 
                "sent_to": config['recipients'],
                "method": "Gmail API"
            }, 200
        else:
            print("❌ Falha no envio do relatório")
            return {"status": "error", "message": "Falha no envio do email"}, 500
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return {"status": "error", "message": str(e)}, 500 