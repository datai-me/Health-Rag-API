# Deployment Guide

## 🚀 Production Deployment Guide

This guide covers deploying the Health RAG API to production environments.

## Prerequisites

- Python 3.9+
- PostgreSQL 13+ (recommended for production)
- Redis (optional, for caching)
- Nginx (for reverse proxy)
- SSL certificate (Let's Encrypt recommended)

## 🔧 Environment Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql

postgres=# CREATE DATABASE health_rag_prod;
postgres=# CREATE USER health_rag_user WITH PASSWORD 'your_secure_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE health_rag_prod TO health_rag_user;
postgres=# \q
```

### 3. Application Setup

```bash
# Clone repository
git clone <repository-url>
cd health_rag_api

# Install dependencies
poetry install --only main

# Copy and configure environment
cp .env.example .env
nano .env  # Edit with production values
```

### 4. Production Environment Variables

```bash
# .env for production
APP_NAME=Health RAG API
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://health_rag_user:your_secure_password@localhost/health_rag_prod

# Security
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
GROQ_API_KEY=your-production-groq-key
JINA_API_KEY=your-production-jina-key

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 🐳 Docker Deployment

### 1. Build Docker Image

```bash
docker build -t health-rag-api:latest .
```

### 2. Run with Docker Compose

```bash
# Start all services (with PostgreSQL)
docker-compose --profile with-postgres up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### 3. Docker Compose Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: health-rag-api:latest
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env.prod
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  postgres:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_DB: health_rag_prod
      POSTGRES_USER: health_rag_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api

volumes:
  postgres_data:
```

## 🔒 Nginx Configuration

### 1. Create Nginx Config

```nginx
# /etc/nginx/sites-available/health-rag-api
upstream api_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/health-rag-api-access.log;
    error_log /var/log/nginx/health-rag-api-error.log;

    # Proxy to API
    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}
```

### 2. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/health-rag-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔐 SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal is set up automatically
sudo certbot renew --dry-run
```

## 🎯 Systemd Service

### 1. Create Service File

```bash
# /etc/systemd/system/health-rag-api.service
[Unit]
Description=Health RAG API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/health_rag_api
Environment="PATH=/opt/health_rag_api/.venv/bin"
ExecStart=/opt/health_rag_api/.venv/bin/gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/health-rag-api/access.log \
    --error-logfile /var/log/health-rag-api/error.log \
    --log-level info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable health-rag-api
sudo systemctl start health-rag-api
sudo systemctl status health-rag-api
```

## 📊 Monitoring

### 1. Application Logs

```bash
# View systemd logs
sudo journalctl -u health-rag-api -f

# View application logs
tail -f /var/log/health-rag-api/error.log
```

### 2. Health Checks

```bash
# Check API health
curl https://api.yourdomain.com/api/v1/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "service": "Health RAG API"
}
```

## 🔄 Deployment Workflow

### 1. Zero-Downtime Deployment

```bash
#!/bin/bash
# deploy.sh

set -e

echo "Pulling latest changes..."
git pull origin main

echo "Installing dependencies..."
poetry install --only main

echo "Running database migrations..."
# poetry run alembic upgrade head

echo "Restarting service..."
sudo systemctl restart health-rag-api

echo "Checking service status..."
sudo systemctl status health-rag-api

echo "Deployment complete!"
```

### 2. Rollback Procedure

```bash
#!/bin/bash
# rollback.sh

set -e

echo "Rolling back to previous version..."
git checkout HEAD^

echo "Installing dependencies..."
poetry install --only main

echo "Restarting service..."
sudo systemctl restart health-rag-api

echo "Rollback complete!"
```

## 🛡️ Security Checklist

- [ ] Use strong SECRET_KEY (32+ characters)
- [ ] Enable HTTPS only
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Set up firewall (UFW)
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor logs for suspicious activity
- [ ] Use non-root user for application

## 📈 Performance Optimization

### 1. Gunicorn Workers

```bash
# Calculate workers: (2 x CPU cores) + 1
# For 4 CPU cores: (2 x 4) + 1 = 9 workers

gunicorn app.main:app \
    -w 9 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

### 2. Database Connection Pooling

```python
# In config.py
engine = create_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

### 3. Redis Caching (Optional)

```python
# Add Redis for caching
# pip install redis

from redis import Redis
redis_client = Redis(host='localhost', port=6379, db=0)
```

## 🔍 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   sudo journalctl -u health-rag-api -n 50
   ```

2. **Database connection errors**
   ```bash
   # Test PostgreSQL connection
   psql -h localhost -U health_rag_user -d health_rag_prod
   ```

3. **Port already in use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

## 📞 Support

For production issues:
- Check logs: `/var/log/health-rag-api/`
- Review systemd status: `sudo systemctl status health-rag-api`
- Monitor health endpoint: `/api/v1/health`
