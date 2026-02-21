# ViT Deepfake Detector - Architecture Documentation

Complete technical architecture documentation for the ViT Deepfake Detector system.

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Data Flow](#data-flow)
3. [Deployment Options](#deployment-options)
4. [Component Breakdown](#component-breakdown)
5. [Database Abstraction](#database-abstraction)
6. [API Architecture](#api-architecture)
7. [Configuration-Driven Design](#configuration-driven-design)
8. [Scalability & Performance](#scalability--performance)
9. [Security Architecture](#security-architecture)
10. [Technology Stack](#technology-stack)

---

## System Architecture Overview

### Layered Architecture

The application follows a **layered architecture pattern** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│  • Web Browser (HTML5)                                   │
│  • Mobile App (future)                                   │
│  • REST API Clients                                      │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                  FRONTEND LAYER                          │
│  • HTML Templates (index, login, register, dashboard)    │
│  • CSS (Responsive, Dark/Light Mode)                     │
│  • JavaScript (auth.js, dashboard.js, main.js)           │
│  • Static Assets                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                   BACKEND LAYER (Flask)                  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Route Handlers                                     │  │
│  │  • Authentication Routes (/auth/*)                │  │
│  │  • Detection API Routes (/api/detection/*)        │  │
│  │  • Home Routes (/, /login, /register, /dashboard) │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Services                                           │  │
│  │  • DeepFake Detector (ViT Model)                  │  │
│  │  • File Management (Upload, Validation)           │  │
│  │  • Authentication (Hashing, Sessions)             │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Core                                               │  │
│  │  • Configuration (DB_TYPE selection)              │  │
│  │  • Decorators (login_required, validate_file)     │  │
│  │  • Utilities (SSL, File ops, Backups)             │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼─────────┐  ┌────────▼────────┐
│  DATABASE LAYER │  │  ML LAYER       │
│                 │  │                  │
│ • SQLAlchemy    │  │ • Vision         │
│   Models        │  │   Transformer    │
│ • SQLite        │  │ • Image          │
│   (Local)       │  │   Processor      │
│                 │  │ • Inference      │
│ • MongoEngine   │  │   Pipeline       │
│   Models        │  │ • Confidence     │
│ • MongoDB Local │  │   Scoring        │
│ • MongoDB Atlas │  │                  │
│   (Cloud)       │  │                  │
└─────────────────┘  └──────────────────┘
        │
┌───────▼──────────────────────────────┐
│       STORAGE LAYER                  │
│ • Uploads Folder (Images)            │
│ • Models Folder (ViT weights)        │
│ • Temporary Files                    │
└──────────────────────────────────────┘
```

### Architecture Principles

1. **Separation of Concerns** - Clear boundaries between layers
2. **Database Abstraction** - Switch databases with configuration only
3. **Modular Design** - Independent, reusable components
4. **API-First** - RESTful API foundation
5. **Configuration-Driven** - Environment-based settings
6. **Security-Focused** - Password hashing, session management, input validation

---

## Data Flow

### Complete User Journey

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ├─► 1. AUTHENTICATION FLOW
       │    ├─ POST /auth/register
       │    │   ├─ Validate input
       │    │   ├─ Hash password (Werkzeug)
       │    │   └─ SaveUser (SQLite/MongoDB)
       │    │
       │    └─ POST /auth/login
       │        ├─ Verify credentials
       │        ├─ Create session (Flask-Login)
       │        └─ Return session cookie
       │
       ├─► 2. DETECTION FLOW
       │    └─ POST /api/detection/upload
       │        │
       │        ├─ Validate file
       │        │   ├─ Check file type (JPEG, PNG, BMP, GIF)
       │        │   ├─ Check file size (<16MB)
       │        │   └─ Reject invalid files
       │        │
       │        ├─ Preprocess Image
       │        │   ├─ Load image with PIL
       │        │   ├─ Resize to 224×224
       │        │   ├─ Normalize (ImageNet stats)
       │        │   └─ Format as tensor
       │        │
       │        ├─ Run ViT Model
       │        │   ├─ Forward pass through 12 layers
       │        │   ├─ 768-dim embeddings
       │        │   ├─ 2-class classification head
       │        │   └─ Get logits [real_score, deepfake_score]
       │        │
       │        ├─ Post-Process Results
       │        │   ├─ Apply softmax
       │        │   ├─ Get max probability
       │        │   ├─ Set label (REAL/DEEPFAKE)
       │        │   └─ Calculate confidence (0-1)
       │        │
       │        ├─ Save to Database
       │        │   ├─ SQLite Path:
       │        │   │   └─ INSERT INTO detection (...)
       │        │   │
       │        │   └─ MongoDB Path:
       │        │       └─ db.detections.insertOne({...})
       │        │
       │        └─ Return JSON Response
       │            ├─ prediction (REAL/DEEPFAKE)
       │            ├─ confidence (0.95)
       │            ├─ processing_time (0.32s)
       │            └─ detection_id (UUID)
       │
       └─► 3. HISTORY & STATS FLOW
           ├─ GET /api/detection/history?page=1&limit=10
           │   ├─ Fetch user detections (paginated)
           │   ├─ SQLite: SELECT * FROM detection WHERE user_id=X
           │   ├─ MongoDB: db.detections.find({user_id: ObjectId(...)})
           │   └─ Return paginated results
           │
           └─ GET /api/detection/stats
               ├─ Count total detections
               ├─ Count REAL detections
               ├─ Count DEEPFAKE detections
               ├─ Calculate avg confidence
               └─ Return statistics JSON
```

### Image Processing Pipeline

```
Input Image (JPG/PNG/BMP/GIF)
    ↓
1. Load Image
   └─ PIL.Image.open()
    ↓
2. Face Detection (Optional)
   └─ OpenCV face cascade
    ↓
3. Resize
   └─ 224×224 pixels (ViT requirement)
    ↓
4. Normalize
   ├─ Convert to RGB
   ├─ Divide by 255
   └─ Apply ImageNet stats
       [mean=0.5, std=0.5]
    ↓
5. Convert to Tensor
   └─ torch.tensor(H, W, C)
    ↓
6. Forward Pass
   ├─ ViT backbone (12 layers)
   ├─ Patch embedding (16×16)
   ├─ Transformer encoder
   └─ Classification head
    ↓
7. Get Logits
   └─ [real_logit, deepfake_logit]
    ↓
8. Apply Softmax
   └─ [real_prob, deepfake_prob]
    ↓
9. Extract Result
   ├─ prediction = argmax(probs)
   ├─ confidence = max(probs)
   └─ label = {0: 'REAL', 1: 'DEEPFAKE'}
    ↓
Output
└─ {"prediction": "DEEPFAKE", "confidence": 0.95}
```

---

## Deployment Options

### 1. Development Setup

**Environment:** Local machine
**Database:** SQLite
**Server:** Flask development server

```
┌──────────────────┐
│  Browser         │
│  localhost:5000  │
└────────┬─────────┘
         │
         ▼
   ┌──────────────────────┐
   │  Flask Dev Server    │
   │  python -m flask run │
   └──────────┬───────────┘
              │
              ▼
       ┌────────────────┐
       │  SQLite File   │
       │  users.db      │
       └────────────────┘

Configuration:
- DB_TYPE=sqlite
- FLASK_APP=backend/app.py
- DEBUG=True
- Environment: development
```

**Setup Time:** 10-15 minutes
**Best For:** Learning, prototyping, single developer
**Strengths:**
- No external dependencies
- Simple setup
- File-based storage
- Automatic reloading

---

### 2. Docker Compose Setup

**Environment:** Containerized
**Database:** MongoDB (container)
**Services:** Flask, MongoDB, Nginx (optional)

```
┌─────────────────────────────────────────┐
│         Docker Compose Network          │
├─────────────────────────────────────────┤
│                                         │
│ ┌──────────────────────────────────┐   │
│ │  Flask Service                   │   │
│ │  - Port: 5000                    │   │
│ │  - app_mongo_enabled.py          │   │
│ │  - Environment variables         │   │
│ └──────────────────────────────────┘   │
│                                         │
│ ┌──────────────────────────────────┐   │
│ │  MongoDB Service                 │   │
│ │  - Port: 27017                   │   │
│ │  - Volume: mongodb_data          │   │
│ │  - Authentication: admin/pass    │   │
│ └──────────────────────────────────┘   │
│                                         │
│ ┌──────────────────────────────────┐   │
│ │  Nginx Service (Optional)        │   │
│ │  - Port: 80/443                  │   │
│ │  - Reverse proxy                 │   │
│ │  - SSL/TLS support               │   │
│ └──────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
         │
         ▼
   Browser: localhost:5000 or domain.com

Orchestration:
- docker-compose -f docker-compose-mongodb.yml up -d

Configuration:
- DB_TYPE=mongodb
- MONGODB_URI=mongodb://mongodb:27017/deepfake_detector
- FLASK_APP=backend/app_mongo_enabled.py
```

**Setup Time:** 15-20 minutes (with Docker installed)
**Best For:** Team development, staging, testing
**Strengths:**
- Isolated environments
- Reproducible builds
- Easy scaling
- Volume management

---

### 3. Production Deployment

**Environment:** Cloud platform (AWS/Azure/GCP/Heroku)
**Database:** MongoDB Atlas (managed)
**Services:** Load Balancer, Multiple Workers, Nginx, CDN

```
┌────────────────────────────────────────────────────────┐
│              Production Infrastructure                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Internet                                             │
│     │                                                 │
│     ▼                                                 │
│  ┌─────────────────────────────────┐                 │
│  │  CDN (CloudFront/Cloudflare)    │                 │
│  │  - Static assets caching        │                 │
│  │  - Global distribution          │                 │
│  └─────────────┬───────────────────┘                 │
│                │                                      │
│                ▼                                      │
│  ┌──────────────────────────────────┐                │
│  │  Load Balancer (ELB/ALB)         │                │
│  │  - SSL/TLS termination           │                │
│  │  - Session stickiness            │                │
│  │  - Health checks                 │                │
│  └──────────────┬───────────────────┘                │
│                 │                                     │
│   ┌─────────────┼─────────────┐                      │
│   │             │             │                      │
│   ▼             ▼             ▼                      │
│  ┌────┐       ┌────┐       ┌────┐                   │
│  │ W1 │       │ W2 │       │ W3 │                   │
│  │    │       │    │       │    │                   │
│  │Guni│       │Guni│       │Guni│                   │
│  │corn│       │corn│       │corn│                   │
│  │ 4  │       │ 4  │       │ 4  │                   │
│  │WRK │       │WRK │       │WRK │                   │
│  └──┬─┘       └──┬─┘       └──┬─┘                   │
│     │            │            │                     │
│     └────────────┼────────────┘                     │
│                  │                                  │
│                  ▼                                  │
│     ┌──────────────────────────┐                   │
│     │  Shared Nginx            │                   │
│     │  Reverse Proxy           │                   │
│     │  - Request routing       │                   │
│     │  - Compression (gzip)    │                   │
│     │  - Rate limiting         │                   │
│     └──────────────┬───────────┘                   │
│                    │                               │
│                    ▼                               │
│     ┌──────────────────────────┐                   │
│     │  MongoDB Atlas Cluster   │                   │
│     │  - Managed service       │                   │
│     │  - Auto-backup           │                   │
│     │  - Replication (3+)      │                   │
│     │  - Sharding support      │                   │
│     │  - TLS/SSL encryption    │                   │
│     └──────────────────────────┘                   │
│                                                    │
└────────────────────────────────────────────────────┘

Monitoring & Logging:
├─ CloudWatch/ELK Stack (Logs)
├─ Prometheus/Grafana (Metrics)
└─ PagerDuty/Slack (Alerts)

CI/CD Pipeline:
├─ GitHub Actions/CodePipeline
├─ Build & Test
├─ Push to ECR/DockerHub
└─ Deploy with rolling updates

Configuration:
- DB_TYPE=mongodb
- MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/...
- FLASK_APP=backend/app_mongo_enabled.py
- FLASK_ENV=production
- DEBUG=False
```

**Setup Time:** 1-2 hours (infrastructure setup)
**Best For:** Production, scaling, reliability
**Strengths:**
- High availability
- Auto-scaling
- Managed database
- CI/CD integration
- Global CDN

---

## Component Breakdown

### Backend Routes & Services

#### Authentication Routes
```python
# File: backend/auth.py or backend/auth_mongo.py

POST /auth/register
├─ Input: username, email, password, password_confirm
├─ Validation:
│  ├─ Check username not exists
│  ├─ Check email not exists
│  ├─ Validate password strength
│  └─ Match passwords
├─ Processing:
│  ├─ Hash password with Werkzeug
│  ├─ Create user record
│  └─ Save to database
└─ Response: {status, message, user_id}

POST /auth/login
├─ Input: username_or_email, password
├─ Validation:
│  ├─ Find user by username/email
│  ├─ Verify password hash
│  └─ Check account status
├─ Processing:
│  ├─ Create session (Flask-Login)
│  ├─ Set session cookie
│  └─ Return user object
└─ Response: {status, message, user}

POST /auth/logout
├─ Processing:
│  └─ Clear session
└─ Response: {status, message}

POST /auth/change-password
├─ Authentication: Required
├─ Input: old_password, new_password
├─ Validation:
│  ├─ Verify old password
│  ├─ Validate new password
│  └─ Check not same
├─ Processing:
│  ├─ Hash new password
│  └─ Update in database
└─ Response: {status, message}
```

#### Detection API Routes
```python
# File: backend/api_routes.py or backend/api_routes_mongo.py

POST /api/detection/upload
├─ Authentication: Required (login_required)
├─ Input: image file (multipart/form-data)
├─ Processing:
│  ├─ Validate file:
│  │  ├─ Check type (JPEG, PNG, BMP, GIF)
│  │  ├─ Check size (<16MB)
│  │  └─ Check not corrupted
│  ├─ Save file:
│  │  └─ Generate UUID filename
│  ├─ Preprocess:
│  │  ├─ Resize to 224×224
│  │  ├─ Normalize
│  │  └─ Convert to tensor
│  ├─ Detect:
│  │  ├─ Forward pass through ViT
│  │  ├─ Get logits
│  │  └─ Apply softmax
│  └─ Save to database:
│     ├─ Store metadata
│     ├─ Link to user
│     └─ Record timestamp
└─ Response: {detection_id, prediction, confidence, processing_time}

GET /api/detection/history?page=1&limit=10
├─ Authentication: Required
├─ Parameters: page (int), limit (int, max 100)
├─ Processing:
│  ├─ Query database:
│  │  ├─ SQLite: SELECT * FROM detection WHERE user_id=X LIMIT offset,limit
│  │  └─ MongoDB: db.detections.find({user_id: X}).skip(offset).limit(limit)
│  ├─ Count total:
│  │  ├─ SQLite: SELECT COUNT(*) FROM detection WHERE user_id=X
│  │  └─ MongoDB: db.detections.countDocuments({user_id: X})
│  └─ Calculate pages
└─ Response: {detections: [...], total, pages, current_page}

GET /api/detection/details/<detection_id>
├─ Authentication: Required
├─ Authorization: Must be owner
├─ Processing:
│  └─ Query database for single record
└─ Response: {detection details}

DELETE /api/detection/delete/<detection_id>
├─ Authentication: Required
├─ Authorization: Must be owner
├─ Processing:
│  ├─ Delete file from disk
│  └─ Delete record from database
└─ Response: {status, message}

GET /api/detection/stats
├─ Authentication: Required
├─ Processing:
│  ├─ Count total detections
│  ├─ Count REAL detections
│  ├─ Count DEEPFAKE detections
│  └─ Calculate average confidence
└─ Response: {total, real_count, deepfake_count, avg_confidence}

GET /api/health
├─ Authentication: Not required
├─ Processing:
│  └─ Check database connection
└─ Response: {status, database_type, message}
```

### Machine Learning Inference

```python
# File: backend/deepfake_detector.py

class DeepfakeDetector:
    
    def __init__(self, model_path, device='cpu'):
        # Load pretrained ViT model
        # From: google/vit-base-patch16-224-in21k
        # Weights: 86M parameters
        # Input: 224×224×3 (RGB)
        # Output: 2-dim logits [REAL, DEEPFAKE]
    
    def preprocess_image(self, image_path):
        # 1. Load image with PIL
        # 2. Resize to 224×224
        # 3. Convert to RGB (if needed)
        # 4. Normalize with ImageNet stats
        #    - mean: [0.5, 0.5, 0.5]
        #    - std: [0.5, 0.5, 0.5]
        # 5. Convert to tensor
        # Return: torch.Tensor (1, 3, 224, 224)
    
    def detect(self, image_path):
        # 1. Preprocess image
        # 2. Set model to eval mode
        # 3. Disable gradients
        # 4. Forward pass through ViT
        # 5. Get logits
        # 6. Apply softmax
        # 7. Extract:
        #    - Prediction (argmax)
        #    - Confidence (max prob)
        #    - Label mapping
        # Return: (prediction, confidence, processing_time)
    
    def save_model(self, save_path):
        # Save model weights to disk
        # For later inference
```

### Database Models

#### SQLAlchemy (SQLite)
```python
# File: backend/models.py

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    detections = db.relationship('Detection', backref='user')
    
    Methods:
    - set_password(password)
    - check_password(password)
    - get_id()

class Detection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200))
    prediction = db.Column(db.String(20), nullable=False)  # REAL/DEEPFAKE
    confidence = db.Column(db.Float, nullable=False)  # 0.0-1.0
    processing_time = db.Column(db.Float)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    Methods:
    - to_dict()
```

#### MongoEngine (MongoDB)
```python
# File: backend/mongo_models.py

class MongoUser(Document):
    meta = {
        'collection': 'users',
        'indexes': ['username', 'email']
    }
    
    username = StringField(unique=True, required=True)
    email = EmailField(unique=True, required=True)
    password_hash = StringField(required=True)
    
    Methods:
    - set_password(password)
    - check_password(password)
    - get_id()

class MongoDetection(Document):
    meta = {
        'collection': 'detections',
        'indexes': [
            'user_id',
            ('user_id', 'created_at'),
            'created_at'
        ]
    }
    
    user_id = ObjectIdField(required=True)
    filename = StringField(required=True)
    original_filename = StringField()
    prediction = StringField(required=True)  # REAL/DEEPFAKE
    confidence = FloatField(required=True)  # 0.0-1.0
    processing_time = FloatField()  # seconds
    created_at = DateTimeField(default=datetime.utcnow, db_field='created_at')
    
    Methods:
    - to_dict()
```

---

## Database Abstraction

### Configuration-Based Selection

```python
# File: backend/config.py

class Config:
    # Database type: 'sqlite' or 'mongodb'
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
    
    # SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///users.db'
    )
    
    # MongoDB
    MONGODB_URI = os.getenv(
        'MONGODB_URI',
        'mongodb://localhost:27017/deepfake_detector'
    )
    MONGODB_DB = os.getenv(
        'MONGODB_DB',
        'deepfake_detector'
    )
    
    # Other settings
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/vit_deepfake_detector.pth')
    DEVICE = os.getenv('DEVICE', 'cpu')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'backend/uploads')
```

### Application Factory Pattern

```python
# File: backend/app.py or backend/app_mongo_enabled.py

def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(config[config_name or 'development'])
    
    db_type = app.config.get('DB_TYPE', 'sqlite').lower()
    
    if db_type == 'mongodb':
        # MongoDB Setup
        from mongoengine import connect
        connect(
            db=app.config.get('MONGODB_DB'),
            host=app.config.get('MONGODB_URI')
        )
        
        from mongo_models import MongoUser
        from auth_mongo import auth_mongo_bp
        from api_routes_mongo import detection_mongo_bp
        
        @login_manager.user_loader
        def load_user(user_id):
            return MongoUser.objects(id=user_id).first()
        
        app.register_blueprint(auth_mongo_bp)
        app.register_blueprint(detection_mongo_bp)
    
    else:
        # SQLite Setup
        from flask_sqlalchemy import SQLAlchemy
        db = SQLAlchemy(app)
        
        from models import User
        from auth import auth_bp
        from api_routes import detection_bp
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(detection_bp)
    
    # Common setup
    login_manager.init_app(app)
    # ... rest of setup
    
    return app
```

### Database Switching

To switch databases, only update `.env`:

```bash
# For SQLite (Development)
DB_TYPE=sqlite
FLASK_APP=backend/app.py
DATABASE_URL=sqlite:///users.db

# For MongoDB Local (Staging)
DB_TYPE=mongodb
FLASK_APP=backend/app_mongo_enabled.py
MONGODB_URI=mongodb://localhost:27017/deepfake_detector
MONGODB_DB=deepfake_detector

# For MongoDB Cloud (Production)
DB_TYPE=mongodb
FLASK_APP=backend/app_mongo_enabled.py
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/deepfake_detector?retryWrites=true&w=majority
MONGODB_DB=deepfake_detector
```

**No code changes required!**

---

## API Architecture

### REST API Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | /auth/register | No | Create user account |
| POST | /auth/login | No | Authenticate user |
| POST | /auth/logout | Yes | End session |
| POST | /auth/change-password | Yes | Update password |
| POST | /api/detection/upload | Yes | Upload & detect |
| GET | /api/detection/history | Yes | Get user history |
| GET | /api/detection/details/<id> | Yes | Get single result |
| DELETE | /api/detection/delete/<id> | Yes | Delete record |
| GET | /api/detection/stats | Yes | Get statistics |
| GET | /api/health | No | Health check |

### Request/Response Format

All API responses follow a consistent JSON format:

```json
{
  "status": "success" | "error",
  "data": { ... },
  "message": "Human readable message",
  "error_code": "optional_error_code"
}
```

### Authentication

- **Method:** Session-based (Flask-Login)
- **Session Storage:** Server memory
- **Session Duration:** Browser session (can be configured)
- **User Loader:** Custom user_loader function
- **Decorators:** @login_required on protected routes

### Error Handling

```python
Global error handlers:
- 400: Bad Request
- 401: Unauthorized (authentication required)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 500: Internal Server Error

Custom decorators:
- @validate_file_upload(): File validation
- @handle_exceptions: Exception handling
- @login_required: Authentication check
```

---

## Configuration-Driven Design

### Environment Variables

```bash
# Flask Configuration
FLASK_ENV=development|production
FLASK_APP=backend/app.py|backend/app_mongo_enabled.py
DEBUG=True|False
SECRET_KEY=your-secret-key-here

# Database Selection
DB_TYPE=sqlite|mongodb

# SQLite (optional)
DATABASE_URL=sqlite:///users.db

# MongoDB
MONGODB_URI=mongodb://host:port/db or mongodb+srv://user:pass@cluster
MONGODB_DB=database_name

# Model Configuration
MODEL_PATH=models/vit_deepfake_detector.pth
DEVICE=cpu|cuda
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=backend/uploads

# Security
SESSION_COOKIE_SECURE=True|False
SESSION_COOKIE_HTTPONLY=True|False
SESSION_COOKIE_SAMESITE=Strict|Lax
```

### Configuration Hierarchy

1. **Environment Variables** (.env file)
   - Highest priority
   - Specific to deployment

2. **Default Values** (config.py)
   - Fallback values
   - Reasonable defaults

3. **Hardcoded** (in code)
   - Last resort
   - Avoid this

### Environment Profiles

```python
# Development
FLASK_ENV=development
DB_TYPE=sqlite
DEBUG=True

# Staging
FLASK_ENV=production
DB_TYPE=mongodb
DEBUG=False
MONGODB_URI=mongodb://staging-mongo:27017

# Production
FLASK_ENV=production
DB_TYPE=mongodb
DEBUG=False
MONGODB_URI=mongodb+srv://prod-user:pwd@cluster.mongodb.net
SESSION_COOKIE_SECURE=True
```

---

## Scalability & Performance

### Database Scalability

| Aspect | SQLite | MongoDB Local | MongoDB Atlas |
|--------|--------|---------------|-------------|
| Single User | ✅ Excellent | ✅ Excellent | ✅ Excellent |
| 10 Users | ✅ Good | ✅ Excellent | ✅ Excellent |
| 100 Users | ⚠️ Acceptable | ✅ Excellent | ✅ Excellent |
| 1000 Users | ❌ Poor | ✅ Good | ✅ Excellent |
| 10000+ Users | ❌ Not suitable | ⚠️ Limited | ✅ Excellent |
| Sharding | ❌ No | ⚠️ Manual | ✅ Automatic |
| Replication | ❌ No | ⚠️ Manual | ✅ Automatic |
| Backup | ❌ Manual | ⚠️ Manual | ✅ Automatic |

### Application Scalability

```
Single Process (Development)
└─ Flask dev server (1 worker)
   └─ SQLite or MongoDB

Horizontal Scaling (Production)
├─ Gunicorn (4+ workers)
├─ Load Balancer (distribute requests)
├─ Nginx Reverse Proxy
├─ Session Store (Redis for distributed sessions)
└─ MongoDB Atlas (shared database)

Vertical Scaling
└─ Increase:
   ├─ Gunicorn workers
   ├─ MongoDB server resources
   ├─ Nginx worker processes
   └─ System memory/CPU
```

### Performance Optimization

#### Image Processing
- Cache preprocessed images
- Batch processing for multiple images
- Use GPU (CUDA) for faster inference
- Limit image size before upload

#### Database
- Index frequently queried fields
- Use pagination for large result sets
- Connection pooling (MongoEngine handles it)
- Query optimization

#### Caching
- Browser cache (static assets)
- Server cache (Redis for sessions, caching)
- CDN cache (CloudFront, Cloudflare)

---

## Security Architecture

### Authentication & Authorization

```
User Credentials
    ↓
Password Hashing (Werkzeug bcrypt)
    ├─ Secure hash algorithm
    ├─ Salt included
    └─ Configurable iterations
    ↓
Session Creation (Flask-Login)
    ├─ Session cookie
    ├─ User ID stored server-side
    └─ HttpOnly flag (prevent XSS)
    ↓
Authorization Check
    ├─ @login_required decorator
    └─ User ownership verification
```

### Input Validation

```python
# File Validation
- Allowed types: JPEG, PNG, BMP, GIF
- Max size: 16 MB
- Malware scanning: (optional integration)

# Form Validation
- Username: 3-80 chars, alphanumeric+_
- Email: Valid email format
- Password: min 6 chars (configurable)

# API Validation
- SQL Injection: SQLAlchemy/MongoEngine ORM
- Cross-Site Scripting (XSS): Templating engine
- Cross-Site Request Forgery (CSRF): Flask-CSRF
```

### Data Protection

```
At Rest:
- SQLite: Unencrypted file (can be encrypted)
- MongoDB Local: Unencrypted (can enable auth)
- MongoDB Atlas: Encrypted at rest

In Transit:
- HTTP → Use HTTPS only (production)
- TLS 1.2+ (minimum security)
- Certificate validation

Sensitive Data:
- Passwords: Hashed with bcrypt
- Sessions: Server-side tokens
- API Keys: Environment variables
- Images: Temporary storage, auto-cleanup
```

### Rate Limiting & DDoS Protection

```
Nginx Configuration:
- limit_req: Request rate limiting
- limit_conn: Connection limiting

Application:
- Session timeouts
- Brute-force protection
- File upload limits

CDN:
- DDoS protection
- Geographic blocking
- Bot detection
```

---

## Technology Stack

### Frontend

| Technology | Purpose | Version |
|-----------|---------|---------|
| HTML5 | Markup | Latest |
| CSS3 | Styling | Latest |
| JavaScript | Dynamic behavior | ES6+ |
| Bootstrap | Responsive framework | 5.x (optional) |

### Backend

| Technology | Purpose | Version |
|-----------|---------|---------|
| Flask | Web framework | 2.3.x |
| Flask-Login | Authentication | 0.6.x |
| Flask-CORS | CORS support | 4.0.x |
| SQLAlchemy | ORM (SQLite) | 2.0.x |
| MongoEngine | ODM (MongoDB) | 3.0.x |
| Werkzeug | WSGI utilities | 2.3.x |
| PyTorch | Deep learning | 2.0.x |
| Transformers | ViT model | 4.30.x |
| OpenCV | Image processing | 4.8.x |
| Pillow | Image manipulation | 10.x |
| python-dotenv | Environment config | 1.0.x |

### Database

| Technology | Deployment | Purpose |
|-----------|-----------|---------|
| SQLite | Local file | Development |
| MongoDB | Local server | Staging |
| MongoDB Atlas | Cloud | Production |

### DevOps

| Technology | Purpose | Usage |
|-----------|---------|-------|
| Docker | Containerization | docker-compose up -d |
| Docker Compose | Container orchestration | Multi-service setup |
| Gunicorn | WSGI server | Production (4+ workers) |
| Nginx | Reverse proxy | Production, TLS termination |

### Tools & Services

| Tool | Purpose |
|------|---------|
| pytest | Unit testing |
| Postman | API testing |
| MongoDB Compass | Database GUI |
| Prometheus | Metrics collection |
| Grafana | Visualization |
| ELK Stack | Log aggregation |

---

## File Organization

```
deep fake/
├── backend/
│   ├── __init__.py
│   ├── app.py                    # SQLite Flask app
│   ├── app_mongo_enabled.py      # MongoDB Flask app
│   ├── config.py                 # Configuration
│   ├── models.py                 # SQLAlchemy models
│   ├── mongo_models.py           # MongoEngine models
│   ├── auth.py                   # SQLite auth routes
│   ├── auth_mongo.py             # MongoDB auth routes
│   ├── api_routes.py             # SQLite detection routes
│   ├── api_routes_mongo.py       # MongoDB detection routes
│   ├── deepfake_detector.py      # ViT model wrapper
│   ├── decorators.py             # Custom decorators
│   ├── utils.py                  # Utility functions
│   ├── init_db.py                # SQLite initialization
│   ├── init_mongodb.py           # MongoDB initialization
│   └── uploads/                  # User-uploaded images
│
├── frontend/
│   ├── templates/
│   │   ├── index.html            # Home page
│   │   ├── login.html            # Login form
│   │   ├── register.html         # Registration form
│   │   └── dashboard.html        # Main dashboard
│   │
│   └── static/
│       ├── css/
│       │   └── style.css         # Main stylesheet
│       │
│       └── js/
│           ├── main.js           # Home page logic
│           ├── auth.js           # Authentication logic
│           └── dashboard.js      # Dashboard logic
│
├── tests/
│   ├── __init__.py
│   ├── test_app.py               # App tests
│   └── test_detector.py          # Model tests
│
├── models/
│   └── vit_deepfake_detector.pth # ViT weights (auto-downloaded)
│
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Single database compose
├── docker-compose-mongodb.yml    # MongoDB compose
├── nginx.conf                    # Nginx configuration
├── migrate_database.py           # Migration tool
│
├── README.md                     # Project overview
├── QUICKSTART.md                 # Quick start guide
├── ARCHITECTURE.md               # This file
├── API_DOCUMENTATION.md          # API reference
├── DEPLOYMENT.md                 # Deployment guide
├── MONGODB_SETUP.md              # MongoDB setup guide
├── MONGODB_DEPLOYMENT_GUIDE.md   # MongoDB production guide
├── MONGODB_QUICK_REFERENCE.md    # MongoDB quick reference
├── TRAINING.md                   # Model training guide
├── PROJECT_SUMMARY.md            # Project summary
├── PROGRESS.md                   # Development progress
└── FILE_MANIFEST.md              # File listing
```

---

## Summary

The ViT Deepfake Detector follows a **layered, configuration-driven architecture** that allows:

✅ **Database Flexibility** - Switch between SQLite and MongoDB with .env only
✅ **Scalability** - From single developer to production with thousands of users
✅ **Security** - Password hashing, session management, input validation
✅ **Maintainability** - Clear separation of concerns, modular design
✅ **Testing** - Comprehensive test suite, API-first design
✅ **Deployment** - Development, Docker, and cloud-ready

The architecture supports modern development practices while remaining simple enough for quick prototyping and learning.

---

**For detailed information on specific components, see:**

- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API endpoints
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [MONGODB_SETUP.md](MONGODB_SETUP.md) - MongoDB setup
- [MONGODB_DEPLOYMENT_GUIDE.md](MONGODB_DEPLOYMENT_GUIDE.md) - MongoDB production
