# GDScript & Architecture

## Table of Contents

- [Typed GDScript](#typed-gdscript)
- [The frame callbacks](#the-frame-callbacks)
- [Signals up, calls down](#signals-up-calls-down)
- [When signals are the wrong choice](#when-signals-are-the-wrong-choice)
- [Autoload singletons](#autoload-singletons)
- [Direct calls vs signals vs event-bus](#choosing-between-direct-calls-signals-and-an-event-bus-autoload)
- [Node references](#node-references)
- [Model data as custom Resources](#model-data-as-custom-resources-not-nodes-or-dictionaries)
- [Editor tooling with `@tool`](#editor-tooling-with-tool)
- [Lifecycle beyond `_ready`](#lifecycle-beyond-_ready)
- [Disable processing instead of branching](#disable-processing-instead-of-branching)

## Typed GDScript

- Use static types everywhere: `var speed: float = 200.0`, `func take_damage(amount: int) -> void:`. Typing enables autocomplete, catches errors at parse time, and lets the compiler optimize.
- `class_name Enemy` registers a script as a type usable in the editor and in `is`/`as` checks.
- `@export var max_health: int = 100` surfaces a field in the Inspector and lets designers tune per-instance without touching code.
- `@export var target: Node2D` (a typed exported node reference) is the clean alternative to hard-coded `get_node` paths — wire it in the editor.

## The frame callbacks

- `_physics_process(delta)` runs at the configured **fixed timestep** (inspect Physics → Common → Physics Fps). Put physics-body movement and collision logic here.
- `_process(delta)` runs **once per rendered frame** (variable). Put cosmetic updates here: camera smoothing, UI tweens, non-authoritative visuals.
- Multiply accelerations, manual position changes, and timers by `delta`; omitting it ties speed to frame rate. Do **not** multiply the velocity passed to `move_and_slide()` by `delta`: it already integrates `velocity` over the step, so the extra factor makes the body crawl.
- A physics tick slower than the display can cause repeated visual positions. Enable physics interpolation (check which node types your version supports) or interpolate visuals in `_process`, and reset interpolation after teleports.
- `_ready()` fires once when the node and its children have entered the tree; `_init()` fires earlier, before children exist.

## Signals up, calls down

The core decoupling rule:

- A **parent calls methods on its children** (it owns them, it knows they exist).
- A **child emits a signal** that the parent (or an autoload) connects to; the child never reaches up to a specific parent.

```gdscript
# child (Health.gd)
signal died
func take_damage(n: int) -> void:
    health -= n
    if health <= 0:
        died.emit()

# parent connects in _ready()
$Health.died.connect(_on_player_died)
```

This keeps children reusable in any scene. Reaching upward with `get_node("../../GameManager")` is the anti-pattern it replaces.

- Ordinary object-method connections are lost when the callable target is freed. Disconnect while endpoints remain alive if the subscription should end (for example a pooled actor); use `CONNECT_ONE_SHOT` for one intended emission.

### When signals are the wrong choice

Signals are not free — each emit does a dynamic dispatch and walks the connection list. Reserve them for **state-change events** (`died`, `picked_up`, `level_complete`), not steady-state per-frame communication.

- If profiling finds signal dispatch material in repeated collision checks, call a method directly, or use `get_tree().call_group("enemies", "on_tick", delta)` to fan out to a group in one call.
- Keep signals when the emitter should not know its listeners; replace dispatch in a measured hot loop only when the alternative preserves that ownership boundary.

## Autoload singletons

- Register genuinely global systems in **Project Settings → Autoload**: game state, an audio manager, a scene switcher, a save system. They persist across scene changes and are reachable by name (`GameState.score`).
- Keep the autoload list short. Not every manager is global — most belong to a scene. Overusing autoloads recreates the tight coupling signals were meant to remove.

### Choosing between direct calls, signals, and an event-bus autoload

Three mechanisms cover node communication, and picking the wrong one is a common architecture smell:

- **Direct method call** — when the caller already owns the callee (a parent calling its own child, code operating on a reference it was handed). Cheapest, most explicit, and the right default *within* an owned subtree.
- **A local signal, connected by the owner** — when a child needs to notify *without* knowing who's listening, and the listener is a nearby, known node (its parent, or a sibling reached through the parent). This is "signals up, calls down" from above.
- **An event-bus autoload** (an autoload whose only job is `signal player_died`, `signal level_completed`, etc., with no state) — when an event has **multiple unrelated listeners across different scenes** that don't have a structural relationship (UI, audio, analytics, achievements all reacting to one gameplay event). Emitting to a shared bus avoids wiring the same signal to N listeners by hand and avoids a state-holding autoload growing god-object logic — the bus only carries events, it doesn't own game state.
- Don't default to the event bus for everything: a signal a single parent listens to doesn't need a bus hop, and routing every interaction through a global bus turns easy-to-trace calls into implicit, hard-to-grep global events. Reach for the bus when the "who's listening" list is genuinely open-ended or cross-cutting.

## Node references

- Prefer a typed `@export` node reference wired in the editor, or `@onready var thing := $Path` for children **within the same scene**.
- `@onready` vars are assigned just before `_ready()` runs, after `_enter_tree()`. Their deferred initializer has not run in `_init()` or `_enter_tree()`; the earlier value depends on the declared type.
- Never path across scene boundaries. Cross-scene communication goes through signals or an autoload.

## Model data as custom Resources, not Nodes or Dictionaries

For data that isn't itself a scene participant — item definitions, ability configs, dialogue, enemy stat blocks — the expert default is a **custom `Resource` subclass**, not a Node and not a raw Dictionary:

```gdscript
class_name ItemData extends Resource
@export var display_name: String
@export var max_stack: int = 99
@export var icon: Texture2D
```

- Reference-counted, inspector-editable, saveable as `.tres` assets, and shareable across many scene instances with no scene-tree overhead. It's the correct middle ground between a Dictionary (no typing, no editor support) and a Node (unnecessary lifecycle/tree cost for pure data).
- Typed Dictionaries (`Dictionary[String, ItemData]`, added in 4.4) are the right container when you do need a map.

## Editor tooling with `@tool`

- Put `@tool` at the top of a script to make it run **inside the editor**, not just at runtime — for gizmos, live preview of procedural geometry, custom inspector behavior (`_validate_property`), or editor-only validation.
- Guard runtime-only code with `if Engine.is_editor_hint(): return` so it doesn't fire while editing.

## Lifecycle beyond `_ready`

- `_enter_tree()` fires before children are ready; `_ready()` fires once children are ready. Use `_enter_tree` for setup that must happen before descendants initialize, but not for anything that reads an `@onready` var: their deferred initializers have not run there.
- Override `_notification(what)` for engine events the common callbacks don't cover: `NOTIFICATION_WM_CLOSE_REQUEST` (intercept the OS window-close button to prompt "save before quit" — set `get_tree().auto_accept_quit = false`), `NOTIFICATION_APPLICATION_PAUSED`/`_RESUMED` (mobile backgrounding — pause audio/timers), `NOTIFICATION_PREDELETE` (guaranteed cleanup just before free).
- Use `call_deferred()` / `set_deferred()` to mutate the tree safely from inside physics/signal callbacks (adding/removing nodes mid-physics-step is unsafe); it runs the call at idle time instead.

## Disable processing instead of branching

For pooled, off-screen, or paused actors, turn off per-frame work explicitly rather than early-returning inside `_process` every frame:

- `set_process(false)`, `set_physics_process(false)`, or `process_mode = Node.PROCESS_MODE_DISABLED`. Cheaper than running the callback to immediately `return`.
