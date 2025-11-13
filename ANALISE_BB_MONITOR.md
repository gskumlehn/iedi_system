# Análise da Estrutura bb-monitor

## Arquitetura Identificada

O repositório `bb-monitor` segue uma arquitetura em camadas bem definida:

```
app/
├── constants/          # Constantes e configurações estáticas
├── controllers/        # Camada de apresentação (Flask Blueprints)
├── custom_utils/       # Utilitários customizados
├── enums/             # Enumerações e tipos
├── infra/             # Infraestrutura (DB, APIs externas)
├── interfaces/        # Interfaces e contratos
├── models/            # Modelos SQLAlchemy
├── repositories/      # Camada de acesso a dados
├── services/          # Lógica de negócio
├── static/            # Arquivos estáticos (CSS, JS, imagens)
└── templates/         # Templates HTML
```

## Camadas e Responsabilidades

### 1. **Models** (`app/models/`)
- Define entidades do domínio usando SQLAlchemy ORM
- Mapeia tabelas do BigQuery
- Usa `declarative_base()` do SQLAlchemy
- Especifica schema do BigQuery via `__table_args__`

**Exemplo**:
```python
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text

Base = declarative_base()

class Mention(Base):
    __tablename__ = "mention"
    __table_args__ = {"schema": "bb_monitor"}
    
    alert_id = Column(String(64), nullable=False)
    url = Column(Text, primary_key=True, nullable=False)
```

### 2. **Repositories** (`app/repositories/`)
- Camada de acesso a dados
- Métodos estáticos para operações CRUD
- Usa context manager `get_session()` para transações
- Isola lógica SQL/ORM dos services

**Exemplo**:
```python
from app.models.mention import Mention
from app.infra.bq_sa import get_session

class MentionRepository:
    @staticmethod
    def save(mention: Mention) -> Mention:
        with get_session() as session:
            session.add(mention)
            session.commit()
            return mention
    
    @staticmethod
    def find_by_alert_id(alert_id: str) -> List[Mention]:
        with get_session() as session:
            return session.query(Mention).filter(
                Mention.alert_id == alert_id
            ).all()
```

### 3. **Services** (`app/services/`)
- Lógica de negócio
- Orquestra repositories e infra
- Validações e transformações
- Não acessa diretamente o banco (usa repositories)

**Exemplo**:
```python
from app.repositories.mention_repository import MentionRepository

class MentionService:
    def save(self, alert: Alert) -> List[Mention]:
        # Busca menções existentes
        mentions = MentionRepository.find_by_alert_id(alert.id) or []
        
        # Lógica de negócio
        if len(mentions) == len(alert.urls):
            return mentions
        
        # Processa e salva novas menções
        for mention_data in mentions_data:
            mention = self.create(data)
            saved = MentionRepository.save(mention)
            mentions.append(saved)
        
        return mentions
```

### 4. **Controllers** (`app/controllers/`)
- Camada de apresentação (Flask Blueprints)
- Recebe requisições HTTP
- Valida input
- Chama services
- Retorna respostas JSON ou renderiza templates

**Exemplo**:
```python
from flask import Blueprint, request, jsonify
from app.services.ingestion_service import IngestionService

ingestion_bp = Blueprint("ingestion", __name__)
ingestion_service = IngestionService()

@ingestion_bp.route("/ingest", methods=["POST"])
def ingest():
    try:
        row = request.json.get("row")
        result = ingestion_service.ingest(start_row, end_row)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 5. **Infra** (`app/infra/`)
- Configuração de infraestrutura
- Conexão com BigQuery via SQLAlchemy
- Clientes de APIs externas (Brandwatch, Email, Sheets)
- Gerenciamento de sessões e engines

**Exemplo (bq_sa.py)**:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is not None:
        return _engine
    
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project = os.getenv("BQ_PROJECT")
    conn_str = f"bigquery://{project}"
    
    _engine = create_engine(
        conn_str,
        pool_pre_ping=True,
        credentials_path=credentials_path
    )
    return _engine

@contextmanager
def get_session():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
```

### 6. **Enums** (`app/enums/`)
- Enumerações de tipos
- Constantes de domínio
- Facilita validação e type hints

### 7. **Constants** (`app/constants/`)
- Constantes globais
- Mensagens de erro
- Configurações estáticas

### 8. **Custom Utils** (`app/custom_utils/`)
- Funções utilitárias
- Helpers reutilizáveis
- Formatação, conversão, etc.

## Fluxo de Dados

```
HTTP Request
    ↓
Controller (Blueprint)
    ↓
Service (Lógica de Negócio)
    ↓
Repository (Acesso a Dados)
    ↓
Model (SQLAlchemy ORM)
    ↓
BigQuery (via sqlalchemy-bigquery)
```

## Dependências Principais

```
sqlalchemy==1.4.49
sqlalchemy-bigquery==1.10.0
google-cloud-bigquery==3.25.0
google-cloud-bigquery-storage==2.24.0
Flask==3.0.0
```

## Vantagens da Arquitetura

1. **Separação de Responsabilidades**: Cada camada tem função clara
2. **Testabilidade**: Services e repositories podem ser testados isoladamente
3. **Manutenibilidade**: Mudanças em uma camada não afetam outras
4. **Escalabilidade**: Fácil adicionar novos recursos
5. **Reutilização**: Services e repositories podem ser usados por múltiplos controllers
6. **Type Safety**: Uso de models SQLAlchemy garante tipagem
7. **Transaction Management**: Context manager garante commits/rollbacks automáticos

## Aplicação no Sistema IEDI

Vamos replicar essa estrutura no sistema IEDI:

- **Models**: Banco, PortaVoz, VeiculoRelevante, VeiculoNicho, Analise, Mencao, ResultadoIEDI
- **Repositories**: Camada de acesso ao BigQuery
- **Services**: IEDICalculatorService, BrandwatchService, AnaliseService
- **Controllers**: Blueprints Flask para cada funcionalidade
- **Infra**: Conexão BigQuery, cliente Brandwatch

Isso trará:
- ✅ Código mais organizado e profissional
- ✅ Melhor separação de responsabilidades
- ✅ Facilidade de testes
- ✅ Escalabilidade para BigQuery
- ✅ Padrão consistente com bb-monitor
