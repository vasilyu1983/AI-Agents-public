# PMF Survey Analysis Template

How to read a Sean Ellis PMF survey as a product decision. The question wording lives in one place: `marketing-product-analytics/assets/sean-ellis-survey-template.md` (Q1-Q7, plus optional Q8-Q10 for NPS, usage frequency and role). Do not copy the questions here; wording drift breaks detector #1 ingestion in the PMF Insight Engine.

Send only to recent, repeat users: people who have used the product at least 2x in the past 2 weeks. Exclude churned, one-time and brand-new users. Aim for at least 40 qualifying responses per segment before acting on that segment's percentage; the analytics template's n=30 floor gives a directional read only (about +/-17pp at 40%). Always report the count. The survey diagnoses who the product fits; the PMF gate is a flattening retention curve per cohort and segment (see [pmf-measurement.md](../../references/pmf-measurement.md#sean-ellis-survey-design)).

**PMF signal (Q1)**: >40% "Very disappointed" is a heuristic line, not a pass mark. At n=40 a 40% reading has a 95% interval of roughly 26-55%, so report n with every percentage.

**Which answer feeds which analysis step** (question numbers refer to the analytics template):

| Analytics Q | Use in this guide |
|---|---|
| Q1 disappointment | Segment split and action bands (Steps 1, 4) |
| Q2 who would benefit | Sharpen the ICP for the "Very disappointed" profile |
| Q3 main benefit | Positioning and marketing copy: use the most common answers |
| Q4 improvement | Cluster by theme; high-frequency themes from "Very disappointed" users are the highest-leverage improvements |
| Q6 alternative | "General tool" or "wouldn't look" means you own the category; a specific competitor means you need to differentiate |
| Q8-Q10 (optional) | Average NPS column, usage-frequency split, role and team-size split |

---

## Analysis Guide

### Step 1: Segment Responses

Split all responses by:
- Sean Ellis answer (Very disappointed vs others)
- User segment (ICP match, plan type, company size)
- Usage frequency

### Step 2: Profile Your "Very Disappointed" Users

These are your core audience. Analyze:
- Who do they say benefits most? (Q2)
- What benefit do they get? (Q3)
- What do they want improved? (Q4)
- What would they use instead? (Q6)

### Step 3: Compare Segments

Fill this table once per segment, with the segment's n in the heading.

| Metric | Very Disappointed | Somewhat | Not Disappointed |
|--------|------------------|----------|-----------------|
| Count | | | |
| % of total | | | |
| Who they say benefits most | | | |
| Most common benefit | | | |
| Most common alternative | | | |
| Top improvement request | | | |
| Average NPS (if Q8 used) | | | |

### Step 4: Action Items

These bands are heuristics per segment, and they only diagnose. Confirm any call against that segment's retention curve before acting on it.

- **If >40% Very Disappointed**: Strong must-have signal in this segment. If its retention curve also flattens, double down and improve what they love; if the curve keeps falling, suspect who was surveyed before celebrating.
- **If 25-40%**: Promising. Focus on converting "Somewhat" to "Very" — usually means better onboarding or removing friction.
- **If <25%**: Weak must-have signal. Before pivoting, check whether one segment scores well and is being averaged away; if none does, narrow the ICP or change the product.

### Step 5: Track Over Time

Run this survey quarterly. Track the trend, not just the snapshot.

| Quarter | Segment | Very Disappointed % | NPS | Responses (n) | Notes |
|---------|---------|-------------------|-----|---------------|-------|
| <Quarter 1> | | | | | |
| <Quarter 2> | | | | | |
| <Quarter 3> | | | | | |
| <Quarter 4> | | | | | |
