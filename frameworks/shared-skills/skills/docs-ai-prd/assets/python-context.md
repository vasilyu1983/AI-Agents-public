# Python CLAUDE.md Template

Copy and customize for Python projects.

---

```markdown
# [Project Name]

[One-line description of what this project does]

## Tech Stack

- **Python**: [3.11 / 3.12]
- **Framework**: [FastAPI / Django / Flask / None]
- **Database**: [PostgreSQL / MySQL / SQLite] via [SQLAlchemy / Django ORM / Tortoise]
- **Async**: [asyncio / sync]
- **Task Queue**: [Celery / RQ / Dramatiq / None]
- **Package Manager**: [uv / poetry / pip]
- **Testing**: [pytest] + [pytest-asyncio / pytest-django]

## Architecture

[2-3 sentences describing the overall design approach]

### Directory Structure

```
src/
├── api/                  # HTTP layer
│   ├── routes/           # Route definitions
│   ├── deps.py           # Dependency injection
│   └── middleware/       # Request middleware
├── services/             # Business logic
├── repositories/         # Data access layer
├── models/               # Database models
│   ├── entities/         # SQLAlchemy models
│   └── schemas/          # Pydantic schemas
├── core/                 # Core utilities
│   ├── config.py         # Settings
│   ├── security.py       # Auth utilities
│   └── exceptions.py     # Custom exceptions
├── utils/                # Shared utilities
└── tests/                # Test files
    ├── unit/
    ├── integration/
    └── conftest.py
```

### Key Patterns

- **Repository Pattern**: Data access in `repositories/`, services don't touch ORM directly
- **Dependency Injection**: FastAPI `Depends()` or manual DI
- **Pydantic Schemas**: Request/response validation via Pydantic v2
- **Async-first**: All I/O operations are async (FastAPI/SQLAlchemy async)

### Data Flow

```
Request → Middleware → Route → Service → Repository → Database
                                              ↓
Response ← Route ← Service ← Repository ←────┘
```

## Conventions

### Naming

| Type | Convention | Example |
|------|------------|---------|
| Files | snake_case | `user_service.py` |
| Classes | PascalCase | `UserService` |
| Functions | snake_case | `get_user_by_id` |
| Constants | SCREAMING_SNAKE | `MAX_RETRY_COUNT` |
| Private | Leading underscore | `_internal_method` |
| Type aliases | PascalCase | `UserId = int` |

### File Organization

- One class per file for services/repositories
- Models can be grouped by domain
- Tests mirror source structure in `tests/`
- `__init__.py` for explicit exports

### Type Hints

```python
# Always use type hints
def get_user(user_id: int) -> User | None:
    ...

# Use modern syntax (3.10+)
def process(items: list[str]) -> dict[str, int]:
    ...

# Pydantic for validation
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
```

### Imports

```python
# Order: stdlib → third-party → local (isort handles this)
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.user import User

if TYPE_CHECKING:
    from src.services.user import UserService
```

## Key Files

| Purpose | Location | Notes |
|---------|----------|-------|
| Entry point | `src/main.py` | FastAPI app creation |
| App factory | `src/app.py` | App configuration |
| Routes | `src/api/routes/__init__.py` | Router registration |
| Database | `src/core/database.py` | SQLAlchemy engine/session |
| Config | `src/core/config.py` | Pydantic Settings |
| Models | `src/models/` | SQLAlchemy + Pydantic |

## Configuration

### Environment Variables

```bash
# .env
ENV=development
DEBUG=true
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
LOG_LEVEL=DEBUG
```

### Settings Pattern (Pydantic)

```python
# src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "development"
    debug: bool = False
    database_url: str
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
```

## Commands

```bash
# Development
uv run uvicorn src.main:app --reload     # Start dev server
uv run python -m src.main                # Alternative start

# Database
uv run alembic upgrade head              # Run migrations
uv run alembic revision --autogenerate -m "description"  # Create migration
uv run python -m src.scripts.seed        # Seed database

# Testing
uv run pytest                            # Run all tests
uv run pytest -v --tb=short              # Verbose with short traceback
uv run pytest --cov=src                  # With coverage
uv run pytest -k "test_user"             # Run specific tests
uv run pytest -x                         # Stop on first failure

# Quality
uv run ruff check .                      # Linting
uv run ruff check . --fix                # Auto-fix
uv run ruff format .                     # Formatting
uv run mypy src/                         # Type checking
uv run pre-commit run --all-files        # All checks
```

## Important Context

### Technical Decisions

#### [Why FastAPI over Django]
**Context**: Building async API with strong typing
**Decision**: FastAPI for native async + Pydantic integration
**Trade-off**: Less batteries-included than Django, manual auth setup

#### [Why SQLAlchemy 2.0 async]
**Context**: Needed async database operations
**Decision**: SQLAlchemy 2.0 with asyncpg
**Trade-off**: More complex setup than sync, careful session management

### Known Gotchas

- **Async session management**: Always use `async with` for sessions, never share across requests
- **Circular imports**: Use `TYPE_CHECKING` guard for type hints
- **Alembic autogenerate**: Review generated migrations, doesn't catch everything
- **Pydantic v2**: Different from v1, use `model_dump()` not `dict()`
- **SQLAlchemy lazy loading**: Doesn't work in async, use `selectinload()`

### Historical Context

- [Any migrations, refactors, or legacy patterns to know about]

## Testing

### Test Structure

```python
# tests/unit/services/test_user_service.py
import pytest
from src.services.user import UserService

class TestUserService:
    @pytest.fixture
    def service(self, mock_repo):
        return UserService(repo=mock_repo)

    async def test_create_user_success(self, service):
        result = await service.create(email="test@example.com")
        assert result.email == "test@example.com"

    async def test_create_user_duplicate_raises(self, service):
        with pytest.raises(DuplicateEmailError):
            await service.create(email="existing@example.com")
```

### Fixtures

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db_session():
    # Test database session setup
    ...
```

## For AI Assistants

### When modifying this codebase:

- Follow existing patterns in similar files
- Add tests for new functionality (pytest)
- Use type hints everywhere
- Run `ruff check && mypy src/` before committing
- Create Alembic migration for model changes

### Patterns to follow:

- Async/await for all I/O operations
- Pydantic schemas for API input/output
- Repository pattern for database access
- Dependency injection via FastAPI `Depends()`

### Avoid:

- Sync database operations in async context
- Direct ORM queries in route handlers
- `print()` statements (use `logging`)
- Bare `except:` clauses
- Mutable default arguments
```

---

## Quick Start Commands

Run these to gather context for a new Python project:

```bash
# Basic structure
tree -L 3 -I '__pycache__|.venv|.git|.pytest_cache|*.egg-info'

# Dependencies
cat pyproject.toml | grep -A 50 "[tool.poetry.dependencies]" || cat requirements.txt

# Python version
cat .python-version 2>/dev/null || python --version

# Entry point
head -50 src/main.py || head -50 app.py

# Find all services
find . -name "*service*" -type f -name "*.py"

# Check for ORM
ls alembic/ 2>/dev/null && echo "SQLAlchemy/Alembic detected"
ls */migrations/ 2>/dev/null && echo "Django detected"
```
