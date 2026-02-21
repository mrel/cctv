# IPTV Facial Recognition Surveillance System
## Complete Technical Documentation & Development Guide

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Database Design](#4-database-design)
5. [Backend API Specification](#5-backend-api-specification)
6. [Frontend Architecture](#6-frontend-architecture)
7. [AI/ML Pipeline](#7-aiml-pipeline)
8. [Deployment Guide](#8-deployment-guide)
9. [Development Prompts](#9-development-prompts)
10. [Expansion Ideas](#10-expansion-ideas)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Executive Summary

### 1.1 Project Overview

The IPTV Facial Recognition Surveillance System is a production-ready, microservices-based platform designed for enterprise-grade security operations. It processes real-time video streams from IP cameras, performs facial detection and recognition, and provides a comprehensive web interface for security operators.

### 1.2 Core Capabilities

| Capability | Specification |
|------------|---------------|
| Concurrent Streams | 50+ cameras (1080p @ 15fps) |
| Detection Latency | <500ms from capture to notification |
| Recognition Accuracy | 99.2% with ArcFace (LFW benchmark) |
| System Uptime | 99.9% with automatic failover |
| Database | PostgreSQL with pgvector (512-dim embeddings) |

### 1.3 Compliance & Security

- **GDPR Compliant**: Data retention, right to erasure, audit trails
- **SOC 2 Ready**: Immutable audit logs, access controls
- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **RBAC**: Role-based access control (Admin, Operator, Viewer, Auditor)

---

## 2. System Architecture

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Web App    │  │ Mobile App   │  │  API Clients │  │  Dashboards  │   │
│  │   (React)    │  │  (React      │  │   (Python)   │  │  (Grafana)   │   │
│  │              │  │   Native)    │  │              │  │              │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
└─────────┼─────────────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │                 │
          └─────────────────┴────────┬────────┴─────────────────┘
                                     │
┌────────────────────────────────────┴────────────────────────────────────────┐
│                           API GATEWAY LAYER                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         Nginx Load Balancer                             │ │
│  │  - SSL Termination  - Rate Limiting  - Request Routing  - Caching      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
┌─────────▼──────────┐  ┌─────────────▼─────────────┐  ┌────────▼─────────┐
│   WEB INTERFACE    │  │      BACKEND API          │  │  WEBSOCKET API   │
│   (React/Vite)     │  │      (FastAPI)            │  │  (Socket.io)     │
│                    │  │                           │  │                  │
│  - Live View       │  │  - Camera Management      │  │  - Real-time     │
│  - Subject Gallery │  │  - Subject CRUD           │  │    Alerts        │
│  - Analytics       │  │  - Alert Engine           │  │  - Detection     │
│  - Settings        │  │  - Authentication         │  │    Stream        │
└────────────────────┘  └───────────────────────────┘  └──────────────────┘
                                     │
┌────────────────────────────────────┴────────────────────────────────────────┐
│                         MICROSERVICES LAYER                                  │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │ Stream Ingestion │  │ Detection Worker │  │ Recognition Svc  │         │
│  │   (Python)       │  │   (Python/GPU)   │  │   (Python/GPU)   │         │
│  │                  │  │                  │  │                  │         │
│  │ - FFmpeg wrapper │  │ - YOLOv8-face    │  │ - ArcFace        │         │
│  │ - Frame sampling │  │ - Batch process  │  │ - 512-dim embed  │         │
│  │ - Redis Streams  │  │ - GPU optimized  │  │ - Vector search  │         │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘         │
│           │                     │                     │                    │
│  ┌────────┴─────────────────────┴─────────────────────┴─────────┐         │
│  │                    MESSAGE QUEUE (Redis)                      │         │
│  │  camera:{id}:frames → faces:detected → alerts:check          │         │
│  └───────────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴────────────────────────────────────────┐
│                           DATA LAYER                                         │
│                                                                              │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐   │
│  │   PostgreSQL       │  │      Redis         │  │      MinIO         │   │
│  │   (Primary DB)     │  │   (Cache/Queue)    │  │   (Object Store)   │   │
│  │                    │  │                    │  │                    │   │
│  │ - cameras          │  │ - Session cache    │  │ - Live footage     │   │
│  │ - subjects         │  │ - Rate limiting    │  │ - Subject images   │   │
│  │ - sightings        │  │ - Pub/Sub          │  │ - Archive          │   │
│  │ - alerts           │  │ - Streams          │  │ - Backups          │   │
│  │ - audit_logs       │  │                    │  │                    │   │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Service Communication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Camera    │────►│  Ingestion  │────►│   Redis     │────►│  Detection  │
│   Stream    │     │   Service   │     │   Stream    │     │   Worker    │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                    │
                                                                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Alert     │◄────│   Redis     │◄────│ Recognition │◄────│   Faces     │
│   Engine    │     │   Pub/Sub   │     │   Service   │     │  Detected   │
└──────┬──────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  WebSocket  │────►│   Web UI    │     │  Database   │
│   Broadcast │     │   (React)   │     │  (PostgreSQL│
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 3. Technology Stack

### 3.1 Backend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Web Framework | FastAPI | 0.109+ | High-performance async API |
| Database | PostgreSQL | 15+ | Primary data store |
| Vector Extension | pgvector | 0.5+ | Embedding similarity search |
| Cache/Queue | Redis | 7+ | Caching, pub/sub, streams |
| Object Storage | MinIO | Latest | S3-compatible storage |
| ORM | SQLAlchemy | 2.0+ | Database abstraction |
| Migrations | Alembic | 1.13+ | Schema versioning |
| Auth | python-jose | 3.3+ | JWT token handling |
| Passwords | passlib | 1.7+ | Bcrypt hashing |

### 3.2 Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | React | 18+ | UI library |
| Language | TypeScript | 5.0+ | Type safety |
| Build Tool | Vite | 5.0+ | Fast development |
| Styling | Tailwind CSS | 3.4+ | Utility-first CSS |
| Components | shadcn/ui | Latest | Accessible components |
| State | React Context | - | Global state |
| Charts | Recharts | 2.0+ | Data visualization |
| Maps | Leaflet | 1.9+ | Interactive maps |
| Icons | Lucide | Latest | Icon library |

### 3.3 AI/ML Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Detection | YOLOv8-face | Face detection |
| Recognition | ArcFace (InsightFace) | Face embedding |
| Runtime | ONNX Runtime | Model inference |
| GPU | NVIDIA TensorRT | Optimized inference |
| Processing | OpenCV | Image preprocessing |

### 3.4 Infrastructure Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Load Balancer | Nginx | Reverse proxy, SSL |
| Containerization | Docker | Service isolation |
| Orchestration | Docker Compose | Local deployment |
| Monitoring | Prometheus/Grafana | Metrics & dashboards |
| Logging | Loki/Fluentd | Centralized logging |

---

## 4. Database Design

### 4.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ENTITY RELATIONSHIPS                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    users     │       │   cameras    │       │   subjects   │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ user_id (PK) │       │ camera_id(PK)│       │ subject_id(PK│
│ username     │       │ name         │       │ label        │
│ email        │       │ rtsp_url     │       │ subject_type │
│ password_hash│       │ location     │       │ status       │
│ role         │       │ stream_config│       │ primary_embed│
│ is_active    │       │ is_active    │       │ metadata     │
│ created_at   │       │ health_status│       │ consent_status│
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       │                      │                      │
       │                      │                      │
       │         ┌────────────┴──────────────────────┤
       │         │                                   │
       │    ┌────┴────┐                         ┌────┴────┐
       │    │ images  │                         │sightings│
       │    ├─────────┤                         ├─────────┤
       │    │image_id │                         │sighting_│
       │    │subject_id│◄───────────────────────│subject_│
       │    │camera_id│◄───────────────────────│camera_id│
       │    │storage_path                       │image_id │
       │    │quality  │                         │detected_│
       │    │captured_│                         │confidence│
       │    └─────────┘                         └────┬────┘
       │                                             │
       │         ┌───────────────────────────────────┘
       │         │
       │    ┌────┴─────────┐
       │    │  alert_logs  │
       │    ├──────────────┤
       │    │ alert_id     │
       └────┤ acknowledged_│
            │ rule_id      │
            │ subject_id   │
            │ camera_id    │
            └──────────────┘
```

### 4.2 Table Specifications

#### 4.2.1 cameras

```sql
CREATE TABLE cameras (
    camera_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(500),
    rtsp_url TEXT NOT NULL,
    stream_config JSONB DEFAULT '{
        "protocol": "rtsp",
        "resolution": "1920x1080",
        "fps": 15,
        "codec": "h264",
        "auth_type": "basic"
    }',
    detection_zones JSONB,  -- Polygon coordinates for ROI
    is_active BOOLEAN DEFAULT true,
    health_status VARCHAR(50) DEFAULT 'unknown',
    last_frame_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Indexes:**
- `idx_cameras_active` on `is_active`
- `idx_cameras_health` on `health_status`

#### 4.2.2 subjects

```sql
CREATE TABLE subjects (
    subject_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    label VARCHAR(255),
    subject_type VARCHAR(50) DEFAULT 'unknown',
    status VARCHAR(50) DEFAULT 'active',
    primary_embedding VECTOR(512),
    enrollment_date TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP,
    metadata JSONB,
    consent_status VARCHAR(50) DEFAULT 'pending',
    retention_until TIMESTAMP
);
```

**Indexes:**
- `idx_subjects_embedding` using ivfflat (vector_cosine_ops)
- `idx_subjects_type` on `subject_type`
- `idx_subjects_status` on `status`

#### 4.2.3 sightings (Time-Series, Partitioned)

```sql
CREATE TABLE sightings (
    sighting_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subject_id UUID REFERENCES subjects(subject_id),
    camera_id UUID REFERENCES cameras(camera_id),
    image_id UUID REFERENCES images(image_id),
    detection_confidence FLOAT NOT NULL,
    recognition_confidence FLOAT,
    match_distance FLOAT,
    scene_analysis JSONB,
    detected_at TIMESTAMP NOT NULL,
    processed_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (detected_at);

-- Monthly partitions
CREATE TABLE sightings_y2024m01 PARTITION OF sightings
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

**Indexes:**
- `idx_sightings_time` on `detected_at DESC`
- `idx_sightings_subject_time` on `(subject_id, detected_at DESC)`
- `idx_sightings_camera` on `(camera_id, detected_at DESC)`

---

## 5. Backend API Specification

### 5.1 Authentication Endpoints

#### POST /api/v1/auth/login

**Request:**
```json
{
  "username": "admin",
  "password": "secure_password",
  "mfa_code": "123456"  // Optional
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "admin",
    "email": "admin@company.com",
    "role": "admin",
    "mfa_enabled": false
  }
}
```

### 5.2 Camera Endpoints

#### GET /api/v1/cameras

**Query Parameters:**
- `skip` (int): Pagination offset
- `limit` (int): Items per page (max 100)
- `is_active` (bool): Filter by status
- `health_status` (string): Filter by health

**Response:**
```json
{
  "items": [
    {
      "camera_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Main Entrance",
      "location": "Building A - Floor 1",
      "rtsp_url": "rtsp://admin:pass@192.168.1.10:554/stream1",
      "stream_config": {
        "protocol": "rtsp",
        "resolution": "1920x1080",
        "fps": 15,
        "codec": "h264"
      },
      "is_active": true,
      "health_status": "healthy",
      "last_frame_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 20
}
```

#### POST /api/v1/cameras

**Request:**
```json
{
  "name": "Parking Garage",
  "location": "Building A - Basement",
  "rtsp_url": "rtsp://admin:pass@192.168.1.12:554/stream1",
  "stream_config": {
    "protocol": "rtsp",
    "resolution": "1280x720",
    "fps": 10,
    "codec": "h264",
    "auth_type": "digest"
  },
  "detection_zones": [
    {"x": 0.2, "y": 0.3, "w": 0.6, "h": 0.5}
  ]
}
```

### 5.3 Subject Endpoints

#### POST /api/v1/subjects/search-by-image

**Request:** (multipart/form-data)
- `image`: File upload
- `threshold`: 0.7 (min similarity)
- `max_results`: 10

**Response:**
```json
{
  "results": [
    {
      "subject_id": "660e8400-e29b-41d4-a716-446655440000",
      "label": "John Smith",
      "subject_type": "employee",
      "similarity": 0.92,
      "last_seen": "2024-01-15T09:45:00Z"
    }
  ]
}
```

#### POST /api/v1/vector-search

**Request:**
```json
{
  "embedding": [0.023, -0.156, 0.089, ...],  // 512-dim array
  "threshold": 0.7,
  "camera_filter": ["camera-uuid-1", "camera-uuid-2"]
}
```

### 5.4 Alert Endpoints

#### GET /api/v1/alerts/logs

**Query Parameters:**
- `status`: open, acknowledged, resolved, false_positive
- `priority_min`: 1-10
- `time_from`: ISO 8601 timestamp
- `time_to`: ISO 8601 timestamp

**Response:**
```json
{
  "alerts": [
    {
      "alert_id": "770e8400-e29b-41d4-a716-446655440000",
      "rule_name": "Banned Person Detected",
      "rule_type": "blacklist",
      "subject_label": "Robert Wilson",
      "camera_name": "Main Entrance",
      "trigger_data": {
        "detection_confidence": 0.92,
        "location": "Main Entrance"
      },
      "status": "open",
      "priority": 10,
      "created_at": "2024-01-15T10:30:00Z",
      "age_minutes": 5.2
    }
  ]
}
```

### 5.5 WebSocket Endpoints

#### /api/v1/ws/alerts

Real-time alert notifications.

**Message Format:**
```json
{
  "type": "alert",
  "data": {
    "alert_id": "...",
    "rule_name": "Banned Person Detected",
    "priority": 10,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### /api/v1/ws/detections?camera_id={id}

Real-time detection stream for specific camera.

---

## 6. Frontend Architecture

### 6.1 Component Hierarchy

```
App
├── AuthProvider
│   └── ThemeProvider
│       └── BrowserRouter
│           ├── LoginPage (public)
│           └── ProtectedRoute
│               └── Layout
│                   ├── Sidebar
│                   │   ├── Logo
│                   │   └── Navigation
│                   ├── Header
│                   │   ├── Search
│                   │   ├── Notifications
│                   │   └── UserMenu
│                   └── Main Content
│                       ├── DashboardPage
│                       │   ├── StatsCards
│                       │   ├── RecentAlerts
│                       │   └── CameraHealth
│                       ├── LiveViewPage
│                       │   ├── LayoutSelector
│                       │   └── CameraGrid
│                       ├── SubjectsPage
│                       │   ├── SearchFilters
│                       │   └── SubjectGrid
│                       ├── CamerasPage
│                       │   ├── CameraList
│                       │   └── AddCameraDialog
│                       ├── AlertsPage
│                       │   ├── AlertTabs
│                       │   └── AlertList
│                       ├── AnalyticsPage
│                       │   └── Charts
│                       └── SettingsPage
│                           └── SettingsTabs
```

### 6.2 State Management

```typescript
// Global State Structure
interface AppState {
  auth: {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
  };
  cameras: {
    items: Camera[];
    activeStreams: Record<string, MediaStream>;
    healthStatus: Record<string, CameraHealth>;
  };
  subjects: {
    gallery: Subject[];
    currentSubject: Subject | null;
    searchResults: Subject[];
  };
  detections: {
    liveFeed: Detection[];  // Ring buffer (last 100)
    alerts: Alert[];
    statistics: Statistics;
  };
  ui: {
    sidebarCollapsed: boolean;
    theme: 'light' | 'dark' | 'system';
    liveViewLayout: '1x1' | '2x2' | '3x3';
  };
}
```

### 6.3 Custom Hooks

| Hook | Purpose | Usage |
|------|---------|-------|
| `useAuth()` | Authentication state & methods | Login, logout, permissions |
| `useCameras()` | Camera CRUD operations | Camera management |
| `useSubjects()` | Subject CRUD & search | Subject gallery |
| `useAlerts()` | Alert management | Alert feed |
| `useAnalytics()` | Statistics & charts | Dashboard |
| `useWebSocket()` | Real-time connection | Live updates |

---

## 7. AI/ML Pipeline

### 7.1 Detection Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     DETECTION PIPELINE                           │
└─────────────────────────────────────────────────────────────────┘

Camera Stream (RTSP)
        │
        ▼
┌───────────────┐
│ FFmpeg Decode │  ──►  Extract frames at 2fps
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Preprocess    │  ──►  Resize, normalize, format
│ (OpenCV)      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ YOLOv8-face   │  ──►  Detect faces, output bounding boxes
│ Inference     │      Confidence threshold: 0.7
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Face Crop     │  ──►  Extract face regions
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Redis Stream  │  ──►  Queue for recognition
│ (faces:detected)│
└───────────────┘
```

### 7.2 Recognition Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                   RECOGNITION PIPELINE                           │
└─────────────────────────────────────────────────────────────────┘

Redis Stream
(faces:detected)
        │
        ▼
┌───────────────┐
│ Batch Collect │  ──►  Accumulate 4-8 frames for GPU efficiency
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Preprocess    │  ──►  Align faces using landmarks
│ (ArcFace)     │      Normalize to 112x112
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ ArcFace       │  ──►  Generate 512-dim embedding vector
│ Inference     │      ResNet-50 backbone
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Vector Search │  ──►  pgvector cosine similarity
│ (pgvector)    │      SELECT subject_id, embedding <-> $1
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Threshold     │  ──►  >0.6 cosine similarity = known
│ Classification│      <0.6 = new unknown subject
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Database Write│  ──►  Insert sighting record
│ Alert Check   │  ──►  Evaluate alert rules
└───────────────┘
```

### 7.3 Model Specifications

| Model | Input | Output | Size | Latency |
|-------|-------|--------|------|---------|
| YOLOv8n-face | 640x640 | BBoxes + Conf | 6MB | 5ms (GPU) |
| ArcFace-R50 | 112x112 | 512-dim vector | 130MB | 15ms (GPU) |

---

## 8. Deployment Guide

### 8.1 System Requirements

#### Minimum Requirements (Development)
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- GPU: Optional

#### Recommended Requirements (Production)
- CPU: 16+ cores
- RAM: 64GB+
- Storage: 1TB+ NVMe SSD
- GPU: NVIDIA T4 or better
- Network: 10Gbps

### 8.2 Docker Compose Deployment

```bash
# 1. Clone repository
git clone <repository-url>
cd surveillance-system

# 2. Create environment file
cat > .env << EOF
DEBUG=false
DATABASE_URL=postgresql://surveillance:surveillance@postgres:5432/surveillance_db
REDIS_URL=redis://redis:6379/0
MINIO_ENDPOINT=minio:9000
JWT_SECRET=$(openssl rand -hex 32)
EOF

# 3. Start services
docker-compose up -d

# 4. Verify deployment
docker-compose ps
docker-compose logs -f backend

# 5. Access services
echo "Web UI: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo "MinIO Console: http://localhost:9001"
```

### 8.3 Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f infrastructure/k8s/namespace.yaml
kubectl apply -f infrastructure/k8s/configmaps/
kubectl apply -f infrastructure/k8s/secrets/
kubectl apply -f infrastructure/k8s/pvc/
kubectl apply -f infrastructure/k8s/deployments/
kubectl apply -f infrastructure/k8s/services/
kubectl apply -f infrastructure/k8s/ingress/

# Verify
kubectl get pods -n surveillance-system
kubectl get svc -n surveillance-system
```

### 8.4 SSL/TLS Configuration

```bash
# Generate self-signed certificates (development)
mkdir -p infrastructure/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout infrastructure/nginx/ssl/key.pem \
  -out infrastructure/nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# For production, use Let's Encrypt
certbot --nginx -d your-domain.com
```

---

## 9. Development Prompts

### 9.1 Phase 1: Database Setup

```
Create a PostgreSQL database schema for a facial recognition surveillance system with the following requirements:

1. EXTENSIONS:
   - Enable uuid-ossp for UUID generation
   - Enable pgvector for 512-dimensional embedding storage

2. TABLES:
   - cameras: Store RTSP camera configuration with JSONB stream_config and detection_zones
   - subjects: Person identities with VECTOR(512) for face embeddings, GDPR consent fields
   - images: Image metadata with MinIO storage paths, quality scores, bounding boxes
   - sightings: Time-series partitioned table for detection events
   - alert_rules: Rule configuration with JSONB conditions and actions
   - alert_logs: Triggered alerts with status tracking
   - audit_logs: Immutable GDPR compliance logs
   - users: RBAC user management with password hashing

3. INDEXES:
   - Vector similarity search index on subjects.primary_embedding
   - Time-series indexes on sightings for efficient queries
   - Partial indexes for common query patterns

4. FUNCTIONS:
   - search_subjects_by_face(embedding, threshold, max_results)
   - get_subject_timeline(subject_id, from, to, limit)
   - get_camera_stats(camera_id, from, to)

5. VIEWS:
   - active_alerts: Join alert_logs with rules, subjects, cameras
   - camera_health: Health status with detection counts
   - subject_gdpr_export: Complete subject data for GDPR export

Include proper constraints, foreign keys, and comments on all objects.
```

### 9.2 Phase 2: Backend API

```
Build a FastAPI backend for a surveillance system with these specifications:

1. PROJECT STRUCTURE:
   app/
   ├── api/v1/endpoints/    # Route handlers
   ├── core/                # Config, database, Redis, MinIO clients
   ├── middleware/          # Audit logging, rate limiting
   ├── models/              # SQLAlchemy models
   └── schemas/             # Pydantic request/response models

2. AUTHENTICATION:
   - JWT-based with access/refresh tokens
   - bcrypt password hashing
   - RBAC middleware with permission checks

3. ENDPOINTS (all with proper validation):
   
   Cameras:
   - GET    /api/v1/cameras              (list with filters)
   - POST   /api/v1/cameras              (create)
   - GET    /api/v1/cameras/{id}         (get by ID)
   - PUT    /api/v1/cameras/{id}         (update)
   - DELETE /api/v1/cameras/{id}         (delete)
   - GET    /api/v1/cameras/{id}/health  (health status)
   - POST   /api/v1/cameras/{id}/test    (connection test)
   
   Subjects:
   - GET    /api/v1/subjects             (list with search)
   - POST   /api/v1/subjects             (create)
   - GET    /api/v1/subjects/{id}        (get by ID)
   - PUT    /api/v1/subjects/{id}        (update)
   - DELETE /api/v1/subjects/{id}        (delete)
   - GET    /api/v1/subjects/{id}/timeline (movement history)
   - POST   /api/v1/subjects/search-by-image (face search)
   - POST   /api/v1/subjects/vector-search (embedding search)
   
   Alerts:
   - GET    /api/v1/alerts/rules         (list rules)
   - POST   /api/v1/alerts/rules         (create rule)
   - GET    /api/v1/alerts/logs          (list alerts)
   - POST   /api/v1/alerts/logs/{id}/acknowledge
   - POST   /api/v1/alerts/logs/{id}/resolve
   
   Analytics:
   - GET    /api/v1/analytics/statistics (system stats)
   - POST   /api/v1/analytics/heatmap    (activity heatmap)
   - GET    /api/v1/analytics/cameras/{id}/stats

4. WEBSOCKET:
   - /api/v1/ws/alerts (real-time alert broadcast)
   - /api/v1/ws/detections (detection stream)

5. FEATURES:
   - Redis caching with TTL
   - Rate limiting (100 req/min)
   - Request/response logging
   - OpenAPI/Swagger documentation
   - Proper error handling with HTTP status codes
```

### 9.3 Phase 3: Frontend

```
Create a React TypeScript frontend for a surveillance control center:

1. TECH STACK:
   - React 18 with TypeScript
   - Vite for build tooling
   - Tailwind CSS for styling
   - shadcn/ui components
   - React Router for navigation
   - Axios for API calls
   - Socket.io-client for WebSocket

2. PROJECT STRUCTURE:
   src/
   ├── components/          # Reusable components
   ├── contexts/            # AuthContext, ThemeContext
   ├── hooks/               # Custom hooks (useAuth, useCameras, etc.)
   ├── lib/                 # API client, WebSocket manager
   ├── pages/               # Page components
   ├── types/               # TypeScript definitions
   └── App.tsx

3. PAGES:
   
   LoginPage:
   - Username/password form
   - JWT token storage
   - Redirect on auth
   
   DashboardPage:
   - Stats cards (cameras, subjects, alerts, detections)
   - Recent alerts list
   - Camera health status
   
   LiveViewPage:
   - Layout selector (1x1, 2x2, 3x3)
   - Camera selection dropdown per slot
   - Detection overlay on video
   - Alert flashing borders
   
   SubjectsPage:
   - Search and filters
   - Grid of subject cards
   - Type-based color coding
   - Click to detail view
   
   CamerasPage:
   - List/grid view
   - Add camera dialog
   - Health indicators
   - Test connection button
   
   AlertsPage:
   - Tabs: Active, All, Rules
   - Alert cards with priority colors
   - Acknowledge/Resolve buttons
   - Real-time updates
   
   AnalyticsPage:
   - Line chart: Detections over time
   - Pie chart: Subject types
   - Bar chart: Camera activity
   - Statistics cards
   
   SettingsPage:
   - Theme toggle (light/dark/system)
   - Detection threshold sliders
   - Notification preferences
   - GDPR retention settings

4. FEATURES:
   - Dark mode support
   - Responsive design
   - Toast notifications
   - Loading states
   - Error boundaries
   - Permission-based UI
```

### 9.4 Phase 4: AI Workers

```
Implement Python workers for the AI pipeline:

1. STREAM INGESTION SERVICE:
   - FFmpeg wrapper for RTSP stream decoding
   - Frame sampling (2fps for processing)
   - Automatic reconnection with exponential backoff
   - Publish frames to Redis Streams
   - Health monitoring per camera

2. DETECTION WORKER:
   - Consume from Redis Stream
   - YOLOv8-face model inference
   - Batch processing (4-8 frames)
   - GPU optimization with TensorRT
   - Output: bounding boxes, confidence scores
   - Publish detected faces to next queue

3. RECOGNITION WORKER:
   - Consume detected faces
   - ArcFace embedding generation (512-dim)
   - Vector similarity search with pgvector
   - Threshold-based classification
   - Database write for sightings
   - Alert rule evaluation
   - WebSocket broadcast for real-time updates

4. ALERT ENGINE:
   - Subscribe to recognition results
   - Rule evaluation engine
   - Complex event processing
   - Webhook dispatch
   - Email/SMS notifications
   - Alert deduplication

Include Dockerfiles for each service with GPU support.
```

### 9.5 Phase 5: Infrastructure

```
Create deployment infrastructure:

1. DOCKER COMPOSE:
   - PostgreSQL with pgvector
   - Redis
   - MinIO
   - Backend API
   - Frontend (Nginx)
   - AI Workers
   - Nginx load balancer
   - Health checks and dependencies

2. NGINX CONFIGURATION:
   - Reverse proxy to backend
   - Static file serving for frontend
   - WebSocket upgrade handling
   - SSL/TLS termination
   - Rate limiting
   - Security headers

3. KUBERNETES MANIFESTS:
   - Namespace
   - ConfigMaps and Secrets
   - Persistent Volume Claims
   - Deployments with resource limits
   - Services (ClusterIP, LoadBalancer)
   - Ingress with TLS
   - Horizontal Pod Autoscaler

4. MONITORING:
   - Prometheus metrics collection
   - Grafana dashboards
   - Loki log aggregation
   - AlertManager for ops alerts
```

---

## 10. Expansion Ideas

### 10.1 Advanced AI Features

#### 10.1.1 Multi-Factor Recognition
```
Enhance recognition accuracy by combining multiple biometric factors:

1. FACE + GAIT RECOGNITION:
   - Analyze walking patterns from video sequences
   - Train LSTM model on pose estimation keypoints
   - Combine with face embedding for higher accuracy
   - Useful when face is partially occluded

2. FACE + CLOTHING RECOGNITION:
   - Extract clothing features (color histogram, texture)
   - Person re-identification (ReID) model
   - Track subjects across non-overlapping cameras
   - Store clothing preferences in subject metadata

3. FACE + VOICE RECOGNITION:
   - Extract audio from camera streams
   - Speaker identification model
   - Combine with face for multi-modal verification
   - Useful for access control scenarios
```

#### 10.1.2 Behavioral Analysis
```
Add behavioral anomaly detection:

1. LOITERING DETECTION:
   - Track subject positions over time
   - Detect stationary periods exceeding threshold
   - Alert on suspicious loitering near sensitive areas
   - Configurable time and zone parameters

2. CROWD ANALYSIS:
   - Count people in defined zones
   - Detect crowd formation/dispersion
   - Estimate crowd density
   - Alert on overcrowding situations

3. ABANDONED OBJECT DETECTION:
   - Detect stationary objects in motion areas
   - Track object ownership (who left it)
   - Alert on potential security threats
   - Integration with baggage tracking

4. FIGHT/AGGRESSION DETECTION:
   - Analyze body pose sequences
   - Detect aggressive movements
   - Alert security personnel
   - Automatic camera zoom and recording
```

#### 10.1.3 Age, Gender, Emotion Estimation
```
Add demographic and emotional analysis:

1. AGE ESTIMATION:
   - Deep learning model for age prediction
   - Store in subject metadata
   - Analytics: age distribution over time
   - Age-restricted area monitoring

2. GENDER CLASSIFICATION:
   - High-accuracy gender detection
   - Demographic analytics
   - Marketing insights (retail scenarios)

3. EMOTION RECOGNITION:
   - Detect emotions: happy, sad, angry, surprised, neutral
   - Customer satisfaction tracking
   - Anomaly detection (fear, distress)
   - Real-time emotion alerts

4. ATTENTION ANALYSIS:
   - Gaze direction estimation
   - Dwell time on advertisements
   - Heatmaps of attention
   - Retail optimization insights
```

### 10.2 Integration Features

#### 10.2.1 Access Control Integration
```
Integrate with physical access control systems:

1. DOOR CONTROLLER API:
   - Interface with HID, Lenel, CCure systems
   - Face-based door unlock
   - Two-factor authentication (face + card)
   - Audit trail of all access events

2. VISITOR MANAGEMENT:
   - Self-service kiosk for visitor registration
   - Automatic face enrollment
   - Temporary access credentials
   - Automatic expiration and deletion

3. TIME & ATTENDANCE:
   - Clock in/out with face recognition
   - Integration with HR systems (Workday, ADP)
   - Overtime calculation
   - Attendance reports
```

#### 10.2.2 Video Management System (VMS) Integration
```
Integrate with existing VMS platforms:

1. MILESTONE XPROTECT:
   - Plugin for Milestone VMS
   - Metadata injection into video streams
   - Event-based recording triggers
   - Unified search interface

2. GENETEC SECURITY CENTER:
   - Genetec SDK integration
   - Custom analytics plugin
   - Alarm forwarding
   - Bookmark creation

3. HIKVISION/DAHUA NVR:
   - Direct NVR integration
   - ONVIF Profile S/G support
   - Event subscription
   - PTZ camera control
```

#### 10.2.3 SIEM Integration
```
Security Information and Event Management integration:

1. SPLUNK:
   - Splunk HEC for event forwarding
   - Custom Splunk app
   - Dashboards and alerts
   - Correlation with other security events

2. ELASTIC STACK:
   - Filebeat/Logstash integration
   - Elasticsearch index templates
   - Kibana dashboards
   - ML-based anomaly detection

3. QRADAR:
   - LEEF format log forwarding
   - Custom DSM (Device Support Module)
   - Offense creation
   - Reference data synchronization
```

### 10.3 Advanced Analytics

#### 10.3.1 Predictive Analytics
```
Add machine learning for predictions:

1. FOOTFALL FORECASTING:
   - Time-series forecasting (Prophet, LSTM)
   - Predict busy periods
   - Staffing optimization
   - Energy management

2. ANOMALY DETECTION:
   - Unsupervised learning on patterns
   - Detect unusual crowd movements
   - Identify suspicious behavior
   - Adaptive thresholds

3. SUBJECT REAPPEARANCE PREDICTION:
   - Predict when banned subjects might return
   - Based on historical patterns
   - Proactive alert generation
   - Resource allocation optimization
```

#### 10.3.2 Business Intelligence
```
Add business-focused analytics:

1. RETAIL ANALYTICS:
   - Customer journey mapping
   - Dwell time by zone
   - Conversion funnel analysis
   - Queue length monitoring

2. WORKPLACE ANALYTICS:
   - Space utilization tracking
   - Meeting room occupancy
   - Collaboration pattern analysis
   - Hot-desking optimization

3. SAFETY COMPLIANCE:
   - PPE detection (hard hats, vests, masks)
   - Social distancing monitoring
   - Occupancy limit enforcement
   - Compliance reporting
```

### 10.4 Mobile Features

#### 10.4.1 Mobile App
```
Build companion mobile applications:

1. SECURITY GUARD APP:
   - Real-time alert notifications
   - Subject lookup by photo
   - Incident reporting with photos
   - GPS-tagged patrol logs
   - Push-to-talk communication

2. ADMINISTRATOR APP:
   - System health monitoring
   - Camera status overview
   - User management
   - Alert acknowledgment
   - Analytics dashboards

3. EMPLOYEE SELF-SERVICE:
   - Face enrollment
   - Access history
   - Privacy settings
   - GDPR data export request
```

#### 10.4.2 Edge Computing
```
Deploy AI to edge devices:

1. EDGE AI DEVICES:
   - NVIDIA Jetson Nano/Orin
   - Coral TPU
   - Intel NUC with OpenVINO
   - On-device detection and recognition

2. EDGE GATEWAY:
   - Local processing for low-latency
   - Bandwidth optimization
   - Offline operation capability
   - Cloud synchronization

3. SMART CAMERA INTEGRATION:
   - Cameras with built-in AI
   - ONVIF Analytics service
   - Metadata streaming
   - Hybrid cloud-edge architecture
```

### 10.5 Privacy & Compliance

#### 10.5.1 Enhanced GDPR Features
```
Advanced privacy protection:

1. AUTOMATIC FACE BLURRING:
   - Blur faces in archived footage
   - Configurable retention periods
   - One-click GDPR deletion
   - Audit trail of all deletions

2. CONSENT MANAGEMENT:
   - Digital consent forms
   - Granular consent options
   - Consent withdrawal workflow
   - Automated data purging

3. PRIVACY ZONES:
   - Define privacy-sensitive areas
   - Automatic face masking in these zones
   - Exclude from recognition
   - Compliance reporting

4. DATA PORTABILITY:
   - Export all data about a subject
   - Standard formats (JSON, CSV)
   - Image downloads
   - Complete audit history
```

#### 10.5.2 Audit & Compliance
```
Enhanced auditing capabilities:

1. VIDEO AUDIT TRAIL:
   - Record who viewed what footage
   - Timestamp and user attribution
   - Tamper-proof logging
   - Compliance reports

2. CHAIN OF CUSTODY:
   - Track evidence handling
   - Digital signatures
   - Court-admissible exports
   - Legal hold capabilities

3. COMPLIANCE DASHBOARD:
   - GDPR compliance score
   - Data retention status
   - Consent statistics
   - Audit log summaries
```

### 10.6 Scalability Features

#### 10.6.1 Multi-Region Deployment
```
Scale across geographic regions:

1. FEDERATED ARCHITECTURE:
   - Central management, edge processing
   - Cross-region subject search
   - Data residency compliance
   - Disaster recovery

2. EDGE CLUSTERS:
   - Kubernetes at edge locations
   - Local data processing
   - Intermittent connectivity support
   - Sync when connected

3. CDN INTEGRATION:
   - CloudFront/Cloudflare for video
   - Global low-latency access
   - Bandwidth optimization
```

#### 10.6.2 High Availability
```
Ensure 99.99% uptime:

1. ACTIVE-ACTIVE CLUSTERING:
   - Multi-master PostgreSQL (Patroni)
   - Redis Cluster
   - Load balancer failover
   - Session replication

2. DISASTER RECOVERY:
   - Cross-region backups
   - Point-in-time recovery
   - Automated failover
   - RPO/RTO targets

3. PERFORMANCE OPTIMIZATION:
   - Read replicas for analytics
   - Connection pooling (PgBouncer)
   - Redis Cluster for cache
   - CDN for static assets
```

---

## 11. Troubleshooting

### 11.1 Common Issues

#### Database Connection Failures
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Verify connection
psql postgresql://surveillance:surveillance@localhost:5432/surveillance_db -c "SELECT 1"

# Reset database (WARNING: data loss)
docker-compose down -v
docker-compose up -d postgres
```

#### Stream Ingestion Issues
```bash
# Test RTSP stream
ffprobe -rtsp_transport tcp rtsp://user:pass@camera-ip:554/stream

# Check ingestion logs
docker-compose logs -f ingestion

# Restart ingestion service
docker-compose restart ingestion
```

#### GPU Not Detected
```bash
# Verify NVIDIA runtime
nvidia-smi

# Check Docker runtime
docker info | grep Runtime

# Rebuild with GPU support
docker-compose -f docker-compose.gpu.yml up -d
```

### 11.2 Performance Tuning

#### Database Optimization
```sql
-- Analyze tables for query planner
ANALYZE cameras;
ANALYZE subjects;
ANALYZE sightings;

-- Vacuum for space reclamation
VACUUM ANALYZE;

-- Increase work_mem for complex queries
SET work_mem = '256MB';
```

#### Redis Optimization
```bash
# Monitor Redis memory
redis-cli INFO memory

# Check slow queries
redis-cli SLOWLOG GET 10

# Configure maxmemory policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## Appendix A: API Rate Limits

| Endpoint | Rate Limit | Burst |
|----------|------------|-------|
| /api/v1/auth/login | 10/min | 5 |
| /api/v1/cameras/* | 100/min | 20 |
| /api/v1/subjects/* | 100/min | 20 |
| /api/v1/subjects/search-by-image | 30/min | 5 |
| /api/v1/alerts/* | 200/min | 50 |
| /api/v1/analytics/* | 60/min | 10 |

---

## Appendix B: Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `REDIS_URL` | Yes | - | Redis connection string |
| `MINIO_ENDPOINT` | Yes | - | MinIO server endpoint |
| `MINIO_ACCESS_KEY` | Yes | - | MinIO access key |
| `MINIO_SECRET_KEY` | Yes | - | MinIO secret key |
| `JWT_SECRET` | Yes | - | JWT signing secret |
| `JWT_EXPIRATION_HOURS` | No | 24 | Access token lifetime |
| `CORS_ORIGINS` | No | * | Allowed CORS origins |
| `LOG_LEVEL` | No | INFO | Logging level |
| `DETECTION_THRESHOLD` | No | 0.7 | Face detection threshold |
| `RECOGNITION_THRESHOLD` | No | 0.6 | Face recognition threshold |
| `GDPR_DEFAULT_RETENTION_DAYS` | No | 90 | Data retention period |

---

## Appendix C: File Structure Reference

```
surveillance-system/
├── README.md                          # Project overview
├── FULL_DOCUMENTATION.md              # This file
├── docker-compose.yml                 # Local deployment
├── docker-compose.gpu.yml             # GPU-enabled deployment
├── Makefile                           # Common commands
│
├── database/                          # Database migrations
│   ├── 01_extensions.sql
│   ├── 02_cameras.sql
│   ├── 03_subjects.sql
│   ├── 04_images.sql
│   ├── 05_sightings.sql
│   ├── 06_alerts.sql
│   ├── 07_audit.sql
│   ├── 08_users.sql
│   ├── 09_functions.sql
│   ├── 10_seed_data.sql
│   └── alembic/                       # Migration tool
│
├── backend/                           # FastAPI application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   └── v1/
│       │       ├── router.py
│       │       └── endpoints/
│       │           ├── auth.py
│       │           ├── cameras.py
│       │           ├── subjects.py
│       │           ├── sightings.py
│       │           ├── alerts.py
│       │           ├── analytics.py
│       │           ├── users.py
│       │           ├── images.py
│       │           └── websocket.py
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── redis.py
│       │   └── minio_client.py
│       ├── middleware/
│       │   ├── audit.py
│       │   └── rate_limit.py
│       ├── models/
│       │   ├── camera.py
│       │   ├── subject.py
│       │   ├── image.py
│       │   ├── sighting.py
│       │   ├── alert.py
│       │   ├── audit.py
│       │   └── user.py
│       └── schemas/
│           ├── camera.py
│           ├── subject.py
│           ├── image.py
│           ├── sighting.py
│           ├── alert.py
│           ├── user.py
│           └── analytics.py
│
├── frontend/                          # React application
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── index.css
│       ├── components/
│       │   ├── Layout.tsx
│       │   └── ProtectedRoute.tsx
│       ├── contexts/
│       │   ├── AuthContext.tsx
│       │   └── ThemeContext.tsx
│       ├── hooks/
│       │   ├── useAuth.ts
│       │   ├── useCameras.ts
│       │   ├── useSubjects.ts
│       │   ├── useAlerts.ts
│       │   └── useAnalytics.ts
│       ├── lib/
│       │   ├── api.ts
│       │   └── websocket.ts
│       ├── pages/
│       │   ├── LoginPage.tsx
│       │   ├── DashboardPage.tsx
│       │   ├── LiveViewPage.tsx
│       │   ├── SubjectsPage.tsx
│       │   ├── CamerasPage.tsx
│       │   ├── AlertsPage.tsx
│       │   ├── AnalyticsPage.tsx
│       │   ├── SettingsPage.tsx
│       │   ├── UsersPage.tsx
│       │   ├── SubjectDetailPage.tsx
│       │   └── CameraDetailPage.tsx
│       └── types/
│           └── index.ts
│
├── workers/                           # AI/ML workers
│   ├── ingestion/                     # Stream ingestion
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── main.py
│   │
│   ├── detection/                     # Face detection
│   │   ├── Dockerfile
│   │   ├── Dockerfile.gpu
│   │   ├── requirements.txt
│   │   └── src/
│   │       ├── main.py
│   │       └── models/
│   │
│   ├── recognition/                   # Face recognition
│   │   ├── Dockerfile
│   │   ├── Dockerfile.gpu
│   │   ├── requirements.txt
│   │   └── src/
│   │       ├── main.py
│   │       └── models/
│   │
│   └── alert-engine/                  # Alert processing
│       ├── Dockerfile
│       ├── requirements.txt
│       └── src/
│           └── main.py
│
├── infrastructure/                    # Deployment configs
│   ├── nginx/
│   │   └── nginx.conf
│   ├── k8s/                           # Kubernetes manifests
│   │   ├── namespace.yaml
│   │   ├── configmaps/
│   │   ├── secrets/
│   │   ├── pvc/
│   │   ├── deployments/
│   │   ├── services/
│   │   └── ingress/
│   └── monitoring/                    # Prometheus/Grafana
│       ├── prometheus.yml
│       └── grafana-dashboards/
│
└── docs/                              # Additional documentation
    ├── API_REFERENCE.md
    ├── DEPLOYMENT_GUIDE.md
    ├── DEVELOPMENT_GUIDE.md
    └── USER_MANUAL.md
```

---

**Document Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Author**: Surveillance System Team
