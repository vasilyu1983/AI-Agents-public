---
name: software-clean-code-standard
description: "Defines cross-language clean code standards with stable CC-* rule IDs. Use when writing/reviewing code, defining team standards, or citing lint findings."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Clean Code Standard

This skill is the authoritative clean code standard for this repository's shared skills. It defines stable rule IDs (`CC-*`), how to apply them in reviews, and how to extend them safely via language overlays and explicit exceptions.

**Modern Best Practices**: Prefer small, reviewable changes and durable change context. Use BCP 14 normative language consistently (RFC 2119 + RFC 8174). Treat security-by-design and secure defaults as baseline (OWASP Top Ten 2025, NIST SSDF). Prefer GitHub rulesets over branch-protection-only governance. Build observable systems with OpenTelemetry. For current tool choices, consult `data/sources.json` and prefer official docs first.

**Judgment over dogma**: This standard's `CC-*` rules are durable (coupling/cohesion, naming, small interfaces, explicit errors). Numeric folklore — hard function-length caps, "comments are a smell," DRY applied absolutely — is not. Robert C. Martin's *Clean Code* (2nd ed., 2025) and John Ousterhout's *A Philosophy of Software Design* disagree in a published, public debate on function size and commenting (see [references/code-quality-operational-playbook.md § 14](references/code-quality-operational-playbook.md#14-judgment-over-dogma)); apply the rule ID's intent, not a book's specific numeric prescription, and know when *not* to refactor (§ 14.3 of the same reference).

---

## Quick Reference

| Task | Tool/Framework | Command | When to Use |
|------|-----|---------|-------------|
| Cite a standard | `CC-*` rule ID | N/A | PR review comments, design discussions, postmortems |
| Categorize feedback | `CC-NAM`, `CC-ERR`, `CC-SEC`, etc. | N/A | Keep feedback consistent without "style wars" |
| Add stack nuance | Language overlay | N/A | When the base rule is too generic for a language/framework |
| Allow an exception | Waiver record | N/A | When a rule must be violated with explicit risk |
| Reuse shared checklists | `assets/checklists/` | N/A | When you need product-agnostic review/release checklists |
| Reuse utility patterns | `references/*-utilities.md` | N/A | When extracting shared auth/logging/errors/resilience/testing utilities |

## When to Use This Skill

- Defining or enforcing clean code rules across teams and languages.
- Reviewing code: cite `CC-*` IDs and avoid restating standards in reviews.
- Building automation: map linters/CI gates to `CC-*` IDs.
- Resolving recurring review debates: align on rule IDs, scope, and exceptions.

## When NOT to Use This Skill

- **Deep security audits** → [software-security-appsec](../software-security-appsec/SKILL.md) for OWASP/SAST deep dives beyond `CC-SEC-*` baseline.
- **Review workflow mechanics** → [software-code-review](../software-code-review/SKILL.md) for PR workflow, reviewer assignment, and feedback patterns.
- **Refactoring execution** → [qa-refactoring](../qa-refactoring/SKILL.md) for step-by-step refactoring patterns and quality gates.
- **Architecture decisions** → [software-architecture-design](../software-architecture-design/SKILL.md) for system-level tradeoffs beyond code-level rules.

## Workflow

1. Decide whether the request is about a base rule, an overlay, or an exception.
2. Route security, review-process, or refactoring mechanics to the adjacent skill if that is the real problem.
3. Anchor the guidance in existing `CC-*` rules before proposing new wording or automation.
4. Apply the relevant standard, overlay, or waiver pattern with explicit scope and rationale.
5. Cross-check against the navigation references before adding or revising durable standards.

## Rule Application Checklist

When citing or enforcing `CC-*` rules in a review:

- [ ] Rule ID cited explicitly (not paraphrased) — e.g. `CC-SEC-001`, `CC-ERR-003`
- [ ] Scope stated: file, module, service, or whole repo
- [ ] Language overlay applied if the repo is language-specific and the base rule is ambiguous
- [ ] Blocking vs advisory: correctness/security findings block merge; style findings are advisory
- [ ] Waiver path documented if the rule genuinely cannot be satisfied without architectural change

## ASCII Flow

```text
Clean-code request
  -> Identify behavior that must stay unchanged
  -> Find duplication, unclear boundaries, or unsafe complexity
  -> Refactor in the smallest coherent slice
  -> Preserve public contracts and naming consistency
  -> Add or adjust tests for changed control flow
  -> Run focused verification and report residual risk
```

## Decision Tree: Base Rule vs Overlay vs Exception

```text
Feedback needed: [What kind of guidance is this?]
    ├─ Universal, cross-language rule? → Add/modify `CC-*` in `references/clean-code-standard.md`
    │
    ├─ Language/framework-specific nuance? → Add overlay entry referencing existing `CC-*`
    │
    └─ One-off constraint or temporary tradeoff?
        ├─ Timeboxed? → Add waiver with expiry + tracking issue
        └─ Permanent? → Propose a new rule or revise scope/exception criteria
```

---

## Optional: AI/Automation

- Map automation findings to `CC-*` IDs (linters, SAST, dependency scanning) so humans can review impact, not tooling noise.
- Keep AI-assisted suggestions advisory; human reviewers approve/deny with rule citations (https://conventionalcomments.org/).
- Prefer GitHub rulesets, SARIF-capable scanners, and repository-native code scanning for durable enforcement/reporting.

### Reviewing AI-Generated Code

AI-generated code requires the same CC-* standards plus additional vigilance for these patterns:

| Pattern | CC-* Mapping | Detection |
|---------|-------------|-----------|
| Hallucinated imports | CC-DEP-* | `npm info` / `pip index` / type-check fails |
| Stale or deprecated APIs | CC-DEP-* | Compiler warnings, changelog checks |
| Missing error paths | CC-ERR-* | No catch/finally, no null guards, no timeout |
| Premature abstraction | CC-COMPLEXITY-* | Wrappers with single call site, unused generics |
| Confident wrong comments | CC-NAMING-* | Docstrings that don't match implementation |
| Security anti-patterns | CC-SEC-* | String concatenation in queries, hardcoded tokens |

For detailed hallucination detection steps, see [references/code-quality-operational-playbook.md § 11.3](references/code-quality-operational-playbook.md#113-hallucination-detection-checklist).

---

## Navigation

**Resources**
- [references/clean-code-standard.md](references/clean-code-standard.md)
- [references/code-quality-operational-playbook.md](references/code-quality-operational-playbook.md) — Legacy operational playbook (RULE-01–RULE-13)
- [references/clean-code-operational-checklist.md](references/clean-code-operational-checklist.md)
- [references/clean-coder-operational-checklist.md](references/clean-coder-operational-checklist.md)
- [references/code-complete-operational-checklist.md](references/code-complete-operational-checklist.md)
- [references/pragmatic-programmer-operational-checklist.md](references/pragmatic-programmer-operational-checklist.md)
- [references/practice-of-programming-operational-checklist.md](references/practice-of-programming-operational-checklist.md)
- [references/working-effectively-with-legacy-code-operational-checklist.md](references/working-effectively-with-legacy-code-operational-checklist.md)
- [references/art-of-clean-code-operational-checklist.md](references/art-of-clean-code-operational-checklist.md)
- [references/refactoring-operational-checklist.md](references/refactoring-operational-checklist.md)
- [references/design-patterns-operational-checklist.md](references/design-patterns-operational-checklist.md)
- [references/functional-programming-patterns.md](references/functional-programming-patterns.md) — Result/Either types, pipe/compose, immutability, pure functions, railway-oriented programming, CC-* rule mapping
- [references/code-complexity-metrics.md](references/code-complexity-metrics.md) — Cyclomatic/cognitive complexity, Halstead metrics, nesting depth, tooling (ESLint, Biome, Oxlint, SonarQube, Ruff), refactoring triggers
- [data/sources.json](data/sources.json) — Current external references for review, security-by-design, observability, and modern tooling (official docs first)
- [CONVENTIONS.md](CONVENTIONS.md) — Skill structure and validation conventions
- [SKILL-TEMPLATE.md](SKILL-TEMPLATE.md) — Copy-paste starter for new skills
- [sources-schema.json](sources-schema.json) — JSON schema for `data/sources.json`
- [skill-dependencies.json](skill-dependencies.json) — Related-skills dependency graph

**Templates**
- [assets/checklists/backend-api-review-checklist.md](assets/checklists/backend-api-review-checklist.md)
- [assets/checklists/secure-code-review-checklist.md](assets/checklists/secure-code-review-checklist.md)
- [assets/checklists/frontend-performance-a11y-checklist.md](assets/checklists/frontend-performance-a11y-checklist.md)
- [assets/checklists/mobile-release-checklist.md](assets/checklists/mobile-release-checklist.md)
- [assets/checklists/ux-design-review-checklist.md](assets/checklists/ux-design-review-checklist.md)
- [assets/checklists/ux-research-plan-template.md](assets/checklists/ux-research-plan-template.md)

**Utility Patterns**

- [references/utility-patterns.md](references/utility-patterns.md) — When and how to extract a utility instead of duplicating code (the decision guide above the concrete utilities below)
- [references/auth-utilities.md](references/auth-utilities.md)
- [references/error-handling.md](references/error-handling.md)
- [references/config-validation.md](references/config-validation.md)
- [references/resilience-utilities.md](references/resilience-utilities.md)
- [references/logging-utilities.md](references/logging-utilities.md)
- [references/observability-utilities.md](references/observability-utilities.md)
- [references/testing-utilities.md](references/testing-utilities.md)
- [references/llm-utilities.md](references/llm-utilities.md)

**Related Skills**
- [../software-code-review/SKILL.md](../software-code-review/SKILL.md) — Review workflow and judgment; cite `CC-*` IDs
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Security deep dives beyond baseline `CC-SEC-*`
- [../qa-refactoring/SKILL.md](../qa-refactoring/SKILL.md) — Refactoring execution patterns and quality gates
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System-level tradeoffs and boundaries

---

## Freshness Protocol

**IMPORTANT**: When users ask recommendation questions about clean code standards, linters, formatters, static analysis, or code quality tools, you MUST verify current guidance with web search and official docs before answering. If web search is unavailable, say so and answer using `data/sources.json`, clearly flagging that the recommendation may be stale.

### Trigger Conditions

- "What's the best linter for [language]?"
- "What should I use for [code quality/static analysis]?"
- "What's the latest in clean code practices?"
- "Current best practices for [code standards/formatting]?"
- "Is [ESLint/Prettier/Biome] still relevant?"
- "[Biome] vs [ESLint] vs [other]?"
- "Best static analysis tool for [language]?"
- "Should we switch from [legacy tool] to [new tool]?"
- "What should we use in CI for code scanning or code quality gates?"

### Required Verification Workflow

1. Check official docs first for the named tool(s): current docs, release notes/changelog, migration guidance, and supported workflows.
2. Check the official standard/spec when relevant: RFCs, OWASP, NIST, OpenTelemetry, GitHub Docs.
3. Use web search for cross-tool comparisons or current adoption trends only after confirming the primary-source facts.
4. Prefer at most one neutral secondary comparison source when the user explicitly wants market positioning or tradeoff analysis.

### What to Report

After verifying, provide:

- **Current default choice**: What you would adopt now for the user’s stack and why
- **Current landscape**: Which tools are current, maintained, and commonly paired together
- **Migration risk**: Flat config changes, rule-coverage gaps, formatter/linter consolidation, CI/reporting implications
- **Deprecated/declining**: Tools or approaches losing relevance for this use case
- **Recommendation**: Based on fresh official data, not static memory

### Example Topics (verify with fresh search)

- JavaScript/TypeScript linters (ESLint, Biome, oxlint)
- Formatters (Prettier, dprint, Biome)
- Python quality (Ruff, `ty`, mypy, pylint)
- Go linting (golangci-lint, staticcheck)
- Rust analysis (clippy, cargo-deny)
- Code quality metrics and reporting tools
- Code scanning and security automation (CodeQL, Semgrep, SARIF workflows)
- GitHub enforcement controls (rulesets, CODEOWNERS, protected branches)

## Known Traps

- Treating “clean code” as style preference only and ignoring correctness, observability, security, and change safety.
- Enforcing blanket abstraction rules that increase indirection and reduce runtime clarity in the name of cleanliness.
- Mixing language-specific formatter and linter opinions into universal guidance without preserving the stable CC rule intent.
- Letting tool defaults silently redefine the team standard when the explicit repository rule IDs say otherwise.
- Auditing code solely from static style output and missing failure-mode, data-boundary, and operability risks.

## Common Anti-Patterns

- Replacing concrete, understandable code with layered abstractions just to satisfy a cleanliness aesthetic.
- Treating short functions, DRY, or naming rules as absolute even when they harm cohesion, locality, or domain clarity.
- Using “clean code” to block pragmatic duplication that preserves boundaries or avoids premature frameworks.
- Turning rule IDs into checklist theater with no explanation of why the rule matters for maintainability or safety.
- Applying one language ecosystem’s conventions wholesale to another without adaptation for tooling, runtime, and team workflow.

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information, and distinguish facts from inference.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

