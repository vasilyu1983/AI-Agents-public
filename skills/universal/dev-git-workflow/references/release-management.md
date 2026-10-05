# Release Management

Release *process* decisions: versioning scheme, what triggers a release, tags, hotfixes, and rollback. Commit-message rules and changelog/release tooling setup (semantic-release, release-please, changesets, commitlint) are owned by [dev-git-commit-message](../../dev-git-commit-message/SKILL.md), in particular its [changelog generation guide](../../dev-git-commit-message/references/changelog-generation-guide.md).

## Contents

- [Choosing a Versioning Scheme](#choosing-a-versioning-scheme)
- [SemVer Judgment Calls](#semver-judgment-calls)
- [Choosing a Release Trigger](#choosing-a-release-trigger)
- [Tags](#tags)
- [Release Branches and Hotfixes](#release-branches-and-hotfixes)
- [Rollback](#rollback)
- [Release Checklist](#release-checklist)
- [Release Notes and Announcements](#release-notes-and-announcements)

## Choosing a Versioning Scheme

| Artifact | Scheme | Reason |
|----------|--------|--------|
| Library, SDK, CLI, public API | SemVer (semver.org) | Consumers pin ranges; the version number is the compatibility contract |
| Continuously deployed service or web app | CalVer (`YYYY.MM.N`) or build number/commit SHA | Nobody pins it; the useful question is "when" and "which build" |
| Mobile app | user-facing version plus a strictly increasing build number | Stores reject non-increasing build numbers; one user-facing version can have many builds |
| Internal package in a monorepo | SemVer per package, or one fixed version for all | Independent versions if packages have outside consumers; fixed if they always ship together |

Pick one scheme per artifact and write it down. Mixing schemes across a project's history makes range pins and automation misbehave.

## SemVer Judgment Calls

- **Deprecation** is a MINOR change; **removal** is MAJOR.
- **0.x versions** promise nothing: the spec allows anything to change. Package managers' caret ranges treat a 0.x MINOR bump as breaking, so bump MINOR for breaking changes during 0.x and PATCH otherwise. Leave 0.x once external users depend on you.
- **A security fix that must break behavior** is still MAJOR. If you ship it as a PATCH for urgency, say so prominently in the release notes and advisory.
- **Behavior people rely on** counts as API even if undocumented. When unsure whether a fix breaks consumers, treat it as breaking or put it behind an opt-in.
- **Pre-releases** (`2.0.0-rc.1`) sort before the release and are excluded from normal ranges; use them for release candidates, not as a permanent channel.

## Choosing a Release Trigger

| Trigger | Choose when | Watch out for |
|---------|-------------|---------------|
| Manual (a person tags and publishes) | rare releases, few consumers | forgotten steps; make it a scripted checklist |
| Controlled: a bot opens a release PR with the version bump and notes; merging it releases | default for most libraries; you want a human gate and a reviewable changelog | the release PR goes stale if nobody owns merging it |
| Fully automated on every merge to main | every merge to main is releasable and commit/PR-title conventions are enforced | a mislabeled commit publishes the wrong version; there is no gate |

Automation that pushes version-bump or changelog commits directly to main conflicts with rulesets that require PRs. Prefer tools that open release PRs or only create tags and releases; if a bot must push, give that bot identity a narrow, audited bypass rather than loosening the rule for everyone.

Publish from CI with short-lived credentials (for example, OIDC-based trusted publishing where the registry supports it) rather than long-lived tokens in repository secrets. Supply-chain controls for published packages (provenance, signing) are owned by [dev-dependency-management](../../dev-dependency-management/SKILL.md).

## Tags

- Use annotated (`git tag -a`) or signed (`git tag -s`) tags for releases; lightweight tags carry no tagger or date.
- Never move or delete a published release tag. Consumers and caches have already resolved it. If a release is bad, publish a new version.
- Protect release tag patterns (`v*`) with rulesets: no updates, no deletion, creation only by the release process.
- Tag the exact commit CI built and tested; build release artifacts from the tag, not from a branch tip that may have moved.

## Release Branches and Hotfixes

Model-specific hotfix paths are in [branching-strategies.md](branching-strategies.md#hotfix-path-by-model). The rules that apply everywhere:

- Upstream first: fix on main, then `git cherry-pick -x` into each supported release branch.
- A hotfix contains only the fix and its test; no drive-by changes.
- A hotfix still runs the full required checks. An emergency bypass of review is recorded, time-boxed, and followed by a post-merge review.
- After a GitFlow hotfix, merge it into develop and any open `release/*` branch the same day; the forgotten back-merge is the classic regression.

## Rollback

Decide in advance which of these applies, because they differ by artifact:

| Artifact | Rollback | Notes |
|----------|----------|-------|
| Deployed service | redeploy the previous known-good artifact, then fix forward | Rolling back code does not roll back database migrations; make migrations backward-compatible (expand, migrate, contract) so the previous artifact still runs |
| Package in a registry | publish a new PATCH that reverts the change; move the default dist-tag or channel back to the last good version; deprecate or yank the bad version | Most registries never allow republishing or overwriting an existing version number |
| Mobile app | ship a new build; use server-side flags to disable the feature meanwhile | Store review delays make remote flags the only fast lever |
| Git history on main | `git revert` the offending commit(s) or merge (`-m 1`) | Never reset shared branches |

A release that cannot be rolled back (irreversible migration, external API contract change) needs a named owner and an explicit go decision before it ships.

## Release Checklist

Before:

- [ ] Version bump matches the changes (breaking changes flagged in notes with migration steps)
- [ ] The exact commit to release passed required checks; artifacts built from it
- [ ] Migrations are backward-compatible with the previous artifact, or a rollback exception is approved
- [ ] Rollback path for this artifact type written down

During:

- [ ] Tag created by the release process, protected
- [ ] Publish from CI with short-lived credentials
- [ ] Smoke test the released artifact, not a local build

After:

- [ ] Error rates and key metrics watched for the agreed window
- [ ] Release notes published; linked issues closed
- [ ] Fixes landed on release branches are also on main (and develop, if GitFlow)

## Release Notes and Announcements

Release notes are for consumers: lead with breaking changes and required actions, then new features, then fixes. Link the migration guide and the full changelog. For security fixes, link the advisory and state which versions are affected and fixed; publish the advisory through the host's security-advisory mechanism, with a CVE or advisory ID where one is assigned.
