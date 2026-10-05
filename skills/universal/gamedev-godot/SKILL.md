---
name: gamedev-godot
description: "Creates Godot games from empty project to exported build. Use when starting, building, validating, or shipping a Godot 2D/3D game or app."
compatibility: Portable core. Works on Claude Code and Codex. Godot engine facts drift between minor versions; verify volatile numbers and renamed APIs against current primary sources.
version: "1.2"
last_validated: 2026-07-11
---

# Godot Game Creation

Use this skill to take a Godot project from empty editor to a published, exported build using the engine, language, and tooling of the current stable **Godot 4.x** release. Look up the current stable minor and patch in the official release archive and release notes before starting or upgrading a project; the answer decides which node names, defaults, and export caveats apply. The skill covers the durable build spine (prototype → first playable → content → export) and fences the volatile engine layer (renderer names, minor-version API renames, physics-engine defaults, C# and web-export caveats) so you teach what is true for the pinned version, not what was true in Godot 3.

> Version note: treat development snapshots as pre-release until the official archive marks them stable. Pin the exact patch level in CI, not just the minor. Before an upgrade, read the release notes of every minor between the project's version and the target, because defaults change between minors. Past examples: **4.6** made **Jolt the default 3D physics engine** for new projects, [existing projects retain their configured physics engine](https://godotengine.org/releases/4.6/); [**4.7** integrated the **Asset Store**](https://godotengine.org/releases/4.7/); legacy Asset Library links are not automatically broken. Check which addon source the target version uses before pointing contributors at a link.

## Quick Reference

| Stage | Read or Run | Durable default (Godot 4.x) |
|-------|-------------|----------------------------------------|
| **Setup & project** | `references/setup-and-project.md` | One editor install per project via a version manager; commit `project.godot` + source, gitignore `.godot/`; pick **GDScript** unless you have a concrete reason for **C#** (heavier export; check whether the current stable supports C# web export, and if not, web means GDScript) |
| **Language & architecture** | `references/gdscript-and-architecture.md` | `class_name` + `@export` + static typing (`var x: int`); **signals up, calls down**; autoload singletons for cross-scene state; `_physics_process` for physics-synchronized logic; `_process(delta)` for frame-based updates |
| **Build the game** | `references/scenes-and-nodes.md` | Compose with **scenes as reusable prefabs**; keep the node tree shallow; instance scenes, don't deep-nest; `CharacterBody2D/3D` + `move_and_slide()` (velocity in units per second, not multiplied by `delta`); `TileMapLayer` for 2D grids (the monolithic `TileMap` was deprecated in 4.3 — use the editor's one-click migration); **Jolt** became the default 3D physics engine for new projects in 4.6 |
| **Performance & traps** | `references/performance-and-traps.md` | Cache `get_node` results; free with `queue_free()`; pool only when measured spawning/destruction cost warrants it; profile with the built-in profiler + `--verbose`; avoid per-frame allocations in `_process` |
| **Rendering & platforms** | `references/rendering-and-export.md` | Pick the renderer per target (**Forward+** desktop, **Mobile** for phones, **Compatibility** for web/old GPUs); export needs matching **export templates**; test on-device, not just the editor |
| **Ship & polish** | `references/rendering-and-export.md#shipping` | Export presets per platform; strip debug; sign/notarize per store rules (verify per platform); one-button build via `godot --headless --export-release` in CI |

## Game Creation Workflow

1. **Scope to a testable first playable** → verify: one sentence — "a player controls something, can perform the core verb, and has a reason to keep playing." If you can't write it, stop and get it.
2. **Set up the project and repo** → verify: `project.godot` opens in a pinned editor version; `.godot/` is gitignored; a trivial scene runs with F5. See `references/setup-and-project.md`.
3. **Prototype the core verb in one scene** — placeholder art, `CharacterBody2D/3D`, input map → verify: the core verb works with keyboard/gamepad and reads clearly at real speed. See `references/scenes-and-nodes.md`.
4. **Stand up the architecture skeleton** — autoload for global state, signal wiring (signals up, calls down), a scene-per-concept layout → verify: two scenes communicate via signals/autoload without either holding a hard `get_node("../../..")` path to the other. See `references/gdscript-and-architecture.md`.
5. **Reach First Playable** — the core loop is completable end to end; scene transitions work; pause works → verify: someone else finishes the loop without you explaining the controls.
6. **Content pass** — real art/audio, reusable scene prefabs replace placeholders, `TileMapLayer`/`GridMap` for levels, particles and shaders for feel → verify: frame time stays inside budget on a real target device, not just the editor. See `references/scenes-and-nodes.md` and `references/performance-and-traps.md`.
7. **Harden** — profile spawned-object churn before pooling, release obsolete subtrees through their parent or `queue_free()`, remove subscriptions that should stop while their endpoints remain alive, validate saved data on load → verify: walk `references/performance-and-traps.md` Known Traps as a checklist; profiler shows no runaway per-frame allocation or leaked nodes.
8. **Export and ship** — set the renderer per target, install matching export templates, configure export presets, strip debug, sign per platform → verify: an exported release build launches and plays on-device; a headless CI export produces the same artifact. See `references/rendering-and-export.md`.

## Patterns (durable)

- **Scenes are the unit of reuse.** A scene is a prefab: build a thing once (enemy, pickup, UI panel), save it as a `.tscn`, and instance it. Composition over deep inheritance.
- **Signals up, method calls down.** A parent calls methods on its children; a child emits a signal the parent connects to. This keeps children reusable and prevents fragile `get_node("../../..")` coupling.
- **Autoloads for genuinely global state only.** Singletons (game state, audio manager, scene switcher) via Project Settings → Autoload. Do not turn every manager into a global.
- **Synchronize physics logic with `_physics_process`.** Use the physics tick for body movement/collisions; `_process(delta)` can update visuals and non-physics timers using elapsed time ([processing docs](https://docs.godotengine.org/en/stable/tutorials/scripting/idle_and_physics_processing.html)). Multiply accelerations (`velocity.y += gravity * delta`) and manual position or timer changes by `delta`. **Do not multiply the velocity you pass to `move_and_slide()` by `delta`**: it already integrates `velocity` over the physics step.
- **`move_and_slide()` on `CharacterBody`.** Set `velocity` in units per second (`velocity = direction * speed`), call `move_and_slide()`; let the engine resolve collisions. Don't hand-roll integration unless you have a reason.
- **Static typing everywhere.** `var speed: float = 200.0`, typed `@export`, typed function signatures. Enables editor autocomplete, catches errors, and lets the compiler optimize.
- **Profile signal-heavy hot loops.** Keep signals where listener decoupling matters; if measured dispatch cost is material, use direct calls or `get_tree().call_group()` for owned per-frame work.
- **Model pure data as a custom `Resource`, not a Node or Dictionary.** `class_name ItemData extends Resource` with typed `@export`s — inspector-editable, shareable, no scene-tree overhead. The veteran's default for item/ability/stat data.
- **Drop below Nodes when count is the bottleneck.** Nodes wrap the servers; when measured node overhead dominates, consider `MultiMeshInstance2D/3D` / `RenderingServer` (visuals) or `PhysicsDirectSpaceState2D/3D` (bulk queries) — but only when the profiler says so.
- **Prefer `queue_free()` for scene nodes.** Deferred deletion avoids invalidating objects used by the current callback or iteration; child nodes are also deleted when their parent is freed.
- **Decouple the fixed tick from the display rate.** A physics tick slower than the display can produce repeated visual positions; inspect Physics → Common → Physics Fps rather than assuming a fixed rate. Enable physics interpolation (check which node types and dimensions your version supports) or interpolate visuals in `_process`, and reset interpolation after a teleport so the object does not smear across the screen.
- **Pick the renderer for the target, not the prettiest one.** Forward+ is desktop-first; Mobile trades features for phone GPUs; Compatibility (GLES-lineage) is the safe path for web and old hardware.

## Anti-Patterns

- Hard-coding node paths across scene boundaries (`get_node("../../Player")`) instead of signals, exported node references, or an autoload — the top cause of scenes that break when moved.
- Updating physics-body movement outside the physics tick, or omitting `delta` from time-based frame updates. `_process(delta)` is valid for non-physics timing and visual movement.
- Getting `delta` wrong in either direction: forgetting it on manual position, timer, or acceleration updates (speed then scales with frame rate), or multiplying the velocity passed to `move_and_slide()` by it (the classic crawl bug: at an example 60 Hz tick the body moves at 1/60 of the intended speed).
- Deleting a node while the current callback or iteration still needs it — prefer `queue_free()` to avoid invalid references.
- Rewriting spawning around pools without profiling. GDScript uses reference counting, not a tracing garbage collector; creation/destruction cost can still matter. Pool only measured bottlenecks and reset all reused state.
- Treating every signal connection as a leak. An ordinary callable connection is lost when its target is freed; disconnect when a live listener should stop receiving events, and use `CONNECT_ONE_SHOT` when exactly one emission is intended ([Object.connect](https://docs.godotengine.org/en/stable/classes/class_object.html#class-object-method-connect)).
- Assuming C# and GDScript have identical export support — C# web/WASM export has lagged GDScript's. Check the current stable's release notes before promising a C# web build; if it is not supported in stable, the web target means GDScript.
- Shipping without matching **export templates** installed for the editor version → export fails or produces a broken binary.
- Leaving expensive runtime CSG unevaluated. CSG is mainly intended for prototyping; bake or replace it when target-device performance or asset-editing needs warrant it ([CSG guide](https://docs.godotengine.org/en/stable/tutorials/3d/csg_tools.html)).
- Quoting a renderer name, API signature, physics default, or export caveat from Godot 3 or an older 4.x minor without re-verifying — several were renamed or re-defaulted across 4.x (e.g. Jolt became the default 3D physics engine in 4.6).

## Known Traps

- **Frame-rate-dependent logic** — manual motion, acceleration or timers without elapsed-time scaling drift with the update rate. Use `delta` for these updates and physics processing for physics-body movement; do not scale `move_and_slide()` velocity by `delta`.
- **`TileMap` → `TileMapLayer` migration** — the monolithic `TileMap` node was **deprecated in 4.3** (present but frozen — no new features) in favor of per-layer `TileMapLayer` nodes; code and scenes from older tutorials will not match. Use the editor's one-click conversion tool rather than hand-porting.
- **Jolt default versus migration** — **4.6** uses Jolt for new 3D projects while existing projects retain their physics settings. Record the configured engine and re-test after engine/version changes; do not infer an automatic switch from the new-project default.
- **`@onready` ordering** — `@onready var x = $Child` is assigned just before `_ready()` runs, after `_enter_tree()`; do not rely on that deferred initializer in `_init()` or `_enter_tree()`.
- **Fixed-tick stutter on high-refresh displays** — physics-driven motion updates only on physics ticks, which can repeat positions on a faster display. Enable physics interpolation (check which node types your version supports) or interpolate visuals in `_process`; reset interpolation on teleport or respawn.
- **C# / web export** — check whether the current stable supports C# web export before promising a web build for a C# game; if it does not, treat GDScript as the web path.
- **Export templates version-lock** — templates must match the exact editor version **including patch level**. The editor normally reports a missing or mismatched template, so the real CI risk is a pipeline that ignores the export's exit code or never checks the artifact. Pin the exact patch in CI, reinstall templates on every upgrade, and make CI assert the exit code and that the artifact exists.
- **Shader compilation stutter** — Godot compiles shader variants lazily on first use, so effects hitch the first time they appear (worst on Android). Pre-warm materials on a loading screen (hidden `SubViewport`), persist the shader cache, and test on the real target where the editor's pre-cache doesn't hide it. See `references/rendering-and-shaders.md`.
- **`.res`/`ResourceSaver` save-file RCE** — loading a user-modifiable `.tres`/`.res` can execute arbitrary GDScript via resource deserialization. Use `FileAccess` + JSON (or `ConfigFile`) for save data, never `ResourceSaver` for user-shared files. See `references/rendering-and-export.md`.
- **Editor ≠ device** — the editor runs on your desktop GPU with the editor renderer, often with shaders pre-cached; a phone or web target has different capabilities. Test an actual exported build on the real target before shipping.
- **`.godot/` in git** — committing the generated `.godot/` cache causes churn and merge pain; gitignore it and commit only `project.godot` + source + assets.

## Frameworks & tooling (check status in the current release notes before adopting)

| Need | Pick | Status |
|------|------|--------|
| Primary language | **GDScript** (typed) | First-class, fastest iteration, full web export; typed Dictionaries (`Dictionary[K,V]`, added in 4.4) |
| Performance-critical / .NET ecosystem | **C#** (.NET) | First-class but heavier; check C# web-export support in the current stable — if absent, GDScript for web targets |
| Native performance modules | **GDExtension** (C/C++/Rust via godot-cpp / gdext) | Read GDExtension compatibility and binding support for the exact engine versions and target platforms before distributing binaries |
| 3D physics | **Jolt** (built-in) | Became the **default for new 3D projects in 4.6**; check the current default and whether Godot Physics is still selectable |
| 2D tilemaps | **TileMapLayer** (per-layer) | Per-layer node; the monolithic `TileMap` was deprecated in 4.3 |
| Dependency/asset sharing | The engine's official addon store + git submodules | Check which store your version uses (4.7 moved in-editor browsing from the Asset Library to an Asset Store); vet third-party addons for version fit |
| Console export | Licensed middleware/porting vendor, or an in-house port | Check the [official console process](https://godotengine.org/consoles/): platform approval, official SDKs, private export templates and certification; the Foundation does not maintain official ports |
| CI export | **`godot --headless --export-release`** | Scriptable headless export; needs version-matched templates on the runner |

## Save Compatibility Gate

Treat save data as a versioned external contract. Store a schema version, migrate one version at a time, preserve the pre-migration file until the new save is verified, and reject unknown future versions without overwriting them. Before release, load representative saves from every supported shipped version in an exported build and verify the migrated state by gameplay behavior, not only by successful parsing.

## When Godot Is the Wrong Choice

Recommending Godot by default is itself a judgment call, not a rule — push back when the project profile doesn't fit:

- **A console SKU is the primary target.** Plan platform approval, SDK access and private templates through a licensed provider or an in-house port. Verify provider version/platform coverage and support terms; compare the full porting/certification work with alternative engines before committing.
- **The team already has deep Unity or Unreal expertise and no Godot experience**, and the timeline doesn't afford a learning-curve tax — re-platforming mid-project is expensive; the switching cost usually isn't worth it for its own sake.
- **AAA-fidelity 3D rendering is the product** (film-quality GI, Nanite-style virtualized geometry, large open-world streaming). Godot's renderer is credible for stylized and mid-scope 3D, but it doesn't have Unreal's Lumen/Nanite-class pipeline; don't promise that fidelity on Godot.
- **The genre leans on a mature, licensed middleware ecosystem** (large-scale multiplayer backends, advanced physics/destruction, certain anti-cheat or ad-mediation SDKs) that ships Unity/Unreal plugins first and Godot support late or not at all — check the specific vendor before assuming parity.
- **The team needs a large in-house animation/rigging pipeline** matching Unity's Mecanim or Unreal's Control Rig maturity — Godot's `AnimationTree`/`AnimationPlayer` cover most 2D/indie-3D needs but are thinner for complex character-animation production pipelines.
- Godot remains a strong default for 2D, stylized/mid-scope 3D, rapid prototyping, jam games, and teams that value an open-source, royalty-free engine with fast iteration — the above are reasons to *check* fit, not a blanket "avoid Godot."

## Navigation

Resources:

- [references/setup-and-project.md](references/setup-and-project.md) — Editor versioning, project structure, repo hygiene, input maps, and GDScript-vs-C# choice
- [references/gdscript-and-architecture.md](references/gdscript-and-architecture.md) — Typed GDScript, signals (and when direct calls / `call_group` beat them), autoloads, `_process` vs `_physics_process`, custom `Resource` data modeling, `@tool`, `_notification` lifecycle, and node-communication patterns
- [references/scenes-and-nodes.md](references/scenes-and-nodes.md) — Scene composition vs inheritance, node tree design, `CharacterBody`, Jolt physics default, TileMapLayer/GridMap, and instancing
- [references/performance-and-traps.md](references/performance-and-traps.md) — CPU/GPU profiling, the drop-below-Nodes escape hatch (`MultiMesh`/servers), object pooling, node/signal lifecycle, and the full Known Traps catalog with fixes
- [references/rendering-and-shaders.md](references/rendering-and-shaders.md) — Shader compilation stutter and mitigation, lighting/GI strategy (LightmapGI/SDFGI/VoxelGI), `WorldEnvironment`, and `SubViewport` techniques
- [references/rendering-and-export.md](references/rendering-and-export.md) — Renderer choice, export templates and gotchas, save systems (and the `.res` security trap), high-level multiplayer, per-platform presets, and shipping/signing
- [data/sources.json](data/sources.json) — Primary sources to verify volatile facts against

Related skills:

- [../software-mobile/SKILL.md](../software-mobile/SKILL.md) — Mobile-platform constraints and store flows
- [../software-performance/SKILL.md](../software-performance/SKILL.md) — General performance profiling discipline
- [../software-ui-ux-design/SKILL.md](../software-ui-ux-design/SKILL.md) — Onboarding and flow design that transfers to game UX
- [../gamedev-roblox/SKILL.md](../gamedev-roblox/SKILL.md) — Sibling game-creation skill for the Roblox platform

For a relevant previously observed pitfall, consult `learnings.consolidated.md`; otherwise skip empty learning files.

Before an upgrade or export commitment, read the pinned release’s migration notes and platform docs for renderer support, C#/web export, physics settings and signing requirements. If unavailable, mark that specific claim unverified.
