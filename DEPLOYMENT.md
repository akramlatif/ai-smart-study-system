# SmartStudy AI — Deployment Guide

## Local Development (SQLite, no Docker)

The fastest way to run the project locally.

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local: VITE_API_BASE_URL=http://localhost:8000/api/v1
npm run dev
```

App runs at `http://localhost:5173`.

---

## Production Deployment (Docker Compose)

Uses PostgreSQL + Redis + Nginx.

### 1. Create environment file

```bash
cp .env.example .env.prod
```

Edit `.env.prod`:
```env
POSTGRES_USER=smartstudy
POSTGRES_PASSWORD=your-strong-db-password
POSTGRES_DB=smartstudy
REDIS_PASSWORD=your-strong-redis-password
OPENAI_API_KEY=sk-your-openai-key
JWT_SECRET_KEY=your-very-long-random-secret-key
```

### 2. Build and start

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

### 3. Verify

```bash
docker-compose -f docker-compose.prod.yml ps
curl http://localhost/health
```

App runs at `http://localhost`.

### 4. View logs

```bash
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### 5. Stop

```bash
docker-compose -f docker-compose.prod.yml down
```

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | SQLite | SQLAlchemy async DB URL |
| `USE_MEMORY_CACHE` | No | `True` | Use in-memory cache instead of Redis |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis connection URL |
| `OPENAI_API_KEY` | Yes | — | OpenAI API key (sk-...) |
| `JWT_SECRET_KEY` | Yes | dev-key | JWT signing secret (change in production!) |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `JWT_EXPIRE_MINUTES` | No | `1440` | Token expiry (24 hours) |
| `UPLOAD_DIR` | No | `./uploads` | Directory for uploaded files |
| `MAX_PDF_SIZE_MB` | No | `10` | Max PDF upload size in MB |
| `MAX_TEXT_FILE_SIZE_MB` | No | `5` | Max text file upload size in MB |
| `CORS_ORIGINS` | No | `["http://localhost:5173"]` | Allowed CORS origins (JSON array) |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Frontend (`frontend/.env.local`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_API_BASE_URL` | Yes | — | Backend API base URL |

---

## Running Tests

### Backend

```bash
cd backend
pip install -r requirements-dev.txt

# Unit tests
pytest tests/unit/ -v

# Property-based tests (Hypothesis)
pytest tests/property/ -v

# Integration tests
pytest tests/integration/ -v

# All tests with coverage
pytest --cov=app --cov-report=html
```

### Frontend

```bash
cd frontend

# Component tests (Vitest)
npm run test

# E2E tests (Playwright — requires running servers)
npm run test:e2e
```

---

## HTTPS / TLS (Production)

For production, place a reverse proxy (Nginx or Caddy) in front of the Docker stack:

### Caddy (recommended — auto HTTPS)

```caddyfile
yourdomain.com {
    reverse_proxy localhost:80
}
```

### Nginx with Let's Encrypt

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    location / {
        proxy_pass http://localhost:80;
    }
}
```

---

## Scaling

- **Horizontal scaling**: Run multiple backend instances behind a load balancer. Ensure `USE_MEMORY_CACHE=False` and all instances share the same Redis.
- **Database**: Switch from SQLite to PostgreSQL for production (update `DATABASE_URL`).
- **File storage**: Replace local `UPLOAD_DIR` with S3-compatible storage for multi-instance deployments.
