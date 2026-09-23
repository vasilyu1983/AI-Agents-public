---
name: foundations-measurement-theory
description: Audit what scores and instruments measure. Use when auditing construct validity, measurement error, reliability, scales, calibration, invariance, or instrument drift.
version: "1.0"
last_validated: 2026-09-17
---

# Measurement Theory Foundations

Establish whether an observation supports its intended interpretation and decision. A repeatable score can consistently measure the wrong thing.

## When to use

**Use when** a task asks whether a metric, questionnaire, benchmark, sensor, rating, or composite score measures its intended target, or whether scores can be compared across groups, instruments, or time.

**Do not use when** the task is only sampling uncertainty, causal identification, choosing an action, or implementing an evaluation pipeline. Those belong respectively to [statistical inference](../foundations-statistical-inference/SKILL.md), [causal inference](../foundations-causal-inference/SKILL.md), [decision theory](../foundations-decision-theory/SKILL.md), and [ai-evals](../ai-evals/SKILL.md).

## Workflow

1. Define the intended interpretation, population, decision, and cost of measurement error. Identify what is observed and what remains latent.
2. Choose the physical-measurement or psychometric branch in [measurement primitives](references/measurement-primitives.md). Do not translate psychometric reliability into metrological traceability, or treat benchmark scores as physical quantities without justification.
3. Audit the instrument with the eight primitives below. Use evidence actually available; mark missing evidence rather than supplying thresholds or validity claims.
4. For score comparisons, read [comparability and drift](references/comparability-and-drift.md). Preserve instrument versions, scoring changes, administration conditions, and population differences.
5. Complete the [measurement audit template](assets/templates/measurement-audit.md), using the [synthetic example](references/completed-example.md) only as a format example.

## Quick Reference

Eight primitives:

| Primitive | Required decision |
|---|---|
| Construct/measurand | Specify the target, domain, population, and intended use. |
| Operationalization | Identify observation, instrument, scoring, and construct underrepresentation or irrelevant variation. |
| Validity | Evaluate evidence for this interpretation and use; never infer validity from reliability alone. |
| Reliability/precision | Specify what is replicated: items, raters, occasions, tasks, or instruments; estimate the relevant uncertainty. |
| Scale/transformations | Identify meaningful comparisons and operations; an arbitrary zero does not support ratio claims. |
| Error/uncertainty | Separate systematic bias, random error, missingness, and uncertainty in the measurement model. |
| Calibration/traceability | Identify reference and scope; calibration of a probability forecast is different from metrological calibration. |
| Invariance/drift | Determine whether the same interpretation survives group, time, setting, and instrument changes. |

## Completion criteria

Return a **supported**, **conditional**, or **insufficient** verdict for each intended interpretation, with evidence and restrictions. A verdict is an audit conclusion, not certification. Name the missing evidence and the smallest study or calibration needed to resolve it.

Do not use universal Cronbach alpha cutoffs. Internal consistency alone establishes neither unidimensionality, test-retest stability, agreement, nor validity. Keep item-level ordinal responses separate from assumptions used to analyze a composite.

## Fact-Checking

Check source scope against the intended interpretation. Distinguish established definitions, empirical validation evidence, and synthetic illustrations. Sources were inspected through 2026-09-17; verify later standards or instrument changes before describing them as current.

## Navigation

- [Measurement primitives](references/measurement-primitives.md) — definitions, assumptions, and counterexamples.
- [Comparability and drift](references/comparability-and-drift.md) — cross-group and longitudinal checks.
- [Completed example](references/completed-example.md) — synthetic benchmark audit.
- [Output template](assets/templates/measurement-audit.md) — deliverable structure.
- [Dated primary sources](data/sources.json) — source scope and verification cutoff.
