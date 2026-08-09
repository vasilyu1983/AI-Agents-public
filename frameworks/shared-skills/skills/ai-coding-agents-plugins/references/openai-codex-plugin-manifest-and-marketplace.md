# OpenAI Codex Plugin Manifest And Marketplace

Source snapshot: OpenAI Codex commit `7d47056ea42636271ac020b86347fbbef49490aa` (2026-05-22), especially `codex-rs/core-plugins/src/manifest.rs` and the `codex-rs/core-plugins/src/marketplace_*` modules.

## Table Of Contents

- [Design Goal](#design-goal)
- [Manifest Shape](#manifest-shape)
- [Interface Metadata](#interface-metadata)
- [Path Rules](#path-rules)
- [Marketplace Lifecycle](#marketplace-lifecycle)

## Design Goal

Codex treats plugins as bundles that can contribute several capability families without requiring arbitrary code execution during discovery. Use the manifest as the trust and capability boundary.

## Manifest Shape

The Codex manifest loader recognizes these top-level concepts:

- `name`
- `version`
- `description`
- `keywords`
- paths for `skills`, `mcpServers`, `apps`
- `hooks` as paths or inline hook files
- `interface` metadata for UI presentation

For your runtime docs, this is a better baseline than a generic "plugin has tools" model. Plugins may ship prompt assets, external connectors, app mentions, hooks, and UI metadata in one unit.

## Interface Metadata

Codex's interface block supports:

- display name
- short and long descriptions
- developer name
- category
- capabilities
- website, privacy, and terms URLs
- default prompt suggestions
- brand color
- composer icon, logo, screenshots

This matters for a plugin marketplace: install decisions need enough UI metadata to explain what the plugin does before activation.

## Path Rules

Codex validates manifest paths under the plugin root and rejects path traversal or absolute-path tricks. It also caps default prompt count and prompt length.

Copy these constraints:

- require manifest-contributed paths to be plugin-relative
- normalize before activation
- keep interface assets inside the plugin bundle
- cap prompt suggestions so plugin UI metadata cannot consume unbounded prompt budget

## Marketplace Lifecycle

The Codex repo separates:

- installed marketplace records
- marketplace add/remove/upgrade flows
- remote bundle handling
- startup sync
- plugin store state

For a production runtime, treat plugin lifecycle as more than "load a folder":

- install
- verify manifest and bundle
- activate or toggle
- sync with remote/source-of-truth
- upgrade with compatibility checks
- remove and clean stale state

## Traps

- Discovering plugin capabilities by executing plugin code.
- Letting default prompts or screenshots reference files outside the bundle.
- Treating marketplace identity, installed path, and display name as one field.
- Loading hooks before manifest validation and policy checks complete.
