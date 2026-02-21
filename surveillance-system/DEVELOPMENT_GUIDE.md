# Development Guide
## IPTV Facial Recognition Surveillance System

---

## Table of Contents

1. [Development Environment Setup](#1-development-environment-setup)
2. [Project Structure](#2-project-structure)
3. [Coding Standards](#3-coding-standards)
4. [Database Migrations](#4-database-migrations)
5. [Testing](#5-testing)
6. [Debugging](#6-debugging)
7. [Contributing](#7-contributing)

---

## 1. Development Environment Setup

### 1.1 Prerequisites

```bash
# Required software versions
Python 3.11+
Node.js 20+
Docker 24.0+
Docker Compose 2.20+
Git 2.40+
```

### 1.2 Clone Repository

```bash
git clone https://github.com/your-org/surveillance-system.git
cd surveillance-system
```

### 1.3 Backend Setup

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Setup pre-commit hooks
pre-commit install
```

### 1.4 Frontend Setup

```bash
cd frontend
npm install

# Or with pnpm (recommended)
pnpm install
```

### 1.5 Environment Configuration

```bash
# Copy example environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit with your local settings
nano backend/.env
nano frontend/.env.local
```

**Backend .env:**
```bash
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=DEBUG

POSTGRES_USER=surveillance
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=surveillance
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379

MINIO_ENDPOINT=localhost:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

JWT_SECRET_KEY=dev_secret_key_not_for_production
```

**Frontend .env.local:**
```bash
VITE_API_URL=http://localhost:8000/v1
VITE_WS_URL=ws://localhost:8000/v1/ws
```

### 1.6 Start Development Services

```bash
# Start infrastructure (postgres, redis, minio)
docker compose -f docker-compose.dev.yml up -d

# Run backend migrations
cd backend
alembic upgrade head

# Seed development data
python scripts/seed_dev_data.py

# Start backend (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start frontend
cd frontend
npm run dev
```

### 1.7 Verify Setup

```bash
# Check API
curl http://localhost:8000/v1/health

# Check frontend
open http://localhost:5173

# Check API docs
open http://localhost:8000/v1/docs
```

---

## 2. Project Structure

### 2.1 Backend Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py           # Alembic configuration
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── api/
│   │   └── v1/
│   │       ├── deps.py  # Dependencies
│   │       └── endpoints/
│   ├── core/            # Core modules
│   │   ├── config.py    # Settings
│   │   ├── security.py  # Auth utilities
│   │   ├── database.py  # DB connection
│   │   ├── redis.py     # Redis client
│   │   └── minio.py     # MinIO client
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── middleware/      # Custom middleware
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── scripts/             # Utility scripts
├── Dockerfile
├── requirements.txt
└── requirements-dev.txt
```

### 2.2 Frontend Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   │   ├── ui/         # shadcn/ui components
│   │   ├── layout/     # Layout components
│   │   ├── camera/     # Camera components
│   │   ├── subject/    # Subject components
│   │   ├── sighting/   # Sighting components
│   │   ├── alert/      # Alert components
│   │   └── analytics/  # Analytics components
│   ├── pages/          # Page components
│   ├── hooks/          # Custom React hooks
│   ├── contexts/       # React contexts
│   ├── lib/            # Utilities
│   │   ├── api.ts      # API client
│   │   └── utils.ts    # Helper functions
│   ├── types/          # TypeScript types
│   ├── App.tsx
│   └── main.tsx
├── public/
├── tests/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

---

## 3. Coding Standards

### 3.1 Python Standards

We follow PEP 8 with some modifications:

```python
# Line length: 100 characters max
# Use type hints everywhere
from typing import Optional, List, Dict, Any

def process_detection(
    camera_id: str,
    frame: np.ndarray,
    confidence_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Process frame and return detections.
    
    Args:
        camera_id: UUID of the camera
        frame: Input image as numpy array
        confidence_threshold: Minimum confidence for detection
        
    Returns:
        List of detection dictionaries with bbox and confidence
    """
    # Implementation
    pass

# Use async/await for I/O operations
async def fetch_camera(camera_id: str) -> Optional[Camera]:
    async with async_session() as session:
        result = await session.execute(
            select(Camera).where(Camera.id == camera_id)
        )
        return result.scalar_one_or_none()
```

**Linting:**
```bash
# Run all checks
make lint

# Individual tools
flake8 app tests
black app tests --check
isort app tests --check-only
mypy app
pylint app
```

### 3.2 TypeScript Standards

```typescript
// Use explicit types
interface Camera {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'error';
  config: CameraConfig;
}

// Use functional components
const CameraCard: React.FC<CameraCardProps> = ({ camera, onEdit }) => {
  const handleClick = useCallback(() => {
    onEdit(camera.id);
  }, [camera.id, onEdit]);

  return (
    <Card onClick={handleClick}>
      <CardHeader>{camera.name}</CardHeader>
      <CardContent>
        <StatusBadge status={camera.status} />
      </CardContent>
    </Card>
  );
};

// Custom hooks for data fetching
const useCamera = (id: string) => {
  return useQuery({
    queryKey: ['camera', id],
    queryFn: () => api.getCamera(id),
  });
};
```

**Linting:**
```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint:fix

# Type checking
npm run type-check
```

### 3.3 Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/camera-ptz-controls

# 2. Make changes and commit
# Follow conventional commits format:
git commit -m "feat(cameras): add PTZ control support

- Implement pan/tilt/zoom API endpoints
- Add PTZ controls to camera detail page
- Store PTZ presets in database"

# 3. Push branch
git push origin feature/camera-ptz-controls

# 4. Create pull request
# - Fill out PR template
# - Request review from team members
# - Ensure CI passes

# 5. After approval, squash merge
git checkout main
git pull origin main
git merge --squash feature/camera-ptz-controls
git commit -m "feat(cameras): add PTZ control support"
git push origin main
```

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance
```

---

## 4. Database Migrations

### 4.1 Creating Migrations

```bash
# Auto-generate migration from model changes
cd backend
alembic revision --autogenerate -m "add camera ptz fields"

# Review generated migration
nano alembic/versions/xxx_add_camera_ptz_fields.py

# Apply migration
alembic upgrade head

# Rollback (for testing)
alembic downgrade -1
```

### 4.2 Migration Best Practices

```python
"""add camera ptz fields

Revision ID: xxx
Revises: yyy
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'xxx'
down_revision = 'yyy'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns with defaults for existing data
    op.add_column(
        'cameras',
        sa.Column('ptz_enabled', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column(
        'cameras',
        sa.Column('ptz_config', postgresql.JSONB(), nullable=True)
    )
    
    # Create index for JSONB queries
    op.create_index(
        'ix_cameras_ptz_config',
        'cameras',
        ['ptz_config'],
        postgresql_using='gin'
    )


def downgrade():
    op.drop_index('ix_cameras_ptz_config')
    op.drop_column('cameras', 'ptz_config')
    op.drop_column('cameras', 'ptz_enabled')
```

### 4.3 Seeding Data

```python
# backend/scripts/seed_dev_data.py
import asyncio
from app.db.session import async_session
from app.models import Camera, Subject, Watchlist, User
from app.core.security import get_password_hash

async def seed():
    async with async_session() as session:
        # Create watchlists
        employees = Watchlist(name="Employees", color="#4CAF50")
        visitors = Watchlist(name="Visitors", color="#2196F3")
        banned = Watchlist(name="Banned", color="#F44336")
        session.add_all([employees, visitors, banned])
        await session.flush()
        
        # Create cameras
        cameras = [
            Camera(
                name="Main Entrance",
                location="Building A - Floor 1",
                stream_url="rtsp://demo-camera-1.local/stream",
                status="active",
                detection_enabled=True,
                recognition_enabled=True
            ),
            # ... more cameras
        ]
        session.add_all(cameras)
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            role="admin",
            is_active=True
        )
        session.add(admin)
        
        await session.commit()
        print("Development data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
```

---

## 5. Testing

### 5.1 Running Tests

```bash
# Backend tests
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_security.py

# Run with markers
pytest -m "not slow"

# Frontend tests
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### 5.2 Writing Tests

**Backend Unit Test:**
```python
# tests/unit/test_security.py
import pytest
from app.core.security import verify_password, get_password_hash, create_access_token


def test_password_hashing():
    password = "test_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_jwt_token_creation():
    user_id = "test-user-id"
    token = create_access_token({"sub": user_id})
    assert token is not None
    assert isinstance(token, str)
```

**Backend Integration Test:**
```python
# tests/integration/test_cameras.py
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_camera(client, auth_headers):
    response = await client.post(
        "/v1/cameras",
        json={
            "name": "Test Camera",
            "location": "Test Location",
            "stream_url": "rtsp://test.local/stream"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Camera"
    assert "id" in data
```

**Frontend Component Test:**
```typescript
// src/components/camera/CameraCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { CameraCard } from './CameraCard';

const mockCamera = {
  id: '1',
  name: 'Test Camera',
  status: 'active' as const,
  location: 'Test Location',
};

describe('CameraCard', () => {
  it('renders camera information', () => {
    render(<CameraCard camera={mockCamera} onEdit={jest.fn()} />);
    
    expect(screen.getByText('Test Camera')).toBeInTheDocument();
    expect(screen.getByText('Test Location')).toBeInTheDocument();
  });

  it('calls onEdit when clicked', () => {
    const onEdit = jest.fn();
    render(<CameraCard camera={mockCamera} onEdit={onEdit} />);
    
    fireEvent.click(screen.getByRole('button', { name: /edit/i }));
    expect(onEdit).toHaveBeenCalledWith('1');
  });
});
```

### 5.3 Test Coverage

```bash
# Generate coverage report (backend)
pytest --cov=app --cov-report=html --cov-report=term-missing

# Open HTML report
open htmlcov/index.html

# Coverage requirements
# - Unit tests: 80% minimum
# - Integration tests: 60% minimum
# - Critical paths: 90% minimum
```

---

## 6. Debugging

### 6.1 Backend Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()

# Or use built-in breakpoint()
breakpoint()

# VS Code launch.json configuration
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["app.main:app", "--reload"],
            "jinja": true,
            "justMyCode": false
        }
    ]
}
```

### 6.2 Frontend Debugging

```typescript
// Console logging
console.log('Camera data:', camera);
console.table(cameras);

// React DevTools
// Install browser extension
// Components tab for component tree
// Profiler tab for performance

// VS Code debugging
// launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Chrome Debug",
            "type": "chrome",
            "request": "launch",
            "url": "http://localhost:5173",
            "webRoot": "${workspaceFolder}/frontend/src"
        }
    ]
}
```

### 6.3 Database Debugging

```bash
# Connect to database
docker compose exec postgres psql -U surveillance -d surveillance

# Useful queries
\dt                    # List tables
\d cameras            # Describe table
\x auto               # Expanded output

# Query examples
SELECT * FROM cameras WHERE status = 'error';
SELECT camera_id, COUNT(*) FROM sightings 
GROUP BY camera_id ORDER BY count DESC;

# Enable query logging
SET log_statement = 'all';
```

### 6.4 Redis Debugging

```bash
# Connect to Redis
docker compose exec redis redis-cli

# Useful commands
MONITOR               # Watch all commands
KEYS *                # List all keys (careful in production!)
LRANGE camera:frames 0 10   # List stream entries
INFO                  # Server info
```

---

## 7. Contributing

### 7.1 Before You Start

1. Check existing issues and PRs
2. Create an issue for new features
3. Discuss major changes with maintainers
4. Follow the coding standards

### 7.2 Pull Request Process

1. **Create a branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation

3. **Run quality checks**
   ```bash
   # Backend
   make lint
   make test
   
   # Frontend
   npm run lint
   npm run test
   npm run build
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Fill out PR template**
   - Description of changes
   - Related issues
   - Testing performed
   - Screenshots (for UI changes)

### 7.3 Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No console.log statements (frontend)
- [ ] No print statements (backend)
- [ ] Error handling implemented
- [ ] Security considerations addressed

### 7.4 Release Process

```bash
# 1. Update version
# backend/app/__init__.py
# frontend/package.json

# 2. Update CHANGELOG.md

# 3. Create release branch
git checkout -b release/v1.2.0

# 4. Run full test suite
make test-all

# 5. Build and test Docker images
make build
make test-integration

# 6. Tag release
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# 7. Create GitHub release
# Upload release notes
# Attach binaries if needed

# 8. Deploy to staging
make deploy-staging

# 9. Deploy to production
make deploy-production
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [React Documentation](https://react.dev/)
- [TanStack Query](https://tanstack.com/query/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## Support

- GitHub Issues: https://github.com/your-org/surveillance-system/issues
- Discussions: https://github.com/your-org/surveillance-system/discussions
- Email: dev@surveillance.local
