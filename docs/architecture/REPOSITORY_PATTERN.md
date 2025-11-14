# Repository Pattern

The Repository Pattern mediates between the domain and data mapping layers, acting like an in-memory collection of domain objects.

## Purpose

- **Decouple** business logic from data access logic
- **Centralize** data access code
- **Testability** through easy mocking
- **Maintainability** by isolating database changes

## Basic Structure

```python
# app/repositories/product_repository.py
from app.infra.database import get_session
from app.models.product import Product
from typing import List, Optional

class ProductRepository:
    
    @staticmethod
    def list_all(active_only: bool = False) -> List[dict]:
        """List all products"""
        with get_session() as session:
            query = session.query(Product)
            if active_only:
                query = query.filter(Product.active == True)
            products = query.order_by(Product.name).all()
            return [p.to_dict() for p in products]
    
    @staticmethod
    def find_by_id(product_id: int) -> Optional[dict]:
        """Find product by ID"""
        with get_session() as session:
            product = session.query(Product).filter_by(id=product_id).first()
            return product.to_dict() if product else None
    
    @staticmethod
    def create(name: str, price: float, active: bool = True) -> int:
        """Create new product"""
        with get_session() as session:
            product = Product(name=name, price=price, active=active)
            session.add(product)
            session.flush()
            return product.id
    
    @staticmethod
    def update(product_id: int, name: str, price: float, active: bool) -> None:
        """Update existing product"""
        with get_session() as session:
            product = session.query(Product).filter_by(id=product_id).first()
            if product:
                product.name = name
                product.price = price
                product.active = active
    
    @staticmethod
    def delete(product_id: int) -> None:
        """Delete product"""
        with get_session() as session:
            product = session.query(Product).filter_by(id=product_id).first()
            if product:
                session.delete(product)
```

## Why Static Methods?

Repositories in this architecture use static methods because:

1. **No instance state needed**: Repositories don't maintain state between calls
2. **Simpler usage**: No need to instantiate repository objects
3. **Clear intent**: Static methods signal that the class is a namespace for related functions

```python
# ✅ Good: Static methods
products = ProductRepository.list_all()

# ❌ Unnecessary: Instance methods
repo = ProductRepository()
products = repo.list_all()
```

## Return Types

### Return Dictionaries, Not ORM Objects

```python
# ✅ Good: Return dictionaries
@staticmethod
def find_by_id(product_id: int) -> Optional[dict]:
    with get_session() as session:
        product = session.query(Product).filter_by(id=product_id).first()
        return product.to_dict() if product else None

# ❌ Bad: Return ORM objects
@staticmethod
def find_by_id(product_id: int) -> Optional[Product]:
    with get_session() as session:
        product = session.query(Product).filter_by(id=product_id).first()
        return product  # Session closed, object detached!
```

### Why Dictionaries?

1. **Session independence**: Dictionaries don't require active database sessions
2. **Serialization**: Easy to convert to JSON for APIs
3. **Decoupling**: Controllers don't depend on ORM models
4. **Flexibility**: Can return custom shapes without modifying models

## Model to_dict() Method

Every model should implement `to_dict()`:

```python
# app/models/product.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

## Session Management

### Context Manager Pattern

Always use context managers for sessions:

```python
# ✅ Good: Context manager
with get_session() as session:
    product = session.query(Product).first()
    return product.to_dict()

# ❌ Bad: Manual session management
session = get_session()
product = session.query(Product).first()
return product.to_dict()  # Session never closed!
```

### Database Infrastructure

```python
# app/infra/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

_engine = None
_session_maker = None

def get_engine():
    """Create SQLAlchemy engine"""
    global _engine
    if _engine is None:
        db_url = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
        _engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
    return _engine

def get_session_maker():
    """Get sessionmaker"""
    global _session_maker
    if _session_maker is None:
        engine = get_engine()
        _session_maker = sessionmaker(bind=engine)
    return _session_maker

@contextmanager
def get_session():
    """Context manager for database session"""
    SessionMaker = get_session_maker()
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

## Common Repository Methods

### CRUD Operations

```python
class Repository:
    
    @staticmethod
    def list_all() -> List[dict]:
        """List all records"""
        pass
    
    @staticmethod
    def find_by_id(id: int) -> Optional[dict]:
        """Find record by ID"""
        pass
    
    @staticmethod
    def create(**kwargs) -> int:
        """Create new record, return ID"""
        pass
    
    @staticmethod
    def update(id: int, **kwargs) -> None:
        """Update existing record"""
        pass
    
    @staticmethod
    def delete(id: int) -> None:
        """Delete record"""
        pass
```

### Query Methods

```python
class ProductRepository:
    
    @staticmethod
    def find_by_name(name: str) -> Optional[dict]:
        """Find product by exact name"""
        with get_session() as session:
            product = session.query(Product).filter_by(name=name).first()
            return product.to_dict() if product else None
    
    @staticmethod
    def search_by_name(query: str) -> List[dict]:
        """Search products by name (partial match)"""
        with get_session() as session:
            products = session.query(Product).filter(
                Product.name.ilike(f"%{query}%")
            ).all()
            return [p.to_dict() for p in products]
    
    @staticmethod
    def find_by_price_range(min_price: float, max_price: float) -> List[dict]:
        """Find products within price range"""
        with get_session() as session:
            products = session.query(Product).filter(
                Product.price >= min_price,
                Product.price <= max_price
            ).all()
            return [p.to_dict() for p in products]
    
    @staticmethod
    def count_active() -> int:
        """Count active products"""
        with get_session() as session:
            return session.query(Product).filter(Product.active == True).count()
```

## Error Handling

### Repository Level

```python
from sqlalchemy.exc import IntegrityError

class ProductRepository:
    
    @staticmethod
    def create(name: str, price: float) -> int:
        """Create product with error handling"""
        try:
            with get_session() as session:
                product = Product(name=name, price=price)
                session.add(product)
                session.flush()
                return product.id
        except IntegrityError as e:
            if 'Duplicate entry' in str(e):
                raise ValueError(f"Product '{name}' already exists")
            raise ValueError(f"Database constraint violation: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to create product: {e}")
```

### Controller Level

```python
@product_bp.route("/api", methods=['POST'])
def create_product():
    try:
        data = request.json
        product_id = ProductRepository.create(
            name=data['name'],
            price=data['price']
        )
        return jsonify({'id': product_id, 'success': True})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
```

## Pagination

```python
class ProductRepository:
    
    @staticmethod
    def list_paginated(page: int = 1, per_page: int = 20) -> dict:
        """List products with pagination"""
        with get_session() as session:
            query = session.query(Product).filter(Product.active == True)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            products = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'items': [p.to_dict() for p in products],
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
```

## Filtering and Sorting

```python
class ProductRepository:
    
    @staticmethod
    def list_with_filters(
        active: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = 'name',
        sort_order: str = 'asc'
    ) -> List[dict]:
        """List products with dynamic filters"""
        with get_session() as session:
            query = session.query(Product)
            
            # Apply filters
            if active is not None:
                query = query.filter(Product.active == active)
            if min_price is not None:
                query = query.filter(Product.price >= min_price)
            if max_price is not None:
                query = query.filter(Product.price <= max_price)
            
            # Apply sorting
            sort_column = getattr(Product, sort_by, Product.name)
            if sort_order == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
            
            products = query.all()
            return [p.to_dict() for p in products]
```

## Relationships

### One-to-Many

```python
# Models
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="products")
    
    def to_dict(self, include_category=False):
        data = {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id
        }
        if include_category and self.category:
            data['category'] = {
                'id': self.category.id,
                'name': self.category.name
            }
        return data

# Repository
class ProductRepository:
    
    @staticmethod
    def find_with_category(product_id: int) -> Optional[dict]:
        """Find product with category details"""
        with get_session() as session:
            product = session.query(Product).filter_by(id=product_id).first()
            return product.to_dict(include_category=True) if product else None
    
    @staticmethod
    def list_by_category(category_id: int) -> List[dict]:
        """List products in a category"""
        with get_session() as session:
            products = session.query(Product).filter_by(category_id=category_id).all()
            return [p.to_dict() for p in products]
```

## Testing Repositories

### Unit Test with Mock

```python
from unittest.mock import patch, MagicMock

def test_list_all():
    # Mock session and query
    mock_product = MagicMock()
    mock_product.to_dict.return_value = {'id': 1, 'name': 'Test'}
    
    with patch('app.repositories.product_repository.get_session') as mock_session:
        mock_session.return_value.__enter__.return_value.query.return_value.all.return_value = [mock_product]
        
        # Test
        products = ProductRepository.list_all()
        
        # Assert
        assert len(products) == 1
        assert products[0]['name'] == 'Test'
```

### Integration Test with Real Database

```python
def test_create_and_find(db_session):
    # Create
    product_id = ProductRepository.create(
        name='Test Product',
        price=99.99
    )
    
    # Find
    product = ProductRepository.find_by_id(product_id)
    
    # Assert
    assert product is not None
    assert product['name'] == 'Test Product'
    assert product['price'] == 99.99
```

## Best Practices

### 1. One Repository per Model

```
✅ Good:
- ProductRepository → Product model
- CategoryRepository → Category model
- OrderRepository → Order model

❌ Bad:
- DatabaseRepository → All models
```

### 2. Keep Repositories Focused

```python
# ✅ Good: Data access only
class ProductRepository:
    @staticmethod
    def create(name: str, price: float) -> int:
        with get_session() as session:
            product = Product(name=name, price=price)
            session.add(product)
            session.flush()
            return product.id

# ❌ Bad: Business logic in repository
class ProductRepository:
    @staticmethod
    def create(name: str, price: float) -> int:
        # Validation logic (should be in service/controller)
        if price < 0:
            raise ValueError("Price must be positive")
        if len(name) < 3:
            raise ValueError("Name too short")
        
        with get_session() as session:
            product = Product(name=name, price=price)
            session.add(product)
            session.flush()
            return product.id
```

### 3. Use Type Hints

```python
from typing import List, Optional, Dict

class ProductRepository:
    @staticmethod
    def list_all() -> List[Dict]:
        pass
    
    @staticmethod
    def find_by_id(product_id: int) -> Optional[Dict]:
        pass
```

### 4. Document Complex Queries

```python
@staticmethod
def get_top_selling_products(limit: int = 10) -> List[dict]:
    """
    Get top selling products based on order count.
    
    Args:
        limit: Maximum number of products to return
        
    Returns:
        List of products with order count, sorted by count descending
    """
    with get_session() as session:
        # Complex query with joins and aggregation
        results = session.query(
            Product,
            func.count(OrderItem.id).label('order_count')
        ).join(OrderItem).group_by(Product.id).order_by(
            desc('order_count')
        ).limit(limit).all()
        
        return [
            {**product.to_dict(), 'order_count': count}
            for product, count in results
        ]
```

## BigQuery Repository Pattern

### When to Use BigQuery

Use BigQuery repositories for:
- **Analytics queries**: Aggregations, reporting, dashboards
- **Historical data**: Long-term storage and analysis
- **Large datasets**: Petabyte-scale data processing
- **Read-heavy workloads**: Data warehousing, BI tools

Use traditional RDBMS (MySQL/PostgreSQL) for:
- **Transactional data**: CRUD operations, real-time updates
- **Relational integrity**: Foreign keys, constraints
- **Low-latency queries**: Sub-second response times

### BigQuery Repository Example

```python
# app/repositories/analytics_repository.py
from app.infra.bigquery_sa import get_bigquery_session
from app.models.analytics_event import AnalyticsEvent
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime

class AnalyticsRepository:
    
    @staticmethod
    def list_events(start_date: datetime, end_date: datetime, limit: int = 1000) -> List[Dict]:
        with get_bigquery_session() as session:
            events = session.query(AnalyticsEvent)\
                .filter(AnalyticsEvent.event_timestamp >= start_date)\
                .filter(AnalyticsEvent.event_timestamp < end_date)\
                .limit(limit)\
                .all()
            return [event.to_dict() for event in events]
    
    @staticmethod
    def get_event_counts_by_type(start_date: datetime, end_date: datetime) -> List[Dict]:
        with get_bigquery_session() as session:
            results = session.query(
                AnalyticsEvent.event_type,
                func.count(AnalyticsEvent.event_id).label('count')
            ).filter(
                AnalyticsEvent.event_timestamp >= start_date,
                AnalyticsEvent.event_timestamp < end_date
            ).group_by(AnalyticsEvent.event_type)\
             .order_by(func.count(AnalyticsEvent.event_id).desc())\
             .all()
            
            return [
                {'event_type': event_type, 'count': count}
                for event_type, count in results
            ]
    
    @staticmethod
    def insert_event(user_id: str, event_type: str, properties: List[str]) -> int:
        with get_bigquery_session() as session:
            event = AnalyticsEvent(
                user_id=user_id,
                event_type=event_type,
                event_timestamp=datetime.utcnow(),
                properties=properties
            )
            session.add(event)
            session.flush()
            return event.event_id
```

### Hybrid Repository Pattern

For applications using both traditional RDBMS and BigQuery:

```python
# app/repositories/order_repository.py
from app.infra.database import get_session  # MySQL
from app.infra.bigquery_sa import get_bigquery_session  # BigQuery
from app.models.order import Order
from app.models.order_analytics import OrderAnalytics

class OrderRepository:
    
    @staticmethod
    def create(user_id: int, total: float) -> int:
        """Create order in MySQL (transactional)"""
        with get_session() as session:
            order = Order(user_id=user_id, total=total)
            session.add(order)
            session.flush()
            return order.id
    
    @staticmethod
    def find_by_id(order_id: int) -> Optional[Dict]:
        """Find order in MySQL (real-time)"""
        with get_session() as session:
            order = session.query(Order).filter_by(id=order_id).first()
            return order.to_dict() if order else None
    
    @staticmethod
    def get_sales_report(start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get sales analytics from BigQuery (analytics)"""
        with get_bigquery_session() as session:
            results = session.query(
                func.date(OrderAnalytics.order_date).label('date'),
                func.sum(OrderAnalytics.total).label('total_sales'),
                func.count(OrderAnalytics.order_id).label('order_count')
            ).filter(
                OrderAnalytics.order_date >= start_date,
                OrderAnalytics.order_date < end_date
            ).group_by('date')\
             .order_by('date')\
             .all()
            
            return [
                {
                    'date': date.isoformat(),
                    'total_sales': float(total_sales),
                    'order_count': order_count
                }
                for date, total_sales, order_count in results
            ]
```

### BigQuery-Specific Considerations

#### 1. Partitioning for Performance

```python
# Always filter by partition column to reduce costs
@staticmethod
def list_events_by_date(date: datetime) -> List[Dict]:
    with get_bigquery_session() as session:
        # ✅ Good: Filter by partition column
        events = session.query(AnalyticsEvent)\
            .filter(func.date(AnalyticsEvent.event_timestamp) == date)\
            .all()
        return [e.to_dict() for e in events]
```

#### 2. Avoid SELECT *

```python
# ✅ Good: Select only needed columns
@staticmethod
def get_user_ids() -> List[str]:
    with get_bigquery_session() as session:
        results = session.query(AnalyticsEvent.user_id).distinct().all()
        return [user_id for (user_id,) in results]

# ❌ Bad: Selects all columns (expensive)
@staticmethod
def get_user_ids() -> List[str]:
    with get_bigquery_session() as session:
        events = session.query(AnalyticsEvent).all()
        return list(set(e.user_id for e in events))
```

#### 3. Batch Inserts

```python
@staticmethod
def bulk_insert_events(events_data: List[Dict]) -> None:
    with get_bigquery_session() as session:
        events = [
            AnalyticsEvent(**data)
            for data in events_data
        ]
        session.bulk_save_objects(events)
```

## References

- [Repository Pattern by Martin Fowler](https://martinfowler.com/eaaCatalog/repository.html)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/latest/orm/tutorial.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
