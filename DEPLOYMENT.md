# Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Azure Deployment](#azure-deployment)
4. [AWS Deployment](#aws-deployment)
5. [Production Checklist](#production-checklist)

## Local Development

### Setup
```bash
# Navigate to project
cd "deep fake"

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Download ViT model (first run)
python -c "from transformers import ViTForImageClassification; ViTForImageClassification.from_pretrained('google/vit-base-patch16-224-in21k')"

# Run development server
python backend/app.py
```

Visit `http://localhost:5000`

## Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p backend/uploads

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:create_app()"]
```

### Build and Run

```bash
# Build image
docker build -t vit-deepfake:latest .

# Run container
docker run -d \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your_secret_key \
  -v /path/to/uploads:/app/backend/uploads \
  --name deepfake-app \
  vit-deepfake:latest

# Check logs
docker logs deepfake-app

# Stop container
docker stop deepfake-app
```

### Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
      SECRET_KEY: ${SECRET_KEY}
      DATABASE_URL: sqlite:///users.db
    volumes:
      - ./backend/uploads:/app/backend/uploads
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: always
```

## Azure Deployment

### Prerequisites
- Azure subscription
- Azure CLI installed
- Docker installed

### Steps

1. **Create Resource Group**
```bash
az group create --name deepfake-rg --location eastus
```

2. **Create Container Registry**
```bash
az acr create --resource-group deepfake-rg \
  --name deepfakeregistry --sku Basic
```

3. **Build and Push Image**
```bash
# Login to registry
az acr login --name deepfakeregistry

# Build image
az acr build --registry deepfakeregistry \
  --image vit-deepfake:latest .

# Get login server
az acr show --name deepfakeregistry \
  --query loginServer --output tsv
```

4. **Create App Service Plan**
```bash
az appservice plan create --name deepfake-plan \
  --resource-group deepfake-rg \
  --sku B2 --is-linux
```

5. **Create Web App**
```bash
az webapp create --resource-group deepfake-rg \
  --plan deepfake-plan \
  --name vit-deepfake-app \
  --deployment-container-image-name deepfakeregistry.azurecr.io/vit-deepfake:latest
```

6. **Configure Settings**
```bash
az webapp config app-settings set \
  --resource-group deepfake-rg \
  --name vit-deepfake-app \
  --settings \
    FLASK_ENV=production \
    SECRET_KEY="your_secret_key" \
    WEBSITES_PORT=5000
```

7. **Setup Database**
```bash
# Create Azure SQL Database (optional)
az sql server create --name deepfake-server \
  --resource-group deepfake-rg \
  --admin-user azureuser \
  --admin-password P@ssw0rd123!
```

## AWS Deployment

### Using EC2

1. **Launch EC2 Instance**
```bash
# Using AWS CLI
aws ec2 run-instances --image-id ami-0c55b159cbfafe1f0 \
  --count 1 --instance-type t3.medium \
  --key-name my-key-pair \
  --security-groups webserver
```

2. **Connect to Instance**
```bash
ssh -i my-key.pem ubuntu@instance-ip
```

3. **Install Dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv git

# Install CUDA (optional, for GPU)
# Follow NVIDIA CUDA installation guide
```

4. **Deploy Application**
```bash
# Clone repository
git clone <your-repo-url>
cd "deep fake"

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download model
python -c "from transformers import ViTForImageClassification; ViTForImageClassification.from_pretrained('google/vit-base-patch16-224-in21k')"

# Run with gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:create_app()
```

### Using Elastic Beanstalk

1. **Install EB CLI**
```bash
pip install awsebcli --upgrade --user
```

2. **Initialize Application**
```bash
eb init -p python-3.11 vit-deepfake
```

3. **Create Environment**
```bash
eb create deepfake-env
```

4. **Deploy**
```bash
eb deploy
```

## Production Checklist

### Security
- [ ] Set strong SECRET_KEY in production
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure CORS properly
- [ ] Implement rate limiting
- [ ] Add CSRF protection
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] Input validation on all endpoints

### Performance
- [ ] Enable caching (Redis)
- [ ] Database indexing
- [ ] CDN for static assets
- [ ] Compression (gzip)
- [ ] Image optimization
- [ ] Model quantization (int8)
- [ ] Async task processing (Celery)

### Monitoring
- [ ] Application logging
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Database backup strategy
- [ ] Log aggregation (ELK stack)

### Infrastructure
- [ ] Load balancer
- [ ] Auto-scaling policies
- [ ] Database replication
- [ ] Disaster recovery plan
- [ ] DDoS protection
- [ ] Network isolation

### Maintenance
- [ ] Regular model retraining
- [ ] Dependency updates
- [ ] Security patching
- [ ] Database optimization
- [ ] Backup testing
- [ ] Documentation updates

## Environment Variables (Production)

Create `.env.production`:
```
FLASK_ENV=production
SECRET_KEY=generate_with_secrets.token_urlsafe(32)
DATABASE_URL=postgresql://user:password@host/database
MODEL_PATH=/var/models/vit_deepfake_detector.pth
UPLOAD_FOLDER=/var/uploads
MAX_CONTENT_LENGTH=16777216
DEVICE=cuda
USE_GPU=true
SQLALCHEMY_ECHO=false
```

## Nginx Configuration

```nginx
upstream deepfake_app {
    server localhost:5000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    client_max_body_size 16M;
    
    location / {
        proxy_pass http://deepfake_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /var/www/vit-deepfake/frontend/static;
        expires 30d;
    }
}
```

## Systemd Service (Linux)

Create `/etc/systemd/system/deepfake.service`:
```ini
[Unit]
Description=ViT Deepfake Detector
After=network.target

[Service]
Type=notify
User=deepfake
WorkingDirectory=/opt/vit-deepfake
Environment="PATH=/opt/vit-deepfake/venv/bin"
ExecStart=/opt/vit-deepfake/venv/bin/gunicorn \
    -w 4 -b 0.0.0.0:5000 \
    backend.app:create_app()
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable deepfake
sudo systemctl start deepfake
sudo systemctl status deepfake
```

## Troubleshooting

### Out of Memory
- Reduce batch size
- Enable swap
- Use lighter model variant
- Implement caching

### Slow Inference
- Use GPU acceleration
- Enable model quantization
- Implement batching
- Cache frequently accessed images

### Database Issues
- Check connection string
- Verify permissions
- Run migrations
- Check disk space

### SSL Certificate Issues
- Use Let's Encrypt
- Auto-renewal setup
- Certificate pinning

---

For additional help, refer to the main README.md
