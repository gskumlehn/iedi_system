# IEDI System - Project Structure Guide

## Directory Structure

```
iedi_system/
├── app/
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── bank.py
│   │   ├── media_outlet.py
│   │   ├── analysis.py
│   │   ├── mention.py
│   │   └── iedi_result.py
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   ├── bank_repository.py
│   │   ├── media_outlet_repository.py
│   │   ├── analysis_repository.py
│   │   ├── mention_repository.py
│   │   └── iedi_result_repository.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── iedi_calculator.py
│   │   ├── brandwatch_service.py
│   │   └── analysis_service.py
│   ├── controllers/         # Flask blueprints
│   │   ├── __init__.py
│   │   ├── bank_controller.py
│   │   ├── media_outlet_controller.py
│   │   └── analysis_controller.py
│   ├── infra/               # Infrastructure
│   │   ├── __init__.py
│   │   └── bq_sa.py
│   ├── enums/               # Enumerations
│   │   ├── __init__.py
│   │   ├── sentiment.py
│   │   └── reach_group.py
│   ├── constants/           # Constants
│   │   ├── __init__.py
│   │   └── weights.py
│   └── utils/               # Utilities
│       └── __init__.py
├── templates/               # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── banks.html
│   ├── media_outlets.html
│   └── create_analysis.html
├── static/                  # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── app.py                   # Flask application
├── requirements.txt
└── README.md
```

## Code Style Guidelines

### General Rules

1. **Language**: English only (backend)
2. **Comments**: No explanatory comments
3. **Imports**: Alphabetical order
4. **Spacing**: 1 blank line between methods
5. **Type Hints**: Always use type hints

### Import Order

```python
# Standard library
from datetime import datetime
from typing import List, Optional

# Third-party
from flask import Blueprint, jsonify, request
from sqlalchemy import Column, Integer, String

# Local
from app.infra.bq_sa import get_session
from app.models.bank import Bank
```

### Model Example

```python
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Bank(Base):
    __tablename__ = "banks"
    __table_args__ = {"schema": "iedi"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

### Repository Example

```python
from typing import List, Optional
from app.infra.bq_sa import get_session
from app.models.bank import Bank

class BankRepository:

    def create(self, name: str) -> Bank:
        session = get_session()
        bank = Bank(name=name)
        session.add(bank)
        session.commit()
        session.refresh(bank)
        return bank

    def find_by_id(self, bank_id: int) -> Optional[Bank]:
        session = get_session()
        return session.query(Bank).filter(Bank.id == bank_id).first()

    def find_all(self) -> List[Bank]:
        session = get_session()
        return session.query(Bank).all()
```

### Service Example

```python
from typing import Dict, List
from app.constants.weights import TITLE_WEIGHT
from app.models.bank import Bank
from app.repositories.bank_repository import BankRepository

class IEDICalculator:

    def __init__(self):
        self.bank_repo = BankRepository()

    def calculate(self, mention: Dict, bank: Bank) -> float:
        numerator = 0
        denominator = 0
        
        if self._check_title(mention["title"], bank):
            numerator += TITLE_WEIGHT
        denominator += TITLE_WEIGHT
        
        return (numerator / denominator) * 10 if denominator > 0 else 0.0

    def _check_title(self, title: str, bank: Bank) -> bool:
        return bank.name.lower() in title.lower()
```

### Controller Example

```python
from flask import Blueprint, jsonify, request
from app.services.analysis_service import AnalysisService

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api/analysis")
analysis_service = AnalysisService()

@analysis_bp.route("/", methods=["POST"])
def create_analysis():
    data = request.json
    result = analysis_service.create(
        name=data["name"],
        query=data["query"]
    )
    return jsonify({"success": True, "data": result}), 201

@analysis_bp.route("/", methods=["GET"])
def list_analyses():
    analyses = analysis_service.list_all()
    return jsonify({"success": True, "data": analyses}), 200
```

## Frontend Guidelines

### HTML Structure

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>IEDI - Sistema</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <nav>
        <a href="/">Início</a>
        <a href="/bancos">Bancos</a>
        <a href="/veiculos">Veículos</a>
        <a href="/analises">Análises</a>
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
    <script src="/static/js/main.js"></script>
</body>
</html>
```

### Messages (Portuguese)

```javascript
const messages = {
    success: "Operação realizada com sucesso!",
    error: "Erro ao processar solicitação",
    required: "Campo obrigatório",
    invalid: "Valor inválido"
};
```

## Remaining Files to Create

### Repositories
- `media_outlet_repository.py`
- `mention_repository.py`
- `iedi_result_repository.py`

### Services
- `iedi_calculator.py` (use iedi_calculator_v2.py as base)
- `brandwatch_service.py`
- `analysis_service.py`

### Controllers
- `bank_controller.py`
- `media_outlet_controller.py`
- `analysis_controller.py`

### Templates
- `base.html`
- `index.html`
- `banks.html`
- `media_outlets.html`
- `create_analysis.html`

### Static Files
- `static/css/style.css`
- `static/js/main.js`

### Main Application
- `app.py`
- `requirements.txt`

## Next Steps

1. Create remaining repositories following BankRepository pattern
2. Create services following business logic separation
3. Create controllers as Flask blueprints
4. Create minimal frontend templates
5. Create main app.py with all blueprints registered
6. Test end-to-end flow
7. Deploy to production

## Environment Variables

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GCP_PROJECT_ID=your-project-id
FLASK_APP=app.py
FLASK_ENV=development
```
