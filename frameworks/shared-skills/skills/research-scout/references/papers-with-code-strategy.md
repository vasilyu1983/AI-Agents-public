# Papers with Code Strategy (DEAD SOURCE — read this first)

## Status

**Papers with Code was shut down by Meta in July 2025.** `paperswithcode.com` and all
sub-paths (`/sota`, `/methods`, `/task/*`, `/method/*`, `/paper/*`, `/search`) now
301-redirect to Hugging Face Trending Papers. The leaderboards, the verified-code
links, and the search API are gone and are **not** being maintained.

Do not query `paperswithcode.com` in any workflow step or trap counter-recipe.
Treat any instruction that says "search Papers with Code" as superseded by the
**Live Replacement** section below.

## Table of Contents

- [Historical Archive (frozen)](#historical-archive-frozen)
- [Live Replacement for the Reproducibility Signal](#live-replacement-for-the-reproducibility-signal)
- [Migration of the Old Counter-Recipes](#migration-of-the-old-counter-recipes)

## Historical Archive (frozen)

The only surviving artifact is the data dump:

- `https://github.com/paperswithcode/paperswithcode-data` — frozen JSON of the
  9.3k benchmarks / 79.8k papers / 5.6k datasets as of mid-2025. No longer updated.

Use it **only** for pre-July-2025 method/benchmark history. Anything published after
mid-2025 will not be in it. Never present it as a current reproducibility signal.

## Live Replacement for the Reproducibility Signal

Papers with Code's value was "methods linked to verified code and benchmark numbers."
Reconstruct that signal from sources that are still alive:

1. **Direct GitHub repo + star/commit signal** — find the paper's official repo
   (arXiv abs page "Code" link, or the README). Active maintenance + independent
   forks/reimplementations is the reproducibility signal. Delegate deep repo
   inspection to the `research-git` skill.
2. **Hugging Face Papers** — `https://huggingface.co/papers` (daily) and
   `?date=trending`. Community upvotes + linked artifacts (models/datasets/Spaces)
   are the closest live proxy for "this method has running code."
3. **OpenReview / `alphaXiv`** — `https://openreview.net` for venue-reviewed methods
   with reproducibility discussion; `https://www.alphaxiv.org/` for community-flagged
   reproduction failures.
4. **Semantic Scholar** — `intent=methodology` citations (see
   [semantic-scholar-strategy.md](semantic-scholar-strategy.md)) show who actually
   built on the method, not just cited it.

**Reproducibility-tag mapping (replaces the old PwC lookup):**

- Official repo + ≥1 independent reimplementation + runnable benchmark → `code+benchmarks`
- Official repo only, no independent reimplementation → `code_only`
- Paper has full hyperparameters but no public code → `paper_only`
- Depends on a closed model/dataset/API → `proprietary` (trap 11)

## Migration of the Old Counter-Recipes

`known-traps.md` no longer instructs "search Papers with Code." The equivalent
disconfirmation step is now: **search GitHub for third-party reimplementations
(via `research-git`), check Semantic Scholar methodology-intent citations, and
check OpenReview/alphaXiv for flagged reproduction failures.** If none exist
6+ months after publication, the irreproducibility / cherry-picked-baseline
suspicion stands.
