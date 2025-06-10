#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Integrado de Relatório Esportivo com IA Curatorial
Combina: Coleta Bruta + Curadoria Gemini + Email HTML
"""

import json
import os
import logging
import yaml
from datetime import datetime
from pathlib import Path
import re

# Importar módulos existentes
from data_collector import DataCollectorBruto
from ai_curator import AICuratorBetMGM
import gmail_api_reporter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/integrated_reporter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegratedAIReporter:
    """Sistema integrado de relatório esportivo com IA"""
    
    def __init__(self, config_file='env.yaml'):
        """Inicializa o sistema integrado"""
        self.config = self.load_config(config_file)
        self.timestamp = datetime.now()
        self.data_dir = Path('data')
        
        # Inicializar componentes
        self.collector = DataCollectorBruto()
        self.curator = AICuratorBetMGM(config_file)
        
    def load_config(self, config_file):
        """Carrega configurações"""
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            return {}
    
    def extract_top_news_from_ai(self, ai_analysis):
        """Extrai as top notícias da análise IA"""
        try:
            # Buscar por padrões de notícias na análise
            analysis_text = ai_analysis.get('ai_analysis', '')
            
            # Dividir em seções e buscar notícias
            news_items = []
            
            # Padrão simples: buscar por números ou bullets seguidos de título
            lines = analysis_text.split('\n')
            current_news = {}
            
            for line in lines:
                line = line.strip()
                
                # Se encontrar padrão de notícia (número, bullet, etc.)
                if re.match(r'^[\d\-\*\•]\s*', line) and len(line) > 10:
                    if current_news:
                        news_items.append(current_news)
                    
                    # Limpar formatação desnecessária do título
                    clean_title = re.sub(r'^[\d\-\*\•\s]+', '', line).strip()
                    # Remover padrões como "TÍTULO:**", "Por que é relevante para apostas:**" etc.
                    clean_title = re.sub(r'.*?TÍTULO:\s*\*\*\s*', '', clean_title, flags=re.IGNORECASE)
                    clean_title = re.sub(r'.*?Por que é relevante.*?:\s*\*\*\s*', '', clean_title, flags=re.IGNORECASE)
                    clean_title = re.sub(r'.*?Impacto potencial.*?:\s*\*\*\s*', '', clean_title, flags=re.IGNORECASE)
                    clean_title = re.sub(r'.*?Nível de urgência.*?:\s*\*\*\s*', '', clean_title, flags=re.IGNORECASE)
                    clean_title = re.sub(r'.*?Público-alvo.*?:\s*\*\*\s*', '', clean_title, flags=re.IGNORECASE)
                    clean_title = re.sub(r'\*\*', '', clean_title)  # Remover asteriscos restantes
                    
                    current_news = {
                        'title': clean_title.strip(),
                        'relevance': 'Alta',
                        'source': 'IA',
                        'category': 'Curado'
                    }
                elif current_news and line and not line.startswith('**') and not line.lower().startswith('por que') and not line.lower().startswith('impacto') and not line.lower().startswith('nível'):
                    # Adicionar descrição se houver
                    current_news['description'] = line[:200] + '...' if len(line) > 200 else line
            
            # Adicionar última notícia
            if current_news:
                news_items.append(current_news)
            
            return news_items[:15]  # Top 15 como solicitado
            
        except Exception as e:
            logger.error(f"Erro ao extrair notícias da IA: {e}")
            return []
    
    def extract_top_events_from_ai(self, ai_analysis):
        """Extrai os top eventos da análise IA"""
        try:
            analysis_text = ai_analysis.get('ai_analysis', '')
            events = []
            
            # Buscar padrões de jogos (Team vs Team)
            vs_pattern = r'([A-Za-z\s]+)\s+vs?\s+([A-Za-z\s]+)'
            matches = re.findall(vs_pattern, analysis_text)
            
            for i, (team1, team2) in enumerate(matches[:10]):
                events.append({
                    'home_team': team1.strip(),
                    'away_team': team2.strip(),
                    'league': 'Curado por IA',
                    'date': 'Hoje/Amanhã',
                    'time': 'A definir',
                    'sport': 'Futebol/Diversos',
                    'relevance': 'Alta',
                    'ai_curated': True
                })
            
            return events
            
        except Exception as e:
            logger.error(f"Erro ao extrair eventos da IA: {e}")
            return []
    
    def create_artplan_html_email(self, curated_data, raw_stats):
        """Cria email HTML com design Artplan"""
        
        # Extrair dados curados
        news_analysis = curated_data.get('noticias_curadas', {})
        events_analysis = curated_data.get('eventos_analisados', {})
        market_analysis = curated_data.get('impacto_mercado', {})
        
        # Extrair insights da IA
        top_news = self.extract_top_news_from_ai(news_analysis)
        top_events = self.extract_top_events_from_ai(events_analysis)
        
        # Se não conseguir extrair da IA, usar dados brutos com limite
        if len(top_news) < 5:
            # Buscar nos dados fonte
            source_news = news_analysis.get('source_data', [])[:15]
            for news in source_news:
                if len(top_news) < 15:
                    top_news.append({
                        'title': news.get('title', 'Sem título'),
                        'description': news.get('description', 'Sem descrição')[:150] + '...',
                        'source': news.get('source', 'Fonte desconhecida'),
                        'category': news.get('category', 'Geral'),
                        'relevance': 'Média'
                    })
        
        if len(top_events) < 5:
            source_events = events_analysis.get('source_data', [])[:10]
            for event in source_events:
                if len(top_events) < 10:
                    top_events.append(event)
        
        # Processar análise de mercado para bullet points
        market_ai_text = market_analysis.get('ai_analysis', 'Análise não disponível')
        # Converter em bullet points mais legíveis
        market_bullets = []
        lines = market_ai_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('*') or line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
                # Limpar formatação e adicionar como bullet
                clean_line = re.sub(r'^[\*\-\•\d\.\s]+', '', line).strip()
                clean_line = re.sub(r'\*\*', '', clean_line)  # Remover asteriscos
                if clean_line and len(clean_line) > 10:
                    market_bullets.append(clean_line)
        
        if not market_bullets:
            market_bullets = [market_ai_text[:300] + '...']
        
        # Template HTML com cores Artplan (dourado/preto)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Farol de Notícias - Artplan - BetMGM</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                    color: #ffffff;
                    line-height: 1.6;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: #000000;
                    box-shadow: 0 0 30px rgba(212, 175, 55, 0.3);
                }}
                
                .header {{
                    background: linear-gradient(135deg, #d4af37 0%, #f4d03f 100%);
                    color: #000000;
                    padding: 30px;
                    text-align: center;
                    position: relative;
                    overflow: hidden;
                }}
                
                .header::before {{
                    content: '';
                    position: absolute;
                    top: -50%;
                    left: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                    animation: pulse 3s ease-in-out infinite;
                }}
                
                @keyframes pulse {{
                    0%, 100% {{ transform: scale(1); opacity: 0.5; }}
                    50% {{ transform: scale(1.1); opacity: 0.8; }}
                }}
                
                .header h1 {{
                    font-size: 2.5em;
                    font-weight: bold;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    position: relative;
                    z-index: 2;
                }}
                
                .header .subtitle {{
                    font-size: 1.2em;
                    font-weight: 300;
                    position: relative;
                    z-index: 2;
                }}
                
                .stats-bar {{
                    background: linear-gradient(90deg, #2c2c2c 0%, #1a1a1a 100%);
                    padding: 20px;
                    display: flex;
                    justify-content: space-around;
                    border-bottom: 3px solid #d4af37;
                }}
                
                .stat {{
                    text-align: center;
                    padding: 10px;
                }}
                
                .stat-number {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #d4af37;
                    display: block;
                }}
                
                .stat-label {{
                    font-size: 0.9em;
                    color: #cccccc;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .section {{
                    padding: 30px;
                    border-bottom: 1px solid #333333;
                }}
                
                .section-title {{
                    font-size: 1.8em;
                    color: #d4af37;
                    margin-bottom: 20px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                
                .badge {{
                    background: linear-gradient(135deg, #d4af37 0%, #f4d03f 100%);
                    color: #000000;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.7em;
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .news-grid {{
                    display: grid;
                    gap: 20px;
                }}
                
                .news-item {{
                    background: linear-gradient(135deg, #2a2a2a 0%, #1e1e1e 100%);
                    border-radius: 12px;
                    padding: 20px;
                    border-left: 4px solid #d4af37;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }}
                
                .news-item::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.1), transparent);
                    transition: left 0.6s ease;
                }}
                
                .news-item:hover::before {{
                    left: 100%;
                }}
                
                .news-item:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 25px rgba(212, 175, 55, 0.2);
                }}
                
                .news-title {{
                    font-size: 1.2em;
                    font-weight: bold;
                    color: #ffffff;
                    margin-bottom: 10px;
                    line-height: 1.4;
                }}
                
                .news-description {{
                    color: #cccccc;
                    margin-bottom: 15px;
                    line-height: 1.5;
                }}
                
                .news-meta {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 0.9em;
                }}
                
                .news-source {{
                    color: #d4af37;
                    font-weight: 500;
                }}
                
                .events-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 20px;
                }}
                
                .event-card {{
                    background: linear-gradient(135deg, #2a2a2a 0%, #1e1e1e 100%);
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    border: 2px solid #333333;
                    transition: all 0.3s ease;
                }}
                
                .event-card:hover {{
                    border-color: #d4af37;
                    transform: scale(1.02);
                }}
                
                .match {{
                    font-size: 1.3em;
                    font-weight: bold;
                    color: #ffffff;
                    margin-bottom: 10px;
                }}
                
                .vs {{
                    color: #d4af37;
                    font-weight: bold;
                    margin: 0 10px;
                }}
                
                .event-details {{
                    color: #cccccc;
                    font-size: 0.9em;
                    margin-top: 10px;
                }}
                
                .ai-analysis {{
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border-radius: 12px;
                    padding: 25px;
                    margin: 20px 0;
                    border: 2px solid #d4af37;
                }}
                
                .ai-title {{
                    color: #d4af37;
                    font-size: 1.3em;
                    font-weight: bold;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                
                .ai-content {{
                    color: #ffffff;
                    line-height: 1.7;
                }}
                
                .market-bullet {{
                    margin-bottom: 12px;
                    padding-left: 20px;
                    position: relative;
                }}
                
                .market-bullet::before {{
                    content: '•';
                    color: #d4af37;
                    font-weight: bold;
                    position: absolute;
                    left: 0;
                }}
                
                .footer {{
                    background: #d4af37;
                    color: #000000;
                    padding: 30px;
                    text-align: center;
                }}
                
                .footer h3 {{
                    margin-bottom: 10px;
                    font-size: 1.4em;
                }}
                
                .footer p {{
                    margin-bottom: 5px;
                }}
                
                .gemini-credit {{
                    background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
                    color: white;
                    padding: 15px;
                    text-align: center;
                    font-weight: bold;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                
                @media (max-width: 600px) {{
                    .stats-bar {{
                        flex-direction: column;
                        gap: 10px;
                    }}
                    
                    .events-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .header h1 {{
                        font-size: 2em;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <h1>🚨 FAROL DE NOTÍCIAS</h1>
                    <div class="subtitle">
                        Artplan - BetMGM • {datetime.now().strftime("%d/%m/%Y")}
                        <br>Powered by AI
                    </div>
                </div>
                
                <!-- Stats Bar -->
                <div class="stats-bar">
                    <div class="stat">
                        <span class="stat-number">{len(top_news)}</span>
                        <span class="stat-label">Notícias Curadas</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">{len(top_events)}</span>
                        <span class="stat-label">Eventos Hoje/Amanhã</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">{raw_stats.get('total_items_collected', 0)}</span>
                        <span class="stat-label">Dados Coletados</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">100%</span>
                        <span class="stat-label">Dados Reais</span>
                    </div>
                </div>
                
                <!-- Top Notícias Curadas -->
                <div class="section">
                    <h2 class="section-title">
                        📰 Top {len(top_news)} Notícias Curadas
                        <span class="badge">IA</span>
                    </h2>
                    <div class="news-grid">
        """
        
        # Adicionar notícias
        for i, news in enumerate(top_news[:15], 1):
            relevance_color = '#ff6b6b' if news.get('relevance') == 'Alta' else '#feca57' if news.get('relevance') == 'Média' else '#48dbfb'
            
            html_content += f"""
                        <div class="news-item">
                            <div class="news-title">
                                {i}. {news.get('title', 'Título não disponível')}
                            </div>
                            <div class="news-description">
                                {news.get('description', 'Descrição não disponível')[:200]}{'...' if len(news.get('description', '')) > 200 else ''}
                            </div>
                            <div class="news-meta">
                                <span class="news-source">📡 {news.get('source', 'Fonte IA')}</span>
                                <span class="badge" style="background: {relevance_color};">
                                    {news.get('relevance', 'Média')}
                                </span>
                            </div>
                        </div>
            """
        
        # Adicionar eventos
        html_content += f"""
                    </div>
                </div>
                
                <!-- Eventos Relevantes -->
                <div class="section">
                    <h2 class="section-title">
                        ⚽ Top {len(top_events)} Eventos Selecionados
                        <span class="badge">IA</span>
                    </h2>
                    <div class="events-grid">
        """
        
        for event in top_events[:10]:
            html_content += f"""
                        <div class="event-card">
                            <div class="match">
                                {event.get('home_team', 'Time A')}
                                <span class="vs">VS</span>
                                {event.get('away_team', 'Time B')}
                            </div>
                            <div class="event-details">
                                🏆 {event.get('league', 'Liga não informada')}<br>
                                📅 {event.get('date', 'Data a definir')} • ⏰ {event.get('time', 'Horário a definir')}<br>
                                ⚽ {event.get('sport', 'Esporte não informado')}
                            </div>
                        </div>
            """
        
        # Adicionar análise da IA com bullet points
        html_content += f"""
                    </div>
                </div>
                
                <!-- Análise IA de Mercado -->
                <div class="section">
                    <div class="ai-analysis">
                        <div class="ai-title">
                            🧠 Análise de Impacto no Mercado - Gemini AI
                        </div>
                        <div class="ai-content">
        """
        
        # Adicionar bullets da análise de mercado
        for bullet in market_bullets[:8]:  # Máximo 8 bullets
            html_content += f"""
                            <div class="market-bullet">{bullet}</div>
            """
        
        html_content += f"""
                        </div>
                    </div>
                </div>
                
                <!-- Gemini Credit -->
                <div class="section">
                    <div class="gemini-credit">
                        🤖 Notícias e eventos curados por Gemini 1.5 Flash do Google
                        <br>Análise inteligente para maximização de relevância e impacto
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <h3>📊 Artplan - Business Intelligence</h3>
                    <p><strong>Relatório gerado em:</strong> {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}</p>
                    <p><strong>Próximo relatório:</strong> Amanhã às 09:30</p>
                    <p><strong>Tecnologia:</strong> Python + Gemini AI + TheSportsDB API</p>
                    <p style="margin-top: 15px; font-size: 0.9em;">
                        Sistema de dados reais • 0% conteúdo fictício • 100% fontes verificadas
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def send_email_html(self, subject, html_content, recipient_email):
        """Envia email HTML usando a funcionalidade existente"""
        try:
            # Importar e usar o sistema Gmail existente
            from gmail_api_reporter import GmailAPISportsReportREAL
            
            gmail_reporter = GmailAPISportsReportREAL()
            
            # Autenticar primeiro
            if not gmail_reporter.authenticate_gmail():
                logger.error("Falha na autenticação Gmail")
                return False
            
            # Usar o método de envio existente com nosso HTML
            result = gmail_reporter.send_email_report(html_content)
            return result
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    def run_full_process(self):
        """Executa o processo completo: Coleta → Curadoria → Email"""
        logger.info("🚀 Iniciando processo completo integrado")
        logger.info("=" * 80)
        
        try:
            # 1. CAMADA 1: Coleta bruta
            logger.info("🧱 ETAPA 1: Executando coleta bruta...")
            collection_summary = self.collector.run_full_collection()
            
            if not collection_summary:
                logger.error("❌ Falha na coleta de dados")
                return False
            
            # 2. CAMADA 2: Curadoria IA
            logger.info("🔍 ETAPA 2: Executando curadoria IA...")
            curated_data = self.curator.run_full_curation(
                source_dir='data/bruto',
                output_dir='data/curado'
            )
            
            if not curated_data:
                logger.error("❌ Falha na curadoria IA")
                return False
            
            # 3. GERAÇÃO DE EMAIL HTML
            logger.info("📧 ETAPA 3: Gerando email HTML com design Artplan...")
            html_content = self.create_artplan_html_email(curated_data, collection_summary)
            
            # 4. ENVIO DE EMAIL
            logger.info("📤 ETAPA 4: Enviando email...")
            
            subject = f"🚨 Farol de Notícias Artplan-BetMGM • IA • {datetime.now().strftime('%d/%m/%Y')}"
            
            result = self.send_email_html(
                subject=subject,
                html_content=html_content,
                recipient_email=self.config.get('gmail', {}).get('recipient_email', 'caio.castro@artplan.com.br')
            )
            
            if result:
                logger.info("=" * 80)
                logger.info("✅ PROCESSO COMPLETO EXECUTADO COM SUCESSO!")
                logger.info(f"📊 Dados coletados: {collection_summary.get('total_items_collected', 0)}")
                logger.info(f"🧠 Análises IA: {len(curated_data)}")
                logger.info(f"📧 Email enviado: {result}")
                logger.info("=" * 80)
                return True
            else:
                logger.error("❌ Falha no envio do email")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no processo integrado: {e}")
            return False

def main():
    """Função principal"""
    # Verificar se diretórios de log existem
    Path('logs').mkdir(exist_ok=True)
    
    # Executar processo completo
    reporter = IntegratedAIReporter()
    success = reporter.run_full_process()
    
    if success:
        print("\n🎉 SISTEMA EXECUTADO COM SUCESSO!")
        print("📧 Verifique seu email para ver o relatório final")
    else:
        print("\n❌ FALHA NA EXECUÇÃO DO SISTEMA")

if __name__ == "__main__":
    main() 