# Agent Delivery Methods

Practical comparison of the delivery methods and planning systems that matter for AI-assisted coding work in March 2026.

Use this reference when you need to choose how much structure, review, and governance to add around coding agents. Do not treat these methods as interchangeable agent runtimes. Most of them are delivery systems layered on top of existing agent tools.

## Table Of Contents

- [Method Map](#method-map)
- [Popularity Ranking (March 2026)](#popularity-ranking-march-2026)
- [Cross-Cutting Practices](#cross-cutting-practices)
- [Patterns Worth Reusing](#patterns-worth-reusing)
- [Selection Guide](#selection-guide)
- [Layering Guide](#layering-guide)
- [Adoption Rule](#adoption-rule)
- [Primary Sources](#primary-sources)

## Method Map

| Method | Type | Core Artifacts | Best Fit | Main Caution |
|---|---|---|---|---|
| **Get Shit Done (GSD)** | Lightweight delivery workflow | Discussion notes, plan files, phase state | Solo builders and brownfield work that needs speed without losing state | Less formal governance than team-oriented systems |
| **BMAD Method / BMAD v6** | Role-based workflow and Agent-as-Code delivery system | Role chain, blueprints, policies, replayable runs | Teams that want stronger planning, verification, and auditable execution | More ceremony; v6 is still alpha |
| **GitHub Spec Kit** | Spec-driven development toolkit | Constitution, spec, clarify output, plan, tasks | Teams that want explicit handoff from intent to implementation | Heavier artifact flow than lighter tools |
| **OpenSpec** | Lightweight spec layer | Proposal, design, tasks, spec deltas | Repo-native planning with less ceremony than full SDD systems | Lighter governance and enforcement by design |
| **MADD** | Multi-agent delivery methodology | Intention docs, contracts, retro-spec, independent audit | High-risk work where self-validation bias is the main failure mode | Requires more orchestration discipline |
| **AI-SDLC** | Governance and orchestration layer | Declarative policy, gates, reconciliation state | Enterprises that need audit, policy, and quality gates across agent runs | Not a replacement for a day-to-day delivery workflow |
| **Kiro** | Spec-driven IDE (Amazon) | Requirements, design docs, task lists | AWS-native teams wanting structured agent workflows inside an IDE | Vendor-locked to Kiro IDE; spec lifecycle is IDE-managed |
| **TaskMaster** | AI task management via MCP | PRD → structured tasks with dependencies and complexity scores | Teams that want automated task decomposition from PRDs, works across Cursor/Claude Code/Windsurf | Task management layer, not a full delivery workflow |
| **Ralph Loop** | Autonomous agent loop pattern | PRD, loop state, iteration history | Long-running autonomous work (documented: 37h, 250 tasks from 2000-line PRD) | Requires strong acceptance criteria; unbounded loops risk runaway cost |
| **Agent OS** | Standards injection system | Codebase standards, spec shaping, standard index | Teams wanting to extract and enforce existing codebase conventions across agent work | v3 defers spec writing to Plan Mode; not a standalone delivery system |
| **Superpowers** | Discipline-enforcing workflow plugin | TDD skills, brainstorming, debugging, code review, subagent dispatch | Teams that want enforced engineering discipline (TDD, design-before-code, mandatory review) baked into the agent | Claude Code only; opinionated — deletes code written before tests |
| **Tessl Framework** | Spec-as-source SDD platform | Specs, vibe-specs, spec registry, spec deltas | Teams pursuing spec-as-source — specs are the primary artifact, code is generated to match | Closed beta; most aggressive SDD stance — requires buy-in to spec-first culture |
| **JetBrains Central** | Enterprise agent orchestration platform | Agent connections to repos, pipelines, infra, knowledge bases | Enterprise teams wanting unified agent management across JetBrains toolchain | EAP Q2 2026; not yet generally available |

## Popularity Ranking (March 2026)

Ranked by GitHub stars as a proxy for developer adoption. Stars are approximate and change daily.

| # | Method | GitHub Stars | Type | Trend |
|---|--------|-------------|------|-------|
| 1 | **Superpowers** | ~107K | Discipline plugin | Fastest-growing; ~2K stars/day |
| 2 | **GitHub Spec Kit** | ~75K | Spec-driven toolkit | Strong; GitHub-backed |
| 3 | **BMAD Method** | ~37K | Role-based workflow | Steady growth; enterprise adoption |
| 4 | **GSD** | ~35K | Lightweight workflow | Rapid; ~4.5K stars/week |
| 5 | **OpenSpec** | ~28K | Lightweight spec layer | Steady; community-driven |
| 6 | **TaskMaster** | ~25K | Task management | Mature; 90+ releases |
| 7 | **Ralph Loop** | ~10K | Autonomous loop | Niche but viral pattern |
| 8 | **Agent OS** | ~3K (est.) | Standards injection | Smaller community; v3 refocus |
| 9 | **Kiro** | N/A (proprietary IDE) | Spec-driven IDE | Amazon-backed; closed-source |
| 10 | **Tessl** | N/A (closed beta) | Spec-as-source | Funded startup; Martin Fowler coverage |
| 11 | **MADD** | <1K (est.) | Multi-agent methodology | Niche; methodology-focused |
| 12 | **AI-SDLC** | <1K (est.) | Governance layer | Niche; enterprise governance |
| 13 | **JetBrains Central** | N/A (EAP Q2 2026) | Enterprise orchestration | Pre-release; JetBrains-backed |

**Reading the ranking:** Stars measure awareness, not quality. Superpowers leads because it's a plugin (low adoption friction) installed via one command. Spec Kit benefits from GitHub's distribution. The most *methodologically complete* systems (BMAD, MADD, AI-SDLC) have fewer stars because they require more commitment. Match by your failure mode, not by star count.

## Cross-Cutting Practices

These are not delivery methods — they layer on top of any method above.

| Practice | What It Does | When to Add | Key Reference |
|----------|-------------|-------------|---------------|
| **Targeted test context (TDAD)** | Provides agents with source→test dependency maps instead of generic "write tests" instructions | Any coding agent work; reduces regressions by ~70% vs. procedural TDD prompting alone | [arXiv:2603.17973](https://arxiv.org/abs/2603.17973) |
| **Classic TDD** | Write failing test → implement → pass → refactor | When the task genuinely starts from a behavioral specification; pair with TDAD for best results | Agentic Coding Handbook |
| **Independent audit** | Separate agent reviews implementation it did not write | High-risk changes, security-sensitive code, compliance work | MADD pattern |
| **Collaborative debate** | Multi-persona discussion before fan-out to resolve tradeoffs | Architecture decisions affecting multiple workers | BMAD Party Mode; templates in `agents-subagents/assets/templates/debate-*` |
| **Fresh-context spawning** | Each worker gets a clean context with only its task brief | Any parallel or long-running agent work to prevent context rot | GSD thin orchestrator |
| **Durable file-based state** | Plans, progress, decisions persist in repo files (YAML frontmatter + markdown) | Any work spanning multiple sessions or agent restarts | GSD, BMAD, OpenSpec |
| **Enforced TDD + review** | Plugin deletes code written before tests; mandatory code review after implementation | When discipline enforcement matters more than developer freedom | Superpowers plugin |

## Patterns Worth Reusing

You do not need to adopt a method wholesale to benefit from it.

- **Scale-adaptive planning**: use lightweight planning for bounded fixes and deeper spec-first planning for migrations, multi-service work, and risky changes.
- **Plan -> build -> verify boundaries**: freeze the intended outcome before implementation, then verify against explicit acceptance checks rather than "looks good."
- **Versioned agent definitions**: keep roles, constraints, tool access, and success criteria in reviewable artifacts rather than one-off chat prompts.
- **Fresh-context workers**: spawn workers with only the task brief, ownership boundaries, and interface contracts they need.
- **Durable external state**: keep plans, decisions, progress, and dependency outputs in repo files rather than in conversational memory.
- **Collaborative debate before fan-out**: resolve architecture or tradeoff disputes before dispatching parallel workers.
- **Independent validation**: separate implementation from audit when the change is risky enough that self-review is not trustworthy.
- **Declarative policy and replay**: add run manifests, policy gates, and replay when governance or compliance matters more than raw speed.

## Selection Guide

### Solo or small brownfield work

Default to:

- GSD when you want speed plus durable state
- OpenSpec when you want visible repo artifacts and low ceremony
- Superpowers when you want enforced TDD discipline and mandatory review on Claude Code
- Ralph Loop when work is long-running and autonomous with a clear PRD
- classic TDD + TDAD test context on top

### Small product team

Default to:

- Spec Kit when the team benefits from explicit requirement and plan artifacts
- BMAD when role separation, verification, and traceability matter more than minimal ceremony
- OpenSpec when the team wants a lighter repo-native planning layer
- TaskMaster when the team wants automated PRD → task decomposition across multiple agent tools
- Agent OS when codebase conventions need to be extracted and enforced consistently

### Spec-as-source teams

Default to:

- Tessl when specs are the primary artifact and code is generated to match them
- Kiro when the team wants spec-driven workflows inside an IDE with tight AWS integration

### JetBrains-native enterprise teams

Default to:

- JetBrains Central when the team needs unified agent orchestration across JetBrains IDEs and CI (EAP Q2 2026)

### High-risk or compliance-heavy delivery

Default to:

- BMAD or Spec Kit for the delivery structure
- MADD-style independent audit for high-risk changes
- AI-SDLC when you need org-level policy, gates, reconciliation, and audit trails

### Long-running autonomous execution

Default to:

- Ralph Loop for unbounded iteration toward a PRD (set cost/time caps)
- GSD for bounded autonomous work with wave-based parallelism
- Both benefit from TDAD test context to prevent regression accumulation over many iterations

## Layering Guide

Methods compose. Pick a delivery workflow, then add cross-cutting practices as needed.

```text
┌──────────────────────────────────────────────────────────────────┐
│                       GOVERNANCE LAYER                            │
│       AI-SDLC │ JetBrains Central (policy, audit, replay)        │
├──────────────────────────────────────────────────────────────────┤
│                       DELIVERY WORKFLOW                           │
│  GSD │ BMAD │ Spec Kit │ OpenSpec │ Kiro │ Ralph Loop │ Tessl   │
├──────────────────────────────────────────────────────────────────┤
│                     CROSS-CUTTING PRACTICES                       │
│  TDAD test context │ Fresh-context │ Collaborative debate         │
│  Durable state │ Independent audit │ Classic TDD │ Enforced TDD  │
├──────────────────────────────────────────────────────────────────┤
│                       TASK MANAGEMENT                             │
│         TaskMaster │ Agent OS │ Plan Mode │ Superpowers           │
├──────────────────────────────────────────────────────────────────┤
│                       AGENT RUNTIME                               │
│   Claude Code │ Cursor │ Codex │ Windsurf │ Copilot │ Kiro IDE   │
└──────────────────────────────────────────────────────────────────┘
```

Typical combinations:

| Profile | Delivery | Cross-Cutting | Task Layer | Runtime |
|---------|----------|---------------|------------|---------|
| Solo hacker | GSD | TDAD + fresh-context | Plan Mode | Claude Code |
| Solo disciplined | GSD | Enforced TDD + TDAD | Superpowers | Claude Code |
| Startup team | Spec Kit or BMAD | TDAD + debate + durable state | TaskMaster | Cursor or Claude Code |
| Spec-as-source | Tessl | TDAD + durable state | Built-in | Any |
| Enterprise | BMAD + AI-SDLC | All practices + independent audit | TaskMaster | Any |
| JetBrains enterprise | BMAD + JetBrains Central | All practices + independent audit | Built-in | JetBrains IDEs |
| Autonomous run | Ralph Loop or GSD | TDAD + fresh-context + durable state | Built-in | Claude Code or Codex |

## Adoption Rule

Adopt the smallest method that fixes your actual failure mode:

- if the problem is **scope ambiguity**, use spec-driven methods (Spec Kit, BMAD, Kiro)
- if the problem is **context drift**, use fresh-context workers plus durable external state (GSD pattern)
- if the problem is **regressions**, add TDAD test context before adding more process
- if the problem is **self-review bias**, add independent audit (MADD pattern)
- if the problem is **task decomposition**, add TaskMaster or Agent OS
- if the problem is **policy and audit**, add declarative governance (AI-SDLC)
- if the problem is **long-running execution**, add Ralph Loop with cost/time caps
- if the problem is **agent discipline** (skipping tests, writing code before design), add Superpowers enforced TDD
- if the problem is **spec drift** (code diverging from intent over time), use Tessl spec-as-source

Avoid copying the full ceremony of a method when only one pattern is needed.

## Primary Sources

- GSD: <https://github.com/gsd-build/get-shit-done>
- BMAD Method docs: <https://docs.bmad-method.org/>
- BMAD v6 Alpha: <https://bmadcodes.com/v6-alpha/>
- GitHub Spec Kit: <https://github.com/github/spec-kit>
- OpenSpec: <https://openspec.dev/>
- OpenSpec repo: <https://github.com/Fission-AI/OpenSpec>
- MADD: <https://madd.sh/>
- AI-SDLC primer: <https://ai-sdlc.io/docs/spec/primer>
- Kiro: <https://kiro.dev/>
- TaskMaster: <https://www.task-master.dev/>
- Ralph Loop: <https://github.com/snarktank/ralph>
- Agent OS: <https://buildermethods.com/agent-os>
- Agent OS repo: <https://github.com/buildermethods/agent-os>
- TDAD paper: <https://arxiv.org/abs/2603.17973>
- SDD ecosystem map (30+ frameworks): <https://medium.com/@visrow/spec-driven-development-is-eating-software-engineering-a-map-of-30-agentic-coding-frameworks-6ac0b5e2b484>
- SDD tools comparison (Martin Fowler): <https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html>
- Agentic Coding Handbook (TDD chapter): <https://tweag.github.io/agentic-coding-handbook/WORKFLOW_TDD/>
- Superpowers: <https://github.com/obra/superpowers>
- Superpowers (Anthropic plugin page): <https://claude.com/plugins/superpowers>
- Tessl Framework: <https://tessl.io/>
- Tessl SDD docs: <https://docs.tessl.io/use/spec-driven-development-with-tessl>
- JetBrains Central announcement: <https://blog.jetbrains.com/blog/2026/03/24/introducing-jetbrains-central-an-open-system-for-agentic-software-development/>
