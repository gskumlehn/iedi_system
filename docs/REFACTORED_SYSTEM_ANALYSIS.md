# Análise Completa do Sistema IEDI Refatorado

## Visão Geral

O sistema IEDI foi refatorado manualmente para separar claramente as responsabilidades entre **Análises** (períodos de coleta) e **Períodos por Banco** (períodos específicos de cada banco dentro de uma análise). Esta documentação analisa toda a estrutura refatorada em `/app`.

---

## Mudanças Arquiteturais Principais

### 1. Separação de Conceitos

**Antes**: `Analysis` continha apenas um período global

**Depois**: 
- `Analysis`: Representa uma coleta de dados com nome, query e período global
- `BankPeriod`: Representa o período específico de cada banco dentro de uma análise

### 2. Novo Fluxo de Dados

```
1. Criar Analysis (nome, query, custom_period)
   ↓
2. Criar BankPeriods (um para cada banco, com category_detail e datas)
   ↓
3. Extrair mentions da Brandwatch (usando query da Analysis)
   ↓
4. Detectar bancos em cada mention (via categoryDetails ou texto)
   ↓
5. Calcular IEDI para cada mention × banco
   ↓
6. Salvar AnalysisMention (mention_id, bank_id, iedi_score, etc)
   ↓
7. Agregar resultados por banco
   ↓
8. Salvar IEDIResult (analysis_id, bank_id, final_iedi, volumes, etc)
```

---

## Models Refatorados

### Analysis

**Arquivo**: `app/models/analysis.py`

**Campos**:
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | String(36) | UUID da análise |
| `name` | String(255) | Nome descritivo da análise |
| `query_name` | String(255) | Nome da query na Brandwatch |
| `start_date` | TIMESTAMP | Data de início global |
| `end_date` | TIMESTAMP | Data final global |
| `custom_period` | Boolean | Se usa períodos customizados por banco |
| `status` | String(50) | Status da análise (pending, processing, completed) |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Data de atualização |

**Características**:
- ✅ Usa `hybrid_property` para conversão automática UTC → America/Sao_Paulo
- ✅ Método `to_dict()` para serialização JSON
- ✅ Campos privados (`_start_date`) com getters/setters públicos

**Mudanças**:
- ❌ **Removido**: `period_type` (não existe mais no model)
- ✅ **Adicionado**: `name`, `query_name`, `custom_period`, `status`, `updated_at`

### BankPeriod (NOVO)

**Arquivo**: `app/models/bank_period.py`

**Campos**:
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | String(36) | UUID do período |
| `analysis_id` | String(36) | FK para Analysis |
| `bank_id` | String(36) | FK para Bank |
| `category_detail` | String(255) | Nome da categoria na Brandwatch |
| `start_date` | TIMESTAMP | Data de início específica do banco |
| `end_date` | TIMESTAMP | Data final específica do banco |
| `total_mentions` | Integer | Total de mentions processadas |
| `created_at` | TIMESTAMP | Data de criação |

**Propósito**:
- Permite períodos diferentes para cada banco dentro da mesma análise
- Armazena o `category_detail` usado para filtrar mentions do banco
- Rastreia quantas mentions foram processadas por banco

### IEDIResult

**Arquivo**: `app/models/iedi_result.py`

**Campos**:
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | String(36) | UUID do resultado |
| `analysis_id` | String(36) | FK para Analysis |
| `bank_id` | String(36) | FK para Bank |
| `total_volume` | Integer | Total de mentions |
| `positive_volume` | Integer | Mentions positivas |
| `negative_volume` | Integer | Mentions negativas |
| `neutral_volume` | Integer | Mentions neutras |
| `average_iedi` | Float | IEDI médio (média aritmética) |
| `final_iedi` | Float | IEDI final (balizado por positividade) |
| `positivity_rate` | Float | % de mentions positivas |
| `negativity_rate` | Float | % de mentions negativas |
| `created_at` | TIMESTAMP | Data de criação |

**Mudanças**:
- ❌ **Removido**: `total_mentions` (agora é `total_volume`)
- ✅ **Adicionado**: `positive_volume`, `negative_volume`, `neutral_volume`, `average_iedi`, `positivity_rate`, `negativity_rate`

---

## Services Refatorados

### IEDIOrchestrator

**Arquivo**: `app/services/iedi_orchestrator.py`

**Responsabilidade**: Orquestrar todo o fluxo de processamento de uma análise

**Método Principal**: `process_analysis(analysis_id, start_date, end_date, query_name)`

**Fluxo**:
1. Extrai mentions da Brandwatch via `BrandwatchService`
2. Para cada mention:
   - Processa mention via `MentionService`
   - Detecta bancos via `BankDetectionService`
   - Calcula IEDI para cada banco via `IEDICalculationService`
   - Salva `AnalysisMention` (relação mention × banco × iedi)
3. Cria `BankPeriod` para cada banco detectado
4. Agrega resultados via `IEDIAggregationService`
5. Salva `IEDIResult` para cada banco
6. Retorna ranking ordenado por IEDI final

**Dependências**:
- `BrandwatchService`: Extração de mentions
- `MentionService`: Processamento de mentions
- `BankDetectionService`: Detecção de bancos
- `IEDICalculationService`: Cálculo de IEDI
- `IEDIAggregationService`: Agregação de resultados

### BankDetectionService

**Arquivo**: `app/services/bank_detection_service.py`

**Responsabilidade**: Detectar quais bancos são mencionados em uma mention

**Métodos**:
- `detect_banks(mention_data)`: Detecta bancos (prioriza categoryDetails, fallback para texto)
- `_detect_from_categories(mention_data)`: Detecta via categoryDetails (grupo "Bancos")
- `_detect_from_text(mention_data)`: Detecta via título + snippet (regex)

**Lógica**:
```python
1. Tentar detectar via categoryDetails:
   - Buscar categorias com group="Bancos"
   - Comparar nome da categoria com bank.name e bank.variations
   - Retornar bancos encontrados

2. Se não encontrou via categoryDetails:
   - Buscar no título + snippet usando regex
   - Retornar bancos encontrados

3. Se não encontrou nenhum banco:
   - Retornar lista vazia
```

**Constante Importante**:
```python
BANK_GROUP_NAME = "Bancos"
```

### IEDICalculationService

**Arquivo**: `app/services/iedi_calculation_service.py`

**Responsabilidade**: Calcular IEDI de uma mention para um banco específico

**Pesos**:
```python
WEIGHTS = {
    'title': 100,
    'subtitle': 80,
    'relevant_outlet': 95,
    'niche_outlet': 54,
    'reach_group': {
        ReachGroup.A: 91,
        ReachGroup.B: 85,
        ReachGroup.C: 24,
        ReachGroup.D: 20
    }
}
```

**Método Principal**: `calculate_iedi(mention_data, bank)`

**Retorno**:
```python
{
    'iedi_score': float,        # -1 a 1
    'iedi_normalized': float,   # 0 a 10
    'numerator': int,
    'denominator': int,
    'title_verified': int,      # 0 ou 1
    'subtitle_verified': int,   # 0 ou 1
    'relevant_outlet_verified': int,
    'niche_outlet_verified': int
}
```

**Lógica de Cálculo**:
1. Verificar título (banco mencionado?)
2. Verificar subtítulo (apenas se `snippet != fullText`)
3. Classificar grupo de alcance (baseado em `monthlyVisitors`)
4. Verificar veículo relevante (baseado em `isNiche`)
5. Verificar veículo de nicho (baseado em `isNiche`)
6. Calcular numerador (soma dos pesos verificados)
7. Calcular denominador (varia por grupo e presença de subtítulo)
8. Aplicar sinal (positivo=+1, negativo=-1, neutro=0)
9. Normalizar para escala 0-10

**Regra Especial - Denominador**:
- **Grupo A**: NÃO inclui peso de nicho (54)
- **Grupos B, C, D**: Inclui peso de nicho (54)

### AnalysisService

**Arquivo**: `app/services/analysis_service.py`

**Responsabilidade**: Gerenciar criação e consulta de análises

**Métodos**:
- `create_analysis(name, query, custom_period, bank_periods)`: Cria análise + períodos
- `get_all_analyses()`: Lista todas análises
- `get_analysis_results(analysis_id)`: Retorna análise + resultados IEDI
- `process_mentions(analysis_id, mentions_by_bank)`: Processa mentions e calcula IEDI

**Fluxo de Criação**:
```python
1. Criar Analysis (name, query, custom_period)
2. Para cada bank_period em bank_periods:
   - Criar BankPeriod (analysis_id, bank_id, category_detail, start_date, end_date)
3. Retornar analysis.to_dict()
```

---

## Repositories

### AnalysisRepository

**Arquivo**: `app/repositories/analysis_repository.py`

**Métodos**:
- `create(name, query, custom_period)`: Cria análise
- `find_by_id(analysis_id)`: Busca por ID
- `find_all()`: Lista todas (ordenadas por created_at desc)

**Mudanças**:
- ❌ **Removido**: `period_type`, `start_date`, `end_date` do `create()`
- ✅ **Adicionado**: `name`, `query`, `custom_period`

### BankPeriodRepository (NOVO)

**Arquivo**: `app/repositories/bank_period_repository.py`

**Métodos**:
- `create(analysis_id, bank_id, category_detail, start_date, end_date)`: Cria período
- `find_by_analysis(analysis_id)`: Lista períodos de uma análise
- `find_by_analysis_and_bank(analysis_id, bank_id)`: Busca período específico

### IEDIResultRepository

**Arquivo**: `app/repositories/iedi_result_repository.py`

**Métodos** (esperados):
- `create(analysis_id, bank_id, total_volume, positive_volume, ...)`: Cria resultado
- `find_by_analysis(analysis_id)`: Lista resultados de uma análise
- `find_by_analysis_and_bank(analysis_id, bank_id)`: Busca resultado específico

---

## Controllers

### AnalysisController

**Arquivo**: `app/controllers/analysis_controller.py`

**Rotas Atuais**:

#### `GET /`
- Renderiza `analyses.html`

#### `GET /api`
- Lista todas análises
- **Problema**: Usa `period_type` que não existe mais no model

#### `GET /api/<analysis_id>`
- Retorna análise + resultados IEDI
- **Problema**: Usa `period_type` que não existe mais no model

#### `GET /api/<analysis_id>/mentions`
- Lista mentions de uma análise (opcionalmente filtrado por bank_id)
- Retorna `AnalysisMention` (relação mention × banco × iedi)

**Problemas Identificados**:
```python
# Linha 17-18, 34-35
'period_type': a.period_type,  # ❌ Campo não existe mais!
```

---

## Problemas e Inconsistências Identificadas

### 1. AnalysisController usa `period_type` inexistente

**Arquivo**: `app/controllers/analysis_controller.py`

**Linhas**: 17-18, 34-35

**Problema**: Model `Analysis` não tem mais campo `period_type`

**Solução**: Substituir por campos corretos (`name`, `query_name`, `custom_period`)

### 2. AnalysisRepository.create() incompatível

**Arquivo**: `app/repositories/analysis_repository.py`

**Problema**: Método `create()` espera `(name, query, custom_period)`, mas controller ainda não foi atualizado

**Solução**: Criar endpoint POST para criação de análises

### 3. Falta endpoint POST para criação de análises

**Problema**: Controller só tem GET, não tem POST

**Solução**: Adicionar rota POST `/api` para criar análises

### 4. BrandwatchService não filtra por categoryDetails

**Problema**: Extração de mentions não filtra por categoria do banco

**Solução**: Adicionar filtro `category` no `extract_mentions()`

### 5. Teste usa AnalysisRepository.create() com assinatura antiga

**Arquivo**: `tests/test_outubro_bb.py`

**Linhas**: 146-152

**Problema**: Usa `create(id, period_type, start_date, end_date, query_name)` mas assinatura mudou

**Solução**: Atualizar para nova assinatura e criar BankPeriod separadamente

---

## Fluxo Completo Refatorado

### Fase 1: Criação de Análise

```python
# 1. Usuário preenche formulário
{
    "name": "Análise Outubro 2024",
    "query_name": "OPERAÇÃO BB :: MONITORAMENTO",
    "custom_period": false,
    "bank_periods": [
        {
            "bank_id": "uuid-bb",
            "category_detail": "Banco do Brasil",
            "start_date": "2024-10-01T00:00:00",
            "end_date": "2024-10-31T23:59:59"
        }
    ]
}

# 2. Backend cria Analysis
analysis = AnalysisRepository.create(
    name="Análise Outubro 2024",
    query="OPERAÇÃO BB :: MONITORAMENTO",
    custom_period=False
)

# 3. Backend cria BankPeriods
for bp in bank_periods:
    BankPeriodRepository.create(
        analysis_id=analysis.id,
        bank_id=bp["bank_id"],
        category_detail=bp["category_detail"],
        start_date=bp["start_date"],
        end_date=bp["end_date"]
    )
```

### Fase 2: Processamento

```python
# 1. Buscar períodos da análise
bank_periods = BankPeriodRepository.find_by_analysis(analysis_id)

# 2. Para cada banco:
for bp in bank_periods:
    # Extrair mentions da Brandwatch
    mentions = BrandwatchService.extract_mentions(
        query_name=analysis.query_name,
        start_date=bp.start_date,
        end_date=bp.end_date,
        # Filtrar por categoria do banco
        category=bp.category_detail
    )
    
    # Processar cada mention
    for mention_data in mentions:
        # Salvar mention
        mention = MentionService.process_mention(mention_data)
        
        # Detectar bancos (deve retornar apenas o banco do período)
        banks = BankDetectionService.detect_banks(mention_data)
        
        # Calcular IEDI
        for bank in banks:
            iedi = IEDICalculationService.calculate_iedi(mention_data, bank)
            
            # Salvar relação mention × banco × iedi
            AnalysisMentionRepository.create(
                analysis_id=analysis_id,
                mention_id=mention.id,
                bank_id=bank.id,
                **iedi
            )
    
    # Atualizar total_mentions do BankPeriod
    bp.total_mentions = len(mentions)

# 3. Agregar resultados
for bp in bank_periods:
    aggregated = IEDIAggregationService.aggregate_by_bank(
        analysis_id=analysis_id,
        bank_id=bp.bank_id
    )
    
    # Salvar resultado IEDI
    IEDIResultRepository.create(
        analysis_id=analysis_id,
        bank_id=bp.bank_id,
        **aggregated
    )
```

### Fase 3: Visualização

```python
# 1. Listar análises
GET /api/analysis

# 2. Ver detalhes de uma análise
GET /api/analysis/<analysis_id>
# Retorna:
{
    "analysis": {...},
    "bank_periods": [...],
    "results": [...]
}

# 3. Ver mentions de um banco
GET /api/analysis/<analysis_id>/mentions?bank_id=<bank_id>
```

---

## Estrutura de Dados Completa

### Tabelas e Relacionamentos

```
analysis (1) ──┬── (N) bank_period
               │
               └── (N) iedi_result

bank_period (N) ── (1) bank

mention (1) ── (N) analysis_mention ── (1) bank
                                    └── (1) analysis

iedi_result (N) ── (1) bank
                └── (1) analysis
```

### Exemplo de Dados

#### Analysis
```json
{
    "id": "uuid-1",
    "name": "Análise Outubro 2024",
    "query_name": "OPERAÇÃO BB :: MONITORAMENTO",
    "start_date": "2024-10-01T00:00:00-03:00",
    "end_date": "2024-10-31T23:59:59-03:00",
    "custom_period": false,
    "status": "completed",
    "created_at": "2024-11-01T10:00:00-03:00",
    "updated_at": "2024-11-01T15:30:00-03:00"
}
```

#### BankPeriod
```json
{
    "id": "uuid-2",
    "analysis_id": "uuid-1",
    "bank_id": "uuid-bb",
    "category_detail": "Banco do Brasil",
    "start_date": "2024-10-01T00:00:00-03:00",
    "end_date": "2024-10-31T23:59:59-03:00",
    "total_mentions": 1234,
    "created_at": "2024-11-01T10:00:00-03:00"
}
```

#### IEDIResult
```json
{
    "id": "uuid-3",
    "analysis_id": "uuid-1",
    "bank_id": "uuid-bb",
    "total_volume": 1234,
    "positive_volume": 800,
    "negative_volume": 200,
    "neutral_volume": 234,
    "average_iedi": 7.5,
    "final_iedi": 6.8,
    "positivity_rate": 64.8,
    "negativity_rate": 16.2,
    "created_at": "2024-11-01T15:30:00-03:00"
}
```

---

## Conclusão

O sistema foi refatorado com sucesso para separar **Análises** (períodos de coleta) de **Períodos por Banco** (períodos específicos de cada banco). As principais mudanças são:

✅ **Novo model**: `BankPeriod` para períodos customizados por banco
✅ **Model atualizado**: `Analysis` com `name`, `query_name`, `custom_period`, `status`
✅ **Model atualizado**: `IEDIResult` com volumes separados e métricas de positividade
✅ **Service novo**: `IEDIOrchestrator` para orquestrar todo o fluxo
✅ **Service atualizado**: `BankDetectionService` com detecção via categoryDetails
✅ **Service atualizado**: `IEDICalculationService` com cálculo correto de IEDI

❌ **Problemas identificados**:
- Controller usa `period_type` inexistente
- Falta endpoint POST para criar análises
- Teste usa assinatura antiga de `create()`
- BrandwatchService não filtra por categoria

**Próximos passos**:
1. Atualizar SQLs para novos models
2. Criar endpoint POST para análises
3. Propor telas HTML/CSS/JS
4. Refatorar teste de outubro
