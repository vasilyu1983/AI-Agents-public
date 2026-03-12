# Backend Engineering Template Guide

How to add new tech stack templates to this skill.

## Contents

- [Overview](#overview)
- [Template Structure](#template-structure)
- [Sections Explained](#sections-explained)
- [Example: Adding Python + FastAPI Template](#example-adding-python--fastapi-template)
- [Tech Stack Comparison Matrix](#tech-stack-comparison-matrix)
- [Required Components](#required-components)
- [Quality Checklist](#quality-checklist)
- [Naming Convention](#naming-convention)
- [Future Templates](#future-templates)
- [Contributing](#contributing)
- [Shared Utilities (Implementation Patterns)](#shared-utilities-implementation-patterns)
- [Resources](#resources)
- [Questions?](#questions)
- [Version](#version)

---

## Overview

The software-backend skill is designed to be **extensible**. You can easily add support for new tech stacks by creating new template files following the established pattern.

---

## Template Structure

Each template should follow this structure:

```markdown
# Backend Engineering - [Tech Stack Name] Template

*Purpose: Brief description of when to use this stack*

---

# When to Use

Use this template when building:
- [Use case 1]
- [Use case 2]
- [Use case 3]

---

# TEMPLATE STARTS HERE

# 1. Project Overview
# 2. Project Structure
# 3. Environment Configuration
# 4. Database Setup
# 5. Application Setup
# 6. Authentication Implementation
# 7. API Routes & Controllers
# 8. Repository Pattern / Data Access
# 9. Testing
# 10. Docker Setup
# 11. Production Checklist
# 12. API Documentation
# END
```

---

## Sections Explained

### 1. Project Overview
- Project name placeholder
- Tech stack components
- Team roles
- Timeline

### 2. Project Structure
- Directory tree
- File organization
- Module structure
- Naming conventions

### 3. Environment Configuration
- `.env.example` file
- Environment validation
- Configuration management
- Secrets handling

### 4. Database Setup
- Schema definition
- Migration workflow
- ORM/Database client setup
- Connection configuration

### 5. Application Setup
- Framework initialization
- Middleware configuration
- Security setup
- Server entry point
- Graceful shutdown

### 6. Authentication Implementation
- Auth service
- Middleware/guards
- Token generation
- Password hashing
- Authorization logic

**Implementation Reference**: See [auth-utilities.md](../../software-clean-code-standard/utilities/auth-utilities.md) for Argon2id password hashing, jose JWT, and OAuth 2.1/PKCE patterns.

### 7. API Routes & Controllers
- Route definitions
- Controller implementations
- Request handlers
- Response formatting

### 8. Repository Pattern / Data Access
- Repository interfaces
- Data access implementations
- Query methods
- Transaction handling

### 9. Testing
- Unit test examples
- Integration test examples
- E2E test examples
- Test setup
- Coverage configuration

**Implementation Reference**: See [testing-utilities.md](../../software-clean-code-standard/utilities/testing-utilities.md) for Vitest, MSW v2, factories, and fixtures.

### 10. Docker Setup
- Dockerfile
- Multi-stage builds
- docker-compose.yml
- Environment configuration

### 11. Production Checklist
- Security checklist
- Performance checklist
- Monitoring checklist
- Deployment checklist

### 12. API Documentation
- Documentation setup
- Schema definitions
- Example endpoints

---

## Example: Adding Python + FastAPI Template

### Step 1: Create Template File

`assets/template-python-fastapi-sqlalchemy.md`

```markdown
# Backend Engineering - Python + FastAPI + SQLAlchemy Template

*Purpose: Production-grade Python APIs with FastAPI and PostgreSQL*

---

# When to Use

Use this template when building:
- High-performance Python APIs
- Data science backends
- ML model serving
- Async Python applications

---

# TEMPLATE STARTS HERE

# 1. Project Overview

**Tech Stack:**
- [ ] Python 3.11+
- [ ] FastAPI
- [ ] SQLAlchemy 2.0
- [ ] PostgreSQL 14+
- [ ] Redis (caching)
- [ ] Celery (background jobs)
- [ ] Pytest (testing)

---

# 2. Project Structure

```
project-root/
|-- app/
|   |-- api/
|   |   |-- routes/
|   |   |-- dependencies/
|   |   `-- schemas/
|   |-- core/
|   |   |-- config.py
|   |   |-- security.py
|   |   `-- database.py
|   |-- models/
|   |-- services/
|   |-- repositories/
|   `-- main.py
|-- tests/
|-- alembic/
|-- requirements/
|   |-- base.txt
|   |-- dev.txt
|   `-- prod.txt
|-- Dockerfile
|-- docker-compose.yml
`-- pyproject.toml
```

[Continue with remaining sections...]
```

### Step 2: Update sources.json

Add Python/FastAPI resources:

```json
{
  "python_frameworks": [
    {
      "name": "FastAPI Documentation",
      "url": "https://fastapi.tiangolo.com/",
      "type": "framework",
      "relevance": "Modern Python web framework with automatic API docs, async support",
      "update_frequency": "continuous",
      "access": "free",
      "add_as_web_search": true
    },
    {
      "name": "SQLAlchemy Documentation",
      "url": "https://docs.sqlalchemy.org/",
      "type": "orm",
      "relevance": "Python ORM, database toolkit, migrations",
      "update_frequency": "continuous",
      "access": "free",
      "add_as_web_search": true
    },
    {
      "name": "Pydantic Documentation",
      "url": "https://docs.pydantic.dev/",
      "type": "library",
      "relevance": "Data validation using Python type annotations",
      "update_frequency": "active",
      "access": "free",
      "add_as_web_search": true
    }
  ],
  "python_testing": [
    {
      "name": "Pytest Documentation",
      "url": "https://docs.pytest.org/",
      "type": "testing",
      "relevance": "Python testing framework, fixtures, mocking",
      "update_frequency": "active",
      "access": "free",
      "add_as_web_search": false
    }
  ]
}
```

### Step 3: Update README.md

Add to "Supported Tech Stacks" section:

```markdown
### Supported Tech Stacks
[OK] **Node.js + Prisma + PostgreSQL** (complete)
[OK] **Python + FastAPI + SQLAlchemy** (complete)
```

### Step 4: Reference in skill.md

Update the "Templates" section:

```markdown
# Templates

See `assets/` directory for tech-stack-specific implementations:

- `template-nodejs-prisma-postgres.md` - Node.js + Prisma + PostgreSQL
- `template-python-fastapi-sqlalchemy.md` - Python + FastAPI + SQLAlchemy
- More templates can be added for other stacks
```

---

## Tech Stack Comparison Matrix

When creating a new template, consider this comparison:

| Aspect | Node.js + Prisma | Python + FastAPI | Go + GORM | Ruby on Rails |
|--------|------------------|------------------|-----------|---------------|
| **Performance** | High (async) | High (async) | Very High | Medium |
| **Type Safety** | TypeScript | Pydantic | Native | Sorbet |
| **Learning Curve** | Medium | Low-Medium | Medium-High | Low |
| **Ecosystem** | npm (huge) | PyPI (large) | Go modules | RubyGems |
| **Best For** | APIs, real-time | ML/DS backends | Microservices | Full-stack web |
| **ORM** | Prisma | SQLAlchemy | GORM | ActiveRecord |
| **Concurrency** | Event loop | asyncio | Goroutines | Threads |

---

## Required Components

Every template must include:

### Core Patterns [OK]
- [x] Project structure
- [x] Environment configuration
- [x] Database setup and migrations
- [x] Application initialization
- [x] Route/endpoint definitions
- [x] Request/response handling
- [x] Data access layer

### Security [OK]
- [x] Authentication implementation
- [x] Authorization/RBAC
- [x] Password hashing
- [x] Input validation
- [x] Security headers
- [x] Rate limiting
- [x] CORS configuration

### Performance [OK]
- [x] Database query optimization
- [x] Caching strategy
- [x] Pagination implementation
- [x] Response compression
- [x] Connection pooling

### Testing [OK]
- [x] Unit test examples
- [x] Integration test examples
- [x] E2E test examples
- [x] Test database setup
- [x] Mocking strategies

### Operations [OK]
- [x] Docker configuration
- [x] docker-compose for local dev
- [x] Health check endpoint
- [x] Graceful shutdown
- [x] Logging configuration
- [x] Error tracking setup

### Documentation [OK]
- [x] API documentation setup
- [x] README with setup steps
- [x] Environment variable docs
- [x] Deployment guide
- [x] Production checklist

---

## Quality Checklist

Before submitting a new template:

### Code Quality
- [ ] All code examples are tested and working
- [ ] Follows language-specific conventions
- [ ] Type safety enabled where available
- [ ] Consistent naming conventions
- [ ] Proper error handling in all examples

### Completeness
- [ ] All 12 sections are filled out
- [ ] Real-world code examples provided
- [ ] Configuration files are complete
- [ ] Docker setup is production-ready
- [ ] Tests cover critical paths

### Documentation
- [ ] Clear explanations for each pattern
- [ ] "When to Use" guidance provided
- [ ] Checklists for validation
- [ ] Links to official documentation
- [ ] Common pitfalls mentioned

### Integration
- [ ] Referenced in README.md
- [ ] Resources added to sources.json
- [ ] Mentioned in skill.md templates section
- [ ] Command file updated (if needed)

---

## Naming Convention

Template files should follow this pattern:

```
template-<language>-<framework>-<database>.md
```

Examples:
- [OK] `template-nodejs-prisma-postgres.md`
- [OK] `template-python-fastapi-sqlalchemy.md`
- [OK] `template-go-fiber-gorm.md`
- [OK] `template-ruby-rails-postgres.md`
- [OK] `template-java-spring-jpa.md`
- [OK] `template-csharp-aspnet-efcore.md`

---

## Future Templates

Ideas for additional templates:

### High Priority
- [ ] Python + FastAPI + SQLAlchemy + PostgreSQL
- [ ] Go + Fiber + GORM + PostgreSQL
- [ ] Java + Spring Boot + JPA + PostgreSQL
- [ ] C# + ASP.NET Core + EF Core + PostgreSQL

### Medium Priority
- [ ] Ruby on Rails + PostgreSQL
- [ ] PHP + Laravel + Eloquent + PostgreSQL
- [ ] Rust + Actix + Diesel + PostgreSQL
- [ ] Kotlin + Ktor + Exposed + PostgreSQL

### Specialized
- [ ] Node.js + GraphQL + Prisma + PostgreSQL
- [ ] Python + Django REST Framework + PostgreSQL
- [ ] Elixir + Phoenix + Ecto + PostgreSQL
- [ ] Scala + Play + Slick + PostgreSQL

---

## Contributing

To contribute a new template:

1. Fork the repository
2. Create a new template file following this guide
3. Update sources.json with relevant resources
4. Update README.md to list the new stack
5. Test all code examples
6. Submit a pull request with:
   - Template file
   - Updated documentation
   - Example project (optional)

---

## Shared Utilities (Implementation Patterns)

For cross-cutting implementation concerns, reference these centralized utilities:

- [auth-utilities.md](../../software-clean-code-standard/utilities/auth-utilities.md) - Argon2id password hashing, jose JWT, OAuth 2.1/PKCE
- [error-handling.md](../../software-clean-code-standard/utilities/error-handling.md) - Effect Result types, correlation IDs, error boundaries
- [config-validation.md](../../software-clean-code-standard/utilities/config-validation.md) - Zod 3.24+, Valibot, secrets management (1Password/Doppler)
- [resilience-utilities.md](../../software-clean-code-standard/utilities/resilience-utilities.md) - p-retry v6, opossum v8 circuit breaker, OTel spans
- [logging-utilities.md](../../software-clean-code-standard/utilities/logging-utilities.md) - pino v9 + OpenTelemetry integration
- [testing-utilities.md](../../software-clean-code-standard/utilities/testing-utilities.md) - Vitest, MSW v2, factories, fixtures
- [observability-utilities.md](../../software-clean-code-standard/utilities/observability-utilities.md) - OpenTelemetry SDK, tracing, metrics

---

## Resources

- [Node.js Template](../assets/nodejs/template-nodejs-prisma-postgres.md) - Reference implementation
- [Backend Skill Documentation](../skill.md) - Core patterns
- [Sources JSON](../data/sources.json) - Resource format

---

## Questions?

If you have questions about creating a new template:

1. Review the existing Node.js template
2. Check the skill.md for core patterns
3. Consult sources.json for resource structure
4. Open an issue in the repository

---

## Version

- **Version:** 1.0.0
- **Created:** 2025-11-17
- **Last Updated:** 2025-11-17
