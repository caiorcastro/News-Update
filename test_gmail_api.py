#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste local do relatório esportivo com Gmail API
Execute este arquivo para testar antes do deploy
"""

import os
import sys
from gmail_api_reporter import GmailAPISportsReport

def test_report_generation():
    """Testa apenas a geração do relatório"""
    print("🚀 Testando geração do relatório com Gmail API...")
    
    config = {
        'recipients': ['caio.castro@artplan.com.br']
    }
    
    try:
        reporter = GmailAPISportsReport(config)
        
        print("📊 Gerando relatório...")
        report = reporter.generate_report()
        
        print("\n" + "="*60)
        print("📋 RELATÓRIO GERADO COM SUCESSO (Gmail API):")
        print("="*60)
        print(report)
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {str(e)}")
        return False

def test_gmail_api_authentication():
    """Testa apenas a autenticação Gmail API"""
    print("\n🔐 Testando autenticação Gmail API...")
    
    config = {'recipients': ['caio.castro@artplan.com.br']}
    
    try:
        reporter = GmailAPISportsReport(config)
        
        if reporter.authenticate_gmail():
            print("✅ Autenticação Gmail API: OK")
            
            # Testar perfil
            profile = reporter.service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress')
            print(f"📧 Email autenticado: {email}")
            
            return True
        else:
            print("❌ Falha na autenticação Gmail API")
            return False
            
    except Exception as e:
        print(f"❌ Erro na autenticação: {str(e)}")
        return False

def test_email_sending():
    """Testa o envio de email via Gmail API"""
    print("\n📧 Testando envio de email via Gmail API...")
    
    config = {'recipients': ['caio.castro@artplan.com.br']}
    
    try:
        reporter = GmailAPISportsReport(config)
        report = reporter.generate_report()
        
        success = reporter.send_email(report)
        
        if success:
            print("✅ Email enviado com sucesso via Gmail API!")
            print("📬 Verifique sua caixa de entrada: caio.castro@artplan.com.br")
            return True
        else:
            print("❌ Falha no envio do email")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar email: {str(e)}")
        return False

def check_credentials():
    """Verifica se as credenciais estão configuradas"""
    print("🔍 Verificando credenciais...")
    
    files_to_check = [
        ('credentials.json', 'Credenciais OAuth do Google'),
        ('token.pickle', 'Token de autenticação (opcional)')
    ]
    
    all_good = True
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"✅ {description}: {filename}")
        else:
            if filename == 'token.pickle':
                print(f"⚠️  {description}: {filename} (será criado automaticamente)")
            else:
                print(f"❌ {description}: {filename} (OBRIGATÓRIO)")
                all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🎯 TESTE DO RELATÓRIO ESPORTIVO - GMAIL API")
    print("="*55)
    
    # Verificar credenciais
    if not check_credentials():
        print("\n❌ Credenciais não configuradas!")
        print("📋 Execute primeiro: python3 setup_gmail_oauth.py")
        sys.exit(1)
    
    print("\n" + "="*55)
    
    # Teste 1: Geração do relatório
    if test_report_generation():
        print("\n✅ Geração do relatório: OK")
        
        # Teste 2: Autenticação (opcional)
        test_auth = input("\n🤔 Quer testar a autenticação Gmail API? (s/n): ").lower().strip()
        
        if test_auth == 's':
            if test_gmail_api_authentication():
                print("\n✅ Autenticação Gmail API: OK")
                
                # Teste 3: Envio de email
                test_email = input("\n🤔 Quer testar o envio de email? (s/n): ").lower().strip()
                
                if test_email == 's':
                    if test_email_sending():
                        print("\n✅ Envio de email: OK")
                    else:
                        print("\n⚠️ Envio de email: FALHOU")
                else:
                    print("\n⏭️ Teste de email pulado")
            else:
                print("\n⚠️ Autenticação Gmail API: FALHOU")
        else:
            print("\n⏭️ Testes de API pulados")
            
    else:
        print("\n❌ Falha na geração do relatório")
        sys.exit(1)
    
    print("\n🎉 Testes concluídos!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. ✅ Sistema funcionando localmente")
    print("2. 📝 Configure as credenciais no env.yaml")
    print("3. 🚀 Execute o deploy: ./deploy.sh")
    
    print("\n💡 VANTAGENS DA GMAIL API:")
    print("• 🔒 Mais seguro que App Password")
    print("• ⚡ Autenticação OAuth oficial")
    print("• 📊 Rate limits maiores")
    print("• 🎯 TOP 10 oportunidades com IA") 