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

1. **Draw calls / GPU-bound render state** — check the Monitors panel for draw-call count and GPU frame time first. Godot batches poorly across many unique materials; a scene with 500 sprites each on a distinct material generates 500 draw calls. Fix: shared materials/atlases, `CanvasItem` batching, or `MultiMeshInstance2D/3D` for repeated geometry — before touching any script.
2. **Physics** — collision-shape count and complexity (concave vs convex, overlapping `Area`/`RigidBody` counts) show up in the physics monitor. Fix: simplify shapes, use layers/masks to cull unnecessary collision pairs, reduce polling in favor of enter/exit signals.
3. **GDScript hot paths** — only once render and physics are cleared, profile function time in the CPU profiler. Fix: cache node lookups, avoid per-frame allocation, avoid signals in per-frame hot loops (see below). Typed GDScript alone recovers meaningful performance over untyped/dynamic code — check typing before reaching for a language switch.
4. **C# for CPU-bound logic** — if a specific hot subsystem (pathfinding, procedural generation, simulation) is provably GDScript-bound *after* step 3, consider porting just that subsystem to C#, not the whole project.
5. **GDExtension (C/C++/Rust)** — the last resort for the hottest of hot paths (bulk physics queries, custom data structures) where even C# isn't enough. Highest implementation cost and worst iteration speed of the five options; reach for it only when the profiler names a specific function and steps 1–4 are exhausted.

Skipping straight to step 4 or 5 because "GDScript is slow" without profiler evidence is a common overreaction — most real-world frame-time problems in shipped Godot games are draw calls or unbounded node counts (steps 1–2), not language choice.

## Profiling

- Use the built-in **Debugger → Profiler** (frame time by function) *and* the separate **Visual/GPU Profiler** — a CPU-bound frame and a GPU-bound frame need opposite fixes, and the frame-time profiler alone won't tell you which you have. Profile, don't guess.
- Watch **Monitors** (draw calls, node count, memory, physics, video memory) to localize the bottleneck to render / logic / physics before touching code.
- Run with `--verbose` for engine-level logging; `--headless` for CI and automated tests.
- Measure on the **target device**, not the editor. The editor uses your desktop GPU and the editor renderer, which does not represent a phone or a web target — and it has often pre-cached shaders the target hasn't (see shader stutter in `rendering-and-shaders.md`).

## Escape hatch: drop below Nodes when count is the bottleneck

Nodes are a convenience layer over the servers (`RenderingServer`, `PhysicsServer2D/3D`). Each Node carries script, tree, and lifecycle overhead. Past a few thousand homogeneous instances, that overhead *is* the bottleneck:

- **Thousands of identical visuals** (bullets, grass, crowd, tiles-as-sprites) → `MultiMeshInstance2D/3D` or direct `RenderingServer` canvas items, not one Node each. A `MultiMesh` draws N instances in one draw call with no per-instance Node cost.
- **Bulk physics queries** → `PhysicsServer2D/3D` direct raycasts/shape queries when the `Area`/`RayCast` Node overhead itself shows up in the profiler.
- This is a *confirmed-by-profiler* move, not a default — for a few hundred instances, Nodes are fine and far simpler.

## Object pooling

- Instancing and freeing objects every frame (bullets, particles, floating damage text) causes allocation spikes and stutter.
- Pool: pre-instance a fixed set, hide + deactivate on "death," and reuse instead of `queue_free()`. Keep a free-list and grab from it on spawn.
- `GPUParticles2D/3D` handle their own batching — prefer them over hand-spawned particle nodes for effects.

## Node & signal lifecycle

- Every node you `instantiate()` and `add_child()` must eventually be freed (`queue_free()`), or it leaks and keeps its subtree alive.
- Disconnect per-instance signal connections when either side is freed, or connect with `CONNECT_ONE_SHOT` for fire-once handlers. A leftover connection keeps a freed context referenced — Godot's most common silent leak.
- Watch the **node count** monitor: a number that only ever climbs means you are leaking instanced scenes.

## Per-frame cost

- Cache `get_node`/`$Path` lookups in `@onready` variables; don't re-resolve a path every frame.
- Avoid per-frame allocations (new arrays, dictionaries, strings) inside `_process`/`_physics_process`; build them once and mutate.
- Put gameplay in `_physics_process` (fixed rate); keep `_process` for visuals so heavy logic isn't tied to render frame rate.
- Prefer `Area` overlap signals over polling distances every frame when you only need enter/exit events.

## Known Traps catalog

- **Frame-rate-dependent logic** — movement/timers in `_process` without `* delta` drift across machines and refresh rates. Fix: `_physics_process` + multiply by `delta`.
- **`free()` mid-frame** — freeing during signal handling or iteration is a use-after-free crash. Fix: `queue_free()`.
- **`TileMap` → `TileMapLayer`** — code/scenes from older tutorials reference the removed monolithic node. `as of mid-2026 — verify` the current node for your version.
- **`@onready` used too early** — referencing an `@onready` var in `_init()` or before `_ready()` returns null. Fix: use it in/after `_ready()`.
- **Leaked signal connections** — per-instance connects never disconnected keep freed nodes referenced. Fix: `CONNECT_ONE_SHOT` or disconnect on free.
- **Export-template mismatch** — templates must match the exact editor version or export fails/ships broken. Fix: reinstall templates on every editor upgrade. See `rendering-and-export.md`.
- **Editor ≠ device** — a scene that runs at 120 fps in the editor can stutter on a phone or web target. Fix: profile an exported build on the real target.
- **`.godot/` committed** — the generated cache in git causes churn and merge conflicts. Fix: gitignore it.
