import pickle
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
import pytz
import yaml
import json
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

# Importar nossos módulos de dados reais
from real_sports_data import get_today_events, get_tomorrow_events, get_recent_results, get_esports_events, get_weekly_schedule
from real_news_scraper import get_sports_news

class GmailAPISportsReportREAL:
    """Relatório esportivo com dados REAIS via Gmail API"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, config_file='env.yaml'):
        """Inicializa o sistema de relatório esportivo com dados reais"""
        self.config = self.load_config(config_file)
        self.service = None
        self.timezone = pytz.timezone('America/Sao_Paulo')
        
    def load_config(self, config_file):
        """Carrega configurações do arquivo YAML"""
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            return {}
    
    def authenticate_gmail(self):
        """Autentica com a API do Gmail"""
        creds = None
        
        # Verificar se já existe token salvo
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # Se não há credenciais válidas, fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Salvar credenciais para próxima execução
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Autenticação Gmail API realizada com sucesso!")
        return True
    
    def collect_real_sports_data(self):
        """Coleta dados esportivos reais de múltiplas fontes"""
        print("🔄 Coletando dados esportivos reais...")
        
        # Coletar dados de diferentes fontes
        today_events = get_today_events()
        tomorrow_events = get_tomorrow_events()
        recent_results = get_recent_results()
        esports_events = get_esports_events()
        weekly_schedule = get_weekly_schedule()
        
        return {
            'today_events': today_events,
            'tomorrow_events': tomorrow_events,
            'recent_results': recent_results,
            'esports_events': esports_events,
            'weekly_schedule': weekly_schedule
        }
    
    def collect_real_news(self):
        """Coleta notícias esportivas reais via web scraping"""
        print("📰 Coletando notícias esportivas reais...")
        return get_sports_news()
    
    def generate_html_report(self, sports_data, news_data):
        """Gera relatório HTML com dados reais"""
        current_time = datetime.now().strftime('%d/%m/%Y às %H:%M')
        
        # Estatísticas
        total_events = len(sports_data['today_events']) + len(sports_data['tomorrow_events'])
        total_news = len(news_data)
        total_results = len(sports_data['recent_results'])
        total_esports = len(sports_data['esports_events'])
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório Esportivo Artplan - Dados Reais</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 300;
                }}
                .subtitle {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 1.1em;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    padding: 30px;
                    background: #f8f9fa;
                }}
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                    border-left: 4px solid #007bff;
                }}
                .stat-number {{
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #007bff;
                    margin: 0;
                }}
                .stat-label {{
                    color: #666;
                    margin: 5px 0 0 0;
                    font-size: 0.9em;
                }}
                .section {{
                    padding: 30px;
                    border-bottom: 1px solid #eee;
                }}
                .section:last-child {{
                    border-bottom: none;
                }}
                .section-title {{
                    font-size: 1.8em;
                    margin: 0 0 20px 0;
                    color: #2c3e50;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                .badge {{
                    background: #28a745;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 0.7em;
                    font-weight: bold;
                }}
                .badge.api {{
                    background: #007bff;
                }}
                .badge.scraping {{
                    background: #fd7e14;
                }}
                .event-grid {{
                    display: grid;
                    gap: 15px;
                }}
                .event-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #007bff;
                }}
                .event-title {{
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 8px;
                }}
                .event-details {{
                    color: #666;
                    font-size: 0.9em;
                }}
                .news-grid {{
                    display: grid;
                    gap: 20px;
                }}
                .news-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #28a745;
                }}
                .news-title {{
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .news-title a {{
                    color: #2c3e50;
                    text-decoration: none;
                }}
                .news-title a:hover {{
                    color: #007bff;
                }}
                .news-meta {{
                    color: #666;
                    font-size: 0.8em;
                    margin-bottom: 10px;
                }}
                .news-description {{
                    color: #555;
                    font-size: 0.9em;
                }}
                .footer {{
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .no-data {{
                    text-align: center;
                    color: #666;
                    font-style: italic;
                    padding: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚽ Relatório Esportivo Artplan</h1>
                    <p class="subtitle">Sistema com Dados Reais • {current_time}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{total_events}</div>
                        <div class="stat-label">Eventos Programados</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{total_results}</div>
                        <div class="stat-label">Resultados Recentes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{total_news}</div>
                        <div class="stat-label">Notícias Coletadas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{total_esports}</div>
                        <div class="stat-label">Eventos E-sports</div>
                    </div>
                </div>
        """
        
        # Seção de Jogos de Hoje
        html_content += f"""
                <div class="section">
                    <h2 class="section-title">
                        🏆 Jogos de Hoje
                        <span class="badge api">API REAL</span>
                    </h2>
        """
        
        if sports_data['today_events']:
            html_content += '<div class="event-grid">'
            for event in sports_data['today_events']:
                html_content += f"""
                    <div class="event-card">
                        <div class="event-title">{event.get('home_team', 'N/A')} vs {event.get('away_team', 'N/A')}</div>
                        <div class="event-details">
                            📅 {event.get('date', 'N/A')} • ⏰ {event.get('time', 'N/A')}<br>
                            🏟️ {event.get('league', 'N/A')}<br>
                            📍 {event.get('venue', 'N/A') if event.get('venue') else 'Local não informado'}
                        </div>
                    </div>
                """
            html_content += '</div>'
        else:
            html_content += '<div class="no-data">Nenhum jogo programado para hoje</div>'
        
        html_content += '</div>'
        
        # Seção de Resultados Recentes
        html_content += f"""
                <div class="section">
                    <h2 class="section-title">
                        📊 Resultados Recentes
                        <span class="badge api">API REAL</span>
                    </h2>
        """
        
        if sports_data['recent_results']:
            html_content += '<div class="event-grid">'
            for result in sports_data['recent_results']:
                score = f"{result.get('home_score', 0)}-{result.get('away_score', 0)}"
                html_content += f"""
                    <div class="event-card">
                        <div class="event-title">{result.get('home_team', 'N/A')} {score} {result.get('away_team', 'N/A')}</div>
                        <div class="event-details">
                            📅 {result.get('date', 'N/A')}<br>
                            🏟️ {result.get('league', 'N/A')}<br>
                            📍 {result.get('venue', 'N/A') if result.get('venue') else 'Local não informado'}
                        </div>
                    </div>
                """
            html_content += '</div>'
        else:
            html_content += '<div class="no-data">Nenhum resultado recente disponível</div>'
        
        html_content += '</div>'
        
        # Seção de Jogos de Amanhã
        html_content += f"""
                <div class="section">
                    <h2 class="section-title">
                        📅 Jogos de Amanhã
                        <span class="badge api">API REAL</span>
                    </h2>
        """
        
        if sports_data['tomorrow_events']:
            html_content += '<div class="event-grid">'
            for event in sports_data['tomorrow_events']:
                html_content += f"""
                    <div class="event-card">
                        <div class="event-title">{event.get('home_team', 'N/A')} vs {event.get('away_team', 'N/A')}</div>
                        <div class="event-details">
                            📅 {event.get('date', 'N/A')} • ⏰ {event.get('time', 'N/A')}<br>
                            🏟️ {event.get('league', 'N/A')}<br>
                            📍 {event.get('venue', 'N/A') if event.get('venue') else 'Local não informado'}
                        </div>
                    </div>
                """
            html_content += '</div>'
        else:
            html_content += '<div class="no-data">Nenhum jogo programado para amanhã</div>'
        
        html_content += '</div>'
        
        # Seção de E-sports
        html_content += f"""
                <div class="section">
                    <h2 class="section-title">
                        🎮 E-sports
                        <span class="badge api">API REAL</span>
                    </h2>
        """
        
        if sports_data['esports_events']:
            html_content += '<div class="event-grid">'
            for event in sports_data['esports_events']:
                html_content += f"""
                    <div class="event-card">
                        <div class="event-title">{event.get('home_team', 'N/A')} vs {event.get('away_team', 'N/A')}</div>
                        <div class="event-details">
                            🎮 {event.get('game', event.get('league', 'N/A'))}<br>
                            📅 {event.get('date', 'N/A')} • ⏰ {event.get('time', 'N/A')}<br>
                            🏆 {event.get('league', 'N/A')}
                        </div>
                    </div>
                """
            html_content += '</div>'
        else:
            html_content += '<div class="no-data">Nenhum evento de e-sports programado</div>'
        
        html_content += '</div>'
        
        # Seção de Notícias
        html_content += f"""
                <div class="section">
                    <h2 class="section-title">
                        📰 Notícias Esportivas
                        <span class="badge scraping">WEB SCRAPING</span>
                    </h2>
        """
        
        if news_data:
            html_content += '<div class="news-grid">'
            for news in news_data[:10]:  # Mostrar apenas as 10 primeiras
                html_content += f"""
                    <div class="news-card">
                        <div class="news-title">
                            <a href="{news.get('link', '#')}" target="_blank">{news.get('title', 'Título não disponível')}</a>
                        </div>
                        <div class="news-meta">
                            📰 {news.get('source', 'Fonte não informada')} • 
                            🏷️ {news.get('category', 'Categoria não informada')}
                        </div>
                        <div class="news-description">{news.get('description', 'Descrição não disponível')}</div>
                    </div>
                """
            html_content += '</div>'
        else:
            html_content += '<div class="no-data">Nenhuma notícia disponível</div>'
        
        html_content += '</div>'
        
        # Footer
        html_content += f"""
                <div class="footer">
                    <p><strong>Sistema de Relatório Esportivo Artplan</strong></p>
                    <p>Dados coletados via TheSportsDB API e Web Scraping de sites brasileiros</p>
                    <p>Gerado em {current_time}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def send_email_report(self, html_content):
        """Envia o relatório por email via Gmail API"""
        try:
            # Configurações do email - múltiplas opções de configuração
            sender_email = (
                self.config.get('gmail', {}).get('sender_email') or
                self.config.get('SENDER_EMAIL') or
                self.config.get('EMAIL_FROM') or
                'analytics.artplan@gmail.com'
            )
            
            recipient_email = (
                self.config.get('gmail', {}).get('recipient_email') or
                self.config.get('email', {}).get('default_recipient') or
                self.config.get('RECIPIENTS') or
                self.config.get('EMAIL_TO') or
                'caio.castro@artplan.com.br'
            )
            
            print(f"📧 Enviando de: {sender_email}")
            print(f"📧 Enviando para: {recipient_email}")
            
            # Criar mensagem
            message = MIMEMultipart('alternative')
            message['Subject'] = f"⚽ Relatório Esportivo Artplan - {datetime.now().strftime('%d/%m/%Y')}"
            message['From'] = sender_email
            message['To'] = recipient_email
            
            # Adicionar conteúdo HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            # Codificar mensagem
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Enviar email
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"✅ Email enviado com sucesso! Message ID: {send_message['id']}")
            return True
            
        except HttpError as error:
            print(f"❌ Erro ao enviar email: {error}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False
    
    def generate_and_send_report(self):
        """Função principal que gera e envia o relatório completo"""
        print("🚀 Iniciando Sistema de Relatório Esportivo com Dados Reais")
        print("=" * 60)
        
        # Autenticar Gmail
        if not self.authenticate_gmail():
            print("❌ Falha na autenticação do Gmail")
            return False
        
        # Coletar dados esportivos reais
        sports_data = self.collect_real_sports_data()
        
        # Coletar notícias reais
        news_data = self.collect_real_news()
        
        # Gerar relatório HTML
        print("📄 Gerando relatório HTML...")
        html_content = self.generate_html_report(sports_data, news_data)
        
        # Enviar por email
        print("📧 Enviando relatório por email...")
        success = self.send_email_report(html_content)
        
        if success:
            print("\n✅ RELATÓRIO ENVIADO COM SUCESSO!")
            print("📊 Estatísticas do relatório:")
            print(f"   • Eventos hoje: {len(sports_data['today_events'])}")
            print(f"   • Eventos amanhã: {len(sports_data['tomorrow_events'])}")
            print(f"   • Resultados recentes: {len(sports_data['recent_results'])}")
            print(f"   • Eventos e-sports: {len(sports_data['esports_events'])}")
            print(f"   • Notícias coletadas: {len(news_data)}")
        else:
            print("\n❌ FALHA AO ENVIAR RELATÓRIO")
        
        return success

def main():
    """Função principal"""
    reporter = GmailAPISportsReportREAL()
    reporter.generate_and_send_report()

if __name__ == "__main__":
    main()