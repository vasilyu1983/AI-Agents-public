# Discovering & Vetting New Architectures

The field moves faster than the advisor skill can be re-edited. When the right approach might
be newer than what's catalogued, **discover and vet it deliberately** — don't adopt on hype or
reject on unfamiliarity. This skill *decides*; the scout skills *find*.

## Table of Contents

- [Discover (scout, don't drift)](#discover-scout-dont-drift)
- [Vet Before Adopting](#vet-before-adopting)
- [Reframe the Output](#reframe-the-output)
- [Emerging Classes (mid-2026)](#emerging-classes-mid-2026)

---

## Discover (scout, don't drift)

Scan a small, fixed set of signals rather than drifting across the whole feed:

| Signal type | Example source | Reads |
|---|---|---|
| Release feed | Hugging Face Daily Papers | what's new this week |
| Human-preference leaderboard | LMArena | crowd-ranked head-to-head quality |
| Cost / intelligence tracker | Artificial Analysis | the price/quality frontier |
| Open-weight traction | r/LocalLLaMA | what self-hosters actually run |
| Synthesis | one newsletter | the digested "so what" |

Hand the actual scouting to [research-arxiv-scout](../../research-arxiv-scout/SKILL.md) and
[research-scout](../../research-scout/SKILL.md) — this skill decides; they find.

## Vet Before Adopting

Leaderboard rank is a *filter, not a verdict*:

1. **Elimination filter only.** Treat public benchmarks as a way to rule candidates *out*, not
   in. Expect a large gap between lab scores and your workflow — benchmarks get saturated,
   contaminated, and gamed. Prefer contamination-resistant, still-unsaturated ones.
2. **Build a golden set.** 50–200 real examples from *your* task; score there (deterministic
   checks + LLM-judge + a little human review). Non-negotiable — hand off methodology to
   [ai-evals](../../ai-evals/SKILL.md).
3. **Hold the problem constant.** Same eval, same inputs across candidates — otherwise you are
   measuring the harness, not the architecture.
4. **Let it settle.** Wait a couple of weeks after a splashy release before betting a design on
   it; verify version-specific claims against primary sources.

## Reframe the Output

Increasingly the answer is not one winning architecture but a **routing policy** — which
model/approach for which task class. "Pick one" and "route among several" are both valid
outputs; say which you're producing.

## Emerging Classes (mid-2026)

Know they exist; don't bet a build on them yet. Full named-examples-and-status table is in
[decision-matrices.md](decision-matrices.md#emerging-architecture-classes-mid-2026):
tokenizer-free/byte-level (BLT), JEPA/latent-predictive (V-JEPA 2), world models (Genie 3),
looped/recurrent-depth (Ouro), diffusion-LM (Mercury 2, Gemini Diffusion). These move monthly;
default to "named but not yet load-bearing" unless your own golden-set eval says otherwise.
