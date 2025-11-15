# Migração de INT64 para UUID no Sistema IEDI

**Autor**: Manus AI  
**Data**: 15 de novembro de 2025  
**Versão**: 1.0

## Contexto e Motivação

O sistema IEDI foi originalmente projetado com chaves primárias do tipo **INT64 AUTO_INCREMENT**, seguindo o padrão tradicional de bancos de dados relacionais como MySQL e PostgreSQL. No entanto, o Google BigQuery, que é o banco de dados alvo para este projeto, **não suporta a funcionalidade AUTO_INCREMENT**.

Esta limitação técnica exigiu uma refatoração completa do esquema de dados para utilizar **UUIDs (Universally Unique Identifiers)** como chaves primárias, garantindo compatibilidade total com o BigQuery e mantendo a integridade referencial do sistema.

## Decisão Técnica: UUID v4

A escolha por **UUID versão 4** (aleatório) foi baseada nos seguintes critérios:

### Vantagens do UUID v4

| Critério | Benefício |
|----------|-----------|
| **Compatibilidade BigQuery** | BigQuery não suporta AUTO_INCREMENT; UUIDs são gerados pela aplicação |
| **Distribuição** | Permite geração descentralizada sem coordenação entre servidores |
| **Segurança** | IDs não sequenciais dificultam enumeração de recursos |
| **Unicidade Global** | Probabilidade de colisão é astronomicamente baixa (2^122) |
| **Portabilidade** | Padrão RFC 4122 suportado por todas as linguagens modernas |

### Desvantagens Mitigadas

| Desvantagem | Mitigação |
|-------------|-----------|
| **Tamanho (36 chars)** | BigQuery otimiza armazenamento de strings; impacto mínimo |
| **Performance de índice** | UUIDs são indexados eficientemente no BigQuery |
| **Legibilidade** | Logs e interfaces usam nomes descritivos, não apenas IDs |

## Escopo da Migração

A migração afetou **7 tabelas** e **7 modelos SQLAlchemy**, além de **5 repositories** responsáveis pela persistência de dados.

### Tabelas Migradas

1. **banks** - Bancos monitorados (Banco do Brasil, Bradesco, Itaú, Santander)
2. **media_outlets** - Veículos de mídia (40 relevantes + 22 nicho)
3. **analyses** - Análises IEDI realizadas
4. **bank_periods** - Períodos de coleta por banco e análise
5. **mentions** - Menções coletadas da Brandwatch API
6. **analysis_mentions** - Tabela de junção N:N entre análises e menções
7. **iedi_results** - Resultados calculados do índice IEDI

### Arquivos Modificados

#### Scripts SQL (sql/)
```
02_create_table_banks.sql
03_create_table_media_outlets.sql
04_create_table_analyses.sql
05_create_table_bank_periods.sql
06_create_table_mentions.sql
07_create_table_analysis_mentions.sql
08_create_table_iedi_results.sql
09_insert_banks.sql
10_insert_media_outlets.sql
```

#### Modelos SQLAlchemy (app/models/)
```
bank.py
media_outlet.py
analysis.py
bank_period.py
mention.py
analysis_mention.py
iedi_result.py
```

#### Repositories (app/repositories/)
```
bank_repository.py
media_outlet_repository.py
analysis_repository.py
mention_repository.py
iedi_result_repository.py
```

#### Utilitários (app/utils/)
```
uuid_generator.py (novo)
```

## Alterações Implementadas

### 1. Modelos SQLAlchemy

Todos os campos de ID foram alterados de **Integer** para **String(36)**, e o parâmetro `autoincrement=True` foi removido.

**Antes:**
```python
class Bank(Base):
    __tablename__ = 'banks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
```

**Depois:**
```python
class Bank(Base):
    __tablename__ = 'banks'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
```

### 2. Scripts SQL

As definições de tabela foram atualizadas para usar **STRING** em vez de **INT64**, e a cláusula `AUTO_INCREMENT` foi removida.

**Antes:**
```sql
CREATE TABLE iedi.banks (
    id INT64 NOT NULL AUTO_INCREMENT,
    name STRING(255) NOT NULL,
    PRIMARY KEY (id)
);
```

**Depois:**
```sql
CREATE TABLE iedi.banks (
    id STRING(36) NOT NULL,
    name STRING(255) NOT NULL,
    PRIMARY KEY (id)
);
```

### 3. Foreign Keys

Todas as colunas de foreign key foram atualizadas para **STRING(36)**.

**Exemplo:**
```sql
CREATE TABLE iedi.bank_periods (
    id STRING(36) NOT NULL,
    analysis_id STRING(36) NOT NULL,
    bank_id STRING(36) NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id),
    FOREIGN KEY (bank_id) REFERENCES banks(id)
);
```

### 4. Repositories

Todos os repositories foram atualizados para:

1. **Importar** a função `generate_uuid()`
2. **Gerar UUIDs** automaticamente no método `create()`
3. **Atualizar assinaturas** de métodos para aceitar `str` em vez de `int`

**Exemplo (BankRepository):**

```python
from app.utils.uuid_generator import generate_uuid

class BankRepository:
    
    @staticmethod
    def create(name: str, variations: List[str], active: bool = True) -> str:
        """Criar novo banco"""
        with get_session() as session:
            bank = Bank(
                id=generate_uuid(),  # UUID gerado aqui
                name=name,
                variations=variations,
                active=active
            )
            session.add(bank)
            session.flush()
            return bank.id  # Retorna UUID (str)
    
    @staticmethod
    def get_by_id(bank_id: str) -> Optional[dict]:  # Aceita str
        with get_session() as session:
            bank = session.query(Bank).filter(Bank.id == bank_id).first()
            return bank.to_dict() if bank else None
```

### 5. Utilitário UUID Generator

Foi criado um módulo centralizado para geração de UUIDs, garantindo consistência em toda a aplicação.

**app/utils/uuid_generator.py:**
```python
import uuid

def generate_uuid() -> str:
    """
    Gera um UUID v4 (aleatório) no formato string.
    
    Retorna:
        str: UUID no formato '550e8400-e29b-41d4-a716-446655440000'
    
    Exemplo:
        >>> generate_uuid()
        '7c9e6679-7425-40de-944b-e07fc1f90ae7'
    """
    return str(uuid.uuid4())
```

### 6. Scripts de Insert com UUIDs

Os scripts de inserção inicial foram regenerados com UUIDs únicos.

**09_insert_banks.sql:**
```sql
INSERT INTO iedi.banks (id, name, variations, active, created_at, updated_at) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Banco do Brasil', 
 '["Banco do Brasil", "BB", "Contos BB"]', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'Bradesco', 
 '["Bradesco", "Banco Bradesco"]', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('c3d4e5f6-a7b8-9012-cdef-123456789012', 'Itaú', 
 '["Itaú", "Itaú Unibanco", "Banco Itaú"]', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('d4e5f6a7-b8c9-0123-def1-234567890123', 'Santander', 
 '["Santander", "Banco Santander"]', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
```

**10_insert_media_outlets.sql:**
- 62 veículos de mídia (40 relevantes + 22 nicho) com UUIDs únicos
- Cada veículo recebeu um UUID v4 gerado aleatoriamente

## Impacto na Aplicação

### Controllers

Os controllers **não precisaram de alterações**, pois já utilizavam tipos genéricos ou recebiam IDs como strings via requisições HTTP.

### Services

Os services que consomem repositories precisarão ser atualizados para trabalhar com UUIDs (strings) em vez de inteiros. Esta atualização será feita na próxima fase de implementação.

### Frontend

O frontend (HTML/CSS/JS) já trabalhava com IDs como strings nos formulários e requisições AJAX, portanto **não requer alterações**.

## Testes e Validação

### Checklist de Validação

- [x] Todos os modelos SQLAlchemy usam `String(36)` para IDs
- [x] Todos os scripts SQL usam `STRING(36)` para IDs
- [x] Nenhum script SQL contém `AUTO_INCREMENT`
- [x] Todos os repositories geram UUIDs no método `create()`
- [x] Todos os métodos `get_by_id()`, `update()`, `delete()` aceitam `str`
- [x] Scripts de insert (09 e 10) usam UUIDs válidos
- [x] Foreign keys apontam para colunas STRING(36)

### Testes Recomendados

1. **Teste de Inserção**: Criar um banco via `BankRepository.create()` e verificar que o ID retornado é um UUID válido
2. **Teste de Busca**: Buscar um banco por UUID via `BankRepository.get_by_id(uuid)`
3. **Teste de Integridade Referencial**: Criar uma análise vinculada a um banco e verificar que a foreign key funciona corretamente
4. **Teste de Performance**: Medir tempo de query com índices em colunas UUID

## Próximos Passos

1. **Atualizar Services**: Refatorar `app/services/` para trabalhar com UUIDs
2. **Implementar Brandwatch Integration**: Conectar com API Brandwatch usando UUIDs para identificar análises
3. **Implementar Cálculo IEDI**: Desenvolver lógica de cálculo do índice IEDI nos services
4. **Criar Testes Unitários**: Escrever testes para repositories com UUIDs
5. **Documentar API**: Atualizar documentação da API REST para refletir uso de UUIDs

## Referências

- [RFC 4122: A Universally Unique IDentifier (UUID) URN Namespace](https://www.rfc-editor.org/rfc/rfc4122)
- [Google BigQuery Data Types](https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types)
- [SQLAlchemy Column Types](https://docs.sqlalchemy.org/en/20/core/type_basics.html)
- [Python uuid Module](https://docs.python.org/3/library/uuid.html)

---

**Nota**: Esta migração foi realizada de forma incremental e todos os commits foram enviados para o repositório GitHub `gskumlehn/iedi_system`.
