# Evidence Packaging

Use this file when the research output needs to be auditable or reusable.

## Keep These Layers Separate

- raw sources
- extracted evidence notes
- comparison matrix or working memo
- final synthesis

## Minimum Research Ledger

For each source, keep:

- title
- URL or canonical identifier
- source type
- access date
- evidence excerpt or summary
- confidence or caveat note

## Synthesis Rule

- Claims in the final brief should map back to specific sources.
- Tag assumptions, inferred conclusions, and unresolved gaps explicitly.

## Source-Grading Rubric

Score every source on two axes, separately — do not collapse them into one number. A source can be highly reliable but not credible on the claim at hand (a well-maintained vendor blog is reliable, but is not a credible source for an unbiased benchmark of that vendor's own product), or credible but unreliable (a domain expert's unarchived tweet).

**Reliability** — how trustworthy is this *source* as a document, independent of the claim:

| Score | Criteria |
|-------|----------|
| 3 — High | Primary document (spec, filing, paper, official API/product doc), stable URL, named author or institution, verifiable publication date |
| 2 — Medium | Secondary reporting with named sourcing (trade press, reputable news, maintained docs that cite primaries) |
| 1 — Low | Unattributed aggregator, SEO content farm, forum post, undated page, or a page that itself cites no primary source |
| 0 — Reject | Model-generated text presented as a source (A4), a page that fails a URL-health check, or a source behind a paywall you have not actually read |

**Credibility (for this claim)** — how much authority does this source have on the *specific claim* being cited, independent of how reliable the document is in general:

| Score | Criteria |
|-------|----------|
| 3 — High | The source is the origin of the claim (the paper that reports the number, the vendor that sets its own price, the regulator that issued the rule) |
| 2 — Medium | The source has direct subject-matter standing but is not the origin (a domain expert restating a primary finding, a competitor's documented comparison) |
| 1 — Low | The source is adjacent to the topic but not authoritative on this specific claim (a general news outlet citing a stat with no link to the origin) |
| 0 — Reject | The source has no domain standing on this claim, or the claim is outside what the source actually asserts (citation laundering, A6) |

**How to use both scores**:
- Record both numbers per source in the ledger (add two columns to the [source-ledger template](../assets/templates/source-ledger.template.md) if it lacks them), not a blended average.
- A claim entering synthesis needs reliability ≥ 2 AND credibility ≥ 2 from at least one source, or it is a gap, not a finding.
- When two sources disagree, prefer the one with higher credibility on that specific claim, not the one with higher reliability in general (P6, and the contradiction-resolution note in SKILL.md).
- Independence check: before letting two sources corroborate each other, confirm they do not share a common origin (a wire story picked up by five outlets, a press release paraphrased by several blogs) — corroboration from non-independent sources is one data point, not two.
