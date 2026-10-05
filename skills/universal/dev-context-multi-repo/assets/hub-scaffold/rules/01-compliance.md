# Rule 01 — Compliance

> **Stub.** Replace with your own regulatory regime. This points at an
> example template; it is illustrative scaffolding, not compliance advice.

Binding compliance constraints for any agent changing code or docs in the
portfolio. Keep this short and non-inferable — the *why* and the full
checklist live in the referenced template.

## Source template

Start from the generic, clearly-labelled example:
`dev-context-engineering/assets/compliance-fca-emi.md`
(swap the FCA/EMI regime references for yours: e.g. PSD2, MiCA, SOC 2,
HIPAA, PCI DSS, or your sector regulator).

## What goes here (replace)

- The 3–6 hard rules an agent must never violate (e.g. "no change to
  &lt;regulated-flow&gt; without a named human approver").
- The gate that blocks merge — see `dev-context-engineering/assets/fca-compliance-gate.yml`.
- Where the evidence/audit trail is recorded.

If a task conflicts with a rule here, stop and surface the conflict.
