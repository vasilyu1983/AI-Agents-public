# Rendering & Export

## Table of Contents

- [Choosing a renderer](#choosing-a-renderer)
- [Export templates](#export-templates)
- [Export presets per platform](#export-presets-per-platform)
- [Shipping](#shipping)
- [Export gotchas beyond templates](#export-gotchas-beyond-templates)
- [Save systems (and the `.res` security trap)](#save-systems-and-the-res-security-trap)
- [Multiplayer (high-level `MultiplayerAPI`)](#multiplayer-high-level-multiplayerapi)

## Choosing a renderer

Godot ships multiple rendering methods. Pick by **target**, not by which looks best in the editor. `as of Godot 4.7, July 2026 — verify` the exact names and capabilities for your minor version. For lighting/GI and shader-stutter strategy on top of the renderer, see `rendering-and-shaders.md`:

| Renderer | Use for | Trade-off |
|----------|---------|-----------|
| **Forward+** | Desktop, modern GPUs | Most features (clustered lighting, SDFGI); heavier on low-end/mobile |
| **Mobile** | Phones and tablets | Tuned for tiled mobile GPUs; fewer high-end features |
| **Compatibility** | Web and old/low-end hardware | GLES-lineage; widest reach, fewest features |

- Set the method in **Project Settings → Rendering → Renderer**. Some features silently no-op on a renderer that doesn't support them — test the visual on the actual target renderer.
- For a web build, Compatibility is the safe default; confirm your effects work there before committing to them.

## Export templates

- Exporting requires **export templates** matching the **exact editor version**. Install them via *Editor → Manage Export Templates*.
- A version mismatch fails silently or produces a broken binary — reinstall templates every time you upgrade the editor. This is the single most common export failure.

## Export presets per platform

- Configure presets in **Project → Export** (one per platform: Windows, macOS, Linux, Android, iOS, Web).
- Each preset controls architecture, features, icons, and signing. Strip debug for release builds.
- Android needs the SDK + a debug/release keystore; iOS needs an Xcode project and Apple signing; web produces a `.wasm` + HTML shell that must be served with the right COOP/COEP headers for threaded builds — `as of Godot 4.7, July 2026 — verify` current header/threading requirements.
- **C# web export is not supported in stable** as of 4.7 (July 2026) — a prototype was demoed but has not shipped. Route any web target to a GDScript project; do not promise a C# browser build. Re-verify per release.
- **Android on-device export (GABE)** — `as of Godot 4.7, July 2026 — verify`: the Godot Android Build Environment (GABE) companion app shipped **stable** in 4.7, letting you run a Gradle export (AAB/APK) directly on an Android or XR device — including projects using Play Billing/AdMob plugins — without a PC in the loop. Useful for mobile-only teams, but the desktop `godot --headless --export-release` path remains the reliable CI story; don't assume feature parity between the two toolchains without checking the current release notes.
- **No official console export.** Godot ships no first-party PlayStation/Xbox/Nintendo Switch export target — the open-source/MIT model is structurally incompatible with console NDAs. Shipping to a console SKU means licensing a third-party porting/middleware vendor (e.g. W4 Games) as a separate dependency, on its own version-support cadence (often lagging the current Godot minor) and its own pricing/support terms. Budget for this as a distinct workstream, not a checkbox on the export-presets list, and re-verify vendor Godot-version coverage before committing to a target release.

## Shipping

- Build headless in CI: `godot --headless --export-release "<preset name>" <output-path>`. The runner needs the matching editor + templates installed.
- Sign/notarize per store rules (Apple notarization, Android signing, Microsoft Store packaging). These rules change — `verify per platform` before a release.
- Verify the **exported release build** launches and plays on-device, and that the headless CI export matches a manual export. An exported build behaves differently from `F5` in the editor (paths, threading, renderer availability).

### Export gotchas beyond templates

- The export ships a **`.pck`** (or embeds it in the binary). Encrypt it with an export-time key if protecting source matters — small runtime decryption cost, and the key still ships in the binary, so treat it as a speed bump.
- CI runners need a **freshly imported** `.godot/imported/` cache before export. Import headless once (`godot --headless --import`) before `--export-release`, or you hit stale/missing `.import` artifacts that only reproduce on the runner.
- Strip unused import formats / resources to cut binary size for mobile and web.

## Save systems (and the `.res` security trap)

- For save data, prefer **`FileAccess` + `JSON.stringify`/`JSON.parse`** (or **`ConfigFile`** for simple key-value settings). Store under `user://` (the writable per-user path), not `res://` (read-only in an export).
- **Do not** load `ResourceSaver`/`.tres`/`.res` save files that could be user-modified or downloaded from an untrusted source. Resource deserialization can instantiate scripts — a maliciously crafted `.res` can execute arbitrary GDScript on load. Custom `Resource` classes are fine for data you author yourself; they are **not** safe as a user-shared save format.
- Persist input remapping and settings alongside the save (a common omission that breaks accessibility and controller support).

## Multiplayer (high-level `MultiplayerAPI`)

- Use the built-in high-level API over ENet: `MultiplayerSynchronizer` for replicated state, `@rpc(...)` annotations (`any_peer`/`authority`, `reliable`/`unreliable`, `call_local`) for remote calls.
- Design **server-authoritative**: never trust client-reported position/health without validation — the same "adversarial vs cosmetic" judgment applies as in any networked game.
- **Physics is not bit-deterministic** across platforms or under frame-rate variance. Do not rely on client-side physics matching the server's (no naive lockstep replay); reconcile via server-authoritative snapshots. This also constrains replay systems and rollback netcode.
