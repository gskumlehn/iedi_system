# Architecture Documentation

This folder contains **generic technical guidelines** and architectural patterns for building Python web applications with Flask and clean architecture principles.

## Core Principles

This documentation follows a **clean architecture pattern** inspired by industry best practices, emphasizing:

- **Separation of concerns** through layered architecture
- **Modularity** with blueprints and repositories
- **Dependency inversion** - depend on abstractions, not implementations
- **Single responsibility** - each module has one reason to change
- **Code in English** without comments (self-documenting code)
- **Type hints** for better code documentation and IDE support

## Documentation Index

### Core Architecture

1. **[ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md)** - Complete overview of clean architecture layers, design patterns (Factory, Repository, Blueprint, Context Manager), request flow, and core principles.

2. **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** - Standard project structure template with folder organization, file responsibilities, and layer definitions (controllers, services, repositories, models, infrastructure).

3. **[BLUEPRINT_PATTERN.md](./BLUEPRINT_PATTERN.md)** - Flask blueprints for modular routing, URL prefix strategies, error handling, and best practices for organizing controllers.

4. **[REPOSITORY_PATTERN.md](./REPOSITORY_PATTERN.md)** - Data access layer abstraction, session management, CRUD operations, query patterns, and testing strategies.

5. **[DATABASE_SETUP.md](./DATABASE_SETUP.md)** - SQLAlchemy configuration, connection pooling, transaction management, migrations, performance optimization, and security best practices.

## Architecture Layers

The recommended architecture follows these layers:

```
┌─────────────────────────────────────────┐
│     Presentation (Controllers)          │  ← HTTP routing, request/response
├─────────────────────────────────────────┤
│     Business Logic (Services)           │  ← Business rules, orchestration
├─────────────────────────────────────────┤
│     Data Access (Repositories)          │  ← Database queries, persistence
├─────────────────────────────────────────┤
│     Domain (Models)                     │  ← Entities, ORM mappings
├─────────────────────────────────────────┤
│     Infrastructure                      │  ← Database, external APIs
└─────────────────────────────────────────┘
```

### Layer Responsibilities

1. **Controllers** (`app/controllers/`) - Handle HTTP requests/responses, input validation
2. **Services** (`app/services/`) - Implement business logic, orchestrate operations
3. **Repositories** (`app/repositories/`) - Abstract data access, manage database operations
4. **Models** (`app/models/`) - Define domain entities with ORM mappings
5. **Infrastructure** (`app/infra/`) - Database connections, external integrations

## Technology Stack

### Core Framework
- **Python**: 3.11+
- **Flask**: 3.0+ (web framework)
- **SQLAlchemy**: 2.0+ (ORM)
- **Gunicorn**: WSGI server for production

### Database Support
- **MySQL/MariaDB**: Production-grade relational database
- **PostgreSQL**: Advanced features, ACID compliance
- **SQLite**: Development and testing

### Design Patterns
- **Factory Pattern**: Application creation (`create_app()`)
- **Repository Pattern**: Data access abstraction
- **Blueprint Pattern**: Modular routing
- **Context Manager Pattern**: Session management

## Quick Start

### 1. Project Structure

```
project/
├── wsgi.py                    # Entry point
├── app/
│   ├── __init__.py           # Application factory
│   ├── controllers/          # Blueprints (HTTP layer)
│   ├── services/             # Business logic
│   ├── repositories/         # Data access
│   ├── models/               # Domain entities
│   └── infra/                # Infrastructure
├── templates/                # HTML templates
├── static/                   # CSS/JS/images
├── tests/                    # Test suite
└── requirements.txt          # Dependencies
```

### 2. Application Factory

```python
# app/__init__.py
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    
    # Register blueprints
    from app.controllers.feature_controller import feature_bp
    app.register_blueprint(feature_bp, url_prefix="/features")
    
    return app
```

### 3. Blueprint Controller

```python
# app/controllers/feature_controller.py
from flask import Blueprint, jsonify
from app.repositories.feature_repository import FeatureRepository

feature_bp = Blueprint("feature", __name__)

@feature_bp.route("/api")
def list_features():
    features = FeatureRepository.list_all()
    return jsonify(features)
```

### 4. Repository

```python
# app/repositories/feature_repository.py
from app.infra.database import get_session
from app.models.feature import Feature

class FeatureRepository:
    @staticmethod
    def list_all():
        with get_session() as session:
            features = session.query(Feature).all()
            return [f.to_dict() for f in features]
```

## Best Practices

### Code Organization
- ✅ One blueprint per feature/resource
- ✅ One repository per model
- ✅ Keep controllers thin (HTTP only)
- ✅ Business logic in services
- ✅ Data access in repositories

### Database
- ✅ Use context managers for sessions
- ✅ Return dictionaries from repositories
- ✅ Enable connection pooling
- ✅ Use parameterized queries
- ✅ Implement proper error handling

### Testing
- ✅ Unit tests for repositories and services
- ✅ Integration tests for controllers
- ✅ Use separate test database
- ✅ Mock external dependencies

### Security
- ✅ Environment variables for secrets
- ✅ Parameterized queries (prevent SQL injection)
- ✅ Password hashing (never store plain text)
- ✅ HTTPS in production (ProxyFix middleware)

## Purpose

These documents provide **reusable architectural patterns** that can be applied to any Python web application project.

### What This Is
- ✅ Generic architectural guidelines
- ✅ Design patterns and best practices
- ✅ Code structure templates
- ✅ Technology stack recommendations

### What This Is NOT
- ❌ Project-specific business logic
- ❌ Domain-specific calculations
- ❌ API integration details for specific services
- ❌ Implementation of specific features

## Navigation

- [← Back to root](../../README.md)
- [→ Business Documentation](../business/README.md) - Project-specific logic and integrations

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Repository Pattern by Martin Fowler](https://martinfowler.com/eaaCatalog/repository.html)
