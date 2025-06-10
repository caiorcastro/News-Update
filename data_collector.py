#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAMADA 1: Coleta e Armazenamento Bruto de Dados Esportivos
Sistema que coleta TUDO que seja relevante e salva separadamente
Execução: Diária às 9h30 via agendamento
"""

import json
import os
from datetime import datetime, timedelta
import logging
import argparse
import pytz
from pathlib import Path

# Importar módulos existentes
from real_sports_data import (
    get_today_events, get_tomorrow_events, get_recent_results, 
    get_esports_events, get_weekly_schedule
)
from real_news_scraper import get_sports_news

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataCollectorBruto:
    """Coleta bruta de dados esportivos com armazenamento estruturado"""
    
    def __init__(self, data_dir='data/bruto'):
        """Inicializa o coletor de dados brutos"""
        self.data_dir = Path(data_dir)
        self.timezone = pytz.timezone('America/Sao_Paulo')
        self.timestamp = datetime.now(self.timezone)
        
        # Criar diretórios
        self.setup_directories()
        
    def setup_directories(self):
        """Cria estrutura de diretórios necessária"""
        directories = [
            self.data_dir,
            self.data_dir / 'daily',
            self.data_dir / 'archive',
            Path('logs')
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Diretórios criados: {self.data_dir}")
        
    def get_filename(self, data_type):
        """Gera nome do arquivo baseado no tipo e data"""
        date_str = self.timestamp.strftime('%Y%m%d')
        return self.data_dir / 'daily' / f"{data_type}_{date_str}.json"
    
    def save_data(self, data, filename, description):
        """Salva dados em arquivo JSON com metadados"""
        try:
            output = {
                'metadata': {
                    'timestamp': self.timestamp.isoformat(),
                    'data_type': description,
                    'total_items': len(data) if isinstance(data, list) else 1,
                    'collection_success': True,
                    'source': 'data_collector_bruto'
                },
                'data': data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
                
            logger.info(f"✅ {description}: {len(data) if isinstance(data, list) else 1} itens salvos em {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar {description}: {e}")
            return False
    
    def collect_sports_events(self):
        """Coleta eventos esportivos de hoje e amanhã"""
        logger.info("🏆 Coletando eventos esportivos...")
        
        # Eventos de hoje
        today_events = get_today_events()
        filename_today = self.get_filename('eventos_hoje')
        self.save_data(today_events, filename_today, 'Eventos de Hoje')
        
        # Eventos de amanhã
        tomorrow_events = get_tomorrow_events()
        filename_tomorrow = self.get_filename('eventos_amanha')
        self.save_data(tomorrow_events, filename_tomorrow, 'Eventos de Amanhã')
        
        # Consolidar eventos próximas 24h
        all_events = today_events + tomorrow_events
        filename_24h = self.get_filename('jogos_proximas_24h')
        self.save_data(all_events, filename_24h, 'Jogos Próximas 24h')
        
        return {
            'today': len(today_events),
            'tomorrow': len(tomorrow_events),
            'total_24h': len(all_events)
        }
    
    def collect_recent_results(self):
        """Coleta resultados recentes"""
        logger.info("📊 Coletando resultados recentes...")
        
        recent_results = get_recent_results()
        filename = self.get_filename('resultados_recentes')
        self.save_data(recent_results, filename, 'Resultados Recentes')
        
        return len(recent_results)
    
    def collect_esports_events(self):
        """Coleta eventos de e-sports"""
        logger.info("🎮 Coletando eventos de e-sports...")
        
        esports_events = get_esports_events()
        filename = self.get_filename('eventos_esports')
        self.save_data(esports_events, filename, 'Eventos E-sports')
        
        return len(esports_events)
    
    def collect_weekly_schedule(self):
        """Coleta programação semanal"""
        logger.info("📅 Coletando programação semanal...")
        
        weekly_schedule = get_weekly_schedule()
        filename = self.get_filename('programacao_semanal')
        self.save_data(weekly_schedule, filename, 'Programação Semanal')
        
        return len(weekly_schedule)
    
    def collect_news(self):
        """Coleta notícias esportivas brutas"""
        logger.info("📰 Coletando notícias esportivas...")
        
        # Coletar notícias das últimas 24h
        news_data = get_sports_news()
        
        # Adicionar timestamp para cada notícia
        for news in news_data:
            news['collected_at'] = self.timestamp.isoformat()
            news['collection_source'] = 'data_collector_bruto'
        
        filename = self.get_filename('noticias_brutas_ultimas_24h')
        self.save_data(news_data, filename, 'Notícias Brutas Últimas 24h')
        
        return len(news_data)
    
    def collect_market_data(self):
        """Coleta dados de mercado e transferências"""
        logger.info("💰 Coletando dados de mercado...")
        
        # Por agora, usar dados de notícias filtradas por mercado
        all_news = get_sports_news()
        market_news = [
            news for news in all_news 
            if any(keyword in news.get('title', '').lower() + news.get('description', '').lower() 
                  for keyword in ['transferência', 'contratação', 'venda', 'mercado', 'reforço'])
        ]
        
        filename = self.get_filename('dados_mercado')
        self.save_data(market_news, filename, 'Dados de Mercado')
        
        return len(market_news)
    
    def collect_trending_topics(self):
        """Coleta tópicos em alta baseado em notícias"""
        logger.info("📈 Analisando tópicos em alta...")
        
        all_news = get_sports_news()
        
        # Extrair palavras-chave mais frequentes
        keyword_count = {}
        trending_keywords = [
            'flamengo', 'palmeiras', 'corinthians', 'são paulo', 'santos',
            'vasco', 'botafogo', 'fluminense', 'brasileirão', 'libertadores',
            'copa do brasil', 'seleção', 'neymar', 'lesão', 'técnico'
        ]
        
        for news in all_news:
            text = f"{news.get('title', '')} {news.get('description', '')}".lower()
            for keyword in trending_keywords:
                if keyword in text:
                    keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
        
        # Ordenar por frequência
        trending = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        trending_data = {
            'period': '24h',
            'trending_keywords': [{'keyword': k, 'mentions': v} for k, v in trending],
            'related_news': [
                news for news in all_news 
                if any(keyword[0] in f"{news.get('title', '')} {news.get('description', '')}".lower() 
                      for keyword in trending[:5])
            ][:10]
        }
        
        filename = self.get_filename('topicos_trending')
        self.save_data(trending_data, filename, 'Tópicos em Alta')
        
        return len(trending_data['trending_keywords'])
    
    def archive_old_data(self, days_to_keep=7):
        """Arquiva dados antigos"""
        logger.info(f"🗄️ Arquivando dados antigos (>{days_to_keep} dias)...")
        
        cutoff_date = self.timestamp - timedelta(days=days_to_keep)
        daily_dir = self.data_dir / 'daily'
        archive_dir = self.data_dir / 'archive'
        
        archived_count = 0
        
        for file_path in daily_dir.glob('*.json'):
            # Extrair data do nome do arquivo
            try:
                date_str = file_path.stem.split('_')[-1]  # Pegar último elemento (data)
                file_date = datetime.strptime(date_str, '%Y%m%d')
                file_date = self.timezone.localize(file_date)
                
                if file_date < cutoff_date:
                    # Mover para arquivo
                    archive_path = archive_dir / file_path.name
                    file_path.rename(archive_path)
                    archived_count += 1
                    logger.info(f"Arquivado: {file_path.name}")
                    
            except (ValueError, IndexError) as e:
                logger.warning(f"Não foi possível processar arquivo {file_path.name}: {e}")
        
        logger.info(f"✅ {archived_count} arquivos antigos arquivados")
        return archived_count
    
    def generate_collection_summary(self, stats):
        """Gera resumo da coleta"""
        summary = {
            'collection_timestamp': self.timestamp.isoformat(),
            'collection_date': self.timestamp.strftime('%Y-%m-%d'),
            'collection_time': self.timestamp.strftime('%H:%M:%S'),
            'timezone': str(self.timezone),
            'statistics': stats,
            'total_items_collected': sum(v for v in stats.values() if isinstance(v, int)),
            'collection_success': True
        }
        
        # Salvar resumo
        summary_file = self.data_dir / f"collection_summary_{self.timestamp.strftime('%Y%m%d')}.json"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return summary
    
    def run_full_collection(self):
        """Executa coleta completa de todos os dados"""
        logger.info("🚀 Iniciando coleta bruta completa de dados esportivos")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        stats = {}
        
        try:
            # Coletar eventos esportivos
            events_stats = self.collect_sports_events()
            stats.update(events_stats)
            
            # Coletar resultados recentes
            stats['resultados_recentes'] = self.collect_recent_results()
            
            # Coletar e-sports
            stats['eventos_esports'] = self.collect_esports_events()
            
            # Coletar programação semanal
            stats['programacao_semanal'] = self.collect_weekly_schedule()
            
            # Coletar notícias
            stats['noticias_coletadas'] = self.collect_news()
            
            # Coletar dados de mercado
            stats['dados_mercado'] = self.collect_market_data()
            
            # Analisar tópicos trending
            stats['topicos_trending'] = self.collect_trending_topics()
            
            # Arquivar dados antigos
            stats['arquivos_antigos'] = self.archive_old_data()
            
            # Gerar resumo
            summary = self.generate_collection_summary(stats)
            
            # Calcular tempo total
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("=" * 60)
            logger.info("✅ COLETA BRUTA CONCLUÍDA COM SUCESSO!")
            logger.info(f"⏱️ Tempo total: {duration:.2f} segundos")
            logger.info("📊 Resumo da coleta:")
            
            for key, value in stats.items():
                if isinstance(value, int):
                    logger.info(f"   • {key.replace('_', ' ').title()}: {value}")
                elif isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        logger.info(f"   • {subkey.replace('_', ' ').title()}: {subvalue}")
            
            logger.info(f"📁 Dados salvos em: {self.data_dir}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Erro durante coleta: {e}")
            return None

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Coleta bruta de dados esportivos')
    parser.add_argument('--mode', choices=['bruto', 'test'], default='bruto',
                       help='Modo de execução')
    parser.add_argument('--data-dir', default='data/bruto',
                       help='Diretório para salvar dados')
    
    args = parser.parse_args()
    
    if args.mode == 'test':
        print("🧪 Modo de teste - executando coleta de exemplo...")
        
    # Inicializar coletor
    collector = DataCollectorBruto(data_dir=args.data_dir)
    
    # Executar coleta completa
    summary = collector.run_full_collection()
    
    if summary:
        print(f"\n✅ Coleta concluída! Total de itens: {summary['total_items_collected']}")
        print(f"📁 Dados salvos em: {args.data_dir}")
    else:
        print("\n❌ Falha na coleta!")

if __name__ == "__main__":
    main() 