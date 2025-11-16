# BigQuery Database Setup

This guide covers BigQuery configuration, connection management, and best practices for Python applications using SQLAlchemy.

## Overview

Google BigQuery is a serverless, highly scalable cloud data warehouse designed for analytics:

- **Serverless**: No infrastructure management required
- **Columnar storage**: Optimized for analytical queries
- **Petabyte scale**: Handles massive datasets efficiently
- **Pay-per-query**: Charged based on data processed
- **SQL interface**: Standard SQL with extensions

## When to Use BigQuery

**Ideal for:**
- Analytics and reporting dashboards
- Data warehousing and historical data storage
- Large-scale data processing (TB to PB)
- Read-heavy workloads with complex aggregations
- Machine learning and data science workflows

**Not ideal for:**
- High-frequency transactional workloads (OLTP)
- Low-latency queries requiring sub-second responses
- Applications requiring foreign key constraints
- Real-time CRUD operations

## BigQuery Limitations

### No AUTO_INCREMENT Support

BigQuery does not support `AUTO_INCREMENT` or `SERIAL` columns. Use **UUID (STRING)** for primary keys instead:

```sql
CREATE TABLE iedi.banks (
  id STRING(36) NOT NULL,  -- UUID format
  name STRING(255) NOT NULL,
  PRIMARY KEY (id) NOT ENFORCED
);
```

**Python UUID Generation**:

```python
import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

# Usage
bank_id = generate_uuid()  # "550e8400-e29b-41d4-a716-446655440000"
```

### Primary Keys Not Enforced

BigQuery primary keys are **metadata only** - they are not enforced at write time. Application logic must ensure uniqueness.

## Installation

### 1. Install Dependencies

```bash
pip install sqlalchemy-bigquery
pip install google-cloud-bigquery
pip install db-dtypes
```

### 2. Authentication Setup

BigQuery uses Google Cloud authentication. You need a service account key:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

**Service Account Permissions Required:**
- `BigQuery Data Editor` - Read/write data
- `BigQuery Job User` - Execute queries

## Connection String

```python
DATABASE_URL = "bigquery://project-id/dataset-name"
```

## SQLAlchemy Configuration

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "bigquery://my-project/iedi",
    credentials_path="/path/to/service-account.json"
)

Session = sessionmaker(bind=engine)
session = Session()
```

## Schema Design Best Practices

### Use STRING for IDs

```python
from sqlalchemy import Column, String

class Bank(Base):
    __tablename__ = "banks"
    __table_args__ = {"schema": "iedi"}
    
    id = Column(String(36), primary_key=True)  # UUID
    name = Column(String(255), nullable=False)
```

### Use TIMESTAMP for Dates

```python
from sqlalchemy_bigquery import TIMESTAMP

class Mention(Base):
    created_at = Column(TIMESTAMP, nullable=False)
```

### Use ARRAY for Lists

```python
from sqlalchemy_bigquery import ARRAY

class Bank(Base):
    variations = Column(ARRAY(String))
```

## Common Patterns

### Insert with UUID

```python
from app.utils.uuid_generator import generate_uuid

bank = Bank(
    id=generate_uuid(),
    name="Banco do Brasil"
)
session.add(bank)
session.commit()
```

### Query by UUID

```python
bank = session.query(Bank).filter(Bank.id == "550e8400-...").first()
```

## Performance Tips

1. **Partition tables** by date for time-series data
2. **Cluster tables** by frequently filtered columns
3. **Avoid SELECT \*** - specify columns explicitly
4. **Use LIMIT** for exploratory queries
5. **Cache results** for repeated queries

## Troubleshooting

### "Column not found" errors
Ensure schema name is specified in `__table_args__`

### "Permission denied" errors
Verify service account has required BigQuery roles

### Slow queries
Check query execution plan and add clustering/partitioning
