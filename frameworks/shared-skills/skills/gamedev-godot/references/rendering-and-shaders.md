# Rendering, Lighting & Shaders

Expert Godot is heavily a rendering discipline. This reference covers the depth beyond renderer choice (which lives in `rendering-and-export.md`). `as of Godot 4.7, July 2026 — verify` renderer/feature availability per version.

## Table of Contents

- [Shader compilation stutter](#shader-compilation-stutter)
- [Lighting & global illumination](#lighting--global-illumination)
- [WorldEnvironment](#worldenvironment)
- [SubViewport tricks](#subviewport-tricks)

## Shader compilation stutter

The single most-complained-about Godot 4.x shipping issue. Godot compiles shader **variants lazily on first use** by default, so the first time a given material/effect appears on screen the frame hitches — worse on Forward+/Vulkan, and worse on Android where drivers recompile per device.

Mitigations (verify current project-setting paths per version):

- **Persist the shader cache to disk** (`rendering/shader_compiler/shader_cache/...`), stored under `.godot/shader_cache`, so compilation survives between runs where the platform allows it.
- **Pre-warm materials on a loading screen** — render a hidden `SubViewport` containing every representative material before gameplay starts, so first-use compilation happens during "Loading…", not mid-combat.
- On Android specifically, consider an **ubershader**-style always-compile-everything approach so there's no per-variant hitch at the cost of a heavier initial compile.
- **Test stutter on the actual export target.** The editor has usually pre-cached shaders from prior editor runs, so it will *not* reproduce the hitch a fresh install shows a real player.

## Lighting & global illumination

Renderer choice (`rendering-and-export.md`) constrains what's available; this is the strategy on top of it:

| Scene type | Tool | Cost / constraint |
|------------|------|-------------------|
| Static / architectural, no moving lights | **`LightmapGI`** (baked) | Cheap at runtime; must re-bake on geometry/light change; no response to dynamic lights |
| Dynamic scene, moving lights, Forward+ only | **`SDFGI`** | Real-time GI; meaningfully more expensive; **not available on Mobile/Compatibility** renderers |
| Medium dynamic scene | **`VoxelGI`** | Baked probe volume; middle ground; bounded to the probe region |
| Mobile target | Baked lightmaps or simple additive lighting | SDFGI is Forward+ only — plan lighting around this from the start, not after picking Mobile |

The trap: prototyping with SDFGI on desktop Forward+, then discovering it's gone when you switch to the Mobile renderer for a phone build. Decide the lighting strategy against the **target** renderer.

## WorldEnvironment

- Configure ambient light, tonemapping, SSAO/SSIL, glow/bloom, fog, and sky **globally** via a single `WorldEnvironment` node (with an `Environment` resource) — not per-camera. Per-camera environment overrides exist but are the exception.
- Tonemapping (e.g. ACES/AgX) and exposure are here — a scene that looks "washed out" or "crushed" is usually a tonemap/exposure setting, not a light-intensity problem.

## SubViewport tricks

`SubViewport` renders a separate scene to a texture (`ViewportTexture`). Staple uses:

- **Minimaps** — a second camera over the world rendered into a UI panel.
- **Render-to-texture effects** — security cameras, portals, mirrors, in-world screens.
- **Split-screen** — one `SubViewport` per player inside `SubViewportContainer`s.
- **UI-embedded 3D** — a live rotating model in an inventory/character screen.
- **Shader pre-warm** (see above).

Each `SubViewport` is a separate render pass — budget them; don't spawn more than the target can afford.
