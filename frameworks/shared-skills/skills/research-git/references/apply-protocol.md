# Apply Protocol

## Table of Contents

- [Prerequisites](#prerequisites)
- [Apply Workflow](#apply-workflow)
- [Conflict Resolution](#conflict-resolution)
- [Multi-Skill Insights](#multi-skill-insights)
- [Reverting an Apply](#reverting-an-apply)
- [Common Apply Mistakes](#common-apply-mistakes)
- [Definition of Done](#definition-of-done)

How to merge approved insights from a research pack into target skills. This is the opt-in Phase 6 — only run after the user reviews the research pack.

## Prerequisites

Before running the apply phase:
1. ✅ Research pack exists at `docs/research/<scan-id>.md`
2. ✅ User has reviewed the pack
3. ✅ User has explicitly approved which insights to merge (column "Approved?" in the pack)
4. ✅ Each approved insight has: source URL, commit SHA, license, target skill, target file

If any of these are missing, STOP and complete them first.

## Apply Workflow

### Step 1: Group insights by target skill

Even if the research pack covers 5 different target skills, apply them one skill at a time. Never modify multiple unrelated skills in one apply run — it makes review harder and creates fuzzy commits.

### Step 2: For each target skill, plan the changes

For each approved insight going to this skill, decide:

| Action | When | Example |
|--------|------|---------|
| **New reference file** | The insight is a self-contained topic with no existing equivalent | New `references/storekit-2-iap-flows.md` |
| **Append to existing reference** | The insight extends a topic the file already covers | Add a section to `references/swift-concurrency-diagnostics.md` |
| **Update SKILL.md table** | The insight is a quick-reference row | Add a row to the Quick Reference table |
| **Update SKILL.md prose** | The insight is a top-level workflow change | Update the When To Use section |
| **Update data/sources.json** | Always — for audit trail | Every apply touches sources.json |

### Step 3: Apply with attribution

For each change, follow the attribution rules in [attribution-rules.md](attribution-rules.md):

- New file: attribution at the top
- New section: HTML comment citation at the start
- Table row: inline source link
- sources.json: full entry with commit SHA

### Step 4: Verify the apply

After making changes:
1. Read the modified file to confirm the change is in place
2. Run any skill validator (e.g., `skill-validator` plugin) on the target skill
3. Check that the file structure is still valid (frontmatter, headings, links)

### Step 5: Commit per target skill

One commit per target skill, with a clear message:

```
feat(software-ios-native): merge 3 patterns from twostraws/Swift-Concurrency-Agent-Skill

- Add references/swift-actor-isolation-patterns.md (new)
- Extend references/swift-concurrency-diagnostics.md with TaskGroup section
- Update SKILL.md Quick Reference with concurrency row
- data/sources.json: add twostraws repo with commit SHA

Source: github.com/twostraws/Swift-Concurrency-Agent-Skill@abc1234, MIT license
```

This makes the apply phase fully auditable.

## Conflict Resolution

If an approved insight contradicts existing content in the target skill:

1. **STOP** — do not silently overwrite
2. Present both versions to the user with the source for each
3. Ask which version is correct (or whether both should coexist with version/date qualifiers)
4. Only proceed after explicit guidance

## Multi-Skill Insights

If a single insight applies to multiple target skills (e.g., a Stripe pattern that's relevant to both `software-payments` and `software-ios-native` for StoreKit cross-reference), apply it twice with cross-references:

```markdown
> **Source**: Adapted from [twostraws/X](https://github.com/...). Also referenced in [../software-payments/references/stripe-edge-cases.md].
```

## Reverting an Apply

If a merged pattern turns out to be wrong:
1. Revert the commit (`git revert <sha>`)
2. Add the source to a `data/sources-blacklist.json` in the target skill with the reason
3. Re-run the diff_against_local.sh check next time you scan that author

## Common Apply Mistakes

| Mistake | Fix |
|---------|-----|
| Applying without user approval | Always wait for explicit "approved" markers in the research pack |
| Modifying multiple unrelated skills in one commit | Split into one commit per target skill |
| Forgetting attribution on new content | Always cite source URL + commit SHA |
| Forgetting to update data/sources.json | sources.json is part of every apply, not optional |
| Silently overwriting conflicting content | STOP and ask for guidance on conflicts |
| Skipping the verify step | Always read the file after editing to confirm |
| Verbose commit messages | Keep to 3-5 lines: what merged, from where, license |

## Definition of Done

An apply phase is complete when:
- ✅ All approved insights are merged into target skills
- ✅ Each merged insight has full attribution
- ✅ Each target skill's data/sources.json is updated
- ✅ Each target skill is committed separately
- ✅ The research pack is updated with "applied" markers next to each merged insight
- ✅ The research pack itself is committed for audit trail
