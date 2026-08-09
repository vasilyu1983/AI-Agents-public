# Curator Newsletters Strategy

## Table of Contents

- [What Curators Are Good For](#what-curators-are-good-for)
- [Curator Map](#curator-map)
- [Discovery Path](#discovery-path)
- [Credibility Signals](#credibility-signals)
- [Biases](#biases)

## What Curators Are Good For

Curators do the **synthesis work** that papers and blogs don't:
- Pre-filtering — they read 100 papers so you read 5
- Pattern naming — "this is an instance of X" mapping
- Applicability framing — what to actually do with the idea
- Caveats — they call out failure modes that papers gloss over

The catch: curators reflect their own bias. Use them as discovery + framing, not as primary evidence.

## Curator Map

| Curator | URL | Cadence | Strengths | Watch out for |
|---------|-----|---------|-----------|---------------|
| Lilian Weng (Lil'Log) | https://lilianweng.github.io/ | Sporadic, deep | LLM agents, RL, prompting, evals — long-form synthesis | Long gaps between posts; coverage gaps in newer topics |
| Sebastian Raschka (Ahead of AI) | https://magazine.sebastianraschka.com/ | Weekly | LLM internals, fine-tuning, training recipes; reproducibility-leaning | Skews toward training-time methods over inference / system patterns |
| Eugene Yan | https://eugeneyan.com/ | Periodic, applied | Applied LLM patterns, eval, ML systems | Industry case studies sometimes miss research depth |
| Latent Space | https://www.latent.space/ | Weekly+ | Builder interviews, applied frameworks, AI engineering | Conversational; needs source-checking |
| Simon Willison | https://simonwillison.net/ | Daily | LLM tools, prompt injection, applied tinkering with verbose method notes | Personal-blog format; depth varies |
| The Batch (Andrew Ng) | https://www.deeplearning.ai/the-batch/ | Weekly | Balanced research + industry digest; broad coverage | Each item is brief; depth requires drill-down |
| Import AI (Jack Clark) | https://jack-clark.net/ | Weekly | AI policy + research weekly; high signal on emerging systems and safety | Policy-leaning; less applicability detail |
| Chip Huyen | https://huyenchip.com/ | Periodic | ML systems, LLM stack, deployment patterns | Lower frequency |
| Andrej Karpathy | https://karpathy.bearblog.dev/blog/ | Rare | Foundational ML and LLM internals, when posting | Very low cadence; treat as bonus, not primary |
| Interconnects (Nathan Lambert) | https://www.interconnects.ai/ | 1–3x/week | Post-training, RLHF, open-model ecosystem — deep and current | Narrower scope; less coverage of pretraining and systems |
| Davis Summarizes Papers (Davis Blalock) | https://dblalock.substack.com/ | Weekly | Systematic triage of ~600 arXiv ML papers → 10–20 picks; 10k+ researcher subscribers | Selection shaped by one person's taste; coverage skews to ML fundamentals over systems |

## Discovery Path

1. **Subscribe to or RSS-poll** 3-5 curators whose coverage overlaps with your work.
2. **Skim weekly digests** for items tagged with your topic.
3. **For high-signal items**, follow through to the underlying paper or post; the curator's note is framing, not evidence.
4. **When 2+ curators cover the same idea**, that's a cresting signal — but it's also a hype-bubble risk (trap 8).
5. **For a topic scan**, check curator archives by topic tag if available (Eugene Yan, Lilian Weng, Chip Huyen all maintain searchable archives).

## Curator-Specific Tips

- **Lilian Weng** posts essays that themselves become canonical references. Treat as both a discovery layer and a reference text.
- **Sebastian Raschka** ablations-heavy and reproducibility-focused — best curator for steal-confidence on training methods.
- **Eugene Yan** explicitly maps research to industry application — best for applicability framing.
- **Latent Space** podcast transcripts are surprisingly high-signal but require time to skim.
- **Simon Willison** is the best source for "I tried this with code, here's what happened" — fast applied signal.
- **The Batch** is the broadest digest — useful as a coverage net, not for depth.
- **Import AI** focuses on system-level capability changes more than method-level techniques.
- **Interconnects (Nathan Lambert)** is the go-to source for post-training and RLHF developments; covers open-model ecosystem (Llama, Mistral, alignment fine-tuning) with more depth than most newsletters. RSS: https://www.interconnects.ai/feed
- **Davis Summarizes Papers** triages ~600 arXiv ML papers weekly down to 10–20 — useful as a high-recall filter before deeper reading. Skews ML fundamentals; less coverage of systems or NLP-specific work.
- **@_akhaliq (AK) on X** curates Hugging Face Daily Papers; his X posts surface papers slightly ahead of the HF Daily Papers page — useful as a real-time leading indicator. Not a newsletter; X-only signal.

## Credibility Signals

- **Curator links to the underlying paper or repo** — minimum bar; if a curator describes a method without sourcing, downgrade.
- **Curator names limitations or failure modes** — separates synthesis from amplification.
- **Curator has track record** (years of consistent coverage with corrections when wrong) — trust accrues.
- **Independent corroboration across curators** — if 3+ curators independently flag the same idea as worth attention, the evidence is strong even if no single one is authoritative.

## Biases

- **Selection bias.** Curators read what they're already interested in. New topics outside their beat are under-covered.
- **Recency / hype bias.** Curators chase what's new and discussed; mature methods are under-covered relative to importance.
- **English-language and Western-startup bias.**
- **LLM bias.** Most active curators in 2024-2026 cover LLMs disproportionately; classical ML, theory, and systems work get less attention.
- **Sponsorship.** Some newsletters take sponsors; check disclosures. Not always a problem, but worth knowing.
- **Audience optimization.** Newsletters that grow fast often optimize for engagement, which can shade content toward hot takes.
