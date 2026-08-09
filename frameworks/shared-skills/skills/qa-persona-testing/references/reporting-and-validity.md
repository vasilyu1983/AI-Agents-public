# Reporting and Validity

How to turn session logs into a defensible improvement report, and what persona simulation can and cannot claim.

## Table of Contents

- [Severity Model](#severity-model)
- [Ranking and Aggregation](#ranking-and-aggregation)
- [Report Assembly](#report-assembly)
- [Validity Limits](#validity-limits)
- [Sycophancy Audit Before Shipping the Report](#sycophancy-audit-before-shipping-the-report)
- [Handoffs](#handoffs)

## Severity Model

Use Nielsen's 0-4 severity scale (nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/):

| Score | Meaning |
|---|---|
| 0 | Not a usability problem |
| 1 | Cosmetic — fix only if spare time |
| 2 | Minor — low priority |
| 3 | Major — important to fix (blocks or badly delays, workaround exists) |
| 4 | Catastrophic — imperative to fix before release (task-blocking or trust-breaking) |

**Reliability caveat (empirical):** LLM evaluators are moderately reliable at detecting *that* a usability issue exists (Cohen's Kappa ~0.50, 84% exact agreement) but weak at *severity scoring* — near-zero Krippendorff's Alpha across repeated runs on the same sites (arXiv:2512.04262, IEEE VL/HCC 2025). Therefore:

- Severity 4 assignments require a mechanical justification (task literally cannot complete, data loss, error page, trust-breaking dark pattern) — not vibes.
- For severity 3-4 findings, do a second scoring pass in a fresh context; if the two passes disagree by ≥2 points, mark the score `unstable` and let a human set it.
- Never sort the final fix list on severity alone; use severity x frequency (below).

## Ranking and Aggregation

1. Merge friction events across session logs; two events are the same finding if they occur at the same step/element with the same failure shape.
2. Rank by **severity first, then frequency** (how many personas/scenarios hit it). A severity-3 hit by all personas outranks a severity-4 hit only by the `assumed`-confidence edge persona.
3. Weight by persona confidence: findings from `assumed` personas drop one rank tier versus `validated` personas.
4. Every finding cites: session log + step number, a verbatim persona quote, and an evidence artifact. **No finding without a trace** — untraceable impressions get cut, not softened.

## Report Assembly

Use [../assets/findings-report.md](../assets/findings-report.md). Rules per section:

- **Executive summary**: the one-sentence top verdict must be actionable ("Fix the silent card-decline error on checkout step 3"), not thematic ("improve checkout UX").
- **Improve list**: each entry names the smallest change that removes the friction and the expected effect (completion, trust, speed). Avoid redesign essays.
- **Avoid list**: patterns that would hurt *this* ICP even if popular elsewhere (e.g., adding a chatbot gate for a low-trust persona). Source each from a logged persona reaction.
- **Keep list**: friction-free flows to protect — convert them into regression tests so fixes elsewhere don't break them.
- **Validity section is mandatory** and must appear even when the client didn't ask for it (see next section).

## Validity Limits

What the research record says persona simulation can and cannot support:

| Claim type | Supportable? | Basis |
|---|---|---|
| Mechanical failure (broken flow, dead end, error, missing state) | **Yes — treat as real** | The failure is in the app, not the simulation |
| Directional friction ("this step confuses this segment") | Partially — as a prioritized hypothesis | Synthetic users capture direction better than magnitude (NN/g 2025) |
| Effect size ("40% of users will abandon here") | **No** | Synthetic responses have compressed variance; magnitude is unreliable (NN/g 2025) |
| Emotional/preference verdicts ("users will love this") | **No — hypothesis only** | Documented sycophancy: synthetic users praise what real users later reject |
| Causal claims ("persona X behaves this way *because* they are X") | **No** | Persona-conditioned generation is observational, not interventional (arXiv:2605.20767) |

Framing rule from NN/g: presenting synthetic-user findings as equivalent to real-user research is an ethical violation, not just a methods caveat. Label every non-mechanical finding "simulated-persona signal — corroborate before treating as validated user behavior."

## Sycophancy Audit Before Shipping the Report

Before finalizing, run this checklist:

- [ ] Did any persona abandon any scenario? If completion was 100%, verify budgets were enforced; consider whether scenarios were too easy or the persona too agreeable.
- [ ] Does every positive verdict include the "what almost made them leave" answer?
- [ ] For high-stakes runs: did the adversarial second pass (skeptic persona or self-refutation) run, and are divergent findings marked low-confidence? Treat this as mandatory (not optional) for subjective surfaces — pricing perception, trust/privacy screens, values-laden copy — where sycophancy runs materially higher than on mechanically checkable flows.
- [ ] Is the model that ran the persona recorded? Sycophancy is strongly model-dependent (arXiv:2604.11609 measured a ~1.7x spread between two current models at p < 10⁻³²), so persona packs run on different models are not directly comparable across runs.
- [ ] Did the persona behave like a *person* or like a *stereotype of its segment*? Flawless persona adherence is not reassurance — see the fidelity trap in [persona-construction.md](persona-construction.md#the-fidelity-trap). If findings amount to "this demographic behaves as expected," suspect caricature and discount them.
- [ ] Are all severity 3-4 scores backed by mechanical justification or a stable second pass?
- [ ] Is the Validity and Limitations section present and specific (not boilerplate)?
- [ ] Was the environment actually emulated to the persona (viewport, `networkConditions`, CPU throttle)? An unthrottled desktop run on a mobile/low-bandwidth persona suppresses the entire latency-and-abandonment finding class — report that as a coverage gap rather than as "no performance issues found".

## Handoffs

| Finding type | Next skill |
|---|---|
| Severity ≥3 mechanical failures | `qa-testing-playwright` — encode as regression tests |
| Preference/emotional hypotheses worth money | `software-ux-research` — validate with real users |
| Accessibility findings (missing names, focus traps) | `qa-testing-accessibility` |
| Design-level fixes (hierarchy, flows, patterns) | `software-ui-ux-design` |
| "Wrong ICP" signals (persona genuinely has no use for the product) | `startup-idea-validation` |
