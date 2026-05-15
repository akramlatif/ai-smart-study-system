"""Integration tests for auth flow: register → login → protected route."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.main import app
from app.core.database import Base, get_db
from app.core.redis import get_redis, _MemoryCache


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def override_get_redis():
    return _MemoryCache()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_creates_user(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "securepassword123",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["name"] == "Test User"


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected(client):
    payload = {"email": "dup@example.com", "name": "User", "password": "pass123"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_with_valid_credentials(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "name": "Login User",
        "password": "mypassword",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "mypassword",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_with_wrong_password_rejected(client):
    await client.post("/api/v1/auth/register", json={
        "email": "wrong@example.com",
        "name": "User",
        "password": "correctpassword",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_requires_auth(client):
    response = await client.post("/api/v1/sessions")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_protected_route_accessible_with_token(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "auth@example.com",
        "name": "Auth User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    response = await client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert "session_id" in response.json()
