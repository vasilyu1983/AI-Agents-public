# Plugin-Only Restriction Recipes

A plugin-only restriction is a settings flag or feature that can only be enabled by certain trusted settings sources. Not every source is equally trusted to unlock plugin surfaces.

## Table of Contents

- [The Core Problem](#the-core-problem)
- [Trust Classes](#trust-classes)
- [Recipes](#recipes)
- [Invariants](#invariants)
- [Anti-patterns](#anti-patterns)
- [Related](#related)

## The Core Problem

Without source-aware trust, a user who edits their local `settings.local.json` can enable a plugin surface that an operator intended to be locked to managed policy. The merge layer must track *which source set a value* so trust rules can be enforced at apply time, not just at read time.

## Trust Classes

| Trust class | Sources included | Can enable plugin surfaces? |
|-------------|-----------------|----------------------------|
| `policy` | `distro_policy`, `managed_policy` | Yes — full plugin authority |
| `user` | `user` settings file, CLI flags | Only if `distro_policy` / `managed_policy` have not restricted plugins |
| `project` | `project` settings file | Only for scoped project-level plugin activations if allowed by user/policy |
| `local` | `local` settings file | Never — lowest trust; plugin enables from local are ignored |

## Recipes

### Recipe 1 — Lock a plugin surface to policy-class sources only

Scenario: your runtime ships a `network_search` built-in that is off by default. You want it enabled only when an operator explicitly allows it via managed policy.

**Settings schema:**

```json
{
  "network_search": {
    "type": "boolean",
    "default": false,
    "plugin_only": true,
    "min_trust_class": "policy"
  }
}
```

**Merge-time enforcement:**

```python
def apply_value(key, value, source_trust_class, schema):
    field = schema[key]
    if field.get("plugin_only") and field.get("min_trust_class") == "policy":
        if source_trust_class not in ("policy",):
            # Silently ignore; do not error (user should not see "permission denied")
            return
    runtime_state[key] = value
```

**Result:** a user setting `network_search = true` in their `~/.config/agent/settings.json` has no effect unless managed policy also allows it.

### Recipe 2 — Allow project-scoped plugin activation (but not local)

Scenario: your runtime has a `code_execution_sandbox` plugin. You want teams to be able to opt into it by adding it to the checked-in project settings, but individual developers should not be able to enable it machine-locally in their gitignored file.

**Settings schema:**

```json
{
  "code_execution_sandbox": {
    "type": "boolean",
    "default": false,
    "plugin_only": true,
    "min_trust_class": "project"
  }
}
```

**Trust ordering for this recipe:**

```
policy   (enables)
user     (enables, subject to policy ceiling)
project  (enables — min_trust_class = "project")
local    (BLOCKED — below min_trust_class)
```

**Audit log entry** (required for plugin activations):

```json
{
  "event": "plugin_surface_activated",
  "key": "code_execution_sandbox",
  "value": true,
  "source": "project",
  "source_file": "<repo>/.agent/settings.json",
  "trust_class": "project",
  "timestamp": "2026-04-27T10:00:00Z"
}
```

### Recipe 3 — Graduated plugin rollout (managed policy + user opt-in)

Scenario: you are rolling out a new `deep_codebase_index` plugin. You want managed policy to opt specific teams in, and then individual users within those teams to be able to further customize it.

**Step 1 — managed policy enables the surface:**

```json
// managed_policy/plugins.json
{ "deep_codebase_index": { "enabled": true, "max_index_size_mb": 500 } }
```

**Step 2 — user can narrow (but not broaden):**

```json
// user settings.json
{ "deep_codebase_index": { "max_index_size_mb": 100 } }  ← valid: narrows
{ "deep_codebase_index": { "max_index_size_mb": 1000 } } ← REJECTED: exceeds policy ceiling
```

**Ceiling enforcement at merge time:**

```python
def merge_numeric_with_ceiling(key, user_val, policy_val):
    if policy_val is not None:
        return min(user_val, policy_val)  # user can narrow, not broaden
    return user_val
```

### Recipe 4 — Detecting and logging trust-class violations

Rather than silently ignoring low-trust plugin enables, log them so operators can diagnose misconfigured settings files:

```python
def apply_value_with_logging(key, value, source_trust_class, schema, logger):
    field = schema[key]
    min_class = field.get("min_trust_class")
    if field.get("plugin_only") and not trust_satisfies(source_trust_class, min_class):
        logger.warning(
            "plugin_surface_blocked",
            key=key,
            requested_value=value,
            source_trust_class=source_trust_class,
            required_trust_class=min_class,
        )
        return  # Do not apply
    runtime_state[key] = value
```

Surface these log entries in the effective-settings debug view so operators can see "this setting was requested but blocked."

## Invariants

- Plugin-only trust is enforced at **apply time**, after merging — not at read time.
- Trust-class violations must be **silent to the user** (no error thrown) but **logged for operators**.
- The effective-settings view must show which trust class won for plugin-surface keys.
- Local settings (`settings.local.json`) must never enable plugin surfaces. This is unconditional.
- An operator-locked plugin surface can be narrowed by lower-trust sources but never broadened.

## Anti-patterns

- Checking trust class only when writing a settings file, not when applying merged values. Users can edit files directly.
- Allowing `local` settings to enable plugin surfaces "for developer convenience." That is a security boundary, not a convenience setting.
- Treating all boolean flags the same regardless of whether they unlock execution or network surfaces.
- Not logging trust-class blocks — silent failures make debugging impossible.

## Related

- [`settings-precedence-table.md`](settings-precedence-table.md) — Full source-precedence table with override examples
- [`settings-source-precedence-and-managed-policy.md`](settings-source-precedence-and-managed-policy.md) — Source model and managed policy architecture
- [`deferred-tool-policy-layer.md`](deferred-tool-policy-layer.md) — How ToolSearch trigger is settings-gated
