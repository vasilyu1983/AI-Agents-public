# Primitive: Failure Mode and Effects Analysis (FMEA)

## Definition

**Failure Mode and Effects Analysis (FMEA)** is a bottom-up, inductive technique that systematically identifies potential failure modes of a system's components, determines their effects on higher-level function, and ranks their risk to drive mitigation priorities.

FMEA produces a **Risk Priority Number (RPN)**:

```
RPN = Severity (S) × Occurrence (O) × Detection (D)
```

Each factor is scored on a 1–10 scale:

| Factor | 1 (Low) | 5 (Medium) | 10 (High) |
|--------|---------|-----------|----------|
| Severity (S) | Minor inconvenience | Degraded performance | Safety hazard or data loss |
| Occurrence (O) | Extremely unlikely | Occasional | Near-certain |
| Detection (D) | Easily detected before impact | Detected after impact | Undetectable |

**Higher RPN = higher priority for mitigation.** Maximum RPN = 1,000.

When FMEA is applied to critical safety systems, the variant **FMECA** (Failure Mode, Effects, and Criticality Analysis) adds a criticality matrix that separates catastrophic from marginal failure modes.

## When to Use

- Design reviews before a product or service launches.
- Process audits to identify where a manufacturing or operational process can go wrong.
- Post-incident retrospectives to capture failure modes missed in prior FMEA.
- Regulatory contexts (IATF 16949 for automotive, IEC 60812 for electrical systems, FDA process FMEA for medical devices).
- Prioritising reliability improvements when budget is constrained — attack highest-RPN items first.

## Inputs

| Input | Description |
|-------|-------------|
| Component / process list | Complete inventory of items under analysis |
| Functional requirements | What each component must do under normal and stressed conditions |
| Historical failure data | Known failure modes from field reports, post-mortems, test results |
| Severity definitions | Organisation-specific S scale calibrated to business impact |

## Outputs

- FMEA worksheet (one row per failure mode).
- RPN ranking table with recommended actions.
- Owner and target date for each high-RPN mitigation.
- Updated RPNs after mitigations are applied (residual risk).

## FMEA Worksheet Structure

| Component | Function | Failure Mode | Effect on System | S | Cause | O | Detection Controls | D | RPN | Recommended Action | Owner |
|-----------|----------|-------------|-----------------|---|-------|---|-------------------|---|-----|-------------------|-------|
| Auth service | Validate JWT tokens | Token signing key unavailable | All API requests rejected | 9 | KMS outage | 3 | Health-check alert | 4 | 108 | Add local key cache with 15-min TTL | Platform team |

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| RPN treated as an objective ranking | High-RPN items with low severity can crowd out low-RPN items with catastrophic severity | Always review S=9/10 items regardless of RPN; never ignore high-severity rows |
| Detection score conflated with monitoring coverage | A metric that exists but is never acted on scores as "detected" | Score Detection by whether the failure is detected *before* customer impact, not just before engineers notice |
| FMEA done once, never updated | Architecture drift makes the worksheet obsolete | Gate FMEA reviews to each significant architecture change and each major incident |
| Occurrence rated by intuition, not data | Inconsistent O scores across teams; ranking unreliable | Anchor O to observed or modelled failure rates (primitive 01) where available |
| Over-narrow scope (one component at a time) | Interaction failures and common-cause modes missed | Include interface failure modes and shared-dependency failure modes explicitly |

## Worked Example

**Scope**: Checkout service, 3-hour FMEA sprint before Black Friday launch.

| Component | Failure Mode | Effect | S | O | D | RPN | Action |
|-----------|-------------|--------|---|---|---|-----|--------|
| Payment API | Timeout under load | Orders silently fail | 9 | 6 | 5 | 270 | Add retry with idempotency key + circuit breaker |
| Inventory cache | Stale stock count | Oversell | 7 | 4 | 6 | 168 | Reduce TTL; add stock-level alert at 5 units |
| Order DB | Replication lag spike | Duplicate order risk | 8 | 3 | 4 | 96 | Add idempotency check at application layer |
| CDN | Origin fallback fails | Slow page load for all | 5 | 2 | 3 | 30 | — (acceptable residual risk) |

**Payment API timeout (RPN 270) is the priority**. The circuit breaker prevents cascading failures; the idempotency key prevents duplicate charges on retry. Both mitigations reduce O and improve D, projecting residual RPN of 90.

## Tooling Note (2025)

LLMs can generate failure mode candidates from unstructured field data — maintenance logs, customer reviews, warranty records — with **~87–91% substantial agreement** versus expert gold standards. GPT-4 achieves 91%, GPT-4o 87%, and Gemini 80% on 100-review validation corpora; part identification accuracy reaches 98–99%. Use as an input-phase accelerator to surface candidate failure modes faster from large unstructured corpora; **do not skip expert RPN scoring review**. Fine-tuning is not required — 2–3 prompt-engineering iterations yield production-quality candidates. Human-in-the-loop validation remains essential, and false-negative rate (missed critical failure modes) is not yet quantified. Validated primarily on automotive domain; transfer to safety-critical systems should be treated as unvalidated until replicated. (El Hassani et al. 2025, Design Science, Cambridge University Press. DOI: 10.1017/dsj.2025.7.)

## Sources

- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- IEC 60812 (2018). *Failure modes and effects analysis (FMEA and FMECA)*. International Electrotechnical Commission.
- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer.
- El Hassani, I., Masrour, T., Kourouma, N., & Tavčar, J. (2025). AI-driven FMEA: integration of large language models for faster and more accurate risk analysis. *Design Science*, Volume 11. Cambridge University Press.
