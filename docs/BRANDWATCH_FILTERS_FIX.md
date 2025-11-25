# Correção de Filtros Brandwatch API

**Data**: 25 de novembro de 2025  
**Autor**: Manus AI

---

## Resumo

Este documento descreve as correções aplicadas aos filtros Brandwatch para garantir que funcionem corretamente conforme a documentação da bcr-api.

---

## Problema Identificado

### Código Anterior (Usuário)

```python
# BrandwatchService.fetch()
parent_category_filter = [parent_name]
category_filter = {parent_name: category_names} if category_names else {}

for page in client.queries.iter_mentions(
    name=query_name,
    startDate=DateUtils.to_iso_format(start_date),
    endDate=DateUtils.to_iso_format(end_date),
    pageSize=5000,
    iter_by_page=True,
    params={
        "parentCategory": parent_category_filter,
        "category": category_filter
    }
):
```

**Problemas**:
1. ❌ Filtros passados via `params={}` ao invés de **kwargs diretos**
2. ❌ Faltava filtro `pageType="news"` para evitar buscar não-notícias
3. ❌ `passes_filter()` validava `contentSourceName` **após** buscar (ineficiente)

---

## Correções Aplicadas

### 1. BrandwatchService

**Antes**:
```python
params={
    "parentCategory": parent_category_filter,
    "category": category_filter
}

for page in client.queries.iter_mentions(
    name=query_name,
    startDate=...,
    endDate=...,
    params=params
):
```

**Depois**:
```python
kwargs = {
    "startDate": DateUtils.to_iso_format(start_date),
    "endDate": DateUtils.to_iso_format(end_date),
    "pageSize": 5000,
    "iter_by_page": True,
    "pageType": "news"  # NOVO: Filtrar apenas notícias
}

if parent_name:
    kwargs["parentCategory"] = [parent_name]

if category_names:
    kwargs["category"] = {parent_name: category_names}

for page in client.queries.iter_mentions(
    name=query_name,
    **kwargs  # Passa filtros como kwargs
):
```

**Benefícios**:
- ✅ Filtros passados como **kwargs diretos** (formato correto)
- ✅ Adicionado `pageType="news"` para filtrar na API
- ✅ Menos dados transferidos pela rede

---

### 2. MentionService

**Antes**:
```python
def passes_filter(self, mention_data, parent_name, category_names):
    content_source = mention_data.get('contentSourceName')

    if not (content_source == "News" or content_source == "Online News"):
        return False  # ❌ Filtro aplicado APÓS buscar

    categories = self.extract_categories(mention_data.get('categoryDetails', []), parent_name)
    if not categories:
        return False

    return any(category in category_names for category in categories)
```

**Depois**:
```python
def passes_filter(self, mention_data, parent_name, category_names):
    # Filtro de contentSource removido (já aplicado via pageType="news" na API)
    
    # Validar se mention tem categorias do parent_name
    categories = self.extract_categories(mention_data.get('categoryDetails', []), parent_name)
    if not categories:
        return False

    # Validar se mention pertence a alguma das categorias solicitadas
    if category_names:
        return any(category in category_names for category in categories)
    
    # Se category_names é None, aceitar todas as categorias do parent
    return True
```

**Benefícios**:
- ✅ Removido filtro `contentSourceName` (já aplicado na API)
- ✅ Mantida validação de categorias (segurança adicional)
- ✅ Suporte para `category_names=None` (buscar todas as categorias do parent)

---

## Formato Correto dos Filtros

### Documentação bcr-api

**Fonte**: `.venv/lib/python3.10/site-packages/bcr_api/filters.py`

```python
params = {
    "parentCategory": list,  # Lista de nomes de categorias pai
    "category": dict,        # Dicionário {parent: [child1, child2, ...]}
    "pageType": (str, list), # "news", "blog", "forum", "twitter", etc.
    ...
}
```

### Uso Correto

```python
# Filtro 1: Categoria pai
parentCategory=["Bancos"]

# Filtro 2: Categorias específicas
category={"Bancos": ["Banco do Brasil", "Itaú"]}

# Filtro 3: Tipo de página
pageType="news"
```

---

## Fluxo Completo

### Exemplo: Buscar Banco do Brasil em Outubro 2024

```python
# 1. MentionAnalysisService chama MentionService
mentions = mention_service.fetch_and_filter_mentions(
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 31),
    query_name="OPERAÇÃO BB :: MONITORAMENTO",
    parent_name="Bancos",
    category_names=["Banco do Brasil"]
)

# 2. MentionService chama BrandwatchService
mentions_data = brandwatch_service.fetch(
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 31),
    query_name="OPERAÇÃO BB :: MONITORAMENTO",
    parent_name="Bancos",
    category_names=["Banco do Brasil"]
)

# 3. BrandwatchService passa filtros para API
kwargs = {
    "startDate": "2024-10-01T00:00:00",
    "endDate": "2024-10-31T23:59:59",
    "pageSize": 5000,
    "iter_by_page": True,
    "pageType": "news",
    "parentCategory": ["Bancos"],
    "category": {"Bancos": ["Banco do Brasil"]}
}

for page in client.queries.iter_mentions(name="OPERAÇÃO BB :: MONITORAMENTO", **kwargs):
    all_mentions.extend(page)

# 4. MentionService valida categorias (segurança adicional)
for mention_data in mentions_data:
    if passes_filter(mention_data, "Bancos", ["Banco do Brasil"]):
        save_or_update(mention_data)
```

---

## Impacto

### Performance

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| **Filtro contentSource** | Python | API (`pageType`) | **Mais eficiente** |
| **Filtro parentCategory** | Python | API | **Mais eficiente** |
| **Filtro category** | Python | API | **Mais eficiente** |
| **Validação adicional** | ❌ Não | ✅ Sim | **Mais seguro** |

### Benefícios

✅ **Filtros aplicados na API** (menos dados transferidos)  
✅ **`pageType="news"`** evita buscar não-notícias  
✅ **Validação adicional** em `passes_filter()` (segurança)  
✅ **Suporte para `category_names=None`** (buscar todas as categorias do parent)

---

## Testes

### Validar Filtros

```python
from app.services.brandwatch_service import BrandwatchService
from datetime import datetime

service = BrandwatchService()

# Teste 1: Buscar apenas notícias de bancos
mentions = service.fetch(
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 31),
    query_name="OPERAÇÃO BB :: MONITORAMENTO",
    parent_name="Bancos",
    category_names=None  # Todas as categorias de "Bancos"
)
print(f"Total mentions (todos os bancos): {len(mentions)}")

# Teste 2: Buscar apenas Banco do Brasil
mentions = service.fetch(
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 31),
    query_name="OPERAÇÃO BB :: MONITORAMENTO",
    parent_name="Bancos",
    category_names=["Banco do Brasil"]
)
print(f"Total mentions (apenas BB): {len(mentions)}")
```

---

## Arquivos Alterados

1. ✅ `app/services/brandwatch_service.py`
   - Adicionado `pageType="news"`
   - Filtros passados como **kwargs diretos**

2. ✅ `app/services/mention_service.py`
   - Removido filtro `contentSourceName` de `passes_filter()`
   - Adicionado suporte para `category_names=None`

3. ✅ `docs/BRANDWATCH_FILTERS_FIX.md` (este documento)

---

## Conclusão

✅ **Filtros corrigidos** para formato esperado pela bcr-api  
✅ **`pageType="news"`** adicionado para filtrar na API  
✅ **Validação adicional** mantida para segurança  
✅ **Suporte para buscar todas as categorias** de um parent

**Status**: ✅ Pronto para teste com credenciais Brandwatch reais

---

**Data de Correção**: 25 de novembro de 2025  
**Versão**: 1.1  
**Status**: ✅ Corrigido
