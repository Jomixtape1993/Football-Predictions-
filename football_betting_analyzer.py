#!/usr/bin/env python3
"""
Sistema de Análise Profissional de Apostas Desportivas para Futebol
Autor: Manus AI
Data: 27/06/2025

Este sistema recolhe e processa dados de futebol para fornecer previsões diárias
baseadas em escalações, desempenho de jogadores, lesões e histórico entre equipas.
"""

import sqlite3
import requests
import json
import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FootballDataCollector:
    """Classe responsável pela recolha de dados de futebol."""
    
    def __init__(self, db_path: str = "football_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa a base de dados com as tabelas necessárias."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela Equipa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipa (
                id_equipa INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_equipa TEXT NOT NULL,
                pais TEXT,
                liga TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela Jogador
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jogador (
                id_jogador INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_jogador TEXT NOT NULL,
                posicao TEXT,
                id_equipa INTEGER,
                idade INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_equipa) REFERENCES equipa (id_equipa)
            )
        ''')
        
        # Tabela Jogo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jogo (
                id_jogo INTEGER PRIMARY KEY AUTOINCREMENT,
                data_jogo DATE NOT NULL,
                id_equipa_casa INTEGER,
                id_equipa_fora INTEGER,
                golos_casa INTEGER,
                golos_fora INTEGER,
                status TEXT DEFAULT 'agendado',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_equipa_casa) REFERENCES equipa (id_equipa),
                FOREIGN KEY (id_equipa_fora) REFERENCES equipa (id_equipa)
            )
        ''')
        
        # Tabela Desempenho_Equipa_Jogo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS desempenho_equipa_jogo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_jogo INTEGER,
                id_equipa INTEGER,
                golos_marcados INTEGER DEFAULT 0,
                golos_sofridos INTEGER DEFAULT 0,
                remates_baliza INTEGER DEFAULT 0,
                remates_sofridos INTEGER DEFAULT 0,
                posse_bola REAL DEFAULT 0.0,
                cantos INTEGER DEFAULT 0,
                cartoes_amarelos INTEGER DEFAULT 0,
                cartoes_vermelhos INTEGER DEFAULT 0,
                clean_sheet BOOLEAN DEFAULT 0,
                falhas_penalti INTEGER DEFAULT 0,
                penaltis_sofridos INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_jogo) REFERENCES jogo (id_jogo),
                FOREIGN KEY (id_equipa) REFERENCES equipa (id_equipa)
            )
        ''')
        
        # Tabela Desempenho_Jogador_Jogo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS desempenho_jogador_jogo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_jogo INTEGER,
                id_jogador INTEGER,
                golos INTEGER DEFAULT 0,
                assistencias INTEGER DEFAULT 0,
                minutos_jogados INTEGER DEFAULT 0,
                cartoes_amarelos INTEGER DEFAULT 0,
                cartoes_vermelhos INTEGER DEFAULT 0,
                remates INTEGER DEFAULT 0,
                remates_baliza INTEGER DEFAULT 0,
                passes_completos REAL DEFAULT 0.0,
                desarmes INTEGER DEFAULT 0,
                intercecoes INTEGER DEFAULT 0,
                faltas_cometidas INTEGER DEFAULT 0,
                faltas_sofridas INTEGER DEFAULT 0,
                penaltis_marcados INTEGER DEFAULT 0,
                penaltis_sofridos INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_jogo) REFERENCES jogo (id_jogo),
                FOREIGN KEY (id_jogador) REFERENCES jogador (id_jogador)
            )
        ''')
        
        # Tabela Lesões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lesoes (
                id_lesao INTEGER PRIMARY KEY AUTOINCREMENT,
                id_jogador INTEGER,
                data_inicio DATE NOT NULL,
                data_fim_estimada DATE,
                tipo_lesao TEXT,
                gravidade TEXT,
                impacto_equipa INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_jogador) REFERENCES jogador (id_jogador)
            )
        ''')
        
        # Tabela Confrontos_Diretos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS confrontos_diretos (
                id_confronto INTEGER PRIMARY KEY AUTOINCREMENT,
                id_equipa1 INTEGER,
                id_equipa2 INTEGER,
                data_confronto DATE NOT NULL,
                vencedor INTEGER,
                golos_equipa1 INTEGER,
                golos_equipa2 INTEGER,
                local TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_equipa1) REFERENCES equipa (id_equipa),
                FOREIGN KEY (id_equipa2) REFERENCES equipa (id_equipa),
                FOREIGN KEY (vencedor) REFERENCES equipa (id_equipa)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Base de dados inicializada com sucesso.")
    
    def add_team(self, nome_equipa: str, pais: str = None, liga: str = None) -> int:
        """Adiciona uma nova equipa à base de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO equipa (nome_equipa, pais, liga)
            VALUES (?, ?, ?)
        ''', (nome_equipa, pais, liga))
        
        team_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Equipa '{nome_equipa}' adicionada com ID {team_id}")
        return team_id
    
    def add_player(self, nome_jogador: str, posicao: str, id_equipa: int, idade: int = None) -> int:
        """Adiciona um novo jogador à base de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO jogador (nome_jogador, posicao, id_equipa, idade)
            VALUES (?, ?, ?, ?)
        ''', (nome_jogador, posicao, id_equipa, idade))
        
        player_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Jogador '{nome_jogador}' adicionado com ID {player_id}")
        return player_id
    
    def add_match(self, data_jogo: str, id_equipa_casa: int, id_equipa_fora: int, 
                  golos_casa: int = None, golos_fora: int = None, status: str = 'agendado') -> int:
        """Adiciona um novo jogo à base de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO jogo (data_jogo, id_equipa_casa, id_equipa_fora, golos_casa, golos_fora, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data_jogo, id_equipa_casa, id_equipa_fora, golos_casa, golos_fora, status))
        
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Jogo adicionado com ID {match_id}")
        return match_id
    
    def get_team_performance(self, id_equipa: int, num_jogos: int = 10) -> Dict:
        """Obtém o desempenho de uma equipa nos últimos N jogos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                AVG(golos_marcados) as media_golos_marcados,
                AVG(golos_sofridos) as media_golos_sofridos,
                AVG(remates_baliza) as media_remates_baliza,
                AVG(posse_bola) as media_posse_bola,
                AVG(cantos) as media_cantos,
                AVG(cartoes_amarelos) as media_cartoes_amarelos,
                AVG(cartoes_vermelhos) as media_cartoes_vermelhos,
                SUM(clean_sheet) * 100.0 / COUNT(*) as percentagem_clean_sheets,
                COUNT(*) as total_jogos
            FROM desempenho_equipa_jogo dej
            JOIN jogo j ON dej.id_jogo = j.id_jogo
            WHERE dej.id_equipa = ? AND j.status = 'finalizado'
            ORDER BY j.data_jogo DESC
            LIMIT ?
        ''', (id_equipa, num_jogos))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[8] > 0:  # total_jogos > 0
            return {
                'media_golos_marcados': round(result[0] or 0, 2),
                'media_golos_sofridos': round(result[1] or 0, 2),
                'diferenca_golos': round((result[0] or 0) - (result[1] or 0), 2),
                'media_remates_baliza': round(result[2] or 0, 2),
                'media_posse_bola': round(result[3] or 0, 2),
                'media_cantos': round(result[4] or 0, 2),
                'media_cartoes_amarelos': round(result[5] or 0, 2),
                'media_cartoes_vermelhos': round(result[6] or 0, 2),
                'percentagem_clean_sheets': round(result[7] or 0, 2),
                'total_jogos': result[8]
            }
        else:
            return {}
    
    def get_player_performance(self, id_jogador: int, num_jogos: int = 20) -> Dict:
        """Obtém o desempenho de um jogador nos últimos N jogos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                SUM(golos) as total_golos,
                SUM(assistencias) as total_assistencias,
                AVG(minutos_jogados) as media_minutos,
                SUM(cartoes_amarelos) as total_cartoes_amarelos,
                SUM(cartoes_vermelhos) as total_cartoes_vermelhos,
                AVG(remates) as media_remates,
                AVG(remates_baliza) as media_remates_baliza,
                AVG(passes_completos) as media_passes_completos,
                AVG(desarmes) as media_desarmes,
                AVG(intercecoes) as media_intercecoes,
                COUNT(*) as total_jogos
            FROM desempenho_jogador_jogo dpj
            JOIN jogo j ON dpj.id_jogo = j.id_jogo
            WHERE dpj.id_jogador = ? AND j.status = 'finalizado'
            ORDER BY j.data_jogo DESC
            LIMIT ?
        ''', (id_jogador, num_jogos))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[10] > 0:  # total_jogos > 0
            return {
                'total_golos': result[0] or 0,
                'total_assistencias': result[1] or 0,
                'media_minutos': round(result[2] or 0, 2),
                'total_cartoes_amarelos': result[3] or 0,
                'total_cartoes_vermelhos': result[4] or 0,
                'media_remates': round(result[5] or 0, 2),
                'media_remates_baliza': round(result[6] or 0, 2),
                'media_passes_completos': round(result[7] or 0, 2),
                'media_desarmes': round(result[8] or 0, 2),
                'media_intercecoes': round(result[9] or 0, 2),
                'total_jogos': result[10]
            }
        else:
            return {}
    
    def get_head_to_head(self, id_equipa1: int, id_equipa2: int, num_confrontos: int = 10) -> Dict:
        """Obtém o histórico de confrontos diretos entre duas equipas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                vencedor,
                golos_equipa1,
                golos_equipa2,
                data_confronto,
                local
            FROM confrontos_diretos
            WHERE (id_equipa1 = ? AND id_equipa2 = ?) OR (id_equipa1 = ? AND id_equipa2 = ?)
            ORDER BY data_confronto DESC
            LIMIT ?
        ''', (id_equipa1, id_equipa2, id_equipa2, id_equipa1, num_confrontos))
        
        confrontos = cursor.fetchall()
        conn.close()
        
        if not confrontos:
            return {}
        
        vitorias_equipa1 = 0
        vitorias_equipa2 = 0
        empates = 0
        total_golos_equipa1 = 0
        total_golos_equipa2 = 0
        
        for confronto in confrontos:
            vencedor, golos1, golos2, data, local = confronto
            
            if vencedor == id_equipa1:
                vitorias_equipa1 += 1
            elif vencedor == id_equipa2:
                vitorias_equipa2 += 1
            else:
                empates += 1
            
            total_golos_equipa1 += golos1 or 0
            total_golos_equipa2 += golos2 or 0
        
        total_confrontos = len(confrontos)
        
        return {
            'total_confrontos': total_confrontos,
            'vitorias_equipa1': vitorias_equipa1,
            'vitorias_equipa2': vitorias_equipa2,
            'empates': empates,
            'percentagem_vitorias_equipa1': round(vitorias_equipa1 * 100 / total_confrontos, 2),
            'percentagem_vitorias_equipa2': round(vitorias_equipa2 * 100 / total_confrontos, 2),
            'percentagem_empates': round(empates * 100 / total_confrontos, 2),
            'media_golos_equipa1': round(total_golos_equipa1 / total_confrontos, 2),
            'media_golos_equipa2': round(total_golos_equipa2 / total_confrontos, 2)
        }
    
    def get_team_injuries(self, id_equipa: int) -> List[Dict]:
        """Obtém a lista de jogadores lesionados de uma equipa."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                j.nome_jogador,
                j.posicao,
                l.tipo_lesao,
                l.gravidade,
                l.data_inicio,
                l.data_fim_estimada,
                l.impacto_equipa
            FROM lesoes l
            JOIN jogador j ON l.id_jogador = j.id_jogador
            WHERE j.id_equipa = ? AND (l.data_fim_estimada IS NULL OR l.data_fim_estimada >= date('now'))
            ORDER BY l.impacto_equipa DESC, l.data_inicio DESC
        ''', (id_equipa,))
        
        lesoes = cursor.fetchall()
        conn.close()
        
        return [
            {
                'nome_jogador': lesao[0],
                'posicao': lesao[1],
                'tipo_lesao': lesao[2],
                'gravidade': lesao[3],
                'data_inicio': lesao[4],
                'data_fim_estimada': lesao[5],
                'impacto_equipa': lesao[6]
            }
            for lesao in lesoes
        ]

if __name__ == "__main__":
    # Teste do sistema
    collector = FootballDataCollector()
    
    # Adicionar equipas de exemplo
    benfica_id = collector.add_team("SL Benfica", "Portugal", "Primeira Liga")
    porto_id = collector.add_team("FC Porto", "Portugal", "Primeira Liga")
    
    # Adicionar jogadores de exemplo
    collector.add_player("Rafa Silva", "Extremo", benfica_id, 31)
    collector.add_player("Pepe", "Defesa Central", porto_id, 41)
    
    # Adicionar jogo de exemplo
    match_id = collector.add_match("2025-06-28", benfica_id, porto_id)
    
    print("Sistema de recolha de dados inicializado com sucesso!")
    print(f"Base de dados criada em: {collector.db_path}")

