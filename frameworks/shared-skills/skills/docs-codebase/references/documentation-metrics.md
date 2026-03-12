# Documentation Metrics

How to measure documentation quality, coverage, and health across a codebase.

---

## Core Metrics

Track four dimensions. Each serves a different decision.

| Metric | What It Answers | Signal Source |
|--------|----------------|---------------|
| **Coverage** | Is it documented at all? | Code-to-docs ratio |
| **Freshness** | Is it still current? | Git timestamps, page views |
| **Accuracy** | Does it match reality? | Broken examples, user reports |
| **Findability** | Can people locate it? | Search analytics, support tickets |

---

## Coverage Measurement

Coverage = documented items / total items. Measure per category.

**What to count:**

| Category | "Total" Source | "Documented" Source |
|----------|---------------|---------------------|
| API endpoints | OpenAPI spec or route files | API reference docs |
| Config options | Schema or `.env.example` | Configuration guide |
| Error codes | Error constants file | Troubleshooting docs |
| CLI commands | Command registry | CLI reference |
| Public functions | Exported symbols | JSDoc / docstrings |

**Script pattern (API endpoints):**

```bash
# Count routes in source
TOTAL=$(grep -rc "router\.\(get\|post\|put\|delete\)" src/routes/ | awk -F: '{s+=$2} END {print s}')

# Count documented endpoints
DOCUMENTED=$(grep -c "^### " docs/api-reference.md)

echo "Coverage: $DOCUMENTED / $TOTAL ($(( DOCUMENTED * 100 / TOTAL ))%)"
```

Set a coverage floor per category. 90% for API endpoints, 80% for config, 70% for error codes is a reasonable starting point.

---

## Freshness Scoring

Combine time-based and behavior-based signals.

**Time-based signals:**

```bash
# Days since last edit per doc file
for f in docs/**/*.md; do
  days=$(( ($(date +%s) - $(git log -1 --format=%ct -- "$f")) / 86400 ))
  echo "$days days: $f"
done | sort -rn
```

**Freshness tiers:**

| Tier | Age | Action |
|------|-----|--------|
| Fresh | < 90 days | No action |
| Aging | 90-180 days | Review next quarter |
| Stale | 180-365 days | Flag for rewrite or archive |
| Dead | > 365 days | Archive or delete |

**Behavior-based signals (stronger than timestamps):**

- Doc references a dependency version 2+ majors behind
- Code path documented has been deleted or renamed
- Page gets zero views for 90+ days (if analytics available)
- Related source file changed but doc file did not

---

## Quality Indicators

Track these as automated checks, not manual audits.

**Broken links:** Run `markdown-link-check` in CI. Zero tolerance -- every broken link is a bug.

**Outdated screenshots:** Flag images older than 6 months. No automated fix; add to quarterly review queue.

**Stale code examples:** Extract fenced code blocks, run them. Any non-zero exit is a doc bug.

**Readability drift:** Run `textstat` or Vale. Flag pages where Flesch-Kincaid grade exceeds 12.

**Terminology inconsistency:** Use Vale with a project vocab file. Flag mixed usage of the same concept (e.g., "log in" vs "sign in" vs "authenticate").

---

## Dashboard Design

**Weekly (automated, async):**
- Broken link count
- CI doc-test pass rate
- New pages created vs pages archived

**Monthly (team review):**
- Coverage percentages per category
- Freshness distribution (% fresh / aging / stale / dead)
- Top 10 stalest pages
- Support tickets traceable to missing docs

**Quarterly (planning input):**
- Coverage trend over time
- Time-to-resolution for doc-related support tickets
- Pages archived vs pages rewritten
- Docs NPS or CSAT if collected

---

## Tooling

| Need | Tool | Integration |
|------|------|-------------|
| Link checking | `markdown-link-check` | CI on every PR |
| Prose linting | Vale with Google/Microsoft style | CI on every PR |
| Spell check | cspell with project dictionary | CI on every PR |
| Code example testing | `markdown-code-runner` or custom extract-and-run | CI nightly |
| Freshness reporting | Custom git-log script | Cron, posts to Slack |
| Coverage reporting | Custom route-vs-docs diff | CI on release branches |
| Analytics | Plausible, PostHog, or Google Analytics | Docs site |

---

## Benchmarks and Thresholds

Decision guide for what to do when metrics cross a line.

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| API coverage | > 90% | 70-90% | < 70% |
| Config coverage | > 80% | 60-80% | < 60% |
| Broken links | 0 | 1-3 | > 3 |
| Stale pages (>180d) | < 10% | 10-25% | > 25% |
| Doc-test pass rate | 100% | > 90% | < 90% |

**When to flag:** Yellow metrics go on the next sprint backlog.

**When to rewrite:** Page is stale + low accuracy + still gets traffic. Rewrite from scratch rather than patching.

**When to archive:** Page is stale + zero traffic + referenced feature is deprecated. Move to an archive folder, remove from navigation.

---

## Anti-Patterns

- **Vanity dashboards.** Tracking total page count instead of coverage ratio. More pages is not better.
- **Manual-only audits.** If metrics require a human to compute them, they will not be computed. Automate or skip.
- **Measuring without acting.** A dashboard nobody reviews is waste. Assign owners to each metric threshold.
- **Precision theater.** Reporting coverage to two decimal places when the denominator is a rough estimate. Round to the nearest 5%.
- **Ignoring behavior signals.** A page edited yesterday can still be wrong. Combine timestamps with code-change correlation.

---

## Related Resources

- [documentation-testing.md](documentation-testing.md) - Automated quality checks
- [docs-as-code-setup.md](docs-as-code-setup.md) - CI/CD integration for docs
- [writing-best-practices.md](writing-best-practices.md) - Content quality standards
