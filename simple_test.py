#!/usr/bin/env python3
"""
Teste Simplificado do Sistema de Análise de Apostas de Futebol
Autor: Manus AI
Data: 27/06/2025
"""

import sqlite3
import random
from datetime import datetime, timedelta
from football_betting_analyzer import FootballDataCollector
from prediction_engine import FootballPredictionEngine

def create_sample_data():
    """Cria dados de exemplo para teste."""
    
    # Remover base de dados existente
    import os
    if os.path.exists("football_data.db"):
        os.remove("football_data.db")
    
    collector = FootballDataCollector()
    
    # Adicionar equipas
    benfica_id = collector.add_team("SL Benfica", "Portugal", "Primeira Liga")
    porto_id = collector.add_team("FC Porto", "Portugal", "Primeira Liga")
    sporting_id = collector.add_team("Sporting CP", "Portugal", "Primeira Liga")
    braga_id = collector.add_team("SC Braga", "Portugal", "Primeira Liga")
    
    # Adicionar jogadores
    collector.add_player("Rafa Silva", "Extremo", benfica_id, 31)
    collector.add_player("João Mário", "Médio", benfica_id, 31)
    collector.add_player("Pepe", "Defesa Central", porto_id, 41)
    collector.add_player("Otávio", "Médio Ofensivo", porto_id, 29)
    
    # Adicionar alguns jogos históricos
    conn = sqlite3.connect("football_data.db")
    cursor = conn.cursor()
    
    # Jogo 1: Benfica 2-1 Porto (finalizado)
    cursor.execute('''
        INSERT INTO jogo (data_jogo, id_equipa_casa, id_equipa_fora, golos_casa, golos_fora, status)
        VALUES ('2025-06-20', ?, ?, 2, 1, 'finalizado')
    ''', (benfica_id, porto_id))
    match1_id = cursor.lastrowid
    
    # Dados de desempenho para o jogo 1
    cursor.execute('''
        INSERT INTO desempenho_equipa_jogo 
        (id_jogo, id_equipa, golos_marcados, golos_sofridos, remates_baliza, posse_bola, cantos, cartoes_amarelos)
        VALUES (?, ?, 2, 1, 8, 65.0, 6, 2)
    ''', (match1_id, benfica_id))
    
    cursor.execute('''
        INSERT INTO desempenho_equipa_jogo 
        (id_jogo, id_equipa, golos_marcados, golos_sofridos, remates_baliza, posse_bola, cantos, cartoes_amarelos)
        VALUES (?, ?, 1, 2, 5, 35.0, 3, 3)
    ''', (match1_id, porto_id))
    
    # Jogo 2: Porto 3-0 Sporting (finalizado)
    cursor.execute('''
        INSERT INTO jogo (data_jogo, id_equipa_casa, id_equipa_fora, golos_casa, golos_fora, status)
        VALUES ('2025-06-22', ?, ?, 3, 0, 'finalizado')
    ''', (porto_id, sporting_id))
    match2_id = cursor.lastrowid
    
    # Dados de desempenho para o jogo 2
    cursor.execute('''
        INSERT INTO desempenho_equipa_jogo 
        (id_jogo, id_equipa, golos_marcados, golos_sofridos, remates_baliza, posse_bola, cantos, cartoes_amarelos, clean_sheet)
        VALUES (?, ?, 3, 0, 10, 55.0, 8, 1, 1)
    ''', (match2_id, porto_id))
    
    cursor.execute('''
        INSERT INTO desempenho_equipa_jogo 
        (id_jogo, id_equipa, golos_marcados, golos_sofridos, remates_baliza, posse_bola, cantos, cartoes_amarelos)
        VALUES (?, ?, 0, 3, 3, 45.0, 2, 4)
    ''', (match2_id, sporting_id))
    
    # Adicionar confronto direto histórico
    cursor.execute('''
        INSERT INTO confrontos_diretos 
        (id_equipa1, id_equipa2, data_confronto, vencedor, golos_equipa1, golos_equipa2, local)
        VALUES (?, ?, '2025-05-15', ?, 2, 1, 'Casa')
    ''', (benfica_id, porto_id, benfica_id))
    
    # Adicionar uma lesão
    cursor.execute('''
        INSERT INTO lesoes 
        (id_jogador, data_inicio, data_fim_estimada, tipo_lesao, gravidade, impacto_equipa)
        VALUES (3, '2025-06-25', '2025-07-10', 'Muscular', 'Moderada', 4)
    ''')
    
    # Adicionar jogo futuro para análise
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO jogo (data_jogo, id_equipa_casa, id_equipa_fora, status)
        VALUES (?, ?, ?, 'agendado')
    ''', (tomorrow, benfica_id, porto_id))
    
    conn.commit()
    conn.close()
    
    return {
        'benfica_id': benfica_id,
        'porto_id': porto_id,
        'sporting_id': sporting_id,
        'braga_id': braga_id
    }

def main():
    print("=== TESTE SIMPLIFICADO DO SISTEMA DE ANÁLISE ===\n")
    
    # Criar dados de exemplo
    print("1. A criar dados de exemplo...")
    team_ids = create_sample_data()
    
    # Inicializar motor de previsão
    engine = FootballPredictionEngine()
    
    # Teste 1: Análise de jogo específico
    print("\n2. Teste de análise de jogo específico:")
    print("--- SL Benfica vs FC Porto ---")
    
    prediction = engine.predict_match(team_ids['benfica_id'], team_ids['porto_id'])
    
    print(f"Previsão: {prediction['previsao_principal']} ({prediction['confianca']}% confiança)")
    print(f"Probabilidades:")
    print(f"  • Vitória {prediction['equipa_casa']}: {prediction['probabilidades']['vitoria_casa']}%")
    print(f"  • Empate: {prediction['probabilidades']['empate']}%")
    print(f"  • Vitória {prediction['equipa_fora']}: {prediction['probabilidades']['vitoria_fora']}%")
    
    print(f"\nAnálise Detalhada:")
    print(f"  • Força da equipa (Casa/Fora): {prediction['analise_detalhada']['forca_equipa_casa']:.3f} / {prediction['analise_detalhada']['forca_equipa_fora']:.3f}")
    print(f"  • Impacto jogadores (Casa/Fora): {prediction['analise_detalhada']['impacto_jogadores_casa']:.3f} / {prediction['analise_detalhada']['impacto_jogadores_fora']:.3f}")
    print(f"  • Impacto lesões (Casa/Fora): {prediction['analise_detalhada']['impacto_lesoes_casa']:.3f} / {prediction['analise_detalhada']['impacto_lesoes_fora']:.3f}")
    print(f"  • Fator casa/fora: {prediction['analise_detalhada']['fator_casa']:.3f} / {prediction['analise_detalhada']['fator_fora']:.3f}")
    print(f"  • Confrontos diretos (Casa/Fora): {prediction['analise_detalhada']['fator_confrontos_diretos_casa']:.3f} / {prediction['analise_detalhada']['fator_confrontos_diretos_fora']:.3f}")
    
    # Teste 2: Verificar desempenho das equipas
    print(f"\n3. Teste de desempenho das equipas:")
    collector = FootballDataCollector()
    
    for team_name, team_id in team_ids.items():
        performance = collector.get_team_performance(team_id, 10)
        if performance:
            print(f"\n{team_name.replace('_id', '').replace('_', ' ').title()}:")
            print(f"  • Golos marcados/jogo: {performance['media_golos_marcados']}")
            print(f"  • Golos sofridos/jogo: {performance['media_golos_sofridos']}")
            print(f"  • Diferença de golos: {performance['diferenca_golos']}")
            print(f"  • Clean sheets: {performance['percentagem_clean_sheets']}%")
            print(f"  • Jogos analisados: {performance['total_jogos']}")
    
    # Teste 3: Verificar lesões
    print(f"\n4. Teste de relatório de lesões:")
    injuries = collector.get_team_injuries(team_ids['porto_id'])
    if injuries:
        print(f"FC Porto ({len(injuries)} lesionados):")
        for injury in injuries:
            print(f"  • {injury['nome_jogador']} ({injury['posicao']}): {injury['tipo_lesao']} - {injury['gravidade']}")
    else:
        print("FC Porto: Sem lesões reportadas")
    
    # Teste 4: Análise diária
    print(f"\n5. Teste de análise diária:")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    daily_analyses = engine.generate_daily_analysis(tomorrow)
    
    if daily_analyses:
        print(f"Jogos agendados para {tomorrow}:")
        for analysis in daily_analyses:
            print(f"  • {analysis['equipa_casa']} vs {analysis['equipa_fora']}")
            print(f"    Previsão: {analysis['previsao_principal']} ({analysis['confianca']}%)")
    else:
        print(f"Nenhum jogo agendado para {tomorrow}")
    
    print(f"\n=== TESTE CONCLUÍDO COM SUCESSO ===")
    print(f"O sistema está funcional e pronto para análise de apostas desportivas!")

if __name__ == "__main__":
    main()

