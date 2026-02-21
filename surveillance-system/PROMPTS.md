# Complete Prompts for Recreation
## IPTV Facial Recognition Surveillance System

---

This document contains detailed, step-by-step prompts that can be used to recreate the entire surveillance system from scratch. Each prompt is self-contained and builds upon previous work.

---

## Table of Contents

1. [Phase 1: Database Schema](#phase-1-database-schema)
2. [Phase 2: Backend API](#phase-2-backend-api)
3. [Phase 3: Frontend Application](#phase-3-frontend-application)
4. [Phase 4: AI/ML Pipeline](#phase-4-aiml-pipeline)
5. [Phase 5: Infrastructure & Deployment](#phase-5-infrastructure--deployment)
6. [Phase 6: Testing & Documentation](#phase-6-testing--documentation)

---

## Phase 1: Database Schema

### Prompt 1.1: Database Foundation

```
Create a PostgreSQL database schema for a facial recognition surveillance system with the following requirements:

CORE REQUIREMENTS:
1. Use PostgreSQL with pgvector extension for 512-dimensional face embeddings
2. Support time-series data partitioning for high-volume sightings
3. Implement audit logging for GDPR compliance
4. Design for 50+ concurrent camera streams
5. Handle 1M+ daily face detections

CREATE THE FOLLOWING TABLES:

1. extensions.sql - Enable required extensions (pgvector, uuid-ossp, pg_trgm)

2. cameras.sql - Camera management:
   - id (UUID PK), name, location, stream_url
   - status (active/inactive/error)
   - fps, resolution, detection_enabled, recognition_enabled
   - config (JSONB for ROI, thresholds)
   - created_at, updated_at, last_seen_at

3. subjects.sql - People in the system:
   - id (UUID PK), name, external_id
   - watchlist_id (FK), status, alert_on_match
   - metadata (JSONB for custom fields)
   - created_at, updated_at, last_seen_at

4. watchlists.sql - Subject categories:
   - id (SERIAL PK), name, description, color
   - priority, is_active

5. images.sql - Subject reference images:
   - id (UUID PK), subject_id (FK)
   - image_path, embedding (vector(512))
   - quality_score, face_count, landmarks
   - created_at

6. sightings.sql - Detection events:
   - id (UUID PK), camera_id (FK), subject_id (FK nullable)
   - confidence, bounding_box, image_path
   - embedding (vector(512)), metadata
   - detected_at, created_at
   - Partition by detected_at (monthly)

7. alerts.sql - Recognition alerts:
   - id (UUID PK), sighting_id (FK), subject_id (FK)
   - severity, message, status, acknowledged
   - created_at, acknowledged_at

8. audit_logs.sql - Compliance logging:
   - id (UUID PK), user_id, action, table_name
   - record_id, old_values, new_values
   - ip_address, user_agent, created_at

9. users.sql - System users:
   - id (UUID PK), username, email, hashed_password
   - role (admin/operator/viewer/auditor)
   - is_active, last_login_at, created_at

Include:
- Proper indexes for all foreign keys
- GIN indexes for JSONB fields
- IVFFlat index for vector similarity search
- Triggers for updated_at timestamps
- Row Level Security policies
```

### Prompt 1.2: Database Functions

```
Create PostgreSQL functions for the surveillance system:

1. Similarity Search Function:
   - Function: find_similar_faces(embedding vector(512), threshold float, top_k int)
   - Returns: table with subject_id, confidence, image_id
   - Uses cosine similarity for vector comparison

2. Sighting Statistics Function:
   - Function: get_sighting_stats(camera_id UUID, from_date date, to_date date)
   - Returns: daily counts of detections and recognitions

3. Audit Log Trigger:
   - Trigger: audit_trigger on all tables
   - Automatically logs INSERT, UPDATE, DELETE operations
   - Captures old and new values as JSONB

4. Partition Management:
   - Function: create_monthly_partition(table_name text, year int, month int)
   - Automatically creates time-series partitions

5. Data Retention:
   - Function: purge_old_data(retention_days int)
   - Deletes or anonymizes data older than retention period
```

---

## Phase 2: Backend API

### Prompt 2.1: FastAPI Project Structure

```
Create a FastAPI backend for the surveillance system with this structure:

backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── auth.py
│   │       │   ├── cameras.py
│   │       │   ├── subjects.py
│   │       │   ├── sightings.py
│   │       │   ├── alerts.py
│   │       │   ├── analytics.py
│   │       │   └── users.py
│   │       └── deps.py      # Dependencies
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Settings management
│   │   ├── security.py      # JWT, password hashing
│   │   ├── database.py      # Database connection
│   │   ├── redis.py         # Redis client
│   │   └── minio.py         # MinIO/S3 client
│   ├── models/
│   │   ├── __init__.py
│   │   ├── camera.py
│   │   ├── subject.py
│   │   ├── sighting.py
│   │   ├── alert.py
│   │   ├── audit.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── camera.py
│   │   ├── subject.py
│   │   ├── sighting.py
│   │   ├── alert.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── camera_service.py
│   │   ├── subject_service.py
│   │   ├── recognition_service.py
│   │   └── alert_service.py
│   └── middleware/
│       ├── __init__.py
│       ├── audit.py
│       └── rate_limit.py
├── alembic/                 # Database migrations
├── tests/
├── Dockerfile
└── requirements.txt

REQUIREMENTS:
- FastAPI 0.104+
- SQLAlchemy 2.0+ with async support
- Pydantic 2.0+
- Alembic for migrations
- Redis-py for caching
- MinIO client for object storage
- python-jose for JWT
- passlib for password hashing
- psycopg2-binary and asyncpg
- pgvector Python bindings
```

### Prompt 2.2: Configuration & Core

```
Implement the core configuration and security modules:

1. config.py:
   - Use pydantic-settings for environment variables
   - Database config (URL, pool size, max overflow)
   - Redis config (host, port, password)
   - MinIO config (endpoint, access key, secret key, bucket)
   - JWT config (secret key, algorithm, expiration)
   - Camera defaults (fps, resolution, thresholds)
   - Email/SMTP config for alerts

2. security.py:
   - Password hashing with bcrypt
   - JWT token creation and verification
   - Password validation (min length, complexity)
   - Token refresh logic

3. database.py:
   - SQLAlchemy async engine setup
   - SessionLocal for dependency injection
   - Base model class with common fields
   - Connection pooling configuration

4. redis.py:
   - Async Redis client singleton
   - Connection pool management
   - Helper methods for common operations

5. minio.py:
   - MinIO client singleton
   - Methods: upload_file, download_file, delete_file, get_presigned_url
   - Bucket creation on startup
```

### Prompt 2.3: API Endpoints

```
Implement all REST API endpoints:

AUTHENTICATION:
POST   /v1/auth/login              - Login with username/password
POST   /v1/auth/refresh            - Refresh access token
POST   /v1/auth/logout             - Logout (invalidate token)
GET    /v1/auth/me                 - Get current user

CAMERAS:
GET    /v1/cameras                 - List cameras (paginated, filterable)
POST   /v1/cameras                 - Create camera
GET    /v1/cameras/{id}            - Get camera details
PUT    /v1/cameras/{id}            - Update camera
DELETE /v1/cameras/{id}            - Delete camera
GET    /v1/cameras/{id}/stream     - Get live stream URL
GET    /v1/cameras/{id}/stats      - Get camera statistics
POST   /v1/cameras/{id}/enable     - Enable detection
POST   /v1/cameras/{id}/disable    - Disable detection

SUBJECTS:
GET    /v1/subjects                - List subjects (paginated, searchable)
POST   /v1/subjects                - Create subject
GET    /v1/subjects/{id}           - Get subject details
PUT    /v1/subjects/{id}           - Update subject
DELETE /v1/subjects/{id}           - Delete subject
POST   /v1/subjects/{id}/images    - Upload subject image
GET    /v1/subjects/{id}/images    - List subject images
DELETE /v1/subjects/{id}/images/{image_id} - Delete image
POST   /v1/subjects/search         - Search by face image

SIGHTINGS:
GET    /v1/sightings               - List sightings (paginated, filterable)
GET    /v1/sightings/{id}          - Get sighting details
GET    /v1/sightings/{id}/image    - Get sighting image
GET    /v1/sightings/{id}/context  - Get full frame with overlay
POST   /v1/sightings/export        - Export sightings (CSV/JSON)

ALERTS:
GET    /v1/alerts                  - List alerts (paginated, filterable)
GET    /v1/alerts/{id}             - Get alert details
POST   /v1/alerts/{id}/acknowledge - Acknowledge alert
POST   /v1/alerts/{id}/resolve     - Resolve alert
GET    /v1/alerts/rules            - List alert rules
POST   /v1/alerts/rules            - Create alert rule
PUT    /v1/alerts/rules/{id}       - Update alert rule
DELETE /v1/alerts/rules/{id}       - Delete alert rule

ANALYTICS:
GET    /v1/analytics/dashboard     - Get dashboard statistics
GET    /v1/analytics/trends        - Get detection trends
GET    /v1/analytics/cameras       - Get camera analytics
GET    /v1/analytics/subjects/{id} - Get subject analytics
POST   /v1/analytics/reports       - Generate report

USERS:
GET    /v1/users                   - List users (admin only)
POST   /v1/users                   - Create user
GET    /v1/users/{id}              - Get user details
PUT    /v1/users/{id}              - Update user
DELETE /v1/users/{id}              - Delete user
POST   /v1/users/{id}/change-password - Change password
GET    /v1/users/me                - Get current user

WEBSOCKET:
WS     /v1/ws                      - WebSocket for real-time updates

Implement proper:
- Request/response validation with Pydantic
- Authentication dependencies
- Role-based access control
- Error handling
- Pagination
- Filtering and sorting
- Rate limiting
```

### Prompt 2.4: Services & Business Logic

```
Implement the service layer with business logic:

1. camera_service.py:
   - create_camera, update_camera, delete_camera
   - get_camera_stream_url (generate RTSP/HTTP URL)
   - validate_stream_url (check if camera is accessible)
   - get_camera_stats (aggregations from sightings)
   - enable/disable detection

2. subject_service.py:
   - create_subject, update_subject, delete_subject
   - add_subject_image (extract embedding, validate quality)
   - remove_subject_image
   - search_by_face (vector similarity search)
   - get_subject_timeline (all sightings ordered by time)

3. recognition_service.py:
   - process_detection (face crop, quality check)
   - find_matches (vector search against gallery)
   - update_subject_embeddings (when new images added)
   - get_recognition_stats

4. alert_service.py:
   - create_alert (on subject match)
   - acknowledge_alert, resolve_alert
   - get_alert_rules, create_alert_rule
   - evaluate_alert_rules (check if alert should fire)
   - send_notifications (email, webhook, push)

5. analytics_service.py:
   - get_dashboard_stats (summary metrics)
   - get_trends (time-series data)
   - get_camera_analytics (per-camera metrics)
   - get_subject_analytics (per-subject metrics)
   - generate_report (export to PDF/Excel)
```

---

## Phase 3: Frontend Application

### Prompt 3.1: React Project Setup

```
Create a React TypeScript frontend for the surveillance system:

frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── layout/          # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── MainLayout.tsx
│   │   ├── camera/          # Camera components
│   │   │   ├── CameraCard.tsx
│   │   │   ├── CameraGrid.tsx
│   │   │   ├── CameraForm.tsx
│   │   │   └── LiveStream.tsx
│   │   ├── subject/         # Subject components
│   │   │   ├── SubjectCard.tsx
│   │   │   ├── SubjectForm.tsx
│   │   │   ├── SubjectGallery.tsx
│   │   │   └── FaceUpload.tsx
│   │   ├── sighting/        # Sighting components
│   │   │   ├── SightingCard.tsx
│   │   │   ├── SightingList.tsx
│   │   │   └── SightingDetail.tsx
│   │   ├── alert/           # Alert components
│   │   │   ├── AlertCard.tsx
│   │   │   ├── AlertList.tsx
│   │   │   └── AlertBadge.tsx
│   │   └── analytics/       # Analytics components
│   │       ├── StatCard.tsx
│   │       ├── TrendChart.tsx
│   │       └── CameraHeatmap.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── LiveView.tsx
│   │   ├── CamerasPage.tsx
│   │   ├── CameraDetail.tsx
│   │   ├── SubjectsPage.tsx
│   │   ├── SubjectDetail.tsx
│   │   ├── SightingsPage.tsx
│   │   ├── AlertsPage.tsx
│   │   ├── AnalyticsPage.tsx
│   │   ├── SettingsPage.tsx
│   │   ├── UsersPage.tsx
│   │   ├── Login.tsx
│   │   └── NotFound.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useCameras.ts
│   │   ├── useSubjects.ts
│   │   ├── useSightings.ts
│   │   ├── useAlerts.ts
│   │   ├── useAnalytics.ts
│   │   ├── useWebSocket.ts
│   │   └── useLocalStorage.ts
│   ├── contexts/
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   ├── utils.ts         # Utilities
│   │   └── constants.ts     # Constants
│   ├── types/
│   │   ├── camera.ts
│   │   ├── subject.ts
│   │   ├── sighting.ts
│   │   ├── alert.ts
│   │   └── user.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js

TECH STACK:
- React 18+ with TypeScript
- Vite for build tooling
- React Router v6 for routing
- TanStack Query (React Query) for data fetching
- Zustand or Context for state management
- Tailwind CSS for styling
- shadcn/ui component library
- Recharts for charts
- React Hook Form for forms
- Zod for validation
- Axios for HTTP requests
- Socket.io-client for WebSocket
```

### Prompt 3.2: API Client & Hooks

```
Implement the API client and custom hooks:

1. api.ts:
   - Create axios instance with base URL
   - Request interceptor to add JWT token
   - Response interceptor for error handling
   - Methods for all API endpoints
   - Type-safe request/response types

2. useAuth.ts:
   - login(credentials)
   - logout()
   - refreshToken()
   - isAuthenticated
   - currentUser
   - hasPermission(permission)

3. useCameras.ts:
   - useCameras(queryParams) - list with pagination
   - useCamera(id) - get single camera
   - useCreateCamera() - mutation
   - useUpdateCamera() - mutation
   - useDeleteCamera() - mutation
   - useCameraStats(id) - get statistics

4. useSubjects.ts:
   - useSubjects(queryParams)
   - useSubject(id)
   - useCreateSubject()
   - useUpdateSubject()
   - useDeleteSubject()
   - useUploadImage()
   - useSearchByFace()

5. useSightings.ts:
   - useSightings(queryParams)
   - useSighting(id)
   - useExportSightings()

6. useAlerts.ts:
   - useAlerts(queryParams)
   - useAlert(id)
   - useAcknowledgeAlert()
   - useResolveAlert()
   - useUnreadCount()

7. useAnalytics.ts:
   - useDashboardStats()
   - useTrends(params)
   - useCameraAnalytics()
   - useSubjectAnalytics(id)

8. useWebSocket.ts:
   - connect()
   - disconnect()
   - subscribe(topic, callback)
   - onDetection(callback)
   - onRecognition(callback)
   - onAlert(callback)
```

### Prompt 3.3: Pages & Components

```
Implement all pages with full functionality:

1. Login.tsx:
   - Username/password form
   - Form validation with Zod
   - Error handling
   - Redirect on success
   - "Remember me" option

2. Dashboard.tsx:
   - Summary statistics cards
   - Hourly activity chart
   - Recent alerts list
   - Camera status overview
   - Quick actions

3. LiveView.tsx:
   - Grid of live camera streams
   - Camera selection/filtering
   - Fullscreen mode
   - Detection overlay
   - PTZ controls (if supported)

4. CamerasPage.tsx:
   - Camera list with search
   - Add camera button
   - Camera status indicators
   - Edit/delete actions
   - Bulk operations

5. CameraDetail.tsx:
   - Camera information
   - Live stream
   - Configuration form
   - Statistics tab
   - Recent sightings

6. SubjectsPage.tsx:
   - Subject gallery with search
   - Filter by watchlist
   - Add subject button
   - Import/export
   - Bulk operations

7. SubjectDetail.tsx:
   - Subject information
   - Image gallery
   - Upload new images
   - Timeline of sightings
   - Edit/delete actions

8. SightingsPage.tsx:
   - Sighting list with filters
   - Date range picker
   - Camera filter
   - Subject filter
   - Export functionality
   - Image preview

9. AlertsPage.tsx:
   - Alert list with severity colors
   - Filter by status/severity
   - Acknowledge/resolve actions
   - Alert rules management
   - Notification settings

10. AnalyticsPage.tsx:
    - Trend charts (line, bar)
    - Camera comparison
    - Subject frequency
    - Heatmap visualization
    - Export reports

11. SettingsPage.tsx:
    - General settings
    - Camera defaults
    - Detection thresholds
    - Alert configuration
    - Data retention
    - System info

12. UsersPage.tsx (admin only):
    - User list
    - Add/edit user
    - Role assignment
    - Permission management
```

---

## Phase 4: AI/ML Pipeline

### Prompt 4.1: Stream Ingestion Worker

```
Create a stream ingestion worker:

workers/ingestion/
├── Dockerfile
├── requirements.txt
├── config.py
├── stream_manager.py
├── frame_extractor.py
└── main.py

REQUIREMENTS:
- FFmpeg for stream processing
- OpenCV for frame extraction
- Redis for message queuing
- Asyncio for concurrent streams

FUNCTIONALITY:
1. Connect to multiple RTSP streams concurrently
2. Extract frames at configurable FPS
3. Apply ROI (Region of Interest) cropping
4. Push frames to Redis Streams
5. Handle stream reconnection on failure
6. Monitor stream health
7. Support H.264/H.265 codecs

CONFIGURATION:
- frame_sample_rate: 5 (process 5 fps)
- reconnect_attempts: 5
- reconnect_delay: 5 seconds
- buffer_size: 30 frames

REDIS STREAM FORMAT:
stream: camera:{camera_id}:frames
{
    "camera_id": "uuid",
    "timestamp": "2024-01-20T14:25:30Z",
    "frame_data": "base64_encoded_jpeg",
    "sequence": 12345
}
```

### Prompt 4.2: Face Detection Worker

```
Create a face detection worker using YOLOv8:

workers/detection/
├── Dockerfile
├── requirements.txt
├── config.py
├── model.py
├── detector.py
└── main.py

REQUIREMENTS:
- ultralytics (YOLOv8)
- PyTorch with CUDA support
- OpenCV
- NumPy
- Redis
- Pillow

FUNCTIONALITY:
1. Consume frames from Redis Streams
2. Run YOLOv8-face detection
3. Extract face crops
4. Filter by minimum face size
5. Quality check (blur detection)
6. Push detections to next queue

MODEL:
- YOLOv8n-face (nano) for speed
- Or YOLOv8m-face (medium) for accuracy
- Input size: 640x640
- Confidence threshold: 0.7
- NMS IoU threshold: 0.45

OUTPUT FORMAT:
stream: faces:detected
{
    "camera_id": "uuid",
    "timestamp": "2024-01-20T14:25:30Z",
    "detections": [
        {
            "bbox": [x, y, width, height],
            "confidence": 0.92,
            "face_crop": "base64_encoded_jpeg",
            "quality_score": 0.85
        }
    ]
}

OPTIMIZATION:
- Batch processing (4-8 frames)
- GPU acceleration
- Model quantization (INT8)
- TensorRT for NVIDIA GPUs
```

### Prompt 4.3: Face Recognition Worker

```
Create a face recognition worker using ArcFace:

workers/recognition/
├── Dockerfile
├── requirements.txt
├── config.py
├── model.py
├── recognizer.py
├── database.py
└── main.py

REQUIREMENTS:
- insightface (ArcFace)
- PyTorch with CUDA
- ONNX Runtime
- pgvector Python bindings
- SQLAlchemy
- NumPy
- scikit-learn

FUNCTIONALITY:
1. Consume detections from Redis
2. Extract 512-dimensional embeddings
3. Search against subject gallery
4. Apply similarity threshold
5. Store results in database
6. Trigger alerts on matches

MODEL:
- ArcFace (iresnet100)
- Input: 112x112 RGB
- Output: 512-dim embedding
- Normalized embeddings

RECOGNITION PIPELINE:
1. Face alignment using landmarks
2. Embedding extraction
3. Vector similarity search (cosine)
4. Threshold: 0.6 (configurable)
5. Top-k matches (k=5)

DATABASE SEARCH:
```sql
SELECT subject_id, image_id, 
       1 - (embedding <=> query_embedding) as similarity
FROM images
WHERE 1 - (embedding <=> query_embedding) > threshold
ORDER BY embedding <=> query_embedding
LIMIT 5;
```

OUTPUT:
- Store sighting in database
- If match found: create alert
- Update subject last_seen_at
```

### Prompt 4.4: Alert Engine

```
Create an alert processing engine:

workers/alert-engine/
├── Dockerfile
├── requirements.txt
├── config.py
├── alert_processor.py
├── notification_service.py
└── main.py

FUNCTIONALITY:
1. Listen for recognition events
2. Evaluate alert rules
3. Send notifications
4. Escalate unacknowledged alerts

ALERT RULES:
- Watchlist-based rules
- Time-based rules (after hours)
- Location-based rules
- Confidence thresholds
- Frequency thresholds

NOTIFICATION CHANNELS:
- Email (SMTP)
- Webhook (HTTP POST)
- Push notifications (Firebase)
- SMS (Twilio)
- Slack/Teams integration

ESCALATION:
- Acknowledgment timeout: 5 minutes
- Escalate to supervisor
- Increase severity
- Send to additional recipients
```

---

## Phase 5: Infrastructure & Deployment

### Prompt 5.1: Docker Compose

```
Create a complete docker-compose.yml:

SERVICES:
1. postgres:
   - Image: ankane/pgvector:latest
   - Ports: 5432:5432
   - Volumes: postgres_data:/var/lib/postgresql/data
   - Environment: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

2. redis:
   - Image: redis:7-alpine
   - Ports: 6379:6379
   - Volumes: redis_data:/data
   - Command: redis-server --appendonly yes

3. minio:
   - Image: minio/minio:latest
   - Ports: 9000:9000, 9001:9001
   - Volumes: minio_data:/data
   - Command: server /data --console-address ":9001"

4. backend:
   - Build: ./backend
   - Ports: 8000:8000
   - Depends_on: postgres, redis, minio
   - Environment: All config from .env
   - Volumes: ./backend:/app (dev mode)

5. frontend:
   - Build: ./frontend
   - Ports: 3000:80
   - Depends_on: backend

6. nginx:
   - Image: nginx:alpine
   - Ports: 80:80, 443:443
   - Volumes: ./nginx.conf:/etc/nginx/nginx.conf
   - Depends_on: backend, frontend

7. ingestion-worker:
   - Build: ./workers/ingestion
   - Depends_on: redis
   - Deploy: replicas: 1

8. detection-worker:
   - Build: ./workers/detection
   - Depends_on: redis, postgres
   - Deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: 1
             capabilities: [gpu]

9. recognition-worker:
   - Build: ./workers/recognition
   - Depends_on: redis, postgres
   - Deploy: GPU resources

10. alert-engine:
    - Build: ./workers/alert-engine
    - Depends_on: redis, postgres

VOLUMES:
- postgres_data
- redis_data
- minio_data
```

### Prompt 5.2: Dockerfiles

```
Create optimized Dockerfiles for each service:

1. backend/Dockerfile:
   - Python 3.11 slim base
   - Install system dependencies
   - Copy requirements.txt
   - Install Python packages
   - Copy application code
   - Expose port 8000
   - CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000

2. frontend/Dockerfile:
   - Node 20 base for build
   - Copy package.json
   - Install dependencies
   - Build application
   - Nginx alpine for serving
   - Copy built files to nginx html
   - Copy nginx.conf

3. workers/detection/Dockerfile:
   - NVIDIA CUDA base image
   - Install Python, OpenCV
   - Install PyTorch with CUDA
   - Install ultralytics
   - Copy worker code
   - Download YOLOv8 model

4. workers/recognition/Dockerfile:
   - NVIDIA CUDA base image
   - Install insightface, onnxruntime-gpu
   - Download ArcFace model
   - Copy worker code
```

### Prompt 5.3: Kubernetes Manifests

```
Create Kubernetes deployment manifests:

1. namespace.yaml - surveillance namespace

2. configmap.yaml - Application configuration

3. secret.yaml - Sensitive data (base64 encoded)

4. postgres-statefulset.yaml:
   - StatefulSet with 1 replica
   - PersistentVolumeClaim
   - Service

5. redis-deployment.yaml:
   - Deployment
   - PersistentVolumeClaim
   - Service

6. minio-deployment.yaml:
   - Deployment
   - PersistentVolumeClaim
   - Service

7. backend-deployment.yaml:
   - Deployment with 3 replicas
   - Service (ClusterIP)
   - HorizontalPodAutoscaler
   - Liveness/Readiness probes

8. frontend-deployment.yaml:
   - Deployment
   - Service

9. worker-deployment.yaml:
   - Separate deployments for each worker type
   - GPU node selector for AI workers

10. ingress.yaml:
    - NGINX Ingress
    - TLS configuration
    - Path-based routing
```

---

## Phase 6: Testing & Documentation

### Prompt 6.1: Test Suite

```
Create comprehensive tests:

backend/tests/
├── conftest.py
├── unit/
│   ├── test_security.py
│   ├── test_models.py
│   └── test_services.py
├── integration/
│   ├── test_auth.py
│   ├── test_cameras.py
│   ├── test_subjects.py
│   ├── test_sightings.py
│   └── test_alerts.py
└── e2e/
    └── test_full_pipeline.py

TEST REQUIREMENTS:
- pytest with async support
- pytest-asyncio
- httpx for async HTTP client
- factory-boy for test data
- faker for fake data
- coverage reporting

TEST CASES:
1. Authentication: login, logout, token refresh, invalid credentials
2. Cameras: CRUD, stream validation, stats
3. Subjects: CRUD, image upload, face search
4. Sightings: filtering, pagination, export
5. Alerts: creation, acknowledgment, rules
6. Full pipeline: frame → detection → recognition → alert
```

### Prompt 6.2: Documentation

```
Create comprehensive documentation:

1. README.md:
   - Project overview
   - Features list
   - Quick start guide
   - Screenshots
   - Architecture diagram

2. API_REFERENCE.md:
   - All endpoints
   - Request/response examples
   - Authentication
   - Error codes
   - Rate limiting

3. DEPLOYMENT_GUIDE.md:
   - Prerequisites
   - Docker Compose deployment
   - Kubernetes deployment
   - SSL/TLS setup
   - Backup/restore
   - Monitoring

4. EXPANSION_FEATURES.md:
   - Advanced AI features
   - Analytics enhancements
   - Enterprise integrations
   - Edge computing
   - Multi-region deployment

5. PROMPTS.md (this file):
   - Recreation prompts
   - Step-by-step instructions
```

---

## Quick Start Commands

```bash
# 1. Clone and setup
git clone <repo>
cd surveillance-system
cp .env.example .env
# Edit .env with your settings

# 2. Start infrastructure
docker compose up -d postgres redis minio

# 3. Run migrations
docker compose run --rm backend alembic upgrade head

# 4. Start all services
docker compose up -d

# 5. Create admin user
docker compose exec backend python scripts/create_admin.py

# 6. Access application
# Frontend: http://localhost:3000
# API: http://localhost:8000/v1
# MinIO: http://localhost:9001
```

---

## Summary

This document provides complete prompts to recreate the IPTV Facial Recognition Surveillance System from scratch. Follow the phases in order:

1. **Phase 1**: Set up the database schema with all tables and functions
2. **Phase 2**: Build the FastAPI backend with all endpoints
3. **Phase 3**: Create the React frontend with all pages
4. **Phase 4**: Implement the AI/ML workers
5. **Phase 5**: Configure Docker and Kubernetes deployment
6. **Phase 6**: Add tests and documentation

Each prompt is self-contained and can be given to an AI assistant or developer to implement that specific component.
