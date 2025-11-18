# Endpoints Necessários para as Telas de Análises

## Visão Geral

Este documento lista todos os endpoints necessários para povoar as telas de criação e listagem de análises, incluindo dados de `Analysis` e `BankPeriod`.

---

## Endpoints Existentes

### ✅ GET `/api/analysis`

**Status**: Implementado (mas precisa correção)

**Descrição**: Lista todas as análises cadastradas

**Problema Atual**:
```python
# app/controllers/analysis_controller.py - Linha 17-18
'period_type': a.period_type,  # ❌ Campo não existe no model
```

**Resposta Esperada** (após correção):
```json
[
    {
        "id": "uuid-1",
        "name": "Análise Outubro 2024",
        "query_name": "OPERAÇÃO BB :: MONITORAMENTO",
        "start_date": "2024-10-01T00:00:00-03:00",
        "end_date": "2024-10-31T23:59:59-03:00",
        "custom_period": false,
        "status": "completed",
        "created_at": "2024-11-01T10:00:00-03:00",
        "updated_at": "2024-11-01T15:30:00-03:00",
        "bank_count": 1
    }
]
```

**Correção Necessária**:
```python
@analysis_bp.route("/api", methods=['GET'])
def list_analyses():
    analyses = AnalysisRepository.find_all()
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'query_name': a.query_name,
        'start_date': a.start_date.isoformat() if a.start_date else None,
        'end_date': a.end_date.isoformat() if a.end_date else None,
        'custom_period': a.custom_period,
        'status': a.status,
        'created_at': a.created_at.isoformat() if a.created_at else None,
        'updated_at': a.updated_at.isoformat() if a.updated_at else None,
        'bank_count': len(BankPeriodRepository.find_by_analysis(a.id))
    } for a in analyses])
```

---

### ✅ GET `/api/analysis/<analysis_id>`

**Status**: Implementado (mas precisa correção e expansão)

**Descrição**: Retorna detalhes de uma análise específica

**Problema Atual**:
```python
# app/controllers/analysis_controller.py - Linha 34-35
'period_type': analysis.period_type,  # ❌ Campo não existe no model
```

**Resposta Esperada** (após correção):
```json
{
    "id": "uuid-1",
    "name": "Análise Outubro 2024",
    "query_name": "OPERAÇÃO BB :: MONITORAMENTO",
    "start_date": "2024-10-01T00:00:00-03:00",
    "end_date": "2024-10-31T23:59:59-03:00",
    "custom_period": false,
    "status": "completed",
    "created_at": "2024-11-01T10:00:00-03:00",
    "updated_at": "2024-11-01T15:30:00-03:00",
    "bank_periods": [
        {
            "id": "uuid-2",
            "bank_id": "uuid-bb",
            "category_detail": "Banco do Brasil",
            "start_date": "2024-10-01T00:00:00-03:00",
            "end_date": "2024-10-31T23:59:59-03:00",
            "total_mentions": 1234
        }
    ],
    "results": [
        {
            "id": "uuid-3",
            "bank_id": "uuid-bb",
            "total_volume": 1234,
            "positive_volume": 800,
            "negative_volume": 200,
            "neutral_volume": 234,
            "average_iedi": 7.5,
            "final_iedi": 6.8,
            "positivity_rate": 64.8,
            "negativity_rate": 16.2
        }
    ]
}
```

**Correção Necessária**:
```python
@analysis_bp.route("/api/<string:analysis_id>", methods=['GET'])
def get_analysis(analysis_id):
    analysis = AnalysisRepository.find_by_id(analysis_id)
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    bank_periods = BankPeriodRepository.find_by_analysis(analysis_id)
    results = IEDIResultRepository.find_by_analysis(analysis_id)
    
    return jsonify({
        'id': analysis.id,
        'name': analysis.name,
        'query_name': analysis.query_name,
        'start_date': analysis.start_date.isoformat() if analysis.start_date else None,
        'end_date': analysis.end_date.isoformat() if analysis.end_date else None,
        'custom_period': analysis.custom_period,
        'status': analysis.status,
        'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
        'updated_at': analysis.updated_at.isoformat() if analysis.updated_at else None,
        'bank_periods': [{
            'id': bp.id,
            'bank_id': bp.bank_id,
            'category_detail': bp.category_detail,
            'start_date': bp.start_date.isoformat() if bp.start_date else None,
            'end_date': bp.end_date.isoformat() if bp.end_date else None,
            'total_mentions': bp.total_mentions
        } for bp in bank_periods],
        'results': [{
            'id': r.id,
            'bank_id': r.bank_id,
            'total_volume': r.total_volume,
            'positive_volume': r.positive_volume,
            'negative_volume': r.negative_volume,
            'neutral_volume': r.neutral_volume,
            'average_iedi': r.average_iedi,
            'final_iedi': r.final_iedi,
            'positivity_rate': r.positivity_rate,
            'negativity_rate': r.negativity_rate
        } for r in results]
    })
```

---

### ✅ GET `/api/analysis/<analysis_id>/mentions`

**Status**: Implementado

**Descrição**: Lista mentions de uma análise (opcionalmente filtrado por bank_id)

**Query Parameters**:
- `bank_id` (opcional): Filtrar por banco específico

**Resposta**:
```json
[
    {
        "analysis_id": "uuid-1",
        "mention_id": "uuid-m1",
        "bank_id": "uuid-bb",
        "iedi_score": 0.75,
        "iedi_normalized": 8.75,
        "numerator": 285,
        "denominator": 380,
        "title_verified": 1,
        "subtitle_verified": 1,
        "relevant_outlet_verified": 1,
        "niche_outlet_verified": 0,
        "created_at": "2024-11-01T15:30:00-03:00"
    }
]
```

**Uso**: Não usado diretamente nas telas propostas, mas útil para debug

---

## Endpoints Faltando (Precisam ser Criados)

### ❌ POST `/api/analysis`

**Status**: **NÃO IMPLEMENTADO**

**Descrição**: Cria uma nova análise com períodos por banco

**Request Body**:
```json
{
    "name": "Análise Outubro 2024",
    "query_name": "OPERAÇÃO BB :: MONITORAMENTO",
    "custom_period": false,
    "start_date": "2024-10-01T00:00:00",
    "end_date": "2024-10-31T23:59:59",
    "bank_periods": [
        {
            "bank_id": "uuid-bb",
            "category_detail": "Banco do Brasil",
            "start_date": "2024-10-01T00:00:00",
            "end_date": "2024-10-31T23:59:59"
        }
    ]
}
```

**Resposta**:
```json
{
    "id": "uuid-1",
    "name": "Análise Outubro 2024",
    "query_name": "OPERAÇÃO BB :: MONITORAMENTO",
    "start_date": "2024-10-01T00:00:00-03:00",
    "end_date": "2024-10-31T23:59:59-03:00",
    "custom_period": false,
    "status": "pending",
    "created_at": "2024-11-01T10:00:00-03:00",
    "updated_at": "2024-11-01T10:00:00-03:00"
}
```

**Implementação Sugerida**:
```python
@analysis_bp.route("/api", methods=['POST'])
def create_analysis():
    data = request.get_json()
    
    # Validar campos obrigatórios
    required_fields = ['name', 'query_name', 'bank_periods']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo obrigatório: {field}'}), 400
    
    # Criar análise
    analysis = AnalysisRepository.create(
        name=data['name'],
        query_name=data['query_name'],
        custom_period=data.get('custom_period', False),
        start_date=datetime.fromisoformat(data.get('start_date')),
        end_date=datetime.fromisoformat(data.get('end_date'))
    )
    
    # Criar períodos por banco
    for bp_data in data['bank_periods']:
        BankPeriodRepository.create(
            analysis_id=analysis.id,
            bank_id=bp_data['bank_id'],
            category_detail=bp_data['category_detail'],
            start_date=datetime.fromisoformat(bp_data['start_date']),
            end_date=datetime.fromisoformat(bp_data['end_date'])
        )
    
    return jsonify(analysis.to_dict()), 201
```

---

### ❌ DELETE `/api/analysis/<analysis_id>`

**Status**: **NÃO IMPLEMENTADO**

**Descrição**: Exclui uma análise e todos os dados relacionados

**Resposta**:
```json
{
    "success": true,
    "message": "Análise excluída com sucesso"
}
```

**Implementação Sugerida**:
```python
@analysis_bp.route("/api/<string:analysis_id>", methods=['DELETE'])
def delete_analysis(analysis_id):
    analysis = AnalysisRepository.find_by_id(analysis_id)
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    # Excluir em cascata (ordem importante!)
    # 1. AnalysisMention
    AnalysisMentionRepository.delete_by_analysis(analysis_id)
    
    # 2. IEDIResult
    IEDIResultRepository.delete_by_analysis(analysis_id)
    
    # 3. BankPeriod
    BankPeriodRepository.delete_by_analysis(analysis_id)
    
    # 4. Analysis
    AnalysisRepository.delete(analysis_id)
    
    return jsonify({
        'success': True,
        'message': 'Análise excluída com sucesso'
    }), 200
```

**Nota**: Precisa implementar métodos `delete_by_analysis()` nos repositories

---

### ❌ GET `/api/banks`

**Status**: **NÃO IMPLEMENTADO**

**Descrição**: Lista todos os bancos cadastrados (para popular dropdown)

**Resposta**:
```json
[
    {
        "id": "uuid-bb",
        "name": "Banco do Brasil",
        "variations": ["BB", "Banco do Brasil S.A."]
    },
    {
        "id": "uuid-itau",
        "name": "Itaú",
        "variations": ["Itaú Unibanco", "Banco Itaú"]
    }
]
```

**Implementação Sugerida**:
```python
# app/controllers/bank_controller.py

@bank_bp.route("/api", methods=['GET'])
def list_banks():
    banks = BankRepository.find_all()
    return jsonify([{
        'id': b.id,
        'name': b.name.value,
        'variations': b.variations
    } for b in banks])
```

---

## Endpoints Opcionais (Melhorias Futuras)

### 🔄 POST `/api/analysis/<analysis_id>/process`

**Descrição**: Inicia processamento de uma análise

**Request Body**:
```json
{
    "force": false
}
```

**Resposta**:
```json
{
    "success": true,
    "message": "Processamento iniciado",
    "job_id": "uuid-job-1"
}
```

**Uso**: Disparar processamento assíncrono via IEDIOrchestrator

---

### 🔄 GET `/api/analysis/<analysis_id>/status`

**Descrição**: Retorna status de processamento em tempo real

**Resposta**:
```json
{
    "status": "processing",
    "progress": 45.5,
    "current_step": "Calculando IEDI",
    "mentions_processed": 560,
    "total_mentions": 1234
}
```

**Uso**: Polling para atualizar UI durante processamento

---

### 🔄 PATCH `/api/analysis/<analysis_id>`

**Descrição**: Atualiza campos de uma análise

**Request Body**:
```json
{
    "name": "Novo Nome",
    "status": "completed"
}
```

**Resposta**:
```json
{
    "id": "uuid-1",
    "name": "Novo Nome",
    "status": "completed",
    "updated_at": "2024-11-01T16:00:00-03:00"
}
```

---

## Resumo de Endpoints Necessários

### Implementados (com correções)
| Método | Endpoint | Status | Ação Necessária |
|--------|----------|--------|-----------------|
| GET | `/api/analysis` | ✅ Implementado | Corrigir `period_type` → campos corretos |
| GET | `/api/analysis/<id>` | ✅ Implementado | Corrigir `period_type` + adicionar `bank_periods` |
| GET | `/api/analysis/<id>/mentions` | ✅ Implementado | Nenhuma |

### Faltando (precisam ser criados)
| Método | Endpoint | Prioridade | Descrição |
|--------|----------|------------|-----------|
| POST | `/api/analysis` | 🔴 **ALTA** | Criar análise + períodos |
| DELETE | `/api/analysis/<id>` | 🔴 **ALTA** | Excluir análise |
| GET | `/api/banks` | 🔴 **ALTA** | Listar bancos para dropdown |
| POST | `/api/analysis/<id>/process` | 🟡 Média | Iniciar processamento |
| GET | `/api/analysis/<id>/status` | 🟡 Média | Status de processamento |
| PATCH | `/api/analysis/<id>` | 🟢 Baixa | Atualizar análise |

---

## Alterações Necessárias nos Repositories

### AnalysisRepository

**Método `create()` precisa aceitar novos campos**:
```python
@staticmethod
def create(name: str, query_name: str, custom_period: bool, 
           start_date: datetime, end_date: datetime) -> Analysis:
    with get_session() as session:
        analysis = Analysis(
            id=generate_uuid(),
            name=name,
            query_name=query_name,
            start_date=start_date,
            end_date=end_date,
            custom_period=custom_period,
            status='pending',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(analysis)
        session.commit()
        session.refresh(analysis)
        return analysis
```

**Adicionar método `delete()`**:
```python
@staticmethod
def delete(analysis_id: str) -> bool:
    with get_session() as session:
        analysis = session.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            session.delete(analysis)
            session.commit()
            return True
        return False
```

### BankPeriodRepository

**Adicionar método `delete_by_analysis()`**:
```python
@staticmethod
def delete_by_analysis(analysis_id: str) -> int:
    with get_session() as session:
        count = session.query(BankPeriod).filter(
            BankPeriod.analysis_id == analysis_id
        ).delete()
        session.commit()
        return count
```

### IEDIResultRepository

**Adicionar método `delete_by_analysis()`**:
```python
@staticmethod
def delete_by_analysis(analysis_id: str) -> int:
    with get_session() as session:
        count = session.query(IEDIResult).filter(
            IEDIResult.analysis_id == analysis_id
        ).delete()
        session.commit()
        return count
```

### AnalysisMentionRepository

**Adicionar método `delete_by_analysis()`**:
```python
@staticmethod
def delete_by_analysis(analysis_id: str) -> int:
    with get_session() as session:
        count = session.query(AnalysisMention).filter(
            AnalysisMention.analysis_id == analysis_id
        ).delete()
        session.commit()
        return count
```

---

## Ordem de Implementação Recomendada

1. **Corrigir endpoints existentes** (GET `/api/analysis` e GET `/api/analysis/<id>`)
2. **Implementar GET `/api/banks`** (necessário para dropdown)
3. **Atualizar `AnalysisRepository.create()`** (aceitar novos campos)
4. **Implementar POST `/api/analysis`** (criação de análises)
5. **Implementar métodos `delete_by_analysis()`** nos repositories
6. **Implementar DELETE `/api/analysis/<id>`** (exclusão de análises)
7. **Testar fluxo completo** (criar → listar → ver detalhes → excluir)

---

## Exemplo de Fluxo Completo

### 1. Usuário abre tela de análises
```
GET /api/banks → Carrega lista de bancos para dropdown
GET /api/analysis → Carrega lista de análises
```

### 2. Usuário cria nova análise
```
POST /api/analysis
Body: {
    "name": "Análise Outubro 2024",
    "query_name": "OPERAÇÃO BB :: MONITORAMENTO",
    "custom_period": false,
    "start_date": "2024-10-01T00:00:00",
    "end_date": "2024-10-31T23:59:59",
    "bank_periods": [...]
}
```

### 3. Usuário visualiza detalhes
```
GET /api/analysis/uuid-1 → Retorna análise + bank_periods + results
```

### 4. Usuário exclui análise
```
DELETE /api/analysis/uuid-1 → Exclui análise e dados relacionados
```

---

## Conclusão

Para as telas funcionarem completamente, são necessários:

✅ **3 endpoints corrigidos** (GET `/api/analysis`, GET `/api/analysis/<id>`, GET `/api/analysis/<id>/mentions`)
❌ **3 endpoints novos** (POST `/api/analysis`, DELETE `/api/analysis/<id>`, GET `/api/banks`)
🔧 **4 métodos novos** nos repositories (`delete()`, `delete_by_analysis()` × 3)

**Prioridade ALTA**: POST `/api/analysis`, DELETE `/api/analysis/<id>`, GET `/api/banks`
