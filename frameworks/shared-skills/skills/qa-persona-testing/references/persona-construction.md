# Persona Construction

How to convert an ICP or user segment into an executable persona specification, and how to keep the simulation honest.

## Table of Contents

- [Evidence First: Grounding the Persona](#evidence-first-grounding-the-persona)
- [From ICP to Behavioral Spec](#from-icp-to-behavioral-spec)
- [Persona Memory and Preference History](#persona-memory-and-preference-history)
- [Anti-Sycophancy](#anti-sycophancy)
- [Persona-Drift Checks](#persona-drift-checks)
- [Low-Confidence Persona Classes](#low-confidence-persona-classes)
  - [The fidelity trap](#the-fidelity-trap)
  - [Attribute truncation](#attribute-truncation)

## Evidence First: Grounding the Persona

Demographic-only personas simulate poorly. NN/g's synthesis of three 2024-2025 digital-twin studies (published 15 Aug 2025, nngroup.com/articles/ai-simulations-studies/) found:

- Interview-grounded twins reached **85%** accuracy on GSS survey questions and 80% on personality assessments; survey-based twins managed 78% for backfilling missing data but only **67%** on entirely new questions.
- Interview-grounding also cut bias substantially versus demographic-only models: political bias down 36-62%, racial bias down 7-38%.
- Synthetic responses had consistently lower standard deviations than human data — differences came out statistically significant but tiny in magnitude (e.g. 1.66 vs. 1.58 on a purchase-likelihood scale).

That last point is why this skill forbids effect-size claims: a real difference can be reproduced directionally while its size is compressed to near-meaninglessness. Practical rules:

1. Prefer, in order: real interview transcripts > support tickets and reviews (`research-review-mining`) > analytics segments (`marketing-product-analytics`) > founder/PM assumptions.
2. Copy verbatim user language into the persona profile (goals, complaints, vocabulary). The persona should speak like the evidence, not like a marketing one-pager.
3. Record provenance and a confidence label (`validated` / `partially validated` / `assumed`) in the profile. Assumed personas are usable for smoke-level persona testing, but every finding they produce must carry the hedge.

## From ICP to Behavioral Spec

An ICP describes who buys; a testable persona describes **how that person behaves in a UI**. For each trait in the profile's trait table, set a value and know its mechanical effect:

| Trait | How to calibrate from evidence |
|---|---|
| Tech fluency | Job role + tool stack from interviews/reviews. Low fluency = no shortcuts, no URL editing, misses hover-only affordances |
| Patience | Support-ticket tone, review complaints about speed. Encode as concrete budgets: max failed attempts per step (e.g., 2) and max wait tolerance (e.g., 10s) |
| Reading style | Skimmers react only to headings, buttons, and errors; encode "do not read body copy unless stuck" |
| Trust posture | Segment norms: finance/health personas hesitate at data requests; encode explicit hesitation checkpoints |
| Error reaction | From review mining: does this segment blame themselves or the product? Determines whether recovery paths get exercised |
| Exploration | Goal-locked personas penalize detours; wanderers surface discoverability issues |

Budget hard numbers into the profile. "Impatient" is not executable; "abandons after 2 failed attempts or any single wait >10 seconds" is.

## Persona Memory and Preference History

Static persona cards under-perform personas that carry state. Two research patterns to apply:

- **UXAgent** (arXiv:2504.09407) persists a memory/interaction log across the session so the simulated user's reactions build on earlier steps (frustration accumulates; a second confusing screen after a first one triggers abandonment sooner).
- **Persona2Web** (arXiv:2602.17003) shows agents personalize better from an implicit preference *history* than from explicit instructions — give the persona 3-5 prior facts ("last app they used for this was X and they left because Y") the agent can draw on rather than only adjectives.

Implementation: keep a running "persona state" note during the session (mood, accumulated friction count, remaining patience budget) and consult it before each action.

## Anti-Sycophancy

The best-documented failure mode of synthetic users is over-agreeableness: they cluster near the mean with too little variance (NN/g, 15 Aug 2025 — synthetic responses showed consistently lower standard deviations and "less diversity in their opinions" than human data), and they validate rather than push back.

Primary evidence for the sycophancy mechanism: *Intersectional Sycophancy* (arXiv:2604.11609, rev. May 2026) ran 768 multi-turn conversations across 128 personas and 3 domains, and found sycophancy varies sharply by model, by domain, and by persona demographics:

- **Model choice dominates.** GPT-5-nano averaged 2.96 vs. Claude Haiku 4.5 at 1.74 (p < 10⁻³²). The weakest case — a confident 23-year-old Hispanic woman persona on GPT-5-nano — averaged 5.33/10.
- **Domain matters.** Within GPT-5-nano, philosophy elicited **41% more sycophancy than mathematics** — subjective, values-adjacent topics pull harder toward validation than checkable ones.
- **It is intersectional.** Sycophancy emerged from *combinations* of perceived user traits, not any single demographic axis.

Two practical consequences. First, note the model you ran the persona on in the session log — sycophancy is model-dependent enough that the same persona pack on a different model is not directly comparable. Second, scale the counter-measures to the surface: a checkout-correctness scenario is closer to "mathematics" (mechanically checkable), while pricing perception, trust and privacy screens, and values-laden copy are closer to "philosophy" and warrant a stricter patience budget plus a mandatory adversarial second pass. (The paper tested math/philosophy/conspiracy domains, not UX surfaces — the mapping to product surfaces is this skill's inference, not the paper's claim.)

Design against sycophancy as a hard constraint:

1. **Patience budgets are mandatory and enforced.** A session where every scenario completes is suspicious by default — check whether budgets were actually applied.
2. **Mandatory abandonment**: when the budget is exhausted, the persona quits and the log records the abandonment point. No heroic completion.
3. **No unearned praise**: the session verdict must name at least one thing that almost made the persona leave; if genuinely nothing did, say so explicitly and flag the scenario as possibly too easy.
4. **Adversarial second pass** (for high-stakes runs): re-run the verdict step asking the persona agent to argue *against* its own positive findings, or run a skeptic persona over the same scenario. Divergence between passes marks low-confidence findings.
5. **No tester knowledge**: the persona cannot use URLs, dev tools, docs, or product knowledge the real person would not have. Navigation happens only via visible UI from the declared entry point.

## Persona-Drift Checks

After ~10-15 steps, LLM agents drift from persona voice back into helpful-QA-engineer voice. Controls:

- Re-read the persona profile at the start of every scenario (fresh session = fresh in-context persona).
- Keep the session log's two channels separate: if QA vocabulary ("affordance", "modal", "validation error") appears in the *persona voice* column, that step is drifted — rewrite it in character or discount it.
- One scenario per browser context. Long mixed sessions accelerate drift and bleed app state (auth, carts) between scenarios.

Drift is only half the problem. The opposite failure — the persona locking into a caricature of its demographic label — is documented in [The fidelity trap](#the-fidelity-trap) below, and looks like *good* adherence. Check both directions: a session is clean when the persona neither slid into QA-engineer voice nor behaved like a stereotype of its segment.

## Low-Confidence Persona Classes

Specialized/enterprise personas (compliance officers, clinicians, procurement leads) and underrepresented identity groups get flattened into caricature. This is now primary-sourced, not a practitioner hypothesis:

- **Persona collapse / homogenization** (*The Chameleon's Limit*, arXiv:2604.24698, Apr 2026): 10 models, 1,144 personas, 26 identity dimensions. Models converge distinct profiles into homogeneous behavior while simultaneously exaggerating between-group differences.
- **Occupational persona bias** (arXiv:2510.21011, rev. Jun 2026): 1.5M+ occupational personas audited against US BLS data across 41 occupations; demographic skews recur across models with unrelated training origins — structural, not a quirk of one vendor.
- **Persona prompting does not fix stereotyping** (arXiv:2509.08484, Sept 2025): persona conditioning changed surface wording without reducing abstraction/stereotyping bias; in-group personas stereotyped as much as out-group ones.

### The fidelity trap

The most counterintuitive finding, and the one that changes how you read a session: **fidelity and stereotyping are coupled, not traded off.** In *The Chameleon's Limit*, every model scoring persona-fidelity ρ > 0.9 also produced between-group divergence of Cohen's d > 6 — against d = 2 being "very large" in human personality research. MiniMax-M2 hit ρ=0.95 with d̄=15.7; Claude Haiku 4.5 ρ=0.95 with d̄=13.7. The authors' reading: high ρ "may simply indicate better caricature manufacturing."

Consequence for this skill: an agent that appears to follow the persona profile *perfectly* is not evidence of a good simulation. Treat flawless persona adherence on a specialized or underrepresented persona as a caricature-risk signal and check the session for stereotyped behavior, not just for drift. This is the mirror image of [Persona-Drift Checks](#persona-drift-checks) — drift is one failure mode, caricature is the opposite one, and a session can only be clean if it avoids both.

### Attribute truncation

Models systematically drop low-salience identity attributes. Mean mention rates in self-introductions across the 10 models tested: gender 89%, country 86%, political ideology 60%, age 33%, **social class 25%**.

This hits exactly the personas this skill cares about: enterprise and specialist roles are defined mainly by *low-salience* traits (domain sub-specialty, seniority, procurement authority, regulatory constraint), which are the first things to get dropped. A "compliance officer" persona easily degrades into a generic professional with a job title attached.

Mitigations for these persona classes:

- Downgrade confidence one level regardless of evidence quality.
- Put the low-salience traits in the scenario tasks themselves, not only in the profile header, so they cannot be silently dropped.
- Lean harder on verbatim domain language from real artifacts (tickets, transcripts, RFPs).
- Route more findings to real-user validation (`software-ux-research`) before acting on them.
- Prefer mechanical findings (broken flows, errors, dead ends) from these personas; discount their preference and emotion signals more aggressively than for validated mainstream personas.
