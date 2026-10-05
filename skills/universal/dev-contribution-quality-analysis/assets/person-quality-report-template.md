# Contribution Quality Report: {Person Name}

Generated: {date}
Analysis window: {start_date} to {end_date}

## At a Glance

| Dimension | Score | Max | Trend |
|-----------|-------|-----|-------|
| D1 Delivery cadence | context only | — | {d1_trend} |
| D2 Code Quality | {d2_score} | {d2_max} | {d2_trend} |
| D3 Commit Craft | {d3_score} | {d3_max} | {d3_trend} |
| D4 Review & Collaboration | {d4_score} | {d4_max} | {d4_trend} |
| D5 Test & Safety | {d5_score} | {d5_max} | {d5_trend} |
| **Overall** | **{total_score}** | **{total_max}** | |

**Tier: {tier} — {tier_label}** ({pct}% of the measured maximum; unmeasured: {unmeasured_dimensions})

Opt-in report: share with the person first, with the sampled evidence and a correction path.

Role: {role}

## Key Strengths

- {strength_1}
- {strength_2}
- {strength_3}

## Areas for Growth

- {area_1}
- {area_2}

## Detailed Dimension Breakdown

### D1: Delivery cadence (context only; not in tier)

- Weekly commits: mean {mean_weekly}, CV {cv}
- Within-window commit-count ratio: {trend_ratio} (not a quality trend)

### D2: Code Quality ({d2_score}/{d2_max})

- Churn (14-day): {churn_pct} ("unknown" without per-file line history)
- Refactoring ratio: {refactor_pct} ("unknown" without move/rename detection)
- Net lines: +{insertions}/-{deletions} = {net} net
- Complexity delta: {complexity_status}
- CC-* compliance: {cc_status}

### D3: Commit Craft ({d3_score}/{d3_max})

- Message quality: {msg_score}/5 ({generic_pct}% generic)
- Scope: mean {files_per_commit} files/commit
- PR size: P50={pr_p50} LOC, P90={pr_p90} LOC ({small_pr_pct}% under 250 LOC)
- Self-merge: {self_merge_count} ({self_merge_pct}%, 95% CI {self_merge_ci})

### D4: Review & Collaboration ({d4_score}/{d4_max})

- Review participation: {review_rate} review events/week ("unavailable" without forge review events; merges are not reviews)
- Cross-repo: {distinct_repos} meaningful repos
- Review responsiveness: {responsiveness_status}
- Review depth: {depth_status}

### D5: Test & Safety ({d5_score}/{d5_max})

- Test signal: {test_signal_pct}% of commits
- Feature commits with tests: {feature_test_pct}%
- Security awareness: {security_status}

## Sampled Commit Quality

{sampled_commits_section}

## Volume Context (not scored)

- Commits: {commit_count} | MRs: {mr_count} | Active days: {active_days}/{expected_days} ({coverage}%) | MR throughput: {mr_per_week}/week (role baseline {mr_baseline})

## Context and Limitations

- Data tier: {data_tier}
- {limitation_notes}

## Recommended Actions

1. {action_1}
2. {action_2}
3. {action_3}
