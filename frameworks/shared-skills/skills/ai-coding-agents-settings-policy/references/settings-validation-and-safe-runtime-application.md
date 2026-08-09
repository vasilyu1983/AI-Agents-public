# Settings Validation And Safe Runtime Application

## Table Of Contents

- [Parse And Validate At The Boundary](#parse-and-validate-at-the-boundary)
- [Preserve Files, Skip Bad Fragments](#preserve-files-skip-bad-fragments)
- [Safe Environment Controls](#safe-environment-controls)
- [Runtime Application Path](#runtime-application-path)
- [Validation Schema Design](#validation-schema-design)
- [Change Notification](#change-notification)
- [Design Rules To Reuse](#design-rules-to-reuse)

## Parse And Validate At The Boundary

The settings layer uses:

- JSON parsing
- schema validation
- targeted filtering for invalid permission rules
- helpful error formatting with paths and suggestions

This is a strong pattern for agent runtimes:

- parse once
- validate once
- convert to a normalized typed structure
- keep runtime code away from raw config blobs

## Preserve Files, Skip Bad Fragments

`parseSettingsFile()` plus `filterInvalidPermissionRules()` show a useful compromise:

- invalid files can remain on disk
- invalid fragments are ignored when safe
- warnings explain what was skipped

Why this matters:

- one malformed rule should not brick the whole runtime
- users need actionable diagnostics
- the runtime should remain usable while the config is fixed

## Safe Environment Controls

`managedEnvConstants.ts` splits env handling into:

- provider-managed env vars that settings must not override
- dangerous shell-related settings
- safe env vars that can be applied before trust dialogs

This is worth copying directly as a control model:

- host-owned provider routing should not be replaceable by user settings
- secrets, endpoints, proxies, and shell helpers need stricter treatment
- only a whitelist of low-risk env vars should auto-apply under managed policy

## Runtime Application Path

`applySettingsChange()` is the key reference.

It:

- reloads settings from disk
- reloads permission rules
- refreshes hook snapshots
- re-derives permission context
- strips unsafe permissions again where needed
- transitions plan or auto mode state
- updates app state in one place

Reusable rule:

- apply settings changes through one central runtime function
- recompute derived state
- avoid scattered ad hoc listeners mutating independent subsystems

## Validation Schema Design

`utils/settings/types.ts` shows several useful patterns:

- backward-compatible schema evolution guidance
- explicit permission schema
- exact-one-of validation for allowlists and denylists
- optional fields for future growth
- exported schema URL for machine-readable tooling

This is stronger than informal config docs because:

- editors can validate settings automatically
- migration rules stay close to the schema
- admin and user tooling can reuse the same contract

## Change Notification

The settings comments indicate:

- caches are reset before listeners run
- both interactive and headless paths use the same application logic

Keep that pattern:

- filesystem or remote notifications should invalidate caches first
- listeners should always read fresh settings
- UI and SDK modes should not have divergent settings-application paths

## Design Rules To Reuse

- Validate at the settings boundary, not deep inside runtime code.
- Preserve files but ignore bad fragments when safe.
- Use env whitelists and provider-managed stripping for dangerous configuration.
- Recompute derived runtime state through one application path.
- Publish a schema and keep backward compatibility explicit.
