# MongoDB Setup and Startup Guide

## Prerequisites

### Install MongoDB Community Edition

#### Windows
1. Download MongoDB from: https://www.mongodb.com/try/download/community
2. Run the installer and follow the setup wizard
3. MongoDB will be installed as a Windows Service (mongod) by default
4. Verify installation: Open PowerShell and run `mongosh`

#### Linux (Ubuntu)
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### macOS
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

## Configuration Options

### Option 1: Local MongoDB (Default)
In `.env`:
```
DB_TYPE=mongodb
MONGODB_URI=mongodb://localhost:27017/deepfake_detector
MONGODB_DB=deepfake_detector
```

### Option 2: MongoDB Atlas (Cloud)
In `.env`:
```
DB_TYPE=mongodb
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/deepfake_detector?retryWrites=true&w=majority
MONGODB_DB=deepfake_detector
```

1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Create database user and get connection string
4. Replace `username`, `password`, and `cluster` in URI above

## Installation Steps

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Update Flask app reference in .env:
```
FLASK_APP=backend/app_mongo_enabled.py
```

3. Initialize MongoDB (creates demo user):
```bash
python backend/init_mongodb.py
```

Expected output:
```
✓ Connected to MongoDB: mongodb://localhost:27017/deepfake_detector
✓ Indexes created successfully
Demo user: username=demo, email=demo@example.com
```

## Running the Application

### Using Python (Development)
```bash
# Windows
set FLASK_ENV=development & python -m flask run

# Linux/Mac
export FLASK_ENV=development && python -m flask run
```

### Using Gunicorn (Production)
```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 "backend.app_mongo_enabled:create_app()"
```

### Using Docker Compose (with MongoDB Container)
```bash
docker-compose up
```

## Verify MongoDB Connection

1. Check MongoDB is running:
```bash
# Windows (Admin CMD)
sc query MongoDB

# Linux/Mac
sudo systemctl status mongod
```

2. Test connection:
```bash
mongosh "mongodb://localhost:27017"
```

3. Check collections in database:
```
use deepfake_detector
db.getCollectionNames()
```

## API Health Check

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "mongodb",
  "message": "Deepfake Detector API running on mongodb"
}
```

## Switching Between SQLite and MongoDB

### To Switch to SQLite:
In `.env`:
```
DB_TYPE=sqlite
FLASK_APP=backend/app.py
```

### To Switch to MongoDB:
In `.env`:
```
DB_TYPE=mongodb
FLASK_APP=backend/app_mongo_enabled.py
```

**Note:** Data is NOT automatically migrated between databases. You'll need to create new accounts and re-upload images.

## Data Structure in MongoDB

### Collections Created:
- `users` - User accounts (username, email, password_hash)
- `detections` - Detection results (prediction, confidence, user_id, timestamp)

### Example MongoDB Query:
```bash
mongosh
use deepfake_detector

# View all users
db.users.find()

# View all detections for a user
db.detections.find({user_id: ObjectId("...")})

# Get statistics
db.detections.aggregate([
  {$group: {_id: "$prediction", count: {$sum: 1}}}
])
```

## Troubleshooting

### Error: "Refusing to connect"
- Ensure MongoDB is running: `mongosh`
- Check MONGODB_URI in .env file
- For Atlas: Add your IP to IP Whitelist

### Error: "authentication failed"
- MongoDB Atlas: Verify username/password
- Local MongoDB: May need to disable auth or create user

### Error: "pymongo.errors.ServerSelectionTimeoutError"
- MongoDB service not running
- Wrong connection string
- Network connectivity issue

### Clear Database (MongoDB)
```bash
mongosh
use deepfake_detector
db.users.deleteMany({})
db.detections.deleteMany({})
```

## MongoDB Monitoring

### Using MongoDB Compass (GUI)
1. Download: https://www.mongodb.com/try/download/compass
2. Connect to: `mongodb://localhost:27017`
3. Browse databases, collections, and documents visually

### Command Line:
```bash
# Connect to database
mongosh "mongodb://localhost:27017/deepfake_detector"

# View users
db.users.find().pretty()

# View recent detections
db.detections.find().sort({created_at: -1}).limit(10)

# Get total count
db.detections.countDocuments({})
```

## Performance Tips

1. **Indexes**: Already created on username, email, and user_id fields
2. **Connection Pooling**: Handled automatically by MongoEngine
3. **Pagination**: Use limit and skip for large result sets
4. **Aggregation**: Use MongoDB aggregation pipeline for complex queries

## Next Steps

1. Update your application to use `app_mongo_enabled.py`
2. Install MongoDB on your system
3. Run `init_mongodb.py` to initialize database
4. Create user account through web interface
5. Start uploading images for deepfake detection
