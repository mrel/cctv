# API Reference Documentation
## IPTV Facial Recognition Surveillance System

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [Cameras API](#2-cameras-api)
3. [Subjects API](#3-subjects-api)
4. [Sightings API](#4-sightings-api)
5. [Alerts API](#5-alerts-api)
6. [Analytics API](#6-analytics-api)
7. [Users API](#7-users-api)
8. [WebSocket API](#8-websocket-api)
9. [Error Codes](#9-error-codes)
10. [Rate Limiting](#10-rate-limiting)

---

## Base URL

```
Production: https://api.surveillance.local/v1
Development: http://localhost:8000/v1
```

## Authentication

All API requests require authentication using JWT tokens.

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "permissions": ["cameras:read", "cameras:write", ...]
  }
}
```

### Using Tokens

Include the access token in all requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Refresh Token

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 2. Cameras API

### List Cameras

```http
GET /cameras?page=1&page_size=20&status=active&search=entrance
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | Page number (default: 1) |
| page_size | integer | Items per page (default: 20, max: 100) |
| status | string | Filter by status: active, inactive, error |
| search | string | Search by name or location |

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Main Entrance Camera",
      "location": "Building A - Main Entrance",
      "stream_url": "rtsp://camera1.local/stream",
      "status": "active",
      "fps": 15,
      "resolution": "1920x1080",
      "detection_enabled": true,
      "recognition_enabled": true,
      "created_at": "2024-01-15T10:30:00Z",
      "last_seen_at": "2024-01-20T14:25:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

### Get Camera Details

```http
GET /cameras/{camera_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Main Entrance Camera",
  "location": "Building A - Main Entrance",
  "stream_url": "rtsp://camera1.local/stream",
  "status": "active",
  "fps": 15,
  "resolution": "1920x1080",
  "detection_enabled": true,
  "recognition_enabled": true,
  "config": {
    "detection_threshold": 0.7,
    "recognition_threshold": 0.6,
    "roi": [[100, 100], [1820, 100], [1820, 980], [100, 980]],
    "min_face_size": 80
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-18T09:15:00Z",
  "last_seen_at": "2024-01-20T14:25:00Z"
}
```

### Create Camera

```http
POST /cameras
Content-Type: application/json

{
  "name": "New Camera",
  "location": "Building B - Parking",
  "stream_url": "rtsp://camera2.local/stream",
  "fps": 15,
  "resolution": "1920x1080",
  "detection_enabled": true,
  "recognition_enabled": true,
  "config": {
    "detection_threshold": 0.7,
    "recognition_threshold": 0.6
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "New Camera",
  "location": "Building B - Parking",
  "status": "active",
  "created_at": "2024-01-20T14:30:00Z"
}
```

### Update Camera

```http
PUT /cameras/{camera_id}
Content-Type: application/json

{
  "name": "Updated Camera Name",
  "detection_enabled": false
}
```

### Delete Camera

```http
DELETE /cameras/{camera_id}
```

**Response:** `204 No Content`

### Get Camera Stream

```http
GET /cameras/{camera_id}/stream
```

Returns MJPEG stream for live viewing.

### Get Camera Stats

```http
GET /cameras/{camera_id}/stats?from=2024-01-01&to=2024-01-20
```

**Response:**
```json
{
  "camera_id": "550e8400-e29b-41d4-a716-446655440000",
  "period": {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-20T23:59:59Z"
  },
  "total_detections": 15420,
  "total_recognitions": 8750,
  "unique_subjects": 342,
  "average_daily_detections": 771,
  "peak_hour": "08:00-09:00",
  "uptime_percentage": 99.2
}
```

---

## 3. Subjects API

### List Subjects

```http
GET /subjects?page=1&page_size=20&watchlist=1&search=john
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | Page number |
| page_size | integer | Items per page |
| watchlist | integer | Filter by watchlist ID |
| status | string | Filter by status |
| search | string | Search by name |

**Response:**
```json
{
  "items": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "John Smith",
      "external_id": "EMP001",
      "watchlist_id": 1,
      "watchlist_name": "Employees",
      "status": "active",
      "alert_on_match": true,
      "image_count": 5,
      "created_at": "2024-01-10T08:00:00Z",
      "last_seen_at": "2024-01-20T09:15:00Z"
    }
  ],
  "total": 1250,
  "page": 1,
  "page_size": 20,
  "pages": 63
}
```

### Get Subject Details

```http
GET /subjects/{subject_id}
```

**Response:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "name": "John Smith",
  "external_id": "EMP001",
  "watchlist_id": 1,
  "watchlist_name": "Employees",
  "status": "active",
  "alert_on_match": true,
  "metadata": {
    "department": "Security",
    "employee_id": "EMP001",
    "access_level": "Level 3"
  },
  "images": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "image_url": "/api/v1/subjects/.../image.jpg",
      "quality_score": 0.92,
      "created_at": "2024-01-10T08:00:00Z"
    }
  ],
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "last_seen_at": "2024-01-20T09:15:00Z"
}
```

### Create Subject

```http
POST /subjects
Content-Type: application/json

{
  "name": "Jane Doe",
  "external_id": "EMP002",
  "watchlist_id": 1,
  "alert_on_match": true,
  "metadata": {
    "department": "IT",
    "employee_id": "EMP002"
  }
}
```

### Update Subject

```http
PUT /subjects/{subject_id}
Content-Type: application/json

{
  "name": "Jane Smith",
  "alert_on_match": false
}
```

### Delete Subject

```http
DELETE /subjects/{subject_id}
```

### Upload Subject Image

```http
POST /subjects/{subject_id}/images
Content-Type: multipart/form-data

image: [binary image data]
quality_threshold: 0.7
```

**Response:**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "subject_id": "770e8400-e29b-41d4-a716-446655440002",
  "image_url": "/api/v1/subjects/.../image.jpg",
  "quality_score": 0.89,
  "embedding_stored": true,
  "created_at": "2024-01-20T14:30:00Z"
}
```

### Search by Face

```http
POST /subjects/search
Content-Type: multipart/form-data

image: [binary image data]
threshold: 0.7
top_k: 10
```

**Response:**
```json
{
  "matches": [
    {
      "subject": {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "name": "John Smith",
        "external_id": "EMP001"
      },
      "confidence": 0.92,
      "matched_image_id": "880e8400-e29b-41d4-a716-446655440003"
    }
  ],
  "processing_time_ms": 245
}
```

---

## 4. Sightings API

### List Sightings

```http
GET /sightings?page=1&page_size=50&camera_id=xxx&subject_id=xxx&from=2024-01-01&to=2024-01-20
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | Page number |
| page_size | integer | Items per page (max: 100) |
| camera_id | uuid | Filter by camera |
| subject_id | uuid | Filter by subject |
| from | datetime | Start date (ISO 8601) |
| to | datetime | End date (ISO 8601) |
| confidence_min | float | Minimum confidence (0-1) |
| matched_only | boolean | Only matched sightings |

**Response:**
```json
{
  "items": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "camera_id": "550e8400-e29b-41d4-a716-446655440000",
      "camera_name": "Main Entrance Camera",
      "subject_id": "770e8400-e29b-41d4-a716-446655440002",
      "subject_name": "John Smith",
      "confidence": 0.92,
      "bounding_box": {
        "x": 450,
        "y": 200,
        "width": 120,
        "height": 150
      },
      "image_url": "/api/v1/sightings/.../image.jpg",
      "detected_at": "2024-01-20T14:25:30Z",
      "created_at": "2024-01-20T14:25:31Z"
    }
  ],
  "total": 15420,
  "page": 1,
  "page_size": 50,
  "pages": 309
}
```

### Get Sighting Details

```http
GET /sightings/{sighting_id}
```

### Get Sighting Image

```http
GET /sightings/{sighting_id}/image
```

Returns the cropped face image.

### Get Sighting Context

```http
GET /sightings/{sighting_id}/context
```

Returns the full frame image with bounding box overlay.

### Export Sightings

```http
POST /sightings/export
Content-Type: application/json

{
  "camera_ids": ["550e8400-..."],
  "subject_ids": ["770e8400-..."],
  "from": "2024-01-01T00:00:00Z",
  "to": "2024-01-20T23:59:59Z",
  "format": "csv",
  "include_images": false
}
```

**Response:**
```json
{
  "export_id": "bb0e8400-e29b-41d4-a716-446655440006",
  "status": "processing",
  "download_url": null,
  "expires_at": "2024-01-21T14:30:00Z"
}
```

---

## 5. Alerts API

### List Alerts

```http
GET /alerts?page=1&page_size=20&status=pending&severity=high&acknowledged=false
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | pending, acknowledged, resolved, dismissed |
| severity | string | low, medium, high, critical |
| acknowledged | boolean | Filter by acknowledgment |
| watchlist_id | integer | Filter by watchlist |

**Response:**
```json
{
  "items": [
    {
      "id": "cc0e8400-e29b-41d4-a716-446655440007",
      "sighting_id": "aa0e8400-e29b-41d4-a716-446655440005",
      "subject_id": "770e8400-e29b-41d4-a716-446655440002",
      "subject_name": "John Smith",
      "watchlist_name": "Employees",
      "severity": "medium",
      "message": "Employee John Smith detected at Main Entrance",
      "status": "pending",
      "acknowledged": false,
      "image_url": "/api/v1/alerts/.../image.jpg",
      "created_at": "2024-01-20T14:25:31Z"
    }
  ],
  "total": 45,
  "unacknowledged_count": 12,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

### Get Alert Details

```http
GET /alerts/{alert_id}
```

### Acknowledge Alert

```http
POST /alerts/{alert_id}/acknowledge
Content-Type: application/json

{
  "notes": "Verified employee entry"
}
```

### Resolve Alert

```http
POST /alerts/{alert_id}/resolve
Content-Type: application/json

{
  "resolution": "authorized_access",
  "notes": "Employee showed badge"
}
```

### Get Alert Rules

```http
GET /alerts/rules
```

**Response:**
```json
{
  "items": [
    {
      "id": "dd0e8400-e29b-41d4-a716-446655440008",
      "name": "VIP Alert",
      "description": "Alert when VIP is detected",
      "watchlist_id": 2,
      "severity": "high",
      "is_active": true,
      "created_at": "2024-01-10T08:00:00Z"
    }
  ]
}
```

### Create Alert Rule

```http
POST /alerts/rules
Content-Type: application/json

{
  "name": "After Hours Alert",
  "description": "Alert for any detection after business hours",
  "watchlist_id": null,
  "severity": "medium",
  "time_restrictions": {
    "start_time": "18:00",
    "end_time": "08:00",
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
  },
  "is_active": true
}
```

---

## 6. Analytics API

### Get Dashboard Stats

```http
GET /analytics/dashboard
```

**Response:**
```json
{
  "period": {
    "from": "2024-01-20T00:00:00Z",
    "to": "2024-01-20T23:59:59Z"
  },
  "summary": {
    "total_detections": 15420,
    "total_recognitions": 8750,
    "unique_subjects": 342,
    "total_alerts": 45,
    "unacknowledged_alerts": 12
  },
  "cameras": {
    "total": 50,
    "active": 48,
    "inactive": 2
  },
  "subjects": {
    "total": 1250,
    "watchlists": {
      "1": 800,
      "2": 50,
      "3": 400
    }
  },
  "hourly_activity": [
    {"hour": 0, "detections": 120, "recognitions": 80},
    {"hour": 1, "detections": 85, "recognitions": 60},
    ...
  ]
}
```

### Get Detection Trends

```http
GET /analytics/trends?from=2024-01-01&to=2024-01-20&group_by=day
```

**Response:**
```json
{
  "period": {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-20T23:59:59Z"
  },
  "group_by": "day",
  "data": [
    {
      "date": "2024-01-01",
      "detections": 1200,
      "recognitions": 800,
      "unique_subjects": 150
    },
    {
      "date": "2024-01-02",
      "detections": 1350,
      "recognitions": 900,
      "unique_subjects": 165
    }
  ]
}
```

### Get Camera Analytics

```http
GET /analytics/cameras?from=2024-01-01&to=2024-01-20
```

**Response:**
```json
{
  "cameras": [
    {
      "camera_id": "550e8400-e29b-41d4-a716-446655440000",
      "camera_name": "Main Entrance Camera",
      "detections": 5420,
      "recognitions": 3200,
      "unique_subjects": 280,
      "uptime_percentage": 99.5
    }
  ]
}
```

### Get Subject Analytics

```http
GET /analytics/subjects/{subject_id}?from=2024-01-01&to=2024-01-20
```

**Response:**
```json
{
  "subject_id": "770e8400-e29b-41d4-a716-446655440002",
  "subject_name": "John Smith",
  "period": {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-20T23:59:59Z"
  },
  "total_sightings": 45,
  "unique_cameras": 5,
  "first_seen": "2024-01-01T08:30:00Z",
  "last_seen": "2024-01-20T17:45:00Z",
  "average_confidence": 0.89,
  "sightings_by_camera": [
    {
      "camera_id": "550e8400-...",
      "camera_name": "Main Entrance",
      "count": 20
    }
  ],
  "sightings_by_hour": [
    {"hour": 8, "count": 15},
    {"hour": 9, "count": 12},
    ...
  ]
}
```

### Generate Report

```http
POST /analytics/reports
Content-Type: application/json

{
  "report_type": "activity_summary",
  "from": "2024-01-01T00:00:00Z",
  "to": "2024-01-20T23:59:59Z",
  "camera_ids": ["550e8400-..."],
  "format": "pdf",
  "email_to": ["admin@example.com"]
}
```

---

## 7. Users API

### List Users

```http
GET /users?page=1&page_size=20&role=operator&is_active=true
```

**Response:**
```json
{
  "items": [
    {
      "id": "ee0e8400-e29b-41d4-a716-446655440009",
      "username": "operator1",
      "email": "operator1@example.com",
      "full_name": "Operator One",
      "role": "operator",
      "is_active": true,
      "last_login_at": "2024-01-20T10:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20,
  "pages": 2
}
```

### Get User Details

```http
GET /users/{user_id}
```

### Create User

```http
POST /users
Content-Type: application/json

{
  "username": "newoperator",
  "email": "newoperator@example.com",
  "full_name": "New Operator",
  "password": "SecurePass123!",
  "role": "operator",
  "permissions": ["cameras:read", "subjects:read", "alerts:read"]
}
```

### Update User

```http
PUT /users/{user_id}
Content-Type: application/json

{
  "full_name": "Updated Name",
  "is_active": false
}
```

### Delete User

```http
DELETE /users/{user_id}
```

### Change Password

```http
POST /users/{user_id}/change-password
Content-Type: application/json

{
  "current_password": "OldPass123!",
  "new_password": "NewPass123!"
}
```

### Get Current User

```http
GET /users/me
```

---

## 8. WebSocket API

### Connection

```javascript
const ws = new WebSocket('wss://api.surveillance.local/v1/ws');

ws.onopen = () => {
  // Authenticate
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(message);
};
```

### Subscribe to Topics

```javascript
// Subscribe to detections
ws.send(JSON.stringify({
  type: 'subscribe',
  topic: 'detections',
  filters: {
    camera_ids: ['550e8400-...'],
    confidence_min: 0.7
  }
}));

// Subscribe to alerts
ws.send(JSON.stringify({
  type: 'subscribe',
  topic: 'alerts'
}));

// Subscribe to camera status
ws.send(JSON.stringify({
  type: 'subscribe',
  topic: 'camera_status'
}));
```

### Message Types

**Detection Event:**
```json
{
  "type": "detection",
  "data": {
    "sighting_id": "aa0e8400-e29b-41d4-a716-446655440005",
    "camera_id": "550e8400-e29b-41d4-a716-446655440000",
    "camera_name": "Main Entrance Camera",
    "confidence": 0.92,
    "bounding_box": {"x": 450, "y": 200, "width": 120, "height": 150},
    "timestamp": "2024-01-20T14:25:30Z"
  }
}
```

**Recognition Event:**
```json
{
  "type": "recognition",
  "data": {
    "sighting_id": "aa0e8400-e29b-41d4-a716-446655440005",
    "subject_id": "770e8400-e29b-41d4-a716-446655440002",
    "subject_name": "John Smith",
    "confidence": 0.92,
    "watchlist_name": "Employees",
    "timestamp": "2024-01-20T14:25:31Z"
  }
}
```

**Alert Event:**
```json
{
  "type": "alert",
  "data": {
    "alert_id": "cc0e8400-e29b-41d4-a716-446655440007",
    "severity": "high",
    "message": "Banned individual detected",
    "subject_name": "Unknown Person",
    "camera_name": "Main Entrance",
    "image_url": "...",
    "timestamp": "2024-01-20T14:25:31Z"
  }
}
```

**Camera Status:**
```json
{
  "type": "camera_status",
  "data": {
    "camera_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "error",
    "error_message": "Connection timeout",
    "timestamp": "2024-01-20T14:30:00Z"
  }
}
```

---

## 9. Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 422 | Unprocessable | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

**Error Response Format:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

---

## 10. Rate Limiting

Rate limits are applied per API key/user:

| Endpoint | Limit | Window |
|----------|-------|--------|
| Authentication | 5 | per minute |
| All endpoints | 1000 | per minute |
| Sightings list | 100 | per minute |
| Search by face | 30 | per minute |
| Export | 5 | per hour |

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642681200
```

---

## SDK Examples

### Python

```python
import requests

class SurveillanceAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def list_cameras(self, page=1, page_size=20):
        response = requests.get(
            f'{self.base_url}/cameras',
            headers=self.headers,
            params={'page': page, 'page_size': page_size}
        )
        return response.json()
    
    def search_by_face(self, image_path, threshold=0.7):
        with open(image_path, 'rb') as f:
            response = requests.post(
                f'{self.base_url}/subjects/search',
                headers={'Authorization': self.headers['Authorization']},
                files={'image': f},
                data={'threshold': threshold}
            )
        return response.json()

# Usage
api = SurveillanceAPI('https://api.surveillance.local/v1', 'your_token')
cameras = api.list_cameras()
```

### JavaScript

```javascript
class SurveillanceAPI {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  async listCameras(page = 1, pageSize = 20) {
    const response = await fetch(
      `${this.baseUrl}/cameras?page=${page}&page_size=${pageSize}`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.json();
  }

  async searchByFace(imageFile, threshold = 0.7) {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('threshold', threshold);

    const response = await fetch(
      `${this.baseUrl}/subjects/search`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`
        },
        body: formData
      }
    );
    return response.json();
  }
}

// Usage
const api = new SurveillanceAPI('https://api.surveillance.local/v1', 'your_token');
const cameras = await api.listCameras();
```
