# Team Contribution Quality Calibration: {Team Name}

Generated: {date}
Analysis window: {start_date} to {end_date}

## Team Summary

- Total: {total_persons} persons ({scored_count} scored, {insufficient_count} insufficient data)
- Tier distribution: {tier_distribution}
- Mean quality: {mean_pct}%

## Comparison Matrix

| Person | Tier | Score | D1 | D2 | D3 | D4 | D5 | Commits | MRs |
|--------|------|-------|----|----|----|----|----|---------|-----|
{comparison_rows}

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

## Outliers

{outlier_section}

## Individual Highlights

{individual_highlights}

## Calibration Context

- Scoring model: 6 dimensions (D1-D5 scored, D6 context-only)
- Data tier: {data_tier}
- CC-* rules from software-clean-code-standard
- {additional_context}
