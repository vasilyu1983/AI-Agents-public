# PMF Bet Memo Template

A bet memo is the bridge between *evidence* (PMF Insight Engine digest + scorecard) and *action* (one experiment, one owner, one kill criterion). One memo per active bet. Maximum length: two pages. Decisions, not narration.

If the team can't fit the bet on this template, the bet is too vague. Tighten it.

---

## 0. Bet metadata

| | |
|---|---|
| **Bet ID** | `<initials>-<yyyy-mm>-<slug>` (e.g. `vu-2026-05-arabic-25-34-onboarding`) |
| **Owner** | <single named person> |
| **Reviewer** | <person who calls go/no-go at end> |
| **Decision date** | <when the kill/scale call gets made> |
| **Stage** | hypothesis / running / scaled / killed |
| **Linked detector(s)** | e.g. `01-hidden-lover-segment`, `03-activation-not-predictive` |
| **Linked scorecard dimension** | e.g. `sean_ellis`, `retention_w4` |

## 1. The blind spot (what the data showed)

Quote 1-3 specific rows from the PMF Insight Engine digest. Do not paraphrase. Numbers must come from the detector output, not from intuition.

> Example:
> Detector #1 fired: `locale=ar × age_band=25-34, n=78, pmf_score=0.46, blended_pmf_score=0.31` — there is a hidden lover-segment we are not currently targeting in onboarding or messaging.
> Detector #3 also fired on the same segment: candidate activation event `daily_digest_full_view` has r²=0.18 with M2 retention — our current activation metric does not predict retention for this segment.

**Why this is a blind spot, not just a finding:** in 1-2 sentences, name what would have been *missed* if only blended dashboards were read. The bet memo must justify why this needs an experiment now, not next quarter.

## 2. The hypothesis

Single sentence, formal structure:

> If we **<change>**, then **<segment>** will **<measurable outcome>** by **<magnitude>** within **<timeframe>**, because **<mechanism>**.

> Example:
> If we replace the generic onboarding with a 4-step Arabic-localized flow anchored on the daily digest, then Arabic-locale 25-34 users will reach the new candidate activation event `digest_personalized` at >=40% within their first 7 days (currently 8%), because the digest is the value moment for that segment per detector #1 + the user-research notes from May 2026.

Avoid:
- Hypotheses that don't name a segment (the engine exists to *prevent* this).
- Hypotheses without a magnitude (we cannot kill them later).
- Hypotheses that bundle multiple changes (we won't know which one moved the metric).

## 3. The bet

Describe the change in 5-10 lines, no more. Concrete enough that an engineer can scope it in 1 day.

- **What we will build/change:**
- **What we will NOT build:** *(scope discipline matters more than ambition here)*
- **Cost estimate:** <person-weeks>
- **Reversibility:** *(easy / medium / hard — feeds into kill criterion)*

## 4. Success metric (single, primary)

```
metric:        <event or computed metric>
formula:       <how it is computed>
data source:   <PostHog query / dashboard URL>
target:        <strong/good/tipping band from the relevant scorecard>
read at:       <date / cohort age>
```

A bet has *one* primary success metric. Anything else is a guardrail or instrumentation, not the bet's outcome.

**Guardrails (any of these regress = stop the bet):**
- <metric 1 with current value and tolerable floor>
- <metric 2 with current value and tolerable floor>

## 5. Kill criterion

```
If <primary metric> has not reached <minimum acceptable value> by <date>,
we will <stop / revert / hand back to discovery>.
```

The kill criterion is a contract with the future. Specific, time-bounded, named.

## 6. What this displaces

What other work is *not* happening because we chose this bet? Naming it forces priority discussion now instead of after the bet runs.

- Displacing: <project / feature / area>
- Reasoning: <why this bet beats it on leverage = magnitude × addressability × evidence>

## 7. What we'll learn even if it fails

A failed bet should still produce one decision-grade learning. Name it now.

- If the bet fails *and* segment retention does not move → <conclusion>
- If the bet succeeds *but* primary metric stays flat → <conclusion>

## 8. Cross-detector check

Did any *other* detector also fire on the same segment? List them. Multi-detector hits are higher-confidence bets; single-detector bets need an explicit "we're betting on one signal" disclosure.

| Detector | Fired? | Reinforces or contradicts this bet? |
|---|---|---|
| 01 hidden-lover-segment | Y | reinforces |
| 02 inverted-retention | N | — |
| 03 activation-not-predictive | Y | reinforces (informs the new activation event) |
| 04 pricing-value-mismatch | N | — |
| 05 churn-precursor-7-14d | Y | informs guardrail metric |
| 06 switching-trigger-clusters | Y | informs hero copy |
| 07 negative-reverse-feature | N | — |
| 08 unmet-adjacent-job | N | — |
| 09 free-tier-corpse | N | — |
| 10 distribution-decay | N | — |

## 9. Sign-off

| Role | Name | Decision | Date |
|------|------|----------|------|
| Owner | | proposed | |
| Reviewer | | approved / blocked | |
| Engineering | | scoped / cannot scope | |

---

## How to use this template

1. **Generate** from the PMF Insight Engine digest: pick the highest-leverage detector hit (`magnitude × addressability × evidence`).
2. **Score check**: confirm the dimension this bet moves is one of the lowest 2 dimensions on the relevant scorecard (`pmf-scorecard-b2b.yaml` or `pmf-scorecard-b2c.yaml`).
3. **Single-page draft**: complete sections 0-7 in <30 minutes. If you can't, the evidence is too thin — go back to discovery.
4. **Reviewer pass**: someone who didn't write it must read it cold and predict the outcome before approval.
5. **Run, then close**: at the decision date, the reviewer writes the outcome on this same memo and links to the next bet (scale, kill, or revise).

## Common traps

- **Bet that protects current investment.** The bet is not "let's prove existing thing works." Genuinely consider that the engine surfaced a real blind spot.
- **Bet without a specific user segment.** Re-read detector #1 — every bet should name a segment.
- **Multiple primary metrics.** Pick one. Others are guardrails.
- **No kill criterion.** Without it, the bet runs forever and crowds out new bets.
- **Reviewer is the same as the owner.** Never. Use a peer or skip-level.

## What changes after the bet

- **Won:** scorecard dimension moves up by >=1 band; ship to broader segment; create next bet to expand or stack.
- **Killed:** scorecard dimension stays flat; document the learning, retire the hypothesis, return engineering capacity to the displaced work or to the next-highest-leverage detector hit.
- **Inconclusive:** treat as a kill. The bet was poorly designed if you can't tell.
