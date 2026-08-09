# Coordination Repo Layout

```text
portfolio-hub/
├── AGENTS.md
├── CLAUDE.md
├── catalog/
├── profiles/
├── graphs/
├── reports/
├── docs/
│   ├── architecture/
│   ├── domains/
│   └── migrations/
├── schemas/
├── scripts/
└── sources/
```

Design rule:
- generated artifacts live outside the root instruction files
- schemas and scripts are versioned
- architecture docs link to profiles instead of duplicating them

Embedded repo-local variant:

```text
repo/
├── AGENTS.md
├── docs/
│   ├── product/
│   ├── tech/
│   ├── reports/
│   └── context/
│       ├── profiles/
│       ├── catalog/
│       ├── graphs/
│       └── reports/
└── scripts/
```

Use the embedded layout when the repo already has canonical narrative docs and you need generated context artifacts to stay isolated from those hand-authored files.
