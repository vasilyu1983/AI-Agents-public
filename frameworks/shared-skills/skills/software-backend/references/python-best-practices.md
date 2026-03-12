# Python Backend Best Practices

Comprehensive guide for building high-performance, type-safe backend services with Python and FastAPI.

## Contents

- [Type Hints & Type Safety](#type-hints--type-safety)
- [Async/Await Patterns](#asyncawait-patterns)
- [FastAPI Best Practices](#fastapi-best-practices)
- [SQLAlchemy 2.0 Patterns](#sqlalchemy-20-patterns)
- [Error Handling Patterns](#error-handling-patterns)
- [Testing Best Practices](#testing-best-practices)
- [Performance Optimization](#performance-optimization)
- [Security Best Practices](#security-best-practices)
- [Logging Best Practices](#logging-best-practices)
- [Common Pitfalls](#common-pitfalls)
- [Resources](#resources)

---

## Type Hints & Type Safety

### Basic Type Annotations

```python
from typing import Optional, List, Dict, Union, Any

def greet(name: str) -> str:
    return f"Hello, {name}!"

def process_items(items: List[int]) -> int:
    return sum(items)

def find_user(user_id: int) -> Optional[User]:
    # Returns User or None
    return db.query(User).filter(User.id == user_id).first()

# Generic types
from typing import TypeVar, Generic

T = TypeVar('T')

def get_first(items: List[T]) -> Optional[T]:
    return items[0] if items else None
```

### Pydantic Models

```python
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)

    @validator('password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime

    class Config:
        orm_mode = True  # Allow ORM model conversion

# Usage
try:
    user = UserCreate(
        email="test@example.com",
        password="Pass123",
        full_name="Test User"
    )
except ValidationError as e:
    print(e.json())
```

### MyPy Static Type Checking

```python
# mypy.ini or pyproject.toml
[mypy]
python_version = 3.11
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

# Run: mypy app/
```

---

## Async/Await Patterns

### Basic Async Functions

```python
import asyncio
from typing import List

async def fetch_user(user_id: int) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        return User(**response.json())

# Calling async functions
async def main():
    user = await fetch_user(1)
    print(user)

asyncio.run(main())
```

### Concurrent Operations

```python
import asyncio

# gather: Run multiple tasks concurrently
async def fetch_multiple_users(user_ids: List[int]) -> List[User]:
    tasks = [fetch_user(user_id) for user_id in user_ids]
    users = await asyncio.gather(*tasks)
    return users

# as_completed: Process results as they complete
async def fetch_with_progress(user_ids: List[int]) -> List[User]:
    tasks = [fetch_user(user_id) for user_id in user_ids]
    users = []

    for coro in asyncio.as_completed(tasks):
        user = await coro
        users.append(user)
        print(f"Fetched user {user.id}")

    return users
```

### Async Context Managers

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# Usage
async with get_db_connection() as conn:
    result = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
```

### Background Tasks

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Simulated email sending
    time.sleep(1)
    print(f"Email sent to {email}: {message}")

@app.post("/signup")
async def signup(
    user: UserCreate,
    background_tasks: BackgroundTasks
):
    # Create user immediately
    db_user = create_user(user)

    # Send email in background
    background_tasks.add_task(
        send_email,
        user.email,
        "Welcome to our service!"
    )

    return db_user
```

---

## FastAPI Best Practices

### Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

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

# Use in endpoints
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Authentication Dependency

```python
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception

    return user

# Use in protected endpoints
@app.get("/users/me")
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return current_user
```

### Request/Response Models

```python
from pydantic import BaseModel
from typing import Optional

class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int

@app.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(User).offset(pagination.skip).limit(pagination.limit)
    result = await db.execute(query)
    users = result.scalars().all()

    count_query = select(func.count()).select_from(User)
    total = await db.scalar(count_query)

    return {
        "items": users,
        "total": total,
        "skip": pagination.skip,
        "limit": pagination.limit
    }
```

### Error Handling

```python
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Usage
def get_user_or_404(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user
```

---

## SQLAlchemy 2.0 Patterns

### Async Engine & Session

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarativebase

Base = DeclarativeBase()

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

### Models

```python
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    posts: Mapped[List["Post"]] = relationship(back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="posts")
```

### Queries

```python
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

# Select queries
async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

# Eager loading relationships
async def get_user_with_posts(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.posts))
    )
    return result.scalar_one_or_none()

# Filtering and sorting
async def list_active_users(db: AsyncSession, skip: int, limit: int) -> List[User]:
    result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

# Update
async def update_user(db: AsyncSession, user_id: int, **kwargs):
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(**kwargs)
    )
    await db.commit()

# Delete
async def delete_user(db: AsyncSession, user_id: int):
    await db.execute(
        delete(User).where(User.id == user_id)
    )
    await db.commit()
```

### Transactions

```python
async def transfer_funds(
    db: AsyncSession,
    from_account_id: int,
    to_account_id: int,
    amount: float
) -> None:
    async with db.begin():  # Transaction context
        # Withdraw
        from_account = await db.get(Account, from_account_id)
        if not from_account or from_account.balance < amount:
            raise ValueError("Insufficient funds")

        from_account.balance -= amount

        # Deposit
        to_account = await db.get(Account, to_account_id)
        if not to_account:
            raise ValueError("Destination account not found")

        to_account.balance += amount

        # Commit happens automatically if no exception
```

---

## Error Handling Patterns

### Custom Exceptions

```python
class APIException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

class NotFoundException(APIException):
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail)

class UnauthorizedException(APIException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=401,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class ValidationException(APIException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)
```

### Try-Except Patterns

```python
from contextlib import suppress

# Specific exception handling
try:
    user = await get_user(user_id)
except NotFoundException:
    return create_default_user()
except DatabaseException as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database error")

# Multiple exceptions
try:
    result = risky_operation()
except (ValueError, TypeError) as e:
    logger.error(f"Invalid input: {e}")
    raise ValidationException(str(e))

# Suppress specific exceptions
with suppress(FileNotFoundError):
    os.remove("temp_file.txt")

# Finally for cleanup
try:
    file = open("data.txt")
    process(file)
finally:
    file.close()
```

---

## Testing Best Practices

### Pytest Fixtures

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.main import app
from app.core.database import Base

@pytest.fixture
async def db_engine():
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost/test_db",
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

### Unit Tests

```python
@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }

    user = await create_user(db_session, user_data)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.hashed_password != "password123"

@pytest.mark.asyncio
async def test_get_user_not_found(db_session: AsyncSession):
    with pytest.raises(NotFoundException):
        await get_user(db_session, 99999)
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
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
            "full_name": "Test User"
        }
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
```

### Parametrized Tests

```python
@pytest.mark.parametrize("email,password,should_pass", [
    ("valid@example.com", "Pass123!", True),
    ("invalid-email", "Pass123!", False),
    ("valid@example.com", "short", False),
    ("", "Pass123!", False),
])
async def test_user_validation(email, password, should_pass):
    try:
        user = UserCreate(
            email=email,
            password=password,
            full_name="Test"
        )
        assert should_pass
    except ValidationError:
        assert not should_pass
```

---

## Performance Optimization

### Database Query Optimization

```python
# Bad: N+1 query problem
users = await db.execute(select(User))
for user in users.scalars():
    posts = await db.execute(
        select(Post).where(Post.user_id == user.id)
    )  # N queries!

# Good: Eager loading
users = await db.execute(
    select(User).options(selectinload(User.posts))
)
for user in users.scalars():
    posts = user.posts  # Already loaded!

# Selective field loading
result = await db.execute(
    select(User.id, User.email).where(User.is_active == True)
)
```

### Caching with Redis

```python
import redis.asyncio as redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache(ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Try to get from cache
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )

            return result
        return wrapper
    return decorator

# Usage
@cache(ttl=600)
async def get_popular_posts(limit: int = 10) -> List[Post]:
    # Expensive query
    result = await db.execute(
        select(Post)
        .order_by(Post.views.desc())
        .limit(limit)
    )
    return result.scalars().all()
```

### Background Job Processing with Celery

```python
from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

@celery_app.task
def send_email_task(to: str, subject: str, body: str):
    # Send email
    send_email(to, subject, body)

@celery_app.task
def process_large_file(file_path: str):
    # Process file
    data = read_file(file_path)
    results = process_data(data)
    save_results(results)

# Usage in FastAPI
@app.post("/upload")
async def upload_file(file: UploadFile):
    file_path = save_uploaded_file(file)

    # Queue background task
    process_large_file.delay(file_path)

    return {"status": "processing", "file": file.filename}
```

---

## Security Best Practices

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### JWT Token Management

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "your-secret-key-min-32-characters"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

### Input Sanitization

```python
import bleach
from typing import Any

def sanitize_html(text: str) -> str:
    allowed_tags = ['p', 'br', 'strong', 'em', 'a']
    allowed_attributes = {'a': ['href', 'title']}

    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

class SanitizedStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError('string required')
        return sanitize_html(v)

# Usage in Pydantic
class CommentCreate(BaseModel):
    content: SanitizedStr
```

---

## Logging Best Practices

### Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)

# Configure logging
logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)

# Usage
logger.info("User created", extra={"user_id": user.id, "email": user.email})
logger.error("Database error", extra={"error": str(e)}, exc_info=True)
```

### Request Logging Middleware

```python
import time
from fastapi import Request
from uuid import uuid4

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid4())
    start_time = time.time()

    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
        }
    )

    response = await call_next(request)

    duration = time.time() - start_time

    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "duration": f"{duration:.3f}s",
        }
    )

    return response
```

---

## Common Pitfalls

### Mutable Default Arguments

```python
# Bad: Mutable default creates shared state
def append_item(item, items=[]):
    items.append(item)
    return items

# Good: Use None and create new list
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Not Closing Resources

```python
# Bad: File not closed on exception
file = open("data.txt")
process(file.read())
file.close()

# Good: Use context manager
with open("data.txt") as file:
    process(file.read())
# File automatically closed
```

### Forgetting await in Async Code

```python
# Bad: Returns coroutine, not result
async def get_user():
    user = fetch_user()  # Missing await!
    return user

# Good: Await async function
async def get_user():
    user = await fetch_user()
    return user
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Real Python Tutorials](https://realpython.com/)
- [Effective Python](https://effectivepython.com/)
