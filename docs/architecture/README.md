# Architecture Documentation

This folder contains generic technical guidelines and architectural patterns for building Python-based data processing systems with clean architecture principles.

## Core Principles

This documentation follows a **clean architecture pattern** inspired by industry best practices, emphasizing:

- **Separation of concerns** through layered architecture
- **Code in English** without comments (self-documenting code)
- **Alphabetically ordered imports** for consistency
- **One-line spacing between methods** for readability
- **Hybrid property patterns** for database compatibility

## Documentation Index

### Project Foundation

**[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** - Complete project structure template with folder organization, file responsibilities, and layer definitions (models, repositories, services, controllers).

**[NAMING_CONVENTIONS.md](./NAMING_CONVENTIONS.md)** - Comprehensive naming standards for backend (Python) and frontend (JavaScript/TypeScript) including variables, functions, classes, files, and database entities.

### Setup and Installation

**[INSTALLATION.md](./INSTALLATION.md)** - Step-by-step installation guide for setting up the development environment, dependencies, and initial configuration.

**[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Implementation guide covering the complete development workflow from project initialization to deployment.

### System Architecture

**[SYSTEM_FLOW.md](./SYSTEM_FLOW.md)** - System flowcharts and architecture diagrams illustrating data flow, component interactions, and process sequences.

### Integration Patterns

**[API_INTEGRATION.md](./API_INTEGRATION.md)** - Guidelines for integrating external APIs, handling authentication, error management, and data transformation patterns.

**[BIGQUERY_INTEGRATION.md](./BIGQUERY_INTEGRATION.md)** - Specific patterns for integrating Google BigQuery as data warehouse, including schema design, hybrid properties for compatibility, and query optimization.

## Architecture Layers

The recommended architecture follows these layers:

1. **Models** - Data entities with ORM mappings and hybrid properties
2. **Repositories** - Data access layer abstracting database operations
3. **Services** - Business logic and orchestration
4. **Controllers** - API endpoints and request handling
5. **Infrastructure** - External integrations (databases, APIs, cloud services)

## Technology Stack Template

- **Backend**: Python 3.11+, Flask 3.0+, SQLAlchemy
- **Database**: BigQuery (data warehouse), PostgreSQL/MySQL (operational)
- **API Integration**: REST APIs with requests library
- **Code Style**: English, no comments, clean architecture

## Navigation

- [← Back to root](../../README.md)
- [→ Business Documentation](../business/README.md)
