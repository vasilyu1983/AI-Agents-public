# Idea: {{Clean mechanism name}}

> Re-name the idea by what it *does*. Don't keep the paper's acronym unless it's also descriptive.

**Source(s):** {{primary URL}} {{| code URL}} {{| corroborating curator/blog URL}}
**Method shape(s):** {{prompting-pattern | architecture-tweak | training-recipe | evaluation-method | data-construction-recipe | inference-time-method | system-design-pattern | theoretical-bound | negative-result | survey-or-taxonomy}}
**Discovered via:** {{arXiv search | HF Papers daily | Semantic Scholar citation walk | GitHub (research-git) | conference proceedings | industry blog | curator newsletter}}
**Cluster ID:** {{stable method-identity slug — must match sibling findings about the same method}}
**Window:** {{30d | 90d | 365d}}

---

## What it does (1-2 sentences, plain language)

{{Mechanism in plain language. No "we propose". No jargon shield.}}

## Inputs / outputs / preconditions

- **Inputs:** {{what you need going in}}
- **Outputs:** {{what comes out}}
- **Preconditions:** {{model size, infra, data type, compute requirements}}

## Evidence

| Field | Value |
|-------|-------|
| Empirical claim | {{X improves Y by Z%}} |
| Benchmark(s) | {{name + version}} |
| N | {{number of runs / examples}} |
| Baselines | {{what it was compared against}} |
| Evidence grade | {{A / B / C / D / F}} — see [idea-extraction-framework.md](../references/idea-extraction-framework.md#evidence-grades) |

## Reproducibility

| Field | Value |
|-------|-------|
| Code | {{repo URL or "none"}} |
| Benchmarks | {{linked or "none"}} |
| Compute budget | {{rough — affects who can replicate}} |
| Reproducibility tag | {{code+benchmarks / code_only / paper_only / proprietary}} |

## Why it might transfer to {{target}}

- {{Specific reason 1}}
- {{Specific reason 2}}

## Why it might NOT transfer

- {{Specific risk 1}}
- {{Specific risk 2}}

## Lift estimate

- **Days to first prototype:** {{1-3 / 1-2 weeks / >2 weeks}}
- **Skills required:** {{e.g., training infra, prompt iteration, eval design}}

## How to apply (recipe)

> Pull the matching recipe from [recipes.md](../references/recipes.md) for this method shape.

1. {{Step 1 — concrete and prerequisite-aware}}
2. {{Step 2}}
3. {{Step 3}}

**First measurement:** {{the earliest signal that tells you "keep going" or "stop"}}

**Common pitfalls (from recipe):**
- {{pitfall 1}}
- {{pitfall 2}}

## Kill criteria

- {{Concrete metric or threshold — when to stop pursuing}}
- {{Concrete metric or threshold}}

## Trap tags

> See [known-traps.md](../references/known-traps.md). Multi-tag allowed.

- {{trap-tag-1}}
- {{trap-tag-2}}

## Cross-source corroboration

| Source family | Found? | Pointer |
|--------------|--------|---------|
| arXiv | {{yes/no}} | {{URL or "—"}} |
| HF Papers | {{yes/no}} | {{URL or "—"}} |
| Semantic Scholar (citing graph) | {{yes/no}} | {{N citing papers; URL or "—"}} |
| GitHub reimplementations (via research-git) | {{yes/no}} | {{repo URL + stars or "—"}} |
| Conference | {{yes/no}} | {{venue/year or "—"}} |
| Industry blog | {{yes/no}} | {{URL or "—"}} |
| Curator newsletter | {{yes/no}} | {{URL or "—"}} |

## Status

**Gate:** {{promote | validate | background | kill}}
**Score:** {{from aggregator — ranking only, does not decide the gate}}
**Corroboration:** {{yes | no | unreliable-no-cluster_id}}
**Reason:** {{one-line gate reason from aggregator}}

> `background` = a falsifying negative result or a survey/taxonomy. Not a steal
> candidate; kept as context so the next scan does not re-litigate it.

---

_Output uses arXiv data — Thank you to arXiv for use of its open access interoperability._
