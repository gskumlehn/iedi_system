# Project Structure Template

This document defines a generic project structure for Python-based data processing systems following clean architecture principles.

## Directory Structure

```
project_root/
├── app/
│   ├── models/              # Data models (SQLAlchemy ORM)
│   │   ├── __init__.py
│   │   ├── entity_a.py
│   │   ├── entity_b.py
│   │   └── entity_c.py
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   ├── entity_a_repository.py
│   │   ├── entity_b_repository.py
│   │   └── entity_c_repository.py
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── calculation_service.py
│   │   ├── external_api_service.py
│   │   └── orchestration_service.py
│   ├── controllers/         # API endpoints (Flask blueprints)
│   │   ├── __init__.py
│   │   ├── entity_a_controller.py
│   │   ├── entity_b_controller.py
│   │   └── process_controller.py
│   ├── infra/               # Infrastructure integrations
│   │   ├── __init__.py
│   │   ├── database_engine.py
│   │   └── external_api_client.py
│   ├── enums/               # Enumerations
│   │   ├── __init__.py
│   │   ├── status.py
│   │   └── category.py
│   ├── constants/           # Application constants
│   │   ├── __init__.py
│   │   └── config.py
│   └── utils/               # Utility functions
│       └── __init__.py
├── templates/               # HTML templates (if using server-side rendering)
│   ├── base.html
│   ├── index.html
│   └── components/
├── static/                  # Static assets (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── img/
├── sql/                     # SQL scripts for database setup
│   ├── 01_create_schema.sql
│   ├── 02_create_tables.sql
│   └── 03_insert_seed_data.sql
├── tests/                   # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/                    # Documentation
│   ├── architecture/
│   └── business/
├── .env_sample              # Environment variables template
├── .gitignore
├── app.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md
```

## Layer Responsibilities

### Models (`app/models/`)

Data entities representing database tables or domain objects.

**Responsibilities:**
- Define table structure with SQLAlchemy ORM
- Implement hybrid properties for database compatibility (dates, enums, arrays)
- Define relationships between entities
- Keep models pure (no business logic)

**Example:**
```python
from sqlalchemy import Column, Integer, String, Date, Enum
from sqlalchemy.ext.hybrid import hybrid_property

class Entity(Base):
    __tablename__ = 'entities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    _status = Column('status', String(20))
    _created_at = Column('created_at', DateTime(timezone=True))
    
    @hybrid_property
    def status(self):
        return EntityStatus(self._status) if self._status else None
    
    @status.setter
    def status(self, value):
        self._status = value.value if value else None
```

### Repositories (`app/repositories/`)

Data access layer abstracting database operations.

**Responsibilities:**
- CRUD operations (Create, Read, Update, Delete)
- Query construction and execution
- Transaction management
- Return domain models, not raw database rows

**Example:**
```python
class EntityRepository:
    def __init__(self, session):
        self.session = session
    
    def find_all(self):
        return self.session.query(Entity).all()
    
    def find_by_id(self, entity_id):
        return self.session.query(Entity).filter(Entity.id == entity_id).first()
    
    def save(self, entity):
        self.session.add(entity)
        self.session.commit()
        return entity
    
    def delete(self, entity_id):
        entity = self.find_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
```

### Services (`app/services/`)

Business logic and orchestration layer.

**Responsibilities:**
- Implement business rules and calculations
- Orchestrate multiple repositories
- Handle external API integrations
- Coordinate complex workflows
- Validate business constraints

**Example:**
```python
class CalculationService:
    def __init__(self, entity_repository, config_repository):
        self.entity_repository = entity_repository
        self.config_repository = config_repository
    
    def calculate_metric(self, entity_id):
        entity = self.entity_repository.find_by_id(entity_id)
        config = self.config_repository.get_active_config()
        
        # Business logic here
        result = self._apply_formula(entity, config)
        
        return result
    
    def _apply_formula(self, entity, config):
        # Complex calculation logic
        pass
```

### Controllers (`app/controllers/`)

API endpoints handling HTTP requests and responses.

**Responsibilities:**
- Define REST API routes
- Validate request parameters
- Call appropriate services
- Format responses (JSON)
- Handle HTTP status codes and errors

**Example:**
```python
from flask import Blueprint, jsonify, request

entity_bp = Blueprint('entities', __name__)

@entity_bp.route('/api/entities', methods=['GET'])
def list_entities():
    service = EntityService()
    entities = service.get_all_entities()
    return jsonify([entity.to_dict() for entity in entities])

@entity_bp.route('/api/entities/<int:id>', methods=['GET'])
def get_entity(id):
    service = EntityService()
    entity = service.get_entity_by_id(id)
    if not entity:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(entity.to_dict())
```

### Infrastructure (`app/infra/`)

External system integrations and technical concerns.

**Responsibilities:**
- Database connection management
- External API clients
- Cloud service integrations (BigQuery, S3, etc.)
- Configuration management

**Example:**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseEngine:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()
```

### Enums (`app/enums/`)

Type-safe enumeration definitions.

**Responsibilities:**
- Define fixed sets of values
- Provide type safety
- Centralize constant definitions

**Example:**
```python
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

## Code Organization Principles

1. **Alphabetical imports** - All imports sorted alphabetically
2. **One-line spacing** - Single blank line between methods
3. **English only** - All code, variables, and functions in English
4. **No comments** - Self-documenting code with clear naming
5. **Single responsibility** - Each class/function has one clear purpose
6. **Dependency injection** - Pass dependencies through constructors

## File Naming Conventions

- **Models**: `entity_name.py` (singular, snake_case)
- **Repositories**: `entity_name_repository.py`
- **Services**: `purpose_service.py` or `entity_name_service.py`
- **Controllers**: `entity_name_controller.py`
- **Tests**: `test_entity_name.py`

## Import Order

```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party packages
from flask import Flask, jsonify
from sqlalchemy import Column, Integer

# 3. Local application
from app.models.entity import Entity
from app.repositories.entity_repository import EntityRepository
```

All imports within each group should be alphabetically sorted.
