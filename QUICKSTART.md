# Quick start guide for the ViT Deepfake Detector

## 🗄️ Choose Your Database

You have two options:

| Database | Setup Time | Best For | Requirement |
|----------|-----------|----------|-------------|
| **SQLite** (Default) | 1 min | Development | None - works immediately |
| **MongoDB** | 5-10 min | Production/Team | Install MongoDB or use cloud |

**→ Start with SQLite for fastest setup, then upgrade to MongoDB later if needed**

---

## Quick Start: SQLite (5 minutes - Recommended for First Run)

### 1. Clone and Setup (5 minutes)

```bash
# Navigate to project
cd "deep fake"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database (1 minute)

```bash
# Create and initialize database with demo user
python backend/init_db.py
```

Output:
```
✓ Database tables created successfully
✓ Demo user created: username=demo, password=Demo@12345
✓ Database initialization complete!
```

### 3. Download Model (varies by internet speed)

The ViT model will be automatically downloaded on first run. For faster startup:

```bash
python -c "from transformers import ViTForImageClassification; ViTForImageClassification.from_pretrained('google/vit-base-patch16-224-in21k')"
```

### 4. Start Application (1 minute)

```bash
# For SQLite (default)
python -m flask run
```

You should see:
```
* Running on http://127.0.0.1:5000
* Press CTRL+C to quit
```

---

## Upgrade to MongoDB (Optional - Skip if Using SQLite)

Once comfortable with SQLite, you can upgrade to MongoDB for production use.

### MongoDB Quick Setup (5-10 minutes)

**Step 1: Install MongoDB**

```bash
# Windows: Download installer from mongodb.com and run it
# Linux: sudo apt-get install -y mongodb-org && sudo systemctl start mongod
# Mac: brew install mongodb-community && brew services start mongodb-community
```

**Step 2: Update Configuration**

```bash
# Edit .env file and change:
DB_TYPE=mongodb
FLASK_APP=backend/app_mongo_enabled.py
MONGODB_URI=mongodb://localhost:27017/deepfake_detector
MONGODB_DB=deepfake_detector
```

**Step 3: Initialize MongoDB Database**

```bash
python backend/init_mongodb.py
```

Expected output:
```
✓ Connected to MongoDB: mongodb://localhost:27017/deepfake_detector
✓ Indexes created successfully
✓ Demo user created: username=demo, email=demo@example.com
```

**Step 4: Start with MongoDB**

```bash
python -m flask run
```

**Step 5: Verify MongoDB is Active**

```bash
curl http://localhost:5000/api/health
# Should show: "database": "mongodb"
```

### MongoDB Cloud (MongoDB Atlas) - No Installation Needed

Prefer cloud? Use MongoDB Atlas instead:

1. Create free account at https://www.mongodb.com/cloud/atlas
2. Create cluster and database user
3. Whitelist your IP
4. Update .env:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/deepfake_detector
   ```
5. Run: `python backend/init_mongodb.py`

**For Detailed MongoDB Setup**: See [MONGODB_SETUP.md](MONGODB_SETUP.md)

---

### 5. Access Application

Open your browser and go to: **http://localhost:5000**

## First Steps

### Step 1: Login with Demo Account
1. Click "Login" button
2. Username: `demo`
3. Password: `Demo@12345`
4. Click "Login"

### Step 2: Upload an Image
1. Go to Dashboard
2. Click "Upload Image" tab
3. Drag & drop an image (or click to browse)
4. Wait for analysis (usually < 5 seconds)
5. See result: REAL or DEEPFAKE with confidence

### Step 3: View History
1. Click "Detection History" tab
2. See all your detections
3. View details like confidence scores
4. Delete old records if needed

### Step 4: Check Statistics
1. Click "Statistics" tab
2. View summary of your detections
3. Real vs Deepfake count
4. Average confidence

### Step 5: Change Password (Optional)
1. Click "Settings" tab
2. Enter current password
3. Create new password
4. Confirm new password
5. Click "Update Password"

## Testing

### Test with Sample Images

Create test images directory:
```bash
mkdir test_images
```

Place test images in this directory (JPEG, PNG, BMP, or GIF).

### Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_app.py::AuthTestCase -v

# With coverage
pytest --cov=backend tests/
```

## Common Issues & Solutions

### "ModuleNotFoundError: No module named 'transformers'"

```bash
pip install --upgrade transformers torch
```

### "Port 5000 is already in use"

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Model Takes Too Long to Load

This is normal on first run. The model downloads (~350MB). 
For faster subsequent runs, it will be cached.

### Database Error on Startup

```bash
# Delete and recreate database
rm backend/users.db
python backend/init_db.py
```

### CUDA/GPU Issues

If you don't have GPU or get CUDA errors:
```python
# Edit backend/config.py
DEVICE = 'cpu'  # Force CPU
```

## Project Structure

```
deep fake/
├── backend/              # Flask backend
│   ├── app.py           # SQLite version (START HERE)
│   ├── app_mongo_enabled.py  # MongoDB version (for MongoDB)
│   ├── config.py        # Configuration
│   ├── models.py        # SQLite database models
│   ├── mongo_models.py  # MongoDB document schemas
│   ├── auth.py          # SQLite authentication
│   ├── auth_mongo.py    # MongoDB authentication
│   ├── api_routes.py    # SQLite detection API
│   ├── api_routes_mongo.py   # MongoDB detection API
│   ├── deepfake_detector.py  # ViT model (shared)
│   ├── init_db.py       # SQLite database setup
│   ├── init_mongodb.py  # MongoDB database setup
│   └── uploads/         # Uploaded images
├── frontend/            # Web interface (shared)
│   ├── templates/       # HTML pages
│   └── static/          # CSS, JavaScript
├── tests/               # Unit tests
├── models/              # Trained models
├── requirements.txt     # Dependencies (includes MongoDB packages)
├── .env                 # Configuration (DB_TYPE, MONGODB_URI)
├── README.md           # Full documentation
├── MONGODB_SETUP.md    # MongoDB installation guide
├── MONGODB_DEPLOYMENT_GUIDE.md  # Production deployment
└── migrate_database.py  # Database migration tool
```

**Note:** Choose SQLite (app.py) for quick start or MongoDB (app_mongo_enabled.py) for production.

## File Upload Limits & Formats

- **Max Size**: 16 MB
- **Formats**: JPEG, PNG, BMP, GIF
- **Recommended**: JPEG for faster processing

## Performance Tips

1. **Faster Detection**
   - Use GPU: Install CUDA toolkit
   - Smaller images: Pre-resize to 224x224

2. **Better Accuracy**
   - Use high-quality images
   - Face should be clearly visible
   - Good lighting helps

3. **Storage**
   - Delete old detections periodically
   - Backups are created automatically

## Next Steps

After getting comfortable with the app:

1. **Upgrade Database** (Optional):
   - See [MONGODB_SETUP.md](MONGODB_SETUP.md) to upgrade from SQLite to MongoDB
   - Or use [MONGODB_QUICK_REFERENCE.md](MONGODB_QUICK_REFERENCE.md) for quick switching

2. **Production Deployment**:
   - SQLite: See [DEPLOYMENT.md](DEPLOYMENT.md#sqlite-deployment)
   - MongoDB: See [MONGODB_DEPLOYMENT_GUIDE.md](MONGODB_DEPLOYMENT_GUIDE.md)

3. **Custom Training**: See [TRAINING.md](TRAINING.md)

4. **API Integration**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## Getting Help

- **Setup Questions**: See [MONGODB_QUICK_REFERENCE.md](MONGODB_QUICK_REFERENCE.md)
- **Full Documentation**: Check [README.md](README.md)
- **API Usage**: Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Production Deployment**: Check [DEPLOYMENT.md](DEPLOYMENT.md) (SQLite) or [MONGODB_DEPLOYMENT_GUIDE.md](MONGODB_DEPLOYMENT_GUIDE.md) (MongoDB)

## Commands Cheatsheet

### Development (SQLite - Default)
```bash
python -m flask run                 # Start dev server
python backend/init_db.py           # Initialize SQLite
python -m pytest tests/ -v          # Run tests
```

### Development (MongoDB - Optional)
```bash
python -m flask run                 # Start dev server
python backend/init_mongodb.py      # Initialize MongoDB
```

### Database Management
```bash
# SQLite
rm backend/users.db                 # Reset SQLite database
python backend/init_db.py           # Reinitialize SQLite

# MongoDB (Local)
mongosh                             # Connect to MongoDB
use deepfake_detector               # Select database
db.dropDatabase()                   # Reset database
python backend/init_mongodb.py      # Reinitialize MongoDB

# Both: Migrate between databases
python migrate_database.py          # Interactive migration tool
```

### Model Management
```bash
# Download ViT model manually
python -c "from transformers import ViTForImageClassification; ViTForImageClassification.from_pretrained('google/vit-base-patch16-224-in21k')"
```

### Virtual Environment
```bash
python -m venv venv                # Create venv
venv\Scripts\activate              # Activate (Windows)
source venv/bin/activate          # Activate (Linux/Mac)
deactivate                         # Deactivate
```

### Dependency Management
```bash
pip install -r requirements.txt    # Install all dependencies
pip freeze > requirements.txt      # Save installed packages
```

## Default Credentials

**Demo Account** (auto-created for both SQLite and MongoDB):
- Username: `demo`
- Email: `demo@example.com`
- Password: `Demo@12345` (SQLite) or `demo123` (MongoDB)

**Change these immediately in production!**

---

## Database Selection Reference

### Use SQLite When:
- ✅ Learning/experimenting
- ✅ Single developer
- ✅ Quick prototyping
- ✅ Development machine

### Use MongoDB When:
- ✅ Production deployment
- ✅ Scaling to multiple users
- ✅ Team collaboration
- ✅ Cloud deployment
- ✅ Need automatic backups

**Switch anytime**: Just update .env and run appropriate init script.

See [MONGODB_QUICK_REFERENCE.md](MONGODB_QUICK_REFERENCE.md) for database switching guide.

---

**Estimated Time to Full Setup**: 
- SQLite: 10-15 minutes (including first model download)
- MongoDB: 20-25 minutes (including MongoDB installation + model download)

Happy detecting! 🔍
