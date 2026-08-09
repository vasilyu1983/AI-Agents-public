# Setup & Project

## Table of Contents

- [Editor & versioning](#editor--versioning)
- [Project structure & repo hygiene](#project-structure--repo-hygiene)
- [Input maps](#input-maps)
- [GDScript vs C#](#gdscript-vs-c)

## Editor & versioning

- Pin **one editor version per project**. Godot 4.x behavior and node names drift across minor versions; a project opened in a newer editor may silently migrate scenes. Record the version in the repo (README or a `.godot-version` convention).
- The editor is a single self-contained binary. Use a version manager or a per-project download rather than a global system install so two projects can target two versions.
- The **standard** build runs GDScript only; the **.NET/Mono** build adds C#. Pick the build that matches your language choice — don't install .NET tooling you won't use.

## Project structure & repo hygiene

- **Commit**: `project.godot`, all `.tscn`/`.tres`/`.gd`/`.cs` source, and imported source assets (`.png`, `.wav`, …).
- **Gitignore**: `.godot/` (the generated editor cache and import metadata), `export/` build output, and any `*.import` you regenerate. `.godot/` in git causes constant churn and merge conflicts — this is the most common Godot repo mistake.
- Lay out folders by concept, not by type: `scenes/player/`, `scenes/enemies/`, `autoload/`, `ui/`. Keeping a scene's script, art, and sub-scenes together makes scenes portable.
- A `.tscn` stores node paths and resource references relative to the project — moving files in the OS file manager breaks them. Move and rename **inside the Godot editor** so references update.

## Input maps

- Define actions in **Project Settings → Input Map** (`move_left`, `jump`, `interact`), then read them with `Input.is_action_pressed("jump")`. Never hard-code raw keycodes in gameplay scripts.
- Map both keyboard and gamepad events to the same action so controller support is free.
- `Input.get_vector("left","right","up","down")` gives a normalized 2D input vector — the idiomatic way to read movement.

## GDScript vs C#

Default to **GDScript** unless you have a concrete reason otherwise:

| Factor | GDScript | C# (.NET) |
|--------|----------|-----------|
| Iteration speed | Fastest (no compile step) | Slower (compile) |
| Web export | Full support | **Not supported in stable** as of Godot 4.7 (July 2026) — prototype only; verify per release |
| Ecosystem | Godot-native APIs | Full .NET libraries |
| Export size | Small | Heavier (ships .NET runtime) |
| Performance | Good, typed GDScript optimizes | Faster for CPU-heavy code |

- For CPU-bound hot paths in either language, consider **GDExtension** (C/C++ via godot-cpp, or Rust via gdext) rather than switching the whole project to C#.
- `as of mid-2026 — verify`: C# web export support has changed across 4.x releases. Confirm before promising a browser build for a C# project.
