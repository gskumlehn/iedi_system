# SQL Scripts - IEDI BigQuery Schema

Scripts SQL para criação do schema e tabelas do sistema IEDI no Google BigQuery.

## Ordem de Execução

Execute os scripts na ordem numérica:

1. `01_create_schema.sql` - Cria o schema `iedi`
2. `02_create_table_banks.sql` - Cria tabela de bancos
3. `03_create_table_relevant_media_outlets.sql` - Cria tabela de veículos relevantes
4. `04_create_table_niche_media_outlets.sql` - Cria tabela de veículos de nicho
5. `05_create_table_analyses.sql` - Cria tabela de análises
6. `06_create_table_bank_periods.sql` - Cria tabela de períodos por banco
7. `07_create_table_mentions.sql` - Cria tabela de menções
8. `08_create_table_iedi_results.sql` - Cria tabela de resultados IEDI

## Como Executar

### Opção 1: BigQuery Console

1. Acesse o [BigQuery Console](https://console.cloud.google.com/bigquery)
2. Selecione seu projeto
3. Clique em "Compose new query"
4. Cole o conteúdo de cada arquivo SQL
5. Execute na ordem

### Opção 2: bq CLI

```bash
# Configurar projeto
export PROJECT_ID=your-gcp-project-id

# Executar scripts
bq query --project_id=$PROJECT_ID < 01_create_schema.sql
bq query --project_id=$PROJECT_ID < 02_create_table_banks.sql
bq query --project_id=$PROJECT_ID < 03_create_table_relevant_media_outlets.sql
bq query --project_id=$PROJECT_ID < 04_create_table_niche_media_outlets.sql
bq query --project_id=$PROJECT_ID < 05_create_table_analyses.sql
bq query --project_id=$PROJECT_ID < 06_create_table_bank_periods.sql
bq query --project_id=$PROJECT_ID < 07_create_table_mentions.sql
bq query --project_id=$PROJECT_ID < 08_create_table_iedi_results.sql
```

### Opção 3: Python (SQLAlchemy)

```python
from app.models import Base
from app.infra.bq_sa import engine

# Cria todas as tabelas automaticamente
Base.metadata.create_all(engine)
```

## Estrutura do Schema

```
iedi/
├── banks                        (Bancos)
├── relevant_media_outlets       (Veículos relevantes)
├── niche_media_outlets          (Veículos de nicho)
├── analyses                     (Análises)
├── bank_periods                 (Períodos por banco)
├── mentions                     (Menções da Brandwatch)
└── iedi_results                 (Resultados IEDI agregados)
```

## Relacionamentos

```
analyses (1) ──→ (N) bank_periods
analyses (1) ──→ (N) mentions
analyses (1) ──→ (N) iedi_results

bank_periods (N) ──→ (1) banks
iedi_results (N) ──→ (1) banks

mentions (N) ──→ (N) banks (via categories array)
```

## Tipos de Dados BigQuery

| Tipo Python | Tipo BigQuery | Exemplo |
|-------------|---------------|---------|
| `int` | `INT64` | 123 |
| `str` | `STRING` | "texto" |
| `float` | `FLOAT64` | 3.14 |
| `bool` | `BOOL` | TRUE/FALSE |
| `datetime` | `TIMESTAMP` | 2025-01-01 00:00:00 UTC |
| `list[str]` | `ARRAY<STRING>` | ["item1", "item2"] |

## Observações

- Todas as tabelas usam `INT64` para IDs (auto-increment gerenciado pela aplicação)
- Timestamps são armazenados em UTC
- Arrays são nativos do BigQuery (`ARRAY<STRING>`)
- Schema `iedi` está configurado para região `us`

## Limpeza

Para remover todas as tabelas e o schema:

```sql
DROP SCHEMA iedi CASCADE;
```

⚠️ **ATENÇÃO**: Este comando remove TODOS os dados permanentemente!
