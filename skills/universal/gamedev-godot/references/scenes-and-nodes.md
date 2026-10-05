# Scenes & Nodes

## Table of Contents

- [Scenes as prefabs](#scenes-as-prefabs)
- [Node tree design](#node-tree-design)
- [Movement bodies](#movement-bodies)
- [2D grids and 3D levels](#2d-grids-and-3d-levels)
- [Instancing and lifecycle](#instancing-and-lifecycle)

## Scenes as prefabs

- A **scene (`.tscn`) is a reusable prefab**. Build a thing once — an enemy, a pickup, a UI panel — save it, and instance it wherever needed. This is Godot's primary reuse mechanism; prefer it over deep script inheritance.
- A scene has a single **root node** whose type defines what the scene "is" (`Area2D` pickup, `CharacterBody2D` player, `Control` menu).
- Composition beats inheritance *as a default*: give a scene child nodes for its parts (a `Sprite2D`, a `CollisionShape2D`, a `Health` sub-scene) rather than subclassing.
- **But scene inheritance earns its place** for a family of variants that share node structure and differ in tuned values or a few overridden children (`EnemyBase` → `EnemyGoblin`/`EnemyOrc`, via right-click → New Inherited Scene). Reach for composition when the shared part is a self-contained reusable *behavior* (a Health component, a Hitbox); reach for inheritance when it's a structural *variant* of the same actor. Blindly composing every variant from scratch is as much a smell as over-inheriting.

## Node tree design

- Keep the tree **shallow and meaningful**. Deep nesting makes node paths fragile and traversal slow.
- Name nodes by role, not type (`Muzzle`, not `Marker2D3`), because scripts and the editor reference them by name.
- Group repeated actors under a container node you can iterate (`get_children()`), or add them to a **group** (`add_to_group("enemies")`) and act on the group.

## Movement bodies

- **`CharacterBody2D` / `CharacterBody3D`** for player- and AI-controlled movers: set `velocity` in units per second, call `move_and_slide()`, and let the engine resolve collisions and slopes.
- **`RigidBody`** for physics-driven objects you push forces onto; don't set position directly on a RigidBody.
- **`StaticBody`** for immovable geometry; **`Area`** for overlap detection (triggers, hurtboxes) without collision response.
- Do movement in `_physics_process`. `move_and_slide()` already integrates `velocity` over the physics step, so **do not multiply the velocity you pass to it by `delta`**: `velocity = dir * speed * delta` is the classic crawl bug (1/60 of the intended speed at an example 60 Hz tick). Multiply accelerations and manual position or timer changes by `delta`:

```gdscript
func _physics_process(delta: float) -> void:
    velocity.y += gravity * delta          # acceleration: scale by delta
    velocity.x = input_dir * speed         # velocity: units per second, no delta
    move_and_slide()                       # integrates velocity over the step
```
- **Jolt** became the default 3D physics engine for new projects in **4.6**; check the current default in the release notes of the version you pin. A project upgraded in place keeps its configured engine unless switched, so physics can behave differently after an upgrade that changes it; re-test.

## 2D grids and 3D levels

- **`TileMapLayer`** is the per-layer 2D tile node — one node per layer. The older monolithic `TileMap` node was **deprecated in 4.3** (kept but frozen, no new features; check whether the version you pin still ships it); older tutorials showing a single `TileMap` with internal layers are out of date. Use the editor's one-click conversion tool to migrate.
- **`GridMap`** places 3D meshes on a grid from a `MeshLibrary` — the 3D analogue for blocky level building.
- For freeform 3D levels, compose scenes and use `CSGShape` nodes for greyboxing, then replace with real meshes.

## Instancing and lifecycle

```gdscript
var bullet := BulletScene.instantiate()
add_child(bullet)
bullet.global_position = muzzle.global_position
```

- `preload("res://…")` loads a scene at parse time (constant path); `load(...)` loads at runtime (dynamic path).
- Free nodes with **`queue_free()`**, which defers destruction to the end of the frame. Avoid immediate `free()` when a callback or iteration still needs the node; deleting a parent also deletes its children.
- For frequently spawned objects, **pool** only when profiling identifies creation/destruction as a bottleneck; reset reused state. See `performance-and-traps.md`.
