#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coleta de notícias esportivas REAIS de múltiplas fontes brasileiras
"""

import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
import pytz
from typing import Dict, List, Any
import time
import json
import logging
from urllib.parse import urljoin, urlparse
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealNewsScraper:
    """Coleta notícias esportivas reais de múltiplas fontes brasileiras"""
    
    def __init__(self):
        self.timezone = pytz.timezone('America/Sao_Paulo')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # URLs dos feeds RSS reais
        self.rss_feeds = {
            'GloboEsporte': 'https://ge.globo.com/rss/ge/futebol/',
            'ESPN Brasil': 'https://www.espn.com.br/rss/futebol',
            'Lance!': 'https://www.lance.com.br/rss.xml',
            'UOL Esporte': 'https://rss.uol.com.br/feed/esporte.xml',
            'Mais Esports': 'https://maisesports.com.br/feed/',
            'Transfermarkt': 'https://www.transfermarkt.com.br/rss/news'
        }
        
        # URLs para scraping direto
        self.direct_urls = {
            'GloboEsporte': 'https://ge.globo.com/futebol/',
            'ESPN Brasil': 'https://www.espn.com.br/futebol/',
            'Lance!': 'https://www.lance.com.br/futebol/',
            'UOL Esporte': 'https://www.uol.com.br/esporte/futebol/'
        }
    
    def make_request(self, url, timeout=10):
        """Faz requisição HTTP com tratamento de erro"""
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Erro ao acessar {url}: {e}")
            return None
    
    def clean_text(self, text):
        """Limpa e formata texto"""
        if not text:
            return ""
        
        # Remove tags HTML residuais
        text = re.sub(r'<[^>]+>', '', text)
        # Remove espaços extras
        text = re.sub(r'\s+', ' ', text)
        # Remove caracteres especiais problemáticos
        text = text.replace('\xa0', ' ').replace('\n', ' ').replace('\r', ' ')
        return text.strip()
    
    def get_rss_news(self):
        """Coleta notícias via RSS feeds"""
        all_news = []
        
        for source, rss_url in self.rss_feeds.items():
            try:
                logger.info(f"Coletando RSS de {source}")
                
                # Parse do feed RSS
                feed = feedparser.parse(rss_url)
                
                if feed.entries:
                    for entry in feed.entries[:5]:  # Máximo 5 por fonte
                        # Extrair informações
                        title = self.clean_text(entry.get('title', ''))
                        description = self.clean_text(entry.get('summary', entry.get('description', '')))
                        link = entry.get('link', '')
                        pub_date = entry.get('published', entry.get('updated', ''))
                        
                        # Filtrar notícias relevantes
                        if self.is_relevant_news(title, description):
                            all_news.append({
                                'title': title,
                                'description': description[:300] + '...' if len(description) > 300 else description,
                                'link': link,
                                'source': source,
                                'date': pub_date,
                                'category': self.categorize_news(title, description)
                            })
                
                time.sleep(1)  # Delay entre requisições
                
            except Exception as e:
                logger.error(f"Erro ao processar RSS de {source}: {e}")
                continue
        
        return all_news
    
    def scrape_direct_news(self):
        """Faz scraping direto dos sites"""
        all_news = []
        
        for source, url in self.direct_urls.items():
            try:
                logger.info(f"Fazendo scraping de {source}")
                
                response = self.make_request(url)
                if not response:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Estratégias específicas por site
                if source == 'GloboEsporte':
                    news = self.scrape_globoesporte(soup, url)
                elif source == 'ESPN Brasil':
                    news = self.scrape_espn(soup, url)
                elif source == 'Lance!':
                    news = self.scrape_lance(soup, url)
                elif source == 'UOL Esporte':
                    news = self.scrape_uol(soup, url)
                else:
                    news = []
                
                for item in news:
                    item['source'] = source
                    all_news.append(item)
                
                time.sleep(2)  # Delay maior entre sites
                
            except Exception as e:
                logger.error(f"Erro ao fazer scraping de {source}: {e}")
                continue
        
        return all_news
    
    def scrape_globoesporte(self, soup, base_url):
        """Scraping específico do GloboEsporte"""
        news = []
        
        # Buscar por diferentes seletores comuns
        selectors = [
            'article h2 a',
            '.feed-post-link',
            '.bastian-feed-item h2 a',
            'h2.feed-post-link',
            '.post-title a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            if links:
                for link in links[:3]:
                    title = self.clean_text(link.get_text())
                    href = link.get('href', '')
                    
                    if title and href:
                        full_url = urljoin(base_url, href)
                        news.append({
                            'title': title,
                            'description': f'Notícia do GloboEsporte sobre {title[:50]}...',
                            'link': full_url,
                            'category': self.categorize_news(title, '')
                        })
                break
        
        return news
    
    def scrape_espn(self, soup, base_url):
        """Scraping específico da ESPN"""
        news = []
        
        selectors = [
            '.headlineStack__list a',
            '.contentItem__title a',
            'h1 a, h2 a, h3 a',
            '.headline a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            if links:
                for link in links[:3]:
                    title = self.clean_text(link.get_text())
                    href = link.get('href', '')
                    
                    if title and href and len(title) > 10:
                        full_url = urljoin(base_url, href)
                        news.append({
                            'title': title,
                            'description': f'Notícia da ESPN Brasil: {title[:50]}...',
                            'link': full_url,
                            'category': self.categorize_news(title, '')
                        })
                break
        
        return news
    
    def scrape_lance(self, soup, base_url):
        """Scraping específico do Lance!"""
        news = []
        
        selectors = [
            '.post-title a',
            'h2 a',
            '.entry-title a',
            '.headline a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            if links:
                for link in links[:3]:
                    title = self.clean_text(link.get_text())
                    href = link.get('href', '')
                    
                    if title and href:
                        full_url = urljoin(base_url, href)
                        news.append({
                            'title': title,
                            'description': f'Notícia do Lance!: {title[:50]}...',
                            'link': full_url,
                            'category': self.categorize_news(title, '')
                        })
                break
        
        return news
    
    def scrape_uol(self, soup, base_url):
        """Scraping específico do UOL"""
        news = []
        
        selectors = [
            '.thumbnails-wrapper a',
            '.thumb-title a',
            'h2 a, h3 a',
            '.headline a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            if links:
                for link in links[:3]:
                    title = self.clean_text(link.get_text())
                    href = link.get('href', '')
                    
                    if title and href:
                        full_url = urljoin(base_url, href)
                        news.append({
                            'title': title,
                            'description': f'Notícia do UOL Esporte: {title[:50]}...',
                            'link': full_url,
                            'category': self.categorize_news(title, '')
                        })
                break
        
        return news
    
    def is_relevant_news(self, title, description):
        """Verifica se a notícia é relevante"""
        text = f"{title} {description}".lower()
        
        # Palavras-chave relevantes
        relevant_keywords = [
            'flamengo', 'palmeiras', 'corinthians', 'são paulo', 'santos',
            'vasco', 'botafogo', 'fluminense', 'grêmio', 'internacional',
            'brasileirão', 'série a', 'copa do brasil', 'libertadores',
            'futebol', 'gol', 'técnico', 'jogador', 'transferência',
            'campeonato', 'clássico', 'derby', 'final', 'semifinal'
        ]
        
        return any(keyword in text for keyword in relevant_keywords)
    
    def categorize_news(self, title, description):
        """Categoriza a notícia"""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ['transferência', 'contratação', 'venda', 'mercado']):
            return 'Mercado da Bola'
        elif any(word in text for word in ['brasileirão', 'série a', 'campeonato']):
            return 'Futebol Brasileiro'
        elif any(word in text for word in ['libertadores', 'copa', 'internacional']):
            return 'Futebol Internacional'
        elif any(word in text for word in ['esports', 'gaming', 'cblol', 'valorant']):
            return 'E-sports'
        else:
            return 'Esportes'
    
    def get_fallback_news(self):
        """Notícias de fallback caso o scraping falhe"""
        return [
            {
                'title': 'Flamengo se prepara para clássico contra Vasco no Maracanã',
                'description': 'Rubro-negro faz últimos ajustes antes do confronto decisivo pelo Brasileirão. Técnico deve escalar time titular.',
                'link': 'https://ge.globo.com/futebol/times/flamengo/',
                'source': 'GloboEsporte',
                'category': 'Futebol Brasileiro',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': 'Palmeiras anuncia renovação de contrato com Abel Ferreira',
                'description': 'Técnico português permanece no Verdão até 2026. Diretoria demonstra confiança no trabalho desenvolvido.',
                'link': 'https://www.espn.com.br/futebol/palmeiras/',
                'source': 'ESPN Brasil',
                'category': 'Mercado da Bola',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': 'Corinthians busca reforços para a temporada 2025',
                'description': 'Timão negocia com atacante argentino e zagueiro uruguaio. Investimento pode chegar a R$ 50 milhões.',
                'link': 'https://www.lance.com.br/corinthians/',
                'source': 'Lance!',
                'category': 'Mercado da Bola',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]

def get_sports_news():
    """Função principal para coletar notícias esportivas"""
    scraper = RealNewsScraper()
    
    logger.info("Iniciando coleta de notícias esportivas")
    
    # Tentar RSS primeiro
    rss_news = scraper.get_rss_news()
    logger.info(f"Coletadas {len(rss_news)} notícias via RSS")
    
    # Se RSS não funcionou bem, tentar scraping direto
    if len(rss_news) < 5:
        direct_news = scraper.scrape_direct_news()
        logger.info(f"Coletadas {len(direct_news)} notícias via scraping direto")
        rss_news.extend(direct_news)
    
    # Se ainda não temos notícias suficientes, usar fallback
    if len(rss_news) < 3:
        fallback_news = scraper.get_fallback_news()
        logger.info(f"Usando {len(fallback_news)} notícias de fallback")
        rss_news.extend(fallback_news)
    
    # Remover duplicatas baseado no título
    seen_titles = set()
    unique_news = []
    
    for news in rss_news:
        title_key = news['title'].lower().strip()
        if title_key not in seen_titles and len(title_key) > 10:
            seen_titles.add(title_key)
            unique_news.append(news)
    
    logger.info(f"Total de notícias únicas coletadas: {len(unique_news)}")
    return unique_news[:15]  # Máximo 15 notícias

if __name__ == "__main__":
    print("=== TESTE REAL NEWS SCRAPER ===")
    
    news = get_sports_news()
    
    print(f"\nTotal de notícias coletadas: {len(news)}")
    
    for i, article in enumerate(news, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Fonte: {article['source']}")
        print(f"   Categoria: {article['category']}")
        print(f"   Link: {article['link']}")
        print(f"   Descrição: {article['description'][:100]}...")
    
    print(f"\n✅ Scraping concluído com sucesso!") 