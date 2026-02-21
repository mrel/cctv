# Deployment Guide
## IPTV Facial Recognition Surveillance System

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [System Requirements](#2-system-requirements)
3. [Docker Compose Deployment](#3-docker-compose-deployment)
4. [Kubernetes Deployment](#4-kubernetes-deployment)
5. [Production Configuration](#5-production-configuration)
6. [SSL/TLS Setup](#6-ssltls-setup)
7. [Backup & Recovery](#7-backup--recovery)
8. [Monitoring & Logging](#8-monitoring--logging)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Docker | 24.0+ | Container runtime |
| Docker Compose | 2.20+ | Multi-container orchestration |
| NVIDIA Docker | 2.13+ | GPU support (optional) |
| kubectl | 1.28+ | Kubernetes CLI (optional) |
| Helm | 3.12+ | Kubernetes package manager (optional) |

### Install Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

### Install NVIDIA Docker (for GPU support)

```bash
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-docker2
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi
```

---

## 2. System Requirements

### Minimum Requirements (Development)

| Component | Specification |
|-----------|---------------|
| CPU | 4 cores |
| RAM | 16 GB |
| Storage | 100 GB SSD |
| Network | 1 Gbps |

### Recommended Requirements (Production)

| Component | Specification |
|-----------|---------------|
| CPU | 16+ cores |
| RAM | 64 GB |
| GPU | NVIDIA RTX 4090 / A100 |
| Storage | 1 TB NVMe SSD |
| Network | 10 Gbps |

### GPU Requirements (for AI workers)

| Model | VRAM | Concurrent Streams |
|-------|------|-------------------|
| RTX 3060 | 12 GB | 5-8 |
| RTX 4090 | 24 GB | 15-20 |
| A100 | 40/80 GB | 50+ |

---

## 3. Docker Compose Deployment

### 3.1 Clone and Configure

```bash
# Clone the repository
git clone https://github.com/your-org/surveillance-system.git
cd surveillance-system

# Create environment file
cp .env.example .env

# Edit configuration
nano .env
```

### 3.2 Environment Configuration

```bash
# .env file

# Database Configuration
POSTGRES_USER=surveillance
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=surveillance
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_minio_password
MINIO_ENDPOINT=minio:9000
MINIO_BUCKET=surveillance

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_min_32_chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Configuration
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=INFO

# Camera Configuration
DEFAULT_DETECTION_THRESHOLD=0.7
DEFAULT_RECOGNITION_THRESHOLD=0.6
FRAME_SAMPLE_RATE=5

# Alert Configuration
ALERT_WEBHOOK_URL=https://your-webhook.com/alerts
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USER=alerts@example.com
EMAIL_PASSWORD=your_email_password

# GPU Configuration
GPU_ENABLED=true
CUDA_VISIBLE_DEVICES=0
```

### 3.3 Deploy Services

```bash
# Start all services
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f detection-worker
```

### 3.4 Initialize Database

```bash
# Run database migrations
docker compose exec backend alembic upgrade head

# Seed initial data
docker compose exec backend python -m app.db.seed
```

### 3.5 Create Admin User

```bash
# Create admin user
docker compose exec backend python -c "
from app.core.security import get_password_hash
from app.models.user import User
from app.db.session import SessionLocal

db = SessionLocal()
admin = User(
    username='admin',
    email='admin@example.com',
    hashed_password=get_password_hash('admin123'),
    role='admin',
    is_active=True
)
db.add(admin)
db.commit()
print('Admin user created successfully')
"
```

### 3.6 Verify Deployment

```bash
# Check API health
curl http://localhost:8000/v1/health

# Check frontend
curl http://localhost:3000

# Check MinIO console
open http://localhost:9001

# Check Grafana (if enabled)
open http://localhost:3001
```

---

## 4. Kubernetes Deployment

### 4.1 Prerequisites

```bash
# Create Kubernetes cluster (using k3s as example)
curl -sfL https://get.k3s.io | sh -

# Configure kubectl
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Add Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
```

### 4.2 Deploy Dependencies

```bash
# Create namespace
kubectl create namespace surveillance

# Deploy PostgreSQL with pgvector
helm install postgres bitnami/postgresql \
  --namespace surveillance \
  --set image.repository=ankane/pgvector \
  --set image.tag=latest \
  --set auth.username=surveillance \
  --set auth.password=your_password \
  --set auth.database=surveillance \
  --set persistence.size=100Gi

# Deploy Redis
helm install redis bitnami/redis \
  --namespace surveillance \
  --set auth.enabled=true \
  --set auth.password=your_password \
  --set persistence.size=10Gi

# Deploy MinIO
helm install minio bitnami/minio \
  --namespace surveillance \
  --set auth.rootUser=minioadmin \
  --set auth.rootPassword=your_password \
  --set persistence.size=500Gi

# Deploy NGINX Ingress
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

### 4.3 Create ConfigMaps and Secrets

```bash
# Create configmap
kubectl create configmap surveillance-config \
  --namespace surveillance \
  --from-literal=APP_ENV=production \
  --from-literal=LOG_LEVEL=INFO \
  --from-literal=DEFAULT_DETECTION_THRESHOLD=0.7

# Create secrets
kubectl create secret generic surveillance-secrets \
  --namespace surveillance \
  --from-literal=POSTGRES_PASSWORD=your_password \
  --from-literal=REDIS_PASSWORD=your_password \
  --from-literal=JWT_SECRET_KEY=your_secret_key \
  --from-literal=MINIO_ROOT_PASSWORD=your_password
```

### 4.4 Deploy Application

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: surveillance-backend
  namespace: surveillance
spec:
  replicas: 3
  selector:
    matchLabels:
      app: surveillance-backend
  template:
    metadata:
      labels:
        app: surveillance-backend
    spec:
      containers:
      - name: backend
        image: surveillance/backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: surveillance-config
        - secretRef:
            name: surveillance-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: surveillance-backend
  namespace: surveillance
spec:
  selector:
    app: surveillance-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

```bash
# Apply deployments
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/worker-deployment.yaml
kubectl apply -f k8s/ingress.yaml

# Check status
kubectl get pods -n surveillance
kubectl get svc -n surveillance
kubectl get ingress -n surveillance
```

### 4.5 GPU Worker Deployment

```yaml
# k8s/gpu-worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: surveillance-detection-worker
  namespace: surveillance
spec:
  replicas: 2
  selector:
    matchLabels:
      app: detection-worker
  template:
    metadata:
      labels:
        app: detection-worker
    spec:
      nodeSelector:
        nvidia.com/gpu.present: "true"
      containers:
      - name: worker
        image: surveillance/detection-worker:latest
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            memory: "4Gi"
            cpu: "2000m"
        envFrom:
        - configMapRef:
            name: surveillance-config
        - secretRef:
            name: surveillance-secrets
```

---

## 5. Production Configuration

### 5.1 Database Optimization

```sql
-- Run on PostgreSQL for production optimization

-- Increase connection limit
ALTER SYSTEM SET max_connections = '200';

-- Shared buffers (25% of RAM)
ALTER SYSTEM SET shared_buffers = '16GB';

-- Effective cache size (50% of RAM)
ALTER SYSTEM SET effective_cache_size = '32GB';

-- Work memory
ALTER SYSTEM SET work_mem = '64MB';

-- Maintenance work memory
ALTER SYSTEM SET maintenance_work_mem = '2GB';

-- WAL settings
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET max_wal_size = '4GB';

-- Checkpoint settings
ALTER SYSTEM SET checkpoint_completion_target = '0.9';

-- Apply changes
SELECT pg_reload_conf();
```

### 5.2 Redis Optimization

```bash
# redis.conf additions for production
maxmemory 8gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
```

### 5.3 NGINX Configuration

```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
    
    # Upstream backends
    upstream backend {
        least_conn;
        server backend1:8000 max_fails=3 fail_timeout=30s;
        server backend2:8000 max_fails=3 fail_timeout=30s;
        server backend3:8000 max_fails=3 fail_timeout=30s;
    }
    
    # API server
    server {
        listen 80;
        server_name api.surveillance.local;
        
        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
    }
    
    # Frontend server
    server {
        listen 80;
        server_name surveillance.local;
        
        location / {
            proxy_pass http://frontend:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## 6. SSL/TLS Setup

### 6.1 Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d surveillance.local -d api.surveillance.local

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 6.2 Using Custom Certificate

```bash
# Create certificate directory
sudo mkdir -p /etc/nginx/ssl
sudo chmod 700 /etc/nginx/ssl

# Copy certificates
sudo cp your_certificate.crt /etc/nginx/ssl/
sudo cp your_private.key /etc/nginx/ssl/

# Set permissions
sudo chmod 600 /etc/nginx/ssl/*
```

```nginx
# Update NGINX configuration
server {
    listen 443 ssl http2;
    server_name api.surveillance.local;
    
    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    location / {
        proxy_pass http://backend;
        # ... proxy settings
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.surveillance.local;
    return 301 https://$server_name$request_uri;
}
```

---

## 7. Backup & Recovery

### 7.1 Database Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="surveillance_${DATE}.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker compose exec -T postgres pg_dump \
  -U surveillance \
  -d surveillance \
  | gzip > "$BACKUP_DIR/$BACKUP_FILE"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" s3://your-backup-bucket/

# Keep only last 7 days
find $BACKUP_DIR -name "surveillance_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/surveillance/backup.sh >> /var/log/surveillance-backup.log 2>&1
```

### 7.2 MinIO Backup

```bash
#!/bin/bash
# minio-backup.sh

BACKUP_DIR="/backups/minio"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup MinIO bucket
mc mirror surveillance/minio/surveillance "$BACKUP_DIR/surveillance_$DATE"

# Compress
tar -czf "$BACKUP_DIR/surveillance_$DATE.tar.gz" -C "$BACKUP_DIR" "surveillance_$DATE"
rm -rf "$BACKUP_DIR/surveillance_$DATE"

# Upload to S3
aws s3 cp "$BACKUP_DIR/surveillance_$DATE.tar.gz" s3://your-backup-bucket/

# Cleanup
find $BACKUP_DIR -name "surveillance_*.tar.gz" -mtime +7 -delete
```

### 7.3 Database Recovery

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <backup_file>"
    exit 1
fi

# Stop application
docker compose stop backend

# Restore database
gunzip < "$BACKUP_FILE" | docker compose exec -T postgres psql \
  -U surveillance \
  -d surveillance

# Start application
docker compose start backend

echo "Restore completed from: $BACKUP_FILE"
```

---

## 8. Monitoring & Logging

### 8.1 Prometheus & Grafana Setup

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123

  node-exporter:
    image: prom/node-exporter:latest
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'

volumes:
  prometheus_data:
  grafana_data:
```

### 8.2 Application Metrics

```python
# Add to backend for Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
detection_counter = Counter('face_detections_total', 'Total face detections')
recognition_counter = Counter('face_recognitions_total', 'Total face recognitions')
recognition_duration = Histogram('recognition_duration_seconds', 'Recognition duration')
active_cameras = Gauge('active_cameras', 'Number of active cameras')
```

### 8.3 Log Aggregation

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logging/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

volumes:
  elasticsearch_data:
```

---

## 9. Troubleshooting

### 9.1 Common Issues

#### Database Connection Failed

```bash
# Check PostgreSQL logs
docker compose logs postgres

# Verify connection
docker compose exec postgres psql -U surveillance -d surveillance -c "SELECT 1;"

# Check network
docker network inspect surveillance_default
```

#### GPU Not Detected

```bash
# Verify NVIDIA driver
nvidia-smi

# Check nvidia-docker
 docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi

# Rebuild GPU worker
docker compose build --no-cache detection-worker
docker compose up -d detection-worker
```

#### High Memory Usage

```bash
# Check memory usage
docker stats

# Restart services
docker compose restart backend

# Increase memory limits in docker-compose.yml
```

#### Camera Stream Issues

```bash
# Test camera stream
ffprobe rtsp://camera-ip/stream

# Check ingestion worker logs
docker compose logs -f ingestion-worker

# Verify Redis streams
docker compose exec redis redis-cli LRANGE camera:frames 0 10
```

### 9.2 Health Checks

```bash
# Full system health check
#!/bin/bash

echo "=== System Health Check ==="

# Check Docker
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check API
curl -s http://localhost:8000/v1/health | jq

# Check database
docker compose exec postgres pg_isready -U surveillance

# Check Redis
docker compose exec redis redis-cli ping

# Check MinIO
curl -s http://localhost:9000/minio/health/live

# Check GPU (if enabled)
nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu --format=csv

echo "=== Health Check Complete ==="
```

### 9.3 Performance Tuning

```bash
# Database vacuum and analyze
docker compose exec postgres vacuumdb -U surveillance -d surveillance -v -z

# Redis memory optimization
docker compose exec redis redis-cli MEMORY PURGE

# Clear old sightings (if retention policy allows)
docker compose exec backend python -c "
from app.db.session import SessionLocal
from app.models.sighting import Sighting
from datetime import datetime, timedelta

db = SessionLocal()
cutoff = datetime.utcnow() - timedelta(days=90)
deleted = db.query(Sighting).filter(Sighting.detected_at < cutoff).delete()
db.commit()
print(f'Deleted {deleted} old sightings')
"
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start all services |
| `docker compose down` | Stop all services |
| `docker compose logs -f` | View all logs |
| `docker compose ps` | List running services |
| `docker compose exec backend bash` | Access backend shell |
| `docker compose restart [service]` | Restart a service |
| `docker compose build --no-cache [service]` | Rebuild a service |
| `kubectl get pods -n surveillance` | List Kubernetes pods |
| `kubectl logs -f deployment/backend -n surveillance` | View Kubernetes logs |

---

## Support

For additional support:
- Documentation: https://docs.surveillance.local
- Issues: https://github.com/your-org/surveillance-system/issues
- Email: support@surveillance.local
