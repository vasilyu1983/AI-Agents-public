# Insight Mining (Mode A — Skills)

How to identify what's worth extracting from a fetched agent-skill repo — and what to skip. For practice-scan mining, see [practice-scan-targets.md](practice-scan-targets.md). For code-pattern mining, see [code-pattern-mining.md](code-pattern-mining.md).

## What to Extract (high value)

| Type | Why | Example |
|------|-----|---------|
| **Version-specific gotchas** | Time-bound, expensive to rediscover | "Stripe v20 Invoice type doesn't have `.subscription` directly" |
| **Working code patterns** | Verified, copy-paste-ready (with attribution) | "Lazy-init Stripe client with proxy pattern to avoid build-time crashes" |
| **Anti-patterns with rationale** | Documented dead ends | "Never hardcode `payment_method_types: ['card']`" |
| **Citations to primary sources** | Pointers to docs/papers/issues you didn't know existed | Link to a specific WWDC session, RFC, or postmortem |
| **Edge cases** | Bug-prevention knowledge | "ICU plurals break on locales with 4+ plural forms" |
| **Test fixtures and setup recipes** | Reduces ramp-up time | Working test harness for a tricky integration |
| **Diagnostic commands** | Tools that surface real issues | `xcodebuild -showBuildTimingSummary` flag combinations |

## What NOT to Extract (low value)

| Type | Why to skip |
|------|------------|
| Generic best practices | "Write tests" — already known, no signal |
| Prose explanations of how things work | LLMs already know the basics |
| Prompt boilerplate | "You are a helpful assistant..." — universal filler |
| Marketing/positioning text | "This skill helps you write better code" — meta-noise |
| Author opinions without evidence | "I prefer X over Y" with no rationale |
| Tutorials for absolute beginners | Wrong audience, doesn't help an experienced agent |
| Content already in your local equivalent | Use diff_against_local.sh to filter this out |

## The Diff-Against-Local Filter

Before extracting anything, compare the external skill to your local equivalent:

```bash
scripts/diff_against_local.sh \
  docs/research/<scan-id>/raw/twostraws__SwiftUI-Agent-Skill/ \
  frameworks/shared-skills/skills/software-ios-native/
```

The diff identifies:
- **Reference files external has that local lacks** → potential new content
- **Sections in external SKILL.md not in local** → potential new patterns
- **Citations external has that local lacks** → new primary sources to check
- **Versions external mentions that local doesn't** → potential time-bound updates

Only patterns flagged as novel by the diff should be extracted. Everything else is duplicate.

## Quality Filter

For each candidate insight, ask:

1. **Is it specific?** "Use lazy initialization" is generic. "Lazy-init Stripe client with proxy pattern to avoid build-time crashes from `process.env.STRIPE_KEY` being undefined at module load" is specific.

2. **Is it evidence-backed?** Does the insight reference a version, a commit, a docs link, or a real failure mode? Or is it just opinion?

3. **Is it dated?** Did the source mention a date or version range? Insights without date context decay fast.

4. **Does it survive the "obvious to a senior dev" test?** If yes, skip it. The signal lives in non-obvious patterns.

5. **Is it falsifiable?** Could you write a test or check that proves it true or false? If not, it's vibes, not knowledge.

## Extraction Output Format

For each insight worth keeping, capture:

```markdown
### Pattern: <short name>

**Source**: https://github.com/<owner>/<repo>/blob/<commit-sha>/references/<file>.md
**Extracted**: 2026-04-23
**License**: MIT

**The pattern**:
<1-3 sentence description in your own words — not copy-paste>

**Why it matters**:
<evidence from the source — what failure does this prevent?>

**Where it goes**:
- Target skill: `software-ios-native`
- Target file: `references/swift-concurrency-diagnostics.md`
- Action: append new section / update existing section / create new file

**Novel vs local**: new (not present in local)

**Confidence**: high (cited in source), medium (single mention), low (inferred)
```

## Common Mining Mistakes

- **Extracting prose without verifying it's specific** → fills the catalog with filler
- **Skipping the diff step** → duplicates existing content, creates contradictions
- **Copy-pasting verbatim** → license violation + voice drift
- **Extracting anything that "sounds smart"** → optimize for actionable, not impressive
- **Ignoring date/version context** → ages-out fast, becomes wrong quickly
- **Failing to capture confidence level** → downstream consumers can't judge reliability
