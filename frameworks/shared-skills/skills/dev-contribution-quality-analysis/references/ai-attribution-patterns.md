# AI Attribution Patterns

## Table of Contents

- [Attribution Tooling](#attribution-tooling)
- [Detection Heuristics (When No Tooling Available)](#detection-heuristics-when-no-tooling-available)
- [Quality Metrics for AI-Assisted Code](#quality-metrics-for-ai-assisted-code)
- [Industry Context](#industry-context)
- [How This Skill Uses AI Attribution](#how-this-skill-uses-ai-attribution)

Patterns for detecting, measuring, and contextualizing AI-assisted code contributions. All signals in this document are **context-only** and do not affect quality tier assignment.

---

## Attribution Tooling

### Ground-Truth Attribution

These tools record AI authorship at the point of creation:

| Tool | Method | Coverage | License |
|------|--------|----------|---------|
| Agent Blame (Mesa) | Git hooks intercept AI edits from Cursor, Claude Code, OpenCode; stores in git notes | Line-level | Apache 2.0 |
| Git AI | Git extension tracking AI-generated code; provides AI Blame CLI | Line-level | Open source |
| Agent Trace (Cursor RFC) | Vendor-neutral JSON spec for AI vs. human contributions; four types: human, AI, mixed, unknown | File and line-level | Open spec |

### Detection-Based Attribution

These tools analyze code to infer AI authorship after the fact:

| Tool | Method | Accuracy | Use Case |
|------|--------|----------|----------|
| Pangram Labs | AST analysis, token probability, entropy, neural fingerprinting | ~8% FN, very low FP | CI/CD integration |
| Fingerprinting (arxiv 2601.17406) | 41 features across commit patterns, PR structure, code changes, patch-level, temporal | 97.2% F1 multi-class agent ID | Research, bulk analysis |

---

## Detection Heuristics (When No Tooling Available)

When neither ground-truth attribution nor commercial detection tools are available, these statistical heuristics provide weak signals. **Important**: false-positive rates are high. Use for investigation prompts only, never as evidence.

### Commit Message Fingerprints

From the arxiv 2601.17406 study of 33,580 PRs across five AI agents:

| Feature | Importance | Signal |
|---------|-----------|--------|
| Multiline commit ratio | 44.7% | AI agents produce significantly more multiline commit messages |
| Change concentration | 10.1% | AI commits tend to touch files with higher directory depth |
| Avg commit message length | 2.3% | AI messages are often longer and more detailed |
| Conventional commit ratio | — | Some agents (Claude Code) consistently use conventional format |

### Agent-Specific Signatures

| Agent | Distinctive Pattern |
|-------|-------------------|
| Claude Code | High conditional density (27.2%), elevated comment density (19.8%) |
| Cursor | Bullet points in PR body (17.2%), hyperlinks (12.8%) |
| Codex | Very short PR descriptions, high files-per-commit ratio |
| Copilot | Inline suggestions show low multiline ratio, conventional commit adherence varies |

### Code-Level Indicators

| Indicator | What to Look For | Confidence |
|-----------|-----------------|------------|
| Low entropy in diffs | AI code is more uniform and predictable; human code shows higher entropy from mixed styles | Low |
| Naming inconsistency | Long functions with inconsistent naming across same file | Low |
| Over-documented | Excessive inline comments explaining obvious code | Low |
| Pattern repetition | Same structural pattern repeated without abstraction | Medium |
| Hallucinated imports | Import statements for non-existent modules or deprecated APIs | Medium |
| Confident-wrong comments | Comments that describe code behavior inaccurately but confidently | Low |

---

## Quality Metrics for AI-Assisted Code

### AI Code Survival Rate

Definition: percentage of AI-attributed lines that survive 30 days without being rewritten or deleted.

Calculation:
1. Identify lines attributed to AI (via ground-truth tooling)
2. Track those lines through subsequent commits for 30 days
3. Lines that are unchanged, or changed only for unrelated reasons (e.g., file rename), count as surviving
4. Report survival rate as a percentage

Benchmarks:
- No established industry benchmark at time of writing; verify before citing
- Preliminary data from GitClear suggests AI-generated code has higher 2-week churn than human code
- Survival rate below 60% suggests AI contributions need more human review

### AI Quality Parity

Compare D2 (Code Quality) and D3 (Commit Craft) scores between:
- Commits flagged as AI-assisted
- Commits by the same person without AI flags

Parity or better scores indicate the developer is using AI effectively. Significantly worse scores suggest accepting AI output without adequate review.

### Verification Burden

Compare 14-day churn rate between:
- AI-heavy commits (> 50% AI-attributed lines)
- The person's overall baseline churn rate

If AI-heavy commits have > 1.5x the baseline churn rate, the developer is accepting AI output that requires excessive rework.

---

## Industry Context

### Key Statistics

- 2.74x more cross-site scripting vulnerabilities in AI-generated code, and only 12-13% of context-dependent (XSS-class) samples secure by default (Veracode GenAI Code Security Report, Oct 2025; 100+ LLMs tested across 4 languages, 45% overall failure rate on security checks)
- 1.75x more logic/correctness errors in AI-authored PRs vs. human-authored PRs — this figure is from CodeRabbit's Dec 2025 analysis of 470 real pull requests, not from Veracode. Cite it as CodeRabbit; do not merge the two sources' numbers into one citation.
- Code duplication rose from 8.3% to 12.3% of changed lines (2021-2024, GitClear)
- Refactoring dropped from 25% to under 10% of changed lines (GitClear)
- Code churn (2-week rewrite) increased 83.9% (GitClear)
- Apiiro (Sep 2025): AI-generated code introduced 10,000+ new security findings per month across studied repositories — a 10x spike in 6 months; privilege escalation paths up 322%, architectural design flaws up 153%
- GitGuardian: 6.4% of repos using GitHub Copilot leak at least one secret, 40% higher than 4.6% baseline
- METR study (arxiv 2507.09089): 39-44% gap between perceived and actual AI productivity for early-2025 tools

### Implications for Quality Assessment

1. **Don't penalize AI use** — penalize poor outcomes. A developer who uses AI and produces durable, well-tested code is contributing effectively.
2. **Watch churn rate** — if someone's churn rate has increased alongside AI tool adoption, their acceptance bar may be too low.
3. **Watch duplication** — AI tools default to generating new code rather than refactoring existing patterns. Rising duplication signals insufficient post-generation review.
4. **Test coverage as proxy** — AI-assisted code that includes tests is more likely to be reviewed and understood by the developer.
5. **Distinguish "AI-assisted" from "agent-authored."** By mid-2026, autonomous coding agents (Devin, Codex cloud tasks, Claude Code delegated/background sessions) can open and iterate on a PR with no human keystrokes in the diff, merged under a human's identity as reviewer/approver. Treat this as a fifth contributor type alongside human/AI/mixed/unknown: the person-level signals in D2-D3 measure the agent's output plus the human's review and delegation judgment, not their own coding craft. Flag these explicitly in reports rather than silently blending them into the person's craft score — conflating the two erases the actual skill being evaluated (orchestration and review) and can wrongly credit or discredit a person for code they never wrote a line of.

---

## How This Skill Uses AI Attribution

AI attribution data flows into Dimension 6 (AI Development Quality), which is always context-only:

1. **D6 is not scored** in the overall quality tier
2. When AI attribution data is available, D6 sub-signals (survival rate, quality parity, verification burden) are computed and reported
3. When no attribution data exists, D6 is marked "not available"
4. AI attribution does NOT affect D1-D5 scoring in any way

The quality-neutral stance means: a commit is scored the same way regardless of whether it was written by a human, an AI, or both. What matters is the outcome (churn, test presence, review, complexity), not the authorship.
