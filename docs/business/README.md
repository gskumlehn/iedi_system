# Business Documentation - Sistema IEDI

Esta pasta contém documentação **específica do negócio** do Sistema IEDI (Índice de Exposição Digital na Imprensa), incluindo metodologia de cálculo, integração com Brandwatch e mapeamento de dados.

## Documentos

### Metodologia e Cálculos

1. **[METODOLOGIA_IEDI.md](./METODOLOGIA_IEDI.md)** - Metodologia completa do cálculo IEDI (versão final adaptada):
   - Fórmulas de cálculo
   - Pesos por grupo de alcance (A, B, C, D)
   - Bônus e verificações (título, subtítulo, veículo relevante, veículo de nicho)
   - Balizamento por positividade
   - Exemplos práticos

### Integração Brandwatch

2. **[MAPEAMENTO_BRANDWATCH.md](./MAPEAMENTO_BRANDWATCH.md)** - Mapeamento completo de campos da API Brandwatch:
   - Campos extraídos da API
   - Transformações necessárias
   - Filtros aplicados (mediaType: News)
   - Classificação de veículos por alcance

3. **[BRANDWATCH_INTEGRATION.md](./BRANDWATCH_INTEGRATION.md)** - Guia técnico de integração com a API Brandwatch:
   - Configuração de credenciais
   - Endpoints utilizados
   - Fluxo de extração de menções
   - Tratamento de erros e retry logic
   - Exemplos de código

4. **[BIGQUERY_INTEGRATION.md](./BIGQUERY_INTEGRATION.md)** - Integração com BigQuery como data warehouse:
   - Schema de tabelas
   - Queries de análise
   - Otimizações de performance

### Visualização e Análise

5. **[FORMULAS_POWERBI.md](./FORMULAS_POWERBI.md)** - Fórmulas DAX para Power BI:
   - Medidas calculadas (IEDI médio, positividade, etc.)
   - Colunas customizadas
   - Tabelas de apoio para visualizações

## Visão Geral do Sistema IEDI

O **Sistema IEDI** automatiza o cálculo do Índice de Exposição Digital na Imprensa para bancos brasileiros, integrando-se com a plataforma Brandwatch para extração de menções e aplicando metodologia proprietária de pontuação.

### Entidades Principais

- **Bancos**: Instituições financeiras analisadas (Banco do Brasil, Itaú, Bradesco, Santander)
- **Veículos Relevantes**: Portais de notícias classificados por grupo de alcance (A, B, C, D)
- **Veículos de Nicho**: Portais especializados em economia/finanças
- **Análises**: Períodos de coleta de dados (ex: 1T2025)
- **Menções**: Matérias extraídas da Brandwatch
- **Resultados IEDI**: Índices calculados por banco

### Fluxo Básico

1. **Configuração**: Cadastrar bancos, veículos e credenciais Brandwatch
2. **Análise**: Definir período de referência e datas de divulgação por banco
3. **Extração**: Conectar à Brandwatch API e extrair menções do período
4. **Cálculo**: Aplicar fórmulas IEDI em cada menção
5. **Agregação**: Calcular índice médio e aplicar balizamento
6. **Ranking**: Gerar comparativo entre bancos

### Metodologia IEDI (Resumo)

O IEDI é calculado com base em:

#### Componentes do Numerador
- **Grupo de Alcance do Veículo**: 20 a 91 pontos (A=91, B=85, C=24, D=20)
- **Bônus Veículo Relevante**: +95 pontos (se na lista de veículos relevantes)
- **Bônus Veículo de Nicho**: +54 pontos (exceto grupo A)
- **Presença no Título**: +100 pontos (banco mencionado no título)
- **Presença no Subtítulo**: +80 pontos (banco mencionado no snippet)

#### Denominadores
- **Grupo A**: 286 (positivo) ou 366 (negativo/neutro)
- **Outros Grupos**: 280 (positivo) ou 360 (negativo/neutro)

#### Fórmula Final
```
IEDI_Base = Numerador / Denominador
IEDI_Base = IEDI_Base × (-1) se sentimento ≠ positivo
IEDI_Escala = (10 × IEDI_Base + 1) / 2
IEDI_Final = IEDI_Médio × (% Positividade / 100)
```

### Grupos de Alcance

| Grupo | Visitantes Mensais | Peso |
|-------|-------------------|------|
| A     | ≥ 29 milhões      | 91   |
| B     | 11M - 29M         | 85   |
| C     | 500K - 11M        | 24   |
| D     | < 500K            | 20   |

## Diferença entre Architecture e Business

### `docs/architecture/` (Genérico)
- ✅ Padrões arquiteturais reutilizáveis
- ✅ Estrutura de código Flask + SQLAlchemy
- ✅ Design patterns (Repository, Blueprint, Factory)
- ✅ Aplicável a **qualquer** projeto web Python

### `docs/business/` (Específico)
- ✅ Regras de negócio do IEDI
- ✅ Integração com Brandwatch
- ✅ Fórmulas de cálculo proprietárias
- ✅ Aplicável **apenas** ao Sistema IEDI

## Navegação

- [← Voltar para raiz](../../README.md)
- [→ Documentação de Arquitetura](../architecture/README.md) - Padrões técnicos genéricos

## Contato

Para dúvidas sobre a metodologia IEDI ou integração Brandwatch, consulte os documentos específicos nesta pasta.
