# Análise Completa do Fluxo IEDI - Sistema Atual

## Visão Geral

Este documento mapeia **minuciosamente** o fluxo completo do sistema IEDI, desde a criação de uma `Analysis` até o cálculo final dos resultados.

---

## Fluxo Completo (Passo a Passo)

### 1. Criação da Analysis

**Entry Point**: `AnalysisService.save()`

**Assinatura**:
```python
def save(
    self, 
    name=None,                    # Nome da análise
    query=None,                   # Nome da query Brandwatch
    bank_names=None,              # Lista de nomes de bancos (modo padrão)
    start_date=None,              # Data início (modo padrão)
    end_date=None,                # Data fim (modo padrão)
    custom_bank_dates=None        # Lista de dicts com datas customizadas por banco
) -> Analysis
```

**Parâmetros**:
- **Modo Padrão**: `bank_names` + `start_date` + `end_date`
  - Todos os bancos usam o mesmo período
  - Exemplo: `["Banco do Brasil", "Itaú"]` com `2024-10-01` a `2024-10-31`

- **Modo Customizado**: `custom_bank_dates`
  - Cada banco tem seu próprio período
  - Exemplo:
    ```python
    [
        {
            "bank_name": "Banco do Brasil",
            "start_date": "2024-10-01",
            "end_date": "2024-10-31"
        },
        {
            "bank_name": "Itaú",
            "start_date": "2024-09-01",
            "end_date": "2024-09-30"
        }
    ]
    ```

**Processo**:
```
1. Validar name e query (obrigatórios)
   ↓
2. BankAnalysisService.validate() - Validar bancos e datas
   ↓
3. Criar objeto Analysis (name, query_name, is_custom_dates)
   ↓
4. AnalysisRepository.save(analysis) - Salvar no banco
   ↓
5. BankAnalysisService.save_all() - Criar BankAnalysis para cada banco
   ↓
6. Iniciar thread assíncrona: MentionAnalysisService.process_mention_analysis()
   ↓
7. Retornar Analysis criada
```

---

### 2. Validação e Criação de BankAnalysis

**Service**: `BankAnalysisService.validate()`

**Processo**:
```
1. Verificar se é modo padrão OU customizado (não ambos)
   ↓
2. Se modo padrão:
   - Validar e parsear start_date e end_date
   - Validar range (start < end < now)
   - Para cada bank_name:
     * Validar se existe no enum BankName
     * Criar BankAnalysis(bank_name, start_date, end_date)
   ↓
3. Se modo customizado:
   - Para cada item em custom_bank_dates:
     * Validar e parsear start_date e end_date
     * Validar range (start < end < now)
     * Validar se bank_name existe no enum BankName
     * Criar BankAnalysis(bank_name, start_date, end_date)
   ↓
4. Retornar lista de BankAnalysis validados
```

**Campos de BankAnalysis criados**:
```python
BankAnalysis(
    id=generate_uuid(),           # Gerado automaticamente
    analysis_id=None,             # Será setado depois
    bank_name="Banco do Brasil",  # Enum BankName
    start_date=datetime(...),
    end_date=datetime(...),
    total_mentions=0,             # Será calculado depois
    positive_volume=0.0,          # Será calculado depois
    negative_volume=0.0,          # Será calculado depois
    iedi_mean=None,               # Será calculado depois
    iedi_score=None               # Será calculado depois
)
```

---

### 3. Salvamento de BankAnalysis

**Service**: `BankAnalysisService.save_all()`

**Processo**:
```
Para cada BankAnalysis na lista:
  1. Setar analysis_id
  2. BankAnalysisRepository.save(bank_analysis)
```

---

### 4. Processamento Assíncrono de Mentions

**Service**: `MentionAnalysisService.process_mention_analysis()`

**Executado em thread separada**

**Processo**:
```
1. Verificar se is_custom_dates
   ↓
2. Se custom_dates:
   - process_custom_dates()
   - Para cada BankAnalysis:
     * Buscar mentions do período específico
     * Processar mentions para este banco
     * Calcular métricas e atualizar BankAnalysis
   ↓
3. Se standard_dates:
   - process_standard_dates()
   - Buscar mentions UMA VEZ (período do primeiro banco)
   - Para cada BankAnalysis:
     * Filtrar mentions para este banco
     * Processar mentions
     * Calcular métricas e atualizar BankAnalysis
```

---

### 5. Busca e Filtragem de Mentions

**Service**: `MentionService.fetch_and_filter_mentions()`

**Processo**:
```
1. BrandwatchService.fetch(start_date, end_date, query_name)
   ↓
2. BrandwatchClient.queries.get_mentions()
   - Conecta com Brandwatch via bcr-api
   - Retorna lista de dicts com dados das mentions
   ↓
3. Para cada mention_data:
   - Verificar se contentSource == "News"
   - Se passar filtro:
     * Extrair categories de categoryDetails
     * Extrair URL (url ou originalUrl)
     * Verificar se mention já existe (por URL)
     * Se existe: atualizar
     * Se não existe: criar nova
     * Salvar/atualizar no banco
     * Adicionar à lista filtered_mentions
   ↓
4. Retornar lista de objetos Mention
```

**Campos de Mention**:
```python
Mention(
    id=generate_uuid(),
    url=...,
    brandwatch_id=...,
    original_url=...,
    title=...,
    snippet=...,
    full_text=...,
    domain=...,
    published_date=...,
    sentiment=...,              # "positive", "negative", "neutral"
    categories=[...],           # Lista de nomes de categorias
    monthly_visitors=...
)
```

---

### 6. Processamento de Mentions por Banco

**Service**: `MentionAnalysisService.process_mentions()`

**Processo**:
```
1. Buscar objeto Bank do banco (BankRepository.find_by_name())
   ↓
2. Para cada Mention:
   - Verificar se é válida para este banco:
     * mention.categories deve conter o objeto Bank
     * (is_valid_for_bank() verifica se bank in mention.categories)
   - Se válida:
     * create_mention_analysis(mention, bank)
     * Adicionar à lista mention_analyses
   ↓
3. Se há mention_analyses:
   - MentionAnalysisRepository.bulk_save(mention_analyses)
   ↓
4. Retornar lista de MentionAnalysis
```

**IMPORTANTE**: 
- `mention.categories` é uma **lista de objetos Bank**
- O método `is_valid_for_bank()` verifica se `bank in categories`
- Isso significa que a mention precisa ter sido categorizada na Brandwatch com o nome do banco

---

### 7. Criação de MentionAnalysis (Cálculo IEDI)

**Service**: `MentionAnalysisService.create_mention_analysis()`

**Processo Detalhado**:

#### 7.1. Extrair Dados Básicos
```python
mention_analysis = MentionAnalysis()
mention_analysis.mention_id = mention.id
mention_analysis.bank_name = bank.name  # Enum BankName
mention_analysis.sentiment = Sentiment.from_string(mention.sentiment)
```

#### 7.2. Classificar Reach Group
```python
mention_analysis.reach_group = classify_reach_group(mention.monthlyVisitors)

# Thresholds:
# A: > 10.000.000
# B: > 1.000.000
# C: >= 100.000
# D: < 100.000
```

#### 7.3. Verificar Menção no Título
```python
mention_analysis.title_mentioned = False
for variation in bank.variations:
    if variation.lower() in mention.title.lower():
        mention_analysis.title_mentioned = True
        break
```

#### 7.4. Verificar Menção no Subtítulo
```python
mention_analysis.subtitle_used = (mention.snippet != mention.full_text)

if subtitle_used:
    first_paragraph = extract_first_paragraph(mention.full_text)
    for variation in bank.variations:
        if variation.lower() in first_paragraph.lower():
            mention_analysis.subtitle_mentioned = True
            break
```

#### 7.5. Classificar Veículos
```python
relevant_domains = MediaOutletRepository.find_by_niche(False)
niche_domains = MediaOutletRepository.find_by_niche(True)

relevant_vehicle = mention.domain in relevant_domains
niche_vehicle = mention.domain in niche_domains

mention_analysis.niche_vehicle = niche_vehicle
```

#### 7.6. Calcular Numerador
```python
reach_weight = REACH_GROUP_WEIGHTS[reach_group]  # A=100, B=80, C=24, D=0

title_pts = 95 if title_mentioned else 0
subtitle_pts = 54 if (subtitle_mentioned and subtitle_used) else 0
relevant_pts = 95 if relevant_vehicle else 0
niche_pts = 54 if niche_vehicle else 0

numerator = title_pts + subtitle_pts + reach_weight + relevant_pts + niche_pts
```

#### 7.7. Calcular Denominador
```python
if subtitle_used:
    if reach_group == A:
        denominator = 95 + 54 + 100 + 95 = 344
    else:
        denominator = 95 + 54 + reach_weight + 95 + 54
else:
    if reach_group == A:
        denominator = 95 + 100 + 95 = 290
    else:
        denominator = 95 + reach_weight + 95 + 54
```

#### 7.8. Calcular IEDI Score
```python
sign = -1 if sentiment == NEGATIVE else 1

if denominator > 0:
    iedi_score = (numerator / denominator) * sign
    iedi_normalized = ((iedi_score + 1) / 2) * 10
else:
    iedi_score = 0
    iedi_normalized = 0
```

**Fórmulas**:
- `iedi_score`: -1.0 a +1.0
- `iedi_normalized`: 0 a 10

---

### 8. Cálculo de Métricas do Banco

**Service**: `BankAnalysisService.compute_and_persist_bank_metrics()`

**Processo**:
```python
total = len(mention_analyses)
positive = 0
negative = 0
normalized_vals = []

for mention_analysis in mention_analyses:
    if mention_analysis.sentiment == NEGATIVE:
        negative += 1
    else:
        positive += 1
    
    normalized_vals.append(mention_analysis.iedi_normalized)

# Calcular IEDI médio
iedi_mean = sum(normalized_vals) / len(normalized_vals) if normalized_vals else 0.0

# Calcular IEDI final (balizado pela positividade)
positivity_ratio = positive / total if total > 0 else 0.0
iedi_final = iedi_mean * positivity_ratio

# Atualizar BankAnalysis
bank_analysis.total_mentions = total
bank_analysis.positive_volume = positive
bank_analysis.negative_volume = negative
bank_analysis.iedi_mean = iedi_mean
bank_analysis.iedi_score = iedi_final

BankAnalysisRepository.update(bank_analysis)
```

**Fórmulas**:
- `iedi_mean`: Média aritmética de todos os `iedi_normalized`
- `positivity_ratio`: `positive / total`
- `iedi_final`: `iedi_mean × positivity_ratio`

---

## Resumo do Fluxo

```
1. AnalysisService.save()
   ├─ Validar name, query
   ├─ BankAnalysisService.validate() → Lista de BankAnalysis
   ├─ AnalysisRepository.save(analysis)
   ├─ BankAnalysisService.save_all() → Salvar BankAnalysis
   └─ Thread: MentionAnalysisService.process_mention_analysis()
       ├─ Se custom_dates:
       │   └─ Para cada BankAnalysis:
       │       ├─ MentionService.fetch_and_filter_mentions()
       │       │   ├─ BrandwatchService.fetch()
       │       │   │   └─ BrandwatchClient.queries.get_mentions()
       │       │   └─ Filtrar contentSource == "News"
       │       ├─ MentionAnalysisService.process_mentions()
       │       │   ├─ Para cada Mention:
       │       │   │   ├─ is_valid_for_bank() → bank in mention.categories
       │       │   │   └─ create_mention_analysis()
       │       │   │       ├─ Classificar reach_group
       │       │   │       ├─ Verificar title_mentioned
       │       │   │       ├─ Verificar subtitle_mentioned
       │       │   │       ├─ Classificar veículos
       │       │   │       ├─ Calcular numerador
       │       │   │       ├─ Calcular denominador
       │       │   │       └─ Calcular iedi_score e iedi_normalized
       │       │   └─ MentionAnalysisRepository.bulk_save()
       │       └─ BankAnalysisService.compute_and_persist_bank_metrics()
       │           ├─ Contar positive/negative
       │           ├─ Calcular iedi_mean
       │           ├─ Calcular iedi_final
       │           └─ BankAnalysisRepository.update()
       └─ Se standard_dates:
           ├─ MentionService.fetch_and_filter_mentions() (UMA VEZ)
           └─ Para cada BankAnalysis:
               ├─ MentionAnalysisService.process_mentions()
               └─ BankAnalysisService.compute_and_persist_bank_metrics()
```

---

## Pontos Críticos para o Teste

### 1. Variáveis de Ambiente Brandwatch
```bash
BW_PROJECT=<project_id>
BW_EMAIL=<username>
BW_PASSWORD=<password>
```

### 2. Categorias na Brandwatch
- **CRÍTICO**: Mentions precisam ter `categoryDetails` com o nome do banco
- Exemplo:
  ```json
  {
    "categoryDetails": [
      {"name": "Banco do Brasil"},
      {"name": "Notícias"}
    ]
  }
  ```
- O método `is_valid_for_bank()` verifica se `bank in mention.categories`
- Se a mention não tiver a categoria do banco, ela será **ignorada**

### 3. Banco Precisa Existir no Banco de Dados
```python
bank = BankRepository.find_by_name(bank_name)
# Precisa retornar objeto Bank com:
# - name (enum BankName)
# - variations (lista de strings)
```

### 4. Media Outlets Precisam Estar Cadastrados
```python
relevant_domains = MediaOutletRepository.find_by_niche(False)
niche_domains = MediaOutletRepository.find_by_niche(True)
# Precisam retornar listas de domínios
```

---

## Teste Correto (Estrutura)

```python
# 1. Criar Analysis via AnalysisService
analysis = AnalysisService().save(
    name="Análise Outubro 2024 - Banco do Brasil",
    query="OPERAÇÃO BB :: MONITORAMENTO",
    bank_names=["Banco do Brasil"],
    start_date="2024-10-01T00:00:00",
    end_date="2024-10-31T23:59:59"
)

# 2. Aguardar processamento assíncrono
# (ou mockar thread para executar sincronamente)

# 3. Buscar BankAnalysis criado
bank_analyses = BankAnalysisRepository.find_by_analysis_id(analysis.id)

# 4. Verificar resultados
for ba in bank_analyses:
    print(f"Banco: {ba.bank_name}")
    print(f"Total: {ba.total_mentions}")
    print(f"Positivas: {ba.positive_volume}")
    print(f"Negativas: {ba.negative_volume}")
    print(f"IEDI Médio: {ba.iedi_mean}")
    print(f"IEDI Final: {ba.iedi_score}")
```

---

## Diferenças do Fluxo Anterior

| Aspecto | Anterior (Incorreto) | Atual (Correto) |
|---------|---------------------|-----------------|
| **Entry Point** | `AnalysisRepository.create()` | `AnalysisService.save()` |
| **BankPeriod** | Criado manualmente | Criado via `BankAnalysisService` |
| **Nome da Tabela** | `bank_period` | `bank_analysis` |
| **Processamento** | Manual via Orchestrator | Automático via thread |
| **Detecção de Banco** | Via `BankDetectionService` | Via `categories` da mention |
| **Cálculo IEDI** | Via `IEDICalculationService` | Via `MentionAnalysisService` |

---

## Conclusão

O fluxo real do sistema é **completamente diferente** do que foi documentado anteriormente. O sistema usa:

1. **`AnalysisService`** como entry point (não `AnalysisRepository`)
2. **`BankAnalysis`** (não `BankPeriod`)
3. **Thread assíncrona** para processamento (não orquestrador manual)
4. **Categorias da Brandwatch** para detectar banco (não `BankDetectionService`)
5. **`MentionAnalysisService`** para calcular IEDI (não `IEDICalculationService`)

O teste precisa ser **completamente refatorado** para seguir este fluxo.
