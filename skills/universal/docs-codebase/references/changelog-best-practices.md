# Changelog Best Practices

Decision rules for changelogs in the [Keep a Changelog](https://keepachangelog.com/) format with [Semantic Versioning](https://semver.org/). The format itself (sections, `[Unreleased]`, compare links) is in the spec and in [assets/project-management/changelog-template.md](../assets/project-management/changelog-template.md); this file covers the judgment calls.

## Table of Contents

- [Who the Changelog Is For](#who-the-changelog-is-for)
- [What Goes In](#what-goes-in)
- [Writing Entries](#writing-entries)
- [Breaking Changes and Deprecations](#breaking-changes-and-deprecations)
- [Security Entries](#security-entries)
- [Generated vs Curated](#generated-vs-curated)
- [CI Enforcement](#ci-enforcement)
- [Release Checklist](#release-checklist)

---

## Who the Changelog Is For

The reader is a user deciding whether and how to upgrade, not a maintainer reviewing history. Every entry should answer "does this affect me, and what do I do?" Commit history already serves maintainers.

## What Goes In

- **In:** user-visible behavior, public API and CLI changes, configuration and default changes, dependency floor changes (runtime or platform minimums), deprecations, removals, security fixes.
- **Out:** refactors, test changes, CI changes, internal dependency bumps with no user effect, typo fixes in code.
- **Default changes are behavior changes.** A new default page size, timeout, or sort order goes under `Changed` even when no signature changed; users relying on the old default break.
- Use one category per entry: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. Do not invent categories; tooling and readers scan for these.

## Writing Entries

- Lead with the user-visible effect, then the detail: "Search returns results in under 200 ms for 1M-row indexes (was ~1 s)" beats "Refactored search indexing".
- Be specific: name the endpoint, flag, option, or limit that changed. "Fixed bugs" and "Performance improvements" are not entries.
- Group related commits into one entry; a commit dump is a changelog nobody reads.
- Link each entry to its issue or PR for readers who need detail.
- Every released version has an ISO date (`YYYY-MM-DD`) and a compare link.
- No marketing tone; the changelog is reference material.

## Breaking Changes and Deprecations

- Mark every breaking entry explicitly (`**BREAKING**:`) and put breaking entries first within their section. A reader skimming for upgrade risk must find all of them without reading every line.
- Every breaking entry shows old and new usage or links to a migration guide.
- Every `Deprecated` entry states the replacement and the removal version or date. A deprecation without a removal target is never acted on.
- Every `Removed` entry names the version where it was deprecated, so users can see they were warned.
- A breaking change in a minor or patch release is a versioning bug: fix the version number, do not just document it.

## Security Entries

- Always list security fixes, in `Security`, even when the fix is a dependency bump.
- Include the CVE or advisory ID when one exists, and state affected versions.
- Do not describe the exploit. Link the advisory, and coordinate publication timing with the disclosure process.

## Generated vs Curated

- **Generate** from Conventional Commits when commits are disciplined and the audience is developers who read commit-level detail (libraries, SDKs).
- **Curate** (or generate, then edit) when the audience is end users or operators, or when commit messages are not written for them.
- Generated output still needs a human pass for breaking-change callouts and migration notes; commit messages rarely contain them.
- Pick one generator for the repo and document the commit convention in CONTRIBUTING. Check the tool's current maintenance status before adopting it; several changelog generators have been deprecated in favor of others.

## CI Enforcement

- Require a changelog entry on PRs that touch user-facing paths, with an explicit skip label (for example `no-changelog`) for internal-only changes. A hard requirement with no escape hatch produces junk entries.
- Diff against the PR's merge base, not `HEAD~1`: PR checkouts may be shallow or contain several commits.

```bash
base=$(git merge-base origin/main HEAD)
git diff --name-only "$base"...HEAD | grep -qx 'CHANGELOG.md' || {
  echo "CHANGELOG.md not updated. Add an entry under [Unreleased] or apply the no-changelog label." >&2
  exit 1
}
```

## Release Checklist

- [ ] `[Unreleased]` entries moved under the new version with today's date
- [ ] Version number matches the highest-severity change (breaking → major)
- [ ] Breaking entries marked and first, each with migration path
- [ ] Deprecations name replacement and removal target
- [ ] Security entries carry CVE/advisory IDs
- [ ] Compare links at the bottom updated, including `[Unreleased]`
- [ ] Release tagged in git to match the changelog version
