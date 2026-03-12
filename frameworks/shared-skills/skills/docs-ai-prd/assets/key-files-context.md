# Key Files Context Template

Template for documenting important files in CLAUDE.md.

---

```markdown
## Key Files

### Entry Points

| Purpose | Location | Notes |
|---------|----------|-------|
| Main entry | `src/index.ts` | Server bootstrap, starts HTTP server |
| App setup | `src/app.ts` | Express/Fastify app configuration |
| CLI entry | `src/cli.ts` | Command-line interface entry |

### Configuration

| Purpose | Location | Notes |
|---------|----------|-------|
| Environment | `.env.example` | Template for environment variables |
| App config | `src/config/index.ts` | Validated configuration loading |
| TypeScript | `tsconfig.json` | Compiler options |
| ESLint | `.eslintrc.js` | Linting rules |
| Prettier | `.prettierrc` | Formatting rules |

### Database

| Purpose | Location | Notes |
|---------|----------|-------|
| Schema | `prisma/schema.prisma` | Database schema definition |
| Migrations | `prisma/migrations/` | Migration history |
| Seed data | `prisma/seed.ts` | Initial/test data |
| DB client | `src/db/client.ts` | Database connection instance |

### API Layer

| Purpose | Location | Notes |
|---------|----------|-------|
| Routes | `src/api/routes/index.ts` | All route definitions |
| Middleware | `src/middleware/` | Auth, validation, error handling |
| Controllers | `src/api/handlers/` | Request handlers |

### Business Logic

| Purpose | Location | Notes |
|---------|----------|-------|
| Services | `src/services/` | Core business logic |
| Repositories | `src/repositories/` | Data access layer |
| Domain models | `src/domain/` | Business entities |

### Types & Interfaces

| Purpose | Location | Notes |
|---------|----------|-------|
| API types | `src/types/api.ts` | Request/response types |
| Domain types | `src/types/domain.ts` | Business entity types |
| Config types | `src/types/config.ts` | Configuration types |
| Shared types | `src/types/index.ts` | Re-exported types |

### Testing

| Purpose | Location | Notes |
|---------|----------|-------|
| Test setup | `src/test/setup.ts` | Jest/Vitest configuration |
| Fixtures | `src/test/fixtures/` | Test data |
| Mocks | `src/test/mocks/` | Mock implementations |
| E2E tests | `tests/e2e/` | End-to-end tests |

### DevOps

| Purpose | Location | Notes |
|---------|----------|-------|
| Dockerfile | `Dockerfile` | Container build |
| Docker Compose | `docker-compose.yml` | Local development |
| CI/CD | `.github/workflows/` | GitHub Actions |
| K8s manifests | `k8s/` | Kubernetes deployment |

### Documentation

| Purpose | Location | Notes |
|---------|----------|-------|
| README | `README.md` | Project overview |
| API docs | `docs/api/` | API documentation |
| ADRs | `docs/adr/` | Architecture decisions |
| CLAUDE.md | `CLAUDE.md` | AI context |
```

---

## Discovery Commands

Find key files in a new codebase:

```bash
# Entry points
find . -name "index.*" -o -name "main.*" -o -name "app.*" -o -name "server.*" | head -20

# Configuration files
find . -name "*.config.*" -o -name "config.*" -o -name ".env*" | grep -v node_modules

# Package/dependency files
ls package.json requirements.txt Cargo.toml go.mod pom.xml 2>/dev/null

# Database/ORM files
find . -name "schema.prisma" -o -name "*.entity.ts" -o -name "models.py" | head -20

# Route definitions
grep -r "router\.\|app\.get\|app\.post\|@Get\|@Post" --include="*.ts" -l | head -10

# Test configuration
find . -name "jest.config.*" -o -name "vitest.config.*" -o -name "pytest.ini" 2>/dev/null
```

## Usage

1. Copy the relevant sections
2. Fill in actual file paths
3. Add notes about non-obvious locations
4. Remove sections that don't apply
