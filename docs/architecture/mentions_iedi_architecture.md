# Arquitetura: Mentions + IEDI

## Visão Geral

Este documento descreve a arquitetura de armazenamento e processamento de menções no sistema IEDI, com foco na separação entre **dados brutos** (mentions) e **cálculos IEDI específicos por banco** (analysis_mentions).

A arquitetura suporta menções que citam **múltiplos bancos**, permitindo que cada banco tenha seu próprio cálculo IEDI independente.

---

## Cenário: Múltiplos Bancos por Menção

Uma menção pode citar múltiplos bancos simultaneamente:

> **Título**: "Banco do Brasil e Itaú lideram ranking de crédito no Brasil"  
> **Veículo**: Valor Econômico  
> **Data**: 15/11/2024

Cada banco mencionado deve ter seu próprio **cálculo IEDI**:

1. **Verificação de Título**: O banco está mencionado no título? (BB: sim, Itaú: sim)
2. **Verificação de Subtítulo**: O banco está no subtítulo? (BB: sim, Itaú: não)
3. **Numerador**: Quantidade de verificações positivas (BB: 2, Itaú: 1)
4. **Score IEDI**: Cálculo final (BB: 85.5, Itaú: 82.3)

---

## Arquitetura de Dados

### Diagrama Entidade-Relacionamento

```
┌─────────────┐         ┌──────────────────────┐         ┌────────────┐
│  mentions   │         │ analysis_mentions    │         │   banks    │
├─────────────┤         ├──────────────────────┤         ├────────────┤
│ id (PK)     │────┐    │ analysis_id (PK,FK)  │         │ id (PK)    │
│ url (UNIQUE)│    │    │ mention_id (PK,FK)   │────┐    │ name       │
│ title       │    └───→│ bank_id (PK,FK)      │────┘    │ variations │
│ snippet     │         │                      │         │ active     │
│ domain      │         │ iedi_score           │         └────────────┘
│ sentiment   │         │ iedi_normalized      │
│ ...         │         │ numerator            │
└─────────────┘         │ denominator          │
                        │ title_verified       │
                        │ subtitle_verified    │
                        │ ...                  │
                        └──────────────────────┘
```

### Tabela: `mentions`

Armazena **dados brutos** da Brandwatch, sem cálculos IEDI.

```sql
CREATE TABLE iedi.mentions (
  id STRING(36) NOT NULL,
  url STRING(500) NOT NULL,
  brandwatch_id STRING(255),
  original_url STRING(500),
  
  title TEXT,
  snippet TEXT,
  full_text TEXT,
  domain STRING(255),
  published_date TIMESTAMP,
  
  categories ARRAY<STRING>,
  sentiment STRING(50) NOT NULL,
  
  media_outlet_id STRING(36),
  monthly_visitors INT64 DEFAULT 0,
  reach_group STRING(10) NOT NULL,
  
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP,
  
  PRIMARY KEY (id) NOT ENFORCED
);

CREATE UNIQUE INDEX idx_mentions_url ON iedi.mentions(url);
```

**Características**:
- **Identificador único**: `url` (não `brandwatch_id`)
- **Sem cálculos IEDI**: Apenas dados brutos
- **Reutilizável**: Mesma menção pode aparecer em múltiplas análises

### Tabela: `analysis_mentions`

Relacionamento N:N entre análises, menções e bancos, com **cálculos IEDI específicos**.

```sql
CREATE TABLE iedi.analysis_mentions (
  analysis_id STRING(36) NOT NULL,
  mention_id STRING(36) NOT NULL,
  bank_id STRING(36) NOT NULL,
  
  iedi_score FLOAT64,
  iedi_normalized FLOAT64,
  numerator INT64,
  denominator INT64,
  
  title_verified INT64 DEFAULT 0,
  subtitle_verified INT64 DEFAULT 0,
  relevant_outlet_verified INT64 DEFAULT 0,
  niche_outlet_verified INT64 DEFAULT 0,
  
  created_at TIMESTAMP NOT NULL,
  
  PRIMARY KEY (analysis_id, mention_id, bank_id) NOT ENFORCED
);
```

**Características**:
- **Chave primária composta**: (analysis_id, mention_id, bank_id)
- **Cálculos IEDI**: Específicos para cada combinação
- **Múltiplos bancos**: Mesma menção pode ter N registros (um por banco)

---

## Exemplo Prático

### Menção com 2 Bancos

**Dados da Brandwatch**:

```json
{
  "url": "https://valor.globo.com/financas/noticia/2024/11/15/bb-e-itau-lideram-ranking.html",
  "title": "Banco do Brasil e Itaú lideram ranking de crédito",
  "snippet": "Banco do Brasil registrou crescimento de 15% no trimestre...",
  "domain": "valor.globo.com",
  "sentiment": "positive",
  "categoryDetails": [
    {"name": "Banco do Brasil", "group": "Bancos"},
    {"name": "Itaú", "group": "Bancos"}
  ]
}
```

### Armazenamento

**1. Tabela `mentions`** (1 registro):

| id | url | title | sentiment |
|----|-----|-------|-----------|
| uuid-001 | https://valor... | BB e Itaú lideram... | positive |

**2. Tabela `analysis_mentions`** (2 registros):

| analysis_id | mention_id | bank_id | iedi_score | numerator | title_verified | subtitle_verified |
|-------------|------------|---------|------------|-----------|----------------|-------------------|
| analysis-nov | uuid-001 | bb-id | 0.8550 | 366 | 1 | 1 |
| analysis-nov | uuid-001 | itau-id | 0.8230 | 286 | 1 | 0 |

**Explicação**:
- **BB**: Mencionado no título E subtítulo → numerator = 366
- **Itaú**: Mencionado apenas no título → numerator = 286

---

## Fluxo de Processamento

### 1. Coleta (Brandwatch)

```python
mentions_data = brandwatch_service.extract_mentions(
    start_date=datetime(2024, 11, 1),
    end_date=datetime(2024, 11, 30),
    query_name="OPERAÇÃO BB :: MONITORAMENTO"
)
```

### 2. Processar Menção

```python
mention = mention_service.process_mention(mention_data)
```

**Ações**:
- Extrai URL única
- Verifica se menção já existe
- Enriquece com metadados (veículo, alcance)
- Armazena em `mentions`

### 3. Detectar Bancos

```python
detected_banks = bank_detection_service.detect_banks(mention_data)
```

**Lógica**:
- Verifica `categoryDetails` com `group == "Bancos"`
- Fallback: busca no texto (título + snippet)

### 4. Calcular IEDI (para cada banco)

```python
for bank in detected_banks:
    iedi_result = iedi_calculation_service.calculate_iedi(
        mention_data=mention_data,
        bank=bank
    )
```

**Retorna**:
```python
{
    'iedi_score': 0.8550,
    'iedi_normalized': 9.28,
    'numerator': 366,
    'denominator': 428,
    'title_verified': 1,
    'subtitle_verified': 1,
    'relevant_outlet_verified': 1,
    'niche_outlet_verified': 0
}
```

### 5. Armazenar Relacionamento

```python
analysis_mention_repo.create(
    analysis_id=analysis_id,
    mention_id=mention.id,
    bank_id=bank.id,
    **iedi_result
)
```

---

## Queries SQL de Exemplo

### Buscar menções de uma análise

```sql
SELECT 
    m.title,
    m.url,
    b.name AS bank_name,
    am.iedi_normalized,
    am.numerator,
    am.denominator
FROM iedi.analysis_mentions am
JOIN iedi.mentions m ON am.mention_id = m.id
JOIN iedi.banks b ON am.bank_id = b.id
WHERE am.analysis_id = 'analysis-nov-2024'
ORDER BY am.iedi_normalized DESC;
```

### Ranking IEDI por banco

```sql
SELECT 
    b.name AS bank_name,
    COUNT(*) AS total_mentions,
    AVG(am.iedi_normalized) AS avg_iedi
FROM iedi.analysis_mentions am
JOIN iedi.banks b ON am.bank_id = b.id
WHERE am.analysis_id = 'analysis-nov-2024'
GROUP BY b.name
ORDER BY avg_iedi DESC;
```

### Menções com múltiplos bancos

```sql
SELECT 
    m.url,
    m.title,
    COUNT(DISTINCT am.bank_id) AS num_banks
FROM iedi.mentions m
JOIN iedi.analysis_mentions am ON m.id = am.mention_id
WHERE am.analysis_id = 'analysis-nov-2024'
GROUP BY m.url, m.title
HAVING COUNT(DISTINCT am.bank_id) > 1;
```

---

## Vantagens da Arquitetura

### 1. Suporte a Múltiplos Bancos
Cada banco tem cálculo IEDI independente na mesma menção.

### 2. Reutilização de Dados
Menções podem ser reutilizadas em múltiplas análises (mensal, trimestral).

### 3. Rastreabilidade
URL permite rastrear menção de volta à publicação original.

### 4. Separação de Responsabilidades
- `mentions`: Dados brutos (imutáveis)
- `analysis_mentions`: Cálculos IEDI (específicos por análise)

### 5. Escalabilidade
Suporta análises históricas sem reprocessar menções.

---

## Desenvolvido por Manus AI
