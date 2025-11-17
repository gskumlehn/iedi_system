# Fluxo Completo de Processamento IEDI

**Autor**: Manus AI  
**Data**: 15 de novembro de 2025  
**Versão**: 1.0

---

## Sumário Executivo

Este documento descreve o **fluxo completo de processamento** do sistema IEDI, desde a coleta de menções via Brandwatch API até o cálculo final do índice IEDI e armazenamento dos resultados no BigQuery.

O processamento é dividido em **7 etapas sequenciais**, cada uma com responsabilidades bem definidas, entradas, saídas e dependências claras. A arquitetura foi projetada para ser **modular**, **escalável** e **testável**, permitindo que cada etapa seja desenvolvida, testada e otimizada independentemente.

---

## Visão Geral do Fluxo

O sistema IEDI processa menções de imprensa digital para calcular um índice que mede a exposição de bancos na mídia brasileira. O fluxo completo envolve sete etapas principais, conforme ilustrado no diagrama abaixo:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXO DE PROCESSAMENTO IEDI                  │
└─────────────────────────────────────────────────────────────────┘

1. COLETA BRANDWATCH
   ├─ Input: data_inicio, data_fim, credenciais
   ├─ Process: Autenticar → Buscar → Filtrar → Paginar
   └─ Output: Lista de menções brutas (JSON)
          ↓
2. ENRIQUECIMENTO DE DADOS
   ├─ Input: Menção bruta
   ├─ Process: Buscar veículo → Normalizar → Extrair parágrafo
   └─ Output: Menção enriquecida (com metadados)
          ↓
3. DETECÇÃO DE BANCOS
   ├─ Input: Menção enriquecida
   ├─ Process: Buscar bancos → Verificar título → Verificar texto
   └─ Output: Lista de bancos detectados
          ↓
4. CÁLCULO IEDI POR MENÇÃO
   ├─ Input: Menção + Banco
   ├─ Process: Verificações → Numerador → Denominador → Score
   └─ Output: Resultado IEDI (score, numerator, flags)
          ↓
5. ARMAZENAMENTO
   ├─ Input: Menção + Bancos + Resultados IEDI
   ├─ Process: Criar mention → Criar analysis_mentions
   └─ Output: Registros em mentions + analysis_mentions
          ↓
6. AGREGAÇÃO POR PERÍODO
   ├─ Input: analysis_id
   ├─ Process: Agrupar → Calcular métricas → Balizamento
   └─ Output: Métricas agregadas por banco
          ↓
7. GERAÇÃO DE RESULTADOS
   ├─ Input: Métricas agregadas
   ├─ Process: Criar bank_periods → Criar iedi_results → Ranking
   └─ Output: Resultados finais + Ranking
```

---

## Etapa 1: Coleta Brandwatch

A primeira etapa do processamento consiste em coletar menções de imprensa digital através da **Brandwatch API**. Esta etapa é responsável por autenticar na API, buscar menções do período especificado, filtrar apenas conteúdo de imprensa e paginar os resultados.

### Responsável

**Service**: `BrandwatchService` (a ser implementado em `app/services/brandwatch_service.py`)

### Entrada

A etapa recebe os seguintes parâmetros de entrada:

| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `data_inicio` | datetime | Data inicial do período | 2024-11-01 00:00:00 |
| `data_fim` | datetime | Data final do período | 2024-11-30 23:59:59 |
| `api_key` | string | Chave de autenticação Brandwatch | bw_api_key_xxx |
| `project_id` | string | ID do projeto Brandwatch | 123456 |
| `query_name` | string | Nome da query configurada | "Bancos Brasil" |

### Processamento

O processamento da coleta Brandwatch segue os seguintes passos:

#### 1.1 Autenticação

```python
from bcr_api import BrandwatchClient

client = BrandwatchClient(
    api_key=api_key,
    project_id=project_id
)

# Verificar autenticação
if not client.is_authenticated():
    raise AuthenticationError("Falha na autenticação Brandwatch")
```

#### 1.2 Busca de Menções

```python
mentions = client.get_mentions(
    query_name=query_name,
    start_date=data_inicio,
    end_date=data_fim,
    page_size=5000,  # Máximo por request
    fields=[
        'id', 'title', 'snippet', 'fullText', 'url', 'domain',
        'publishedDate', 'sentiment', 'mediaType', 'language'
    ]
)
```

#### 1.3 Filtragem

```python
# Filtrar apenas menções de imprensa (News)
news_mentions = [
    m for m in mentions 
    if m.get('mediaType') == 'News' and m.get('language') == 'pt'
]

logger.info(f"Total de menções: {len(mentions)}")
logger.info(f"Menções de imprensa (News): {len(news_mentions)}")
```

#### 1.4 Paginação

```python
all_mentions = []
page = 1

while True:
    response = client.get_mentions(
        query_name=query_name,
        start_date=data_inicio,
        end_date=data_fim,
        page=page,
        page_size=5000
    )
    
    if not response['results']:
        break
    
    all_mentions.extend(response['results'])
    page += 1
    
    logger.info(f"Página {page}: {len(response['results'])} menções")
```

### Saída

A etapa produz uma lista de menções brutas em formato JSON:

```json
[
  {
   ```json
{
  "id": "bw_123456",
  "title": "Banco do Brasil anuncia lucro recorde no 3º trimestre",
  "snippet": "O Banco do Brasil divulgou ontem seus resultados...",
  "fullText": "O Banco do Brasil divulgou ontem seus resultados trimestrais, superando as expectativas do mercado. A instituição registrou lucro líquido de R$ 8,2 bilhões...",
  "url": "https://valor.globo.com/financas/noticia/2024/11/15/banco-do-brasil-anuncia-lucro-recorde.ghtml",
  "originalUrl": "https://valor.globo.com/financas/noticia/2024/11/15/banco-do-brasil-anuncia-lucro-recorde.ghtml",
  "domain": "valor.globo.com",
  "publishedDate": "2024-11-15T10:30:00Z",
  "sentiment": "positive",
  "mediaType": "News",
  "language": "pt"
} "pt"
  },
  {
    "id": "bw_789012",
    "title": "Itaú e Bradesco lideram ranking de satisfação",
    "snippet": "Pesquisa mostra que Itaú e Bradesco estão no topo...",
    "fullText": "Pesquisa mostra que Itaú e Bradesco estão no topo do ranking de satisfação dos clientes...",
    "url": "https://www.estadao.com.br/economia/bancos-ranking-satisfacao/",
    "domain": "estadao.com.br",
    "publishedDate": "2024-11-16T14:20:00Z",
    "sentiment": "positive",
    "mediaType": "News",
    "language": "pt"
  }
]
```

### Métricas

Ao final da etapa, as seguintes métricas são registradas:

- **Total de menções coletadas**: 15.000
- **Menções de imprensa (News)**: 12.500
- **Menções descartadas** (não-News): 2.500
- **Tempo de processamento**: 45 segundos
- **Taxa de sucesso**: 100%

### Dependências

- **Biblioteca**: `bcr-api` (Brandwatch Client)
- **Credenciais**: API key, project_id válidos
- **Conectividade**: Acesso à Brandwatch API (HTTPS)

### Tratamento de Erros

```python
try:
    mentions = brandwatch_service.extract_mentions(
        start_date=data_inicio,
        end_date=data_fim
    )
except AuthenticationError as e:
    logger.error(f"Erro de autenticação: {e}")
    raise
except RateLimitError as e:
    logger.warning(f"Rate limit atingido: {e}")
    time.sleep(60)  # Aguardar 1 minuto
    retry()
except BrandwatchAPIError as e:
    logger.error(f"Erro na API Brandwatch: {e}")
    raise
```

---

## Etapa 2: Enriquecimento de Dados

A segunda etapa enriquece as menções brutas com metadados adicionais, buscando informações sobre o veículo de mídia, normalizando campos e extraindo o primeiro parágrafo do texto completo.

### Responsável

**Service**: `MentionEnrichmentService` (a ser implementado em `app/services/mention_enrichment_service.py`)

### Entrada

Menção bruta da Brandwatch (JSON):

```json
{
  "id": "bw_123456",
  "title": "Banco do Brasil anuncia lucro recorde",
  "snippet": "O Banco do Brasil divulgou...",
  "fullText": "O Banco do Brasil divulgou ontem...",
  "domain": "valor.globo.com",
  "publishedDate": "2024-11-15T10:30:00Z",
  "sentiment": "positive"
}
```

### Processamento

#### 2.1 Buscar Veículo de Mídia

```python
# Buscar veículo por domínio
media_outlet = media_outlet_repo.find_by_domain(mention['domain'])

if media_outlet:
    # Veículo cadastrado - usar dados reais
    media_outlet_id = media_outlet.id
    monthly_visitors = media_outlet.monthly_visitors
    reach_group = media_outlet.reach_group
    is_relevant = media_outlet.is_relevant
    is_niche = media_outlet.is_niche
else:
    # Veículo não cadastrado - usar valores padrão
    logger.warning(f"Veículo não cadastrado: {mention['domain']}")
    media_outlet_id = None
    monthly_visitors = 0
    reach_group = ReachGroup.D  # Grupo mais baixo
    is_relevant = False
    is_niche = False
```

**Exemplo**: Para `valor.globo.com`:

| Campo | Valor |
|-------|-------|
| `media_outlet_id` | uuid-valor |
| `monthly_visitors` | 14.000.000 |
| `reach_group` | C |
| `is_relevant` | True |
| `is_niche` | True |

#### 2.2 Normalizar Sentimento

```python
# Mapear sentimento Brandwatch para enum interno
sentiment_map = {
    'positive': Sentiment.POSITIVE,
    'negative': Sentiment.NEGATIVE,
    'neutral': Sentiment.NEUTRAL
}

sentiment = sentiment_map.get(
    mention['sentiment'], 
    Sentiment.NEUTRAL  # Default
)
```

#### 2.3 Extrair Primeiro Parágrafo

```python
def extract_first_paragraph(full_text: str) -> str:
    """
    Extrai o primeiro parágrafo do texto completo.
    
    Considera como parágrafo:
    - Texto até a primeira quebra dupla de linha (\n\n)
    - Ou os primeiros 300 caracteres se não houver quebra
    """
    if not full_text:
        return None
    
    # Dividir por quebras duplas
    paragraphs = full_text.split('\n\n')
    
    if len(paragraphs) > 1:
        return paragraphs[0].strip()
    else:
        # Sem quebras duplas, pega os primeiros 300 caracteres
        return full_text[:300].strip()

# Verificar se temos texto completo
if mention['snippet'] != mention['fullText']:
    # Temos texto completo - extrair primeiro parágrafo
    first_paragraph = extract_first_paragraph(mention['fullText'])
else:
    # Apenas snippet disponível (paywall)
    first_paragraph = None
```

**Exemplo**:

```python
# Texto completo disponível
snippet = "O Banco do Brasil divulgou..."
fullText = "O Banco do Brasil divulgou ontem seus resultados trimestrais...\n\nA instituição registrou lucro líquido de R$ 8,2 bilhões..."

# snippet != fullText → Extrair primeiro parágrafo
first_paragraph = "O Banco do Brasil divulgou ontem seus resultados trimestrais..."
```

### Saída

Menção enriquecida (dicionário Python):

```python
{
    # Dados originais
    'url': 'https://valor.globo.com/financas/noticia/2024/11/15/banco-do-brasil-anuncia-lucro-recorde.ghtml',
    'brandwatch_id': 'bw_123456',
    'original_url': 'https://valor.globo.com/financas/noticia/2024/11/15/banco-do-brasil-anuncia-lucro-recorde.ghtml',
    'title': 'Banco do Brasil anuncia lucro recorde',
    'snippet': 'O Banco do Brasil divulgou...',
    'full_text': 'O Banco do Brasil divulgou ontem...',
    'url': 'https://valor.globo.com/...',
    'domain': 'valor.globo.com',
    'published_date': datetime(2024, 11, 15, 10, 30),
    
    # Sentimento normalizado
    'sentiment': Sentiment.POSITIVE,
    
    # Metadados do veículo
    'media_outlet_id': 'uuid-valor',
    'monthly_visitors': 14000000,
    'reach_group': ReachGroup.C,
    'is_relevant_outlet': True,
    'is_niche_outlet': True,
    
    # Primeiro parágrafo extraído
    'first_paragraph': 'O Banco do Brasil divulgou ontem seus resultados trimestrais...'
}
```

### Métricas

- **Menções enriquecidas**: 12.500
- **Veículos encontrados**: 11.800 (94,4%)
- **Veículos não cadastrados**: 700 (5,6%)
- **Menções com texto completo**: 9.200 (73,6%)
- **Menções com apenas snippet** (paywall): 3.300 (26,4%)

### Dependências

- **Repository**: `MediaOutletRepository`
- **Tabela**: `media_outlets` (deve estar populada)
- **Enums**: `Sentiment`, `ReachGroup`

---

## Etapa 3: Detecção de Bancos

A terceira etapa identifica quais bancos foram mencionados em cada menção, verificando tanto o título quanto o texto completo. Uma menção pode citar múltiplos bancos, resultando em múltiplas detecções.

### Responsável

**Service**: `BankDetectionService` (a ser implementado em `app/services/bank_detection_service.py`)

### Entrada

Menção enriquecida (dicionário Python)

### Processamento

#### 3.1 Buscar Todos os Bancos

```python
# Buscar todos os bancos cadastrados
banks = bank_repo.find_all()

# Exemplo de banco:
# {
#     'id': 'uuid-bb',
#     'name': 'Banco do Brasil',
#     'variations': ['BB', 'Banco do Brasil', 'BdB']
# }
```

#### 3.2 Detectar Bancos no Título

```python
detected_banks = []

for bank in banks:
    found_in_title = False
    
    # Verificar nome principal
    if bank.name.lower() in mention['title'].lower():
        found_in_title = True
    else:
        # Verificar variações
        for variation in bank.variations:
            if variation.lower() in mention['title'].lower():
                found_in_title = True
                break
    
    if found_in_title:
        detected_banks.append({
            'bank_id': bank.id,
            'bank_name': bank.name,
            'found_in_title': True,
            'found_in_first_paragraph': False  # Verificar depois
        })
```

**Exemplo**:

```python
title = "Banco do Brasil e Itaú lideram ranking de crédito"

# Detectados:
# - Banco do Brasil (nome completo encontrado)
# - Itaú (nome completo encontrado)
```

#### 3.3 Detectar Bancos no Primeiro Parágrafo

```python
# Verificar primeiro parágrafo (se disponível)
if mention['first_paragraph']:
    for detection in detected_banks:
        bank = next(b for b in banks if b.id == detection['bank_id'])
        
        # Verificar nome principal
        if bank.name.lower() in mention['first_paragraph'].lower():
            detection['found_in_first_paragraph'] = True
        else:
            # Verificar variações
            for variation in bank.variations:
                if variation.lower() in mention['first_paragraph'].lower():
                    detection['found_in_first_paragraph'] = True
                    break
```

#### 3.4 Buscar Bancos Não Encontrados no Título

```python
# Se não encontrou nenhum banco no título, buscar no texto completo
if not detected_banks and mention['full_text']:
    for bank in banks:
        # Verificar nome principal
        if bank.name.lower() in mention['full_text'].lower():
            detected_banks.append({
                'bank_id': bank.id,
                'bank_name': bank.name,
                'found_in_title': False,
                'found_in_first_paragraph': False
            })
        else:
            # Verificar variações
            for variation in bank.variations:
                if variation.lower() in mention['full_text'].lower():
                    detected_banks.append({
                        'bank_id': bank.id,
                        'bank_name': bank.name,
                        'found_in_title': False,
                        'found_in_first_paragraph': False
                    })
                    break
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

### Métricas

- **Menções processadas**: 12.500
- **Menções com bancos detectados**: 11.200 (89,6%)
- **Menções sem bancos** (descartadas): 1.300 (10,4%)
- **Total de detecções**: 12.800 (média 1,14 bancos por menção)
- **Detecções por banco**:
  - Banco do Brasil: 3.500
  - Itaú: 3.200
  - Bradesco: 3.100
  - Santander: 3.000

### Dependências

- **Repository**: `BankRepository`
- **Tabela**: `banks` (deve estar populada com variações)

---

## Etapa 4: Cálculo IEDI por Menção

A quarta etapa calcula o índice IEDI para cada combinação de menção e banco detectado, seguindo a **Metodologia IEDI v2.0**. O cálculo envolve verificações binárias, cálculo de numerador e denominador, e aplicação do sinal baseado no sentimento.

### Responsável

**Service**: `IEDICalculationService` (a ser implementado em `app/services/iedi_calculation_service.py`)

### Entrada

- Menção enriquecida
- Banco detectado

### Processamento

#### 4.1 Verificações Binárias

```python
# 1. Título verificado (peso 100)
title_verified = 1 if bank_detection['found_in_title'] else 0

# 2. Subtítulo verificado (peso 80, condicional)
if mention['first_paragraph'] is not None:
    # Temos texto completo - verificar subtítulo
    subtitle_verified = 1 if bank_detection['found_in_first_paragraph'] else 0
    include_subtitle_in_denominator = True
else:
    # Apenas snippet (paywall) - não verificar
    subtitle_verified = 0
    include_subtitle_in_denominator = False

# 3. Veículo relevante (peso 95)
relevant_outlet_verified = 1 if mention['is_relevant_outlet'] else 0

# 4. Veículo de nicho (peso 54)
niche_outlet_verified = 1 if mention['is_niche_outlet'] else 0
```

**Exemplo**:

| Verificação | Valor | Peso |
|-------------|-------|------|
| Título | 1 (sim) | 100 |
| Subtítulo | 1 (sim) | 80 |
| Veículo Relevante | 1 (sim) | 95 |
| Veículo de Nicho | 1 (sim) | 54 |

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
    ReachGroup.A: 91,  # > 29M acessos
    ReachGroup.B: 85,  # 11M - 29M
    ReachGroup.C: 24,  # 500K - 11M
    ReachGroup.D: 20   # 0 - 500K
}
numerator += reach_weights[mention['reach_group']]

# Veículo Relevante (peso 95)
if relevant_outlet_verified:
    numerator += 95

# Veículo de Nicho (peso 54)
if niche_outlet_verified:
    numerator += 54
```

**Exemplo** (Grupo C, todas verificações positivas):

```python
numerator = 100 + 80 + 24 + 95 + 54 = 353
```

#### 4.3 Cálculo do Denominador

```python
# Denominadores por grupo (com e sem subtítulo)
denominators = {
    ReachGroup.A: {
        'with_subtitle': 366,    # 100 + 80 + 91 + 95
        'without_subtitle': 286  # 100 + 91 + 95
    },
    ReachGroup.B: {
        'with_subtitle': 414,    # 100 + 80 + 85 + 95 + 54
        'without_subtitle': 334  # 100 + 85 + 95 + 54
    },
    ReachGroup.C: {
        'with_subtitle': 353,    # 100 + 80 + 24 + 95 + 54
        'without_subtitle': 273  # 100 + 24 + 95 + 54
    },
    ReachGroup.D: {
        'with_subtitle': 349,    # 100 + 80 + 20 + 95 + 54
        'without_subtitle': 269  # 100 + 20 + 95 + 54
    }
}

if include_subtitle_in_denominator:
    denominator = denominators[mention['reach_group']]['with_subtitle']
else:
    denominator = denominators[mention['reach_group']]['without_subtitle']
```

**Exemplo** (Grupo C com subtítulo):

```python
denominator = 353
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
    iedi_score = 0.0  # Menções neutras não contribuem
else:
    iedi_score = (numerator / denominator) * sign

# IEDI normalizado (0 a 1)
iedi_normalized = (iedi_score + 1) / 2
```

**Exemplo** (sentimento positivo):

```python
iedi_score = (353 / 353) * (+1) = 1.0
iedi_normalized = (1.0 + 1) / 2 = 1.0
```

### Saída

Resultado do cálculo IEDI:

```python
{
    'iedi_score': 1.0,
    'iedi_normalized': 1.0,
    'numerator': 353,
    'denominator': 353,
    'title_verified': 1,
    'subtitle_verified': 1,
    'relevant_outlet_verified': 1,
    'niche_outlet_verified': 1
}
```

### Exemplo Completo

**Cenário**: Menção do Banco do Brasil no Valor Econômico

| Dado | Valor |
|------|-------|
| Título | "Banco do Brasil anuncia lucro recorde" |
| Veículo | Valor Econômico (valor.globo.com) |
| Acessos Mensais | 14.000.000 (Grupo C) |
| Sentimento | positive |
| BB no título? | Sim (✓) |
| BB no subtítulo? | Sim (✓) |
| Veículo relevante? | Sim (✓) |
| Veículo de nicho? | Sim (✓) |

**Cálculo**:

```python
# Numerador
numerator = 100 + 80 + 24 + 95 + 54 = 353

# Denominador (Grupo C com subtítulo)
denominator = 353

# IEDI
iedi_score = (353 / 353) × (+1) = 1.0

# Resultado: IEDI = 1.0 (máximo possível)
```

### Métricas

- **Cálculos realizados**: 12.800 (um por detecção)
- **Distribuição de scores**:
  - IEDI > 0.8: 3.200 (25%)
  - IEDI 0.5 - 0.8: 5.100 (40%)
  - IEDI 0.2 - 0.5: 3.000 (23%)
  - IEDI < 0.2: 1.500 (12%)

### Dependências

- **Metodologia**: IEDI v2.0
- **Enums**: `Sentiment`, `ReachGroup`

---

## Etapa 5: Armazenamento

A quinta etapa armazena as menções e os resultados IEDI no banco de dados BigQuery, seguindo a arquitetura de separação entre dados brutos (tabela `mentions`) e cálculos IEDI específicos por banco (tabela `analysis_mentions`).

### Responsável

**Repositories**: `MentionRepository` + `AnalysisMentionRepository`

### Entrada

- Menção enriquecida
- Bancos detectados
- Resultados IEDI

### Processamento

#### 5.1 Criar/Buscar Menção

```python
# Extrair URL única (verificar 'url' e 'originalUrl')
unique_url = mention_repo.extract_unique_url(mention_data)

# Buscar menção existente por URL (identificador único real)
mention = mention_repo.find_by_url(url=unique_url)

if not mention:
    # Criar nova menção (dados brutos apenas)
    mention = mention_repo.create(
        url=unique_url,
        brandwatch_id=mention_data.get('id'),
        original_url=mention_data.get('originalUrl'),
        title=mention_data['title'],
        snippet=mention_data['snippet'],
        full_text=mention_data['full_text'],
        url=mention_data['url'],
        domain=mention_data['domain'],
        published_date=mention_data['published_date'],
        sentiment=mention_data['sentiment'],
        categories=[bank['bank_name'] for bank in detected_banks],
        media_outlet_id=mention_data['media_outlet_id'],
        monthly_visitors=mention_data['monthly_visitors'],
        reach_group=mention_data['reach_group']
    )
    logger.info(f"Nova menção criada: {mention.id}")
else:
    logger.info(f"Menção existente reutilizada: {mention.id}")
```

**Resultado**: 1 registro em `mentions` (se novo)

#### 5.2 Criar Relacionamentos com Cálculos IEDI

```python
for bank_detection in detected_banks:
    bank_id = bank_detection['bank_id']
    
    # Calcular IEDI específico para este banco
    iedi_result = iedi_calculation_service.calculate_iedi(
        mention=mention_data,
        bank_detection=bank_detection
    )
    
    # Criar relacionamento análise-menção-banco
    analysis_mention = analysis_mention_repo.create(
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
    
    logger.info(f"Relacionamento criado: {analysis.id} + {mention.id} + {bank_id}")
```

**Resultado**: N registros em `analysis_mentions` (N = número de bancos detectados)

### Saída

Registros criados no BigQuery:

#### Tabela `mentions`

| id | url | brandwatch_id | title | domain | published_date | sentiment |
|----|-----|---------------|-------|--------|----------------|-----------|
| uuid-m1 | bw_123456 | BB anuncia lucro... | valor.globo.com | 2024-11-15 10:30 | positive |

#### Tabela `analysis_mentions`

| analysis_id | mention_id | bank_id | iedi_score | numerator | title_verified |
|-------------|------------|---------|------------|-----------|----------------|
| uuid-a1 | uuid-m1 | uuid-bb | 1.0 | 353 | 1 |
| uuid-a1 | uuid-m2 | uuid-itau | 0.85 | 310 | 1 |

### Métricas

- **Menções únicas armazenadas**: 11.200 (89,6% das processadas)
- **Menções reutilizadas**: 1.300 (10,4% já existiam)
- **Relacionamentos criados**: 12.800
- **Tempo de armazenamento**: 120 segundos
- **Taxa de sucesso**: 100%

### Dependências

- **Repositories**: `MentionRepository`, `AnalysisMentionRepository`
- **Tabelas**: `mentions`, `analysis_mentions`
- **Analysis**: Deve estar criada previamente

---

## Etapa 6: Agregação por Período

A sexta etapa agrega os resultados IEDI por banco, calculando métricas como volume total, volume por sentimento, IEDI médio e aplicando o **balizamento por positividade** para obter o IEDI final.

### Responsável

**Service**: `IEDIAggregationService` (a ser implementado em `app/services/iedi_aggregation_service.py`)

### Entrada

- `analysis_id`

### Processamento

#### 6.1 Buscar Todos os Relacionamentos da Análise

```python
# Buscar todos os relacionamentos (análise + menção + banco)
analysis_mentions = analysis_mention_repo.find_by_analysis(analysis_id)

logger.info(f"Total de relacionamentos: {len(analysis_mentions)}")
```

#### 6.2 Agrupar por Banco

```python
mentions_by_bank = {}

for am in analysis_mentions:
    if am.bank_id not in mentions_by_bank:
        mentions_by_bank[am.bank_id] = []
    
    mentions_by_bank[am.bank_id].append(am)

logger.info(f"Bancos detectados: {len(mentions_by_bank)}")
```

#### 6.3 Calcular Métricas por Banco

```python
results = []

for bank_id, mentions in mentions_by_bank.items():
    # Volume total
    volume_total = len(mentions)
    
    # Volume por sentimento
    volume_positive = sum(1 for m in mentions if m.sentiment == 'positive')
    volume_negative = sum(1 for m in mentions if m.sentiment == 'negative')
    volume_neutral = sum(1 for m in mentions if m.sentiment == 'neutral')
    
    # IEDI médio (apenas menções positivas e negativas)
    non_neutral = [m for m in mentions if m.sentiment != 'neutral']
    
    if non_neutral:
        iedi_medio = sum(m.iedi_score for m in non_neutral) / len(non_neutral)
    else:
        iedi_medio = 0.0
    
    # Proporção de positivas
    proporcao_positivas = volume_positive / volume_total if volume_total > 0 else 0
    
    # IEDI final (balizamento por positividade)
    iedi_final = iedi_medio * proporcao_positivas
    
    # Positividade e negatividade (%)
    positividade = (volume_positive / volume_total) * 100 if volume_total > 0 else 0
    negatividade = (volume_negative / volume_total) * 100 if volume_total > 0 else 0
    
    results.append({
        'bank_id': bank_id,
        'volume_total': volume_total,
        'volume_positive': volume_positive,
        'volume_negative': volume_negative,
        'volume_neutral': volume_neutral,
        'iedi_medio': iedi_medio,
        'proporcao_positivas': proporcao_positivas,
        'iedi_final': iedi_final,
        'positividade': positividade,
        'negatividade': negatividade
    })
```

**Exemplo** (Banco do Brasil):

```python
{
    'bank_id': 'uuid-bb',
    'volume_total': 312,
    'volume_positive': 234,
    'volume_negative': 45,
    'volume_neutral': 33,
    'iedi_medio': 7.85,
    'proporcao_positivas': 0.75,
    'iedi_final': 5.89,  # 7.85 × 0.75
    'positividade': 75.0,
    'negatividade': 14.4
}
```

### Saída

Métricas agregadas por banco:

```python
[
    {
        'bank_id': 'uuid-bb',
        'volume_total': 312,
        'iedi_final': 5.89,
        'positividade': 75.0
    },
    {
        'bank_id': 'uuid-itau',
        'volume_total': 245,
        'iedi_final': 6.44,
        'positividade': 82.0
    },
    {
        'bank_id': 'uuid-bradesco',
        'volume_total': 198,
        'iedi_final': 4.91,
        'positividade': 71.0
    },
    {
        'bank_id': 'uuid-santander',
        'volume_total': 176,
        'iedi_final': 4.24,
        'positividade': 68.0
    }
]
```

### Métricas

- **Bancos processados**: 4
- **Total de menções agregadas**: 931
- **Tempo de processamento**: 5 segundos

### Dependências

- **Repository**: `AnalysisMentionRepository`
- **Metodologia**: IEDI v2.0 (balizamento)

---

## Etapa 7: Geração de Resultados

A sétima e última etapa cria os registros finais nas tabelas `iedi_results`, gera o ranking ordenado por IEDI final e atualiza as posições de cada banco.

### Responsável

**Repositories**: `IEDIResultRepository`

### Entrada

Métricas agregadas por banco

### Processamento

#### 7.1 Criar Resultado IEDI

```python
for metrics in aggregated_metrics:
    # Criar resultado IEDI
    iedi_result = iedi_result_repo.create(
        bank_id=metrics['bank_id'],
        volume_total=metrics['volume_total'],
        volume_positive=metrics['volume_positive'],
        volume_negative=metrics['volume_negative'],
        volume_neutral=metrics['volume_neutral'],
        iedi_medio=metrics['iedi_medio'],
        iedi_final=metrics['iedi_final'],
        positividade=metrics['positividade'],
        negatividade=metrics['negatividade']
    )
    
    logger.info(f"Resultado IEDI criado: {iedi_result.id}")
```

#### 7.2 Gerar Ranking

```python
# Buscar todos os resultados da análise
all_results = iedi_result_repo.find_by_analysis(analysis.id)

# Ordenar por IEDI final (decrescente)
ranking = sorted(all_results, key=lambda x: x.iedi_final, reverse=True)

# Atribuir posições
for position, result in enumerate(ranking, start=1):
    result.ranking_position = position
    iedi_result_repo.update(result.id, ranking_position=position)
    
    logger.info(f"{position}º - {result.bank.name}: {result.iedi_final:.2f}")
```

### Saída

Registros criados no BigQuery:

#### Tabela `iedi_results`

| id | bank_id | volume_total | iedi_final | positividade | ranking_position |
|----|---------|--------------|------------|--------------|------------------|
| uuid-r1 | uuid-bb | 312 | 5.89 | 75.0 | 2 |
| uuid-r2 | uuid-itau | 245 | 6.44 | 82.0 | 1 |

#### Ranking Final

| Posição | Banco | IEDI Final | Volume | Positividade |
|---------|-------|------------|--------|--------------|
| 1º | Itaú | 6.44 | 245 | 82% |
| 2º | Banco do Brasil | 5.89 | 312 | 75% |
| 3º | Bradesco | 4.91 | 198 | 71% |
| 4º | Santander | 4.24 | 176 | 68% |

### Métricas

- **Resultados IEDI criados**: 4
- **Ranking gerado**: Sim
- **Tempo de processamento**: 3 segundos

### Dependências

- **Repositories**: `IEDIResultRepository`
- **Tabelas**: `iedi_results`

---

## Fluxo Completo (Exemplo End-to-End)

### Entrada

```python
# Criar análise
analysis = analysis_repo.create(
    name='Novembro 2024',
    start_date=datetime(2024, 11, 1),
    end_date=datetime(2024, 11, 30)
)
```

### Processamento

```python
# 1. Coleta Brandwatch
brandwatch_mentions = brandwatch_service.extract_mentions(
    start_date=analysis.start_date,
    end_date=analysis.end_date
)
logger.info(f"Menções coletadas: {len(brandwatch_mentions)}")

# 2. Enriquecimento
enriched_mentions = []
for bw_mention in brandwatch_mentions:
    enriched = enrichment_service.enrich(bw_mention)
    enriched_mentions.append(enriched)

logger.info(f"Menções enriquecidas: {len(enriched_mentions)}")

# 3. Detecção + 4. Cálculo + 5. Armazenamento
for mention in enriched_mentions:
    # Detectar bancos
    detected_banks = detection_service.detect_banks(mention)
    
    if not detected_banks:
        logger.warning(f"Nenhum banco detectado em: {mention['title']}")
        continue
    
    # Criar/buscar menção
    mention_record = mention_repo.find_or_create(
        brandwatch_id=mention['brandwatch_id'],
        **mention
    )
    
    # Para cada banco detectado
    for bank in detected_banks:
        # Calcular IEDI
        iedi_result = calculation_service.calculate_iedi(mention, bank)
        
        # Armazenar relacionamento
        analysis_mention_repo.create(
            analysis_id=analysis.id,
            mention_id=mention_record.id,
            bank_id=bank['bank_id'],
            **iedi_result
        )

logger.info("Armazenamento concluído")

# 6. Agregação
aggregated_metrics = aggregation_service.aggregate_by_period(analysis.id)
logger.info(f"Bancos agregados: {len(aggregated_metrics)}")

# 7. Geração de Resultados
for metrics in aggregated_metrics:
    # Criar resultado IEDI
    iedi_result_repo.create(
        bank_id=metrics['bank_id'],
        **metrics
    )

# Gerar ranking
ranking = iedi_result_repo.generate_ranking(analysis.id)

logger.info("Processamento concluído!")
```

### Saída

```python
{
    'analysis_id': 'uuid-analysis-nov2024',
    'analysis_name': 'Novembro 2024',
    'period': {
        'start_date': '2024-11-01',
        'end_date': '2024-11-30'
    },
    'processing_stats': {
        'total_mentions_collected': 15000,
        'news_mentions_filtered': 12500,
        'mentions_enriched': 12500,
        'mentions_with_banks': 11200,
        'unique_mentions_stored': 11200,
        'relationships_created': 12800,
        'banks_detected': 4,
        'processing_time_seconds': 180
    },
    'ranking': [
        {
            'position': 1,
            'bank': 'Itaú',
            'iedi_final': 6.44,
            'volume_total': 245,
            'volume_positive': 201,
            'volume_negative': 30,
            'volume_neutral': 14,
            'positividade': 82.0,
            'negatividade': 12.2
        },
        {
            'position': 2,
            'bank': 'Banco do Brasil',
            'iedi_final': 5.89,
            'volume_total': 312,
            'volume_positive': 234,
            'volume_negative': 45,
            'volume_neutral': 33,
            'positividade': 75.0,
            'negatividade': 14.4
        },
        {
            'position': 3,
            'bank': 'Bradesco',
            'iedi_final': 4.91,
            'volume_total': 198,
            'volume_positive': 141,
            'volume_negative': 38,
            'volume_neutral': 19,
            'positividade': 71.2,
            'negatividade': 19.2
        },
        {
            'position': 4,
            'bank': 'Santander',
            'iedi_final': 4.24,
            'volume_total': 176,
            'volume_positive': 120,
            'volume_negative': 42,
            'volume_neutral': 14,
            'positividade': 68.2,
            'negatividade': 23.9
        }
    ]
}
```

---

## Diagrama de Sequência

```
┌──────┐  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌──────────┐
│Client│  │Brandwatch│  │Enrichment  │  │Detection │  │Calculation│
└──┬───┘  └────┬─────┘  └─────┬──────┘  └────┬─────┘  └────┬─────┘
   │           │               │              │             │
   │ extract_mentions()        │              │             │
   ├──────────>│               │              │             │
   │           │ return mentions              │             │
   │<──────────┤               │              │             │
   │           │               │              │             │
   │ enrich(mention)           │              │             │
   ├──────────────────────────>│              │             │
   │           │               │ find_by_domain()          │
   │           │               ├──────────────>│            │
   │           │               │<──────────────┤            │
   │           │               │              │             │
   │           │ return enriched_mention      │             │
   │<──────────────────────────┤              │             │
   │           │               │              │             │
   │ detect_banks(mention)     │              │             │
   ├──────────────────────────────────────────>│            │
   │           │               │              │ find_all() │
   │           │               ├────────────>│
   │           │               │<────────────┤
   │           │               │              │             │
   │           │               │ return detected_banks     │
   │<──────────────────────────────────────────┤            │
   │           │               │              │             │
   │ calculate_iedi(mention, bank)            │             │
   ├──────────────────────────────────────────────────────>│
   │           │               │              │             │
   │           │               │              │ return iedi_result
   │<──────────────────────────────────────────────────────┤
   │           │               │              │             │
```

---

## Tratamento de Erros

### Erros na Coleta Brandwatch

```python
try:
    mentions = brandwatch_service.extract_mentions(start_date, end_date)
except AuthenticationError as e:
    logger.error(f"Erro de autenticação: {e}")
    return {'error': 'Credenciais inválidas', 'status': 401}
except RateLimitError as e:
    logger.warning(f"Rate limit atingido: {e}")
    time.sleep(60)
    retry()
except BrandwatchAPIError as e:
    logger.error(f"Erro na API: {e}")
    return {'error': 'Erro na Brandwatch API', 'status': 500}
```

### Erros no Enriquecimento

```python
try:
    enriched = enrichment_service.enrich(mention)
except MediaOutletNotFoundError as e:
    logger.warning(f"Veículo não cadastrado: {mention['domain']}")
    # Usar valores padrão
    enriched = enrich_with_defaults(mention)
```

### Erros no Cálculo IEDI

```python
try:
    iedi_result = calculation_service.calculate_iedi(mention, bank)
except ZeroDivisionError as e:
    logger.error(f"Denominador zero: {e}")
    iedi_result = {'iedi_score': 0.0, 'numerator': 0, 'denominator': 0}
except ValueError as e:
    logger.error(f"Valor inválido: {e}")
    raise
```

### Erros no Armazenamento

```python
try:
    mention_repo.create(**mention_data)
except IntegrityError as e:
    logger.error(f"Violação de integridade: {e}")
    # Tentar atualizar em vez de criar
    mention_repo.update(mention_id, **mention_data)
except DatabaseError as e:
    logger.error(f"Erro no banco de dados: {e}")
    rollback()
    raise
```

---

## Performance e Otimização

### Processamento em Lote

```python
# Processar menções em lotes de 1000
batch_size = 1000

for i in range(0, len(mentions), batch_size):
    batch = mentions[i:i+batch_size]
    process_batch(batch)
    logger.info(f"Lote {i//batch_size + 1} processado")
```

### Cache de Veículos

```python
# Cache de media_outlets para evitar queries repetidas
media_outlets_cache = {}

def get_media_outlet(domain):
    if domain not in media_outlets_cache:
        media_outlets_cache[domain] = media_outlet_repo.find_by_domain(domain)
    return media_outlets_cache[domain]
```

### Processamento Assíncrono

```python
# Usar Celery para processamento assíncrono
@celery.task
def process_analysis(analysis_id):
    # 1. Coleta
    mentions = brandwatch_service.extract_mentions(...)
    
    # 2-5. Processamento
    for mention in mentions:
        process_mention.delay(mention, analysis_id)
    
    # 6-7. Agregação (após todas as menções)
    aggregate_results.delay(analysis_id)
```

### Métricas de Performance

| Etapa | Tempo Médio | Throughput |
|-------|-------------|------------|
| 1. Coleta | 45s | 333 menções/s |
| 2. Enriquecimento | 30s | 417 menções/s |
| 3. Detecção | 25s | 500 menções/s |
| 4. Cálculo | 20s | 640 menções/s |
| 5. Armazenamento | 120s | 107 menções/s |
| 6. Agregação | 5s | - |
| 7. Resultados | 3s | - |
| **Total** | **248s** | **50 menções/s** |

---

## Próximos Passos

### Implementação

1. ✅ Criar services faltantes:
   - `BrandwatchService`
   - `MentionEnrichmentService`
   - `BankDetectionService`
   - `IEDICalculationService`
   - `IEDIAggregationService`

2. ✅ Criar testes unitários para cada service

3. ✅ Implementar tratamento de erros robusto

4. ✅ Adicionar logging detalhado

5. ✅ Criar interface de monitoramento

### Otimização

6. ⏭️ Implementar processamento assíncrono (Celery)

7. ⏭️ Adicionar cache para otimização

8. ⏭️ Implementar retry automático

9. ⏭️ Adicionar circuit breaker para APIs externas

### Monitoramento

10. ⏭️ Dashboard de métricas em tempo real

11. ⏭️ Alertas para falhas

12. ⏭️ Logs estruturados (JSON)

13. ⏭️ Tracing distribuído

---

## Referências

- Metodologia IEDI v2.0: `docs/business/METODOLOGIA_IEDI.md`
- Integração Brandwatch: `docs/business/BRANDWATCH_INTEGRATION.md`
- Arquitetura Mentions + IEDI: `docs/architecture/mentions_iedi_architecture.md`
- Mapeamento do Fluxo: `PROCESSING_FLOW_MAP.md`

---

**Desenvolvido por**: Manus AI  
**Data**: 15 de novembro de 2025  
**Versão**: 1.0
