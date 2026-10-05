# qa-testing-mobile — Learnings

## Patterns That Work

## Mistakes to Avoid

## Domain Knowledge

- [2026-07-11] Appium, Detox, and Patrol engine ranges are narrower than "Node 20+" or "any RN"; look up the supported Node/RN ranges in each project's release notes before quoting them. Drizz/TestSprite marketing stats are vendor self-reported, not independently audited -- cite as directional only.
- [2026-09-23] Version pins went stale within one audit pass; look them up rather than refreshing them in the skill. Mann-Whitney regression check must test current > baseline (`mannwhitneyu(current, baseline, alternative='greater')`); the reversed argument order never flags a slowdown.

## Open Questions

## Consolidated Principles
