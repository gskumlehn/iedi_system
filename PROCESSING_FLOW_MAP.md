# Mapeamento do Fluxo de Processamento IEDI

**Autor**: Manus AI  
**Data**: 15 de novembro de 2025

---

## Visão Geral do Fluxo

O processamento IEDI é dividido em **7 etapas principais**:

```
1. Coleta Brandwatch
   ↓
2. Enriquecimento de Dados
   ↓
3. Detecção de Bancos
   ↓
4. Cálculo IEDI por Menção
   ↓
5. Armazenamento
   ↓
6. Agregação por Período
   ↓
7. Geração de Resultados
```

---

## Etapa 1: Coleta Brandwatch

### Responsável
`BrandwatchService` (a ser implementado)

### Entrada
- **Período**: data_inicio, data_fim
- **Credenciais**: API key, project_id, query_name
- **Filtros**: mediaType=News, language=pt

### Processamento
1. Autenticar na Brandwatch API
2. Buscar menções do período
3. Filtrar apenas mediaType="News"
4. Paginar resultados (max 5000 por request)
5. Extrair campos relevantes

### Saída
Lista de menções brutas (JSON):
```json
{
  "id": "bw_123456",
  "title": "Banco do Brasil anuncia lucro recorde",
  "snippet": "O Banco do Brasil divulgou...",
  "fullText": "O Banco do Brasil divulgou ontem...",
  "url": "https://valor.globo.com/...",
  "domain": "valor.globo.com",
  "publishedDate": "2024-11-15T10:30:00Z",
  "sentiment": "positive",
  "mediaType": "News"
}
```

### Dependências
- Brandwatch API credentials
- bcr-api library

---

## Etapa 2: Enriquecimento de Dados

### Responsável
`MentionEnrichmentService` (a ser implementado)

### Entrada
Menção bruta da Brandwatch

### Processamento

#### 2.1 Buscar Veículo de Mídia
```python
# Buscar veículo por domínio
media_outlet = media_outlet_repo.find_by_domain(mention['domain'])

if media_outlet:
    monthly_visitors = media_outlet.monthly_visitors
    reach_group = media_outlet.reach_group
    is_relevant = media_outlet.is_relevant
    is_niche = media_outlet.is_niche
else:
    # Veículo não cadastrado - usar valores padrão
    monthly_visitors = 0
    reach_group = 'D'
    is_relevant = False
    is_niche = False
```

#### 2.2 Normalizar Sentimento
```python
# Mapear sentimento Brandwatch para enum interno
sentiment_map = {
    'positive': Sentiment.POSITIVE,
    'negative': Sentiment.NEGATIVE,
    'neutral': Sentiment.NEUTRAL
}
sentiment = sentiment_map.get(mention['sentiment'], Sentiment.NEUTRAL)
```

#### 2.3 Extrair Primeiro Parágrafo
```python
# Verificar se temos texto completo
if mention['snippet'] != mention['fullText']:
    # Extrair primeiro parágrafo do fullText
    first_paragraph = extract_first_paragraph(mention['fullText'])
else:
    # Apenas snippet disponível (paywall)
    first_paragraph = None
```

### Saída
Menção enriquecida:
```python
{
    'brandwatch_id': 'bw_123456',
    'title': 'Banco do Brasil anuncia lucro recorde',
    'snippet': 'O Banco do Brasil divulgou...',
    'full_text': 'O Banco do Brasil divulgou ontem...',
    'first_paragraph': 'O Banco do Brasil divulgou...',  # Extraído
    'url': 'https://valor.globo.com/...',
    'domain': 'valor.globo.com',
    'published_date': datetime(2024, 11, 15, 10, 30),
    'sentiment': Sentiment.POSITIVE,
    'media_outlet_id': 'uuid-valor',
    'monthly_visitors': 14000000,
    'reach_group': ReachGroup.C,
    'is_relevant_outlet': True,
    'is_niche_outlet': True
}
```

### Dependências
- `MediaOutletRepository`
- Tabela `media_outlets` populada

---

## Etapa 3: Detecção de Bancos

### Responsável
`BankDetectionService` (a ser implementado)

### Entrada
Menção enriquecida

### Processamento

#### 3.1 Buscar Todos os Bancos
```python
banks = bank_repo.find_all()
```

#### 3.2 Detectar Bancos no Título
```python
detected_banks = []

for bank in banks:
    # Verificar nome principal
    if bank.name.lower() in mention['title'].lower():
        detected_banks.append(bank)
        continue
    
    # Verificar variações (BB, Itaú, etc.)
    for variation in bank.variations:
        if variation.lower() in mention['title'].lower():
            detected_banks.append(bank)
            break
```

#### 3.3 Detectar Bancos no Texto Completo
```python
# Se não encontrou no título, buscar no texto completo
if not detected_banks and mention['full_text']:
    for bank in banks:
        if bank.name.lower() in mention['full_text'].lower():
            detected_banks.append(bank)
```

### Saída
Lista de bancos detectados:
```python
[
    {
        'bank_id': 'uuid-bb',
        'bank_name': 'Banco do Brasil',
        'found_in_title': True,
        'found_in_first_paragraph': True
    },
    {
        'bank_id': 'uuid-itau',
        'bank_name': 'Itaú',
        'found_in_title': True,
        'found_in_first_paragraph': False
    }
]
```

### Dependências
- `BankRepository`
- Tabela `banks` populada com variações

---

## Etapa 4: Cálculo IEDI por Menção

### Responsável
`IEDICalculationService` (a ser implementado)

### Entrada
- Menção enriquecida
- Banco detectado

### Processamento

#### 4.1 Verificações Binárias
```python
# 1. Título verificado
title_verified = 1 if bank_found_in_title else 0

# 2. Subtítulo verificado (condicional)
if mention['first_paragraph'] is not None:
    subtitle_verified = 1 if bank_found_in_first_paragraph else 0
    include_subtitle_in_denominator = True
else:
    subtitle_verified = 0
    include_subtitle_in_denominator = False

# 3. Veículo relevante
relevant_outlet_verified = 1 if mention['is_relevant_outlet'] else 0

# 4. Veículo de nicho
niche_outlet_verified = 1 if mention['is_niche_outlet'] else 0
```

#### 4.2 Cálculo do Numerador
```python
numerator = 0

# Título (peso 100)
if title_verified:
    numerator += 100

# Subtítulo (peso 80, condicional)
if include_subtitle_in_denominator and subtitle_verified:
    numerator += 80

# Grupo de Alcance (pesos variáveis)
reach_weights = {
    ReachGroup.A: 91,
    ReachGroup.B: 85,
    ReachGroup.C: 24,
    ReachGroup.D: 20
}
numerator += reach_weights[mention['reach_group']]

# Veículo Relevante (peso 95)
if relevant_outlet_verified:
    numerator += 95

# Veículo de Nicho (peso 54)
if niche_outlet_verified:
    numerator += 54
```

#### 4.3 Cálculo do Denominador
```python
# Denominadores por grupo (com e sem subtítulo)
denominators = {
    ReachGroup.A: {'with_subtitle': 366, 'without_subtitle': 286},
    ReachGroup.B: {'with_subtitle': 414, 'without_subtitle': 334},
    ReachGroup.C: {'with_subtitle': 353, 'without_subtitle': 273},
    ReachGroup.D: {'with_subtitle': 349, 'without_subtitle': 269}
}

if include_subtitle_in_denominator:
    denominator = denominators[mention['reach_group']]['with_subtitle']
else:
    denominator = denominators[mention['reach_group']]['without_subtitle']
```

#### 4.4 Cálculo do IEDI
```python
# Sinal (sentimento)
if mention['sentiment'] == Sentiment.POSITIVE:
    sign = +1
elif mention['sentiment'] == Sentiment.NEGATIVE:
    sign = -1
else:  # NEUTRAL
    sign = 0

# IEDI (-1 a 1)
if sign == 0:
    iedi_score = 0.0
else:
    iedi_score = (numerator / denominator) * sign

# IEDI normalizado (0 a 1)
iedi_normalized = (iedi_score + 1) / 2
```

### Saída
Resultado do cálculo IEDI:
```python
{
    'iedi_score': 0.85,
    'iedi_normalized': 0.925,
    'numerator': 353,
    'denominator': 366,
    'title_verified': 1,
    'subtitle_verified': 1,
    'relevant_outlet_verified': 1,
    'niche_outlet_verified': 1
}
```

### Dependências
- Metodologia IEDI v2.0
- Enums: Sentiment, ReachGroup

---

## Etapa 5: Armazenamento

### Responsável
`MentionRepository` + `AnalysisMentionRepository`

### Entrada
- Menção enriquecida
- Bancos detectados
- Resultados IEDI

### Processamento

#### 5.1 Criar/Buscar Menção
```python
# Buscar menção existente por brandwatch_id
mention = mention_repo.find_by_brandwatch_id(brandwatch_id)

if not mention:
    # Criar nova menção (dados brutos apenas)
    mention = mention_repo.create(
        brandwatch_id=brandwatch_id,
        title=title,
        snippet=snippet,
        full_text=full_text,
        url=url,
        domain=domain,
        published_date=published_date,
        sentiment=sentiment,
        categories=[bank.name for bank in detected_banks],
        media_outlet_id=media_outlet_id,
        monthly_visitors=monthly_visitors,
        reach_group=reach_group
    )
```

#### 5.2 Criar Relacionamentos com Cálculos IEDI
```python
for bank_detection in detected_banks:
    bank_id = bank_detection['bank_id']
    iedi_result = calculate_iedi(mention, bank_detection)
    
    # Criar relacionamento análise-menção-banco
    analysis_mention_repo.create(
        analysis_id=analysis.id,
        mention_id=mention.id,
        bank_id=bank_id,
        iedi_score=iedi_result['iedi_score'],
        iedi_normalized=iedi_result['iedi_normalized'],
        numerator=iedi_result['numerator'],
        denominator=iedi_result['denominator'],
        title_verified=iedi_result['title_verified'],
        subtitle_verified=iedi_result['subtitle_verified'],
        relevant_outlet_verified=iedi_result['relevant_outlet_verified'],
        niche_outlet_verified=iedi_result['niche_outlet_verified']
    )
```

### Saída
Registros criados:
- 1 registro em `mentions` (se novo)
- N registros em `analysis_mentions` (N = número de bancos detectados)

### Dependências
- `MentionRepository`
- `AnalysisMentionRepository`
- `Analysis` criada previamente

---

## Etapa 6: Agregação por Período

### Responsável
`IEDIAggregationService` (a ser implementado)

### Entrada
- `analysis_id`

### Processamento

#### 6.1 Buscar Todos os Relacionamentos da Análise
```python
analysis_mentions = analysis_mention_repo.find_by_analysis(analysis_id)
```

#### 6.2 Agrupar por Banco
```python
mentions_by_bank = {}

for am in analysis_mentions:
    if am.bank_id not in mentions_by_bank:
        mentions_by_bank[am.bank_id] = []
    
    mentions_by_bank[am.bank_id].append(am)
```

#### 6.3 Calcular Métricas por Banco
```python
for bank_id, mentions in mentions_by_bank.items():
    # Volume total
    volume_total = len(mentions)
    
    # Volume por sentimento
    volume_positive = sum(1 for m in mentions if m.sentiment == 'positive')
    volume_negative = sum(1 for m in mentions if m.sentiment == 'negative')
    volume_neutral = sum(1 for m in mentions if m.sentiment == 'neutral')
    
    # IEDI médio (apenas menções positivas e negativas)
    non_neutral = [m for m in mentions if m.sentiment != 'neutral']
    iedi_medio = sum(m.iedi_score for m in non_neutral) / len(non_neutral)
    
    # Proporção de positivas
    proporcao_positivas = volume_positive / volume_total
    
    # IEDI final (balizamento)
    iedi_final = iedi_medio * proporcao_positivas
    
    # Positividade e negatividade
    positividade = (volume_positive / volume_total) * 100
    negatividade = (volume_negative / volume_total) * 100
```

### Saída
Métricas agregadas por banco:
```python
{
    'bank_id': 'uuid-bb',
    'volume_total': 312,
    'volume_positive': 234,
    'volume_negative': 45,
    'volume_neutral': 33,
    'iedi_medio': 7.85,
    'proporcao_positivas': 0.75,
    'iedi_final': 5.89,
    'positividade': 75.0,
    'negatividade': 14.4
}
```

### Dependências
- `AnalysisMentionRepository`
- Metodologia IEDI (balizamento)

---

## Etapa 7: Geração de Resultados

### Responsável
`IEDIResultRepository`

### Entrada
Métricas agregadas por banco

### Processamento

#### 7.1 Buscar Bank Period
```python
# Buscar ou criar bank_period
bank_period = bank_period_repo.find_by_analysis_and_bank(
    analysis_id=analysis.id,
    bank_id=bank_id
)

if not bank_period:
    bank_period = bank_period_repo.create(
        analysis_id=analysis.id,
        bank_id=bank_id,
        start_date=analysis.start_date,
        end_date=analysis.end_date
    )
```

#### 7.2 Criar Resultado IEDI
```python
iedi_result = iedi_result_repo.create(
    bank_period_id=bank_period.id,
    volume_total=metrics['volume_total'],
    volume_positive=metrics['volume_positive'],
    volume_negative=metrics['volume_negative'],
    volume_neutral=metrics['volume_neutral'],
    iedi_medio=metrics['iedi_medio'],
    iedi_final=metrics['iedi_final'],
    positividade=metrics['positividade'],
    negatividade=metrics['negatividade']
)
```

#### 7.3 Gerar Ranking
```python
# Buscar todos os resultados da análise
all_results = iedi_result_repo.find_by_analysis(analysis_id)

# Ordenar por IEDI final (decrescente)
ranking = sorted(all_results, key=lambda x: x.iedi_final, reverse=True)

# Atribuir posições
for position, result in enumerate(ranking, start=1):
    result.ranking_position = position
    iedi_result_repo.update(result.id, ranking_position=position)
```

### Saída
Registros criados:
- N registros em `bank_periods` (N = número de bancos detectados)
- N registros em `iedi_results`
- Ranking atualizado

### Dependências
- `BankPeriodRepository`
- `IEDIResultRepository`

---

## Fluxo Completo (Exemplo)

### Entrada
```python
analysis = {
    'name': 'Novembro 2024',
    'start_date': '2024-11-01',
    'end_date': '2024-11-30'
}
```

### Processamento

```python
# 1. Coleta Brandwatch
brandwatch_mentions = brandwatch_service.extract_mentions(
    start_date='2024-11-01',
    end_date='2024-11-30'
)
# Resultado: 15.000 menções

# 2. Enriquecimento
enriched_mentions = []
for bw_mention in brandwatch_mentions:
    enriched = enrichment_service.enrich(bw_mention)
    enriched_mentions.append(enriched)

# 3. Detecção de Bancos
for mention in enriched_mentions:
    detected_banks = detection_service.detect_banks(mention)
    
    # 4. Cálculo IEDI
    for bank in detected_banks:
        iedi_result = calculation_service.calculate_iedi(mention, bank)
        
        # 5. Armazenamento
        mention_record = mention_repo.find_or_create(
            brandwatch_id=mention['brandwatch_id'],
            **mention
        )
        
        analysis_mention_repo.create(
            analysis_id=analysis.id,
            mention_id=mention_record.id,
            bank_id=bank['bank_id'],
            **iedi_result
        )

# 6. Agregação
aggregation_service.aggregate_by_period(analysis.id)

# 7. Geração de Resultados
results = iedi_result_repo.find_by_analysis(analysis.id)
```

### Saída
```python
{
    'analysis_id': 'uuid-analysis-nov2024',
    'total_mentions_processed': 15000,
    'unique_mentions_stored': 14850,
    'banks_detected': 4,
    'results': [
        {
            'position': 1,
            'bank': 'Banco do Brasil',
            'iedi_final': 7.42,
            'volume_total': 312,
            'positividade': 75.0
        },
        {
            'position': 2,
            'bank': 'Itaú',
            'iedi_final': 7.85,
            'volume_total': 245,
            'positividade': 82.0
        },
        {
            'position': 3,
            'bank': 'Bradesco',
            'iedi_final': 6.91,
            'volume_total': 198,
            'positividade': 71.0
        },
        {
            'position': 4,
            'bank': 'Santander',
            'iedi_final': 6.23,
            'volume_total': 176,
            'positividade': 68.0
        }
    ]
}
```

---

## Dependências entre Etapas

```
Etapa 1 (Coleta)
  ↓
Etapa 2 (Enriquecimento) ← Depende de: media_outlets
  ↓
Etapa 3 (Detecção) ← Depende de: banks
  ↓
Etapa 4 (Cálculo) ← Depende de: metodologia IEDI
  ↓
Etapa 5 (Armazenamento) ← Depende de: analysis criada
  ↓
Etapa 6 (Agregação) ← Depende de: etapa 5 completa
  ↓
Etapa 7 (Resultados) ← Depende de: etapa 6 completa
```

---

## Próximos Passos

1. Implementar services faltantes
2. Criar testes unitários para cada etapa
3. Implementar tratamento de erros robusto
4. Adicionar logging detalhado
5. Criar interface de monitoramento
6. Implementar processamento assíncrono (Celery)
7. Adicionar cache para otimização
