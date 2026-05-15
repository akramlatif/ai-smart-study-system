from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.core.config import settings
from app.core.redis import close_redis
from app.core.rate_limit import RateLimitMiddleware
from app.routers import auth, sessions, analysis, quiz, documents, dashboard, learning_modes, tutor, progress


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start document cleanup background task
    from app.core.cleanup import run_cleanup_loop
    from app.core.database import get_db
    cleanup_task = asyncio.create_task(run_cleanup_loop(get_db, interval_seconds=3600))
    yield
    # Shutdown
    cleanup_task.cancel()
    await close_redis()


app = FastAPI(
    title="SmartStudy AI API",
    description="AI-Powered Smart Study System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(quiz.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(learning_modes.router, prefix="/api/v1")
app.include_router(tutor.router, prefix="/api/v1")
app.include_router(progress.router, prefix="/api/v1")
