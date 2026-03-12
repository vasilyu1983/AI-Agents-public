# Architecture Extraction Guide

How to identify and document system architecture from an existing codebase.

---

## Quick Extraction Process

```bash
# 1. Get directory structure
tree -L 3 -I 'node_modules|.git|dist|build|__pycache__|.venv' > structure.txt

# 2. Identify entry points
find . -name "main.*" -o -name "index.*" -o -name "app.*" -o -name "server.*" | head -20

# 3. Find configuration
find . -name "*.config.*" -o -name "config.*" -o -name ".env*" | grep -v node_modules

# 4. Check package.json/requirements.txt for dependencies
cat package.json 2>/dev/null | jq '.dependencies' || cat requirements.txt 2>/dev/null

# 5. Find architectural patterns in imports
grep -r "import.*from" --include="*.ts" --include="*.js" | head -50
```

---

## Component Discovery

### Identify Layers

Most applications follow layered architecture:

| Layer | Common Names | Purpose |
|-------|--------------|---------|
| **Presentation** | `api/`, `routes/`, `controllers/`, `handlers/`, `views/` | HTTP/UI handling |
| **Business Logic** | `services/`, `usecases/`, `domain/`, `core/` | Business rules |
| **Data Access** | `repositories/`, `models/`, `dal/`, `db/` | Database operations |
| **Infrastructure** | `infra/`, `adapters/`, `external/` | External services |
| **Shared** | `utils/`, `lib/`, `common/`, `shared/` | Cross-cutting concerns |

### Detect Patterns

Look for these indicators:

```bash
# Repository pattern
grep -r "Repository\|repo\." --include="*.ts" --include="*.py"

# Service layer
grep -r "Service\|service\." --include="*.ts" --include="*.py"

# Dependency injection
grep -r "inject\|@Injectable\|@Inject\|container\." --include="*.ts"

# Event-driven
grep -r "emit\|publish\|subscribe\|EventEmitter\|on\(" --include="*.ts" --include="*.py"
```

---

## Data Flow Mapping

### Trace a Request

Follow a typical request through the system:

1. **Entry point**: Where does the request arrive? (`routes.ts`, `app.py`)
2. **Validation**: Where is input validated? (`middleware/`, `validators/`)
3. **Business logic**: Which service handles it? (`services/`)
4. **Data access**: How does it reach the database? (`repositories/`, `models/`)
5. **Response**: How is the response formatted? (`transformers/`, `serializers/`)

### Document the Flow

```markdown
## Data Flow

1. Request → `src/api/routes.ts` (route matching)
2. → `src/middleware/auth.ts` (authentication)
3. → `src/middleware/validate.ts` (request validation)
4. → `src/api/handlers/user.ts` (handler)
5. → `src/services/UserService.ts` (business logic)
6. → `src/repositories/UserRepository.ts` (data access)
7. → Database
8. ← Response transformation
9. ← HTTP response
```

---

## Abstraction Identification

### Find Core Abstractions

```bash
# Find interfaces/abstract classes
grep -r "interface \|abstract class \|Protocol\|ABC" --include="*.ts" --include="*.py"

# Find type definitions
grep -r "type \|TypeAlias\|TypedDict" --include="*.ts" --include="*.py"

# Find base classes
grep -r "extends \|class.*Base\|class.*Abstract" --include="*.ts" --include="*.py"
```

### Document Key Abstractions

```markdown
## Key Abstractions

| Abstraction | Location | Purpose |
|-------------|----------|---------|
| `IUserRepository` | `src/interfaces/repositories.ts` | User data access contract |
| `BaseService` | `src/services/base.ts` | Shared service functionality |
| `ApiResponse<T>` | `src/types/api.ts` | Standard response wrapper |
```

---

## Dependency Analysis

### Analyze Import Patterns

```bash
# Most imported files (indicates core components)
grep -rh "from '\..*'" --include="*.ts" | sort | uniq -c | sort -rn | head -20

# External dependency usage
grep -rh "from '[^.]" --include="*.ts" | sort | uniq -c | sort -rn | head -20
```

### Map Dependencies

```markdown
## Component Dependencies

```
UserController
    └── UserService
            ├── UserRepository
            │       └── Database
            ├── EmailService
            │       └── SendGrid
            └── CacheService
                    └── Redis
```
```

---

## Architecture Documentation Template

```markdown
## Architecture Overview

[Project Name] follows a [layered/hexagonal/microservices] architecture.

### High-Level Structure

```
┌─────────────────────────────────────────┐
│              Presentation               │
│   (routes, controllers, middleware)     │
├─────────────────────────────────────────┤
│            Business Logic               │
│        (services, use cases)            │
├─────────────────────────────────────────┤
│              Data Access                │
│     (repositories, models, ORM)         │
├─────────────────────────────────────────┤
│            Infrastructure               │
│   (database, cache, external APIs)      │
└─────────────────────────────────────────┘
```

### Key Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| API Layer | `src/api/` | HTTP handling, routing, validation |
| Services | `src/services/` | Business logic, orchestration |
| Repositories | `src/repositories/` | Data access, persistence |
| Models | `src/models/` | Data structures, ORM entities |

### Data Flow

1. HTTP Request → Router → Middleware → Controller
2. Controller → Service (business logic)
3. Service → Repository (data access)
4. Repository → Database
5. Response flows back through the same layers

### External Integrations

- **Database**: PostgreSQL via Prisma ORM
- **Cache**: Redis for session storage
- **Email**: SendGrid for transactional emails
- **Auth**: Auth0 for authentication
```

---

## Common Architecture Patterns

### Monolith

```
src/
├── api/           # All routes
├── services/      # All business logic
├── models/        # All data models
└── utils/         # Shared utilities
```

### Domain-Driven

```
src/
├── user/
│   ├── api/
│   ├── service/
│   └── repository/
├── order/
│   ├── api/
│   ├── service/
│   └── repository/
└── shared/
```

### Clean/Hexagonal

```
src/
├── domain/        # Entities, value objects
├── application/   # Use cases, services
├── infrastructure/# Database, external services
└── presentation/  # API, CLI, UI
```

---

## Validation Checklist

After extracting architecture:

- [ ] All major directories are documented
- [ ] Data flow is traceable
- [ ] Key abstractions are identified
- [ ] External dependencies are listed
- [ ] Patterns used are named
- [ ] Component responsibilities are clear
- [ ] Diagram matches actual code structure
