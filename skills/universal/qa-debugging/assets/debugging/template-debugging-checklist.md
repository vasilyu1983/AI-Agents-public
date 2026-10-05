# Debugging Checklist Template

Copy into the ticket or session notes. For a one-page version use
`template-debugging-worksheet.md`. For incident command, communications, and postmortems use
`../../../ops-incident-response/assets/runbook-template.md` and
`../../../ops-incident-response/assets/postmortem-template.md`.

## 1. Signature and Scope

```
Failure signature (error + first in-our-code frame): ______________________
Request / trace ID: ____________  Build SHA: ____________  Env: ____________
First seen (timestamp): ____________  Repro rate: ___ / ___ runs
Expected vs actual: ______________________________________________________
Impact ongoing?  [ ] yes -> mitigate first, capture evidence a restart would destroy
                 [ ] no
Changes in window (all of them, not just the last deploy):
  [ ] deploys (every involved service)  [ ] flags  [ ] config pushes  [ ] migrations
  [ ] dependency / cert / quota expiry  [ ] autoscaling / infra  [ ] traffic mix  [ ] cron
```

## 2. Hypotheses (write the prediction before testing)

```
| # | Hypothesis | Evidence for | If true, test X shows Y | Result |
|---|------------|--------------|-------------------------|--------|
| 1 |            |              |                         |        |
| 2 |            |              |                         |        |
| 3 |            |              |                         |        |
Next test chosen because it splits the most remaining hypotheses: __________
Evidence searched that would REFUTE the leading hypothesis: ______________
```

## 3. Time-Box Checkpoints

```
30 min:  Can I state the failure signature and repro rate? If not, stop and capture
         (trace, core, recording, stack dump) instead of re-running.
60 min:  2-3 hypotheses disconfirmed and the next is a guess? Stop guessing; add
         instrumentation that answers one specific question.
120 min: No converging evidence? Change approach (bisect, rr, input minimization,
         different environment) or escalate with the evidence gathered so far.
```

## 4. Root Cause and Evidence Bar

```
Root cause: ______________________________________________________________
Mechanism (which variable, how it reaches the symptom): __________________
Evidence path:
  [ ] fail-before / pass-after reproduction with a mechanism-specific intervention
  [ ] direct forensic evidence (core, causal trace, corrupt record, immutable artifact)
      that rules out the credible alternatives
  [ ] neither -> label `probable`, list residual uncertainty: _________________
Recurrence of a cause already patched elsewhere?  [ ] yes -> design note + guardrail
```

## 5. Fix and Verification

```
[ ] Fix changes the causal variable, not a downstream symptom
[ ] Original reproducer passes; adjacent edge cases checked
[ ] Regression test at the lowest effective layer: ______________________
[ ] Intermittent bug: re-measured failure rate over ___ runs (was ___)
[ ] Production: regressed metric back to baseline on the same traffic slice
[ ] Debug code, temporary flags, and scoped instrumentation removed
```

## 6. Prevention

```
Detection gap (signal that should have alerted earlier): _________________
Guardrail (see template-root-cause-to-guardrail.md): ______________________
```
