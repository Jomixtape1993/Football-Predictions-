#!/usr/bin/env python3
"""
Sistema de Teste e Validação para o Analisador de Apostas de Futebol
Autor: Manus AI
Data: 27/06/2025

Este módulo popula a base de dados com dados de exemplo realistas
e testa o sistema de previsão com cenários diversos.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from football_betting_analyzer import FootballDataCollector
from prediction_engine import FootballPredictionEngine
import logging

logger = logging.getLogger(__name__)

class FootballTestSystem:
    """Sistema de teste com dados realistas."""
    
    def __init__(self, db_path: str = "football_data.db"):
        self.db_path = db_path
        self.collector = FootballDataCollector(db_path)
        self.engine = FootballPredictionEngine(db_path)
    
    def populate_sample_data(self):
        """Popula a base de dados com dados de exemplo realistas."""
        
        # Limpar dados existentes
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Limpar tabelas (manter estrutura)
        tables = ['confrontos_diretos', 'lesoes', 'desempenho_jogador_jogo', 
                 'desempenho_equipa_jogo', 'jogo', 'jogador', 'equipa']
        for table in tables:
            cursor.execute(f'DELETE FROM {table}')
        
        conn.commit()
        conn.close()
        
        # Adicionar equipas da Primeira Liga Portuguesa
        teams_data = [
            ("SL Benfica", "Portugal", "Primeira Liga"),
            ("FC Porto", "Portugal", "Primeira Liga"),
            ("Sporting CP", "Portugal", "Primeira Liga"),
            ("SC Braga", "Portugal", "Primeira Liga"),
            ("Vitória SC", "Portugal", "Primeira Liga"),
            ("FC Famalicão", "Portugal", "Primeira Liga"),
            ("Casa Pia AC", "Portugal", "Primeira Liga"),
            ("Rio Ave FC", "Portugal", "Primeira Liga"),
            ("Moreirense FC", "Portugal", "Primeira Liga"),
            ("Boavista FC", "Portugal", "Primeira Liga")
        ]
        
        team_ids = {}
        for nome, pais, liga in teams_data:
            team_id = self.collector.add_team(nome, pais, liga)
            team_ids[nome] = team_id
        
        # Adicionar jogadores para cada equipa
        players_data = {
            "SL Benfica": [
                ("Rafa Silva", "Extremo", 31),
                ("João Mário", "Médio", 31),
                ("Gonçalo Ramos", "Avançado", 23),
                ("Nicolás Otamendi", "Defesa Central", 36),
                ("Odysseas Vlachodimos", "Guarda-redes", 30)
            ],
            "FC Porto": [
                ("Pepe", "Defesa Central", 41),
                ("Otávio", "Médio Ofensivo", 29),
                ("Mehdi Taremi", "Avançado", 32),
                ("Diogo Costa", "Guarda-redes", 25),
                ("Galeno", "Extremo", 27)
            ],
            "Sporting CP": [
                ("Pedro Gonçalves", "Médio Ofensivo", 26),
                ("Viktor Gyökeres", "Avançado", 26),
                ("Morten Hjulmand", "Médio Defensivo", 25),
                ("Sebastián Coates", "Defesa Central", 34),
                ("Antonio Adán", "Guarda-redes", 37)
            ],
            "SC Braga": [
                ("Ricardo Horta", "Extremo", 30),
                ("Simon Banza", "Avançado", 28),
                ("João Moutinho", "Médio", 38),
                ("Víctor Gómez", "Defesa", 27),
                ("Matheus", "Guarda-redes", 32)
            ]
        }
        
        player_ids = {}
        for team_name, players in players_data.items():
            if team_name in team_ids:
                team_id = team_ids[team_name]
                player_ids[team_name] = []
                for nome, posicao, idade in players:
                    player_id = self.collector.add_player(nome, posicao, team_id, idade)
                    player_ids[team_name].append(player_id)
        
        # Adicionar jogos históricos (últimos 3 meses)
        start_date = datetime.now() - timedelta(days=90)
        match_ids = []
        
        # Gerar 30 jogos históricos
        for i in range(30):
            game_date = start_date + timedelta(days=i*3)
            
            # Escolher equipas aleatórias
            team_names = list(team_ids.keys())
            home_team = random.choice(team_names)
            away_team = random.choice([t for t in team_names if t != home_team])
            
            # Simular resultado
            home_goals = random.randint(0, 4)
            away_goals = random.randint(0, 3)
            
            match_id = self.collector.add_match(
                game_date.strftime('%Y-%m-%d'),
                team_ids[home_team],
                team_ids[away_team],
                home_goals,
                away_goals,
                'finalizado'
            )
            match_ids.append((match_id, team_ids[home_team], team_ids[away_team], home_goals, away_goals))
        
        # Adicionar dados de desempenho para os jogos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for match_id, home_id, away_id, home_goals, away_goals in match_ids:
            # Dados da equipa da casa
            cursor.execute('''
                INSERT INTO desempenho_equipa_jogo 
                (id_jogo, id_equipa, golos_marcados, golos_sofridos, remates_baliza, 
                 remates_sofridos, posse_bola, cantos, cartoes_amarelos, cartoes_vermelhos, 
                 clean_sheet, falhas_penalti, penaltis_sofridos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match_id, home_id, home_goals, away_goals,
                random.randint(3, 12), random.randint(2, 8),
                random.uniform(40, 70), random.randint(2, 10),
                random.randint(0, 4), random.randint(0, 1),
                1 if away_goals == 0 else 0, random.randint(0, 1), random.randint(0, 1)
            ))
            
            # Dados da equipa visitante
            cursor.execute('''
                INSERT INTO desempenho_equipa_jogo 
                (id_jogo, id_equipa, golos_marcados, golos_sofridos, remates_baliza, 
                 remates_sofridos, posse_bola, cantos, cartoes_amarelos, cartoes_vermelhos, 
                 clean_sheet, falhas_penalti, penaltis_sofridos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match_id, away_id, away_goals, home_goals,
                random.randint(2, 8), random.randint(3, 12),
                random.uniform(30, 60), random.randint(1, 8),
                random.randint(0, 4), random.randint(0, 1),
                1 if home_goals == 0 else 0, random.randint(0, 1), random.randint(0, 1)
            ))
        
        # Adicionar dados de desempenho dos jogadores
        for team_name, players in player_ids.items():
            for player_id in players:
                for match_id, home_id, away_id, _, _ in match_ids:
                    team_id = team_ids[team_name]
                    if team_id in [home_id, away_id]:
                        # Simular se o jogador participou (80% de probabilidade)
                        if random.random() < 0.8:
                            cursor.execute('''
                                INSERT INTO desempenho_jogador_jogo 
                                (id_jogo, id_jogador, golos, assistencias, minutos_jogados, 
                                 cartoes_amarelos, cartoes_vermelhos, remates, remates_baliza, 
                                 passes_completos, desarmes, intercecoes, faltas_cometidas, 
                                 faltas_sofridas, penaltis_marcados, penaltis_sofridos)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                match_id, player_id,
                                random.randint(0, 2) if random.random() < 0.15 else 0,  # golos
                                random.randint(0, 1) if random.random() < 0.20 else 0,  # assistências
                                random.randint(60, 90),  # minutos
                                random.randint(0, 1) if random.random() < 0.25 else 0,  # cartões amarelos
                                random.randint(0, 1) if random.random() < 0.05 else 0,  # cartões vermelhos
                                random.randint(0, 5),  # remates
                                random.randint(0, 3),  # remates à baliza
                                random.uniform(70, 95),  # passes completos %
                                random.randint(0, 4),  # desarmes
                                random.randint(0, 3),  # interceções
                                random.randint(0, 3),  # faltas cometidas
                                random.randint(0, 2),  # faltas sofridas
                                random.randint(0, 1) if random.random() < 0.02 else 0,  # penáltis marcados
                                random.randint(0, 1) if random.random() < 0.03 else 0   # penáltis sofridos
                            ))
        
        # Adicionar algumas lesões
        injury_types = ['Muscular', 'Ligamentar', 'Óssea', 'Contusão']
        severities = ['Ligeira', 'Moderada', 'Grave']
        
        for team_name, players in player_ids.items():
            # 20% dos jogadores têm lesões
            injured_players = random.sample(players, max(1, len(players) // 5))
            for player_id in injured_players:
                start_date = datetime.now() - timedelta(days=random.randint(1, 30))
                end_date = start_date + timedelta(days=random.randint(7, 60))
                
                cursor.execute('''
                    INSERT INTO lesoes 
                    (id_jogador, data_inicio, data_fim_estimada, tipo_lesao, gravidade, impacto_equipa)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    player_id,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d'),
                    random.choice(injury_types),
                    random.choice(severities),
                    random.randint(1, 5)
                ))
        
        # Adicionar confrontos diretos históricos
        big_teams = ["SL Benfica", "FC Porto", "Sporting CP", "SC Braga"]
        for i, team1 in enumerate(big_teams):
            for team2 in big_teams[i+1:]:
                # Adicionar 5 confrontos históricos
                for j in range(5):
                    confronto_date = datetime.now() - timedelta(days=random.randint(30, 365))
                    goals1 = random.randint(0, 4)
                    goals2 = random.randint(0, 3)
                    
                    if goals1 > goals2:
                        winner = team_ids[team1]
                    elif goals2 > goals1:
                        winner = team_ids[team2]
                    else:
                        winner = None
                    
                    cursor.execute('''
                        INSERT INTO confrontos_diretos 
                        (id_equipa1, id_equipa2, data_confronto, vencedor, golos_equipa1, golos_equipa2, local)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        team_ids[team1], team_ids[team2],
                        confronto_date.strftime('%Y-%m-%d'),
                        winner, goals1, goals2,
                        random.choice(['Casa', 'Fora', 'Neutro'])
                    ))
        
        # Adicionar jogos futuros para análise
        tomorrow = datetime.now() + timedelta(days=1)
        future_matches = [
            ("SL Benfica", "FC Porto"),
            ("Sporting CP", "SC Braga"),
            ("Vitória SC", "Boavista FC")
        ]
        
        for home_team, away_team in future_matches:
            if home_team in team_ids and away_team in team_ids:
                self.collector.add_match(
                    tomorrow.strftime('%Y-%m-%d'),
                    team_ids[home_team],
                    team_ids[away_team],
                    status='agendado'
                )
        
        conn.commit()
        conn.close()
        
        logger.info("Base de dados populada com dados de exemplo realistas.")
        return team_ids
    
    def run_comprehensive_test(self):
        """Executa teste abrangente do sistema."""
        print("=== TESTE ABRANGENTE DO SISTEMA DE ANÁLISE ===\n")
        
        # Poplar dados
        print("1. A popular base de dados com dados realistas...")
        team_ids = self.populate_sample_data()
        
        # Testar previsões para jogos futuros
        print("\n2. A gerar análises para jogos de amanhã...")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        daily_analyses = self.engine.generate_daily_analysis(tomorrow)
        
        print(f"\n=== ANÁLISES DIÁRIAS PARA {tomorrow} ===")
        
        for i, analysis in enumerate(daily_analyses, 1):
            print(f"\n--- JOGO {i} ---")
            print(f"{analysis['equipa_casa']} vs {analysis['equipa_fora']}")
            print(f"Previsão: {analysis['previsao_principal']} ({analysis['confianca']}% confiança)")
            print(f"Probabilidades:")
            print(f"  • Vitória {analysis['equipa_casa']}: {analysis['probabilidades']['vitoria_casa']}%")
            print(f"  • Empate: {analysis['probabilidades']['empate']}%")
            print(f"  • Vitória {analysis['equipa_fora']}: {analysis['probabilidades']['vitoria_fora']}%")
            
            print(f"\nAnálise Detalhada:")
            print(f"  • Força da equipa (Casa/Fora): {analysis['analise_detalhada']['forca_equipa_casa']:.3f} / {analysis['analise_detalhada']['forca_equipa_fora']:.3f}")
            print(f"  • Impacto jogadores (Casa/Fora): {analysis['analise_detalhada']['impacto_jogadores_casa']:.3f} / {analysis['analise_detalhada']['impacto_jogadores_fora']:.3f}")
            print(f"  • Impacto lesões (Casa/Fora): {analysis['analise_detalhada']['impacto_lesoes_casa']:.3f} / {analysis['analise_detalhada']['impacto_lesoes_fora']:.3f}")
            print(f"  • Fator casa/fora: {analysis['analise_detalhada']['fator_casa']:.3f} / {analysis['analise_detalhada']['fator_fora']:.3f}")
            print(f"  • Confrontos diretos (Casa/Fora): {analysis['analise_detalhada']['fator_confrontos_diretos_casa']:.3f} / {analysis['analise_detalhada']['fator_confrontos_diretos_fora']:.3f}")
            
            print(f"\nPontuação Final: Casa {analysis['pontuacao_final']['casa']:.3f} | Fora {analysis['pontuacao_final']['fora']:.3f}")
        
        # Testar casos específicos
        print(f"\n\n=== TESTE DE CASOS ESPECÍFICOS ===")
        
        # Teste 1: Benfica vs Porto (clássico)
        print(f"\n--- CLÁSSICO: SL Benfica vs FC Porto ---")
        benfica_id = team_ids["SL Benfica"]
        porto_id = team_ids["FC Porto"]
        
        prediction = self.engine.predict_match(benfica_id, porto_id)
        self.print_detailed_analysis(prediction)
        
        # Teste 2: Verificar desempenho das equipas
        print(f"\n--- DESEMPENHO DAS EQUIPAS (últimos 10 jogos) ---")
        for team_name, team_id in team_ids.items():
            performance = self.collector.get_team_performance(team_id, 10)
            if performance:
                print(f"\n{team_name}:")
                print(f"  • Golos marcados/jogo: {performance['media_golos_marcados']}")
                print(f"  • Golos sofridos/jogo: {performance['media_golos_sofridos']}")
                print(f"  • Diferença de golos: {performance['diferenca_golos']}")
                print(f"  • Clean sheets: {performance['percentagem_clean_sheets']}%")
                print(f"  • Jogos analisados: {performance['total_jogos']}")
        
        # Teste 3: Verificar lesões
        print(f"\n--- RELATÓRIO DE LESÕES ---")
        for team_name, team_id in team_ids.items():
            injuries = self.collector.get_team_injuries(team_id)
            if injuries:
                print(f"\n{team_name} ({len(injuries)} lesionados):")
                for injury in injuries:
                    print(f"  • {injury['nome_jogador']} ({injury['posicao']}): {injury['tipo_lesao']} - {injury['gravidade']}")
        
        print(f"\n=== TESTE CONCLUÍDO COM SUCESSO ===")
    
    def print_detailed_analysis(self, prediction):
        """Imprime análise detalhada de uma previsão."""
        print(f"Previsão: {prediction['previsao_principal']} ({prediction['confianca']}% confiança)")
        print(f"Probabilidades: Casa {prediction['probabilidades']['vitoria_casa']}% | "
              f"Empate {prediction['probabilidades']['empate']}% | "
              f"Fora {prediction['probabilidades']['vitoria_fora']}%")
        
        print(f"\nComponentes da Análise:")
        components = [
            ("Força da Equipa", "forca_equipa_casa", "forca_equipa_fora", 40),
            ("Impacto Jogadores", "impacto_jogadores_casa", "impacto_jogadores_fora", 25),
            ("Impacto Lesões", "impacto_lesoes_casa", "impacto_lesoes_fora", 15),
            ("Confrontos Diretos", "fator_confrontos_diretos_casa", "fator_confrontos_diretos_fora", 10),
            ("Fator Casa/Fora", "fator_casa", "fator_fora", 10)
        ]
        
        for name, home_key, away_key, weight in components:
            home_val = prediction['analise_detalhada'][home_key]
            away_val = prediction['analise_detalhada'][away_key]
            print(f"  • {name} ({weight}%): {home_val:.3f} vs {away_val:.3f}")

if __name__ == "__main__":
    # Executar teste abrangente
    test_system = FootballTestSystem()
    test_system.run_comprehensive_test()

