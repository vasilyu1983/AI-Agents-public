# Release Compatibility Matrix

Tracks which runtime releases are compatible with which plugin API, cache schema, settings schema, and session-store schema versions. Update it with every release, and block incompatible combinations at the startup gates below.

---

## How to Use

- **Runtime release** — the released version of the coding-agent binary, and the channel it shipped on (stable, pre-release, managed, or a custom distribution ID).
- **Plugin API** — the plugin API version the runtime loads.
- **Min plugin API** — the oldest plugin API the runtime still accepts.
- **Cache schema** — the on-disk plugin and tool-registry cache format version.
- **Settings schema** — the settings file format version.
- **Session-store schema** — the persisted session format version.
- **Min rollback target** — the oldest runtime release that can still read state written by this release.
- **—** in that column means no older runtime can read the newly written state; restore a preserved older-format snapshot or provide a tested reverse migration before declaring a downgrade path.
- **Notes** — breaking changes and the migration each one needs.

Replace the placeholder rows with your own releases. Do not copy version numbers from another product.

---

## Matrix

| Runtime release | Channel | Plugin API | Min plugin API | Cache schema | Settings schema | Session-store schema | Min rollback target | Notes |
|---|---|---|---|---|---|---|---|---|
| `<A>` | stable | `<p1>` | `<p1>` | `<c1>` | `<s1>` | `<r1>` | — | Initial release |
| `<B>` | stable | `<p2>` | `<p1>` | `<c1>` | `<s1>` | `<r1>` | `<A>` | Additive plugin API; old plugins load with a deprecation warning |
| `<C>` | stable | `<p2>` | `<p2>` | `<c2>` | `<s2>` | `<r1>` | — | BREAKING: B cannot read c2/s2 state. Preserve a B-readable pre-upgrade snapshot for restore, or test reverse migrations before claiming B as a rollback target. |

---

## Startup Gate Rules

1. **Plugin host range**: if a plugin's declared host range excludes the installed runtime, refuse to load it and surface a clear error naming the plugin and the range.
2. **Cache schema**: if the on-disk cache schema is newer than the runtime supports, refuse to use it and offer a downgrade-safe rebuild.
3. **Settings schema**: if the settings file schema is newer than the runtime supports, fail closed for policy and restriction keys (deny rules, sandbox, allowed sources, managed-only locks) and load defaults with a warning only for preference keys. Never silently overwrite user settings.
4. **Downgrade protection**: if the runtime is older than the minimum runtime recorded in a cache or session store, refuse to open it and explain why.

---

## Migrations

| From → To | Trigger (automatic on launch or explicit command) | Side effects | Reversible before the rollback window closes? |
|---|---|---|---|
| `<c1>` → `<c2>` | | | |
| `<s1>` → `<s2>` | | | |
