#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste local do relatório esportivo Artplan
Execute este arquivo para testar antes do deploy
"""

import os
import sys
from sports_reporter import DailySportsReport

def test_report_generation():
    """Testa apenas a geração do relatório (sem envio de email)"""
    print("🚀 Testando geração do relatório...")
    
    # Configurações básicas (sem senha para teste)
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'email_user': 'analytics.artplan@gmail.com',
        'email_pass': 'TESTE_SEM_SENHA',
        'from_name': 'Relatório Esportivo Artplan',
        'recipients': ['caio.castro@artplan.com.br']
    }
    
    try:
        # Criar o reporter
        reporter = DailySportsReport(email_config)
        
        print("📊 Gerando relatório...")
        report = reporter.generate_report()
        
        print("\n" + "="*60)
        print("📋 RELATÓRIO GERADO COM SUCESSO:")
        print("="*60)
        print(report)
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {str(e)}")
        return False

def test_email_sending():
    """Testa o envio de email (só execute se tiver o App Password)"""
    print("\n🔐 Para testar envio de email, você precisa:")
    print("1. Ter configurado o App Password do Gmail")
    print("2. Colocado a senha no arquivo env.yaml")
    
    app_password = input("\n📧 Digite seu App Password do Gmail (ou ENTER para pular): ").strip()
    
    if not app_password:
        print("⏭️ Pulando teste de email...")
        return False
    
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'email_user': 'analytics.artplan@gmail.com',
        'email_pass': app_password,
        'from_name': 'Relatório Esportivo Artplan',
        'recipients': ['caio.castro@artplan.com.br']
    }
    
    try:
        print("📧 Testando envio de email...")
        reporter = DailySportsReport(email_config)
        report = reporter.generate_report()
        
        success = reporter.send_email(report)
        
        if success:
            print("✅ Email enviado com sucesso!")
            print("📬 Verifique sua caixa de entrada: caio.castro@artplan.com.br")
            return True
        else:
            print("❌ Falha no envio do email")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar email: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 TESTE DO RELATÓRIO ESPORTIVO ARTPLAN")
    print("="*50)
    
    # Teste 1: Geração do relatório
    if test_report_generation():
        print("\n✅ Geração do relatório: OK")
        
        # Teste 2: Envio de email (opcional)
        test_email = input("\n🤔 Quer testar o envio de email também? (s/n): ").lower().strip()
        
        if test_email == 's':
            if test_email_sending():
                print("\n✅ Envio de email: OK")
            else:
                print("\n⚠️ Envio de email: FALHOU")
        else:
            print("\n⏭️ Teste de email pulado")
            
    else:
        print("\n❌ Falha na geração do relatório")
        sys.exit(1)
    
    print("\n🎉 Testes concluídos!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Configure o App Password do Gmail")
    print("2. Atualize o arquivo env.yaml com a senha")
    print("3. Execute o deploy para Google Cloud Functions")
    
    print("\n💡 COMANDOS PARA DEPLOY:")
    print("gcloud config set project peak-service-461120-h8")
    print("gcloud functions deploy daily-sports-report --runtime python311 --trigger-http --entry-point daily_sports_report --env-vars-file env.yaml") 