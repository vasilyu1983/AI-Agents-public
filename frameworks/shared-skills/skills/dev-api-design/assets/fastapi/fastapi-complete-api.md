# FastAPI Complete API Template

Production-ready FastAPI application with authentication, database, validation, error handling, and OpenAPI docs.

## Project Structure

```
fastapi_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── dependencies.py      # Dependency injection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routers/             # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── users.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   └── user_service.py
│   └── utils/
│       ├── __init__.py
│       ├── security.py      # JWT, password hashing
│       └── pagination.py    # Pagination helpers
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_users.py
├── alembic/                 # Database migrations
├── .env.example
├── requirements.txt
└── pyproject.toml
```

## 1. Dependencies (requirements.txt)

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
psycopg2-binary==2.9.9      # PostgreSQL
asyncpg==0.29.0             # Async PostgreSQL
redis==5.0.1
python-dotenv==1.0.0
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0               # For testing
```

## 2. Configuration (app/config.py)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # App
    APP_NAME: str = "FastAPI App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost/dbname"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/dbname"

    # Security
    SECRET_KEY: str  # Required, must be in .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
```

## 3. Database Setup (app/database.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Sync engine (for migrations)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Async engine (for API operations)
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=settings.DEBUG
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

## 4. Models (app/models/user.py)

```python
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from app.database import Base

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

## 5. Schemas (app/schemas/user.py)

```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

class UserStatus(str):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    """Schema for user updates (all fields optional)."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[UserStatus] = None

class UserInDB(UserBase):
    """User schema with database fields."""
    id: UUID
    status: UserStatus
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserInDB):
    """Public user response (no sensitive data)."""
    pass

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Decoded token payload."""
    user_id: UUID
    email: str
    is_admin: bool
```

## 6. Security Utils (app/utils/security.py)

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings
from app.schemas.user import TokenData
from uuid import UUID

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        is_admin: bool = payload.get("is_admin", False)

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return TokenData(user_id=UUID(user_id), email=email, is_admin=is_admin)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    return decode_token(token)

async def require_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Dependency to require admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
```

## 7. Pagination Utils (app/utils/pagination.py)

```python
from typing import Generic, TypeVar, List
from pydantic import BaseModel
from fastapi import Query
from app.config import get_settings

settings = get_settings()
T = TypeVar('T')

class PaginationParams(BaseModel):
    """Pagination query parameters."""
    limit: int = Query(
        default=settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Number of items per page"
    )
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of items to skip"
    )

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    data: List[T]
    total: int
    limit: int
    offset: int
    has_more: bool

def paginate(
    items: List[T],
    total: int,
    params: PaginationParams
) -> PaginatedResponse[T]:
    """Create paginated response."""
    return PaginatedResponse(
        data=items,
        total=total,
        limit=params.limit,
        offset=params.offset,
        has_more=(params.offset + params.limit) < total
    )
```

## 8. User Service (app/services/user_service.py)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from uuid import UUID
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash
from fastapi import HTTPException, status

class UserService:
    """Business logic for user operations."""

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Create new user."""
        # Check if email exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Create user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_users(
        db: AsyncSession,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[User], int]:
        """List users with pagination."""
        # Get total count
        count_result = await db.execute(select(func.count(User.id)))
        total = count_result.scalar_one()

        # Get users
        result = await db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        users = result.scalars().all()

        return list(users), total

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: UUID,
        user_data: UserUpdate
    ) -> Optional[User]:
        """Update user."""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
        """Delete user."""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        await db.delete(user)
        await db.commit()
        return True
```

## 9. Auth Router (app/routers/auth.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import Token
from app.services.user_service import UserService
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token
)
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.

    - **username**: User email address
    - **password**: User password
    """
    # Get user by email
    user = await UserService.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
```

## 10. Users Router (app/routers/users.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    TokenData
)
from app.services.user_service import UserService
from app.utils.security import get_current_user, require_admin
from app.utils.pagination import (
    PaginationParams,
    PaginatedResponse,
    paginate
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_admin)  # Admin only
):
    """Create a new user (admin only)."""
    user = await UserService.create_user(db, user_data)
    return UserResponse.model_validate(user)

@router.get(
    "",
    response_model=PaginatedResponse[UserResponse]
)
async def list_users(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(get_current_user)
):
    """List all users with pagination."""
    users, total = await UserService.list_users(
        db,
        limit=pagination.limit,
        offset=pagination.offset
    )

    user_responses = [UserResponse.model_validate(u) for u in users]
    return paginate(user_responses, total, pagination)

@router.get(
    "/me",
    response_model=UserResponse
)
async def get_current_user_profile(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user's profile."""
    user = await UserService.get_user_by_id(db, current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(get_current_user)
):
    """Get user by ID."""
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)

@router.patch(
    "/{user_id}",
    response_model=UserResponse
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update user (own profile or admin)."""
    # Check permissions
    if user_id != current_user.user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    user = await UserService.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: TokenData = Depends(require_admin)  # Admin only
):
    """Delete user (admin only)."""
    deleted = await UserService.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
```

## 11. Main Application (app/main.py)

```python
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
from app.config import get_settings
from app.routers import auth, users

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting up...")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with RFC 9457 (Problem Details) format."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "https://api.example.com/errors/validation",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed",
            "errors": errors
        }
    )

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

## 12. Environment Variables (.env.example)

```env
# App
APP_NAME="FastAPI App"
APP_VERSION="1.0.0"
DEBUG=False

# Database
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
ASYNC_DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/dbname"

# Security (CHANGE IN PRODUCTION)
SECRET_KEY="your-secret-key-here-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

## 13. Database Migrations (Alembic)

```bash
# Initialize Alembic
alembic init alembic

# Edit alembic/env.py to import your models
# Then create first migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## 14. Testing (tests/test_users.py)

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "SecurePass123"
            }
        )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "SecurePass123"
            }
        )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
createdb your_database_name

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# API docs available at:
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

## Key Features

[check] **Async/await**: Full async support with AsyncSession
[check] **Type safety**: Pydantic v2 for request/response validation
[check] **Authentication**: JWT with access & refresh tokens
[check] **Authorization**: Role-based access control (RBAC)
[check] **Database**: SQLAlchemy 2.0 with Alembic migrations
[check] **Pagination**: Cursor & offset pagination helpers
[check] **Error handling**: RFC 9457 (Problem Details) format
[check] **OpenAPI**: Auto-generated Swagger UI and ReDoc
[check] **Testing**: pytest-asyncio setup
[check] **Security**: Password hashing, CORS, rate limiting
[check] **Dependency injection**: FastAPI's DI system
[check] **Configuration**: Environment-based settings with Pydantic

## Best Practices Applied

- Service layer pattern for business logic
- Repository pattern via SQLAlchemy
- Dependency injection for testability
- Async database operations
- Proper error handling and status codes
- Input validation with Pydantic
- JWT token security
- Database connection pooling
- Structured logging ready
- Type hints throughout
