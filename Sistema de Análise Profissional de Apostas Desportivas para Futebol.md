# Sistema de Análise Profissional de Apostas Desportivas para Futebol

## Visão Geral

Este sistema fornece análises profissionais e previsões diárias para jogos de futebol, baseadas em dados científicos e métricas avançadas. O sistema combina múltiplos fatores para gerar previsões precisas e justificadas.

## Características Principais

### 🎯 Análise Multifatorial
- **Desempenho da Equipa (40%)**: Análise dos últimos 5-10 jogos
- **Desempenho dos Jogadores (25%)**: Estatísticas individuais dos últimos 20 jogos
- **Impacto de Lesões (15%)**: Avaliação de jogadores lesionados
- **Histórico de Confrontos Diretos (10%)**: Resultados anteriores entre equipas
- **Fator Casa/Fora (10%)**: Vantagem do campo próprio

### 📊 Métricas Analisadas

#### Equipas
- Golos marcados e sofridos por jogo
- Remates à baliza e sofridos
- Percentagem de posse de bola
- Cantos a favor
- Cartões amarelos e vermelhos
- Clean sheets (jogos sem sofrer golos)
- Penáltis marcados e sofridos

#### Jogadores
- Golos e assistências
- Minutos jogados
- Remates e remates à baliza
- Percentagem de passes completos
- Desarmes e interceções
- Faltas cometidas e sofridas
- Cartões disciplinares

### 🏥 Sistema de Lesões
- Tipo e gravidade da lesão
- Tempo estimado de recuperação
- Impacto na equipa (escala 1-5)
- Qualidade dos substitutos

## Estrutura do Sistema

### 1. Base de Dados (SQLite)
```
├── equipa (equipas e informações básicas)
├── jogador (jogadores e posições)
├── jogo (jogos e resultados)
├── desempenho_equipa_jogo (estatísticas por jogo)
├── desempenho_jogador_jogo (estatísticas individuais)
├── lesoes (relatório de lesões)
└── confrontos_diretos (histórico entre equipas)
```

### 2. Motor de Análise (Python)
- `FootballDataCollector`: Recolha e armazenamento de dados
- `FootballPredictionEngine`: Algoritmo de previsão
- Sistema de ponderação configurável
- Validação e backtesting

### 3. Interface Web (React)
- Dashboard interativo
- Visualizações em tempo real
- Análise detalhada por jogo
- Relatórios de estatísticas e lesões

## Como Usar

### Instalação e Configuração

1. **Configurar o Backend**:
```bash
# Instalar dependências Python
pip install sqlite3 requests

# Executar sistema de teste
python3 simple_test.py
```

2. **Configurar a Interface Web**:
```bash
# Navegar para o diretório da aplicação
cd football-betting-analyzer

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev -- --host
```

3. **Aceder à Interface**:
   - Abrir browser em `http://localhost:5174`
   - Navegar pelas diferentes secções (Previsões, Estatísticas, Lesões, Análise)

### Utilização Diária

1. **Selecionar Data**: Escolher a data para análise (hoje, amanhã, ou data específica)
2. **Ver Previsões**: Analisar as previsões para jogos agendados
3. **Consultar Estatísticas**: Verificar desempenho das equipas
4. **Verificar Lesões**: Consultar relatório de jogadores lesionados
5. **Entender Análise**: Ler explicação detalhada da metodologia

## Algoritmo de Previsão

### Fórmula de Cálculo
```
Pontuação Final = (
    Força_Equipa × 0.40 +
    Impacto_Jogadores × 0.25 +
    Impacto_Lesões × 0.15 +
    Confrontos_Diretos × 0.10 +
    Fator_Casa_Fora × 0.10
)
```

### Conversão para Probabilidades
1. Normalização das pontuações
2. Cálculo de probabilidade de empate baseado na diferença
3. Distribuição final das probabilidades

### Validação
- **Backtesting**: Teste com dados históricos
- **Comparação com Odds**: Análise de valor vs casas de apostas
- **Monitorização**: Acompanhamento de resultados reais
- **Ajustes**: Refinamento contínuo do modelo

## Ficheiros Principais

### Backend
- `football_betting_analyzer.py`: Sistema de recolha de dados
- `prediction_engine.py`: Motor de previsão
- `simple_test.py`: Sistema de teste
- `football_data.db`: Base de dados SQLite

### Frontend
- `src/App.jsx`: Interface principal
- `src/components/ui/`: Componentes de interface
- `index.html`: Página principal

### Documentação
- `README.md`: Este ficheiro
- `todo.md`: Lista de tarefas concluídas

## Exemplo de Análise

### Jogo: SL Benfica vs FC Porto
```
Previsão: Vitória SL Benfica (53.7% confiança)

Probabilidades:
• Vitória SL Benfica: 53.7%
• Empate: 9.6%
• Vitória FC Porto: 36.7%

Análise Detalhada:
• Força da Equipa: 35.7% vs 40.7%
• Impacto Jogadores: 50.0% vs 50.0%
• Impacto Lesões: 100.0% vs 76.0%
• Fator Casa/Fora: 100.0% vs 7.5%
• Confrontos Diretos: 92.5% vs 7.5%

Pontuação Final: Casa 0.756 | Fora 0.544
```

## Limitações e Considerações

### Limitações Atuais
- Dados de exemplo para demonstração
- Necessita integração com APIs de dados reais
- Modelo pode necessitar calibração com mais dados

### Melhorias Futuras
- Integração com APIs de dados em tempo real
- Machine Learning para otimização automática
- Análise de sentimento e fatores externos
- Previsões de mercados específicos (golos, cantos, etc.)

## Suporte Técnico

### Requisitos do Sistema
- Python 3.11+
- Node.js 20+
- Navegador moderno
- 2GB RAM mínimo

### Resolução de Problemas
1. **Base de dados bloqueada**: Remover `football_data.db` e executar novamente
2. **Porta ocupada**: Alterar porta no comando `npm run dev`
3. **Dependências em falta**: Executar `npm install` novamente

## Licença e Uso

Este sistema foi desenvolvido para fins educacionais e de demonstração. Para uso comercial, recomenda-se:
- Validação adicional com dados reais
- Testes extensivos de backtesting
- Conformidade com regulamentações locais
- Gestão responsável de risco

---

**Desenvolvido por**: Manus AI  
**Data**: 27 de Junho de 2025  
**Versão**: 1.0.0

