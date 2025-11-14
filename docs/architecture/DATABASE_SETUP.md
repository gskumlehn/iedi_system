# Database Setup Guide

This guide covers database configuration, connection management, and best practices for Python applications using SQLAlchemy.

## Database Selection

### Supported Databases

SQLAlchemy supports multiple database backends:

- **PostgreSQL**: Production-grade, ACID compliant, advanced features
- **MySQL/MariaDB**: Widely used, good performance, mature ecosystem
- **SQLite**: Embedded, zero-configuration, development/testing
- **Oracle**: Enterprise, high performance, commercial
- **Microsoft SQL Server**: Enterprise, Windows integration

### Connection Strings

```python
# PostgreSQL
postgresql://user:password@host:5432/database

# MySQL/MariaDB
mysql+pymysql://user:password@host:3306/database

# SQLite
sqlite:///path/to/database.db

# SQL Server
mssql+pyodbc://user:password@host/database?driver=ODBC+Driver+17+for+SQL+Server
```

## SQLAlchemy Setup

### 1. Install Dependencies

```bash
# Core
pip install SQLAlchemy

# Database drivers
pip install pymysql          # MySQL/MariaDB
pip install psycopg2-binary  # PostgreSQL
pip install pyodbc           # SQL Server
```

### 2. Create Database Module

```python
# app/infra/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

_engine = None
_session_maker = None

def get_db_url():
    """Build database URL from environment variables"""
    db_type = os.getenv("DB_TYPE", "mysql")  # mysql, postgresql, sqlite
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "database")
    
    if db_type == "sqlite":
        return f"sqlite:///{db_name}.db"
    elif db_type == "postgresql":
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:  # mysql
        return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"

def get_engine():
    """Create and configure SQLAlchemy engine"""
    global _engine
    if _engine is None:
        db_url = get_db_url()
        _engine = create_engine(
            db_url,
            pool_pre_ping=True,      # Verify connections before using
            pool_recycle=3600,       # Recycle connections after 1 hour
            pool_size=10,            # Connection pool size
            max_overflow=20,         # Max connections beyond pool_size
            echo=False               # Set to True for SQL logging
        )
    return _engine

def get_session_maker():
    """Get sessionmaker instance"""
    global _session_maker
    if _session_maker is None:
        engine = get_engine()
        _session_maker = sessionmaker(bind=engine)
    return _session_maker

@contextmanager
def get_session():
    """Context manager for database sessions"""
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

### 3. Environment Variables

Create `.env` file:

```bash
# Database Type
DB_TYPE=mysql              # mysql, postgresql, sqlite

# Connection
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=your_database

# Optional: Connection pool settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=3600
```

## Models

### Base Model

```python
# app/models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    """Abstract base model with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

### Example Model

```python
# app/models/user.py
from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    
    def to_dict(self):
        """Convert user to dictionary"""
        data = super().to_dict()
        data.update({
            'username': self.username,
            'email': self.email,
            'active': self.active
        })
        return data
```

## Migrations

### Using Alembic

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init migrations

# Configure alembic.ini
# Set: sqlalchemy.url = mysql+pymysql://user:pass@host/db

# Create migration
alembic revision --autogenerate -m "Create users table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Manual Migrations

```python
# scripts/create_tables.py
from app.infra.database import get_engine
from app.models.base import Base
from app.models.user import User
# Import all models

def create_tables():
    """Create all tables"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Tables created successfully")

if __name__ == "__main__":
    create_tables()
```

## Connection Pooling

### Configuration

```python
engine = create_engine(
    db_url,
    # Pool settings
    pool_size=10,              # Number of connections to maintain
    max_overflow=20,           # Max connections beyond pool_size
    pool_timeout=30,           # Seconds to wait for connection
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Verify connection before use
    
    # Performance
    echo=False,                # SQL logging (disable in production)
    echo_pool=False,           # Pool logging
    
    # Execution options
    isolation_level="READ_COMMITTED"  # Transaction isolation level
)
```

### Pool Monitoring

```python
def get_pool_status():
    """Get connection pool statistics"""
    engine = get_engine()
    pool = engine.pool
    
    return {
        'size': pool.size(),
        'checked_in': pool.checkedin(),
        'checked_out': pool.checkedout(),
        'overflow': pool.overflow(),
        'total': pool.size() + pool.overflow()
    }
```

## Transaction Management

### Automatic Transactions

```python
# Context manager handles commit/rollback automatically
with get_session() as session:
    user = User(username="john", email="john@example.com")
    session.add(user)
    # Commits on exit if no exception
```

### Manual Transactions

```python
from app.infra.database import get_session_maker

def complex_operation():
    SessionMaker = get_session_maker()
    session = SessionMaker()
    
    try:
        # Multiple operations
        user = User(username="john")
        session.add(user)
        session.flush()  # Get user.id without committing
        
        # Use user.id for related operations
        profile = Profile(user_id=user.id)
        session.add(profile)
        
        # Commit all changes
        session.commit()
        return user.id
        
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
```

### Nested Transactions (Savepoints)

```python
with get_session() as session:
    user = User(username="john")
    session.add(user)
    
    # Create savepoint
    savepoint = session.begin_nested()
    
    try:
        # Risky operation
        profile = Profile(user_id=user.id)
        session.add(profile)
    except Exception:
        # Rollback to savepoint
        savepoint.rollback()
    
    # Main transaction still active
    session.commit()
```

## Performance Optimization

### Lazy Loading vs Eager Loading

```python
# Lazy loading (default) - N+1 queries problem
users = session.query(User).all()
for user in users:
    print(user.profile.bio)  # Separate query for each user

# Eager loading - Single query with JOIN
from sqlalchemy.orm import joinedload

users = session.query(User).options(
    joinedload(User.profile)
).all()
for user in users:
    print(user.profile.bio)  # No additional queries
```

### Bulk Operations

```python
# Bulk insert
users = [
    User(username=f"user{i}", email=f"user{i}@example.com")
    for i in range(1000)
]
session.bulk_save_objects(users)
session.commit()

# Bulk update
session.query(User).filter(User.active == False).update(
    {'active': True},
    synchronize_session=False
)
session.commit()
```

### Query Optimization

```python
# Select specific columns
usernames = session.query(User.username).all()

# Use indexes
class User(BaseModel):
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
    )

# Limit results
users = session.query(User).limit(100).all()

# Use pagination
def get_users_page(page=1, per_page=20):
    offset = (page - 1) * per_page
    return session.query(User).offset(offset).limit(per_page).all()
```

## Error Handling

### Common Exceptions

```python
from sqlalchemy.exc import (
    IntegrityError,      # Constraint violations
    OperationalError,    # Connection issues
    DataError,           # Invalid data
    ProgrammingError     # SQL syntax errors
)

def create_user(username, email):
    try:
        with get_session() as session:
            user = User(username=username, email=email)
            session.add(user)
            return user.id
            
    except IntegrityError as e:
        if 'Duplicate entry' in str(e):
            raise ValueError(f"User '{username}' already exists")
        raise ValueError(f"Database constraint violation: {e}")
        
    except OperationalError as e:
        raise RuntimeError(f"Database connection error: {e}")
        
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")
```

### Retry Logic

```python
from time import sleep

def execute_with_retry(func, max_retries=3, delay=1):
    """Execute function with retry on connection errors"""
    for attempt in range(max_retries):
        try:
            return func()
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise
            sleep(delay * (attempt + 1))
```

## Testing

### Test Database Setup

```python
# conftest.py
import pytest
from app.infra.database import get_engine, get_session_maker
from app.models.base import Base

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(test_engine):
    """Create test database session"""
    SessionMaker = sessionmaker(bind=test_engine)
    session = SessionMaker()
    
    yield session
    
    session.rollback()
    session.close()
```

### Test Example

```python
def test_create_user(db_session):
    user = User(username="test", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.username == "test"
```

## Security

### SQL Injection Prevention

```python
# ✅ Good: Parameterized queries
username = request.args.get('username')
user = session.query(User).filter(User.username == username).first()

# ❌ Bad: String concatenation
username = request.args.get('username')
query = f"SELECT * FROM users WHERE username = '{username}'"
session.execute(query)  # Vulnerable to SQL injection!
```

### Password Hashing

```python
from werkzeug.security import generate_password_hash, check_password_hash

class User(BaseModel):
    password_hash = Column(String(255))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### Connection String Security

```python
# ✅ Good: Environment variables
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ❌ Bad: Hardcoded credentials
DB_PASSWORD = "my_secret_password"  # Never do this!
```

## Monitoring

### Query Logging

```python
import logging

# Enable SQL logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Or in engine configuration
engine = create_engine(db_url, echo=True)
```

### Performance Profiling

```python
from sqlalchemy import event
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop()
    if total > 1.0:  # Log slow queries
        print(f"Slow query ({total:.2f}s): {statement}")
```

## Best Practices

1. **Always use context managers** for session management
2. **Use connection pooling** in production
3. **Enable pool_pre_ping** to handle stale connections
4. **Set pool_recycle** to avoid connection timeouts
5. **Use parameterized queries** to prevent SQL injection
6. **Implement proper error handling** for database operations
7. **Use migrations** for schema changes
8. **Test with a separate database** (never use production)
9. **Monitor slow queries** and optimize indexes
10. **Never commit sensitive data** (passwords, API keys) in code

## References

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Database Connection Pooling](https://docs.sqlalchemy.org/en/latest/core/pooling.html)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/latest/orm/tutorial.html)
