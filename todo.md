- [x] Definir as métricas de desempenho da equipa (ex: golos marcados/sofridos, posse de bola, remates à baliza).
  - Golos Marcados (GM): Média de golos marcados por jogo.
  - Golos Sofridos (GS): Média de golos sofridos por jogo.
  - Diferença de Golos (DG): GM - GS.
  - Remates à Baliza (RB): Média de remates à baliza por jogo.
  - Remates Sofridos (RS): Média de remates sofridos por jogo.
  - Posse de Bola (PB): Percentagem média de posse de bola por jogo.
  - Cantos (C): Média de cantos a favor por jogo.
  - Cartões Amarelos (CA): Média de cartões amarelos por jogo.
  - Cartões Vermelhos (CV): Média de cartões vermelhos por jogo.
  - Clean Sheets (CS): Percentagem de jogos sem sofrer golos.
  - Falhas de Penálti (FP): Número de penáltis falhados.
  - Penáltis Sofridos (PS): Número de penáltis sofridos.
  - Vitórias (V): Percentagem de vitórias.
  - Empates (E): Percentagem de empates.
  - Derrotas (D): Percentagem de derrotas.
- [x] Definir as métricas de desempenho do jogador (ex: golos, assistências, cartões, minutos jogados).
  - Golos (G): Total de golos marcados.
  - Assistências (A): Total de assistências.
  - Minutos Jogados (MJ): Total de minutos jogados.
  - Cartões Amarelos (CA): Total de cartões amarelos.
  - Cartões Vermelhos (CV): Total de cartões vermelhos.
  - Remates (R): Total de remates.
  - Remates à Baliza (RB): Total de remates à baliza.
  - Passes Completos (PC): Percentagem de passes completos.
  - Desarmes (D): Total de desarmes.
  - Interceções (I): Total de interceções.
  - Faltas Cometidas (FC): Total de faltas cometidas.
  - Faltas Sofridas (FS): Total de faltas sofridas.
  - Penáltis Marcados (PM): Total de penáltis marcados.
  - Penáltis Sofridos (PS): Total de penáltis sofridos (quando o jogador sofre a falta que resulta em penálti).
- [x] Definir como as lesões afetarão as previsões (ex: impacto de jogadores chave).
  - Impacto de Lesões: Avaliar a importância do jogador lesionado para a equipa (ex: titular, artilheiro, defesa principal).
  - Duração da Lesão: Tempo estimado de recuperação e se o jogador estará disponível para o jogo.
  - Substitutos: Qualidade e desempenho dos jogadores que podem substituir os lesionados.
  - Histórico de Lesões: Frequência e tipo de lesões de jogadores chave.
- [x] Definir como o histórico de confrontos diretos será utilizado.
  - Resultados Anteriores: Vitórias, empates e derrotas em confrontos diretos.
  - Golos Marcados/Sofridos: Média de golos marcados e sofridos em confrontos diretos.
  - Desempenho em Casa/Fora: Como as equipas se comportam em casa e fora contra o adversário específico.
  - Tendências Recentes: Se uma equipa tem dominado os confrontos recentes.
- [x] Esboçar a estrutura de dados necessária para armazenar e processar estas informações.
  - Base de Dados Relacional (SQL): Para armazenar dados estruturados de equipas, jogadores, jogos, lesões e confrontos diretos.
    - Tabela Equipa: ID_Equipa, Nome_Equipa, País, Liga, etc.
    - Tabela Jogador: ID_Jogador, Nome_Jogador, Posição, ID_Equipa, etc.
    - Tabela Jogo: ID_Jogo, Data, ID_Equipa_Casa, ID_Equipa_Fora, Golos_Casa, Golos_Fora, etc.
    - Tabela Desempenho_Equipa_Jogo: ID_Jogo, ID_Equipa, GM, GS, RB, RS, PB, C, CA, CV, CS, FP, PS, V, E, D (por jogo).
    - Tabela Desempenho_Jogador_Jogo: ID_Jogo, ID_Jogador, G, A, MJ, CA, CV, R, RB, PC, D, I, FC, FS, PM, PS (por jogo).
    - Tabela Lesões: ID_Lesao, ID_Jogador, Data_Inicio, Data_Fim_Estimada, Tipo_Lesao, Gravidade, Impacto_Equipa.
    - Tabela Confrontos_Diretos: ID_Confronto, ID_Equipa1, ID_Equipa2, Data, Vencedor, Golos_Equipa1, Golos_Equipa2.
  - Armazenamento de Dados Históricos: Manter um histórico extenso (últimos 20 jogos para jogadores, várias épocas para equipas e confrontos diretos).
- [x] Considerar a ponderação de cada métrica na previsão final.
  - Desempenho da Equipa (últimos 5-10 jogos): 40%
  - Desempenho do Jogador (últimos 20 jogos, especialmente jogadores chave): 25%
  - Lesões (impacto em jogadores chave): 15%
  - Histórico de Confrontos Diretos: 10%
  - Fator Casa/Fora: 10%
  - Ajustes Dinâmicos: Considerar fatores como motivação (competição, rivalidade), mudanças de treinador, etc., que podem ajustar as ponderações.
- [x] Desenvolver um plano para a validação das previsões.
  - Backtesting: Utilizar dados históricos para simular apostas e avaliar a precisão do modelo.
  - Comparação com Odds de Casas de Apostas: Comparar as probabilidades geradas pelo modelo com as odds oferecidas pelas casas de apostas para identificar valor.
  - Acompanhamento em Tempo Real: Monitorizar as previsões diárias e os resultados reais para ajustar o modelo conforme necessário.
  - Métricas de Avaliação: Utilizar métricas como precisão, recall, F1-score, e lucro/prejuízo simulado para avaliar o desempenho do modelo.

