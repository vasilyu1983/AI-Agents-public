# Testing Utilities

Centralized patterns for fixtures, factories, mocks, and test helpers.

**Updated**: December 2025
**Node.js**: 24 LTS | **Python**: 3.14+ | **TypeScript**: 5.7+

---

## File Structure

```text
src/
└── test/
    ├── factories/           # Data factories
    │   ├── user.factory.ts
    │   └── order.factory.ts
    ├── fixtures/            # Static test data
    │   └── users.json
    ├── mocks/               # Service mocks
    │   └── api.mock.ts
    └── helpers/             # Test utilities
        └── setup.ts
```

---

## TypeScript: Vitest (Recommended)

### Dependencies

```bash
npm install -D vitest@^3 @faker-js/faker@^9 msw@^2
```

### Factory Pattern (`src/test/factories/user.factory.ts`)

```typescript
import { faker } from '@faker-js/faker';

// ============================================
// BASE FACTORY HELPER
// ============================================

type Factory<T> = {
  build: (overrides?: Partial<T>) => T;
  buildMany: (count: number, overrides?: Partial<T>) => T[];
  buildWithTraits: (...traits: Array<keyof typeof userTraits>) => UserFactory;
};

// ============================================
// USER FACTORY
// ============================================

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin' | 'moderator';
  createdAt: Date;
  updatedAt: Date;
  emailVerified: boolean;
  metadata?: Record<string, unknown>;
}

const userDefaults = (): User => ({
  id: faker.string.uuid(),
  email: faker.internet.email(),
  name: faker.person.fullName(),
  role: 'user',
  createdAt: faker.date.past(),
  updatedAt: new Date(),
  emailVerified: true,
});

// Traits for common variations
const userTraits = {
  admin: { role: 'admin' as const },
  moderator: { role: 'moderator' as const },
  unverified: { emailVerified: false },
  recentlyCreated: { createdAt: new Date() },
} as const;

class UserFactory implements Factory<User> {
  private traits: Partial<User>[] = [];

  build(overrides: Partial<User> = {}): User {
    return {
      ...userDefaults(),
      ...Object.assign({}, ...this.traits),
      ...overrides,
    };
  }

  buildMany(count: number, overrides: Partial<User> = {}): User[] {
    return Array.from({ length: count }, () => this.build(overrides));
  }

  buildWithTraits(...traitNames: Array<keyof typeof userTraits>): UserFactory {
    const factory = new UserFactory();
    factory.traits = traitNames.map((name) => userTraits[name]);
    return factory;
  }

  // Convenience static methods
  static admin(overrides: Partial<User> = {}): User {
    return new UserFactory().buildWithTraits('admin').build(overrides);
  }

  static unverified(overrides: Partial<User> = {}): User {
    return new UserFactory().buildWithTraits('unverified').build(overrides);
  }
}

export const userFactory = new UserFactory();
```

### Database Fixtures (`src/test/fixtures/database.ts`)

```typescript
import { PrismaClient } from '@prisma/client';
import { userFactory } from '../factories/user.factory';

const prisma = new PrismaClient();

// ============================================
// FIXTURE HELPERS
// ============================================

export const fixtures = {
  // Create user in database
  async createUser(overrides: Partial<User> = {}) {
    const data = userFactory.build(overrides);
    return prisma.user.create({ data });
  },

  // Create many users
  async createUsers(count: number, overrides: Partial<User> = {}) {
    const users = userFactory.buildMany(count, overrides);
    return prisma.user.createMany({ data: users });
  },

  // Seed standard test data
  async seed() {
    await this.createUser({ email: 'admin@test.com', role: 'admin' });
    await this.createUser({ email: 'user@test.com', role: 'user' });
  },

  // Clean database between tests
  async clean() {
    const tables = ['User', 'Order', 'Product'];
    for (const table of tables) {
      await prisma.$executeRawUnsafe(`TRUNCATE TABLE "${table}" CASCADE`);
    }
  },

  // Reset sequences
  async resetSequences() {
    await prisma.$executeRaw`ALTER SEQUENCE "User_id_seq" RESTART WITH 1`;
  },
};
```

### API Mocks with MSW (`src/test/mocks/api.mock.ts`)

```typescript
import { http, HttpResponse, delay } from 'msw';
import { setupServer } from 'msw/node';
import { userFactory } from '../factories/user.factory';

// ============================================
// MSW v2 HANDLERS
// ============================================

export const handlers = [
  // GET /api/users
  http.get('/api/users', async () => {
    await delay(100); // Simulate network
    return HttpResponse.json(userFactory.buildMany(10));
  }),

  // GET /api/users/:id
  http.get('/api/users/:id', ({ params }) => {
    const user = userFactory.build({ id: params.id as string });
    return HttpResponse.json(user);
  }),

  // POST /api/users
  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    const user = userFactory.build(body as Partial<User>);
    return HttpResponse.json(user, { status: 201 });
  }),

  // Error scenarios
  http.get('/api/users/not-found', () => {
    return HttpResponse.json(
      { error: 'User not found' },
      { status: 404 }
    );
  }),

  http.get('/api/users/error', () => {
    return HttpResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }),
];

// Setup server
export const server = setupServer(...handlers);

// Helper to add one-time handlers
export const mockOnce = {
  success: (path: string, data: unknown) => {
    server.use(
      http.get(path, () => HttpResponse.json(data), { once: true })
    );
  },
  error: (path: string, status: number, message: string) => {
    server.use(
      http.get(path, () => HttpResponse.json({ error: message }, { status }), { once: true })
    );
  },
};
```

### Test Setup (`src/test/helpers/setup.ts`)

```typescript
import { beforeAll, afterAll, afterEach, vi } from 'vitest';
import { server } from '../mocks/api.mock';
import { fixtures } from '../fixtures/database';

// ============================================
// GLOBAL TEST SETUP
// ============================================

beforeAll(async () => {
  // Start MSW server
  server.listen({ onUnhandledRequest: 'error' });

  // Seed database
  await fixtures.seed();
});

afterEach(async () => {
  // Reset MSW handlers
  server.resetHandlers();

  // Clear mocks
  vi.clearAllMocks();

  // Clean database (optional - use transactions instead for speed)
  // await fixtures.clean();
});

afterAll(async () => {
  server.close();
});

// ============================================
// TEST HELPERS
// ============================================

// Wait for async operations
export const waitFor = (ms: number) => new Promise((r) => setTimeout(r, ms));

// Create authenticated test context
export const withAuth = (userId: string) => ({
  headers: { Authorization: `Bearer test-token-${userId}` },
});

// Snapshot date helper (deterministic dates)
export const freezeDate = (date: Date) => {
  vi.useFakeTimers();
  vi.setSystemTime(date);
  return () => vi.useRealTimers();
};
```

### Example Test (`src/test/user.service.test.ts`)

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { userFactory } from './factories/user.factory';
import { mockOnce } from './mocks/api.mock';
import { fixtures } from './fixtures/database';
import { UserService } from '../services/user.service';

describe('UserService', () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService();
  });

  describe('getUser', () => {
    it('returns user by id', async () => {
      const expected = userFactory.build({ id: '123' });
      mockOnce.success('/api/users/123', expected);

      const user = await service.getUser('123');

      expect(user).toEqual(expected);
    });

    it('throws on not found', async () => {
      mockOnce.error('/api/users/999', 404, 'User not found');

      await expect(service.getUser('999')).rejects.toThrow('User not found');
    });
  });

  describe('createUser', () => {
    it('creates user with valid data', async () => {
      const input = { email: 'new@test.com', name: 'New User' };

      const user = await service.createUser(input);

      expect(user.email).toBe(input.email);
      expect(user.id).toBeDefined();
    });

    it('creates admin user with trait', async () => {
      const admin = userFactory.buildWithTraits('admin').build();

      expect(admin.role).toBe('admin');
    });
  });

  describe('with database', () => {
    it('persists user to database', async () => {
      const user = await fixtures.createUser({ email: 'db@test.com' });

      const found = await service.getUser(user.id);

      expect(found.email).toBe('db@test.com');
    });
  });
});
```

---

## Python: pytest + Factory Boy

### Dependencies

```bash
pip install pytest>=8.3 pytest-asyncio>=0.24 factory-boy>=3.3 faker>=30 respx>=0.22 httpx>=0.28
```

### Factory Pattern (`tests/factories/user_factory.py`)

```python
from datetime import datetime, timezone
from typing import Any

import factory
from factory import fuzzy
from faker import Faker

from src.models.user import User

fake = Faker()


class UserFactory(factory.Factory):
    """Factory for creating User instances."""

    class Meta:
        model = User

    id = factory.LazyFunction(lambda: fake.uuid4())
    email = factory.LazyFunction(lambda: fake.email())
    name = factory.LazyFunction(lambda: fake.name())
    role = "user"
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    email_verified = True

    class Params:
        # Traits
        admin = factory.Trait(role="admin")
        moderator = factory.Trait(role="moderator")
        unverified = factory.Trait(email_verified=False)
        recently_created = factory.Trait(
            created_at=factory.LazyFunction(lambda: datetime.now(timezone.utc))
        )


# Convenience functions
def create_user(**kwargs: Any) -> User:
    return UserFactory(**kwargs)


def create_admin(**kwargs: Any) -> User:
    return UserFactory(admin=True, **kwargs)


def create_users(count: int, **kwargs: Any) -> list[User]:
    return UserFactory.create_batch(count, **kwargs)
```

### Database Fixtures (`tests/fixtures/database.py`)

```python
from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from tests.factories.user_factory import UserFactory


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session with automatic cleanup."""
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5432/test_db",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def seeded_db(db_session: AsyncSession) -> AsyncSession:
    """Database with standard test data."""
    admin = UserFactory(admin=True, email="admin@test.com")
    user = UserFactory(email="user@test.com")

    db_session.add_all([admin, user])
    await db_session.commit()

    return db_session
```

### API Mocks with respx (`tests/mocks/api_mock.py`)

```python
import httpx
import respx
from respx import MockRouter

from tests.factories.user_factory import UserFactory, create_users


def setup_user_mocks(mock: MockRouter) -> None:
    """Configure user API mocks."""

    # GET /api/users
    mock.get("/api/users").mock(
        return_value=httpx.Response(
            200,
            json=[u.model_dump() for u in create_users(10)],
        )
    )

    # GET /api/users/:id
    mock.get(url__regex=r"/api/users/[\w-]+").mock(
        side_effect=lambda request: httpx.Response(
            200,
            json=UserFactory(id=request.url.path.split("/")[-1]).model_dump(),
        )
    )

    # POST /api/users
    mock.post("/api/users").mock(
        return_value=httpx.Response(201, json=UserFactory().model_dump())
    )

    # Error scenarios
    mock.get("/api/users/not-found").mock(
        return_value=httpx.Response(404, json={"error": "User not found"})
    )


@respx.mock
async def test_with_mocks():
    """Example using respx mocks."""
    setup_user_mocks(respx)

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/api/users")
        assert response.status_code == 200
```

### Test Helpers (`tests/helpers.py`)

```python
import asyncio
from collections.abc import Callable
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any
from unittest.mock import patch


def wait_for(seconds: float) -> None:
    """Wait for async operations."""
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(seconds))


@contextmanager
def freeze_time(dt: datetime):
    """Freeze datetime for deterministic tests."""
    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = dt
        mock_dt.utcnow.return_value = dt.replace(tzinfo=None)
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield mock_dt


def with_auth(user_id: str) -> dict[str, str]:
    """Create authenticated headers."""
    return {"Authorization": f"Bearer test-token-{user_id}"}


class AsyncMock:
    """Helper for mocking async functions."""

    def __init__(self, return_value: Any = None):
        self.return_value = return_value
        self.call_count = 0
        self.calls: list[tuple[tuple, dict]] = []

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.call_count += 1
        self.calls.append((args, kwargs))
        return self.return_value
```

### Example Test (`tests/test_user_service.py`)

```python
import pytest
import respx
from httpx import Response

from src.services.user_service import UserService
from tests.factories.user_factory import UserFactory, create_admin
from tests.mocks.api_mock import setup_user_mocks


class TestUserService:
    @pytest.fixture
    def service(self) -> UserService:
        return UserService()

    @respx.mock
    async def test_get_user_returns_user(self, service: UserService):
        expected = UserFactory(id="123")
        respx.get("/api/users/123").mock(
            return_value=Response(200, json=expected.model_dump())
        )

        user = await service.get_user("123")

        assert user.id == "123"

    @respx.mock
    async def test_get_user_raises_on_not_found(self, service: UserService):
        respx.get("/api/users/999").mock(
            return_value=Response(404, json={"error": "User not found"})
        )

        with pytest.raises(Exception, match="User not found"):
            await service.get_user("999")

    def test_factory_creates_admin(self):
        admin = create_admin()

        assert admin.role == "admin"

    def test_factory_with_traits(self):
        user = UserFactory(unverified=True)

        assert user.email_verified is False

    async def test_with_database(self, seeded_db):
        """Test with real database."""
        from src.repositories.user_repo import UserRepository

        repo = UserRepository(seeded_db)
        user = await repo.get_by_email("admin@test.com")

        assert user is not None
        assert user.role == "admin"
```

---

## Testing Best Practices

### Factory Guidelines

```typescript
// DO: Use factories for test data
const user = userFactory.build({ email: 'test@example.com' });

// DO: Use traits for common variations
const admin = userFactory.buildWithTraits('admin').build();

// DON'T: Hardcode test data inline
const user = { id: '1', email: 'test@test.com', name: 'Test' }; // Brittle
```

### Mock Guidelines

```typescript
// DO: Mock at the boundary (HTTP, database)
server.use(http.get('/api/users', () => HttpResponse.json(users)));

// DO: Use one-time handlers for specific tests
mockOnce.error('/api/users/123', 404, 'Not found');

// DON'T: Mock internal implementation details
vi.mock('../utils/formatDate'); // Too coupled to implementation
```

### Database Test Guidelines

```typescript
// DO: Use transactions for isolation
beforeEach(async () => {
  await db.$transaction(async (tx) => {
    // Test runs in transaction
  });
});

// DO: Clean up after tests
afterEach(async () => {
  await fixtures.clean();
});

// DON'T: Share state between tests
let sharedUser; // Causes flaky tests
```

---

## Anti-Pattern: Hardcoded Test Data

```typescript
// BAD - Hardcoded, brittle, repetitive
describe('UserService', () => {
  it('creates user', async () => {
    const user = {
      id: '1',
      email: 'test@test.com',
      name: 'Test User',
      role: 'user',
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-01-01'),
      emailVerified: true,
    };
    // ...
  });
});

// GOOD - Factory with sensible defaults
describe('UserService', () => {
  it('creates user', async () => {
    const user = userFactory.build({ email: 'test@test.com' });
    // ...
  });
});
```

---

## References

- [Vitest Documentation](https://vitest.dev)
- [MSW v2 Documentation](https://mswjs.io)
- [pytest Documentation](https://docs.pytest.org)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io)
- [respx Documentation](https://lundberg.github.io/respx/)
