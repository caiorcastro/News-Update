#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OAuth simples para Gmail API - usando localhost
"""

import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def simple_oauth():
    """Configuração OAuth simples"""
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    print('🔐 CONFIGURAÇÃO OAUTH SIMPLES - ARTPLAN')
    print('='*50)
    
    try:
        # Criar fluxo de autorização usando localhost
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        
        print('🌐 PASSO 1: Iniciando servidor local para OAuth...')
        print('🔑 PASSO 2: Faça login com: analytics.artplan@gmail.com')
        print('⚠️  Se aparecer "App not verified", clique em "Advanced" → "Go to ArtPlan automation (unsafe)"')
        print('📋 PASSO 3: Autorize o acesso e aguarde...')
        
        # Executar fluxo OAuth local (tentará diferentes portas)
        creds = flow.run_local_server(port=0)  # port=0 deixa o sistema escolher uma porta livre
        
        # Salvar credenciais
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        print('✅ Token OAuth salvo com sucesso!')
        
        # Testar Gmail API
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress')
        
        print(f'📧 Email autenticado: {email}')
        
        # Gerar configuração para env.yaml
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        creds_json = json.dumps(creds_data, separators=(',', ':'))
        
        print('\n📝 CONFIGURAÇÃO PARA env.yaml:')
        print('-' * 60)
        print('GOOGLE_CREDENTIALS_JSON: |')
        print(f'  {creds_json}')
        print('-' * 60)
        
        # Salvar em arquivo
        with open('google_credentials_env.txt', 'w') as f:
            f.write(f'GOOGLE_CREDENTIALS_JSON: |\n  {creds_json}\n')
        
        print('✅ Configuração salva em: google_credentials_env.txt')
        
        return True
        
    except Exception as e:
        print(f'❌ Erro: {str(e)}')
        print('\n💡 SOLUÇÃO: Adicione http://localhost:8080 nas Authorized redirect URIs do Google Cloud Console')
        print('   1. Vá para: https://console.cloud.google.com/apis/credentials')
        print('   2. Clique no Client ID OAuth 2.0')
        print('   3. Adicione http://localhost:8080 em "Authorized redirect URIs"')
        print('   4. Clique em "Save" e tente novamente')
        return False

if __name__ == "__main__":
    simple_oauth() 