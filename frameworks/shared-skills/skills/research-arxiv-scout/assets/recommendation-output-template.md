# Research Recommendation Output Template

Use this template for an arXiv scouting report (full) or a short summary (compact).

## Full report

```markdown
# arXiv Research Scout Report

Target: [Skill/GPT Name]
Domain: [Extracted focus area]
Generated: YYYY-MM-DD

Attribution (required for arXiv data):
Thank you to arXiv for use of its open access interoperability.

## Search parameters

arXiv categories: cat1, cat2, cat3
Keywords: keyword1, keyword2, keyword3
Time window: Last N months (YYYY-MM-DD to YYYY-MM-DD)
Papers reviewed: X total, Y shortlisted

## Recommended papers

### 1) [Score: X.X/10] Paper title

Authors: Last et al.
arXiv: https://arxiv.org/abs/YYYY.NNNNN
Submitted: YYYY-MM-DD
Categories: cs.XX, cs.YY

Verified links (optional):
- Code: https://github.com/org/repo
- Dataset: https://example.com/dataset

Why relevant:
- Point 1: Specific reason tied to the target
- Point 2: Practical benefit
- Point 3: Technique/pattern to apply

Key contribution:
[1-2 sentence summary based on abstract/available metadata]

Limits/risks:
- [Constraint, assumption, missing details]
- [Generalization risk]

Suggested action in this repo:
- [Concrete change proposal, file/folder target]

### 2) [Score: X.X/10] Another paper title

[Repeat format]

## Follow-up searches

- [cat:... AND ...]
- [cat:... AND ...]
- [cat:... AND ...]

## Verification log

Checks performed:
- PASS: arXiv IDs are exact
- PASS: All arXiv links resolve to abstract pages
- PASS: Titles/authors match abstract pages
- PASS: No unverified metrics included (citations/stars/acceptance omitted unless verified)
```

## Compact summary (email/slack)

```markdown
arXiv Scout: [Skill Name]
Time window: Last N months

Top 3 papers:
1) [9.2/10] Paper title (YYYY) - https://arxiv.org/abs/YYYY.NNNNN
   Why: [one-line relevance]
   Action: [one-line action]

2) [8.7/10] Another paper (YYYY) - https://arxiv.org/abs/YYYY.NNNNN
   Why: [one-line relevance]
   Action: [one-line action]

3) [8.5/10] Third paper (YYYY) - https://arxiv.org/abs/YYYY.NNNNN
   Why: [one-line relevance]
   Action: [one-line action]

Attribution:
Thank you to arXiv for use of its open access interoperability.
```
