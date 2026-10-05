---
name: software-clean-code-standard
description: "Defines CC-* code rules and waivers. Use when mapping lint findings to rule IDs or tracking complexity mass, erosion, and verbosity across changes."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-08-21
---

# Clean Code Standard

This skill is the authoritative clean code standard for this repository's shared skills. It defines stable rule IDs (`CC-*`), how to apply them in reviews, and how to extend them safely via language overlays and explicit exceptions.

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
- Mapping a concrete review or scanner finding to a `CC-*` ID; use software-code-review for the review workflow.
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
3. Anchor the guidance in existing `CC-*` rules before proposing new wording or automation; map a tool finding by its failure mode, not by tool severity alone.
4. Apply the relevant standard, overlay, or waiver pattern with explicit scope and rationale.
5. Cross-check against the navigation references before adding or revising durable standards.

## Rule Application Checklist

When citing or enforcing `CC-*` rules in a review:

- [ ] Rule ID cited explicitly (not paraphrased) — e.g. `CC-SEC-01`, `CC-ERR-03` (two-digit `CC-<CAT>-<NN>`; only IDs that exist in the catalog — `python3 scripts/check_cc_ids.py [paths]` fails on unknown IDs)
- [ ] Scope stated: file, module, service, or whole repo
- [ ] Language overlay applied if the repo is language-specific and the base rule is ambiguous
- [ ] Blocking vs advisory: correctness/security findings block merge; style findings are advisory
- [ ] Waiver path documented if the rule genuinely cannot be satisfied without architectural change

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

**Refactor evidence gate.**

Do not raise a rule violation solely because code looks unfashionable. Name the maintenance failure it causes: duplicated change, hidden side effect, unsafe coupling, unreadable control flow, or measured complexity hotspot. Preserve stable awkward code when the proposed rewrite lacks a behavior-preserving test or a concrete reduction in change risk; document a narrow exception instead of creating churn.

- Map automation findings through the [rule-level examples](references/clean-code-standard.md#tool-findings-to-rule-ids); inspect the code before assigning a priority.
- Keep AI-assisted suggestions advisory; human reviewers approve/deny with rule citations (https://conventionalcomments.org/).
- Gate new blocking violations against the repository baseline; track erosion and verbosity as reviewed trajectories rather than universal thresholds ([metric guidance](references/code-complexity-metrics.md#trajectory-metrics-for-repeated-ai-edits)).

### Reviewing AI-Generated Code

AI-generated code requires the same CC-* standards plus additional vigilance for these patterns:

| Pattern | CC-* Mapping | Detection |
|---------|-------------|-----------|
| Hallucinated imports | CC-SEC-05 | `npm info` / `pip index` / type-check fails |
| Stale or deprecated APIs | CC-DEP-01 | Compiler warnings, changelog checks |
| Missing error paths | CC-ERR-01, CC-ERR-04 | No catch/finally, no null guards, no timeout |
| Premature abstraction | CC-FUN-06 | Wrappers with single call site, unused generics |
| Confident wrong comments | CC-DOC-01, CC-DOC-02 | Docstrings that don't match implementation |
| Security anti-patterns | CC-SEC-08, CC-SEC-03 | String concatenation in queries, hardcoded tokens |
| Silent fallback or empty catch | CC-ERR-01 | Error path returns a plausible default with no caller-visible failure |
| Weakened or deleted assertion | CC-TST-01, CC-TST-03 | Requirement no longer makes a test fail when reversed |
| Duplicate helper or scope expansion | CC-FUN-05, CC-FUN-06 | Parallel helper appears beside existing behavior or an abstraction has no second use |

For agent change discipline and tests that detect regressions, use [coding-behavior.md](../agents-memory/references/coding-behavior.md#rule-14--tests-verify-intent-not-just-behavior). For detailed hallucination checks, see [references/code-quality-operational-playbook.md § 11.3](references/code-quality-operational-playbook.md#113-hallucination-detection-checklist).

---

## Navigation

**Resources**
- [references/clean-code-standard.md](references/clean-code-standard.md) — the `CC-*` rule definitions themselves; open first to find or cite a rule ID
- [references/code-quality-operational-playbook.md](references/code-quality-operational-playbook.md) — Operational playbook: LLM-code review, complexity management, peer-review controls, judgment over dogma (legacy RULE-01–13 retired; § 1 maps them to `CC-*`)
- [references/working-effectively-with-legacy-code-operational-checklist.md](references/working-effectively-with-legacy-code-operational-checklist.md) — safely changing code with no/weak tests (Feathers)
- [references/refactoring-operational-checklist.md](references/refactoring-operational-checklist.md) — behavior-preserving refactor recipes and preconditions (Fowler)
- [references/design-patterns-operational-checklist.md](references/design-patterns-operational-checklist.md) — when a GoF pattern earns its complexity vs. over-engineering
- [references/functional-programming-patterns.md](references/functional-programming-patterns.md) — Result/Either types, pipe/compose, immutability, pure functions, railway-oriented programming, CC-* rule mapping
- [references/code-complexity-metrics.md](references/code-complexity-metrics.md) — Cyclomatic/cognitive complexity, Halstead metrics, nesting depth, tooling (ESLint, Biome, Oxlint, SonarQube, Ruff), refactoring triggers
- [data/sources.json](data/sources.json) — Current external references for review, security-by-design, observability, and modern tooling (official docs first)

**Templates**
- [assets/checklists/backend-api-review-checklist.md](assets/checklists/backend-api-review-checklist.md)
- [assets/checklists/secure-code-review-checklist.md](assets/checklists/secure-code-review-checklist.md)
- [assets/checklists/frontend-performance-a11y-checklist.md](assets/checklists/frontend-performance-a11y-checklist.md)
- [assets/checklists/mobile-release-checklist.md](assets/checklists/mobile-release-checklist.md)
- [assets/checklists/ux-design-review-checklist.md](assets/checklists/ux-design-review-checklist.md)

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

- For a named linter or scanner, check its official rule documentation and the version resolved by the project before mapping a finding to `CC-*`.
- For a proposed CI gate, check the scanner's current baseline/new-code support and compare its rule coverage with the repository's existing checks.
- Report the selected rule mapping, any unsupported rule or migration risk, and the source used to verify it.

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

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
