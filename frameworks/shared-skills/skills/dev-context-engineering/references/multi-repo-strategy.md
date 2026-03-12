# Multi-Repo Context Strategy

Managing context-driven development across 100+ repositories. Patterns for sharing context, enforcing standards, and coordinating AI agent instructions at scale.

```mermaid
flowchart TD
    AGENTS["AGENTS.md\n(source of truth)"]
    CLAUDE["CLAUDE.md\n(symlink)"]

    AGENTS ---|"ln -s"| CLAUDE

    CC["Claude Code\nreads CLAUDE.md"]
    CX["Codex\nreads AGENTS.md"]

    CLAUDE --> CC
    AGENTS --> CX

    style AGENTS fill:#d4edda,color:#155724
    style CLAUDE fill:#d6eaf8,color:#1b4f72
    style CC fill:#e8daef,color:#4a235a
    style CX fill:#fdebd0,color:#7e5109
```

## Cross-Platform Convention

**AGENTS.md is the primary file.** `CLAUDE.md` is always a symlink:

```bash
ln -s AGENTS.md CLAUDE.md
```

- Codex reads `AGENTS.md` directly
- Claude Code reads `CLAUDE.md` (the symlink)
- One file maintained, zero drift between agents

This convention applies to every repo in the organization.

## Coordination Patterns

Choose one primary coordination pattern based on your organization's structure.

### Pattern 1: Root Coordination Layer (Recommended for Polyrepo)

A dedicated meta-repo holds shared context. Individual repos maintain focused local context.

```
coordination-repo/                    # Shared context (ONE repo)
├── AGENTS.md                         # Org-wide agent instructions (PRIMARY)
├── CLAUDE.md -> AGENTS.md            # Symlink for Claude Code
├── .claude/
│   ├── skills/ -> shared-skills/     # Shared skills (symlink or submodule)
│   ├── rules/
│   │   ├── coding-standards.md       # Org-wide coding conventions
│   │   ├── compliance-fca-emi.md     # FCA/EMI regulatory rules (mandatory)
│   │   ├── data-handling-gdpr-pci.md # GDPR/PCI DSS rules (mandatory)
│   │   ├── security-baseline.md      # Security standards (mandatory)
│   │   └── ai-agent-governance.md    # AI tool restrictions (mandatory)
│   └── settings.json
├── docs/
│   ├── architecture-overview.md      # Cross-repo architecture map
│   └── engineering-standards.md      # Org-wide engineering standards
├── templates/
│   ├── AGENTS.md.template            # Starting point for new repos
│   ├── pr-template.md                # PR template with AI disclosure
│   └── compliance-gate.yml           # CI/CD workflow template
└── scripts/
    ├── clone-repos.sh                # Onboard new developers
    ├── sync-rules.sh                 # Push rule updates to all repos
    ├── validate-repos.sh             # Audit all repos for compliance
    └── setup-symlinks.sh             # Ensure CLAUDE.md symlinks exist
```

```
per-repo/ (each of 100 repos)
├── AGENTS.md                         # Repo-specific context (PRIMARY)
├── CLAUDE.md -> AGENTS.md            # Always symlinked, never separate
├── .claude/
│   └── rules/                        # Repo-specific rules only
│       └── domain-patterns.md        # Tech/domain-specific rules
├── docs/
│   ├── specs/                        # Feature specifications
│   └── plans/                        # Implementation plans
└── ...
```

**How it works**:
1. Developer clones coordination repo alongside work repos
2. `claude --add-dir ../coordination-repo` loads shared context into sessions
3. Shared rules supplement (not replace) repo-local rules
4. Updates to shared rules go through PR review in coordination repo

### Pattern 2: Template Repository + Sync

GitHub template repo with `.claude/`, `AGENTS.md`, CI workflows. New repos start from template; updates propagated via sync workflow.

```yaml
# .github/workflows/template-sync.yml
name: Sync from template
on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6am
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Sync mandatory rules
        run: |
          # Pull latest mandatory rules from template repo
          git clone --depth 1 https://github.com/org/template-repo /tmp/template
          cp /tmp/template/.claude/rules/compliance-*.md .claude/rules/
          cp /tmp/template/.claude/rules/data-handling-*.md .claude/rules/
          cp /tmp/template/.claude/rules/ai-agent-governance.md .claude/rules/
          # Do NOT overwrite repo-specific AGENTS.md or local rules
      - name: Create PR if changes
        run: |
          if [ -n "$(git status --porcelain)" ]; then
            git checkout -b template-sync-$(date +%Y%m%d)
            git add .claude/rules/
            git commit -m "chore: sync mandatory rules from template"
            gh pr create --title "Sync mandatory rules" --body "Automated sync from template repo"
          fi
```

**Best for**: Organizations that want automated propagation without `--add-dir`.

### Pattern 3: Workspace-Level Context

Claude Code `--add-dir` loads shared context from a coordination repo at session start.

```bash
# Developer workflow
claude --add-dir ~/work/coordination-repo --add-dir ~/work/service-repo

# Or via shell alias
alias cc-service='claude --add-dir ~/work/coordination-repo'
cc-service  # Start session with shared context pre-loaded
```

**Best for**: Small organizations (5-20 repos) where a full coordination repo feels heavy.

### Pattern 4: Centralized MCP Toolshed (from Stripe)

A single MCP server aggregates 400+ tools spanning internal systems and SaaS platforms. Agents connect to one endpoint and get access to documentation, ticket details, build statuses, code intelligence, and more.

```
┌─────────────────────────────────────┐
│         Toolshed (MCP Server)       │
│  ┌──────────┐ ┌──────────────────┐  │
│  │ Internal │ │ Code Intelligence│  │
│  │   Docs   │ │  (Sourcegraph)   │  │
│  └──────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────────┐  │
│  │  Ticket  │ │  Build/CI Status │  │
│  │ Systems  │ │                  │  │
│  └──────────┘ └──────────────────┘  │
└──────────────┬──────────────────────┘
               │ MCP protocol
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 Agent A    Agent B    Agent C
(Service X) (Service Y) (Service Z)
```

**Key patterns from Stripe**:
- **Pre-hydration**: Deterministically run relevant MCP tools on linked resources *before* agent starts (faster than agent-driven exploration)
- **Curated access**: Agents get a subset of tools relevant to their task, not all 400+
- **Agent rule files**: Conditional rules by subdirectory — same formats as Cursor/Claude Code
- **Scale result**: 1,000+ merged PRs per week across hundreds of millions of LOC

**Best for**: Large organizations (50+ repos) with centralized platform teams who can maintain the MCP server. Requires investment but provides the richest context.

**Combining patterns**: Stripe's Toolshed (Pattern 4) complements the Coordination Repo (Pattern 1). Use Pattern 1 for static context (rules, AGENTS.md templates) and Pattern 4 for dynamic context (ticket details, build status, code search).

### GitHub Agent HQ (Feb 2026)

GitHub's Agent HQ provides a platform-level coordination layer. Claude and Codex run as first-class agents within GitHub's security perimeter:

**Enterprise AI Controls (GA Feb 2026):**
- **Audit logging**: `actor_is_agent` identifier on every action, `agent_session.task` events tracking session lifecycle
- **Custom agent definitions**: Protected `.github/agents/*.md` files with enterprise-wide push rules
- **MCP enterprise allowlists**: Centralized registry URL for approved MCP servers across all repos
- **Programmatic management**: APIs for enterprise-wide agent configuration and policy enforcement
- **Session visibility**: 24-hour cloud agent session history without record limits

**Multi-agent on GitHub:**
- Assign Claude and Codex to the same task for comparative analysis
- Surface competing architectural approaches and edge cases
- Review different solutions side-by-side within existing PR workflows
- Draft PRs created by agents integrate into standard review process

**Relationship to Coordination Patterns:**
Agent HQ complements (does not replace) the coordination repo. Use Agent HQ for:
- Platform-level governance (audit logs, permissions, MCP allowlists)
- Agent execution and PR creation

Use the coordination repo for:
- Shared context (AGENTS.md, rules, skills)
- Cross-repo standards and compliance rules
- Developer workstation setup (`--add-dir`)

### VS Code Context Engineering Patterns

VS Code's context engineering guide (March 2026) introduces complementary context files alongside AGENTS.md:

**Three-step workflow:**
1. **Custom instructions** (`.github/copilot-instructions.md`) — project-wide context loaded into all chat interactions
2. **Planning agents** (`.github/agents/plan.agent.md`) — persona-driven planning with tool access and handoffs
3. **Implementation agents** (`.github/agents/implement.agent.md`) — code generation following validated plans

**Relationship to AGENTS.md:**
These patterns converge with AGENTS.md rather than competing:
- `AGENTS.md` = agent-agnostic instructions (Claude Code, Codex, any agent)
- `.github/copilot-instructions.md` = Copilot-specific context (VS Code, GitHub)
- `.github/agents/*.md` = Agent skill definitions (VS Code agent mode)

**For multi-repo organizations**, standardize all three via the coordination repo template, ensuring agents get consistent context regardless of which platform invokes them.

## Shared vs Local Context

### Mandatory Context (All 100 repos)

These files MUST exist in every repo. Non-negotiable for regulated organizations:

| File | Purpose | Enforcement |
|------|---------|-------------|
| `AGENTS.md` | Agent instructions (primary) | CI check: file exists |
| `CLAUDE.md` | Symlink to AGENTS.md | CI check: is symlink |
| `.claude/rules/compliance-fca-emi.md` | FCA/EMI audit trail, separation of duties | Template sync |
| `.claude/rules/data-handling-gdpr-pci.md` | GDPR/PCI safe/prohibited data | Template sync |
| `.claude/rules/ai-agent-governance.md` | AI tool restrictions, disclosure | Template sync |

### Recommended Context (Most repos)

| File | Purpose | When to skip |
|------|---------|-------------|
| `.claude/rules/coding-standards.md` | Code style, patterns | Archived repos |
| `.claude/rules/commit-conventions.md` | Commit message format | Archived repos |
| `.github/pull_request_template.md` | PR template with AI disclosure | Internal-only repos |

### Local-Only Context (Per-repo)

| File | Purpose | Examples |
|------|---------|---------|
| AGENTS.md body | Repo-specific instructions | "This is a Next.js app using Prisma..." |
| `.claude/rules/domain-*.md` | Domain patterns | Payment flows, auth patterns |
| `.claude/agents/*.md` | Specialized subagents | Test writer, migration helper |
| `docs/architecture.md` | Repo architecture | Service boundaries, data flow |

## Distribution Mechanisms

| Mechanism | Pros | Cons | Best For |
|-----------|------|------|----------|
| **Git submodule** | Version-pinned, explicit updates | Requires `git submodule update` | Strict version control |
| **Symlinks** | Fast, no extra tooling | Fragile on Windows, path-dependent | Unix-only teams |
| **NPM/package** | Semver, familiar tooling | Overhead for non-JS repos | JS/TS monorepos |
| **CI/CD sync** | Automated, auditable | PR noise, delayed propagation | Regulated environments |
| **`--add-dir`** | Zero setup per repo | Requires coordination repo clone | Developer workstations |
| **Template sync** | Automated PR creation | Requires merging sync PRs | Large orgs with many repos |

### Recommended combination for regulated orgs
1. **CI/CD sync** for mandatory compliance rules (automated, auditable)
2. **`--add-dir`** for shared skills and coding standards (developer convenience)
3. **Template repo** for new repo bootstrapping (consistent starting point)

## Token Budget at Scale

Context has a cost. Budget it:

| Context Layer | Approximate Tokens | Notes |
|--------------|-------------------|-------|
| Shared rules (mandatory) | ~2,000 | Compliance + data handling + governance |
| Shared rules (recommended) | ~1,500 | Coding standards + commit conventions |
| Repo AGENTS.md | ~500-2,000 | Varies by repo complexity |
| Skills discovery | ~500 | Skill router overhead |
| **Workspace overhead** | **~4,500-6,000** | Before any task-specific context |
| Available for work | ~144,000-195,000 | Depends on model context window |

### Optimization strategies
- **Progressive disclosure**: Load detailed rules only when relevant (use rule file names as triggers)
- **Scoped AGENTS.md**: Keep top-level brief, use subdirectory AGENTS.md for deep context
- **Sub-agent isolation**: Heavy research in subagents (separate context windows)
- **RAG patterns**: For repos with extensive documentation, summarize in AGENTS.md, link to full docs

### Cost estimation (100 repos, 20 developers)

```
Per session: ~5K tokens overhead + ~50K tokens work = ~55K tokens
Sessions per developer per day: ~10
Daily org total: 20 devs x 10 sessions x 55K = 11M tokens/day
Monthly: ~220M tokens (input) + ~40M tokens (output)
```

## Sync Scripts

### Validate all repos for compliance

```bash
#!/bin/bash
# validate-repos.sh — Run from parent directory containing all repos
MANDATORY_FILES=(
  "AGENTS.md"
  ".claude/rules/compliance-fca-emi.md"
  ".claude/rules/data-handling-gdpr-pci.md"
  ".claude/rules/ai-agent-governance.md"
)

pass=0; fail=0; total=0

for repo in */; do
  [ ! -d "$repo/.git" ] && continue
  total=$((total + 1))
  repo_pass=true

  for file in "${MANDATORY_FILES[@]}"; do
    if [ ! -f "$repo/$file" ]; then
      echo "MISSING: $repo$file"
      repo_pass=false
    fi
  done

  # Check CLAUDE.md is a symlink
  if [ -f "$repo/CLAUDE.md" ] && [ ! -L "$repo/CLAUDE.md" ]; then
    echo "NOT SYMLINK: ${repo}CLAUDE.md (should be ln -s AGENTS.md CLAUDE.md)"
    repo_pass=false
  fi

  if $repo_pass; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
  fi
done

echo ""
echo "Results: $pass/$total repos compliant ($fail non-compliant)"
```

### Push mandatory rules to all repos

```bash
#!/bin/bash
# sync-rules.sh — Push mandatory rules from coordination repo to all repos
COORDINATION_REPO="./coordination-repo"
MANDATORY_RULES=(
  "compliance-fca-emi.md"
  "data-handling-gdpr-pci.md"
  "ai-agent-governance.md"
)

for repo in repos/*/; do
  [ ! -d "$repo/.git" ] && continue
  name=$(basename "$repo")

  # Ensure .claude/rules/ exists
  mkdir -p "$repo/.claude/rules"

  # Copy mandatory rules
  for rule in "${MANDATORY_RULES[@]}"; do
    cp "$COORDINATION_REPO/.claude/rules/$rule" "$repo/.claude/rules/$rule"
  done

  # Ensure CLAUDE.md symlink
  if [ ! -L "$repo/CLAUDE.md" ]; then
    (cd "$repo" && ln -sf AGENTS.md CLAUDE.md)
  fi

  echo "Synced: $name"
done
```

## InnerSource Governance

For organizations managing shared context at scale:

### Context Curation Guild
- **Members**: 1 engineering lead per team + security + compliance + platform
- **Cadence**: Monthly review of shared rules and skills
- **Authority**: Approve/reject changes to mandatory rules in coordination repo
- **CODEOWNERS**: `.claude/rules/compliance-*` owned by compliance team

### Change Management
- **Mandatory rules**: Require 2 approvals (engineering + compliance)
- **Recommended rules**: Require 1 approval (engineering lead)
- **Local rules**: Team discretion (no cross-team review)
- **Breaking changes**: Announced 2 weeks before propagation, major version bump

### Quarterly Context Audit
1. Review context freshness: `git log --since="90 days" -- AGENTS.md .claude/`
2. Identify stale rules (no updates in 6+ months with active repo)
3. Measure rule compliance rate across repos
4. Survey developers: "Which rules helped? Which were noise?"
5. Retire low-value rules, update outdated ones

### Skill Usage Metrics
- Track which skills are invoked (if instrumented)
- Retire skills with <5% usage over a quarter
- Promote high-usage skills to mandatory/recommended

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| **God coordination repo** | 5000+ line AGENTS.md covering everything | Keep coordination AGENTS.md to org-wide concerns only |
| **Copy-paste rules** | Same rules duplicated across 100 repos | Use sync mechanism, single source of truth |
| **Divergent symlinks** | CLAUDE.md and AGENTS.md contain different content | Enforce symlink check in CI |
| **Manual sync** | "Remember to copy rules when they change" | Automate with CI/CD sync workflow |
| **No local context** | Repos rely entirely on coordination repo | Each repo needs its own AGENTS.md with repo-specific content |
| **Over-syncing** | Every rule synced to every repo | Distinguish mandatory (sync) vs recommended (opt-in) |

## Related References

- **maturity-model.md** — Assess readiness before scaling
- **regulated-environment-patterns.md** — Compliance rules that must be synced
- **fast-track-guide.md** — Batch onboarding for 100 repos
- **context-development-lifecycle.md** — The CDLC feedback loop at scale
