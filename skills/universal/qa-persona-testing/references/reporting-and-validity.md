# Reporting and Validity

How to turn session logs into a defensible improvement report, and what persona simulation can and cannot claim.

## Table of Contents

- [Severity Model](#severity-model)
- [Ranking and Aggregation](#ranking-and-aggregation)
- [Report Assembly](#report-assembly)
- [Validity Limits](#validity-limits)
- [Comparing Designs](#comparing-designs)
- [Sycophancy Audit Before Shipping the Report](#sycophancy-audit-before-shipping-the-report)
- [Handoffs](#handoffs)

## Severity Model

Use [Nielsen's 0-4 severity scale](https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/). The parenthetical impact examples below are this skill's operational guidance; observed frequency and persistence in Nielsen's model require real-user evidence, not a count of simulated personas:

| Score | Meaning |
|---|---|
| 0 | Not a usability problem |
| 1 | Cosmetic — fix only if spare time |
| 2 | Minor — low priority |
| 3 | Major — important to fix (blocks or badly delays, workaround exists) |
| 4 | Catastrophic — imperative to fix before release (task-blocking or trust-breaking) |

**Reliability caveat (empirical):** A GPT-4o code-based evaluation of thirty open-source websites found moderate consistency in detecting *that* a usability issue exists (Cohen's Kappa ~0.50, 84% exact agreement) but weak at *severity scoring* — near-zero Krippendorff's Alpha across repeated runs on the same sites (arXiv:2512.04262, IEEE VL/HCC 2025). Therefore:

- Severity 4 assignments require a mechanical justification (task literally cannot complete, data loss, error page, trust-breaking dark pattern) — not vibes.
- For severity 3-4 findings, do a second scoring pass in a fresh context; if the two passes disagree by ≥2 points, mark the score `unstable` and let a human set it.
- Rank confirmed mechanical defects by severity, then independent reproducibility (below). Do not impose a minimum number of findings at any severity.

## Ranking and Aggregation

1. Merge friction events across session logs; two events are the same finding if they occur at the same step/element with the same failure shape.
2. Rank confirmed mechanical defects by **severity first, then independent reproducibility**: re-run the documented steps in a clean context and record reproduced / not reproduced / not checked. Keep unconfirmed observations in a separate verification queue.
3. Report persona repetition and persona confidence separately. Neither simulated frequency nor an assumed persona changes the severity of a reproduced defect or estimates real-user prevalence.
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
| Mechanical failure (broken flow, dead end, error, missing state) | **Yes, when evidenced and reproduced** | Confirm the app failure independently of the persona narrative |
| Directional friction ("this step confuses this segment") | Partially — as a prioritized hypothesis | Synthetic users capture direction better than magnitude (NN/g 2025) |
| Effect size ("40% of users will abandon here") | **No** | Synthetic responses have compressed variance; magnitude is unreliable (NN/g 2025) |
| Emotional/preference verdicts ("users will love this") | **No — hypothesis only** | Synthetic-user positivity is not calibrated to real users — see the note below; treat uncorroborated praise as an artifact, not a finding |
| Causal claims about a design comparison ("version B converts better than A because of this change") | **No, without controls** | See [Comparing Designs](#comparing-designs): LLM-simulated A/B comparisons are confounded by user drift across arms (arXiv:2605.20767) |

**Note on "synthetic users over-praise" — do not repeat as stated.** NN/g's own Study 3 found synthetic users *less* positive than real ones on purchase likelihood (1.58 vs 1.66) and liking (1.4 vs 1.43), though more positive on uniqueness (2.48 vs 2.12) — a mixed picture, not uniform over-praise. If a persona run looks suspiciously agreeable, treat it as an observed failure mode of that run (task always completes, no friction surfaced) and flag it for the sycophancy audit below, rather than citing "synthetic users over-praise" as a general research finding.

Framing rule from NN/g: realistic synthetic-user output "raise[s] ethical questions," and human participants remain "essential for … ethical and contextual integrity" (nngroup.com/articles/ai-simulations-studies/). NN/g does not call presenting synthetic findings as equivalent to real-user research a "violation" — that framing is this skill's own house rule, stated here because the underlying ethical concern is real: label every non-mechanical finding "simulated-persona signal — corroborate before treating as validated user behavior."

## Comparing Designs

Persona runs are sometimes used to compare two versions of a flow (a redesign, an A/B variant). Treat this as higher-risk than a single-version audit: arXiv:2605.20767 shows that when an LLM-simulated experiment intervenes on a design, the *implicit simulated population itself can drift* between the treatment arms — the personas answering under Design B are not guaranteed to be the same simulated population as under Design A, which confounds any A-versus-B delta. The paper's own subject is intervention-effect estimation under this drift, not "why does persona X behave the way it does."

Minimum controls before treating a persona-run comparison as evidence:

- **Paired seeds.** Run the same persona pack, same seeds/temperature settings, and the same model against both versions — never a fresh persona draw per arm.
- **Negative controls.** Include at least one outcome that should *not* change between versions (e.g., an unrelated page's completion rate). If the negative control moves, the run is confounded and the real delta is not trustworthy.
- **Never ship on a persona delta alone.** A persona-run comparison sets priority and hypothesis, never a ship/no-ship decision — route it to `software-ux-research` or a real experiment before it decides anything with revenue or trust at stake.

## Sycophancy Audit Before Shipping the Report

Before finalizing, run this checklist:

- [ ] Did any persona abandon any scenario? If completion was 100%, verify budgets were enforced; consider whether scenarios were too easy or the persona too agreeable.
- [ ] Does every positive verdict state any observed friction, or explicitly state that none occurred? Do not invent friction to satisfy a quota.
- [ ] For high-stakes runs: did the adversarial second pass (skeptic persona or self-refutation) run, and are divergent findings marked low-confidence? Treat this as mandatory (not optional) for subjective surfaces — pricing perception, trust/privacy screens, values-laden copy — as a house precaution; the cited study did not test these UX surfaces.
- [ ] Is the model that ran the persona recorded? arXiv:2604.11609 found GPT-5-nano averaged a sycophancy score of 2.96 vs Claude Haiku 4.5's 1.74, scored out of 10 (Δ +1.22, p < 10⁻³²) — but that paper measures an *assistant* validating a *user's* false beliefs, conditioned on the user's perceived demographics. In persona testing the roles are inverted: the LLM plays the user reacting to a product. Treat the 2.96/1.74 figures as evidence that sycophancy is strongly model-dependent in general, not as a direct estimate of how agreeable a given simulator model will be as a persona. The safer, directly-on-point evidence is arXiv:2601.17087: agent success rates varied by up to 9 percentage points across different simulator-user LLMs on the same tasks, with systematic miscalibration and different failure patterns than real users. Run high-stakes packs on at least two simulator models and treat cross-model disagreement as low-confidence, rather than assuming one model's run generalizes.
- [ ] Did the persona behave like a *person* or like a *stereotype of its segment*? Flawless persona adherence is not reassurance — see the fidelity trap in [persona-construction.md](persona-construction.md#the-fidelity-trap). If findings amount to "this demographic behaves as expected," suspect caricature and discount them.
- [ ] Are all severity 3-4 scores backed by mechanical justification or a stable second pass?
- [ ] Is the Validity and Limitations section present and specific (not boilerplate)?
- [ ] Was the environment actually emulated to the persona (viewport, `networkConditions`, CPU throttle)? An unthrottled desktop run on a mobile/low-bandwidth persona suppresses the entire latency-and-abandonment finding class — report that as a coverage gap rather than as "no performance issues found".
- [ ] Did the run touch anything live — real payment methods, real email/SMS sends, production data? Persona agents will click Buy, Send, Delete, and Invite exactly as instructed. Require staging or sandbox accounts and test payment methods, and block or sink outbound email/SMS before the run, not after. Never run against production with real user PII.
- [ ] Was more than one simulator model used for a high-stakes pack? A single model's persona run is one sample of a model-dependent process (arXiv:2601.17087: up to 9 pp variance in outcomes across simulator models on identical tasks); report single-model findings as lower-confidence.

## Handoffs

| Finding type | Next skill |
|---|---|
| Severity ≥3 mechanical failures | `qa-testing-playwright` — encode as regression tests |
| Preference/emotional hypotheses worth money | `software-ux-research` — validate with real users |
| Accessibility findings (missing names, focus traps) | `qa-testing-accessibility` |
| Design-level fixes (hierarchy, flows, patterns) | `software-ui-ux-design` |
| "Wrong ICP" signals (persona genuinely has no use for the product) | `startup-idea-validation` |
