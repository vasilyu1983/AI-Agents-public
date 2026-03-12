# Clean Code Standard

Single source of truth for clean code rules. Other skills (especially `software-code-review`) must reference these rules by `CC-*` ID instead of duplicating guidance.

This standard is language-agnostic by default. Language/framework-specific details belong in overlays that reference existing `CC-*` IDs.

Normative keywords use RFC 2119 (https://www.rfc-editor.org/rfc/rfc2119).

---

## How Reviews Use This Standard

Review comments that are primarily about clean code MUST cite a `CC-*` rule ID.

Example:

- `issue (blocking): P1 CC-ERR-01 — Error is swallowed; caller cannot act on failure.`

Use labeled comment intent to reduce ambiguity (https://conventionalcomments.org/).

---

## Review Priority Defaults (P0–P3)

`P0` Critical: security vulnerability, data loss, funds at risk, immediate exploit.
`P1` High: correctness bug, missing error handling, unsafe defaults, major operability gaps.
`P2` Medium: maintainability issues, performance hazards in plausible hot paths.
`P3` Low: minor clarity improvements, non-impactful refactors.

Teams MAY override priorities by repo, but the standard’s default MUST be preserved in the canonical catalog.

---

## Rule ID Scheme

Format: `CC-<CAT>-<NN>`

- `CAT` is a stable category code.
- `NN` is a zero-padded number; IDs are never reused.
- Deprecations MUST keep the old ID and point to a replacement ID.

Categories:

- `CC-NAM` Naming
- `CC-FUN` Functions/methods
- `CC-TYP` Types & data structures
- `CC-FLOW` Control flow
- `CC-ERR` Error handling
- `CC-OBS` Logging & observability
- `CC-PERF` Performance hygiene
- `CC-SEC` Security hygiene
- `CC-TST` Tests
- `CC-DOC` Documentation

---

## Rule Catalog (Core)

### Naming (CC-NAM)

| ID | Rule | Requirement | Default Priority |
|---|---|---|---|
| CC-NAM-01 | Names MUST be intention-revealing and domain-accurate. | MUST | P2 |
| CC-NAM-02 | Domain terms MUST be consistent across a bounded context. | MUST | P2 |
| CC-NAM-03 | Units, encoding, and time semantics MUST be explicit when relevant (e.g., `milliseconds`, `utc`). | MUST | P1 |
| CC-NAM-04 | Boolean names SHOULD read as predicates (`is*`, `has*`, `can*`). | SHOULD | P3 |

### Functions/methods (CC-FUN)

| ID | Rule | Requirement | Default Priority |
|---|---|---|---|
| CC-FUN-01 | Each function MUST have one dominant responsibility (describe in one sentence). | MUST | P2 |
| CC-FUN-02 | Side effects MUST be explicit (naming, return type, or API boundary). | MUST | P1 |
| CC-FUN-03 | Parameter lists SHOULD be small and cohesive; group related parameters into a type/object. | SHOULD | P2 |
| CC-FUN-04 | Pure logic SHOULD be separated from I/O to improve testability and local reasoning. | SHOULD | P2 |
| CC-FUN-05 | Bug-prone duplication SHOULD be eliminated by extracting a well-named helper or abstraction (avoid copy/paste divergence). | SHOULD | P2 |

### Types & data structures (CC-TYP)

| ID | Rule | Requirement | Default Priority |
|---|---|---|---|
| CC-TYP-01 | Invalid states SHOULD be unrepresentable via types/enums/value objects where practical. | SHOULD | P2 |
| CC-TYP-02 | Domain concepts SHOULD use domain types (not raw primitives) when mistakes are costly. | SHOULD | P2 |
| CC-TYP-03 | Internal representations MUST be encapsulated; callers MUST not depend on volatile structure. | MUST | P2 |
| CC-TYP-04 | Domain-significant literals (numbers/strings) SHOULD be named constants/enums with explicit units/meaning; avoid duplicated “magic” literals. | SHOULD | P3 |

### Control flow (CC-FLOW)

| ID | Rule | Requirement | Default Priority |
|---|---|---|---|
| CC-FLOW-01 | Control flow SHOULD be shallow; prefer guard clauses over deep nesting. | SHOULD | P2 |
| CC-FLOW-02 | Complex boolean conditions SHOULD be extracted into named predicates/helpers. | SHOULD | P3 |
| CC-FLOW-03 | Concurrency and shared mutable state MUST be explicit and safe (no hidden races). | MUST | P1 |

### Error handling (CC-ERR)

| ID | Rule | Requirement | Default Priority |
|---|---|---|---|
| CC-ERR-01 | Failures MUST be explicit and actionable; no silent failures or empty catches. | MUST | P1 |
| CC-ERR-02 | Errors MUST carry context (operation + identifiers) without leaking secrets/PII. | MUST | P1 |
| CC-ERR-03 | Retries MUST be bounded, use timeouts, and be safe for idempotency/duplication. | MUST | P0 |
| CC-ERR-04 | I/O calls MUST define timeout and cancellation behavior where supported. | MUST | P1 |

### Logging & observability (CC-OBS)

| ID | Rule | Requirement | Default Priority |
|---|---|---|---|
| CC-OBS-01 | Logs SHOULD be structured and include correlation identifiers where relevant. | SHOULD | P2 |
| CC-OBS-02 | Logs MUST NOT include secrets, credentials, or sensitive personal data. | MUST | P0 |
| CC-OBS-03 | Critical paths MUST be observable via logs/metrics/traces appropriate to risk. | MUST | P1 |

### Performance hygiene (CC-PERF)

| ID | Rule | Requirement | Default Priority |
|---|---|---|---|
| CC-PERF-01 | Work MUST be bounded (limits, pagination, backpressure) for untrusted or large inputs. | MUST | P1 |
| CC-PERF-02 | Obvious performance hazards MUST be avoided (N+1, O(n²) loops on growth paths). | MUST | P2 |
| CC-PERF-03 | Material performance changes SHOULD be supported by measurement in the target environment. | SHOULD | P2 |

### Security hygiene (CC-SEC)

| ID | Rule | Requirement | Default Priority |
|---|---|---|---|
| CC-SEC-01 | Untrusted inputs MUST be validated at trust boundaries (prefer allowlists). | MUST | P0 |
| CC-SEC-02 | Authorization MUST be enforced for every sensitive operation; no bypass paths. | MUST | P0 |
| CC-SEC-03 | Secrets MUST NOT be hardcoded or logged; use secret management and rotation. | MUST | P0 |
| CC-SEC-04 | Cryptography MUST use proven libraries and secure defaults; do not invent crypto. | MUST | P0 |
| CC-SEC-05 | Dependencies MUST be pinned/locked and managed for known vulnerabilities (SCA + timely remediation); prefer trusted sources and provenance where feasible. | MUST | P1 |
| CC-SEC-06 | Passwords MUST be stored using adaptive hashing (Argon2id/bcrypt/scrypt) with organization-approved parameters; never plaintext or reversible encryption. | MUST | P0 |
| CC-SEC-07 | Authentication/session tokens MUST be generated with a CSPRNG and have expiry/rotation per policy; validate tokens on every request. | MUST | P0 |
| CC-SEC-08 | Untrusted inputs MUST NOT be interpolated into interpreters (SQL, shell, HTML); use parameterized queries, escaping, and safe APIs to prevent injection. | MUST | P0 |

### Tests (CC-TST)

| ID | Rule | Requirement | Default Priority |
|---|---|---|---|
| CC-TST-01 | New behavior MUST be covered by tests; bug fixes MUST include regression tests. | MUST | P1 |
| CC-TST-02 | Tests MUST be deterministic and isolated; flakiness is a release risk. | MUST | P1 |
| CC-TST-03 | Tests SHOULD assert behavior and contracts, not incidental implementation details. | SHOULD | P2 |
| CC-TST-04 | Test types SHOULD match risk (unit/integration/e2e) rather than blanket thresholds. | SHOULD | P2 |

### Documentation (CC-DOC)

| ID | Rule | Requirement | Default Priority |
|---|---|---|---|
| CC-DOC-01 | Public interfaces MUST document contracts (inputs, outputs, errors, side effects). | MUST | P2 |
| CC-DOC-02 | Comments SHOULD explain intent and tradeoffs (“why”), not restate code. | SHOULD | P3 |
| CC-DOC-03 | Critical systems SHOULD have operational docs (runbooks, alerts, dashboards) when relevant. | SHOULD | P2 |
| CC-DOC-04 | Commented-out code MUST NOT be committed; non-trivial TODO/FIXME notes MUST be actionable (tracking + owner). | MUST | P3 |

---

## Language Overlays (Non-Duplicative)

Overlays MUST reference existing `CC-*` IDs and add only:

- How to enforce in the language/tooling.
- Accepted idioms and exceptions.
- Automation mapping (linters/formatters/SAST) to rule IDs.

Overlays MUST NOT restate the base rule text.

---

## Exceptions And Waivers

Exceptions MUST be explicit, reviewable, and time-bounded when possible.

Minimum waiver fields:
- `cc_rule_id`
- `justification`
- `risk`
- `owner`
- `created_at`
- `expires_at` (optional but preferred)
- `tracking_issue` (required for non-trivial waivers)

---

## Governance

To add or change a rule:

1. Define the problem and failure modes.
2. Specify scope and exception criteria.
3. Provide at least one enforcement path (human review or automation).
4. Assign a default review priority (P0–P3) that is stable across teams.
5. Do not renumber; deprecate with `replaced_by` if needed.

---

## Optional: AI / Automation

Use automation to reduce review fatigue and keep humans focused on risk and intent.

- Prefer mechanical enforcement in CI (formatters/linters/static analysis), and reference `CC-*` IDs in tool output where possible.
- For repositories on GitHub: use PR templates, CODEOWNERS, and protected branches for consistent review routing and gating (https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository, https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners, https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
