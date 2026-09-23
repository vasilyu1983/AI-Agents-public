# Scoring and Evidence Gates

## Contents

- [Rule Ladder](#rule-ladder)
- [Ranking Score](#ranking-score)
- [Aggregator Output](#aggregator-output)
- [Evidence Quality Gates](#evidence-quality-gates)
- [Window Comparison and Citation Velocity](#window-comparison-and-citation-velocity)
- [Adoption Gate](#adoption-gate)

The gate is rule-decided; the score only ranks. A deterministic rule ladder sets `gate_status`; the numeric score never changes a gate decision — it only orders rows *within* a bucket. This removes the old failure mode where a subjective `applicability` guess (default 3) flipped promote/kill.

## Rule Ladder

First match wins for the gate:

1. trap 11 or 12 present → `kill`
2. three or more trap tags → `kill`
3. `evidence_grade == F` → `kill`
4. `shape == negative-result` → `background` (exempt from low-score kill — a falsified method you considered is *information*, not noise)
5. corroboration below 2 distinct `source_type` sharing one `cluster_id` → cap at `validate`
6. `reproducibility == proprietary` → cap at `validate`
7. `evidence_grade == D` → cap at `validate`
8. any of traps {1,5,6,8} present → cap at `validate`
9. else → `promote`

## Ranking Score

Ordering only, never gates: `(applicability x evidence_strength x reproducibility) / (lift x trap_penalty)`, with per-trap numeric adjustments from [known-traps.md](known-traps.md#scoring-effect) (`evidence -1` for trap 2, `applicability -1/-2` for traps 3/9, `lift +1 tier` for trap 4).

Weights: `applicability` 1-5 (default 3); `evidence` A=5 B=4 C=3 D=2 F=1; `reproducibility` code+benchmarks=5, code_only=4, paper_only=2, proprietary=1; `lift` inverse low=1 medium=3 high=5; `trap_penalty` 1.0 plus 0.5 per non-hard trap.

## Aggregator Output

The aggregator emits `gate_status` (`promote` / `validate` / `kill` / `background`), `gate_reason`, `score` (rank-only), and `corroboration` (`yes` / `no` / `unreliable-no-cluster_id`). Do not promote `kill` rows; `background` rows go in the report's Background section, not the shortlist.

## Evidence Quality Gates

Enforced by the rule ladder, not advisory:

| Gate | Minimum | Enforced by |
|------|---------|-------------|
| Cross-source corroboration | two or more distinct `source_type` sharing one `cluster_id` for `promote` | Rule 5 — caps at `validate` if unmet (no longer a decorative column) |
| Evidence grade | C or higher to `promote` | Rule 7 (D → `validate`), Rule 3 (F → `kill`) |
| Reproducibility | `paper_only` minimum to enter shortlist | Rule 6 (`proprietary` → `validate`, never `promote`) |
| Trap tags | 0-1 ok; 2 → cap `validate`; 3+ → `kill` | Rules 2, 8 plus hard-kill rule 1 |
| Negative results | never killed for low score | Rule 4 → `background` |

## Window Comparison and Citation Velocity

Use citations-per-month-since-publication rather than raw counts to avoid penalising recent papers. Operational thresholds use the Semantic Scholar `influentialCitationCount` field:

- **Emerging** — first influential citations within 90 days of publication with an accelerating monthly rate (month-over-month increase of at least 1 influential citation); sparse in the 365d window
- **Cresting** — more than 10 influential citations in the last 60 days; mentions accelerating across arXiv, HF Papers, and curator sources — attention signal requiring evaluation
- **Mature** — stable influential-citation rate over 90d-365d, at least 2 independent implementations; safest to adopt
- **Declining** — influential-citation rate falling for 2 or more consecutive 30-day windows; likely superseded — investigate the successor

**Cross-source corroboration:** count independent originating studies and reproductions, not paper/newsletter/repository mentions of the same release. Attention alone does not raise evidence quality.

## Adoption Gate

Citation velocity labels attention, not deployability. Before recommending adoption, require a comparable baseline, an evaluation that matches the target failure mode, at least one independently operated implementation or reproduction where feasible, and a prototype kill criterion tied to the target stack. A `cresting` method that fails any of these remains `validate`; "adopt now or be late" is never a gate reason.
