# Blueprint Pattern in Flask

Blueprints are Flask's way of organizing routes and handlers into modular components. This document explains how to structure and use blueprints effectively.

## What are Blueprints?

Blueprints allow you to organize your Flask application into logical components, each with its own routes, templates, and static files.

### Benefits
- **Modularity**: Separate features into independent modules
- **Reusability**: Blueprints can be registered multiple times
- **Organization**: Clear structure for large applications
- **Team collaboration**: Different teams can work on different blueprints

## Basic Blueprint Structure

### 1. Create a Blueprint

```python
# app/controllers/feature_controller.py
from flask import Blueprint, render_template, request, jsonify

feature_bp = Blueprint("feature", __name__)

@feature_bp.route("/")
def index():
    """Feature index page"""
    return render_template("feature/index.html")

@feature_bp.route("/api", methods=['GET'])
def list_features():
    """API endpoint to list features"""
    features = FeatureRepository.list_all()
    return jsonify(features)
```

### 2. Register Blueprint in Application Factory

```python
# app/__init__.py
from flask import Flask
from app.controllers.feature_controller import feature_bp

def create_app():
    app = Flask(__name__)
    
    # Register blueprint with URL prefix
    app.register_blueprint(feature_bp, url_prefix="/features")
    
    return app
```

### 3. Result

With `url_prefix="/features"`, routes become:
- `/features/` → `feature_bp.index()`
- `/features/api` → `feature_bp.list_features()`

## Organizing Controllers

### Directory Structure

```
app/
├── controllers/
│   ├── __init__.py
│   ├── root_controller.py      # Dashboard, home
│   ├── user_controller.py      # User management
│   ├── product_controller.py   # Product CRUD
│   └── api_controller.py       # External API endpoints
```

### Controller Template

```python
# app/controllers/product_controller.py
from flask import Blueprint, render_template, request, jsonify
from app.repositories.product_repository import ProductRepository

# Create blueprint
product_bp = Blueprint("product", __name__)

# HTML routes
@product_bp.route("/")
def index():
    """Product management page"""
    return render_template("products/index.html")

# API routes
@product_bp.route("/api", methods=['GET'])
def list_products():
    """List all products"""
    products = ProductRepository.list_all()
    return jsonify(products)

@product_bp.route("/api", methods=['POST'])
def create_product():
    """Create new product"""
    data = request.json
    product_id = ProductRepository.create(data)
    return jsonify({'id': product_id, 'success': True})

@product_bp.route("/api/<int:product_id>", methods=['GET'])
def get_product(product_id):
    """Get product by ID"""
    product = ProductRepository.find_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product)

@product_bp.route("/api/<int:product_id>", methods=['PUT'])
def update_product(product_id):
    """Update product"""
    data = request.json
    ProductRepository.update(product_id, data)
    return jsonify({'success': True})

@product_bp.route("/api/<int:product_id>", methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    ProductRepository.delete(product_id)
    return jsonify({'success': True})
```

## URL Prefix Strategies

### 1. Feature-based Prefixes

Group routes by feature:

```python
app.register_blueprint(user_bp, url_prefix="/users")
app.register_blueprint(product_bp, url_prefix="/products")
app.register_blueprint(order_bp, url_prefix="/orders")
```

Results in:
- `/users/` → User management page
- `/products/api` → Product API
- `/orders/api/123` → Order details

### 2. API Versioning

Separate API versions:

```python
app.register_blueprint(api_v1_bp, url_prefix="/api/v1")
app.register_blueprint(api_v2_bp, url_prefix="/api/v2")
```

### 3. Mixed Approach

Combine features with API separation:

```python
# HTML pages
app.register_blueprint(dashboard_bp, url_prefix="/")
app.register_blueprint(admin_bp, url_prefix="/admin")

# API endpoints
app.register_blueprint(user_api_bp, url_prefix="/api/users")
app.register_blueprint(product_api_bp, url_prefix="/api/products")
```

## Blueprint Configuration

### Template Folder

Blueprints can have their own template folders:

```python
feature_bp = Blueprint(
    "feature",
    __name__,
    template_folder="templates",
    static_folder="static"
)
```

Directory structure:
```
app/
├── controllers/
│   └── feature_controller.py
├── templates/
│   └── feature/
│       ├── index.html
│       └── detail.html
└── static/
    └── feature/
        ├── style.css
        └── script.js
```

### URL Generation

Use `url_for()` with blueprint name:

```python
# In template
<a href="{{ url_for('feature.index') }}">Features</a>
<a href="{{ url_for('product.list_products') }}">Products API</a>

# In controller
from flask import url_for, redirect

@feature_bp.route("/create")
def create():
    # ... create logic
    return redirect(url_for('feature.index'))
```

## Error Handling in Blueprints

### Blueprint-specific Error Handlers

```python
@product_bp.errorhandler(404)
def product_not_found(error):
    return jsonify({'error': 'Product not found'}), 404

@product_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Invalid request'}), 400
```

### Global Error Handlers

```python
# app/__init__.py
def create_app():
    app = Flask(__name__)
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app
```

## Request Hooks

### Before Request

```python
@product_bp.before_request
def before_product_request():
    """Runs before every request to product blueprint"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
```

### After Request

```python
@product_bp.after_request
def after_product_request(response):
    """Runs after every request to product blueprint"""
    response.headers['X-Custom-Header'] = 'value'
    return response
```

## Best Practices

### 1. One Blueprint per Feature

```
✅ Good: Separate blueprints
- user_controller.py → user_bp
- product_controller.py → product_bp
- order_controller.py → order_bp

❌ Bad: Single monolithic blueprint
- main_controller.py → main_bp (all routes)
```

### 2. Consistent Naming Convention

```python
# Blueprint variable name: {feature}_bp
user_bp = Blueprint("user", __name__)
product_bp = Blueprint("product", __name__)

# Blueprint name (first arg): lowercase, singular
Blueprint("user", __name__)  # ✅
Blueprint("User", __name__)  # ❌
Blueprint("users", __name__) # ❌
```

### 3. Group Related Routes

```python
# ✅ Good: Grouped by resource
@product_bp.route("/api")  # List
@product_bp.route("/api", methods=['POST'])  # Create
@product_bp.route("/api/<int:id>")  # Get
@product_bp.route("/api/<int:id>", methods=['PUT'])  # Update
@product_bp.route("/api/<int:id>", methods=['DELETE'])  # Delete

# ❌ Bad: Scattered routes
@product_bp.route("/list")
@product_bp.route("/new")
@product_bp.route("/show/<int:id>")
```

### 4. Separate HTML and API Routes

```python
# HTML routes (no /api prefix)
@product_bp.route("/")
def index():
    return render_template("products/index.html")

# API routes (with /api prefix)
@product_bp.route("/api")
def list_products():
    return jsonify(products)
```

### 5. Use Descriptive Function Names

```python
# ✅ Good: Clear intent
@product_bp.route("/api", methods=['POST'])
def create_product():
    pass

# ❌ Bad: Unclear
@product_bp.route("/api", methods=['POST'])
def post():
    pass
```

## Testing Blueprints

### Unit Test

```python
def test_list_products(client):
    response = client.get('/products/api')
    assert response.status_code == 200
    assert isinstance(response.json, list)
```

### Integration Test

```python
def test_create_and_retrieve_product(client):
    # Create
    create_response = client.post('/products/api', json={
        'name': 'Test Product',
        'price': 99.99
    })
    assert create_response.status_code == 200
    product_id = create_response.json['id']
    
    # Retrieve
    get_response = client.get(f'/products/api/{product_id}')
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Test Product'
```

## Common Patterns

### RESTful API Blueprint

```python
@api_bp.route("/resources", methods=['GET'])
def list_resources():
    """GET /resources - List all"""
    pass

@api_bp.route("/resources", methods=['POST'])
def create_resource():
    """POST /resources - Create new"""
    pass

@api_bp.route("/resources/<int:id>", methods=['GET'])
def get_resource(id):
    """GET /resources/:id - Get one"""
    pass

@api_bp.route("/resources/<int:id>", methods=['PUT'])
def update_resource(id):
    """PUT /resources/:id - Update"""
    pass

@api_bp.route("/resources/<int:id>", methods=['DELETE'])
def delete_resource(id):
    """DELETE /resources/:id - Delete"""
    pass
```

### Admin Blueprint with Authentication

```python
admin_bp = Blueprint("admin", __name__)

@admin_bp.before_request
def require_admin():
    if not current_user.is_admin:
        abort(403)

@admin_bp.route("/")
def dashboard():
    return render_template("admin/dashboard.html")

@admin_bp.route("/users")
def manage_users():
    return render_template("admin/users.html")
```

## References

- [Flask Blueprints Documentation](https://flask.palletsprojects.com/en/latest/blueprints/)
- [Modular Applications with Blueprints](https://flask.palletsprojects.com/en/latest/patterns/packages/)
- [Large Application Structure](https://flask.palletsprojects.com/en/latest/patterns/packages/)
