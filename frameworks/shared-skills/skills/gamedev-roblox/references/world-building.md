# World Building (Jul 2026)

The craft of building the 3D world and the player's first experience. Build-order principles are durable; lighting API names and numeric defaults are dated.

## Table of Contents

- [Scale and Proportion](#scale-and-proportion)
- [Greybox to First Playable](#greybox-to-first-playable)
- [Modular Kit Construction](#modular-kit-construction)
- [Lighting (Unified Lighting)](#lighting-unified-lighting)
- [Terrain, Parts, and Meshes](#terrain-parts-and-meshes)
- [PBR and SurfaceAppearance](#pbr-and-surfaceappearance)
- [Streaming](#streaming)
- [Sound Design Zones](#sound-design-zones)
- [Publishing and Testing](#publishing-and-testing)

## Scale and Proportion

1 stud ≈ **0.28 m** (28 cm) — the canonical conversion. Build to player scale from the start:

- Character height (`as of May 2026 — verify per body type`): classic blocky ~4.75 studs (~133 cm); R15/Rthro ~5–6.5 studs. R15 Humanoid hip height ≈ 2.35 studs.
- Doorways ≥ 7–8 studs; comfortable ceilings 10–12 studs.
- Player-scale stair step: ~1 stud rise, 2–3 stud run.

Getting scale wrong is expensive to fix after detailing, so validate it in the greybox.

## Greybox to First Playable

The official environmental-art pipeline, and the durable backbone of this skill:

1. **Blockout in Parts only** — no textures, meshes, or scripts. Validate scale, sightlines, and player flow.
2. **Establish pathways** — clear routes and intersections with a limited number of entrances/exits; don't overwhelm players with simultaneous choices.
3. **First Playable** — playable greybox with working spawn/respawn, a single lighting pass, and navigable geometry. **Ship this before any detailing.** It is the checkpoint that proves the world is fun before you sink hours into art.
4. **Modular kit replacement** — swap blockout geometry for reusable kit pieces.
5. **Scene dressing last** — props and detail give the world "personality and a sense of history"; add only after gameplay is validated.

## Modular Kit Construction

Build walls, corners, door frames, floor tiles as a reusable kit and snap them together. Benefits: consistent scale, fewer unique meshes (fewer draw calls — see performance reference), and fast iteration. Reuse identical `MeshId`s across instances so the renderer batches them.

## Lighting (Unified Lighting)

**The lighting API changed in 2025.** The old `Lighting.Technology` enum (`Future`/`ShadowMap`/`Voxel`/`Compatibility`) is **deprecated** — do not set it in new projects. Use:

- `Lighting.LightingStyle` — `Realistic` (≈ former Future, premium per-pixel) or `Soft` (≈ former ShadowMap/Voxel, cheaper).
- `Lighting.PrioritizeLightingQuality` — `Enabled` or `Disabled`.

Default for a new premium world: `LightingStyle = Realistic` + `PrioritizeLightingQuality = Enabled`; the engine scales across devices automatically. For mobile-first experiences, profile `Realistic` on low-end hardware before committing — it can fall back to voxel lighting at low quality levels.

Cheap, high-impact atmosphere: use `Lighting.Atmosphere` (set fog density/color on the Atmosphere object, not the deprecated `Lighting.FogEnd`) and `Lighting.Sky`. Extended light ranges (up to ~120 studs) and emissive masks shipped in 2025–2026.

> `as of May 2026 — verify` the exact property names `LightingStyle`/`PrioritizeLightingQuality` are final, since this system is recent.

## Terrain, Parts, and Meshes

| Building block | Use | Notes |
|----------------|-----|-------|
| **Terrain** (voxel) | Organic landscapes | "Enhanced voxel terrain" was roadmap, not confirmed shipped (`verify`) |
| **Part** (primitive) | Blockout, simple geometry | Cheapest; anchor static ones |
| **MeshPart** (imported) | Detailed assets | glTF/FBX/OBJ; one-click non-destructive reimport is GA; 4K textures now render for detailed models |
| **CSG/Union** | In-Studio boolean geometry | Bakes to a mesh; watch collision fidelity (see performance reference). CSG-on-textured-meshes was roadmap (`verify`) |

Prefer clean imported meshes over in-Studio CSG for environment pieces — you get explicit control over triangle count.

LOD: **SLIM** (Scalable Lightweight Interactive Models) is the next-gen level-of-detail system (Client Beta, late 2025), enabled via `Model.LevelOfDetail = SLIM`, requires StreamingEnabled, static meshes only in v1 (`verify status`).

## PBR and SurfaceAppearance

`SurfaceAppearance` supports full physically-based maps: `ColorMap`, `NormalMap`, `RoughnessMap`, `MetalnessMap`. PBR for avatar accessories is GA. The **Material Generator** (GA) produces full PBR Material Variants from a text prompt; the **Texture Generator** (Beta) produces ColorMap-only textures with a daily cap (see setup reference).

## Streaming

`Workspace.StreamingEnabled = true` is the default in new templates and is mandatory for any large world — without it every player loads the entire Workspace into memory on join (catastrophic on mobile).

- `StreamingMinRadius` — guaranteed-loaded radius around the character (raises memory/bandwidth; increase carefully).
- `StreamingTargetRadius` — max radius the server streams (smaller = less server load; too small = visible pop-in).
- `Model.StreamingMode` — `Atomic` (model streams as one unit) vs `Default` (descendants stream independently).
- `ReplicatedStorage`/`ReplicatedFirst` never stream — keep them lean.
- **Consequence for code:** LocalScripts must access Workspace objects via `WaitForChild(name, timeout)`; direct indexing errors when the object hasn't streamed in. See performance reference traps.

Default radius values are tuned for general use; adjust to map scale (`as of May 2026 — verify defaults`).

## Sound Design Zones

- Attach `Sound` objects to Parts and use `RollOffMaxDistance` for spatial zones.
- Load music/large audio on-demand and unload when done — don't preload everything at start (memory cost).
- Create one-shot sounds on demand and destroy them after playback rather than pooling idle Sound objects.

## Publishing and Testing

Studio Test tab modes:

| Mode | What | Use |
|------|------|-----|
| **Play** (F5) | Single-player client+server in one process | Fast mechanic/UI iteration |
| **Play Here** | Spawn at camera position | Test a specific area |
| **Run** | Server only, no character | Server-script testing |
| **Team Test** | Publishes state, opens multiple Studio clients | Multiplayer, RemoteEvent flow, replication bugs |

- **Device Emulator** tests layout/aspect ratios and input methods only — **not** CPU/GPU performance. Most Roblox players are on mobile, so test the real framerate on a 3–4 year old mid-range Android before shipping.
- **Player Emulator** simulates locale/region for localization and content-policy testing.
- **Publish:** File → Publish to Roblox (Ctrl+P). Set access (Public / Friends / Private) and Game Settings (max players, chat, genre tags, thumbnails) in the Creator Hub / Studio Home tab. Public experiences have identity-verification requirements (`as of May 2026 — verify current thresholds`). Changes don't go live until republished.

Sources: see [../data/sources.json](../data/sources.json) — environmental-art curriculum, modular-environments tutorial, Unified Lighting thread, instance-streaming docs, testing-modes docs, stud-unit reference.
