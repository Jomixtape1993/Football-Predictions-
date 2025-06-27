#!/usr/bin/env python3
"""
Motor de Previsão para Apostas Desportivas de Futebol
Autor: Manus AI
Data: 27/06/2025

Este módulo implementa o algoritmo de análise e previsão baseado em:
- Desempenho da equipa (40%)
- Desempenho dos jogadores (25%)
- Lesões (15%)
- Histórico de confrontos diretos (10%)
- Fator casa/fora (10%)
"""

import math
import sqlite3
from typing import Dict, List, Tuple, Optional
from football_betting_analyzer import FootballDataCollector
import logging

logger = logging.getLogger(__name__)

class FootballPredictionEngine:
    """Motor de previsão para jogos de futebol."""
    
    def __init__(self, db_path: str = "football_data.db"):
        self.db_path = db_path
        self.collector = FootballDataCollector(db_path)
        
        # Ponderações para cada componente da análise
        self.weights = {
            'team_performance': 0.40,
            'player_performance': 0.25,
            'injuries': 0.15,
            'head_to_head': 0.10,
            'home_away': 0.10
        }
    
    def calculate_team_strength(self, id_equipa: int, num_jogos: int = 10) -> float:
        """Calcula a força da equipa baseada no desempenho recente."""
        performance = self.collector.get_team_performance(id_equipa, num_jogos)
        
        if not performance or performance.get('total_jogos', 0) == 0:
            return 0.5  # Valor neutro se não há dados
        
        # Normalizar métricas (0-1)
        goal_diff_score = min(max((performance['diferenca_golos'] + 3) / 6, 0), 1)
        shots_score = min(performance['media_remates_baliza'] / 10, 1)
        possession_score = performance['media_posse_bola'] / 100
        clean_sheets_score = performance['percentagem_clean_sheets'] / 100
        
        # Penalizar cartões
        cards_penalty = min((performance['media_cartoes_amarelos'] + 
                           performance['media_cartoes_vermelhos'] * 3) / 10, 0.3)
        
        # Calcular força da equipa
        team_strength = (
            goal_diff_score * 0.4 +
            shots_score * 0.2 +
            possession_score * 0.2 +
            clean_sheets_score * 0.2 -
            cards_penalty
        )
        
        return max(min(team_strength, 1.0), 0.0)
    
    def calculate_player_impact(self, id_equipa: int, num_jogos: int = 20) -> float:
        """Calcula o impacto dos jogadores chave da equipa."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obter jogadores da equipa
        cursor.execute('''
            SELECT id_jogador, nome_jogador, posicao
            FROM jogador
            WHERE id_equipa = ?
        ''', (id_equipa,))
        
        players = cursor.fetchall()
        conn.close()
        
        if not players:
            return 0.5  # Valor neutro se não há jogadores
        
        total_impact = 0
        player_count = 0
        
        for player_id, nome, posicao in players:
            performance = self.collector.get_player_performance(player_id, num_jogos)
            
            if performance and performance.get('total_jogos', 0) > 0:
                # Calcular impacto baseado na posição
                if posicao in ['Avançado', 'Extremo']:
                    # Atacantes: golos e assistências são mais importantes
                    impact = (
                        performance['total_golos'] * 0.6 +
                        performance['total_assistencias'] * 0.4
                    ) / performance['total_jogos']
                elif posicao in ['Médio', 'Médio Defensivo', 'Médio Ofensivo']:
                    # Médios: assistências, passes e desarmes
                    impact = (
                        performance['total_assistencias'] * 0.4 +
                        performance['media_passes_completos'] / 100 * 0.3 +
                        performance['media_desarmes'] * 0.3
                    )
                else:  # Defesas e Guarda-redes
                    # Defesas: desarmes, interceções, menos cartões
                    impact = (
                        performance['media_desarmes'] * 0.4 +
                        performance['media_intercecoes'] * 0.4 -
                        performance['total_cartoes_amarelos'] * 0.1 -
                        performance['total_cartoes_vermelhos'] * 0.3
                    ) / performance['total_jogos']
                
                # Normalizar impacto (0-1)
                impact = max(min(impact / 2, 1.0), 0.0)
                total_impact += impact
                player_count += 1
        
        return total_impact / player_count if player_count > 0 else 0.5
    
    def calculate_injury_impact(self, id_equipa: int) -> float:
        """Calcula o impacto das lesões na equipa."""
        injuries = self.collector.get_team_injuries(id_equipa)
        
        if not injuries:
            return 1.0  # Sem lesões = impacto máximo
        
        total_impact = 0
        for injury in injuries:
            # Impacto baseado na gravidade e importância do jogador
            gravidade_multiplier = {
                'Ligeira': 0.1,
                'Moderada': 0.3,
                'Grave': 0.6,
                'Muito Grave': 0.9
            }.get(injury['gravidade'], 0.3)
            
            # Impacto baseado na importância do jogador (1-5)
            player_importance = injury['impacto_equipa'] / 5
            
            total_impact += gravidade_multiplier * player_importance
        
        # Converter para fator positivo (menos lesões = melhor)
        injury_factor = max(1.0 - (total_impact / len(injuries)), 0.1)
        return injury_factor
    
    def calculate_head_to_head_factor(self, id_equipa1: int, id_equipa2: int) -> float:
        """Calcula o fator de confrontos diretos."""
        h2h = self.collector.get_head_to_head(id_equipa1, id_equipa2)
        
        if not h2h or h2h.get('total_confrontos', 0) == 0:
            return 0.5  # Valor neutro se não há histórico
        
        # Percentagem de vitórias da equipa 1
        win_percentage = h2h['percentagem_vitorias_equipa1'] / 100
        
        # Ajustar baseado na diferença de golos
        goal_diff = h2h['media_golos_equipa1'] - h2h['media_golos_equipa2']
        goal_factor = min(max((goal_diff + 2) / 4, 0), 1)
        
        # Combinar fatores
        h2h_factor = (win_percentage * 0.7 + goal_factor * 0.3)
        
        return h2h_factor
    
    def calculate_home_away_factor(self, is_home: bool, id_equipa: int) -> float:
        """Calcula o fator casa/fora."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if is_home:
            # Desempenho em casa
            cursor.execute('''
                SELECT 
                    AVG(CASE WHEN j.golos_casa > j.golos_fora THEN 1 ELSE 0 END) as win_rate,
                    AVG(j.golos_casa) as avg_goals_scored,
                    AVG(j.golos_fora) as avg_goals_conceded
                FROM jogo j
                WHERE j.id_equipa_casa = ? AND j.status = 'finalizado'
                ORDER BY j.data_jogo DESC
                LIMIT 10
            ''', (id_equipa,))
        else:
            # Desempenho fora
            cursor.execute('''
                SELECT 
                    AVG(CASE WHEN j.golos_fora > j.golos_casa THEN 1 ELSE 0 END) as win_rate,
                    AVG(j.golos_fora) as avg_goals_scored,
                    AVG(j.golos_casa) as avg_goals_conceded
                FROM jogo j
                WHERE j.id_equipa_fora = ? AND j.status = 'finalizado'
                ORDER BY j.data_jogo DESC
                LIMIT 10
            ''', (id_equipa,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result or result[0] is None:
            # Fator padrão: casa tem vantagem
            return 0.6 if is_home else 0.4
        
        win_rate, avg_scored, avg_conceded = result
        
        # Calcular fator baseado na taxa de vitórias e diferença de golos
        goal_diff_factor = min(max((avg_scored - avg_conceded + 2) / 4, 0), 1)
        home_away_factor = (win_rate * 0.7 + goal_diff_factor * 0.3)
        
        # Aplicar bónus casa se aplicável
        if is_home:
            home_away_factor = min(home_away_factor + 0.1, 1.0)
        
        return home_away_factor
    
    def predict_match(self, id_equipa_casa: int, id_equipa_fora: int) -> Dict:
        """Faz a previsão completa de um jogo."""
        
        # 1. Calcular força das equipas (40%)
        team_strength_home = self.calculate_team_strength(id_equipa_casa)
        team_strength_away = self.calculate_team_strength(id_equipa_fora)
        
        # 2. Calcular impacto dos jogadores (25%)
        player_impact_home = self.calculate_player_impact(id_equipa_casa)
        player_impact_away = self.calculate_player_impact(id_equipa_fora)
        
        # 3. Calcular impacto das lesões (15%)
        injury_impact_home = self.calculate_injury_impact(id_equipa_casa)
        injury_impact_away = self.calculate_injury_impact(id_equipa_fora)
        
        # 4. Calcular fator de confrontos diretos (10%)
        h2h_factor_home = self.calculate_head_to_head_factor(id_equipa_casa, id_equipa_fora)
        h2h_factor_away = 1.0 - h2h_factor_home
        
        # 5. Calcular fator casa/fora (10%)
        home_factor = self.calculate_home_away_factor(True, id_equipa_casa)
        away_factor = self.calculate_home_away_factor(False, id_equipa_fora)
        
        # Calcular pontuação final ponderada
        score_home = (
            team_strength_home * self.weights['team_performance'] +
            player_impact_home * self.weights['player_performance'] +
            injury_impact_home * self.weights['injuries'] +
            h2h_factor_home * self.weights['head_to_head'] +
            home_factor * self.weights['home_away']
        )
        
        score_away = (
            team_strength_away * self.weights['team_performance'] +
            player_impact_away * self.weights['player_performance'] +
            injury_impact_away * self.weights['injuries'] +
            h2h_factor_away * self.weights['head_to_head'] +
            away_factor * self.weights['home_away']
        )
        
        # Normalizar pontuações para probabilidades
        total_score = score_home + score_away
        if total_score > 0:
            prob_home_win = score_home / total_score
            prob_away_win = score_away / total_score
        else:
            prob_home_win = prob_away_win = 0.5
        
        # Calcular probabilidade de empate (baseada na proximidade das pontuações)
        score_diff = abs(score_home - score_away)
        prob_draw = max(0.1, 0.3 - score_diff)
        
        # Normalizar todas as probabilidades
        total_prob = prob_home_win + prob_away_win + prob_draw
        prob_home_win /= total_prob
        prob_away_win /= total_prob
        prob_draw /= total_prob
        
        # Obter nomes das equipas
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT nome_equipa FROM equipa WHERE id_equipa = ?', (id_equipa_casa,))
        nome_casa = cursor.fetchone()[0]
        
        cursor.execute('SELECT nome_equipa FROM equipa WHERE id_equipa = ?', (id_equipa_fora,))
        nome_fora = cursor.fetchone()[0]
        
        conn.close()
        
        # Determinar previsão principal
        if prob_home_win > prob_away_win and prob_home_win > prob_draw:
            prediction = f"Vitória {nome_casa}"
            confidence = prob_home_win
        elif prob_away_win > prob_draw:
            prediction = f"Vitória {nome_fora}"
            confidence = prob_away_win
        else:
            prediction = "Empate"
            confidence = prob_draw
        
        return {
            'equipa_casa': nome_casa,
            'equipa_fora': nome_fora,
            'previsao_principal': prediction,
            'confianca': round(confidence * 100, 1),
            'probabilidades': {
                'vitoria_casa': round(prob_home_win * 100, 1),
                'empate': round(prob_draw * 100, 1),
                'vitoria_fora': round(prob_away_win * 100, 1)
            },
            'analise_detalhada': {
                'forca_equipa_casa': round(team_strength_home, 3),
                'forca_equipa_fora': round(team_strength_away, 3),
                'impacto_jogadores_casa': round(player_impact_home, 3),
                'impacto_jogadores_fora': round(player_impact_away, 3),
                'impacto_lesoes_casa': round(injury_impact_home, 3),
                'impacto_lesoes_fora': round(injury_impact_away, 3),
                'fator_confrontos_diretos_casa': round(h2h_factor_home, 3),
                'fator_confrontos_diretos_fora': round(h2h_factor_away, 3),
                'fator_casa': round(home_factor, 3),
                'fator_fora': round(away_factor, 3)
            },
            'pontuacao_final': {
                'casa': round(score_home, 3),
                'fora': round(score_away, 3)
            }
        }
    
    def generate_daily_analysis(self, data_analise: str) -> List[Dict]:
        """Gera análise diária para todos os jogos agendados numa data específica."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id_jogo, id_equipa_casa, id_equipa_fora
            FROM jogo
            WHERE data_jogo = ? AND status = 'agendado'
        ''', (data_analise,))
        
        jogos = cursor.fetchall()
        conn.close()
        
        analyses = []
        for id_jogo, id_casa, id_fora in jogos:
            analysis = self.predict_match(id_casa, id_fora)
            analysis['id_jogo'] = id_jogo
            analyses.append(analysis)
        
        return analyses

if __name__ == "__main__":
    # Teste do motor de previsão
    engine = FootballPredictionEngine()
    
    # Fazer previsão para o jogo Benfica vs Porto
    prediction = engine.predict_match(1, 2)
    
    print("=== ANÁLISE DE JOGO ===")
    print(f"{prediction['equipa_casa']} vs {prediction['equipa_fora']}")
    print(f"Previsão: {prediction['previsao_principal']} ({prediction['confianca']}% confiança)")
    print(f"Probabilidades: Casa {prediction['probabilidades']['vitoria_casa']}% | "
          f"Empate {prediction['probabilidades']['empate']}% | "
          f"Fora {prediction['probabilidades']['vitoria_fora']}%")
    print("\n=== ANÁLISE DETALHADA ===")
    for key, value in prediction['analise_detalhada'].items():
        print(f"{key}: {value}")

