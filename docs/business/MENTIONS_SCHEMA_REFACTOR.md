# Refatoração do Schema de Menções

## Motivação

No schema original, menções tinham um campo `analysis_id` que criava um relacionamento **1:N** (uma análise → muitas menções). Isso causava problemas:

❌ **Duplicação de Dados**: Mesma menção armazenada múltiplas vezes  
❌ **Desperdício de Armazenamento**: Dados redundantes no BigQuery  
❌ **Inconsistências**: Atualizar uma menção exigia atualizar em todas as análises  
❌ **Inflexibilidade**: Difícil reutilizar menções em novas análises  

---

## Solução: Relacionamento N:N

### Novo Schema

```
┌──────────────┐       ┌─────────────────────┐       ┌──────────────┐
│   analyses   │       │ analysis_mentions   │       │   mentions   │
├──────────────┤       ├─────────────────────┤       ├──────────────┤
│ id (PK)      │───┐   │ analysis_id (PK,FK) │   ┌───│ id (PK)      │
│ name         │   └──→│ mention_id (PK,FK)  │←──┘   │ brandwatch_id│
│ start_date   │       │ bank_id (PK,FK)     │       │ title        │
│ end_date     │       │ created_at          │       │ domain       │
└──────────────┘       └─────────────────────┘       │ published_date│
                                                      │ sentiment    │
                                                      └──────────────┘
```

### Tabelas

#### 1. `mentions` (Dados Brutos)
Armazena menções **únicas** sem vínculo com análises.

```sql
CREATE TABLE iedi.mentions (
  id INT64 NOT NULL,
  brandwatch_id STRING NOT NULL,  -- ID único da Brandwatch
  categories ARRAY<STRING>,
  title STRING,
  snippet STRING,
  full_text STRING,
  url STRING,
  domain STRING,
  published_date TIMESTAMP,
  sentiment STRING NOT NULL,
  -- Campos de cálculo IEDI
  title_verified BOOL DEFAULT FALSE,
  subtitle_verified BOOL DEFAULT FALSE,
  relevant_outlet_verified BOOL DEFAULT FALSE,
  niche_outlet_verified BOOL DEFAULT FALSE,
  numerator FLOAT64 DEFAULT 0.0,
  denominator FLOAT64 DEFAULT 0.0,
  score FLOAT64 DEFAULT 0.0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
```

**Características:**
- ✅ Uma menção aparece **apenas uma vez**
- ✅ Identificada por `brandwatch_id` (único)
- ✅ Sem referência a `analysis_id`

#### 2. `analysis_mentions` (Relacionamento)
Tabela de junção que conecta análises, menções e bancos.

```sql
CREATE TABLE iedi.analysis_mentions (
  analysis_id INT64 NOT NULL,
  mention_id INT64 NOT NULL,
  bank_id INT64 NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  PRIMARY KEY (analysis_id, mention_id, bank_id)
);
```

**Características:**
- ✅ Relacionamento **N:N** entre análises e menções
- ✅ Inclui `bank_id` para identificar qual banco foi detectado
- ✅ Chave primária composta (permite múltiplos bancos por menção)

---

## Exemplo Prático

### Cenário: Menção do Banco do Brasil

**Dados da Menção:**
```
Título: "Banco do Brasil anuncia lucro recorde no 3º trimestre"
Domain: valor.globo.com
Published: 2024-11-15 10:30:00
Brandwatch ID: bw_987654321
```

### Análises que Usam Esta Menção

| Análise | Período | Usa Menção? |
|---------|---------|-------------|
| Novembro 2024 | 01/11 - 30/11 | ✅ Sim |
| Q4 2024 | 01/10 - 31/12 | ✅ Sim |
| Ano 2024 | 01/01 - 31/12 | ✅ Sim |

### Dados Armazenados

#### Tabela `mentions` (1 registro)
```sql
INSERT INTO iedi.mentions VALUES (
  12345,                    -- id
  'bw_987654321',          -- brandwatch_id
  ['Banco do Brasil'],     -- categories
  'Banco do Brasil anuncia lucro recorde...',  -- title
  'valor.globo.com',       -- domain
  '2024-11-15 10:30:00',   -- published_date
  'positive',              -- sentiment
  ...
);
```

#### Tabela `analysis_mentions` (3 registros)
```sql
INSERT INTO iedi.analysis_mentions VALUES
  (101, 12345, 1, CURRENT_TIMESTAMP()),  -- Análise Novembro → Menção 12345 → BB (id=1)
  (102, 12345, 1, CURRENT_TIMESTAMP()),  -- Análise Q4 → Menção 12345 → BB
  (103, 12345, 1, CURRENT_TIMESTAMP());  -- Análise Ano → Menção 12345 → BB
```

---

## Benefícios

### 1. **Reutilização de Dados**
```python
# Criar nova análise usando menções existentes
existing_mentions = session.query(Mention).filter(
    Mention.published_date.between(start_date, end_date)
).all()

for mention in existing_mentions:
    analysis_mention = AnalysisMention(
        analysis_id=new_analysis_id,
        mention_id=mention.id,
        bank_id=detect_bank(mention)
    )
    session.add(analysis_mention)
```

### 2. **Economia de Armazenamento**

| Métrica | Schema Antigo | Schema Novo | Economia |
|---------|---------------|-------------|----------|
| Menções/mês | 15.000 | 15.000 | - |
| Análises/mês | 3 (Nov, Q4, Ano) | 3 | - |
| Registros `mentions` | 45.000 | **15.000** | **67%** |
| Registros `analysis_mentions` | - | 45.000 | - |
| **Total** | **45.000** | **60.000** | Mais eficiente* |

*Apesar de mais registros totais, `analysis_mentions` tem apenas 4 campos (vs 20+ em `mentions`)

### 3. **Consistência**
```python
# Atualizar sentimento de uma menção
mention = session.query(Mention).filter_by(brandwatch_id='bw_987654321').first()
mention.sentiment = 'neutral'
session.commit()

# Todas as análises que usam esta menção verão a atualização automaticamente
```

### 4. **Queries Flexíveis**

```sql
-- Buscar todas as menções de uma análise
SELECT m.*
FROM iedi.mentions m
JOIN iedi.analysis_mentions am ON m.id = am.mention_id
WHERE am.analysis_id = 101;

-- Buscar todas as análises que usam uma menção
SELECT a.*
FROM iedi.analyses a
JOIN iedi.analysis_mentions am ON a.id = am.analysis_id
WHERE am.mention_id = 12345;

-- Buscar menções do Banco do Brasil em múltiplas análises
SELECT a.name, COUNT(DISTINCT m.id) as mention_count
FROM iedi.analyses a
JOIN iedi.analysis_mentions am ON a.id = am.analysis_id
JOIN iedi.mentions m ON m.id = am.mention_id
WHERE am.bank_id = 1
GROUP BY a.name;
```

---

## Migração

### Script SQL
Executar `sql/12_migrate_mentions_schema.sql` para:

1. ✅ Criar tabela `analysis_mentions`
2. ✅ Migrar dados de `mentions.analysis_id` para `analysis_mentions`
3. ✅ Criar backup `mentions_backup`
4. ✅ Criar nova tabela `mentions_new` sem `analysis_id`
5. ✅ Remover duplicatas por `brandwatch_id`
6. ⚠️ **Manual**: Validar dados e substituir tabela antiga

### Validação

```sql
-- Verificar contagem de registros
SELECT 
  (SELECT COUNT(*) FROM iedi.mentions_backup) as old_count,
  (SELECT COUNT(DISTINCT brandwatch_id) FROM iedi.mentions_new) as new_unique_count,
  (SELECT COUNT(*) FROM iedi.analysis_mentions) as relationships_count;

-- Verificar integridade referencial
SELECT am.analysis_id, am.mention_id, am.bank_id
FROM iedi.analysis_mentions am
LEFT JOIN iedi.mentions_new m ON m.id = am.mention_id
WHERE m.id IS NULL;  -- Deve retornar 0 registros
```

---

## Models Python

### Mention (Atualizado)
```python
class Mention(Base):
    __tablename__ = "mentions"
    __table_args__ = {"schema": "iedi"}

    id = Column(Integer, primary_key=True)
    brandwatch_id = Column(String(255), unique=True, nullable=False)
    # SEM analysis_id
    ...
```

### AnalysisMention (Novo)
```python
class AnalysisMention(Base):
    __tablename__ = "analysis_mentions"
    __table_args__ = {"schema": "iedi"}

    analysis_id = Column(Integer, primary_key=True)
    mention_id = Column(Integer, primary_key=True)
    bank_id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
```

---

## Impacto no Código

### Antes
```python
# Criar menção vinculada a uma análise
mention = Mention(
    analysis_id=101,  # Vinculado diretamente
    brandwatch_id='bw_123',
    title='...',
    ...
)
session.add(mention)
```

### Depois
```python
# 1. Criar/buscar menção (independente)
mention = session.query(Mention).filter_by(brandwatch_id='bw_123').first()
if not mention:
    mention = Mention(
        brandwatch_id='bw_123',
        title='...',
        ...
    )
    session.add(mention)
    session.flush()  # Obter mention.id

# 2. Criar relacionamento
analysis_mention = AnalysisMention(
    analysis_id=101,
    mention_id=mention.id,
    bank_id=1
)
session.add(analysis_mention)
```

---

## Referências

- `sql/06_create_table_mentions.sql` - Novo schema de mentions
- `sql/07_create_table_analysis_mentions.sql` - Tabela de relacionamento
- `sql/12_migrate_mentions_schema.sql` - Script de migração
- `app/models/mention.py` - Model Mention atualizado
- `app/models/analysis_mention.py` - Novo model AnalysisMention
