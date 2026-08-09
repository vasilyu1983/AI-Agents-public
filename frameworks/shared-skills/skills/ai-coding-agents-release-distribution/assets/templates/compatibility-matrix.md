# Release Compatibility Matrix

Tracks which runtime versions are compatible with which plugin API, cache schema, and settings schema versions. Update this table with every release. Incompatible combinations must be blocked at the upgrade gate.

---

## How to Use

- **Runtime version** — the released version of the coding-agent binary.
- **Plugin API** — the plugin manifest schema version the runtime loads. A plugin compiled against API `v2` will not load in a runtime that only supports `v1`.
- **Cache schema** — the on-disk session-cache format version. Incompatible cache schemas require a migration or a cache wipe on upgrade.
- **Settings schema** — the `settings.json` format version. Incompatible settings require a migration or reset to defaults.
- **Min plugin API** — oldest plugin API the runtime still accepts (for backwards compatibility).
- **Notes** — breaking changes or migration steps required.

---

## Matrix

| Runtime Version | Plugin API | Min Plugin API | Cache Schema | Settings Schema | Notes |
|----------------|-----------|----------------|--------------|-----------------|-------|
| `0.1.x` | `v1` | `v1` | `v1` | `v1` | Initial release |
| `0.2.x` | `v1` | `v1` | `v1` | `v1` | Bug fixes; no schema changes |
| `0.3.x` | `v2` | `v1` | `v1` | `v2` | Settings schema v2 adds `bypassPermissions` field; v1 settings auto-migrated on first launch |
| `0.4.x` | `v2` | `v1` | `v2` | `v2` | Cache schema v2 adds `resume_token`; v1 caches invalidated (wipe required); plugin API v1 still loads with deprecation warning |
| `1.0.x` | `v3` | `v2` | `v2` | `v3` | **BREAKING**: plugin API v1 dropped; cache v2 preserved; settings v3 adds `managedPolicy` block; migrate with `agent migrate-settings` |
| `1.1.x` | `v3` | `v2` | `v2` | `v3` | No schema changes; feature additions only |
| `1.2.x` | `v4` | `v3` | `v3` | `v3` | **BREAKING**: cache schema v3 encrypts session tokens; migration script required (`agent migrate-cache --encrypt`); plugin API v2 loads with deprecation warning |

---

## Upgrade Gate Rules

1. **Plugin API**: if a plugin's manifest `runtime.min_agent_version` is higher than the installed runtime version, refuse to load and surface a clear error.
2. **Cache schema**: if the on-disk cache schema version is newer than the runtime supports, refuse to start and prompt the user to downgrade or wipe.
3. **Settings schema**: if the settings file schema version is newer than the runtime supports, load with defaults and warn. Never silently overwrite user settings.
4. **Downgrade protection**: if the runtime version is lower than the `baseline.min_runtime` recorded in a cache file, refuse to open the cache (downgrade-protection).

---

## Migration Commands

| From → To | Command | Side Effects |
|-----------|---------|--------------|
| Settings v1 → v2 | Automatic on first launch | Adds `bypassPermissions: false` |
| Cache v1 → v2 | Automatic on first launch | Existing sessions lose `resume_token`; they can still be re-opened from transcript |
| Cache v2 → v3 | `agent migrate-cache --encrypt` | Tokens encrypted at rest; old unencrypted cache deleted |
| Settings v2 → v3 | `agent migrate-settings` | Adds `managedPolicy: null`; existing policy rules preserved |
| Plugin API v1 → v2 | Update plugin `plugin.manifest.json` `runtime.min_agent_version` | Plugin author must bump manifest and re-publish |
