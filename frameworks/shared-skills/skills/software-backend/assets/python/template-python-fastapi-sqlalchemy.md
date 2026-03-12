# Backend Engineering - Python + FastAPI + SQLAlchemy Template

*Purpose: High-performance Python APIs with async support, ideal for ML/DS backends and data-intensive applications*

---

# When to Use

Use this template when building:
- Machine learning model serving APIs
- Data science backends with pandas/NumPy integration
- APIs requiring Python ecosystem libraries (scikit-learn, TensorFlow, PyTorch)
- Rapid prototyping with Python's rich ecosystem
- Services integrating with Jupyter notebooks or data pipelines

**Python/FastAPI Advantages:**
- **Async/await support**: High-performance async I/O (comparable to Node.js)
- **Automatic API docs**: OpenAPI/Swagger UI generated from type hints
- **Pydantic validation**: Runtime type checking with Python type hints
- **ML ecosystem**: Seamless integration with scikit-learn, TensorFlow, PyTorch, pandas
- **Fast development**: Python's expressiveness accelerates prototyping
- **Type safety**: MyPy static type checking (optional but recommended)

---

# TEMPLATE STARTS HERE

# 1. Project Overview

**Tech Stack:**
- [ ] Python 3.12+ (prefer latest stable; type hints + strict linting)
- [ ] FastAPI (current stable, async web framework)
- [ ] SQLAlchemy 2.0+ (async ORM)
- [ ] PostgreSQL 14+ (or org standard)
- [ ] Redis (async via redis-py `redis.asyncio`)
- [ ] Alembic (database migrations)
- [ ] Pydantic v2 (data validation)
- [ ] Pytest (testing)
- [ ] Celery (background jobs, optional)

**Project Name:** `{{project_name}}`

**Team:**
- Backend: {{team_size}} Python developers
- ML/DS: {{ml_team_size}} data scientists

---

# 2. Project Structure

```
project-root/
|-- app/
|   |-- __init__.py
|   |-- main.py                     # FastAPI application entry point
|   |-- api/
|   |   |-- __init__.py
|   |   |-- deps.py                 # Dependency injection
|   |   |-- routes/
|   |   |   |-- __init__.py
|   |   |   |-- auth.py
|   |   |   `-- users.py
|   |   `-- middleware/
|   |       |-- __init__.py
|   |       `-- auth.py
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py               # Configuration management
|   |   |-- security.py             # Password hashing, JWT
|   |   |-- database.py             # Database session management
|   |   `-- cache.py                # Redis client
|   |-- models/
|   |   |-- __init__.py
|   |   `-- user.py                 # SQLAlchemy models
|   |-- schemas/
|   |   |-- __init__.py
|   |   `-- user.py                 # Pydantic schemas
|   |-- services/
|   |   |-- __init__.py
|   |   `-- user.py                 # Business logic
|   |-- repositories/
|   |   |-- __init__.py
|   |   `-- user.py                 # Data access layer
|   `-- utils/
|       |-- __init__.py
|       `-- validators.py
|-- alembic/
|   |-- versions/
|   `-- env.py
|-- tests/
|   |-- __init__.py
|   |-- conftest.py
|   |-- unit/
|   `-- integration/
|-- requirements/
|   |-- base.txt                    # Core dependencies
|   |-- dev.txt                     # Development dependencies
|   `-- prod.txt                    # Production dependencies
|-- .env.example
|-- alembic.ini
|-- pyproject.toml
|-- Dockerfile
|-- docker-compose.yml
|-- Makefile
`-- README.md
```

**Key Principles:**
- Async-first architecture (async/await everywhere)
- Type hints on all functions (enable MyPy strict mode)
- Pydantic schemas for validation
- Repository pattern for data access
- Dependency injection for testability

---

## Centralization Guide

> **Important**: The code patterns in this template should be extracted to `app/core/`. **Do not duplicate** these utilities across modules.

| Utility | Extract To | Reference |
|---------|------------|-----------|
| Config (`Settings`, Pydantic) | `app/core/config.py` | [config-validation.md](../../../software-clean-code-standard/utilities/config-validation.md) |
| JWT (`create_access_token`, `decode_token`) | `app/core/security.py` | [auth-utilities.md](../../../software-clean-code-standard/utilities/auth-utilities.md) |
| Password (`hash_password`, `verify_password`) | `app/core/security.py` | [auth-utilities.md](../../../software-clean-code-standard/utilities/auth-utilities.md) |
| Errors (`AppError`, exception handlers) | `app/core/errors.py` | [error-handling.md](../../../software-clean-code-standard/utilities/error-handling.md) |
| Logging (structlog setup) | `app/core/logging.py` | [logging-utilities.md](../../../software-clean-code-standard/utilities/logging-utilities.md) |

**Pattern**: Create utilities once in `app/core/`, import everywhere via:

```python
from app.core.security import hash_password, create_access_token
from app.core.errors import AppError, NotFoundError
```

---

# 3. Environment Configuration

## .env.example

```env
# Server
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
APP_NAME=your-api
APP_VERSION=1.0.0
APP_DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=0
DATABASE_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=10

# JWT
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=43200  # 30 days

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://yourapp.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "PATCH", "DELETE"]
CORS_ALLOW_HEADERS=["*"]

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60  # seconds

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## pyproject.toml

```toml
[tool.poetry]
name = "your-api"
version = "1.0.0"
description = "FastAPI backend with SQLAlchemy"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.14"
fastapi = "^0.110.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.25"}
asyncpg = "^0.29.0"
alembic = "^1.13.0"
pydantic = {extras = ["email"], version = "^2.6.0"}
pydantic-settings = "^2.1.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.9"
redis = {extras = ["hiredis"], version = "^5.0.1"}
celery = {extras = ["redis"], version = "^5.3.4", optional = true}

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.3"
pytest-cov = "^4.1.0"
httpx = "^0.26.0"
mypy = "^1.8.0"
ruff = "^0.1.14"
black = "^24.1.1"

[tool.black]
line-length = 100
target-version = ['py314']

[tool.ruff]
line-length = 100
target-version = "py314"

[tool.mypy]
python_version = "3.14"
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## app/core/config.py

```python
from functools import lru_cache
from typing import Any

from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_NAME: str = "API"
    APP_VERSION: str = "1.0.0"
    APP_DEBUG: bool = False

    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: RedisDsn
    REDIS_MAX_CONNECTIONS: int = 10

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

---

# 4. Database Setup

## app/core/database.py

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    async with AsyncSessionLocal() as session:
        yield session
```

## app/models/user.py

```python
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
```

## alembic/versions/001_create_users.py

```python
"""create users table

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
```

---

# 5. Application Setup

## app/main.py

```python
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import auth, users
from app.core.config import settings


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    # Shutdown
    logger.info("Shutting down gracefully")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
    )
```

---

# 6. Authentication Implementation

## app/core/security.py

```python
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
```

## app/api/deps.py

```python
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

---

# 7. API Routes & Handlers

## app/schemas/user.py

```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
```

## app/api/routes/auth.py

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.repositories.user import UserRepository
from app.schemas.user import Token, UserCreate, UserResponse


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new user."""
    repo = UserRepository(db)

    # Check if user exists
    existing_user = await repo.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    hashed_password = get_password_hash(user_in.password)
    user = await repo.create(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
    )

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Login with email and password."""
    repo = UserRepository(db)

    user = await repo.get_by_email(form_data.username)  # username is email
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)
```

## app/api/routes/users.py

```python
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserUpdate


router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get current user."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update current user."""
    repo = UserRepository(db)
    updated_user = await repo.update(current_user.id, user_update)
    return updated_user
```

---

# 8. Repository Pattern / Data Access

## app/repositories/user.py

```python
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserUpdate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        is_active: bool = True,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=is_active,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if not user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False

        # Soft delete
        user.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()
        return True

    async def list(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.db.execute(
            select(User).where(User.deleted_at.is_(None)).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
```

---

# 9. Testing

## tests/conftest.py

```python
import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.main import app


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def override_get_db(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

## tests/unit/test_security.py

```python
from app.core.security import create_access_token, decode_token, get_password_hash, verify_password


def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_jwt_token():
    user_id = 123
    token = create_access_token(subject=user_id)

    assert token is not None
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
```

## tests/integration/test_auth.py

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    # Register user first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
```

---

# 10. Docker Setup

## Dockerfile

```dockerfile
# Build stage
FROM python:3.14-slim as builder

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Runtime stage
FROM python:3.14-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## docker-compose.yml

```yaml
version: '3.9'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/myapp
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./app:/app/app
    restart: unless-stopped

  postgres:
    image: postgres:18-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

## Makefile

```makefile
.PHONY: install run test migrate lint format

install:
	poetry install

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v --cov=app --cov-report=html

test-watch:
	pytest-watch

migrate-create:
	alembic revision --autogenerate -m "$(name)"

migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

lint:
	ruff check app/ tests/
	mypy app/

format:
	black app/ tests/
	ruff check --fix app/ tests/

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api
```

---

# 11. Production Checklist

## Security [OK]
- [ ] JWT secret is strong (min 32 chars) and stored securely
- [ ] HTTPS enforced with TLS 1.2+
- [ ] Rate limiting per endpoint
- [ ] CORS restricted to specific origins
- [ ] SQL injection prevention (SQLAlchemy parameterized queries)
- [ ] Password hashing with bcrypt (cost factor 12+)
- [ ] Input validation with Pydantic
- [ ] Security headers (use fastapi-security-headers)
- [ ] Dependency vulnerability scanning (`safety check`)
- [ ] Environment variables validated at startup

## Performance [OK]
- [ ] Database connection pooling configured
- [ ] Redis caching for read-heavy operations
- [ ] Async/await for all I/O operations
- [ ] Database indexes on foreign keys and query columns
- [ ] Response compression (GZipMiddleware)
- [ ] Pagination for list endpoints
- [ ] Load testing with Locust or k6
- [ ] Query optimization with explain analyze

## Observability [OK]
- [ ] Structured logging (JSON format)
- [ ] Request ID tracking
- [ ] Error tracking (Sentry integration)
- [ ] APM integration (New Relic, Datadog)
- [ ] Health check endpoint
- [ ] Metrics exposed (Prometheus format with prometheus-fastapi-instrumentator)
- [ ] OpenTelemetry tracing

## Deployment [OK]
- [ ] Multi-stage Docker build
- [ ] Container security scanning
- [ ] Database migrations automated
- [ ] Graceful shutdown
- [ ] Zero-downtime deployment
- [ ] CI/CD pipeline (GitHub Actions, GitLab CI)
- [ ] Blue-green or canary deployment

## Reliability [OK]
- [ ] Database backups automated
- [ ] Redis persistence configured
- [ ] Retry logic with tenacity
- [ ] Timeout configured for all operations
- [ ] Circuit breaker for external services
- [ ] Background job retry with Celery
- [ ] Dead letter queue for failed tasks

---

# 12. API Documentation

FastAPI automatically generates OpenAPI docs. Access at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

Customize with:

```python
app = FastAPI(
    title="Your API",
    description="API description with **markdown** support",
    version="1.0.0",
    openapi_tags=[
        {"name": "auth", "description": "Authentication endpoints"},
        {"name": "users", "description": "User management"},
    ],
)
```

---

# END

**Congratulations!** You now have a production-grade Python backend with FastAPI, SQLAlchemy, and PostgreSQL.

**Next Steps:**
1. Install dependencies with `poetry install` or `pip install -r requirements/base.txt`
2. Copy `.env.example` to `.env` and configure
3. Start services with `docker-compose up -d`
4. Run migrations with `make migrate-up`
5. Start development server with `make run`
6. Access API docs at `http://localhost:8000/docs`

**Python/FastAPI Best Practices:**
- **Type hints everywhere**: Enable MyPy strict mode for compile-time type checking
- **Async/await**: Use async for all I/O operations (database, Redis, HTTP)
- **Pydantic validation**: Runtime validation with automatic OpenAPI schema generation
- **Dependency injection**: Use FastAPI's `Depends()` for clean, testable code
- **Repository pattern**: Separate data access from business logic
- **Testing**: High test coverage with pytest-asyncio
- **ML integration**: Seamless with scikit-learn, TensorFlow, PyTorch, pandas, NumPy
- **Background jobs**: Use Celery for long-running tasks (model training, batch processing)
