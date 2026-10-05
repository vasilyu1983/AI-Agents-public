# Release Workflow Template

Fill this in once per repository and keep it next to the code (for example `docs/RELEASING.md`). The decisions behind each field are in [release-management.md](../../references/release-management.md); changelog and release-tool setup (semantic-release, release-please, changesets) is owned by [dev-git-commit-message](../../../dev-git-commit-message/SKILL.md).

```markdown
# Releasing <project>

## Versioning
- Scheme: <SemVer | CalVer YYYY.MM.N | build number>   <!-- per artifact if several -->
- Source of truth for the version: <file, tag, or tool>
- Breaking-change rule: <what counts as breaking for this project's consumers>

## Trigger
- Mode: <manual | release PR opened by bot, merged by a human | automatic on merge to main>
- Who may release: <team or role>
- Tool: <tool name>; config at <path>; pinned in CI by commit SHA

## Branches and tags
- Releases are cut from: <main | release/x.y>
- Supported release branches: <list, and for how long>
- Tag format: <vX.Y.Z>; annotated or signed; tag pattern protected (no update, no delete)
- Pre-releases: <X.Y.Z-rc.N>, published to channel/dist-tag <next>

## Steps
1. Confirm the release commit passed the full required pipeline.
2. <Merge the release PR | run `<command>`>. The version bump and changelog are produced by <tool>.
3. CI builds artifacts from the tag and publishes with short-lived credentials (<OIDC / trusted publishing | secret name>).
4. Smoke test the published artifact: <command or checklist>.
5. Watch <dashboards / error rates> for <window>.
6. Publish release notes: breaking changes and required actions first; link migration guide.

## Hotfix
1. Fix on main with a regression test; merge through the normal PR path (expedited review allowed, required checks not skipped).
2. `git cherry-pick -x <sha>` onto each supported `release/x.y`; open a PR per branch.
3. Release a PATCH from each branch via the normal steps.
4. <GitFlow only:> merge the hotfix into `develop` and any open `release/*` the same day.

## Rollback
- Service: redeploy <previous artifact id> with <command>; migrations are expand/contract so the previous build runs against the new schema.
- Package: publish a new PATCH that reverts the change, move the default channel back
  (npm: `npm dist-tag add <pkg>@<last-good> latest`), and deprecate the bad version
  (`npm deprecate <pkg>@<bad> "<reason>; use <last-good>"`). Published versions are never overwritten or re-used.
- Git: `git revert <sha>` (or `git revert -m 1 <merge-sha>`) on main through a PR; never reset main or move a release tag.
- Owner who decides roll back vs fix forward: <name or rotation>

## Security releases
- Advisory drafted privately in <host's security-advisory feature>; CVE requested through <CNA or host>.
- Fixed versions: <list>; affected range stated in the advisory and the release notes.
```

## Filling It In

- **Trigger:** a release PR merged by a human is the default for libraries; fully automatic release on every merge fits only when every merge is releasable and commit or PR-title conventions are enforced in CI.
- **Bot commits and rulesets:** if the release tool pushes version-bump commits to main, it collides with "require PR" rules. Prefer a tool mode that opens a release PR or only creates tags; otherwise give the bot a named, audited bypass.
- **Rollback section:** write it before the first release. The common mistakes are reverting a tag range (`git revert v2.1.0..HEAD` reverts everything since the tag, not the release) and trying to republish over a bad version, which registries refuse.
- **Pre-releases:** publish them under a separate channel or dist-tag so `latest` never points at a release candidate.
