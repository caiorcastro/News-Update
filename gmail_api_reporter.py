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

# Importar nossos módulos de dados reais
from real_sports_data import RealSportsData
from real_news_scraper import RealNewsScraper

class GmailAPISportsReportREAL:
    """Relatório esportivo com dados REAIS via Gmail API"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, credentials_file='credentials.json', token_file='token.pickle', env_file='env.yaml'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.timezone = pytz.timezone('America/Sao_Paulo')
        
        # Carregar configurações
        self.config = self._load_config(env_file)
        
        # Inicializar coletores de dados REAIS
        self.sports_collector = RealSportsData()
        self.news_scraper = RealNewsScraper()
        
        self._authenticate()
    
    def _load_config(self, env_file):
        """Carrega configurações do arquivo env.yaml"""
        try:
            with open(env_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            return {}
    
    def _authenticate(self):
        """Autentica com Gmail API usando OAuth2"""
        creds = None
        
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Autenticação Gmail API realizada com sucesso!")
    
    def collect_real_data(self):
        """Coleta todos os dados REAIS"""
        print("🔄 Coletando dados esportivos REAIS...")
        
        # 1. Dados esportivos 
        print("📊 Buscando eventos esportivos...")
        sports_data = self.sports_collector.get_all_sports_data()
        
        # 2. Notícias via scraping melhorado
        print("📰 Coletando notícias...")
        news_data = self.news_scraper.get_all_news()
        
        return {
            'sports_data': sports_data,
            'news_data': news_data,
            'collection_time': datetime.now(self.timezone).strftime('%d/%m/%Y %H:%M')
        }
    
    def generate_html_report(self, data):
        """Gera relatório HTML com dados REAIS - versão limpa sem mentiras"""
        sports_data = data['sports_data']
        news_data = data['news_data']
        
        # Estatísticas dos dados coletados
        stats = {
            'games_today': len(sports_data.get('games_today', [])),
            'games_tomorrow': len(sports_data.get('games_tomorrow', [])),
            'recent_results': len(sports_data.get('recent_results', [])),
            'esports_events': len(sports_data.get('esports_today', [])),
            'total_news': len(news_data),
            'news_sources': len(set(n['source'] for n in news_data)) if news_data else 0
        }
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .subtitle {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 16px; }}
                .section {{ padding: 25px; border-bottom: 1px solid #eee; }}
                .section:last-child {{ border-bottom: none; }}
                .section h2 {{ color: #1e3c72; margin-top: 0; font-size: 22px; display: flex; align-items: center; }}
                .badge {{ background: #1e3c72; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin-left: 10px; }}
                .real-badge {{ background: #28a745; }}
                .live-badge {{ background: #dc3545; }}
                .game {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #1e3c72; }}
                .game-time {{ font-weight: bold; color: #1e3c72; font-size: 14px; }}
                .game-teams {{ font-size: 16px; font-weight: 600; margin: 5px 0; }}
                .game-info {{ font-size: 13px; color: #666; }}
                .result {{ background: #e8f5e8; border-left-color: #28a745; }}
                .result .game-time {{ color: #28a745; }}
                .news-item {{ padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #17a2b8; }}
                .news-link {{ color: #007bff; text-decoration: none; font-weight: 500; }}
                .news-link:hover {{ text-decoration: underline; }}
                .news-description {{ color: #666; font-size: 13px; margin-top: 5px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; margin: 20px 0; }}
                .stat-card {{ background: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center; }}
                .stat-number {{ font-size: 24px; font-weight: bold; color: #1976d2; }}
                .stat-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
                .footer {{ text-align: center; padding: 20px; background: #f8f9fa; color: #666; border-radius: 0 0 10px 10px; }}
                .esports {{ background: #fff3e0; border-left-color: #ff9800; }}
                .esports .game-time {{ color: #ff9800; }}
                .category-tag {{ background: #6c757d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-left: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏆 Relatório Esportivo Artplan</h1>
                    <p class="subtitle">Dados Coletados em Tempo Real • {data['collection_time']}</p>
                </div>
                
                <div class="section">
                    <h2>📊 Resumo dos Dados Coletados</h2>
                    <div class="stats">
                        <div class="stat-card">
                            <div class="stat-number">{stats['games_today']}</div>
                            <div class="stat-label">Jogos Hoje</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{stats['games_tomorrow']}</div>
                            <div class="stat-label">Jogos Amanhã</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{stats['recent_results']}</div>
                            <div class="stat-label">Resultados Recentes</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{stats['esports_events']}</div>
                            <div class="stat-label">E-sports</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{stats['total_news']}</div>
                            <div class="stat-label">Notícias</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{stats['news_sources']}</div>
                            <div class="stat-label">Fontes</div>
                        </div>
                    </div>
                </div>
        """
        
        # Seção de Jogos de Hoje
        if sports_data.get('games_today'):
            html_content += f"""
                <div class="section">
                    <h2>⚽ Jogos de Hoje <span class="badge real-badge">BRASILEIRÃO</span></h2>
            """
            for game in sports_data['games_today']:
                html_content += f"""
                    <div class="game">
                        <div class="game-time">{game.get('time', 'TBD')} • {game.get('date', '')}</div>
                        <div class="game-teams">{game.get('home_team', 'Time A')} vs {game.get('away_team', 'Time B')}</div>
                        <div class="game-info">{game.get('league', 'Liga')} • {game.get('venue', 'Estádio')} • {game.get('status', 'Agendado')}</div>
                    </div>
                """
            html_content += "</div>"
        
        # Seção de Resultados Recentes
        if sports_data.get('recent_results'):
            html_content += f"""
                <div class="section">
                    <h2>📈 Resultados Recentes <span class="badge live-badge">FINALIZADOS</span></h2>
            """
            for game in sports_data['recent_results']:
                html_content += f"""
                    <div class="game result">
                        <div class="game-time">{game.get('time', 'TBD')} • {game.get('date', '')}</div>
                        <div class="game-teams">{game.get('home_team', 'Time A')} {game.get('score', '0-0')} {game.get('away_team', 'Time B')}</div>
                        <div class="game-info">{game.get('league', 'Liga')} • {game.get('venue', 'Estádio')} • {game.get('attendance', 'Público')}</div>
                    </div>
                """
            html_content += "</div>"
        
        # Seção de Jogos de Amanhã
        if sports_data.get('games_tomorrow'):
            html_content += f"""
                <div class="section">
                    <h2>📅 Jogos de Amanhã <span class="badge">PROGRAMAÇÃO</span></h2>
            """
            for game in sports_data['games_tomorrow']:
                html_content += f"""
                    <div class="game">
                        <div class="game-time">{game.get('time', 'TBD')} • {game.get('date', '')}</div>
                        <div class="game-teams">{game.get('home_team', 'Time A')} vs {game.get('away_team', 'Time B')}</div>
                        <div class="game-info">{game.get('league', 'Liga')} • {game.get('venue', 'Estádio')} • {game.get('tv', 'TV')}</div>
                    </div>
                """
            html_content += "</div>"
        
        # Seção de E-sports
        if sports_data.get('esports_today'):
            html_content += f"""
                <div class="section">
                    <h2>🎮 E-sports Hoje <span class="badge">CBLOL • VALORANT</span></h2>
            """
            for game in sports_data['esports_today']:
                html_content += f"""
                    <div class="game esports">
                        <div class="game-time">{game.get('time', 'TBD')} • {game.get('date', '')}</div>
                        <div class="game-teams">{game.get('home_team', 'Team A')} vs {game.get('away_team', 'Team B')}</div>
                        <div class="game-info">{game.get('league', 'Liga')} • {game.get('game', 'Game')} • {game.get('viewers', 'Audiência')}</div>
                    </div>
                """
            html_content += "</div>"
        
        # Seção de Notícias REAIS
        if news_data:
            html_content += f"""
                <div class="section">
                    <h2>📰 Notícias Esportivas <span class="badge real-badge">{stats['news_sources']} FONTES</span></h2>
            """
            for news in news_data[:12]:  # Mostrar até 12 notícias
                html_content += f"""
                    <div class="news-item">
                        <a href="{news.get('link', '#')}" class="news-link" target="_blank">
                            {news.get('title', 'Título da notícia')}
                        </a>
                        <span class="category-tag">{news.get('category', news.get('source', 'Notícia'))}</span>
                        <div class="news-description">{news.get('description', '')}</div>
                        <small>{news.get('source', 'Fonte')} • {news.get('date', 'Data')}</small>
                    </div>
                """
            html_content += "</div>"
        
        html_content += f"""
                <div class="footer">
                    <p><strong>🚀 Sistema Artplan - Relatório Esportivo Automatizado</strong></p>
                    <p>📊 Dados coletados de múltiplas fontes • 📰 {stats['total_news']} notícias • ⚽ {stats['games_today'] + stats['games_tomorrow']} jogos</p>
                    <p><small>Relatório gerado automaticamente em {data['collection_time']}</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def send_report(self, recipient_email: str):
        """Envia relatório com dados REAIS via Gmail"""
        try:
            print("🔄 Iniciando coleta de dados REAIS...")
            
            # Coletar dados reais
            real_data = self.collect_real_data()
            
            print("📧 Gerando relatório HTML...")
            html_content = self.generate_html_report(real_data)
            
            print("📤 Enviando email...")
            
            # Criar mensagem
            message = MIMEMultipart('alternative')
            message['to'] = recipient_email
            message['from'] = 'artplan.sports.report@gmail.com'
            message['subject'] = f'🏆 Relatório Esportivo Artplan - {real_data["collection_time"]}'
            
            # Adicionar conteúdo HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            # Enviar
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            message_id = send_message.get('id')
            
            print(f"✅ Email enviado com sucesso!")
            print(f"📧 Destinatário: {recipient_email}")
            print(f"🆔 Message ID: {message_id}")
            print(f"📊 Dados coletados:")
            print(f"   • {len(real_data['sports_data'].get('games_today', []))} jogos hoje")
            print(f"   • {len(real_data['sports_data'].get('games_tomorrow', []))} jogos amanhã")
            print(f"   • {len(real_data['sports_data'].get('recent_results', []))} resultados recentes")
            print(f"   • {len(real_data['sports_data'].get('esports_today', []))} eventos de e-sports")
            print(f"   • {len(real_data['news_data'])} notícias de {len(set(n['source'] for n in real_data['news_data']))} fontes")
            
            return message_id
            
        except Exception as e:
            print(f"❌ Erro ao enviar relatório: {e}")
            return None

if __name__ == "__main__":
    # Teste do sistema completo com dados REAIS
    print("🚀 SISTEMA DE RELATÓRIO ESPORTIVO ARTPLAN")
    print("=" * 60)
    
    reporter = GmailAPISportsReportREAL()
    
    # Email de teste
    test_email = "caio.castro@artplan.com.br"
    
    print(f"📧 Enviando relatório para: {test_email}")
    message_id = reporter.send_report(test_email)
    
    if message_id:
        print(f"\n🎉 SUCESSO! Relatório esportivo enviado!")
        print(f"🆔 Message ID: {message_id}")
        print(f"✅ Contém jogos de hoje, amanhã, resultados recentes, e-sports e notícias reais")
    else:
        print("\n❌ Falha no envio do relatório")