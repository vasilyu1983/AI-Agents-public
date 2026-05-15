# Confidence Scoring

Use additive confidence, capped at `1.0`.

Suggested weights:
- README with clear purpose: `+0.20`
- manifest confirms language/runtime: `+0.20`
- CI or deploy config confirms packaging/runtime: `+0.10`
- API spec or interface artifact confirms exposure: `+0.15`
- explicit dependency/integration config: `+0.15`
- ownership signal: `+0.10`
- multiple corroborating files for architecture: `+0.10`

Penalties:
- no README: `-0.10`
- contradictory manifests or docs: `-0.15`
- only naming heuristics: `-0.20`

Never hide low confidence in prose. Surface it.

Confidence does not transfer sideways across sibling repos, providers, or services. A high-confidence finding for one adapter or repo does not justify a universal statement about the rest of the portfolio. When only a subset was checked, keep the summary labeled `subset-verified` until full coverage is complete.

