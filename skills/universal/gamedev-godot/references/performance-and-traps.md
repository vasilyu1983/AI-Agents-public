# Performance & Traps

## Table of Contents

- [Triage order](#triage-order-where-to-look-first)
- [Profiling](#profiling)
- [Escape hatch: drop below Nodes](#escape-hatch-drop-below-nodes-when-count-is-the-bottleneck)
- [Object pooling](#object-pooling)
- [Node & signal lifecycle](#node--signal-lifecycle)
- [Per-frame cost](#per-frame-cost)
- [Known Traps catalog](#known-traps-catalog)

## Triage order: where to look first

When frame time is bad and the cause isn't obvious, check in this order — each step is cheaper to diagnose than the next, and jumping straight to a rewrite (GDExtension, switching languages) before ruling out the cheap causes is the single biggest waste of an optimization pass:

1. **Draw calls / GPU-bound render state** — check the Monitors panel for draw-call count and GPU frame time first. Distinct materials can reduce batching; measure actual draw calls rather than assuming one call per sprite. Fix: shared materials/atlases, `CanvasItem` batching, or `MultiMeshInstance2D/3D` for repeated geometry — before touching any script.
2. **Physics** — collision-shape count and complexity (concave vs convex, overlapping `Area`/`RigidBody` counts) show up in the physics monitor. Fix: simplify shapes, use layers/masks to cull unnecessary collision pairs, reduce polling in favor of enter/exit signals.
3. **GDScript hot paths** — only once render and physics are cleared, profile function time in the CPU profiler. Fix: cache node lookups, avoid per-frame allocation, avoid signals in per-frame hot loops (see below). Typed GDScript alone recovers meaningful performance over untyped/dynamic code — check typing before reaching for a language switch.
4. **C# for CPU-bound logic** — if a specific hot subsystem (pathfinding, procedural generation, simulation) is provably GDScript-bound *after* step 3, consider porting just that subsystem to C#, not the whole project.
5. **GDExtension (C/C++/Rust)** — the last resort for the hottest of hot paths (bulk physics queries, custom data structures) where even C# isn't enough. Highest implementation cost and worst iteration speed of the five options; reach for it only when the profiler names a specific function and steps 1–4 are exhausted.

Skipping straight to step 4 or 5 because "GDScript is slow" without profiler evidence is a common overreaction — identify whether the workload is render-, physics- or script-bound before choosing a rewrite.

## Profiling

- Use the built-in **Debugger → Profiler** (frame time by function) *and* the separate **Visual/GPU Profiler** — a CPU-bound frame and a GPU-bound frame need opposite fixes, and the frame-time profiler alone won't tell you which you have. Profile, don't guess.
- Watch **Monitors** (draw calls, node count, memory, physics, video memory) to localize the bottleneck to render / logic / physics before touching code.
- Run with `--verbose` for engine-level logging; `--headless` for CI and automated tests.
- Measure on the **target device**, not the editor. The editor uses your desktop GPU and the editor renderer, which does not represent a phone or a web target — and it has often pre-cached shaders the target hasn't (see shader stutter in `rendering-and-shaders.md`).

## Escape hatch: drop below Nodes when count is the bottleneck

Nodes are a convenience layer over the servers (`RenderingServer`, `PhysicsServer2D/3D`). Each Node carries script, tree, and lifecycle overhead. Measure this overhead for the actual content and target device; there is no universal instance-count crossover:

- **Thousands of identical visuals** (bullets, grass, crowd, tiles-as-sprites) → `MultiMeshInstance2D/3D` or direct `RenderingServer` canvas items, not one Node each. A `MultiMesh` draws N instances in one draw call with no per-instance Node cost.
- **Bulk physics queries** → inspect the target version’s `PhysicsDirectSpaceState2D/3D` query APIs and timing restrictions when `Area`/`RayCast` node overhead is measured; do not assume these queries are methods on `PhysicsServer` itself.
- This is a *confirmed-by-profiler* move, not a default — retain Nodes when their cost fits the budget.

## Object pooling

- Profile creation/destruction of frequently spawned objects before pooling. GDScript uses reference counting; allocation or setup cost can still cause spikes, while C# has its own managed-memory behavior.
- Pool: pre-instance a fixed set, hide + deactivate on "death," and reuse instead of `queue_free()`. Keep a free-list and grab from it on spawn; reset gameplay state, collision participation and subscriptions on reuse.
- `GPUParticles2D/3D` handle their own batching — prefer them over hand-spawned particle nodes for effects.

## Node & signal lifecycle

- Release obsolete subtrees with `queue_free()` on their owning root; freeing a parent recursively deletes its children. Detached nodes still require explicit lifetime ownership.
- An ordinary callable connection is lost when its target is freed. Disconnect a subscription when a still-live listener should stop receiving events; use `CONNECT_ONE_SHOT` for an intended fire-once handler.
- Watch the **node count** monitor: a number that only ever climbs means you are leaking instanced scenes.

## Per-frame cost

- Cache `get_node`/`$Path` lookups in `@onready` variables; don't re-resolve a path every frame.
- Avoid per-frame allocations (new arrays, dictionaries, strings) inside `_process`/`_physics_process`; build them once and mutate.
- Put physics-synchronized logic in `_physics_process`; `_process(delta)` can handle visuals and non-physics timers with elapsed-time scaling.
- Prefer `Area` overlap signals over polling distances every frame when you only need enter/exit events.

## Known Traps catalog

- **Frame-rate-dependent logic** — movement/timers in `_process` without `* delta` drift across machines and refresh rates. Fix: scale time-based updates by `delta`; run physics-body movement in `_physics_process`.
- **Crawling `CharacterBody`** — `velocity = dir * speed * delta` before `move_and_slide()` moves at 1/60 of the intended speed at an example 60 Hz tick, because `move_and_slide()` already integrates velocity. Fix: set velocity in units per second; scale only accelerations by `delta`.
- **Fixed-tick stutter on high-refresh displays** — physics-driven motion can judder when display rate exceeds physics update rate. Fix: enable physics interpolation (check node-type support for your version) or interpolate visuals in `_process`; reset interpolation on teleport.
- **Invalidated live references** — deleting a node still used by a callback or iteration can break the current operation. Fix: prefer `queue_free()` for scene-node destruction.
- **`TileMap` → `TileMapLayer`** — code/scenes from older tutorials reference the monolithic node, deprecated in 4.3 (frozen, not removed). Fix: migrate with the editor's conversion tool; check the release notes of the version you pin for its current status.
- **`@onready` used too early** — an `@onready` var is assigned just before `_ready()`, so its deferred value is unavailable in `_init()` and `_enter_tree()`. Fix: use it in/after `_ready()`.
- **Stale live subscriptions** — a pooled or inactive receiver can still receive events while alive. Fix: disconnect when that subscription ends, or use `CONNECT_ONE_SHOT` for a single intended emission; ordinary freed targets disconnect automatically.
- **Export-template mismatch** — templates must match the exact editor version or the export fails. Fix: reinstall templates on every editor upgrade, and make CI assert the exit code and that the artifact exists. See `rendering-and-export.md`.
- **Editor ≠ device** — a scene that runs at 120 fps in the editor can stutter on a phone or web target. Fix: profile an exported build on the real target.
- **`.godot/` committed** — the generated cache in git causes churn and merge conflicts. Fix: gitignore it.
