# MongoDB Implementation Checklist

Complete step-by-step checklist to switch your ViT Deepfake Detector to MongoDB.

---

## 📋 Pre-Implementation (Choose One Path)

### Path A: Local MongoDB (Development)
- [ ] MongoDB Community Edition installed
- [ ] MongoDB service running (`mongosh` connects)
- [ ] Port 27017 accessible
- [ ] ~200MB disk space available

### Path B: MongoDB Atlas (Cloud)
- [ ] MongoDB Atlas account created
- [ ] Free cluster deployed
- [ ] Database user created (username/password)
- [ ] IP whitelisted (or 0.0.0.0/0 for dev)
- [ ] Connection string copied

### Path C: Docker (Any Machine)
- [ ] Docker installed
- [ ] Docker Compose installed (or use `docker run`)
- [ ] ~500MB disk space available

---

## 🔧 Phase 1: Configuration Update

### Step 1: Update .env File

```bash
# Edit: .env

# Old settings (SQLite)
# DB_TYPE=sqlite
# FLASK_APP=backend/app.py
# DATABASE_URL=sqlite:///users.db

# New settings (MongoDB)
DB_TYPE=mongodb
FLASK_APP=backend/app_mongo_enabled.py

# Choose one based on your path:

# Path A: Local MongoDB
MONGODB_URI=mongodb://localhost:27017/deepfake_detector
MONGODB_DB=deepfake_detector

# Path B: MongoDB Atlas
# MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/deepfake_detector?retryWrites=true&w=majority
# MONGODB_DB=deepfake_detector
# (Replace 'username', 'password', 'cluster0.xxxxx' with your values)

# Path C: Docker
# MONGODB_URI=mongodb://mongodb:27017/deepfake_detector
# MONGODB_DB=deepfake_detector
```

- [x] Open `.env` file in your editor
- [x] Update DB_TYPE to 'mongodb'
- [x] Update FLASK_APP to 'backend/app_mongo_enabled.py'
- [x] Add MONGODB_URI (select based on your deployment path)
- [x] Add MONGODB_DB='deepfake_detector'
- [x] Save file

### Step 2: Setup Database Service

**If using Path A (Local MongoDB):**
```bash
# Windows
1. Open Services.msc
2. Find "MongoDB" service
3. Right-click → Start
4. Verify: mongosh command works

# Linux
sudo systemctl start mongod
sudo systemctl enable mongod

# Mac
brew services start mongodb-community
```
- [ ] MongoDB service is running
- [ ] Can connect with: `mongosh`

**If using Path B (MongoDB Atlas):**
```bash
# No action needed - cloud-hosted by MongoDB
# Just verify connection string is correct in .env
```
- [ ] MongoDB Atlas cluster deployed
- [ ] Database user credentials created
- [ ] IP address whitelisted
- [ ] Connection string in .env

**If using Path C (Docker):**
```bash
# This will be handled by docker-compose
# See Phase 3 for Docker setup
```
- [ ] Docker engine running
- [ ] docker-compose available

---

## 📦 Phase 2: Install Dependencies

### Step 3: Update Python Packages

```bash
# Install MongoDB-related packages
pip install mongoengine==3.0.5
pip install pymongo==4.5.0
pip install dnspython==2.4.2

# Or reinstall all dependencies
pip install -r requirements.txt
```

- [ ] mongoengine installed
- [ ] pymongo installed
- [ ] dnspython installed
- [ ] All dependencies verified: `pip list | grep mongo`

---

## 🗄️ Phase 3: Initialize Database

### Step 4: Setup MongoDB Collections

**Option A: Using init script**
```bash
# This creates collections, indexes, and demo user
python backend/init_mongodb.py
```

Expected output:
```
✓ Connected to MongoDB: mongodb://localhost:27017/deepfake_detector
✓ Indexes created successfully
✓ Demo user created: username=demo, email=demo@example.com
```

- [ ] Run: `python backend/init_mongodb.py`
- [ ] Output shows successful connection
- [ ] Output shows indexes created
- [ ] Demo user created

**Option B: Manual setup (advanced)**
```bash
# Connect to MongoDB
mongosh

# Create database and collections
use deepfake_detector

# The collections will be auto-created when app runs
# But you can verify:
db.getCollectionNames()
```

---

## ✅ Phase 4: Verification

### Step 5: Test Database Connection

```bash
# Test 1: Direct MongoDB connection
mongosh "mongodb://localhost:27017/deepfake_detector"

# Should show:
# deepfake_detector>

# Test 2: Check collections created
use deepfake_detector
db.getCollectionNames()
# Should show: [ "users", "detections" ]

# Test 3: Check demo user
db.users.findOne()
# Should show demo user
```

- [ ] Can connect to mongosh
- [ ] Collections exist (users, detections)
- [ ] Demo user exists

### Step 6: Verify Flask Configuration

```bash
# Check configuration
python -c "from config import config; print(config['development'].DB_TYPE)"
# Should output: mongodb

python -c "from config import config; print(config['development'].MONGODB_URI)"
# Should output: your MongoDB URI
```

- [ ] DB_TYPE is 'mongodb'
- [ ] MONGODB_URI is correct
- [ ] MONGODB_DB is set

---

## 🚀 Phase 5: Run Application

### Step 7: Start Flask Application

```bash
# Make sure you're in project root directory

# Windows
set FLASK_ENV=development & python -m flask run

# Linux/Mac
export FLASK_ENV=development && python -m flask run
```

Expected output:
```
WARNING in app.runWarnings ...
 * Running on http://127.0.0.1:5000
```

- [ ] Flask starts without errors
- [ ] Server running on http://localhost:5000
- [ ] No connection error messages

### Step 8: Test API Health Check

```bash
# In another terminal/command prompt
curl http://localhost:5000/api/health

# Should return:
# {
#   "status": "healthy",
#   "database": "mongodb",
#   "message": "Deepfake Detector API running on mongodb"
# }
```

- [ ] Health check returns success
- [ ] Database shows as 'mongodb'
- [ ] No authentication errors

---

## 👤 Phase 6: Test Authentication

### Step 9: Test User Registration

```bash
# Register a new user
curl -X POST http://localhost:5000/auth/register \
  -d "username=testuser&email=test@example.com&password=Test123!"

# Should return success message
```

- [ ] Registration works
- [ ] User created in MongoDB

### Step 10: Test User Login

```bash
# Login with created user
curl -X POST http://localhost:5000/auth/login \
  -d "username_or_email=testuser&password=Test123!" \
  -c cookies.txt

# Should return success message
```

- [ ] Login works
- [ ] Session created

---

## 🖼️ Phase 7: Test Detection

### Step 11: Test Image Upload

```bash
# Upload an image for detection
# (Use frontend or API)

# Via API:
curl -X POST http://localhost:5000/api/detection/upload \
  -F "file=@test_image.jpg" \
  -b cookies.txt

# Should return:
# {
#   "detection_id": "...",
#   "prediction": "REAL" or "DEEPFAKE",
#   "confidence": 0.95,
#   ...
# }
```

- [ ] Image upload works
- [ ] Detection runs
- [ ] Results saved in MongoDB

### Step 12: Test Detection History

```bash
# Get detection history
curl http://localhost:5000/api/detection/history \
  -b cookies.txt

# Should return list of detections
```

- [ ] History retrieval works
- [ ] Pagination works
- [ ] Data persists in MongoDB

---

## 🌐 Phase 8: Web Interface Testing

### Step 13: Test Frontend

Open browser: http://localhost:5000

- [ ] Home page loads
- [ ] Can register new account
- [ ] Can login
- [ ] Can upload image
- [ ] Can view detection results
- [ ] Can view history
- [ ] Can view statistics

---

## 📊 Phase 9: Data Verification

### Step 14: Verify MongoDB Data

```bash
# Connect to MongoDB
mongosh "mongodb://localhost:27017/deepfake_detector"

# View users
db.users.find().pretty()

# View detections
db.detections.find().pretty()

# View statistics
db.detections.aggregate([
  {$group: {_id: "$prediction", count: {$sum: 1}}}
])

# Count total documents
db.users.countDocuments()
db.detections.countDocuments()
```

- [ ] Users collection has records
- [ ] Detections collection has records
- [ ] Data is properly indexed
- [ ] Statistics queries work

---

## 🔄 Phase 10: Optional - Data Migration

### Step 15: Migrate Existing Data (if from SQLite)

```bash
# If you had data in SQLite, migrate it
python migrate_database.py

# Follow prompts:
# Select option: 1 (SQLite → MongoDB)
# Confirm migration

# Expected output:
# ✓ Migrated X users
# ✓ Migrated Y detections
# ✓ Migration completed successfully!
```

- [ ] Ran migration script (if needed)
- [ ] Migration completed successfully
- [ ] Old data verified in MongoDB
- [ ] No data loss

---

## 🐳 Phase 11: Optional - Docker Deployment

### Step 16: Deploy with Docker

```bash
# Create appropriate docker-compose setup
# For MongoDB enabled setup:
docker-compose -f docker-compose-mongodb.yml up -d

# Verify containers are running
docker-compose ps

# Initialize database
docker-compose exec deepfake-web python backend/init_mongodb.py

# Check logs
docker-compose logs -f deepfake-web

# Access application
# http://localhost:5000
```

- [ ] Docker containers started
- [ ] Services are healthy
- [ ] Database initialized
- [ ] Application accessible

---

## 🎓 Phase 12: Final Verification

### Step 17: Complete Verification Checklist

```bash
# 1. Check environment
echo $FLASK_APP
# Should output: backend/app_mongo_enabled.py

# 2. Check database connection
curl http://localhost:5000/api/health
# Should show: "database": "mongodb"

# 3. Check MongoDB directly
mongosh
use deepfake_detector
db.stats()
# Should show database statistics

# 4. Check data integrity
python -c "
from mongo_models import MongoUser
users = MongoUser.objects.all()
print(f'Total users: {len(users)}')
"
```

- [ ] FLASK_APP is set to app_mongo_enabled.py
- [ ] Health check shows MongoDB
- [ ] MongoDB is accessible
- [ ] Data is intact

---

## 📝 Phase 13: Documentation & Backup

### Step 18: Backup Your Setup

```bash
# Backup MongoDB data
mongodump --uri="mongodb://localhost:27017/deepfake_detector" \
          --out=./backup/

# Backup configuration
cp .env .env.backup
cp config.py config.py.backup
```

- [ ] Created backup directory
- [ ] MongoDB data backed up
- [ ] Configuration backed up

### Step 19: Document Your Setup

Create a setup log:
```bash
# setup_log.txt
MongoDB Implementation Date: 2024-XX-XX
Database Type: mongodb
Connection String: mongodb://localhost:27017/deepfake_detector
Total Users: X
Total Detections: Y
Backup Location: ./backup/
```

- [ ] Created setup log
- [ ] Documented connection details
- [ ] Noted backup location

---

## 🆘 Troubleshooting

### If Something Fails

**Error: "Cannot connect to MongoDB"**
- [ ] MongoDB service is running
- [ ] Check connection string in .env
- [ ] Verify port 27017 is accessible
- [ ] Run: `mongosh` to test connection

**Error: "Module not found"**
- [ ] Reinstall dependencies: `pip install -r requirements.txt`
- [ ] Check if mongoengine is installed: `pip show mongoengine`

**Error: "Database initialization failed"**
- [ ] Ensure MongoDB is running
- [ ] Check .env MONGODB_URI is correct
- [ ] Clear old database if corrupted: `db.dropDatabase()`
- [ ] Reinitialize: `python backend/init_mongodb.py`

**Error: "Permission denied"**
- [ ] Check file permissions on .env
- [ ] Check MongoDB user permissions
- [ ] For MongoDB Atlas: verify IP is whitelisted

**Error: "Port already in use"**
- [ ] Use different port: `flask run --port 5001`
- [ ] Or kill process using port 5000

---

## ✨ Success Indicators

You've successfully migrated to MongoDB when:

- [x] Application runs without errors
- [x] Health check shows "mongodb"
- [x] Can create user accounts
- [x] Can upload images for detection
- [x] Results are saved and retrievable
- [x] Data persists after app restart
- [x] MongoDB has collections with data
- [x] Frontend works perfectly
- [x] API endpoints respond correctly

---

## 📞 Getting Help

1. **Quick Questions:** See MONGODB_QUICK_REFERENCE.md
2. **Setup Issues:** See MONGODB_SETUP.md
3. **Deployment:** See MONGODB_DEPLOYMENT_GUIDE.md
4. **Technical Details:** See MONGODB_MIGRATION_SUMMARY.md

---

## 🎉 Completion

Once all phases are complete:

✅ MongoDB is configured and running
✅ Application connects successfully
✅ Data is saved and retrieved correctly
✅ Backup is in place
✅ Ready for production use

**Congratulations! Your ViT Deepfake Detector is now MongoDB-enabled!** 🚀

---

**Checklist Version:** 1.0
**Last Updated:** After MongoDB Migration
**Status:** Ready for Implementation
