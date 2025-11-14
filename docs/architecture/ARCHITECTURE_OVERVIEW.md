# Architecture Overview

This document describes the overall architecture pattern used in this system, based on Clean Architecture principles with Flask.

## Architecture Layers

The system follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│          Presentation Layer             │
│    (Controllers / Blueprints)           │
│  - HTTP routing                         │
│  - Request/response handling            │
│  - Input validation                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Business Logic Layer           │
│            (Services)                   │
│  - Business rules                       │
│  - Orchestration                        │
│  - Domain logic                         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Data Access Layer              │
│          (Repositories)                 │
│  - Database queries                     │
│  - Data persistence                     │
│  - Transaction management               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Infrastructure Layer           │
│     (Database / External APIs)          │
│  - SQLAlchemy engine (MySQL/PostgreSQL) │
│  - BigQuery engine (Analytics)          │
│  - Connection pooling                   │
│  - External integrations                │
└─────────────────────────────────────────┘
```

## Directory Structure

```
project/
├── wsgi.py                    # Application entry point
├── app/
│   ├── __init__.py           # Application factory
│   ├── controllers/          # Presentation layer
│   │   ├── root_controller.py
│   │   └── feature_controller.py
│   ├── services/             # Business logic layer
│   │   └── feature_service.py
│   ├── repositories/         # Data access layer
│   │   └── feature_repository.py
│   ├── models/               # Domain models (SQLAlchemy)
│   │   └── feature.py
│   ├── infra/                # Infrastructure
│   │   ├── database.py        # MySQL/PostgreSQL
│   │   └── bigquery_sa.py     # BigQuery (optional)
│   ├── constants/            # Application constants
│   ├── enums/                # Enumerations
│   └── utils/                # Utility functions
├── templates/                # HTML templates (Jinja2)
├── static/                   # Static files (CSS/JS/images)
└── tests/                    # Test suite
```

## Core Principles

### 1. Dependency Inversion
Higher-level modules do not depend on lower-level modules. Both depend on abstractions.

```python
# ❌ Bad: Controller depends on concrete implementation
class FeatureController:
    def __init__(self):
        self.db = MySQLDatabase()  # Tight coupling

# ✅ Good: Controller depends on abstraction
class FeatureController:
    def __init__(self, repository: FeatureRepository):
        self.repository = repository  # Loose coupling
```

### 2. Single Responsibility
Each module has one reason to change.

- **Controllers**: Handle HTTP requests/responses only
- **Services**: Implement business logic only
- **Repositories**: Handle data persistence only

### 3. Separation of Concerns
Each layer has a clear responsibility:

```python
# Controller (HTTP handling)
@feature_bp.route("/api")
def list_features():
    features = FeatureRepository.list_all()
    return jsonify(features)

# Repository (Data access)
class FeatureRepository:
    @staticmethod
    def list_all():
        with get_session() as session:
            return session.query(Feature).all()

# Model (Domain entity)
class Feature(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
```

## Design Patterns

### 1. Factory Pattern
Application creation is encapsulated in a factory function:

```python
def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(feature_bp, url_prefix="/features")
    
    return app
```

### 2. Repository Pattern
Data access is abstracted through repositories:

```python
class FeatureRepository:
    @staticmethod
    def find_by_id(id: int) -> Optional[Feature]:
        with get_session() as session:
            return session.query(Feature).filter_by(id=id).first()
```

### 3. Blueprint Pattern
Routes are organized into blueprints by feature:

```python
feature_bp = Blueprint("feature", __name__)

@feature_bp.route("/")
def index():
    return render_template("feature/index.html")
```

### 4. Context Manager Pattern
Database sessions are managed with context managers:

```python
@contextmanager
def get_session():
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

## Request Flow

```
1. HTTP Request
   ↓
2. Flask Router → Blueprint
   ↓
3. Controller → Validate input
   ↓
4. Service → Business logic (optional)
   ↓
5. Repository → Database query
   ↓
6. Model → ORM mapping
   ↓
7. Database
   ↓
8. Response (JSON/HTML)
```

Example:
```python
# 1. Request: GET /features/api/1

# 2. Router matches blueprint
@feature_bp.route("/api/<int:id>")

# 3. Controller
def get_feature(id):
    # 4. Service (if needed)
    # feature = FeatureService.get_with_details(id)
    
    # 5. Repository
    feature = FeatureRepository.find_by_id(id)
    
    # 6-7. Model + Database
    # SQLAlchemy handles ORM
    
    # 8. Response
    return jsonify(feature.to_dict())
```

## Configuration Management

### Environment Variables
Configuration is loaded from environment variables:

```python
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "database")
```

### Application Factory
Configuration is applied during app creation:

```python
def create_app(config=None):
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.update(config)
    
    # Setup middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    
    # Register blueprints
    register_blueprints(app)
    
    return app
```

## Error Handling

### Repository Level
```python
class FeatureRepository:
    @staticmethod
    def create(data: dict) -> int:
        try:
            with get_session() as session:
                feature = Feature(**data)
                session.add(feature)
                session.flush()
                return feature.id
        except IntegrityError as e:
            raise ValueError(f"Duplicate entry: {e}")
```

### Controller Level
```python
@feature_bp.route("/api", methods=['POST'])
def create_feature():
    try:
        data = request.json
        feature_id = FeatureRepository.create(data)
        return jsonify({'id': feature_id, 'success': True})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
```

## Testing Strategy

### Unit Tests
Test individual components in isolation:

```python
def test_repository_create():
    # Arrange
    data = {'name': 'Test Feature'}
    
    # Act
    feature_id = FeatureRepository.create(data)
    
    # Assert
    assert feature_id > 0
```

### Integration Tests
Test component interactions:

```python
def test_feature_creation_flow(client):
    # Act
    response = client.post('/features/api', json={'name': 'Test'})
    
    # Assert
    assert response.status_code == 200
    assert response.json['success'] == True
```

## Deployment Architecture

```
┌─────────────┐
│   Nginx     │  (Reverse proxy)
│   Port 80   │
└──────┬──────┘
       │
┌──────▼──────┐
│  Gunicorn   │  (WSGI server)
│  Port 8080  │
└──────┬──────┘
       │
┌──────▼──────┐
│ Flask App   │  (Python application)
│  (Workers)  │
└──────┬──────┘
       │
┌──────▼──────┐
│   MySQL     │  (Database)
│  Port 3306  │
└─────────────┘
```

## Best Practices

### 1. Keep Controllers Thin
Controllers should only handle HTTP concerns:
```python
# ✅ Good
@feature_bp.route("/api")
def list_features():
    features = FeatureRepository.list_all()
    return jsonify(features)

# ❌ Bad
@feature_bp.route("/api")
def list_features():
    # Business logic in controller
    features = []
    for item in raw_data:
        if item.is_valid():
            features.append(transform(item))
    return jsonify(features)
```

### 2. Use Static Methods in Repositories
Repositories don't need instance state:
```python
class FeatureRepository:
    @staticmethod
    def list_all():
        # ...
```

### 3. Return Dictionaries from Repositories
Decouple ORM models from API responses:
```python
class Feature(Base):
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class FeatureRepository:
    @staticmethod
    def list_all():
        with get_session() as session:
            features = session.query(Feature).all()
            return [f.to_dict() for f in features]
```

### 4. Use Context Managers for Sessions
Always ensure proper cleanup:
```python
# ✅ Good
with get_session() as session:
    result = session.query(Feature).all()

# ❌ Bad
session = get_session()
result = session.query(Feature).all()
# Session never closed!
```

## References

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Flask Application Factories](https://flask.palletsprojects.com/en/latest/patterns/appfactories/)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [SQLAlchemy Best Practices](https://docs.sqlalchemy.org/en/latest/orm/session_basics.html)
