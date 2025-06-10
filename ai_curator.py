#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAMADA 2: Curadoria Inteligente com IA - Gemini
Sistema que analisa dados brutos e filtra conteúdo estratégico para apostas esportivas
Execução: Após coleta bruta
"""

import json
import os
import logging
import argparse
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import google.generativeai as genai

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_curator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AICuratorBetMGM:
    """Curadoria inteligente para conteúdo estratégico de apostas esportivas"""
    
    def __init__(self, config_file='env.yaml'):
        """Inicializa o curador IA"""
        self.config = self.load_config(config_file)
        self.setup_gemini()
        self.timestamp = datetime.now()
        
        # Prompts específicos para diferentes tipos de análise
        self.prompts = {
            'news_curation': self.get_news_curation_prompt(),
            'events_analysis': self.get_events_analysis_prompt(),
            'market_impact': self.get_market_impact_prompt(),
            'betmgm_strategy': self.get_betmgm_strategy_prompt()
        }
        
    def load_config(self, config_file):
        """Carrega configurações do arquivo YAML"""
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            return {}
    
    def setup_gemini(self):
        """Configura a API do Gemini"""
        api_key = (
            self.config.get('gemini', {}).get('api_key') or
            self.config.get('GEMINI_API_KEY') or
            'AIzaSyAMH1RoJSjtPCes2G4fGjbraNH1FgP-tiM'  # Fallback
        )
        
        if not api_key:
            raise ValueError("Chave da API Gemini não encontrada")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("✅ Gemini AI configurado com sucesso")
    
    def get_news_curation_prompt(self):
        """Prompt para curadoria de notícias"""
        return """
        Você é um especialista em apostas esportivas e marketing de cassinos. 
        Analise as notícias esportivas fornecidas e selecione apenas aquelas que:

        CRITÉRIOS DE SELEÇÃO:
        1. 🎯 Possuem impacto direto em apostas esportivas:
           - Lesões de jogadores importantes
           - Mudanças de técnico
           - Clima extremo que afeta jogos
           - Suspensões ou problemas disciplinares
           - Mudanças de elenco de última hora

        2. 🏢 Relacionam-se com concorrentes da BetMGM:
           - Outras casas de apostas
           - Patrocínios esportivos
           - Regulamentação de apostas

        3. 🇧🇷 Têm alta atratividade para público apostador brasileiro:
           - Times populares (Flamengo, Palmeiras, Corinthians, etc.)
           - Seleção brasileira
           - Brasileirão, Libertadores, Copa do Brasil

        4. 📊 Priorização por relevância:
           - Futebol Brasileiro > Sul-Americano > Europeu > E-sports

        FORMATO DE RESPOSTA:
        Para cada notícia selecionada, forneça:
        - Título original
        - Por que é relevante para apostas
        - Impacto potencial nas odds
        - Público-alvo (apostadores de que tipo de jogo)
        - Nível de urgência (Alto/Médio/Baixo)

        Máximo: 10 notícias mais relevantes
        """
    
    def get_events_analysis_prompt(self):
        """Prompt para análise de eventos"""
        return """
        Você é um analista de apostas esportivas especializado no mercado brasileiro.
        Analise os jogos programados e selecione os 10 mais importantes para apostadores brasileiros.

        CRITÉRIOS DE SELEÇÃO:
        1. 🏆 Relevância para apostadores brasileiros:
           - Times brasileiros em qualquer competição
           - Seleção brasileira
           - Competições que brasileiros acompanham (Copa do Mundo, Libertadores)

        2. 📈 Potencial de apostas:
           - Jogos equilibrados (odds interessantes)
           - Clássicos ou rivalidades
           - Finais, semifinais, jogos decisivos
           - Primeira divisão vs divisões inferiores

        3. ⏰ Horário favorável:
           - Jogos em horário nobre brasileiro
           - Fins de semana
           - Feriados

        4. 🎮 E-sports relevantes:
           - Times brasileiros (LOUD, paiN, FURIA)
           - CBLOL, Valorant, CS2
           - Finais ou playoffs

        FORMATO DE RESPOSTA:
        Para cada jogo selecionado:
        - Times/Jogadores
        - Competição
        - Data e horário
        - Por que é relevante para apostas
        - Tipo de apostas mais populares esperadas
        - Potencial de audiência estimado

        Ordene por relevância decrescente.
        """
    
    def get_market_impact_prompt(self):
        """Prompt para análise de impacto no mercado"""
        return """
        Você é um estrategista de marketing para casas de apostas.
        Analise os dados fornecidos e identifique tendências e oportunidades.

        ANÁLISE REQUERIDA:
        1. 📊 Tendências de mercado:
           - Quais esportes/times estão em alta
           - Padrões de interesse do público
           - Sazonalidade

        2. 🎯 Oportunidades de marketing:
           - Momentos ideais para campanhas
           - Segmentos de público em crescimento
           - Eventos que geram engajamento

        3. ⚠️ Riscos e alertas:
           - Eventos que podem afetar negativamente apostas
           - Polêmicas ou crises
           - Mudanças regulatórias

        4. 📈 Previsões de performance:
           - Eventos com maior potencial de apostas
           - Horários de pico de atividade
           - Tendências emergentes

        FORMATO DE RESPOSTA:
        Forneça análise estruturada com:
        - Resumo executivo (3 pontos principais)
        - Oportunidades imediatas (5 itens)
        - Alertas e riscos (3 itens)
        - Recomendações estratégicas (5 ações)
        """
    
    def get_betmgm_strategy_prompt(self):
        """Prompt específico para estratégia BetMGM"""
        return """
        Você é o diretor de marketing da BetMGM Brasil.
        Baseado nos dados coletados, forneça uma análise estratégica para hoje.

        FOCO ESTRATÉGICO:
        1. 🎯 Competição direta:
           - O que concorrentes estão fazendo
           - Oportunidades de diferenciação
           - Timing de campanhas

        2. 💰 Maximização de revenue:
           - Jogos com maior potencial de apostas
           - Segmentos de usuários mais lucrativos
           - Produtos/odds a destacar

        3. 📱 Engajamento digital:
           - Conteúdo para redes sociais
           - Influenciadores a ativar
           - Hashtags e trends a aproveitar

        4. 🎪 Ativações especiais:
           - Promoções relâmpago
           - Bônus direcionados
           - Eventos ao vivo

        FORMATO DE RESPOSTA:
        1. **Visão Geral do Dia** (1 parágrafo)
        2. **Top 5 Oportunidades Imediatas** (bullets)
        3. **Ações Recomendadas** (lista priorizada)
        4. **Métricas a Monitorar** (KPIs específicos)
        5. **Timing Ideal** (quando executar cada ação)

        Seja específico, acionável e focado em resultados mensuráveis.
        """
    
    def load_raw_data(self, data_dir):
        """Carrega dados brutos da coleta"""
        data_dir = Path(data_dir)
        today = datetime.now().strftime('%Y%m%d')
        
        raw_data = {}
        data_files = {
            'noticias': f'noticias_brutas_ultimas_24h_{today}.json',
            'eventos_hoje': f'eventos_hoje_{today}.json',
            'eventos_amanha': f'eventos_amanha_{today}.json',
            'resultados': f'resultados_recentes_{today}.json',
            'esports': f'eventos_esports_{today}.json',
            'trending': f'topicos_trending_{today}.json',
            'mercado': f'dados_mercado_{today}.json'
        }
        
        for key, filename in data_files.items():
            file_path = data_dir / 'daily' / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        raw_data[key] = data.get('data', [])
                        logger.info(f"✅ Carregado {filename}: {len(raw_data[key])} itens")
                except Exception as e:
                    logger.error(f"❌ Erro ao carregar {filename}: {e}")
                    raw_data[key] = []
            else:
                logger.warning(f"⚠️ Arquivo não encontrado: {filename}")
                raw_data[key] = []
        
        return raw_data
    
    def curate_news(self, news_data):
        """Curadoria inteligente de notícias"""
        if not news_data:
            return []
        
        logger.info("📰 Iniciando curadoria de notícias...")
        
        # Preparar dados para o Gemini
        news_text = "NOTÍCIAS COLETADAS:\n\n"
        for i, news in enumerate(news_data[:20], 1):  # Limitar para não sobrecarregar
            news_text += f"{i}. TÍTULO: {news.get('title', 'N/A')}\n"
            news_text += f"   DESCRIÇÃO: {news.get('description', 'N/A')}\n"
            news_text += f"   FONTE: {news.get('source', 'N/A')}\n"
            news_text += f"   CATEGORIA: {news.get('category', 'N/A')}\n\n"
        
        try:
            prompt = self.prompts['news_curation'] + "\n\nDADOS:\n" + news_text
            response = self.model.generate_content(prompt)
            
            curated_analysis = {
                'analysis_timestamp': self.timestamp.isoformat(),
                'total_news_analyzed': len(news_data),
                'ai_analysis': response.text,
                'source_data': news_data[:10]  # Manter algumas originais para referência
            }
            
            logger.info(f"✅ Curadoria de notícias concluída")
            return curated_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na curadoria de notícias: {e}")
            return {'error': str(e), 'source_data': news_data}
    
    def analyze_events(self, events_data):
        """Análise inteligente de eventos esportivos"""
        all_events = []
        all_events.extend(events_data.get('eventos_hoje', []))
        all_events.extend(events_data.get('eventos_amanha', []))
        all_events.extend(events_data.get('esports', []))
        
        if not all_events:
            return []
        
        logger.info("🏆 Iniciando análise de eventos...")
        
        # Preparar dados para o Gemini
        events_text = "EVENTOS PROGRAMADOS:\n\n"
        for i, event in enumerate(all_events[:15], 1):
            events_text += f"{i}. {event.get('home_team', 'N/A')} vs {event.get('away_team', 'N/A')}\n"
            events_text += f"   COMPETIÇÃO: {event.get('league', 'N/A')}\n"
            events_text += f"   DATA: {event.get('date', 'N/A')} - HORÁRIO: {event.get('time', 'N/A')}\n"
            events_text += f"   ESPORTE: {event.get('sport', 'N/A')}\n\n"
        
        try:
            prompt = self.prompts['events_analysis'] + "\n\nDADOS:\n" + events_text
            response = self.model.generate_content(prompt)
            
            events_analysis = {
                'analysis_timestamp': self.timestamp.isoformat(),
                'total_events_analyzed': len(all_events),
                'ai_analysis': response.text,
                'source_data': all_events[:10]
            }
            
            logger.info(f"✅ Análise de eventos concluída")
            return events_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de eventos: {e}")
            return {'error': str(e), 'source_data': all_events}
    
    def analyze_market_impact(self, all_data):
        """Análise de impacto no mercado"""
        logger.info("📊 Iniciando análise de impacto no mercado...")
        
        # Preparar resumo dos dados
        summary_text = f"""
        RESUMO DOS DADOS COLETADOS:
        
        NOTÍCIAS: {len(all_data.get('noticias', []))} itens
        EVENTOS HOJE: {len(all_data.get('eventos_hoje', []))} jogos
        EVENTOS AMANHÃ: {len(all_data.get('eventos_amanha', []))} jogos
        RESULTADOS RECENTES: {len(all_data.get('resultados', []))} resultados
        E-SPORTS: {len(all_data.get('esports', []))} eventos
        DADOS MERCADO: {len(all_data.get('mercado', []))} itens
        
        TÓPICOS EM ALTA:
        """
        
        # Adicionar tópicos trending
        trending = all_data.get('trending', {})
        if trending and 'trending_keywords' in trending:
            for item in trending['trending_keywords'][:5]:
                summary_text += f"- {item.get('keyword', 'N/A')}: {item.get('mentions', 0)} menções\n"
        
        try:
            prompt = self.prompts['market_impact'] + "\n\nDADOS:\n" + summary_text
            response = self.model.generate_content(prompt)
            
            market_analysis = {
                'analysis_timestamp': self.timestamp.isoformat(),
                'ai_analysis': response.text,
                'data_summary': {
                    'total_news': len(all_data.get('noticias', [])),
                    'total_events': len(all_data.get('eventos_hoje', [])) + len(all_data.get('eventos_amanha', [])),
                    'total_esports': len(all_data.get('esports', [])),
                    'trending_topics': trending.get('trending_keywords', [])[:5]
                }
            }
            
            logger.info(f"✅ Análise de mercado concluída")
            return market_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de mercado: {e}")
            return {'error': str(e)}
    
    def generate_betmgm_strategy(self, all_data):
        """Gera estratégia específica para BetMGM"""
        logger.info("🎯 Gerando estratégia BetMGM...")
        
        # Preparar dados mais relevantes
        strategy_data = f"""
        DADOS PARA ESTRATÉGIA BETMGM:
        
        EVENTOS PRIORITÁRIOS HOJE:
        """
        
        for event in all_data.get('eventos_hoje', [])[:5]:
            strategy_data += f"- {event.get('home_team', 'N/A')} vs {event.get('away_team', 'N/A')} ({event.get('league', 'N/A')})\n"
        
        strategy_data += "\nNOTÍCIAS MAIS RELEVANTES:\n"
        for news in all_data.get('noticias', [])[:5]:
            strategy_data += f"- {news.get('title', 'N/A')} ({news.get('source', 'N/A')})\n"
        
        strategy_data += "\nTÓPICOS TRENDING:\n"
        trending = all_data.get('trending', {})
        if trending and 'trending_keywords' in trending:
            for item in trending['trending_keywords'][:3]:
                strategy_data += f"- {item.get('keyword', 'N/A')}: {item.get('mentions', 0)} menções\n"
        
        try:
            prompt = self.prompts['betmgm_strategy'] + "\n\nDADOS:\n" + strategy_data
            response = self.model.generate_content(prompt)
            
            strategy_analysis = {
                'analysis_timestamp': self.timestamp.isoformat(),
                'strategy_focus': 'BetMGM Brasil - Marketing e Revenue',
                'ai_strategy': response.text,
                'key_metrics': {
                    'priority_events': len(all_data.get('eventos_hoje', [])),
                    'news_impact': len(all_data.get('noticias', [])),
                    'trending_momentum': len(trending.get('trending_keywords', []))
                }
            }
            
            logger.info(f"✅ Estratégia BetMGM gerada")
            return strategy_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de estratégia: {e}")
            return {'error': str(e)}
    
    def save_curated_data(self, curated_data, output_dir):
        """Salva dados curados"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        for data_type, data in curated_data.items():
            filename = output_dir / f"{data_type}_curado_{timestamp}.json"
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"✅ Salvo: {filename}")
            except Exception as e:
                logger.error(f"❌ Erro ao salvar {data_type}: {e}")
    
    def run_full_curation(self, source_dir, output_dir):
        """Executa curadoria completa"""
        logger.info("🧠 Iniciando curadoria inteligente com IA")
        logger.info("=" * 60)
        
        # Carregar dados brutos
        raw_data = self.load_raw_data(source_dir)
        
        if not any(raw_data.values()):
            logger.error("❌ Nenhum dado bruto encontrado para curadoria")
            return None
        
        # Executar diferentes tipos de curadoria
        curated_data = {}
        
        # 1. Curadoria de notícias
        curated_data['noticias_curadas'] = self.curate_news(raw_data.get('noticias', []))
        
        # 2. Análise de eventos
        curated_data['eventos_analisados'] = self.analyze_events(raw_data)
        
        # 3. Análise de impacto no mercado
        curated_data['impacto_mercado'] = self.analyze_market_impact(raw_data)
        
        # 4. Estratégia BetMGM
        curated_data['estrategia_betmgm'] = self.generate_betmgm_strategy(raw_data)
        
        # 5. Resumo executivo
        curated_data['resumo_executivo'] = {
            'timestamp': self.timestamp.isoformat(),
            'total_data_processed': sum(len(v) if isinstance(v, list) else 1 for v in raw_data.values()),
            'analysis_types': list(curated_data.keys()),
            'processing_success': True
        }
        
        # Salvar dados curados
        self.save_curated_data(curated_data, output_dir)
        
        logger.info("=" * 60)
        logger.info("✅ CURADORIA INTELIGENTE CONCLUÍDA!")
        logger.info(f"📊 Tipos de análise: {len(curated_data)}")
        logger.info(f"📁 Dados salvos em: {output_dir}")
        
        return curated_data

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Curadoria inteligente de dados esportivos')
    parser.add_argument('--source', default='data/bruto',
                       help='Diretório com dados brutos')
    parser.add_argument('--output', default='data/curado',
                       help='Diretório para dados curados')
    
    args = parser.parse_args()
    
    # Inicializar curador
    curator = AICuratorBetMGM()
    
    # Executar curadoria completa
    result = curator.run_full_curation(args.source, args.output)
    
    if result:
        print(f"\n✅ Curadoria concluída!")
        print(f"📁 Dados curados salvos em: {args.output}")
    else:
        print("\n❌ Falha na curadoria!")

if __name__ == "__main__":
    main() 