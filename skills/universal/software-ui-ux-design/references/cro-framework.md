# Conversion Design Hand-off

Where UI design ends and conversion-rate optimisation begins. The CRO process, experiments, funnel analysis and page-type playbooks belong to `marketing-cro`; this file keeps the design-side boundary and the vertical UI benchmarking method.

## Table of Contents

- [Design vs CRO Boundary](#design-vs-cro-boundary)
- [Where to Go in marketing-cro](#where-to-go-in-marketing-cro)
- [Domain-Specific UI Benchmarks](#domain-specific-ui-benchmarks)
- [Related Resources](#related-resources)

---

## Design vs CRO Boundary

| This skill owns | marketing-cro owns |
|-----------------|--------------------|
| Usable, accessible flows and states (see [nielsen-heuristics.md](nielsen-heuristics.md), [form-design-patterns.md](form-design-patterns.md)) | Research-to-hypothesis process, prioritisation (ICE/PIE) and the test backlog |
| Visual hierarchy that makes the primary action obvious | Offer, pricing, copy and value-proposition experiments |
| Trust and reassurance *patterns* at the point of risk (security cues, policy links near payment) | Which trust signals and social proof to show, and measuring their effect |
| Variant designs that are each shippable on their own | Sample size, test duration, analysis and rollout decisions |
| Removing friction the heuristics already call a defect | Funnel instrumentation and conversion reporting |

Rules at the seam:

- Fix known usability and accessibility defects before testing them; an A/B test is not needed to prove that a missing label or a hidden error hurts.
- Optimise in order of leverage: value proposition and critical flows before page layout, and page layout before colour or wording tweaks.
- Never ship a "winning" variant that breaks accessibility, honesty (no fake scarcity or confirmshaming) or consent-design rules; see [wcag-accessibility.md](wcag-accessibility.md#dark-patterns-and-consent-design-eu).
- When the question is "should we run an experiment or a study?", use [experiment vs research decision](../../software-ux-research/references/ab-testing-implementation.md).

## Where to Go in marketing-cro

| Need | Reference |
|------|-----------|
| Landing pages | landing-page-optimization.md, audit with landing-audit.md |
| Checkout | checkout-optimization.md |
| Forms and sign-up | form-optimization.md, audit with form-audit.md |
| Pricing pages | pricing-page-optimization.md |
| Social proof and trust | social-proof-trust-signals.md |
| Mobile conversion | mobile-cro.md |
| Funnel drop-off analysis | funnel-analysis.md |
| Test plans and prioritisation | ab-test-plan.md, ice-scoring.md |

---

## Domain-Specific UI Benchmarks

Benchmark a product's UI against the strongest products in its vertical, by flow, not by screenshot.

### Pattern themes by vertical

| Vertical | Patterns worth benchmarking |
|----------|-----------------------------|
| **Fintech / neobanks** | Fee and exchange-rate transparency before commitment; progressive KYC with clear document-capture guidance; transfer initiation depth from the dashboard; card freeze and security controls within one or two taps; notifications that show amount, counterparty and status at a glance |
| **E-commerce / marketplaces** | Guest checkout visibility; checkout step count and field count; search and filter quality; seller and review trust signals (photo reviews, return policy near the buy button); saved items and cart recovery; return-flow clarity |
| **SaaS / productivity** | Time to first meaningful outcome; empty states that offer templates or examples; command palette and keyboard shortcuts for power users; collaboration presence indicators; interactive onboarding rather than tooltip tours |
| **Healthcare / telehealth** | Booking depth to a confirmed appointment; wait-time and queue transparency; triage clarity; plain-language privacy and data-handling cues; accessibility beyond the AA minimum for older and ill users |

Treat any numeric target (steps, seconds, taps) as a hypothesis to measure against the products you compare, not as an industry standard.

### Benchmarking method

1. Pick two or three leading products in the vertical and one direct competitor.
2. Complete the key flows as a real user (sign-up, first core action, payment or booking, cancellation), recording screens and timing.
3. Use pattern libraries (for example Mobbin, Page Flows, Refero) to fill gaps for flows you cannot complete yourself.
4. Build a comparison matrix and rank gaps by the leverage order above.

```markdown
| Flow | Your product | Leader 1 | Leader 2 | Gap | Evidence |
|------|--------------|----------|----------|-----|----------|
| Steps to first core action | | | | | recording link |
| Time to first core action | | | | | recording link |
| Fields at sign-up | | | | | screenshot |
| Recovery from the most common error | | | | | screenshot |
```

5. Hand confirmed gaps to design; hand "which fix converts better" questions to marketing-cro as test candidates.

## Related Resources

- [nielsen-heuristics.md](nielsen-heuristics.md) — usability evaluation before optimisation
- [modern-ux-patterns.md](modern-ux-patterns.md) — interaction patterns
- [Experiment vs research decision](../../software-ux-research/references/ab-testing-implementation.md)
