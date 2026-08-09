# Generative Media Prompt Patterns

> Operational reference for **prompting generative image and video models** to produce consistent-persona short-form content — shot-listing, text-to-image persona, character-consistency edits, image-to-video, lip-sync drive, multi-clip assembly. This is prompt *authoring* for generative media; multimodal *input* analysis (vision/audio/doc) is in [multimodal-prompt-patterns.md](multimodal-prompt-patterns.md). End-to-end production pipeline and compliance gate live in `marketing-content-strategy/references/tiktok-content-production.md` (R6/R7) — this file is the prompt-craft depth behind that pipeline's steps.

**Freshness anchor:** 2026-05. Example model names are intentionally avoided unless verified in the current project context — the **prompt structure is durable; model names churn**. Re-verify exact model + parameter syntax against provider docs before rollout. Numeric/behaviour claims about specific models are indicative, not provider-confirmed.

## Contents

- [Operating truth](#operating-truth)
- [The shot-spec anatomy](#the-shot-spec-anatomy-the-load-bearing-pattern)
- [Pattern catalog](#pattern-catalog-apply)
- [Anti-pattern catalog](#anti-pattern-catalog-refuse)
- [Recipe map](#recipe-map-generation-order--qa-loops)
- [Recipes / copy-paste templates](#recipes--copy-paste-templates)

## Operating truth

A generative-media prompt is a **shot spec, not a sentence**. Quality and consistency come from filling every slot of the spec explicitly; vague prose is the single biggest cause of identity drift and unusable footage. The model fills any slot you leave blank — usually wrongly and differently each run.

## The shot-spec anatomy (the load-bearing pattern)

Every image and video prompt is the same ordered slot list. Omit a slot only deliberately.

`subject (locked identity ref) · wardrobe/props · action · setting · camera (shot size + angle + movement) · lens/optics · lighting · mood/film-look · audio (ambience + dialogue, video only) · duration/pacing · negative (what to exclude)`

## Pattern catalog (apply)

| Pattern | What it does | When |
|---|---|---|
| **Identity-anchor prefix** | Start every generation with the *same verbatim* persona descriptor block (+ source reference image), then vary only the scene slots | Every multi-asset persona — the #1 anti-drift lever |
| **Reference-image > words for identity** | Pass the locked still as an image reference; use text only for *what changes*. Never re-describe the face in prose once you have a reference | Any current consistency-preserving image editor |
| **Slot-complete shot spec** | Fill all anatomy slots; unstated = randomised per run | All image + video |
| **Camera-grammar terms** | Use real film vocabulary: "85mm, shallow DOF, slow dolly-in, eye-level, handheld micro-shake" — models are trained on it | Cinematic / influencer look |
| **Single intent per clip** | One action, one camera move, ≤8–12s. Chain shots, don't cram | Image-to-video |
| **Storyboard before generate** | Break the script into an ordered shot list *before* spending render credits — purpose, shot size, talking/B-roll, duration per shot | Every multi-shot video; prevents regenerating because the cut doesn't work |
| **Continuity chaining** | Adjacent talking shots share wardrobe + lighting + time-of-day + seed; bridge any change with a B-roll cutaway or a match-cut on action — never a raw mismatched hard cut | Any video that is more than one generated clip |
| **Native-audio direction** (Veo-class) | Direct ambience + dialogue *in the prompt* ("quiet café murmur; she says: '…' — warm, unhurried") | When the model generates its own audio |
| **External-voice → lip-sync split** | Generate silent/neutral talking video, then drive mouth with the cloned ElevenLabs track in an omnimodal lip-sync model | When the persona must use a *specific* cloned voice |
| **Negative slot as a guardrail** | Explicitly exclude the known failure set: "no extra fingers, no warped text, no logo, no face morphing, no jump cut" | Every model that accepts negatives |
| **Seed/parameter lock** | Fix seed + aspect + model version across a batch so only the prompt varies | Reproducible batches |
| **Iterate one slot at a time** | Change a single slot per revision; never rewrite the whole prompt — you lose the known-good baseline | Debugging a near-miss |

## Anti-pattern catalog (refuse)

| Anti-pattern | Why it fails |
|---|---|
| **Prose blob** ("a beautiful cinematic video of a girl traveling, very realistic, 4k") | No slots → model randomises everything; nothing reproducible |
| **Re-describing the face every time** | Text descriptors drift; identity must come from the reference image + verbatim anchor block, not fresh prose |
| **Multiple actions/camera moves in one clip** | Models smear or hallucinate transitions; produces unusable warp |
| **Prompting a generic video model to "say [line] in [cloned voice]"** | It synthesises a *different* voice; cloned-voice fidelity needs the lip-sync split pattern |
| **"4k, 8k, ultra, masterpiece" token-stuffing** | 2026 models ignore quality-token spam; spend the tokens on lighting/lens/camera instead |
| **Quality-token negatives instead of failure-set negatives** | Negatives must name concrete artefacts, not adjectives |
| **Rewriting the whole prompt on a near-miss** | Destroys the known-good baseline; change one slot |
| **Mismatched hard cut between talking shots** | Lighting/identity jump screams "stitched AI"; bridge with B-roll or a match-cut |
| **Text/CTA in the platform UI dead zones** | Captions or name-as-link hidden behind TikTok/IG chrome → the funnel silently fails |
| **Stock transitions / speed-ramps as polish** | 2026 low-trust signal; default to hard cuts on action, no template effects |
| **Generating before a shot list exists** | Produces orphan clips that won't cut together; wasted render credits |

## Recipe map (generation order + QA loops)

```text
 G0  shot list  (script -> 4-8 ordered shots; THE build order)
       |
 G1  identity sheet  --> pick 1 = locked reference + verbatim anchor block
       |                 (anchor block reused byte-identical forever)
       v
 G2  multi-scene still  <--------------------------+
       |                                           |  G6 debug:
       +-- talking shot? --yes--> G3  i2v talking   |  change ONE slot,
       |                            |               |  same seed, re-run
       |                          G5  lip-sync (+VO from ElevenLabs)
       |                                           |
       +-- B-roll --------------> G4  i2v motion ---+
       |
 G7  pre-render check   (HARD GATE: pass before spending render credits)
       |
 G8  assembly  (timeline editor: order -> continuity -> audio spine ->
       |         pacing -> captions -> cover -> transitions -> export)
       v
 R7  compliance & synthetic-media gate (production ref) --> publish
```

## Recipes / copy-paste templates

Replace `‹…›`. Keep the anchor block byte-identical across a persona's whole library.

**G0 — Shot list (script → ordered shots, do this first).** Break the ≤30–60s script into 4–8 shots, each ≤8–12s (the per-clip generation ceiling). One row per shot: `# · purpose (hook/context/payoff/CTA) · shot size · talking?(needs G5) or B-roll(G4) · location · wardrobe · ~duration · VO line or ambience`. Rules: shot 1 = the hook, its gap lands in ≤2s; last shot = the name-as-link CTA block; flag every wardrobe/location/lighting change between adjacent talking shots (those need a continuity bridge in G8). The shot list *is* the build order — it tells you which G2 stills, which G3 vs G4, which G5.

**G1 — Persona identity sheet (text-to-image).**
`Full-body and head-and-shoulders portrait of ‹fully synthetic person: age, build, hair, distinct unmistakable facial features, skin detail›, ‹neutral wardrobe›, plain studio backdrop, soft key + fill, 85mm, eye-level, photoreal, natural skin texture. Negative: stylised, cartoon, warped features, extra digits, text, logo.` → pick one output = the locked reference. Save the bracket text verbatim as the **anchor block**.

**G2 — Multi-scene still (consistency edit).** Input: locked reference image + `Same person, identical face and proportions (do not alter identity). Now: ‹wardrobe change› in ‹setting›, ‹action/pose›, ‹shot size + angle›, ‹lighting + time of day›, ‹film look›. Negative: face morphing, age change, different person, warped hands, text.`

**G3 — Image-to-video, cinematic talking shot (native-audio model, e.g. Veo-class).** Input: G2 still + `‹shot size›, ‹slow camera move e.g. gentle dolly-in›, subject ‹micro-action: glances over shoulder, slight smile›, ‹lighting/ambience›. Audio: ‹environment bed›; she says, warm and unhurried: "‹≤12s line›". Duration ~8s, single continuous take. Negative: cut, jump, morphing face, extra limbs, on-screen text.`

**G4 — Motion / travel B-roll (motion-strong model, e.g. Kling-class).** Input: G2 still + `‹dynamic camera: tracking / orbit / crane›, ‹subject locomotion›, ‹environment motion: waves, crowd, traffic›, ‹golden-hour / overcast›, cinematic colour grade. No dialogue. Duration ~5s. Negative: warping, face distortion, frame stutter, watermark.`

**G5 — Lip-sync drive (omnimodal, cloned voice).** Inputs: a G3/G2 talking still or neutral clip **+** the ElevenLabs audio file. Prompt: `Drive lip and jaw to the provided audio with phoneme accuracy; preserve identity, head pose, lighting, and eye behaviour; natural micro-expressions; do not regenerate the face.` Use this whenever a *specific* cloned voice matters (a generic video model will not match it).

**G6 — Debug loop.** Near-miss? Identify the one wrong slot → re-run G2/G3 changing **only that slot**, same seed. Repeat one slot at a time. If identity drifted: the anchor block or reference image was not passed verbatim — fix that first, nothing else.

**G7 — Pre-render check (run before each batch).** (a) Shot list exists (G0) and every clip maps to a row? (b) Anchor block byte-identical to the persona's canon? (c) All anatomy slots filled or deliberately omitted? (d) Negative names concrete artefacts, not adjectives? (e) One action + one camera move per clip? (f) Cloned voice path uses the lip-sync split, not in-prompt voice request? Fail any → fix before spending render credits.

**G8 — Assembly spec (clips → finished video; tool = a timeline editor, not a generator — e.g. CapCut / DaVinci Resolve / equivalent).**
1. **Order** clips per the G0 shot list.
2. **Continuity** — never hard-cut two talking shots with mismatched lighting/identity; bridge with a G4 B-roll cutaway or a match-cut on action (intentional location jumps — the "teleport" beat — are the deliberate exception).
3. **Audio spine** — lay the ElevenLabs VO as the spine; use J/L cuts (audio leads or trails the visual by ~0.3–0.5s) so cuts feel intentional; duck the music bed −12 to −18 dB under VO.
4. **Pacing** — first cut within ≤2s; no shot >~4s without a visual change (2026 retention weighting); cut on action or beat, not on a timer.
5. **Captions** — burn after assembly (auto-caption), kept inside the 9:16 safe zone: clear of the top ~12% (handle) and bottom ~20% (platform caption + CTA + profile rail) and the right ~6% action rail. The name-as-link CTA must sit *inside* the safe zone, never under chrome.
6. **Cover frame** — set an explicit cover (a G2 frame, persona looking at lens + 3–5-word on-cover hook). The cover is chosen, not the literal first frame.
7. **Transitions** — hard cut by default; the only effect is a match-cut/whip-pan the footage actually contains. No template transitions or speed-ramps.
8. **Export** — 9:16, ≥1080×1920, H.264/HEVC ~25–30 Mbps; strip any source watermark and make ≥1 real edit before any cross-post. Compliance/disclosure gate (R7 in the production reference) applies on top before publish.
