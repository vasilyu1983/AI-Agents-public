# Skill Patterns

Common patterns for organizing and structuring agent skills.

## Pattern 1: Single-Domain Skill

For skills focused on one technology or concept.

```text
skill-name/
├── SKILL.md           # Core patterns + quick reference
├── data/
│   └── sources.json   # Official docs, tutorials
└── references/
    └── advanced.md    # Edge cases, deep dives
```

**When to use**: Technology-specific skills (e.g., `testing-playwright`, `document-pdf`)

## Pattern 2: Multi-Tech Skill

For skills covering multiple implementations of same concept.

```text
software-backend/
├── SKILL.md              # Decision tree + common patterns
├── data/
│   └── sources.json
├── references/
│   ├── nodejs-patterns.md
│   ├── python-patterns.md
│   ├── go-patterns.md
│   └── rust-patterns.md
└── assets/
    ├── nodejs/
    ├── python/
    ├── go/
    └── rust/
```

**When to use**: Skills with framework/language variants

## Pattern 3: Workflow Skill

For skills that guide multi-step processes.

```text
dev-workflow-planning/
├── SKILL.md              # Workflow overview + decision points
├── references/
│   ├── phase-1-discovery.md
│   ├── phase-2-design.md
│   ├── phase-3-implementation.md
│   └── phase-4-review.md
└── assets/
    ├── planning-checklist.md
    └── review-template.md
```

**When to use**: Process-oriented skills (planning, review, deployment)

## Pattern 4: Reference Skill

For skills that primarily provide lookup information.

```text
data-sql-optimization/
├── SKILL.md              # Quick syntax reference
├── data/
│   └── sources.json
└── references/
    ├── postgres-specifics.md
    ├── mysql-specifics.md
    ├── optimization-patterns.md
    └── common-queries.md
```

**When to use**: Reference materials, syntax guides, cheat sheets

## Pattern 5: Script Execution

Skills can bundle executable scripts that the assistant can run instead of generating large code blocks.

### When to Execute vs Read

| Approach | Use When | Example |
|----------|----------|---------|
| **Execute** | Utility tasks, validation, data processing | `Run scripts/validate.py` |
| **Read as reference** | Complex algorithms to understand | `See scripts/algorithm.py for logic` |

### Script Execution Pattern

```text
skill-name/
├── SKILL.md
└── scripts/
    ├── validate.py      # Assistant runs this
    ├── generate.sh      # Assistant runs this
    └── complex_algo.py  # Assistant reads this when needed
```

**In SKILL.md**:

```markdown
## Validation
Run `scripts/validate.py <input>` to check format.

## Algorithm Reference
See `scripts/complex_algo.py` for the scoring algorithm logic.
```

**Key benefit**: Script output consumes tokens, but script code does NOT load into context. More efficient than generating equivalent code.

## File Naming Best Practices

| Rule | Good | Bad |
|------|------|-----|
| Descriptive names | `form_validation_rules.md` | `doc2.md` |
| Forward slashes | `references/guide.md` | `references\guide.md` |
| Organize by domain | `references/auth/`, `references/api/` | All files flat |

## SKILL.md Content Patterns

### Quick Reference Table

Always include at top for fast lookup:

```markdown
| Task | Command/Pattern | Notes |
|------|-----------------|-------|
| Create X | `code example` | When to use |
| Debug Y | `another example` | Common pitfall |
```

### Decision Tree

For multi-option skills:

```markdown
## Choosing the Right Approach

**Need real-time updates?**
-> Yes: Use WebSockets (`references/websockets.md`)
-> No: Use REST (`references/rest-patterns.md`)

**High throughput required?**
-> Yes: Consider Go or Rust
-> No: Node.js or Python sufficient
```

### Trigger Keywords

Include in description for better discovery:

```yaml
description: Backend API development with Node.js, Express, Fastify, REST, GraphQL, authentication, database integration, and microservices patterns.
```

## Anti-Patterns

### Too Broad

```yaml
# BAD: Too vague, triggers on everything
name: programming
description: Help with programming tasks
```

### Too Narrow

```yaml
# BAD: Too specific, rarely triggers
name: express-middleware-error-handling-async
description: Handle async errors in Express middleware
```

### Missing Context

```yaml
# BAD: No trigger words, poor discovery
name: backend
description: Backend development
```

### Good Balance

```yaml
# GOOD: Specific domain with clear triggers
name: software-backend
description: Backend API development with Node.js, Python, Go, or Rust including REST/GraphQL APIs, authentication, database integration, and deployment patterns.
```

## Related

- [skill-validation.md](skill-validation.md) - Validation criteria
- [../SKILL.md](../SKILL.md) - Main skill reference
