# Architecture Context Template

Template for documenting system architecture in CLAUDE.md.

---

```markdown
## Architecture

[2-3 sentences describing the overall system design approach]

### System Type

- [ ] Monolith
- [ ] Modular Monolith
- [ ] Microservices
- [ ] Serverless
- [ ] Event-driven
- [ ] Hybrid

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

### Directory Structure

```
src/
├── api/              # HTTP handlers, routes
├── services/         # Business logic
├── repositories/     # Data access layer
├── models/           # Database entities, DTOs
├── utils/            # Shared utilities
├── config/           # Configuration
└── types/            # Type definitions
```

### Key Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| API Layer | `src/api/` | HTTP handling, routing, validation |
| Services | `src/services/` | Business logic, orchestration |
| Repositories | `src/repositories/` | Data access, queries |
| Models | `src/models/` | Data structures, entities |

### Data Flow

```
Request → Router → Middleware (auth, validate) → Handler
                                                    ↓
                                               Service
                                                    ↓
                                              Repository
                                                    ↓
                                               Database
                                                    ↓
Response ← Handler ← Service ← Repository ←────────┘
```

### External Integrations

| Service | Purpose | Location |
|---------|---------|----------|
| Database | [PostgreSQL/MySQL/MongoDB] | `src/db/` |
| Cache | [Redis/Memcached] | `src/cache/` |
| Queue | [RabbitMQ/SQS/BullMQ] | `src/queue/` |
| Auth | [Auth0/Cognito/Custom] | `src/auth/` |

### Architectural Patterns

- **Pattern 1**: [e.g., Repository Pattern for data access]
- **Pattern 2**: [e.g., Service Layer for business logic]
- **Pattern 3**: [e.g., Dependency Injection via container]
```

---

## Usage

1. Copy the template above
2. Remove checkboxes and fill in actual values
3. Adjust directory structure to match your project
4. Add/remove sections as needed

## When to Use

- Setting up CLAUDE.md for a new project
- Documenting existing project architecture
- Onboarding AI assistants to understand system design
