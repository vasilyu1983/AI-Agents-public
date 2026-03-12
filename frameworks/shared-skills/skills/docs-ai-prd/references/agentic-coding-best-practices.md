# Agentic Coding Best Practices

*Purpose: Operational guide for running AI agentic coding workflows and delivering production-ready results with coding agents (Claude Code, Copilot, Cursor, etc).*

*Updated: January 2026*

---

## Context Engineering (2026)

**Context engineering** has superseded prompt engineering as the key discipline for AI coding. It focuses on providing the right information in the right format at the right time.

### Three Pillars of Context Engineering

1. **Project Architecture Knowledge** - Class hierarchies, frameworks, design patterns (stored in CLAUDE.md/AGENTS.md)
2. **Product Requirements Documentation** - Clear specs from user stories and PRDs
3. **Deep Technical Knowledge** - Specialized understanding of core technologies

### Context File Locations by Tool

| Tool | Location | Notes |
|------|----------|-------|
| Claude Code | `CLAUDE.md`, `.claude/` | Auto-loaded at session start |
| Cursor | `.cursor/rules/`, `.cursorrules` | Project-specific rules |
| Windsurf | `.windsurf/rules/` | Cascade context |
| Copilot | `.github/copilot-instructions.md` | Workspace context |
| Cline | `.cline/`, `.clinerules` | Project rules |
| Generic | `AGENTS.md` | Tool-agnostic fallback |

### Just-in-Time Context

Rather than pre-loading all context, maintain lightweight identifiers and load data dynamically:

- Store file paths, stored queries, web links as references
- Load full content into context only when needed
- Reduces token usage and improves focus

---

## Session Continuity Patterns

### Problem

Agents forget everything between sessions. Starting a new chat means the agent doesn't know you refactored the authentication module yesterday.

### Solution: Session Logging

Instruct agents to log sessions and update documentation:

```markdown
## Session Log Pattern

At end of each session, update CLAUDE.md with:
- What was changed (files, functions, APIs)
- Why it was changed (rationale, requirements)
- What's next (TODOs, blockers, decisions needed)
```

### Implementation Checklist

- [ ] Create `## Recent Changes` section in CLAUDE.md
- [ ] Log significant changes with date and rationale
- [ ] Update architectural decisions when patterns change
- [ ] Document new gotchas discovered during implementation
- [ ] Clear old entries after 30 days

---

## Compaction Strategies

When conversations near context window limits, use compaction:

### Manual Compaction

1. Summarize conversation so far
2. Extract key decisions and code changes
3. Start new conversation with summary as context

### Automatic Compaction (Claude Code)

Claude Code handles compaction automatically, but you can optimize:

- Keep CLAUDE.md under 500 lines
- Move detailed context to linked files
- Use progressive disclosure (summary → details on demand)

---

## Parallel Agent Workflows

### Multi-Agent Patterns (2026)

Modern tools support multiple agents working simultaneously:

| Tool | Feature | Use Case |
|------|---------|----------|
| Copilot | Coding Agent | Assign GitHub issues for autonomous work |
| Cursor | Background Agents | Multiple tasks in parallel |
| Claude Code | Task tool | Launch subagents for specific work |

### Orchestration Pattern

```text
1. Define clear task boundaries
2. Assign independent tasks to parallel agents
3. Merge results with human review
4. Resolve conflicts in integration phase
```

### When to Parallelize

- Independent features with no shared state
- Test writing (separate from implementation)
- Documentation updates
- Refactoring different modules

### When NOT to Parallelize

- Tightly coupled code changes
- Database schema migrations
- API contract changes
- Security-critical modifications

---

## Core Patterns

### Pattern 1: Agentic Coding Four-Phase Workflow

**Use when:** Any non-trivial coding project involving LLM/agent output, especially for multi-file changes, PRDs/specs, or production features.

**Structure:**
1. **Planning** – Enter planning mode, define all phases, risks, metrics.
2. **Implementation** – Work in increments, mark tasks complete as you go, review after each section.
3. **Validation** – Run all tests, perform acceptance review, QA by both agent and human.
4. **Handoff** – Summarize, document, update next steps.

**Checklist:**
- [ ] Planning mode activated for >3 files or >2 unknowns
- [ ] Documented plan: executive summary, phases, risks, metrics, timeline
- [ ] Tasks explicitly tracked and marked complete
- [ ] Periodic context/doc updates before compaction or session switch
- [ ] Agentic QA review at phase boundaries

---

### Pattern 2: Incremental Implementation

**Use when:** Breaking down complex features, multi-step code changes, or agentic session chains.

**Structure:**
- Implement 1–2 sections at a time
- Mark tasks complete instantly
- Request agentic review at each phase

**Checklist:**
- [ ] Only current phase implemented (no "do the whole plan")
- [ ] Agent/human review before next phase
- [ ] Tasks list updated after each section

---

### Pattern 3: Multi-Layer Validation

**Use when:** Validating AI/agent-generated code or docs before merging/deployment.

**Structure:**
- **Layer 1:** Automatic agent/hook checks (build, lint, file tracking)
- **Layer 2:** Self-review (prompted QA)
- **Layer 3:** Human/agent specialist review (edge cases, integration)

**Checklist:**
- [ ] Build/tests pass with no regressions
- [ ] Prompted QA checklist completed
- [ ] Edge cases & performance implications checked
- [ ] Risks documented

---

### Pattern 4: Planning Readiness

**Use when:** Deciding whether to initiate a planning phase or jump directly into implementation.

**Checklist:**
- [ ] Does work affect >3 files?
- [ ] Is feature/refactor multi-session or >2 unknowns?
- [ ] Does it require architectural change or complex integration?
- [ ] Are PRD/spec/requirements ambiguous or not documented?
- [ ] Is agent context likely to be lost (compaction, large scope)?
    - If YES to any: Activate Planning Mode

---

## Decision Matrices

| Situation                       | Approach                             | Validation                          |
|----------------------------------|--------------------------------------|-------------------------------------|
| >3 files, complex change         | Planning phase, full agentic loop    | Plan + QA checklist                 |
| Simple bugfix/single file        | Direct implementation                | Lint, self-review, smoke test       |
| Agentic code generation fails QA | Re-plan, isolate failure, iterate    | Test logs, agent/human review       |

---

## Common Mistakes

AVOID: Skipping planning for multi-file or ambiguous work (causes context loss, rework, or agent confusion)  
BEST: Always trigger a planning phase for complex or high-ambiguity work.

AVOID: Implementing entire plan at once (results in agent loss of focus, more errors)  
BEST: Work in 1–2 section increments, checkpoint after each.

AVOID: No explicit review after agentic phase (misses integration issues, security/test regressions)  
BEST: Run agentic QA checklist at every phase boundary.

AVOID: No documentation/context updates after session or compaction  
BEST: Update docs before/after major changes or at session handoff.

---

## Quick Reference

### Agentic Coding QA Checklist

- [ ] Acceptance criteria/metrics are clear and documented
- [ ] Build/lint/tests run with no new errors
- [ ] Self-review for error handling, edge cases, performance, and maintainability
- [ ] Risks and TODOs flagged and summarized
- [ ] Documentation/context files updated

### Planning Readiness Checklist

- [ ] Scope >3 files or multiple unknowns?
- [ ] Major architecture or integration change?
- [ ] PRD/spec is incomplete or ambiguous?
- [ ] Multi-session/multi-phase delivery required?
    - If any YES: **Activate planning phase and document plan**

---

### Example: Agentic Implementation Flow

```

1. Activate planning mode (if scope/complexity triggers)
2. Write/approve plan: phases, tasks, risks, metrics
3. Implement phase 1 only (e.g., database layer)
4. Run build/tests; self-review; document discoveries
5. Mark phase 1 tasks complete; update context
6. Repeat for next phases (e.g., API layer, integration)
7. Before handoff: run full QA, update docs, summarize risks/TODOs

```

---

> **Pro Tip:** Always checkpoint between phases to catch errors early and keep agent/human reviews focused. Use doc updates to prevent context loss on long or multi-session work.
