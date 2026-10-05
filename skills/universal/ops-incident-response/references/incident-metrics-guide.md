# Incident Metrics Guide

## Timestamp Contract

Use one definition across the dashboard and postmortems; MTTx names vary between teams. The local convention in this skill is:

- Detection: impact starts → confirmed detection, including user reports.
- Acknowledgement: alert fires → responder acknowledges (record first action separately).
- Mitigation: acknowledgement → user impact stops; residual processing or data repair may remain.
- Resolution: impact starts → verified full recovery, including integrity and delayed work.

Retain raw timestamps and the observation window. Distinguish recovery from administrative incident closure. Report unknown impact start as unknown rather than substituting detection silently.

## Choosing a Measurement

Davidovič's *Incident Metrics in SRE* shows that small samples and variable durations can undermine trend conclusions from means, medians, and high percentiles. Percentiles do not solve sparse incident data; its simulations find especially high variance in tail percentiles (printed pp. 14–15, 24–28).

Use durations descriptively with sample size, service, severity, and observation period. For a process change, measure the step it targets (for example, detection or a repeated response activity), inspect uncertainty, and compare cohorts with consistent incident criteria. Until those comparisons support a conclusion, report improvement as unmeasured. Incident rate needs a declared time or exposure denominator; fewer declared incidents alone does not establish reliability improvement.

Pair response speed with recovery quality: reopen rate, repeated incident class, postmortem completion, and action closure. Define closure as on-time completed actions divided by actions due in the period so recent not-yet-due work does not distort it.

Source: [Google SRE report](https://sre.google/resources/practices-and-processes/incident-metrics-in-sre/), [PDF](https://sre.google/static/pdf/IncidentMeticsInSre.pdf).
