# Hugging Face Papers Strategy

## Table of Contents

- [Discovery Path](#discovery-path)
- [Query Patterns](#query-patterns)
- [Credibility Signals](#credibility-signals)
- [Biases](#biases)

## Discovery Path

1. **Daily highlights**: https://huggingface.co/papers — community-curated daily list with discussion.
2. **Trending view**: https://huggingface.co/papers/trending — cresting-method detection (`papers?date=trending` returns HTTP 400).
3. **By date**: https://huggingface.co/papers?date=YYYY-MM-DD — for scoped historical scans.
4. **Per-paper page**: https://huggingface.co/papers/{{arxiv_id}} — comments, models that cite the paper, datasets, demos.
5. **JSON endpoints**, documented in the Hub OpenAPI spec (https://huggingface.co/.well-known/openapi.json, browsable at https://huggingface.co/spaces/huggingface/openapi; the Hub API docs page now points there): `GET /api/daily_papers` ("Get Daily Papers"; add `?date=YYYY-MM-DD` for a day) at https://huggingface.co/api/daily_papers, `GET /api/papers/search?q={{terms}}` ("Perform a hybrid semantic / full-text-search on papers"), `GET /api/papers` ("List arXiv papers sorted by published date"), and `GET /api/papers/{{paperId}}`. Re-read the spec for parameters before automating, since it is the source of truth and changes without notice. There is no RSS feed (`papers.rss` returns 404).

HF Papers is essentially a community-curation layer on top of arXiv — papers must be uploaded to arXiv to appear. The added value is the curation, comments, and model/dataset/demo back-references.

## Query Patterns

Walk the daily lists for the window; use the JSON endpoints for automation once you have confirmed they answer.

```text
# Most reliable: walk daily papers for the last N days
https://huggingface.co/papers?date=2026-04-30
https://huggingface.co/papers?date=2026-04-29
...

# Same days as JSON (undocumented; verify on first use)
https://huggingface.co/api/daily_papers?date=2026-04-30
https://huggingface.co/api/papers/search?q=speculative+decoding

# Direct paper page (use arXiv ID without version suffix)
https://huggingface.co/papers/2402.12345
```

For topic-scoped scanning, fetch daily lists for the time window and filter client-side by title/abstract keyword; the search endpoint is a shortcut, not a substitute for the daily walk. Don't construct other synthetic URLs — they may break silently, and dead ones (RSS, `date=trending`) have already been retired from this file.

## Credibility Signals

- **Daily upvote count** — relative; not absolute quality, but indicates community interest.
- **Comments by recognized authors / curators** — sometimes a paper gets a "this is broken because X" comment; high-value.
- **Linked models / datasets / spaces** — concrete artifacts on HF Hub corroborate the paper. Stronger signal than raw upvotes.
- **Featured / Editor's Picks** — HF curation team flags some papers; weak corroboration but worth noting.

## Biases

- **LLM/VLM/agents skew.** HF Papers heavily favors generative AI; classical ML, systems, and theory are underrepresented.
- **Open-weights bias.** Methods that release weights or code on HF Hub are over-represented.
- **English / Western bias** inherited from arXiv.
- **Hype bubbles.** Daily upvotes are noisy; popular ≠ correct. Apply trap 8 (`hype-bubble`) routinely.
- **No peer review.** Inherits from arXiv; HF curation is not editorial vetting.
