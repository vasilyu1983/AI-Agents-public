# MR/PR Quality Signals

## Table of Contents

- [Core Metrics](#core-metrics)
- [Rubber Stamp Detection](#rubber-stamp-detection)
- [Review Distribution](#review-distribution)
- [MR Throughput Benchmarks](#mr-throughput-benchmarks)
- [How This Skill Uses MR Data](#how-this-skill-uses-mr-data)

Benchmarks and thresholds for merge request and pull request quality analysis.

---

## Core Metrics

### PR Size

| Tier | Lines Changed (insertions + deletions) | Interpretation |
|------|---------------------------------------|----------------|
| Elite | < 250 LOC | Easy to review, focused changes |
| Good | 250-500 LOC | Manageable, may need focused review session |
| Warning | 500-1000 LOC | Difficult to review thoroughly; consider splitting |
| Red flag | > 1000 LOC | Likely to be rubber-stamped; split is almost always better |

Source: Google Small CLs guidance, PRPulse research.

### Time to First Review

| Tier | Time | Interpretation |
|------|------|----------------|
| Elite | < 2 hours | Rapid feedback loop; review is prioritized |
| Good | < 4 hours | Healthy review cadence |
| Acceptable | < 24 hours | Within one working day |
| Red flag | > 24 hours | Bottleneck; may indicate capacity or prioritization issues |

Source: Google Code Review Speed, PRPulse benchmarks.

### Review Depth

| Signal | Measurement | Benchmark |
|--------|------------|-----------|
| Comments per 100 LOC | (total review comments / LOC changed) * 100 | 2-10 is healthy range |
| Below 2 | Rubber stamp indicator | |
| Above 15 | May indicate pedantic review or significant quality issues | |

### Self-Merge Rate

| Rate | Interpretation |
|------|----------------|
| 0% | All MRs reviewed by someone else |
| < 5% | Occasional emergency self-merge (acceptable with documented reason) |
| 5-10% | Warning: review process being bypassed regularly |
| > 10% | Red flag: review culture issue |

### Rework Rate

Definition: percentage of MRs that require a bug-fix follow-up within 48 hours of merge.

| Rate | Interpretation |
|------|----------------|
| < 10% | Healthy — issues caught in review, minimal post-merge fixes |
| 10-25% | Moderate — some review gaps, but within normal range |
| > 25% | Red flag — insufficient review depth or testing before merge |

---

## Rubber Stamp Detection

A merge request is likely rubber-stamped when multiple signals converge:

| Signal | Detection |
|--------|-----------|
| Approval time << PR size | Approval within minutes on 500+ line PR |
| Zero comments on substantial changes | > 100 LOC changed with no review comments |
| Generic approval | "LGTM" or "looks good" without specific observations |
| Rapid merge after approval | Merged within seconds of approval |
| Same reviewer pattern | Same person always reviews (and always approves) |

### Rubber Stamp Risk Score

Count how many signals are present per MR:
- 0-1: Normal
- 2-3: Review quality concern
- 4+: Likely rubber stamp

---

## Review Distribution

| Metric | Healthy | Concerning |
|--------|---------|-----------|
| % of team participating in reviews | > 70% | < 40% |
| Review load concentration | No single reviewer handles > 30% of all MRs | One person reviews > 50% |
| Cross-team reviews | Regular | Never |

---

## MR Throughput Benchmarks

Context-dependent — calibrate per team, but research suggests:

| Role | Expected MRs Merged/Week (as author) |
|------|---------------------------------------|
| IC Engineer | 2-4 |
| Senior IC | 2-5 |
| Tech Lead | 1-3 (lower due to review + mentoring load) |
| Engineering Manager | 0.5-2 (when coding) |

---

## How This Skill Uses MR Data

From `mr-acceptances.csv`, the skill extracts:

1. **D1 (Delivery Consistency)**: MR throughput per week as measure of delivery cadence
2. **D3 (Commit Craft)**: PR size distribution, self-merge rate
3. **D4 (Review & Collaboration)**: Review participation rate (MRs merged as non-author)

### Known Limitations

- MR CSV contains merger identity, not reviewer identity. A merger may not have been the reviewer.
- Source branch to author mapping is approximate (based on commit history in the same repo).
- Review comments, approval timestamps, and review cycles require API data not available in the CSV.
- Self-merge detection depends on identity alias resolution accuracy.
