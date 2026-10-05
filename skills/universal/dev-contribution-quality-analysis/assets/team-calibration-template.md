# Team Contribution Quality Calibration: {Team Name}

Generated: {date}
Analysis window: {start_date} to {end_date}

## Team Summary

- Total: {total_persons} persons ({scored_count} scored, {insufficient_count} insufficient data)
- Tier distribution: {tier_distribution}
- Mean quality: {mean_pct}%

## Comparison Matrix

| Person | Tier | Score | D1 (context) | D2 | D3 | D4 | D5 |
|--------|------|-------|----|----|----|----|----|
{comparison_rows}

Rows are alphabetical, never sorted by score or volume. `—` marks an unmeasured dimension (insufficient evidence), not a zero.

## Dimension Medians (Team Baseline)

| Dimension | Median | Max | Team % |
|-----------|--------|-----|--------|
{dimension_median_rows}

## Team Quality Distribution

{tier_a_count} Exemplary | {tier_b_count} Solid | {tier_c_count} Developing | {tier_d_count} Concerning

## Team Strengths

- {strength_1}
- {strength_2}

## Team Gaps

- {gap_1}
- {gap_2}

## Reading the Spread

Do not name outliers or call two people different unless their uncertainty intervals separate; otherwise report "no detectable difference". Use this matrix for role-expectation calibration and coaching, not ranking.

{spread_notes}

## Individual Highlights

{individual_highlights}

## Calibration Context

- Scoring model: D2-D5 scored (66 nominal points); D1 and D6 context-only; volume never scored
- Person-level use follows the Individual-Data Policy in dev-ai-coding-metrics: opt-in, shown to the person first, correction path
- Data tier: {data_tier}
- CC-* rules from software-clean-code-standard
- {additional_context}
