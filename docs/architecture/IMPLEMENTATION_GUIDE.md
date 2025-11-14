# IEDI System - Implementation Guide

## Clean Architecture Created

Following bb-monitor pattern, we created a clean separation of concerns:

### Repositories (Data Access Layer)

**Created (5 repositories)**:
- `BankRepository` - CRUD for banks
- `AnalysisRepository` + `BankPeriodRepository` - Analysis management
- `RelevantMediaOutletRepository` + `NicheMediaOutletRepository` - Media outlets
- `MentionRepository` - Mentions storage
- `IEDIResultRepository` - IEDI results

**Pattern**:
```python
class BankRepository:
    def find_by_id(self, bank_id: int) -> Optional[Bank]:
        session = get_session()
        return session.query(Bank).filter(Bank.id == bank_id).first()
```

### Services (Business Logic Layer)

**Created (4 services)**:
- `BankService` - Bank business logic
- `MediaOutletService` - Media outlet management
- `IEDICalculatorService` - IEDI calculation logic (v2.0 methodology)
- `AnalysisService` - Orchestrates entire analysis flow

**Pattern**:
```python
class IEDICalculatorService:
    def calculate_mention(self, mention: Dict, bank: Bank, ...) -> Dict:
        # Business logic here
        return result
```

### Controllers (API Layer)

**Created (1 controller)**:
- `AnalysisController` - Flask blueprint with 5 endpoints

**Pattern**:
```python
@analysis_bp.route("/", methods=["POST"])
def create_analysis():
    result = analysis_service.create_analysis(...)
    return jsonify({"success": True, "data": result}), 201
```

### Models (Data Layer)

**Created (7 models)**:
- `Bank` - Banks with variations
- `RelevantMediaOutlet` - Relevant media outlets
- `NicheMediaOutlet` - Niche media outlets  
- `Analysis` - Analysis metadata
- `BankPeriod` - Custom periods per bank
- `Mention` - Individual mentions
- `IEDIResult` - Aggregated IEDI results

### Enums & Constants

**Enums**:
- `Sentiment` - POSITIVE, NEGATIVE, NEUTRAL
- `ReachGroup` - A, B, C, D

**Constants**:
- `TITLE_WEIGHT = 100`
- `SUBTITLE_WEIGHT = 80`
- `RELEVANT_OUTLET_WEIGHT = 95`
- `NICHE_OUTLET_WEIGHT = 54`
- `REACH_GROUP_WEIGHTS = {"A": 91, "B": 85, "C": 24, "D": 20}`
- `REACH_GROUP_THRESHOLDS = {"A": 29000000, "B": 11000000, "C": 500000}`

## Code Style

✅ **English only** (backend)  
✅ **No comments** (self-documenting code)  
✅ **Alphabetical imports**  
✅ **1 line spacing** between methods  
✅ **Type hints** everywhere  

## Integration with Existing System

The new architecture is ready to be integrated with the existing `app.py`. Two approaches:

### Option 1: Gradual Migration
Keep existing routes, gradually replace with new services:
```python
# Old
@app.route('/api/bancos', methods=['GET'])
def get_bancos():
    bancos = db.get_bancos()
    return jsonify(bancos)

# New
@app.route('/api/bancos', methods=['GET'])
def get_bancos():
    bancos = bank_service.get_all_active()
    return jsonify({"success": True, "data": bancos})
```

### Option 2: Clean Rewrite
Replace `app.py` entirely with new structure:
```python
from flask import Flask
from app.controllers.analysis_controller import analysis_bp

app = Flask(__name__)
app.register_blueprint(analysis_bp)
```

## Next Steps

1. **Choose migration strategy** (gradual vs clean rewrite)
2. **Set up BigQuery credentials** (GOOGLE_APPLICATION_CREDENTIALS)
3. **Create BigQuery dataset** (`iedi` schema)
4. **Run table creation** (use models to generate DDL)
5. **Seed initial data** (banks, media outlets)
6. **Test endpoints** (Postman/curl)
7. **Deploy**

## Environment Variables

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GCP_PROJECT_ID=your-project-id
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
PORT=5000
```

## API Endpoints

### Analysis
- `POST /api/analysis/` - Create analysis
- `GET /api/analysis/` - List all analyses
- `GET /api/analysis/<id>` - Get analysis results
- `POST /api/analysis/<id>/process` - Process mentions
- `GET /api/analysis/banks` - Get active banks

### Frontend Routes
- `GET /` - Dashboard
- `GET /analises` - Analysis list
- `GET /criar-analise` - Create analysis form
- `GET /analise/<id>` - Analysis details

## Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
export GCP_PROJECT_ID=your-project-id

# Run application
python app.py

# Test endpoint
curl http://localhost:5000/api/analysis/banks
```

## Architecture Benefits

✅ **Separation of concerns** - Each layer has single responsibility  
✅ **Testability** - Easy to unit test each layer  
✅ **Maintainability** - Clear structure, easy to find code  
✅ **Scalability** - Easy to add new features  
✅ **Type safety** - Type hints catch errors early  
✅ **Professional** - Follows industry best practices  

## Files Created

```
app/
├── models/              (7 files)
├── repositories/        (5 files)
├── services/            (4 files)
├── controllers/         (1 file)
├── infra/               (1 file)
├── enums/               (2 files)
├── constants/           (1 file)
└── utils/               (empty)

templates/
└── criar_analise.html   (1 file)

Total: 22 new files
```

## Methodology Implemented

The system implements **IEDI v2.0 methodology**:

✅ Removed spokespersons (weight 20)  
✅ Removed images (weight 20)  
✅ Conditional subtitle verification (snippet vs fullText)  
✅ Dynamic denominators (286-366 for Group A, 280-360 for others)  
✅ Sentiment-based sign application  
✅ Positivity-based balancing  
✅ Reach group classification  

See `METODOLOGIA_IEDI_V2.md` for complete methodology documentation.
