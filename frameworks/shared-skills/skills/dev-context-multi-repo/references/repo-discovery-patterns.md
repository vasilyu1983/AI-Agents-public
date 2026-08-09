# Repo Discovery Patterns

Use shallow discovery first.

Priority signals:
- `.git/`
- root manifests
- CI configuration
- workspace files such as `pnpm-workspace.yaml`, `nx.json`, `turbo.json`
- spec artifacts such as `SPEC.md`, `specs/`, `plans/`, `docs/specs/`

Exclude by default:
- `.archive`
- build artifacts
- vendored dependencies
- generated clients

Classify before scanning deeply:
- standalone repo
- monorepo root
- package inside workspace
- legacy or archived repo

