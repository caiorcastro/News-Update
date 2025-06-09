#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração OAuth para Gmail API
Execute este arquivo para configurar as credenciais do Gmail
"""

import os
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes necessários para enviar emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def create_credentials_json():
    """Cria o arquivo credentials.json interativamente"""
    print("🔐 CONFIGURAÇÃO OAUTH GMAIL API")
    print("="*50)
    print()
    print("📋 PASSO 1: Vamos criar as credenciais OAuth")
    print()
    print("🌐 Primeiro, você precisa:")
    print("1. Acessar: https://console.cloud.google.com")
    print("2. Ir em 'APIs & Services' > 'Credentials'")
    print("3. Clicar em '+ CREATE CREDENTIALS' > 'OAuth 2.0 Client IDs'")
    print("4. Tipo de aplicação: 'Desktop application'")
    print("5. Nome: 'Relatório Esportivo Artplan'")
    print("6. Fazer download do arquivo JSON")
    print()
    
    choice = input("🤔 Você já tem o arquivo JSON das credenciais? (s/n): ").lower()
    
    if choice == 's':
        file_path = input("📁 Digite o caminho do arquivo JSON: ").strip()
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                credentials_data = json.load(f)
            
            # Salvar como credentials.json
            with open('credentials.json', 'w') as f:
                json.dump(credentials_data, f, indent=2)
            
            print("✅ Arquivo credentials.json criado!")
            return True
        else:
            print("❌ Arquivo não encontrado!")
            return False
    else:
        print("📝 Vou te ajudar a criar as credenciais manualmente...")
        print()
        print("Cole aqui o conteúdo do arquivo JSON (CTRL+V e depois ENTER duas vezes):")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "":
                    break
                lines.append(line)
            except EOFError:
                break
        
        json_content = '\n'.join(lines)
        
        try:
            credentials_data = json.loads(json_content)
            with open('credentials.json', 'w') as f:
                json.dump(credentials_data, f, indent=2)
            print("✅ Arquivo credentials.json criado!")
            return True
        except json.JSONDecodeError:
            print("❌ JSON inválido! Tente novamente.")
            return False

def setup_oauth():
    """Configura OAuth e gera token"""
    print("\n🔑 PASSO 2: Configurando OAuth...")
    
    if not os.path.exists('credentials.json'):
        print("❌ Arquivo credentials.json não encontrado!")
        if not create_credentials_json():
            return False
    
    creds = None
    
    # Verificar se já existe token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Se não tem credenciais válidas, fazer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Atualizando token expirado...")
            creds.refresh(Request())
        else:
            print("🌐 Abrindo navegador para autenticação...")
            print("📱 Faça login com: analytics.artplan@gmail.com")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salvar credenciais
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        print("✅ Token OAuth criado e salvo!")
    
    return creds

def test_gmail_api(creds):
    """Testa se a Gmail API está funcionando"""
    print("\n🧪 PASSO 3: Testando Gmail API...")
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Testar perfil do usuário
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress')
        
        print(f"✅ Gmail API funcionando!")
        print(f"📧 Email autenticado: {email}")
        
        if email != 'analytics.artplan@gmail.com':
            print("⚠️  ATENÇÃO: Email diferente do esperado!")
            print("   Esperado: analytics.artplan@gmail.com")
            print(f"   Atual: {email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar Gmail API: {str(e)}")
        return False

def generate_credentials_env():
    """Gera string de credenciais para variável de ambiente"""
    print("\n📋 PASSO 4: Gerando configuração para Cloud Functions...")
    
    if os.path.exists('credentials.json'):
        with open('credentials.json', 'r') as f:
            credentials_data = json.load(f)
        
        # Compactar JSON para uma linha
        credentials_json = json.dumps(credentials_data, separators=(',', ':'))
        
        print("📝 Adicione esta variável no arquivo env.yaml:")
        print()
        print("GOOGLE_CREDENTIALS_JSON: |")
        print(f"  {credentials_json}")
        print()
        
        # Salvar em arquivo
        with open('google_credentials_env.txt', 'w') as f:
            f.write(f"GOOGLE_CREDENTIALS_JSON: |\n  {credentials_json}\n")
        
        print("✅ Configuração salva em: google_credentials_env.txt")
        return True
    
    return False

def main():
    """Função principal"""
    print("🎯 CONFIGURAÇÃO GMAIL API - ARTPLAN")
    print("="*60)
    
    # Verificar se Google Cloud CLI está instalado
    if os.system("gcloud version > /dev/null 2>&1") != 0:
        print("⚠️  Google Cloud CLI não encontrado!")
        print("📥 Instale em: https://cloud.google.com/sdk/docs/install")
    
    # Configurar OAuth
    creds = setup_oauth()
    if not creds:
        print("❌ Falha na configuração OAuth")
        return
    
    # Testar API
    if not test_gmail_api(creds):
        print("❌ Falha no teste da Gmail API")
        return
    
    # Gerar configuração para Cloud Functions
    generate_credentials_env()
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("="*40)
    print("📋 PRÓXIMOS PASSOS:")
    print("1. ✅ OAuth configurado")
    print("2. ✅ Gmail API testada")
    print("3. 📝 Atualize o env.yaml com as credenciais")
    print("4. 🚀 Execute: ./deploy.sh")
    print()
    print("💡 Os arquivos token.pickle e credentials.json foram criados")
    print("   Mantenha-os seguros!")

if __name__ == "__main__":
    main() 