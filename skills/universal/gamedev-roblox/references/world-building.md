# World Building

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

- Character height varies by avatar body type and scale settings (classic blocky rigs are shorter than R15/Rthro): measure your target rig in Studio and build doorways and ceilings from that measurement.
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

**The lighting API has changed.** The old `Lighting.Technology` enum (`Future`/`ShadowMap`/`Voxel`/`Compatibility`) is **deprecated** — do not set it in new projects. Use:

- `Lighting.LightingStyle` — `Realistic` (≈ former Future, premium per-pixel) or `Soft` (≈ former ShadowMap/Voxel, cheaper).
- `Lighting.PrioritizeLightingQuality` — `Enabled` or `Disabled`.

Default for a new premium world: `LightingStyle = Realistic` + `PrioritizeLightingQuality = Enabled`; the engine scales across devices automatically. For mobile-first experiences, profile `Realistic` on low-end hardware before committing — it can fall back to voxel lighting at low quality levels.

Cheap, high-impact atmosphere: use `Lighting.Atmosphere` (set fog density/color on the Atmosphere object, not the deprecated `Lighting.FogEnd`) and `Lighting.Sky`. Check the current maximum light range and emissive-mask support in the lighting docs before designing around them.

> Look up the exact property names (`LightingStyle`/`PrioritizeLightingQuality`) in the current Lighting API reference; this system is recent and names may still change.

## Terrain, Parts, and Meshes

| Building block | Use | Notes |
|----------------|-----|-------|
| **Terrain** (voxel) | Organic landscapes | "Enhanced voxel terrain" was roadmap, not confirmed shipped (`verify`) |
| **Part** (primitive) | Blockout, simple geometry | Cheapest; anchor static ones |
| **MeshPart** (imported) | Detailed assets | glTF/FBX/OBJ; check current reimport features and texture-size limits in the import docs |
| **CSG/Union** | In-Studio boolean geometry | Bakes to a mesh; watch collision fidelity (see performance reference). CSG-on-textured-meshes was roadmap (`verify`) |

Prefer clean imported meshes over in-Studio CSG for environment pieces — you get explicit control over triangle count.

LOD: **SLIM** (Scalable Lightweight Interactive Models) is Roblox's next-generation level-of-detail system, enabled via `Model.LevelOfDetail`, requiring StreamingEnabled, with early versions limited to static meshes. Check its current release stage and supported content before depending on it.

## PBR and SurfaceAppearance

`SurfaceAppearance` supports full physically-based maps: `ColorMap`, `NormalMap`, `RoughnessMap`, `MetalnessMap`. The **Material Generator** produces PBR Material Variants from a text prompt and the **Texture Generator** produces ColorMap textures; check each one's current release stage and limits (see setup reference).

## Streaming

Enable `Workspace.StreamingEnabled` in Studio for large worlds to reduce client load and memory use; it cannot be set by a script. Validate the game’s missing-content and stream-out behavior before relying on streaming.

- `StreamingMinRadius` — highest-priority streaming radius around replication foci; loaded regions inside it do not stream out, but it does not guarantee immediate arrival (raises memory/bandwidth; increase carefully).
- `StreamingTargetRadius` — maximum stream-in distance around replication foci; previously loaded content can remain beyond it (smaller reduces workload but can cause pop-in).
- `Model.ModelStreamingMode` — `Atomic` streams initial descendants together; `Nonatomic` behavior depends on `Workspace.ModelStreamingBehavior`. Read the current per-model streaming controls before choosing persistence modes.
- `ReplicatedStorage`/`ReplicatedFirst` never stream — keep them lean.
- **Consequence for code:** LocalScripts must tolerate missing objects, timeout `nil`, and later stream-out. Use bounded waits when needed, clean up bindings on removal, and rebind when content returns. See performance reference traps.

Default radius values are tuned for general use; look up the current defaults and adjust to map scale.

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

- **Device Emulator** tests layout/aspect ratios and input methods only — **not** CPU/GPU performance. Most Roblox players are on mobile, so test CPU/GPU performance on a real device representing the lowest supported hardware before shipping.
- **Player Emulator** simulates locale/region for localization and content-policy testing.
- **Publish:** File → Publish to Roblox (Ctrl+P). Set access (Public / Friends / Private) and Game Settings (max players, chat, genre tags, thumbnails) in the Creator Hub / Studio Home tab. Public experiences have identity-verification requirements; look up the current thresholds before publishing. Changes don't go live until republished.

Sources: see [../data/sources.json](../data/sources.json) — environmental-art curriculum, modular-environments tutorial, Unified Lighting thread, instance-streaming docs, testing-modes docs, stud-unit reference.
