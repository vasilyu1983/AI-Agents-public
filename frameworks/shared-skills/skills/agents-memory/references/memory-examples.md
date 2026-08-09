# Project Memory Full Examples (AGENTS.md / CLAUDE.md)

Complete, production-ready examples for different project types.

Use these examples as the content for `AGENTS.md` (Codex). If you support both tools, keep a single file by symlinking `CLAUDE.md` to `AGENTS.md`.

---
## Table of Contents

**Stack-specific AGENTS.md + CLAUDE.md templates** (each file is `AGENTS.md` primary, symlinked to `CLAUDE.md`; pair with Example 6 for behavioral rules):

- [Example 1: Next.js SaaS Application](#example-1-nextjs-saas-application)
- [Example 2: Python FastAPI Backend](#example-2-python-fastapi-backend)
- [Example 3: React Native Mobile App](#example-3-react-native-mobile-app)
- [Example 4: Infrastructure/DevOps](#example-4-infrastructuredevops)
- [Example 5: Monorepo with Turborepo](#example-5-monorepo-with-turborepo)

**Shared patterns** (referenced from every stack example):

- [Example 6: Behavioral Rules File](#example-6-behavioral-rules-file) — canonical `.claude/rules/coding-behavior.md` (refined with Karpathy patterns, 2026-04-15)
- [Example 7: Cross-Platform Memory (AGENTS.md + CLAUDE.md)](#example-7-cross-platform-memory-agentsmd-claudemd) — full setup with symlink, verification, and setup script
- [Example 8: Prompt / Agent Library Repo](#example-8-prompt--agent-library-repo) — meta-repos that contain prompts and skills as first-class artifacts

**Starter**:

- [Example 9: Minimal AGENTS.md + CLAUDE.md Starter](#example-9-minimal-agentsmd--claudemd-starter) — shortest working template; use for new repos or to strip a bloated file back to baseline

**Which example to start from?**

| Situation | Start with |
|---|---|
| Brand new repo, no AGENTS.md yet | Example 9 (minimal) + Example 6 (rules) |
| Existing Next.js / React app | Example 1 |
| Python API service | Example 2 |
| React Native / Expo app | Example 3 |
| Terraform / infra repo | Example 4 |
| Monorepo | Example 5 |
| Need behavioral rules only (not a full memory file) | Example 6 |
| Need to set up the bridge between `AGENTS.md` and `CLAUDE.md` | Example 7 |
| Repo IS a library of prompts/skills (like this one) | Example 8 |


## Example 1: Next.js SaaS Application

**File**: `AGENTS.md` (primary). Mirror to `CLAUDE.md` via `ln -sf AGENTS.md CLAUDE.md`. Pairs with [Example 6](#example-6-behavioral-rules-file) for behavioral rules in `.claude/rules/coding-behavior.md`.

```markdown
# SalesMate CRM

B2B sales pipeline management platform. This file works with Codex (reads `AGENTS.md`) and Claude Code (reads `CLAUDE.md` via symlink to the same file).

## Architecture

- **Frontend**: Next.js 16 (App Router), React 19, TypeScript 5.6, Tailwind CSS 4
- **Backend**: Next.js API Routes, Prisma 6, PostgreSQL 17
- **Auth**: NextAuth.js v5 (Auth.js) with Google/GitHub OAuth
- **Payments**: Stripe Billing + Checkout
- **Infrastructure**: Vercel, Neon Postgres

## Directory Structure

\`\`\`
src/
├── app/              # App Router pages
│   ├── (auth)/       # Auth routes (login, register)
│   ├── (dashboard)/  # Protected routes
│   └── api/          # API routes
├── components/
│   ├── ui/           # shadcn/ui components
│   └── features/     # Feature components
├── lib/
│   ├── db.ts         # Prisma client
│   └── auth.ts       # Auth utilities
└── prisma/           # Database schema
\`\`\`

## Commands

- `pnpm dev` — development server
- `pnpm build` — production build
- `pnpm test` — Vitest
- `pnpm lint` — Biome
- `pnpm typecheck` — TypeScript strict
- `pnpm db:push` — push schema changes
- `pnpm db:studio` — open Prisma Studio

## Code Standards

- TypeScript strict mode, no `any` — use `unknown` for untyped data
- Zod for runtime validation at API boundaries
- Server Actions for mutations, React Query for client fetching
- Biome + Prettier handle style — do not put style rules in this file

## Verification

After code changes, run:
1. `pnpm test` — confirm no regressions
2. `pnpm lint` — style compliance
3. `pnpm typecheck` — TypeScript strict

After DB schema edits, run:
1. `pnpm db:push` — apply to dev database
2. Hit the affected route in the browser to confirm end-to-end

For UI changes, verify visually in the browser before claiming success. Type checks and tests verify code correctness, not UX.

## Boundaries

### Always Do
- Run `pnpm test` and `pnpm typecheck` after code changes
- Update `prisma/schema.prisma` when changing DB columns
- Read existing similar code before writing new code

### Ask First
- Installing new dependencies
- Modifying database schema (data migration implications)
- Changing API contracts or public interfaces
- Deleting files

### Never Do
- Force-push to `main`
- Commit secrets (`.env.local`, Stripe keys, database URLs)
- Modify `lib/auth.ts` without review
- Delete test files or disable failing tests to make CI green

## Testing

- Vitest for unit tests, Testing Library for components
- Playwright for E2E (critical paths only)
- 80% coverage for `/lib` and `/components`

## Git Workflow

- Branches: `feat/`, `fix/`, `chore/`
- Conventional commits required
- PR required, 1 approval minimum
- Squash merge to `main`

## Agent Preferences

- `frontend-engineer` for UI work
- `backend-engineer` for API routes
- `sql-engineer` for Prisma queries

## Behavioral Rules

See `.claude/rules/coding-behavior.md` (from Example 6) for assumption surfacing, scope discipline, goal transformation, verification loops, and dead-code hygiene. Those rules apply repo-wide.

---

**This file is working if:** fewer unnecessary changes in PR diffs, fewer "I forgot to run typecheck" comments, and clarifying questions appear before implementation rather than after mistakes.
```

---

## Example 2: Python FastAPI Backend

**File**: `AGENTS.md` (primary). Mirror to `CLAUDE.md` via `ln -sf AGENTS.md CLAUDE.md`. Pairs with [Example 6](#example-6-behavioral-rules-file) for behavioral rules in `.claude/rules/coding-behavior.md`.

```markdown
# OrderFlow API

Order management microservice for e-commerce. This file works with Codex (reads `AGENTS.md`) and Claude Code (reads `CLAUDE.md` via symlink to the same file).

## Architecture

- **Framework**: FastAPI 0.115+, Python 3.13
- **Database**: PostgreSQL 17 with SQLAlchemy 2.0 (async)
- **Cache**: Redis 7
- **Queue**: Celery with Redis broker
- **Auth**: JWT with Authlib

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

- `uv run uvicorn src.main:app --reload` — development server
- `uv run pytest` — run tests
- `uv run alembic upgrade head` — apply migrations
- `uv run ruff check .` — lint
- `uv run ruff format .` — format
- `uv run mypy src` — type check

## Code Standards

- Python 3.13+, type hints required everywhere
- Pydantic v2 for validation and schemas
- Dependency injection via FastAPI `Depends`
- `async`/`await` for all I/O operations
- Ruff + mypy handle style and type errors — do not put style rules in this file

## Verification

After code changes, run:
1. `uv run pytest` — confirm no regressions
2. `uv run ruff check .` — lint compliance
3. `uv run mypy src` — type check

After schema migrations:
1. `uv run alembic upgrade head` — apply migration
2. `curl http://localhost:8000/api/v1/[affected-route]` — hit the endpoint to confirm the schema change works end-to-end

For new API endpoints, check the OpenAPI docs render correctly at `/docs` before claiming success.

## Boundaries

### Always Do
- Run `uv run pytest` and `uv run mypy src` after code changes
- Create an Alembic migration for every schema change (never edit DB directly)
- Read existing similar endpoints before writing new ones

### Ask First
- Installing new dependencies
- Adding a new API version or breaking the public schema
- Changing auth/JWT logic in `core/security.py`
- Modifying Celery task signatures (in-flight jobs depend on them)
- Deleting files

### Never Do
- Force-push to `main`
- Commit secrets (`.env`, JWT signing keys, database URLs)
- Skip migrations by editing DB schema directly
- Disable failing tests to make CI green

## Testing

- pytest with pytest-asyncio
- Factory Boy for fixtures, respx for HTTP mocking
- 90% coverage for `services/`
- Integration tests for all API endpoints

## API Conventions

- RESTful resource naming
- Pagination: `?page=1&per_page=20`
- Errors: RFC 7807 Problem Details
- Versioning: URL path `/api/v1/`

## Behavioral Rules

See `.claude/rules/coding-behavior.md` (from Example 6) for assumption surfacing, scope discipline, goal transformation, verification loops, and dead-code hygiene. Those rules apply repo-wide.

---

**This file is working if:** fewer unnecessary changes in PR diffs, fewer forgotten Alembic migrations, and clarifying questions appear before implementation rather than after mistakes.
```

---

## Example 3: React Native Mobile App

**File**: `AGENTS.md` (primary). Mirror to `CLAUDE.md` via `ln -sf AGENTS.md CLAUDE.md`. Pairs with [Example 6](#example-6-behavioral-rules-file) for behavioral rules in `.claude/rules/coding-behavior.md`.

```markdown
# FitTrack

Fitness tracking mobile application. This file works with Codex (reads `AGENTS.md`) and Claude Code (reads `CLAUDE.md` via symlink to the same file).

## Architecture

- **Framework**: React Native 0.77, Expo SDK 52
- **Navigation**: Expo Router v4
- **State**: Zustand + TanStack Query v5
- **Styling**: NativeWind 4 (Tailwind for RN)
- **Backend**: Supabase
- **Native modules**: New Architecture (Fabric + TurboModules) enabled

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

- `npx expo start` — start Expo dev server
- `npx expo run:ios` — run on iOS simulator
- `npx expo run:android` — run on Android emulator
- `pnpm test` — Jest
- `pnpm lint` — ESLint with Expo config
- `pnpm typecheck` — TypeScript strict
- `eas build --profile preview` — build preview

## Code Standards

- TypeScript strict mode
- Functional components only (no class components)
- Custom hooks for logic extraction
- Avoid inline styles — use NativeWind utility classes
- ESLint handles style — do not put style rules in this file

## Verification

After code changes, run:
1. `pnpm test` — confirm no regressions
2. `pnpm lint` — style compliance
3. `pnpm typecheck` — TypeScript strict

For UI changes, you MUST test on at least one simulator before claiming success:
1. `npx expo run:ios` or `npx expo run:android`
2. Navigate to the screen you changed
3. Confirm behavior matches spec — tests do not catch layout, gesture, or animation regressions

When modifying native code or Expo config, run a full rebuild with `eas build --profile preview` before merging — cached dev builds can mask native crashes.

## Boundaries

### Always Do
- Run `pnpm test` and `pnpm typecheck` after code changes
- Test on a simulator before claiming UI changes work
- Update `app.json` version and build number when shipping

### Ask First
- Installing native modules (triggers rebuild + EAS credentials)
- Changing Expo SDK version (coordination across team)
- Modifying `app.json`, `eas.json`, or native config (`ios/`, `android/`)
- Changing Supabase RLS policies
- Deleting files

### Never Do
- Force-push to `main`
- Commit secrets (Supabase keys, EAS credentials, Apple/Google certs)
- Eject from Expo without team discussion
- Disable failing tests to make CI green

## Testing

- Jest + React Native Testing Library
- Detox for E2E (iOS only)
- Test critical user flows (auth, primary CRUD, payments)

## Agent Preferences

- `mobile-engineer` for all work
- `frontend-engineer` for shared logic with web clients

## Behavioral Rules

See `.claude/rules/coding-behavior.md` (from Example 6) for assumption surfacing, scope discipline, goal transformation, verification loops, and dead-code hygiene. Those rules apply repo-wide.

---

**This file is working if:** fewer "works in the simulator, broken on device" surprises, fewer native rebuilds needed after supposedly-safe edits, and clarifying questions appear before implementation rather than after mistakes.
```

---

## Example 4: Infrastructure/DevOps

**File**: `AGENTS.md` (primary). Mirror to `CLAUDE.md` via `ln -sf AGENTS.md CLAUDE.md`. Pairs with [Example 6](#example-6-behavioral-rules-file) for behavioral rules in `.claude/rules/coding-behavior.md`.

```markdown
# CloudPlatform Infrastructure

AWS infrastructure managed with Terraform. This file works with Codex (reads `AGENTS.md`) and Claude Code (reads `CLAUDE.md` via symlink to the same file).

**Tradeoff notice**: This is a production infrastructure repo. Every change can page someone at 3am. These rules bias aggressively toward caution — slowdown over risk.

## Architecture

- **IaC**: Terraform 1.11+, OpenTofu-compatible
- **Cloud**: AWS (us-east-1, eu-west-1)
- **Kubernetes**: EKS 1.32
- **CI/CD**: GitHub Actions with OIDC (no long-lived keys)
- **State**: S3 + DynamoDB lock
- **Secrets**: AWS Secrets Manager + External Secrets Operator
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
└── global/           # Shared resources (IAM, Route53, org-wide)
kubernetes/
├── base/             # Kustomize base
└── overlays/         # Environment overlays
```

## Commands

- `terraform init` — initialize backend
- `terraform plan -var-file=env.tfvars` — produce a plan
- `terraform apply -var-file=env.tfvars` — apply (requires review; see Boundaries)
- `terraform fmt -recursive` — format all HCL files
- `terraform validate` — syntax + schema check
- `tfsec terraform/` — security scan
- `infracost breakdown --path terraform/environments/<env>` — cost estimate
- `kubectl apply -k kubernetes/overlays/dev` — deploy to dev

## Standards

- `terraform fmt` and `terraform validate` must pass before commit
- `tfsec` must pass on every PR
- Cost estimation required for any change touching `rds/`, `eks/`, or `global/`
- Blue-green deployments only — no in-place mutations of live resources
- All modules must have `README.md` with inputs/outputs table
- Use `for_each` with maps, never `count` (drift resistance)

## Verification

Before applying ANY change:
1. `terraform fmt -recursive` — formatting
2. `terraform validate` — schema
3. `tfsec terraform/` — security
4. `terraform plan -var-file=env.tfvars -out=tfplan` — produce plan
5. **READ the full plan output** — look for `destroy`, `replace`, and `forces new resource`
6. `infracost breakdown --path <env>` — confirm cost delta is expected

After applying to dev:
1. `kubectl get pods -A` — confirm no pod disruption
2. Check Datadog dashboards for the affected service for 10 minutes post-apply
3. Only then promote the same plan to staging, then prod

**Never apply a plan you did not read in full. Never apply to prod without staging soak.**

## Boundaries

### Always Do
- Run `terraform plan` and read the FULL output before any apply
- Use `-var-file=env.tfvars` — never pass variables inline
- Create a PR for every change, even for dev
- Tag every resource with the required tags (see Tagging below)

### Ask First
- Any `terraform apply` to staging or prod (approval required in GitHub Actions)
- Any change that `terraform plan` shows as `destroy` or `replace` on stateful resources (RDS, S3, DynamoDB, EBS)
- Modifying `global/` (affects all environments)
- Adding new IAM policies or trust relationships
- Changing EKS node groups or networking
- Modifying backend/state configuration
- Deleting files

### Never Do
- `terraform apply` without `plan` first
- Commit `.tfvars` files containing real values (use AWS Secrets Manager)
- Commit AWS access keys, session tokens, or state files
- Run `terraform destroy` without a rollback plan
- Bypass `tfsec` failures to ship faster
- Force-push to `main`
- Disable required PR checks

## Tagging

All resources must have:
- `Environment` — dev / staging / prod
- `Team` — platform
- `CostCenter` — infrastructure
- `ManagedBy` — terraform
- `Repository` — github.com/acme/cloudplatform

## Agent Preferences

- `devops-engineer` for module and Kubernetes work
- `security-specialist` for IAM, encryption, network policies

## Behavioral Rules

See `.claude/rules/coding-behavior.md` (from Example 6) for assumption surfacing, scope discipline, goal transformation, verification loops, and dead-code hygiene. Those rules apply repo-wide — with extra emphasis on scope discipline: infrastructure changes do not get "cleanups" as side effects.

---

**This file is working if:** fewer surprise `destroy` events in plans, fewer 3am pages from unreviewed applies, zero committed secrets, and clarifying questions appear before implementation rather than after mistakes.
```

---

## Example 5: Monorepo with Turborepo

**Files**: `AGENTS.md` at repo root (primary), mirrored to `CLAUDE.md` via `ln -sf AGENTS.md CLAUDE.md`. **Plus nested `AGENTS.md` per app/package** when a workspace has local conventions that differ from the root. Each nested file also mirrors to a nested `CLAUDE.md`. Pairs with [Example 6](#example-6-behavioral-rules-file) for behavioral rules in `.claude/rules/coding-behavior.md` at the repo root.

### Root `AGENTS.md`

```markdown
# Acme Platform

Monorepo for Acme web applications. This file works with Codex (reads `AGENTS.md`) and Claude Code (reads `CLAUDE.md` via symlink to the same file).

**Monorepo rule**: this root file has the rules that apply to EVERY workspace. Each app/package with local conventions has its own nested `AGENTS.md` — read that one before editing files in the workspace.

## Architecture

- **Build**: Turborepo 2.4
- **Package Manager**: pnpm 10
- **Apps**: web (Next.js 16), admin (Next.js 16), docs (Nextra 4)
- **Packages**: `ui`, `config`, `tsconfig`, `utils`

## Workspace Structure

\`\`\`
apps/
├── web/              # Main website            → has apps/web/AGENTS.md
├── admin/            # Admin dashboard         → has apps/admin/AGENTS.md
└── docs/             # Documentation
packages/
├── ui/               # Shared components       → has packages/ui/AGENTS.md
├── config/           # ESLint, Biome configs
├── tsconfig/         # Shared TS configs
└── utils/            # Shared utilities
\`\`\`

## Commands (run from repo root)

- `pnpm dev` — start all apps
- `pnpm dev --filter=web` — start specific app
- `pnpm build` — build all
- `pnpm test` — test all packages
- `pnpm lint` — lint all
- `pnpm typecheck` — typecheck all
- `turbo run test --filter=[HEAD^1]` — test only packages affected by last commit

## Standards

- Shared UI components live in `packages/ui` — never duplicate across apps
- No direct cross-app imports (`apps/web` cannot import from `apps/admin`)
- Use workspace protocol: `"workspace:*"` for internal deps
- Changesets for versioning: `pnpm changeset`
- Biome handles style — do not put style rules in this file

## Verification

After code changes, run (from repo root):
1. `turbo run test --filter=[HEAD^1]` — test affected packages only
2. `turbo run lint --filter=[HEAD^1]` — lint affected
3. `turbo run typecheck --filter=[HEAD^1]` — typecheck affected

After changes touching `packages/` (shared code):
1. Run tests across ALL consumers, not just the package: `pnpm test` (full suite)
2. Check `pnpm build` succeeds end-to-end — shared type changes can break consumers silently at build time

For UI changes in `packages/ui`, verify in at least one consuming app in the browser before claiming success.

## Boundaries

### Always Do
- Run commands from repo root with `--filter=<workspace>`
- Check which workspace you are in before editing — and read its nested `AGENTS.md` if one exists
- Create a changeset for every package change: `pnpm changeset`
- Run `turbo run test --filter=[HEAD^1]` before pushing

### Ask First
- Adding a new app or package (monorepo graph impact)
- Changing shared `tsconfig`, `eslint`, or `biome` config
- Modifying `turbo.json` pipeline
- Bumping pnpm or Turborepo major version
- Deleting files from `packages/` (likely break consumers)

### Never Do
- Directly import from another app's `src/` (use `packages/` instead)
- Publish without a changeset entry
- Force-push to `main`
- Commit secrets or `.env` files
- Disable failing tests in one package to unblock another

## When Working Here

1. Check which workspace you're in — `pwd` relative to `apps/` or `packages/`
2. Look for a nested `AGENTS.md` in the workspace; read it before editing
3. Run commands from root with `--filter=<workspace>` (not `cd` into the workspace)
4. For cross-workspace changes, test the full graph: `pnpm test`
5. Update CHANGELOG via `pnpm changeset` before PR

## Agent Preferences

- `frontend-engineer` for work in `apps/` and `packages/ui`
- `backend-engineer` for API routes inside any Next.js app
- `devops-engineer` for `turbo.json`, CI, and release automation

## Behavioral Rules

See `.claude/rules/coding-behavior.md` (from Example 6) for assumption surfacing, scope discipline, goal transformation, verification loops, and dead-code hygiene. Those rules apply repo-wide.

**Monorepo-specific scope discipline**: a change "in `packages/ui`" can break 3 apps. The trace test (every changed line must trace to the user's request) is especially strict here — if a UI package edit needs corresponding app updates, that is IN scope; if it touches unrelated app code, that is OUT.

---

**This file is working if:** fewer accidental cross-app imports, fewer shared-package changes that break consumers at build time, zero changesets forgotten at merge, and clarifying questions appear before implementation rather than after mistakes.
```

### Nested workspace example: `apps/web/AGENTS.md`

Only create a nested file when a workspace has conventions that differ from the root. Keep it short — it inherits everything from the root file.

```markdown
# apps/web

Main public website. Inherits rules from the root `AGENTS.md`. This file only documents what differs.

## Local Conventions

- This app uses ISR (Incremental Static Regeneration); do not introduce `dynamic = 'force-dynamic'` without a revalidation plan
- All user-facing strings go through `next-intl` — never hardcode English
- Page-level metadata lives in `app/[locale]/layout.tsx` — do not fragment it

## Local Commands (run from `apps/web`)

- `pnpm dev` — dev server on :3000
- `pnpm test:e2e` — Playwright E2E (web-only)

## Local Verification

After UI changes, test ISR behavior:
1. `pnpm build && pnpm start`
2. Visit a cached page, then the CMS, then re-request the page — confirm new content appears within the revalidation window

## Local Boundaries

- **Never** disable ISR for a page without documenting the reason in the PR description
- **Ask first** before touching `next.config.mjs` — affects build and deploy config
```

**When to create a nested `AGENTS.md`**: the workspace has a constraint the agent keeps violating from the root file alone (ISR here, or iOS-specific build quirks in `apps/mobile`, or RLS rules in `packages/db`). If the root file already covers it, do not nest — duplication drifts.

---

## Example 6: Behavioral Rules File

Standalone rule file for `.claude/rules/coding-behavior.md` to prevent common AI failure modes. Based on patterns from Andrej Karpathy's agentic coding observations. Refined 2026-04-15 with patterns from [forrestchang/andrej-karpathy-skills@fb8fdb0](https://github.com/forrestchang/andrej-karpathy-skills) (MIT) — goal transformation, trace test, 200-line heuristic, orphan distinction, tradeoff disclosure, and the working-if metric.

**Canonical source**: [`references/coding-behavior.md`](coding-behavior.md) inside this skill. The version shown below is kept inline as a readable example; the standalone file is the single source of truth for installation. To activate the rules in a repo, symlink rather than copy so updates propagate automatically:

```bash
# From your repo root
mkdir -p .claude/rules
ln -sf ~/.claude/skills/agents-memory/references/coding-behavior.md .claude/rules/coding-behavior.md
```

This skill's own CLAUDE.md rules (in the AI-Agents repo) use exactly this pattern — `.claude/rules/coding-behavior.md` is a symlink to the canonical file above, so every update to Example 6 and the standalone file flows through automatically without manual sync.

```markdown
# Coding Behavior Rules

Rules for disciplined, human-supervised agentic coding.

**Tradeoff:** These rules bias toward caution over speed. For trivial tasks, use judgment.

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

### Transform Vague Tasks to Verifiable Goals
Before writing code, convert the request into a testable goal. Strong success criteria let the agent loop independently; weak criteria ("make it work") require constant clarification.

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For each step of a multi-step plan, state the verification check inline:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```

## During Implementation

### Scope Discipline
Touch only what you're asked to touch.

DO NOT:
- Remove comments you don't understand
- "Clean up" code orthogonal to the task
- Refactor adjacent systems as side effects
- Delete code that seems unused without approval

**Test**: Every changed line must trace directly to the user's request.

### Simplicity Enforcement
Before finishing any implementation, verify:
- Can this be done in fewer lines?
- Are these abstractions earning their complexity?
- Would a senior dev say "why didn't you just..."?
- If you wrote 200 lines and it could be 50, rewrite it.

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
Distinguish orphans you created from pre-existing dead code:

**Orphans (code your edits just made unused)** — clean up without asking:
- Remove imports, variables, and functions that your changes orphaned
- Don't leave corpses from your own edits

**Pre-existing dead code (unrelated to your changes)** — mention, do not delete:
- List it explicitly: "I noticed these pre-existing unused elements: [list]"
- Ask before removing: "Should I remove them in a follow-up?"
- Do not quietly expand scope under the cover of cleanup

---

**These rules are working if:** fewer unnecessary changes appear in diffs, fewer rewrites happen because of overcomplication, and clarifying questions come *before* implementation rather than after mistakes.
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
│   └── settings.local.json
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

See `docs/architecture.md` for details.

## Code Standards

- TypeScript strict mode, no `any`
- Prettier + ESLint (run on save)
- Conventional commits required
- 80% test coverage minimum

## Shared Working Rules

- Surface assumptions explicitly before proceeding
- Stop on ambiguity and name the confusion
- Touch only the files needed for the requested task
- Run `pnpm test` when behavior changes
- Never commit secrets or production credentials

## Claude Notes

- Put extra topic-specific detail in `.claude/rules/*.md`
- Keep local-only exclusions in `.claude/settings.local.json`

## Codex Notes

- Keep repo-wide instructions in this file
- Add nested `AGENTS.md` files in packages or services that need local context

## AI Tool Notes

This file works with Codex (AGENTS.md) and Claude Code (CLAUDE.md via symlink). Keep `AGENTS.md` as the single source of truth.

- **Claude Code**: Full support for .claude/rules/ and skills
- **Codex CLI**: Reads AGENTS.md and benefits from nested per-directory AGENTS files
- **Cursor**: Copy the shared essentials into Cursor's native config if needed
```

### Setup Script

```bash
#!/bin/bash
# setup-ai-tools.sh - Initialize cross-platform AI memory
#
# Creates the AGENTS.md/CLAUDE.md bridge and the .claude/rules/ directory.
# The behavioral-rules file is intentionally NOT inlined here — copy the
# canonical template from Example 6 in this same file. Inlining here would
# drift the moment Example 6 is updated.

set -e

# Create directories
mkdir -p .claude/rules docs

# Create symlink (CLAUDE.md → AGENTS.md)
touch AGENTS.md
ln -sf AGENTS.md CLAUDE.md

# Create a placeholder for the behavioral rules file.
# You MUST replace the placeholder with the full Example 6 template.
cat > .claude/rules/coding-behavior.md << 'EOF'
# Coding Behavior Rules

> PLACEHOLDER — replace this file with the full template from
> references/memory-examples.md §"Example 6: Behavioral Rules File".
>
> The canonical template is maintained in a single place (Example 6) so
> updates propagate without drift. See the cross-reference note at the
> top of Example 6 for the current version and its source attribution.
EOF

echo "✓ Created AGENTS.md + CLAUDE.md symlink"
echo "✓ Created .claude/rules/coding-behavior.md (PLACEHOLDER)"
echo ""
echo "Next steps:"
echo "  1. Edit AGENTS.md with your project details (use Examples 1-5 as starting points)"
echo "  2. Replace .claude/rules/coding-behavior.md with the full Example 6 template"
echo "  3. Run: diff AGENTS.md CLAUDE.md  (should be empty — same file via symlink)"
```

### Verification

```bash
# Verify symlink
ls -la CLAUDE.md
# Should show: CLAUDE.md -> AGENTS.md

# Verify both files resolve to the same content
diff AGENTS.md CLAUDE.md
# Should show no output (identical)

# Test with Claude Code
claude "What are my behavioral rules?"

# Test with Codex CLI (if installed)
codex "What are my behavioral rules?"
```

---

## Example 8: Prompt / Agent Library Repo

A repository whose primary purpose is storing and maintaining AI prompt files, Custom GPT configs, agent skills, and reusable frameworks — not a product that calls AI APIs.

```markdown
# [Repo Name]

Operational instructions for AI coding agents working in this repository.

## Repo Purpose

This repo is a prompt and agent library with three active areas:

- `custom-gpt/` — ChatGPT Custom GPT prompts and configs
- `ai-agents/` — Agent SDK and agent-specific implementation assets
- `frameworks/` — Reusable development kits and shared skills

Supporting documentation lives in `docs/`.

## Start Here

Read these files first for context and standards:

- `README.md` (repo overview)
- `frameworks/README.md` (framework catalog)
- `frameworks/shared-skills/graph/codex-discovery.md` (compact Codex router map for choosing the right entry point)
- `frameworks/shared-skills/graph/graph.json` (canonical full skill catalog, plus per-router Mermaid in the same dir)
- `.claude/rules/coding-behavior.md` (behavior rules)

## Standard Agent File Pattern

For prompt-based agents in `custom-gpt/` (and similar folders):

1. `01_agent-name.md` — main instruction file
2. `02_sources-agent-name.json` — curated sources
3. `agent-name.yaml` — runtime/config mapping

Optional: `03_supplemental.md`, `0X_data.json`, `sources/` (git-ignored), `.archive/` (git-ignored)

## Platform Constraints

Custom GPT instruction files have a hard limit of 8000 characters.

- Validate with: `wc -c path/to/01_agent-name.md`
- Target 7500–7900 chars for safe margin
- If content still exceeds limit after optimization, split into numbered files

## YAML / Markdown Alignment

When editing any `01_*.md` prompt, keep its sibling YAML aligned:

- `## COMMANDS` in markdown matches YAML `commands` names
- YAML `max_chars` matches the markdown OUTPUT CONTRACT cap
- `framework`, `tone`, and `answer_shape` consistent across md/yaml

Useful checks:

```bash
find . -type f -name '01_*.md' -not -path '*/.archive/*'
rg -n '^## COMMANDS|^## OUTPUT CONTRACT' custom-gpt -g '!**/.archive/**'
rg -n 'name:\s*/|^max_chars:' custom-gpt -g '!**/.archive/**'
```

## Archive and Token Discipline

Do not read or scan `.archive/` directories unless explicitly requested.

- Exclude glob: `**/.archive/**`
- Use: `rg <pattern> -g '!**/.archive/**'`
- Use: `find . -type f ! -path '*/.archive/*'`

## Editing Rules

- Preserve existing safety/precedence/workflow constraints unless task requires changing them
- Keep markdown and yaml style consistent with surrounding files
- YAML uses two-space indentation and lowercase keys
- Do not rename files/directories unless requested
- Do not create summary/report files by default: `SUMMARY.md`, `CHANGELOG.md`, `MIGRATION.md`

## Shared Skills Maintenance

When editing `frameworks/shared-skills/skills/`:

- Treat `frameworks/shared-skills/graph/` as the canonical generated catalog:
  - `codex-discovery.md` is the compact Codex-facing router map
  - `graph.json` is the full machine-readable catalog
  - regenerate both via `scripts/graph-export.py`; gate drift via `scripts/audit-coverage.py --check`
- In root `AGENTS.md`, point agents to `codex-discovery.md` before `graph.json`, and name the primary routers rather than pasting a full skill list
- Keep `frameworks/shared-skills/README.md` and `frameworks/README.md` aligned when skill counts change
- `project-*` skills are independent and self-contained — never cross-link from domain or router skills
- Cross-link only within the same project family (`project-acme-*` can reference each other, not `software-*`)

## Validation Checklist

```bash
# Unresolved placeholders
rg "{{[^}]+}}" custom-gpt -g '!**/.archive/**'

# Command parity
rg -n '^## COMMANDS' custom-gpt -g '!**/.archive/**'
rg -n 'name:\s*/[A-Za-z0-9:_-]+' custom-gpt -g '!**/.archive/**'

# Character cap for Custom GPT prompts
wc -c custom-gpt/**/01_*.md
```
```

**When to use**: Any repository that IS a library of AI prompts, Custom GPT configs, agent skills, or reusable frameworks. Distinct from an application that calls AI APIs.

**What makes this pattern unique**:
- Platform character cap enforcement is a hard constraint absent from all other repo types
- YAML/markdown parity is a first-class concern (broken parity = agent receives wrong affordances)
- Archive exclusion is load-bearing — polluted context causes silent degradation
- Skill cross-linking constraints prevent one of the most common drift patterns in skills libraries

**Use case**: Teams supporting both Codex and Claude Code, wanting consistent AI behavior across all tools without maintaining duplicate documentation.

---

## Example 9: Minimal AGENTS.md + CLAUDE.md Starter

The shortest working template for a brand-new repo. Use this to start from zero, then add stack-specific details incrementally as you notice repeated mistakes. Pairs with [Example 6](#example-6-behavioral-rules-file) for behavioral rules.

**Setup** (run once per repo):

```bash
touch AGENTS.md
ln -sf AGENTS.md CLAUDE.md         # macOS / Linux — same file, two names
mkdir -p .claude/rules
# Copy the Example 6 template into .claude/rules/coding-behavior.md
```

**Contents of `AGENTS.md` (start here, add sections only when you notice repeated mistakes):**

```markdown
# [Project Name]

[One sentence about what this repo does.] Works with Codex (reads `AGENTS.md`) and Claude Code (reads `CLAUDE.md` via symlink to the same file).

## Commands

- `[cmd]` — start dev
- `[cmd]` — run tests
- `[cmd]` — lint / format
- `[cmd]` — typecheck
- `[cmd]` — build

## Boundaries

### Always Do
- Run tests after code changes
- Read existing similar code before writing new code

### Ask First
- Installing new dependencies
- Modifying [critical thing: DB schema, auth, public API, billing]
- Deleting files

### Never Do
- Force-push to `main`
- Commit secrets

## Verification

After code changes:
1. `[test command]`
2. `[lint command]`
3. `[typecheck command]`

After UI changes, verify visually in the browser — tests check code correctness, not UX.

## Behavioral Rules

See `.claude/rules/coding-behavior.md` (Example 6) for assumption surfacing, scope discipline, goal transformation, and dead-code hygiene.

---

**This file is working if:** fewer unnecessary changes in diffs, fewer rewrites from overcomplication, and clarifying questions appear before implementation rather than after mistakes.
```

**When to use**: starting a new repo, or stripping a bloated `AGENTS.md` back to the exception-file baseline. Every line in this template earns its place in the top ~150 lines that research shows agents actually follow. If you add beyond that, something else must go.

**Why this shape**:
- **Commands come first** — "the agent cannot observe or verify its own work without them" is the single highest-impact gap flagged in the main `SKILL.md` §"Feedback Loops". Put them at the top so the agent sees them before anything else.
- **Boundaries come before Verification** — the Always / Ask / Never pattern reduces ambiguity on *every* tool call, not just after code is written. Putting it near the top means the agent sees permission rules before execution rules.
- **Behavioral Rules is a pointer, not inlined** — so the repo stays DRY against Example 6. If you copy Example 6's rules into the root file instead, they will drift the moment either source updates. One canonical location.
- **The working-if line at the bottom** — how you measure whether this file is earning its token cost (see `SKILL.md` §"Measuring Whether Memory Is Working"). Review every few weeks; if diff quality hasn't changed, the file is cosmetic and needs pruning.

**What this template deliberately leaves out**:
- **Architecture descriptions** → belong in `docs/architecture.md`, not project memory (the agent can read them on demand)
- **Directory tours** → inferable by reading the repo
- **Code style rules** → handled by linters/formatters, not memory (the SKILL.md anti-patterns section names this explicitly)
- **Generic advice** ("write clean code", "follow best practices") → wastes instruction budget without changing behavior
- **Long checklists** → will drop agent compliance below the 150–200 instruction threshold measured across 2,500+ repos
- **Tool-specific behavior** (Claude-only imports, Codex-only flags) → put those in `.claude/rules/*.md` or tool configs, not the shared file

**Progression from this template**: start minimal, add sections only when you see a repeated mistake. Each new rule should pass the exception-file test (hard to infer, needed most sessions, prevents repeated mistakes). When the file grows past ~150 lines, move the oldest content into `docs/` or delete it — ruthless pruning matters more than comprehensive coverage.

**Use case**: any new repo, or any existing repo whose `AGENTS.md` has grown into a README-style document the agent no longer follows. The test is simple — if you can't fit the whole root file on one screen, it's too long.
