# IPTV Facial Recognition Surveillance System

A comprehensive microservices-based facial recognition platform for IPTV surveillance cameras with real-time detection, recognition, and alerting capabilities.

## Features

- **Camera Management**: Add, configure, and monitor RTSP/HTTP camera streams
- **Face Detection & Recognition**: Real-time face detection using YOLOv8 and recognition using ArcFace
- **Subject Tracking**: Vector-based identity management with pgvector
- **Real-time Alerts**: Rule-based notifications for security events
- **Analytics Dashboard**: Heatmaps, movement patterns, and demographic insights
- **GDPR Compliance**: Audit trails, data retention, and consent management
- **Web Control Interface**: React-based SPA for security operators

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer (Nginx)                 │
└─────────────┬───────────────────────────────┬───────────────┘
              │                               │
    ┌─────────▼──────────┐        ┌───────────▼────────────┐
    │   Web Interface    │        │   API Gateway          │
    │   (React SPA)      │◄──────►│   (FastAPI)            │
    └────────────────────┘        └───────────┬────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
        ┌───────────▼──────────┐  ┌───────────▼──────────┐  ┌──────────▼─────────┐
        │  Stream Ingestion    │  │  Recognition Core    │  │   Management API   │
        │  Service (Python)    │  │  (Python/GPU)        │  │   (FastAPI)        │
        └───────────┬──────────┘  └───────────┬──────────┘  └──────────┬─────────┘
                    │                         │                        │
        ┌───────────▼──────────┐  ┌───────────▼──────────┐  ┌──────────▼─────────┐
        │   Message Queue      │  │   Vector Database    │  │   PostgreSQL       │
        │   (Redis Streams)    │  │   (pgvector)         │  │   (Relational)     │
        └──────────────────────┘  └──────────────────────┘  └────────────────────┘
                    │                                                 │
                    └─────────────────────┬──────────────────────────┘
                                          │
                              ┌───────────▼──────────┐
                              │   Object Storage     │
                              │   (MinIO Cluster)    │
                              └──────────────────────┘
```

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Docker runtime (optional, for GPU support)

### One-Command Deployment

```bash
# Clone the repository
git clone <repository-url>
cd surveillance-system

# Start all services
docker-compose up -d

# Access the web interface
open http://localhost:3000
```

### Default Credentials

- **Username**: admin
- **Password**: admin

## Services

| Service | Port | Description |
|---------|------|-------------|
| Web Interface | 3000 | React SPA for operators |
| Backend API | 8000 | FastAPI REST API |
| PostgreSQL | 5432 | Database with pgvector |
| Redis | 6379 | Cache & message queue |
| MinIO | 9000/9001 | Object storage |
| Nginx | 80/443 | Load balancer |

## API Documentation

Once the backend is running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Schema

The system uses PostgreSQL with pgvector extension for vector similarity search:

- **cameras**: Camera configuration and metadata
- **subjects**: Person identities with face embeddings
- **images**: Image asset registry
- **sightings**: Time-series detection events
- **alert_rules**: Alert configuration
- **alert_logs**: Triggered alerts
- **audit_logs**: GDPR compliance audit trail

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Configuration

Environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://... | PostgreSQL connection |
| `REDIS_URL` | redis://... | Redis connection |
| `MINIO_ENDPOINT` | localhost:9000 | MinIO endpoint |
| `JWT_SECRET` | - | JWT signing secret |
| `DETECTION_THRESHOLD` | 0.7 | Face detection threshold |
| `RECOGNITION_THRESHOLD` | 0.6 | Face recognition threshold |

## Production Deployment

### Kubernetes

Kubernetes manifests are provided in `infrastructure/k8s/`:

```bash
kubectl apply -f infrastructure/k8s/
```

### Security Considerations

- Use TLS 1.3 for all communications
- Enable RBAC with appropriate roles
- Configure network policies for camera isolation
- Set up proper secrets management
- Enable audit logging

## License

MIT License - See LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub issue tracker.
