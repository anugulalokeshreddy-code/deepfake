# MongoDB Deployment Guide

Complete guide for deploying the ViT Deepfake Detector with MongoDB support.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud MongoDB (Atlas)](#cloud-mongodb-atlas)
4. [Production Checklist](#production-checklist)
5. [Performance Tuning](#performance-tuning)

## Local Development

### Quick Setup (5 minutes)

#### Prerequisites
- Windows: MongoDB Community Edition or Docker
- Linux: `sudo apt-get install -y mongodb-org`
- Mac: `brew install mongodb-community`

#### Steps

1. **Install MongoDB Community Edition**
   ```bash
   # Windows
   # Download from https://www.mongodb.com/try/download/community
   # Run installer, check "Install MongoDB as a Service"
   
   # Verify installation
   mongosh --version
   ```

2. **Configure Application**
   ```bash
   # Edit .env file
   DB_TYPE=mongodb
   FLASK_APP=backend/app_mongo_enabled.py
   MONGODB_URI=mongodb://localhost:27017/deepfake_detector
   MONGODB_DB=deepfake_detector
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python backend/init_mongodb.py
   ```

5. **Run Application**
   ```bash
   python -m flask run
   ```

6. **Access Application**
   - Web: http://localhost:5000
   - MongoDB: `mongosh localhost:27017`
   - Demo User: username=demo, password=demo123

### Development Tools

#### MongoDB Compass (GUI Client)
```bash
# Download from https://www.mongodb.com/try/download/compass

# Connect to:
mongodb://localhost:27017

# Browse databases and documents visually
```

#### MongoDB Shell (Command Line)
```bash
# Connect to local MongoDB
mongosh "mongodb://localhost:27017"

# Common commands
use deepfake_detector
db.users.find()
db.detections.find().limit(5)
db.detections.countDocuments()
```

---

## Docker Deployment

### Option 1: Using Docker Compose with MongoDB

#### Quick Start
```bash
# Create .env file with MongoDB settings
cat > .env << EOF
DB_TYPE=mongodb
FLASK_APP=backend/app_mongo_enabled.py
MONGODB_URI=mongodb://mongodb:27017/deepfake_detector
MONGODB_DB=deepfake_detector
SECRET_KEY=your-secure-secret-key-here
DEVICE=cpu
EOF

# Start services
docker-compose -f docker-compose-mongodb.yml up -d

# Verify services
docker-compose ps
# Expected: deepfake-web, mongodb, mongodb-express (if enabled)

# Initialize database
docker-compose exec deepfake-web python backend/init_mongodb.py

# View logs
docker-compose logs -f deepfake-web
```

#### Services Created

**deepfake-web** (Flask API)
- Port: 5000
- Health Check: http://localhost:5000/api/health

**mongodb** (Database)
- Port: 27017
- Default User: admin
- Default Password: password (change in production)

**mongodb-express** (Web UI - optional)
- Port: 8081
- Access: http://localhost:8081
- Default User: admin
- Enable with: `--profile mongodb-ui`

#### Useful Commands

```bash
# Stop services
docker-compose -f docker-compose-mongodb.yml down

# View database logs
docker-compose -f docker-compose-mongodb.yml logs mongodb

# Access MongoDB shell
docker-compose exec mongodb mongosh -u admin -p password

# Backup database
docker-compose exec mongodb mongodump --uri="mongodb://admin:password@localhost:27017/deepfake_detector" --out=/data/backup

# Scale services
docker-compose -f docker-compose-mongodb.yml up -d --scale deepfake-web=3
```

### Option 2: MongoDB Container Only

If you want to run MongoDB in Docker but keep Flask local:

```bash
# Start MongoDB container
docker run -d \
  --name deepfake-mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:7.0

# Configure .env
MONGODB_URI=mongodb://admin:password@localhost:27017/deepfake_detector

# Run Flask locally
pip install -r requirements.txt
python backend/init_mongodb.py
python -m flask run
```

---

## Cloud MongoDB (Atlas)

### Setup MongoDB Atlas

#### Step 1: Create MongoDB Atlas Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for free account
3. Create an organization and project

#### Step 2: Create Free Cluster
1. Click "Create a Deployment"
2. Select "Free" tier
3. Choose cloud provider (AWS, Azure, Google Cloud)
4. Choose region (pick closest to you)
5. Click "Create Deployment"
6. Wait for cluster to be ready (5-10 minutes)

#### Step 3: Create Database User
1. Go to "Database Access" → "Add New Database User"
2. Username: `deepfake_user`
3. Password: Generate secure password
4. Permissions: "Read and write to any database"
5. Click "Add User"

#### Step 4: Whitelist IP Address
1. Go to "Network Access" → "Add IP Address"
2. Option A: Add current IP
3. Option B: Allow access from anywhere (0.0.0.0/0) - DEVELOPMENT ONLY
4. Click "Allow"

#### Step 5: Get Connection String
1. Click "Connect" on cluster
2. Select "Drivers"
3. Choose "Python" and version "Latest"
4. Copy connection string
5. Format: `mongodb+srv://user:password@cluster.mongodb.net/deepfake_detector`

### Configure for Atlas

```bash
# Update .env
DB_TYPE=mongodb
MONGODB_URI=mongodb+srv://deepfake_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/deepfake_detector?retryWrites=true&w=majority
MONGODB_DB=deepfake_detector

# Install dnspython (required for MongoDB Atlas)
pip install dnspython

# Initialize database
python backend/init_mongodb.py

# Run application
python -m flask run
```

### Atlas Dashboard Features

- **Monitoring:** CPU, memory, network usage
- **Performance Advisor:** Optimization suggestions
- **Backup:** Automatic daily backups
- **Scaling:** Auto-scale storage and compute
- **Search:** Full-text search on data

### Pricing

- **Free Tier:** 512MB storage, shared cluster
- **Shared Tier:** $9/month, auto-scaling
- **Dedicated Tier:** $57+/month, dedicated instance

---

## Production Checklist

### Security

- [ ] Change default MongoDB credentials
- [ ] Enable IP whitelisting (not 0.0.0.0/0)
- [ ] Use strong SECRET_KEY
- [ ] Enable SSL/TLS for MongoDB connections
- [ ] Enable MongoDB authentication
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS on web server
- [ ] Set Flask DEBUG=False

```bash
# Example secure .env for production
FLASK_ENV=production
FLASK_DEBUG=False
DB_TYPE=mongodb
MONGODB_URI=mongodb+srv://user:complex-password@cluster.mongodb.net/deepfake_detector?ssl=true
SECRET_KEY=generate-with: python -c "import secrets; print(secrets.token_hex(32))"
MAX_CONTENT_LENGTH=16777216
DEVICE=cuda  # if GPU available
```

### Database

- [ ] Enable MongoDB backup and recovery
- [ ] Set up automated backups
- [ ] Test backup restoration
- [ ] Monitor database size
- [ ] Create indexes on frequently queried fields
- [ ] Monitor query performance

### Deployment

- [ ] Use gunicorn (Flask development server is not production-ready)
- [ ] Use nginx as reverse proxy
- [ ] Configure load balancing
- [ ] Enable gzip compression
- [ ] Set up monitoring and logging
- [ ] Configure health checks
- [ ] Set up alerting

### Performance

- [ ] Test with realistic load
- [ ] Monitor response times
- [ ] Optimize database queries
- [ ] Enable caching where appropriate
- [ ] Monitor MongoDB memory usage
- [ ] Check for N+1 queries

---

## Performance Tuning

### MongoDB Indexing

```javascript
// Connect to MongoDB
mongosh

// View indexes
db.users.getIndexes()
db.detections.getIndexes()

// Create additional indexes if needed
db.detections.createIndex({user_id: 1, created_at: -1})
db.detections.createIndex({prediction: 1})

// Monitor index usage
db.users.aggregate([{$indexStats: {}}])
```

### Query Optimization

```python
# Use pagination for large result sets
detections = MongoDetection.objects(user_id=user_id).skip(0).limit(10)

# Use projection to fetch only needed fields
detections = MongoDetection.objects(user_id=user_id).only('prediction', 'confidence')

# Use aggregation for complex queries
pipeline = [
    {'$match': {'user_id': user_id}},
    {'$group': {'_id': '$prediction', 'count': {'$sum': 1}}},
    {'$sort': {'count': -1}}
]
results = db.detections.aggregate(pipeline)
```

### Connection Pooling

```python
# MongoEngine handles connection pooling automatically
# Configure in config.py:
MONGODB_URI = 'mongodb://localhost:27017/db?maxPoolSize=50'
```

### Monitoring Commands

```bash
# Check database statistics
mongosh
db.stats()
db.detections.stats()

# Current operations
db.currentOp()

# Kill slow operation
db.killOp(123)  # operation id

# Check connections
db.serverStatus().connections
```

---

## Troubleshooting

### Connection Issues

```bash
# Test MongoDB is accessible
mongosh "mongodb://localhost:27017"

# If using Atlas, verify:
# - IP is whitelisted
# - Password is correct
# - Special characters in password are URL encoded
```

### Performance Issues

```bash
# Check slow queries
db.setProfilingLevel(1, {slowms: 100})  # Log queries > 100ms
db.system.profile.find().sort({ts: -1}).limit(5).pretty()

# Find large collections
db.getCollectionNames().forEach(c => {
    console.log(c + ': ' + db[c].dataSize() + ' bytes')
})

# Check indexes
db.users.stats()
db.detections.stats()
```

### Memory Issues

```bash
# MongoDB memory usage
db.serverStatus().mem

# Check WiredTiger cache
db.serverStatus().wiredTiger.cache

# Reduce cache size in mongod.conf
storage:
    wiredTiger:
        engineConfig:
            cacheSizeGB: 1
```

---

## Docker Production Stack

### docker-compose-prod.yml

```yaml
version: '3.8'

services:
  deepfake-web:
    image: deepfake-detector:latest
    environment:
      FLASK_ENV: production
      DB_TYPE: mongodb
      MONGODB_URI: ${MONGODB_URI}
    ports:
      - "5000:5000"
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  mongodb:
    image: mongo:7.0
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - mongodb_config:/data/configdb
    restart: always
    command: --auth

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - deepfake-web
    restart: always

volumes:
  mongodb_data:
  mongodb_config:
```

---

## Support & Resources

- **MongoDB Docs:** https://docs.mongodb.com/
- **MongoDB Atlas:** https://www.mongodb.com/cloud/atlas
- **MongoEngine Docs:** http://docs.mongoengine.org/
- **Docker Docs:** https://docs.docker.com/
- **Flask Docs:** https://flask.palletsprojects.com/

---

**Status: ✓ MONGODB DEPLOYMENT READY**

Your application is fully configured to run with MongoDB in development, staging, and production environments.
