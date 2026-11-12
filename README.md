# SmartStudy AI — AI-Powered Smart Study System

An adaptive AI tutor that transforms raw educational content into structured, personalized learning experiences. Paste notes, upload PDFs, or ask questions — get multi-level explanations, context-aware quizzes, and a conversational tutor.

## What's New — Dashboard & Progress v2

- **🔥 Study Streaks** — tracks your current and longest consecutive study-day streaks, plus total active days.
- **📈 Weekly Activity (real data)** — the dashboard chart is now powered by a live API (`/progress/weekly-activity`) instead of hardcoded numbers.
- **⚡ Expanded Quick Actions** — Deep Dive, Quick Quiz, My Library, and Spaced Review, all one click away.
- **🎨 Dashboard UI refresh** — gradient welcome banner with streak badge, skeleton loading states, dark-mode fixes across all panels, and a responsive layout that stacks on smaller screens.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS + Zustand |
| Backend | Python FastAPI + SQLAlchemy + Pydantic |
| Database | PostgreSQL + Redis |
| AI | OpenAI GPT-4o |
| PDF Parsing | PyMuPDF (fitz) |
| Testing | Hypothesis (PBT), Pytest, React Testing Library, Playwright |

## Project Structure

```
smartstudy/
├── frontend/          # React + TypeScript SPA
├── backend/           # Python FastAPI application
├── docker-compose.yml # PostgreSQL + Redis
└── README.md
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker + Docker Compose

### 1. Start Infrastructure

```bash
docker-compose up -d
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Fill in your OpenAI API key
alembic upgrade head      # Run database migrations
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

The app will be available at `http://localhost:5173`.

## API Endpoints (Progress)

| Endpoint | Description |
|---|---|
| `GET /progress/metrics` | Aggregate learning metrics (sessions, topics, accuracy, review queue) |
| `GET /progress/weekly-activity` | Sessions & quiz questions per day, last 7 days |
| `GET /progress/streak` | Current streak, longest streak, and active days |

## Environment Variables

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql://smartstudy:smartstudy@localhost:5432/smartstudy
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
UPLOAD_DIR=./uploads
MAX_PDF_SIZE_MB=10
MAX_TEXT_FILE_SIZE_MB=5
```

### Frontend (`frontend/.env.local`)
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Running Tests

### Backend
```bash
cd backend
pytest tests/unit/          # Unit tests
pytest tests/property/      # Property-based tests (Hypothesis)
pytest tests/integration/   # Integration tests
```

### Frontend
```bash
cd frontend
npm run test                # Component tests (Vitest + RTL)
npm run test:e2e            # E2E tests (Playwright)
```
