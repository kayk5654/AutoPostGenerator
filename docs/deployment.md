# Deployment Guide

This guide covers various deployment options for the Auto Post Generator application, from local development to production cloud deployments.

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- Git (for version control)
- Docker (for containerized deployment)
- LLM provider API keys

## 🏠 Local Development

### Standard Setup

1. **Environment Setup**
   ```bash
   git clone <repository-url>
   cd AutoPostGenerator
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   # Create environment configuration
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run Application**
   ```bash
   streamlit run app.py
   ```

4. **Access Application**
   - Open browser to `http://localhost:8501`
   - The application will be available immediately

### Development with Hot Reload

```bash
streamlit run app.py --server.fileWatcherType auto
```

## 🐳 Docker Deployment

### Build Docker Image

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

### Build and Run

```bash
# Build image
docker build -t auto-post-generator .

# Run container
docker run -p 8501:8501 \\
  -e LOG_LEVEL=INFO \\
  -v $(pwd)/logs:/app/logs \\
  auto-post-generator
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    environment:
      - LOG_LEVEL=INFO
      - LOG_FILE=logs/app.log
      - LOG_FORMAT=json
      - LOG_CONSOLE=0
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with Docker Compose:
```bash
docker-compose up -d
```

## ☁️ Cloud Deployment

### Streamlit Cloud

1. **Prerequisites**
   - GitHub repository
   - Streamlit Cloud account

2. **Setup**
   - Fork/upload repository to GitHub
   - Connect to Streamlit Cloud
   - Configure secrets for API keys

3. **Configuration**
   Create `.streamlit/secrets.toml`:
   ```toml
   [general]
   LOG_LEVEL = "INFO"
   
   # Add API keys as secrets in Streamlit Cloud UI
   ```

4. **Deployment**
   - Automatic deployment on push to main branch
   - Custom domain support available

### Heroku Deployment

1. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

2. **Create Procfile**
   ```
   web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```

3. **Configure Environment**
   ```bash
   heroku config:set LOG_LEVEL=INFO
   heroku config:set LOG_FORMAT=json
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### AWS Deployment

#### Option 1: AWS App Runner

1. **Create apprunner.yaml**
   ```yaml
   version: 1.0
   runtime: python3
   build:
     commands:
       build:
         - pip install -r requirements.txt
   run:
     runtime-version: 3.11
     command: streamlit run app.py --server.address 0.0.0.0 --server.port 8080
     network:
       port: 8080
       env:
         - LOG_LEVEL=INFO
         - LOG_FORMAT=json
   ```

2. **Deploy via AWS Console**
   - Create App Runner service
   - Connect to GitHub repository
   - Configure environment variables

#### Option 2: AWS ECS with Fargate

1. **Build and Push to ECR**
   ```bash
   # Create ECR repository
   aws ecr create-repository --repository-name auto-post-generator
   
   # Build and push image
   docker build -t auto-post-generator .
   docker tag auto-post-generator:latest <account-id>.dkr.ecr.<region>.amazonaws.com/auto-post-generator:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/auto-post-generator:latest
   ```

2. **Create ECS Task Definition**
   ```json
   {
     "family": "auto-post-generator",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "executionRoleArn": "arn:aws:iam::<account>:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "auto-post-generator",
         "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/auto-post-generator:latest",
         "portMappings": [
           {
             "containerPort": 8501,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "LOG_LEVEL",
             "value": "INFO"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/auto-post-generator",
             "awslogs-region": "<region>",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

### Google Cloud Platform

#### Cloud Run Deployment

1. **Build and Deploy**
   ```bash
   gcloud run deploy auto-post-generator \\
     --source . \\
     --platform managed \\
     --region us-central1 \\
     --allow-unauthenticated \\
     --port 8501 \\
     --memory 1Gi \\
     --cpu 1 \\
     --set-env-vars LOG_LEVEL=INFO,LOG_FORMAT=json
   ```

2. **Custom Domain**
   ```bash
   gcloud run domain-mappings create \\
     --service auto-post-generator \\
     --domain your-domain.com
   ```

### Azure Deployment

#### Container Instances

1. **Deploy Container**
   ```bash
   az container create \\
     --resource-group myResourceGroup \\
     --name auto-post-generator \\
     --image auto-post-generator:latest \\
     --dns-name-label auto-post-generator \\
     --ports 8501 \\
     --environment-variables LOG_LEVEL=INFO
   ```

## 🔧 Production Configuration

### Environment Variables

```bash
# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_FORMAT=json
LOG_CONSOLE=0

# Application Limits
MAX_FILE_SIZE_MB=10
MAX_POSTS_PER_REQUEST=50

# Security
SECURE_HEADERS=true
SESSION_TIMEOUT=3600
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL/TLS Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    location / {
        proxy_pass http://localhost:8501;
        # ... proxy settings
    }
}
```

## 📊 Monitoring and Health Checks

### Health Check Endpoint

Streamlit provides a built-in health check at `/_stcore/health`

### Application Monitoring

```python
# Add to app.py for custom health metrics
import psutil
import time

def get_health_metrics():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent(),
        "uptime": time.time() - start_time
    }
```

### Logging Configuration for Production

```python
# Production logging setup
from utils.logging_config import configure_production_logging

configure_production_logging()
```

## 🔒 Security Considerations

### API Key Management

1. **Use Environment Variables**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   export GOOGLE_API_KEY="your-key-here"
   export ANTHROPIC_API_KEY="your-key-here"
   ```

2. **Cloud Secret Management**
   - AWS Secrets Manager
   - Google Secret Manager
   - Azure Key Vault
   - Kubernetes Secrets

### Network Security

1. **Firewall Rules**
   - Only allow necessary ports (80, 443, 8501)
   - Restrict access to admin interfaces

2. **Rate Limiting**
   - Implement at reverse proxy level
   - Use cloud provider rate limiting services

3. **HTTPS Only**
   - Force HTTPS redirects
   - Use HSTS headers

### Application Security

1. **Input Validation**
   - File size limits
   - File type restrictions
   - Content validation

2. **Sensitive Data Protection**
   - Automatic log filtering
   - No persistent storage of user data
   - API key masking

## 🚀 Scaling and Performance

### Horizontal Scaling

1. **Load Balancer Configuration**
   ```nginx
   upstream app_servers {
       server app1:8501;
       server app2:8501;
       server app3:8501;
   }
   
   server {
       location / {
           proxy_pass http://app_servers;
       }
   }
   ```

2. **Container Orchestration**
   - Kubernetes deployment
   - Docker Swarm
   - Cloud container services

### Performance Optimization

1. **Resource Limits**
   ```yaml
   # Docker Compose
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 1G
       reservations:
         memory: 512M
   ```

2. **Caching**
   - Redis for session storage
   - CDN for static assets
   - Application-level caching

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          python run_phase6_tests.py

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy auto-post-generator \\
            --source . \\
            --platform managed \\
            --region us-central1
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Secrets properly managed
- [ ] SSL certificates ready
- [ ] Monitoring configured
- [ ] Backup strategy in place

### Post-Deployment
- [ ] Health checks passing
- [ ] Logs flowing correctly
- [ ] Performance metrics normal
- [ ] Security scans completed
- [ ] Load testing performed
- [ ] Documentation updated

## 🆘 Troubleshooting

### Common Deployment Issues

1. **Port Binding Issues**
   ```bash
   # Check port availability
   netstat -tulpn | grep 8501
   ```

2. **Memory Issues**
   ```bash
   # Monitor memory usage
   docker stats
   ```

3. **Permission Issues**
   ```bash
   # Fix file permissions
   chmod -R 755 /app
   chown -R app:app /app
   ```

4. **Environment Variable Issues**
   ```bash
   # Verify environment variables
   env | grep LOG_
   ```

### Log Analysis

```bash
# View application logs
tail -f logs/app.log

# Search for errors
grep "ERROR" logs/app.log

# JSON log parsing
cat logs/app.log | jq '.level == "ERROR"'
```

For more troubleshooting guidance, see [troubleshooting.md](troubleshooting.md).