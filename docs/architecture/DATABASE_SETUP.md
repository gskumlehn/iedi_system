# Database Setup - BigQuery

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

## Installation

### 1. Install Dependencies

```bash
pip install sqlalchemy-bigquery
pip install google-cloud-bigquery
pip install db-dtypes  # For BigQuery data types
```

### 2. Authentication Setup

BigQuery uses Google Cloud authentication. You need a service account key:

```bash
# Set environment variable pointing to service account JSON
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

**Service Account Permissions Required:**
- `BigQuery Data Editor` - Read/write data
- `BigQuery Job User` - Execute queries
- `BigQuery User` - Access datasets

## Connection Setup

### Basic Connection

```python
# app/infra/bigquery_sa.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

def get_bigquery_engine():
    """Create BigQuery SQLAlchemy engine"""
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("BQ_DATASET_ID")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not all([project_id, dataset_id, credentials_path]):
        raise ValueError("Missing required BigQuery environment variables")
    
    connection_string = f"bigquery://{project_id}/{dataset_id}"
    
    engine = create_engine(
        connection_string,
        credentials_path=credentials_path,
        echo=False  # Set to True for SQL logging
    )
    
    return engine

def get_session_maker():
    """Get sessionmaker instance"""
    engine = get_bigquery_engine()
    return sessionmaker(bind=engine)

@contextmanager
def get_session():
    """Context manager for BigQuery sessions"""
    SessionMaker = get_session_maker()
    session = SessionMaker()
    
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

### Environment Variables

```bash
# .env
GCP_PROJECT_ID=my-project-id
BQ_DATASET_ID=my_dataset
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

## Models

### Base Model

```python
# app/models/base.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

### BigQuery-Specific Data Types

```python
# app/models/analytics_event.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, FLOAT, BOOLEAN, DATE
from sqlalchemy_bigquery import ARRAY, STRUCT
from app.models.base import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    
    # Partition by date for performance
    __table_args__ = {
        'bigquery_partition_by': 'DATE(event_timestamp)',
        'bigquery_cluster_by': ['event_type', 'user_id']
    }
    
    event_id = Column(Integer, primary_key=True)
    user_id = Column(String)
    event_type = Column(String)
    event_timestamp = Column(TIMESTAMP)
    event_date = Column(DATE)  # Partition column
    
    # BigQuery-specific types
    properties = Column(ARRAY(String))  # Array of strings
    metadata = Column(STRUCT)           # Nested structure
    
    value = Column(FLOAT)
    is_active = Column(BOOLEAN)
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'user_id': self.user_id,
            'event_type': self.event_type,
            'event_timestamp': self.event_timestamp.isoformat() if self.event_timestamp else None,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'properties': self.properties,
            'metadata': self.metadata,
            'value': self.value,
            'is_active': self.is_active
        }
```

### Supported Data Types

| BigQuery Type | SQLAlchemy Type | Python Type |
|---------------|-----------------|-------------|
| INT64 | Integer | int |
| FLOAT64 | FLOAT | float |
| STRING | String | str |
| BOOLEAN | BOOLEAN | bool |
| TIMESTAMP | TIMESTAMP | datetime |
| DATE | DATE | date |
| ARRAY | ARRAY(type) | list |
| STRUCT | STRUCT | dict |
| GEOGRAPHY | GEOGRAPHY | str (WKT) |
| JSON | JSON | dict |

## Repository Pattern

```python
# app/repositories/analytics_repository.py
from app.infra.bigquery_sa import get_session
from app.models.analytics_event import AnalyticsEvent
from sqlalchemy import func
from typing import List, Dict, Optional
from datetime import datetime, date

class AnalyticsRepository:
    
    @staticmethod
    def list_events(
        start_date: date,
        end_date: date,
        event_type: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """List events within date range"""
        with get_session() as session:
            query = session.query(AnalyticsEvent)\
                .filter(AnalyticsEvent.event_date >= start_date)\
                .filter(AnalyticsEvent.event_date < end_date)
            
            if event_type:
                query = query.filter(AnalyticsEvent.event_type == event_type)
            
            events = query.limit(limit).all()
            return [event.to_dict() for event in events]
    
    @staticmethod
    def get_event_counts_by_type(start_date: date, end_date: date) -> List[Dict]:
        """Aggregate event counts by type"""
        with get_session() as session:
            results = session.query(
                AnalyticsEvent.event_type,
                func.count(AnalyticsEvent.event_id).label('count')
            ).filter(
                AnalyticsEvent.event_date >= start_date,
                AnalyticsEvent.event_date < end_date
            ).group_by(AnalyticsEvent.event_type)\
             .order_by(func.count(AnalyticsEvent.event_id).desc())\
             .all()
            
            return [
                {'event_type': event_type, 'count': count}
                for event_type, count in results
            ]
    
    @staticmethod
    def insert_event(
        user_id: str,
        event_type: str,
        properties: List[str],
        value: float = 0.0
    ) -> int:
        """Insert new event"""
        with get_session() as session:
            now = datetime.utcnow()
            event = AnalyticsEvent(
                user_id=user_id,
                event_type=event_type,
                event_timestamp=now,
                event_date=now.date(),
                properties=properties,
                value=value,
                is_active=True
            )
            session.add(event)
            session.flush()
            return event.event_id
    
    @staticmethod
    def bulk_insert_events(events_data: List[Dict]) -> None:
        """Bulk insert events for better performance"""
        with get_session() as session:
            events = [
                AnalyticsEvent(**data)
                for data in events_data
            ]
            session.bulk_save_objects(events)
```

## Performance Optimization

### 1. Partitioning

Partition tables by date to reduce data scanned:

```python
class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    
    __table_args__ = {
        'bigquery_partition_by': 'DATE(event_timestamp)',
        'bigquery_partition_expiration_days': 90  # Auto-delete old partitions
    }
```

**Always filter by partition column:**

```python
# Good: Filters by partition column
events = session.query(AnalyticsEvent)\
    .filter(AnalyticsEvent.event_date >= '2024-01-01')\
    .filter(AnalyticsEvent.event_date < '2024-02-01')\
    .all()

# Bad: Scans entire table
events = session.query(AnalyticsEvent)\
    .filter(AnalyticsEvent.user_id == 'user123')\
    .all()
```

### 2. Clustering

Cluster tables by frequently filtered columns:

```python
__table_args__ = {
    'bigquery_partition_by': 'DATE(event_timestamp)',
    'bigquery_cluster_by': ['event_type', 'user_id']
}
```

### 3. Select Only Needed Columns

```python
# Good: Select specific columns
user_ids = session.query(AnalyticsEvent.user_id).distinct().all()

# Bad: Selects all columns (expensive)
events = session.query(AnalyticsEvent).all()
user_ids = list(set(e.user_id for e in events))
```

### 4. Limit Result Sets

```python
# Always use LIMIT for exploratory queries
events = session.query(AnalyticsEvent)\
    .filter(AnalyticsEvent.event_date == date.today())\
    .limit(1000)\
    .all()
```

### 5. Use Aggregations in BigQuery

```python
# Good: Aggregation in BigQuery
daily_totals = session.query(
    AnalyticsEvent.event_date,
    func.sum(AnalyticsEvent.value).label('total')
).group_by(AnalyticsEvent.event_date).all()

# Bad: Fetch all data and aggregate in Python
events = session.query(AnalyticsEvent).all()
daily_totals = {}
for event in events:
    daily_totals[event.event_date] = daily_totals.get(event.event_date, 0) + event.value
```

## Cost Management

### Query Cost Estimation

```python
from google.cloud import bigquery

def estimate_query_cost(query_string: str) -> float:
    """Estimate query cost in USD"""
    client = bigquery.Client()
    
    job_config = bigquery.QueryJobConfig(dry_run=True)
    query_job = client.query(query_string, job_config=job_config)
    
    bytes_processed = query_job.total_bytes_processed
    cost_per_tb = 5.0  # $5 per TB (as of 2024)
    cost = (bytes_processed / (1024**4)) * cost_per_tb
    
    return cost
```

### Cost Optimization Strategies

1. **Partition tables** by date to reduce scanned data
2. **Cluster tables** by frequently filtered columns
3. **Avoid SELECT *** - specify only needed columns
4. **Use materialized views** for repeated queries
5. **Cache results** when possible (24-hour cache)
6. **Set query quotas** to prevent runaway costs
7. **Monitor query costs** with Cloud Logging

## Error Handling

### Common Exceptions

```python
from google.cloud.exceptions import NotFound, BadRequest, Forbidden
from sqlalchemy.exc import OperationalError, ProgrammingError

def safe_query_execution(query_func):
    """Execute BigQuery query with error handling"""
    try:
        return query_func()
        
    except NotFound as e:
        raise ValueError(f"Table or dataset not found: {e}")
        
    except BadRequest as e:
        raise ValueError(f"Invalid query syntax: {e}")
        
    except Forbidden as e:
        raise PermissionError(f"Insufficient permissions: {e}")
        
    except OperationalError as e:
        raise RuntimeError(f"Connection error: {e}")
        
    except ProgrammingError as e:
        raise ValueError(f"SQL syntax error: {e}")
```

### Retry Logic

```python
from time import sleep
from google.api_core.exceptions import TooManyRequests

def execute_with_retry(func, max_retries=3, delay=2):
    """Execute with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except TooManyRequests as e:
            if attempt == max_retries - 1:
                raise
            wait_time = delay * (2 ** attempt)
            sleep(wait_time)
```

## Testing

### Test with BigQuery Emulator

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from app.models.base import Base

@pytest.fixture(scope="session")
def test_engine():
    """Create test BigQuery engine"""
    # Use SQLite for local testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(test_engine):
    """Create test session"""
    from sqlalchemy.orm import sessionmaker
    SessionMaker = sessionmaker(bind=test_engine)
    session = SessionMaker()
    
    yield session
    
    session.rollback()
    session.close()
```

### Integration Test

```python
def test_insert_and_query(db_session):
    """Test event insertion and retrieval"""
    from app.repositories.analytics_repository import AnalyticsRepository
    from datetime import date
    
    # Insert
    event_id = AnalyticsRepository.insert_event(
        user_id="test_user",
        event_type="page_view",
        properties=["home", "desktop"],
        value=1.0
    )
    
    # Query
    events = AnalyticsRepository.list_events(
        start_date=date.today(),
        end_date=date.today(),
        event_type="page_view"
    )
    
    assert len(events) == 1
    assert events[0]['user_id'] == "test_user"
```

## Security

### Service Account Best Practices

1. **Use separate service accounts** for dev/staging/prod
2. **Grant minimum required permissions** (principle of least privilege)
3. **Rotate service account keys** regularly
4. **Never commit credentials** to version control
5. **Use Secret Manager** for production environments

### Connection String Security

```python
# Good: Environment variables
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Bad: Hardcoded paths
CREDENTIALS_PATH = "/path/to/service-account-key.json"  # Never do this!
```

### Row-Level Security

```python
# Filter data based on user permissions
def get_user_events(user_id: str, requesting_user_id: str) -> List[Dict]:
    """Get events with row-level security"""
    if user_id != requesting_user_id:
        raise PermissionError("Cannot access other user's data")
    
    with get_session() as session:
        events = session.query(AnalyticsEvent)\
            .filter(AnalyticsEvent.user_id == user_id)\
            .all()
        return [e.to_dict() for e in events]
```

## Monitoring

### Query Logging

```python
import logging

# Enable SQL logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Or in engine configuration
engine = create_engine(connection_string, echo=True)
```

### Performance Monitoring

```python
from google.cloud import bigquery
from google.cloud.bigquery import QueryJob

def log_query_stats(query_job: QueryJob):
    """Log query performance metrics"""
    print(f"Query completed in {query_job.ended - query_job.started}")
    print(f"Bytes processed: {query_job.total_bytes_processed:,}")
    print(f"Bytes billed: {query_job.total_bytes_billed:,}")
    print(f"Slot time: {query_job.slot_millis} ms")
```

## Best Practices

1. **Always partition tables** by date for time-series data
2. **Use clustering** for frequently filtered columns
3. **Filter by partition column** in every query
4. **Avoid SELECT *** - specify only needed columns
5. **Use bulk inserts** for better performance
6. **Set appropriate query limits** to prevent excessive costs
7. **Monitor query costs** and set budgets/alerts
8. **Use materialized views** for repeated aggregations
9. **Implement proper error handling** for all queries
10. **Test with smaller datasets** before running on production data

## References

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [SQLAlchemy BigQuery Dialect](https://github.com/googleapis/python-bigquery-sqlalchemy)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [BigQuery Pricing](https://cloud.google.com/bigquery/pricing)
- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql)
