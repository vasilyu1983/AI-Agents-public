# Project Memory Full Examples (AGENTS.md / CLAUDE.md)

Complete, production-ready examples for different project types.

Use these examples as the content for `AGENTS.md` (Codex). If you support both tools, keep a single file by symlinking `CLAUDE.md` to `AGENTS.md`.

---

## Example 1: Next.js SaaS Application

```markdown
# SalesMate CRM

B2B sales pipeline management platform.

## Architecture

- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes, Prisma, PostgreSQL
- **Auth**: NextAuth.js with Google/GitHub OAuth
- **Payments**: Stripe
- **Infrastructure**: Vercel, Neon PostgreSQL

## Directory Structure

\`\`\`
src/
├── app/              # App Router pages
│   ├── (auth)/       # Auth routes (login, register)
│   ├── (dashboard)/  # Protected routes
│   └── api/          # API routes
├── components/       # React components
│   ├── ui/           # shadcn/ui components
│   └── features/     # Feature components
├── lib/              # Utilities
│   ├── db.ts         # Prisma client
│   └── auth.ts       # Auth utilities
└── prisma/           # Database schema
\`\`\`

## Commands

- `pnpm dev` - Start development server
- `pnpm build` - Production build
- `pnpm test` - Run Vitest tests
- `pnpm db:push` - Push schema changes
- `pnpm db:studio` - Open Prisma Studio

## Code Standards

- TypeScript strict mode, no `any`
- Use `unknown` for untyped data
- Zod for runtime validation
- Server Actions for mutations
- React Query for data fetching

## Testing

- Vitest for unit tests
- Testing Library for components
- Playwright for E2E (critical paths only)
- 80% coverage for /lib and /components

## Git Workflow

- Branch: `feat/`, `fix/`, `chore/`
- Conventional commits required
- PR required, 1 approval minimum
- Squash merge to main

## Agent Preferences

- Use `frontend-engineer` for UI work
- Use `backend-engineer` for API routes
- Use `sql-engineer` for Prisma queries
```

---

## Example 2: Python FastAPI Backend

```markdown
# OrderFlow API

Order management microservice for e-commerce platform.

## Architecture

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Cache**: Redis
- **Queue**: Celery with Redis broker
- **Auth**: JWT with python-jose

## Directory Structure

\`\`\`
src/
├── api/
│   ├── v1/           # API version 1
│   │   ├── orders/   # Order endpoints
│   │   └── products/ # Product endpoints
│   └── deps.py       # Dependencies
├── core/
│   ├── config.py     # Settings
│   └── security.py   # Auth utilities
├── db/
│   ├── models/       # SQLAlchemy models
│   └── session.py    # Database session
├── schemas/          # Pydantic schemas
├── services/         # Business logic
└── tests/
\`\`\`

## Commands

- `uv run uvicorn src.main:app --reload` - Development
- `uv run pytest` - Run tests
- `uv run alembic upgrade head` - Run migrations
- `uv run ruff check .` - Lint code
- `uv run mypy .` - Type check

## Code Standards

- Python 3.12+
- Type hints required
- Pydantic for validation
- Dependency injection via FastAPI Depends
- async/await for I/O operations

## Testing

- pytest with pytest-asyncio
- Factory Boy for fixtures
- 90% coverage for services/
- Integration tests for API endpoints

## API Conventions

- RESTful resource naming
- Pagination: `?page=1&per_page=20`
- Errors: RFC 7807 Problem Details
- Versioning: URL path `/api/v1/`
```

---

## Example 3: React Native Mobile App

```markdown
# FitTrack

Fitness tracking mobile application.

## Architecture

- **Framework**: React Native 0.73+, Expo SDK 50
- **Navigation**: Expo Router
- **State**: Zustand + React Query
- **Styling**: NativeWind (Tailwind for RN)
- **Backend**: Supabase

## Directory Structure

\`\`\`
app/
├── (tabs)/           # Tab navigation
├── (auth)/           # Auth screens
└── _layout.tsx       # Root layout
components/
├── ui/               # Base components
└── features/         # Feature components
lib/
├── supabase.ts       # Supabase client
└── hooks/            # Custom hooks
\`\`\`

## Commands

- `npx expo start` - Start Expo dev server
- `npx expo run:ios` - Run on iOS simulator
- `npx expo run:android` - Run on Android emulator
- `npm test` - Run Jest tests
- `eas build --profile preview` - Build preview

## Code Standards

- TypeScript strict
- Functional components only
- Custom hooks for logic extraction
- Avoid inline styles (use NativeWind)

## Testing

- Jest + React Native Testing Library
- Detox for E2E (iOS only)
- Test critical user flows

## Agent Preferences

- Use `mobile-engineer` for all work
- Use `frontend-engineer` for shared logic
```

---

## Example 4: Infrastructure/DevOps

```markdown
# CloudPlatform Infrastructure

AWS infrastructure managed with Terraform.

## Architecture

- **IaC**: Terraform 1.6+
- **Cloud**: AWS (us-east-1, eu-west-1)
- **Kubernetes**: EKS 1.29
- **CI/CD**: GitHub Actions
- **Monitoring**: Datadog

## Directory Structure

\`\`\`
terraform/
├── modules/          # Reusable modules
│   ├── vpc/
│   ├── eks/
│   └── rds/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── global/           # Shared resources
kubernetes/
├── base/             # Kustomize base
└── overlays/         # Environment overlays
\`\`\`

## Commands

- `terraform init` - Initialize
- `terraform plan -var-file=env.tfvars` - Plan
- `terraform apply -var-file=env.tfvars` - Apply
- `kubectl apply -k overlays/dev` - Deploy to dev

## Standards

- Terraform fmt before commit
- tfsec for security scanning
- Cost estimation required for large changes
- Blue-green deployments only

## Tagging

All resources must have:
- Environment: dev/staging/prod
- Team: platform
- CostCenter: infrastructure

## Agent Preferences

- Use `devops-engineer` for all work
- Use `security-specialist` for IAM/security
```

---

## Example 5: Monorepo with Turborepo

```markdown
# Acme Platform

Monorepo for Acme web applications.

## Architecture

- **Build**: Turborepo
- **Package Manager**: pnpm
- **Apps**: web (Next.js), admin (Next.js), docs (Nextra)
- **Packages**: ui, config, tsconfig, utils

## Workspace Structure

\`\`\`
apps/
├── web/              # Main website
├── admin/            # Admin dashboard
└── docs/             # Documentation
packages/
├── ui/               # Shared components
├── config/           # ESLint, Prettier configs
├── tsconfig/         # Shared TS configs
└── utils/            # Shared utilities
\`\`\`

## Commands

- `pnpm dev` - Start all apps
- `pnpm build` - Build all
- `pnpm dev --filter=web` - Start specific app
- `pnpm test` - Test all packages
- `pnpm lint` - Lint all

## Standards

- Shared UI components in packages/ui
- No direct cross-app imports
- Use workspace protocol: "workspace:*"
- Changesets for versioning

## When Working Here

1. Check which workspace you're in
2. Run commands from root with --filter
3. Test affected packages: `turbo run test --affected`
4. Update CHANGELOG via changesets
```

---

## Example 6: Behavioral Rules File

Standalone rule file for `.claude/rules/coding-behavior.md` to prevent common AI failure modes. Based on patterns from Andrej Karpathy's agentic coding observations.

```markdown
# Coding Behavior Rules

Rules for disciplined, human-supervised agentic coding.

## Before Implementation

### Surface Assumptions
Before implementing anything non-trivial, explicitly state assumptions:
```
ASSUMPTIONS I'M MAKING:
1. [assumption]
2. [assumption]
→ Correct me now or I'll proceed with these.
```

### Manage Confusion
When encountering inconsistencies or unclear specs:
1. STOP—do not proceed with a guess
2. Name the specific confusion
3. Present the tradeoff or ask the clarifying question
4. Wait for resolution before continuing

### Plan First
For multi-step tasks, emit a lightweight plan:
```
PLAN:
1. [step] — [why]
2. [step] — [why]
→ Executing unless you redirect.
```

## During Implementation

### Scope Discipline
Touch only what you're asked to touch.

DO NOT:
- Remove comments you don't understand
- "Clean up" code orthogonal to the task
- Refactor adjacent systems as side effects
- Delete code that seems unused without approval

### Simplicity Enforcement
Before finishing any implementation, verify:
- Can this be done in fewer lines?
- Are these abstractions earning their complexity?
- Would a senior dev say "why didn't you just..."?

Prefer the boring, obvious solution. Cleverness is expensive.

### Push Back When Warranted
When the proposed approach has clear problems:
- Point out the issue directly
- Explain the concrete downside
- Propose an alternative
- Accept the decision if overridden

Sycophancy is a failure mode.

## After Changes

### Change Summary
After any modification, summarize:
```
CHANGES MADE:
- [file]: [what changed and why]

INTENTIONALLY UNTOUCHED:
- [file]: [left alone because...]

POTENTIAL CONCERNS:
- [any risks or things to verify]
```

### Dead Code Hygiene
After refactoring:
- Identify code that is now unreachable
- List it explicitly
- Ask: "Should I remove these now-unused elements: [list]?"

Don't leave corpses. Don't delete without asking.
```

**Use case**: Add this file when you notice Claude:
- Making assumptions without checking
- Over-engineering simple solutions
- Touching files outside the task scope
- Agreeing too readily to questionable approaches
- Not surfacing tradeoffs on non-obvious decisions

---

## Example 7: Cross-Platform Memory (AGENTS.md + CLAUDE.md)

Complete setup for teams using multiple AI coding assistants with shared behavioral rules.

### File Structure

```text
acme-app/
├── AGENTS.md                    # Primary memory file
├── CLAUDE.md                    # Symlink → AGENTS.md
├── .claude/
│   ├── rules/
│   │   ├── coding-behavior.md   # Karpathy-style behavioral rules
│   │   ├── security.md
│   │   └── testing.md
│   └── settings.json
└── docs/
    └── architecture.md
```

### AGENTS.md (Primary)

```markdown
# Acme App

E-commerce platform with Next.js frontend and Node.js API.

## Quick Start

- `pnpm dev` - Start development
- `pnpm test` - Run tests
- `pnpm build` - Production build

## Architecture

- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind
- **Backend**: Node.js, Fastify, Prisma, PostgreSQL
- **Infrastructure**: Vercel, Neon

See @docs/architecture.md for details.

## Code Standards

- TypeScript strict mode, no `any`
- Prettier + ESLint (run on save)
- Conventional commits required
- 80% test coverage minimum

## Behavioral Rules

@.claude/rules/coding-behavior.md

## Security

@.claude/rules/security.md

## Testing

@.claude/rules/testing.md

## AI Tool Notes

This file works with Codex (AGENTS.md) and Claude Code (CLAUDE.md via symlink). Keep `AGENTS.md` as the single source of truth.

- **Claude Code**: Full support for .claude/rules/ and skills
- **Codex CLI**: Reads AGENTS.md, rules via @imports
- **Cursor**: Copy .claude/rules/coding-behavior.md to .cursorrules if needed
```

### Setup Script

```bash
#!/bin/bash
# setup-ai-tools.sh - Initialize cross-platform AI memory

# Create directories
mkdir -p .claude/rules docs

# Create symlink (CLAUDE.md → AGENTS.md)
ln -sf AGENTS.md CLAUDE.md

# Create behavioral rules
cat > .claude/rules/coding-behavior.md << 'EOF'
# Coding Behavior Rules

## Before Implementation
- Surface assumptions explicitly before proceeding
- STOP on confusion—name it, wait for resolution
- Emit lightweight plan for multi-step tasks

## During Implementation
- Touch only what's asked (no unsolicited cleanup)
- Prefer simple, boring solutions over clever ones
- Push back on bad ideas directly

## After Changes
- Summarize: CHANGES MADE / UNTOUCHED / CONCERNS
- List dead code explicitly, ask before deleting
EOF

echo "✓ Created AGENTS.md + CLAUDE.md symlink"
echo "✓ Created .claude/rules/coding-behavior.md"
echo ""
echo "Next: Edit AGENTS.md with your project details"
```

### Verification

```bash
# Verify symlink
ls -la AGENTS.md
# Should show: CLAUDE.md -> AGENTS.md

# Verify both files have same content
diff AGENTS.md CLAUDE.md
# Should show no output (identical)

# Test with Claude Code
claude "What are my behavioral rules?"

# Test with Codex CLI (if installed)
codex "What are my behavioral rules?"
```

**Use case**: Teams supporting both Codex and Claude Code, wanting consistent AI behavior across all tools without maintaining duplicate documentation.
