# Growth Template: Activation And Retention Diagnosis

Use when growth looks weak but acquisition may not be the root problem.

## Required Inputs

- Acquisition source mix
- Signup or install volume
- First-value event definition
- Activation rate by source, device, platform, or segment
- Retention snapshot
- Monetization or trial-start snapshot if relevant

## Diagnostic Split

| Bottleneck | Evidence | Route |
|---|---|---|
| Acquisition | Few qualified users reach the product | `expert-board` (`marketing-diagnostics`) or `marketing-growth-experiments` |
| Positioning | Users arrive but expect the wrong thing | `expert-board` (`growth`) or `startup-product-marketing-strategist` |
| Activation | Users sign up but do not reach first value | `product-surface`, `expert-board` (`mobile-product`), or `dev-feature-delivery` |
| Retention | Users activate once but do not return | `expert-board` (`product-discovery`) plus analytics |
| Monetization | Users get value but revenue lags | `expert-board` (`monetization`) |
| Measurement | Events cannot support a decision | `expert-board` (`data-analytics`) or `data-instrumentation-analyst` |

## Output Contract

```text
Diagnosis:
- Primary bottleneck:
- Evidence:
- Competing explanation:
- Metric that must improve:
- Smallest next test:
- Required instrumentation:
- Execution team:
- Stop condition:
```

## Guardrails

- Do not prescribe more acquisition until activation quality is understood.
- Do not redesign onboarding from anecdotes alone when event data exists.
- Do not use revenue as the only activation metric unless the product's first value is a purchase.
