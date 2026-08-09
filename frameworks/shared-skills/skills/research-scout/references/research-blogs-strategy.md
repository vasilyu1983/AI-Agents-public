# Industry Research Blogs Strategy

## Table of Contents

- [What Industry Blogs Are Good For](#what-industry-blogs-are-good-for)
- [Source Map](#source-map)
- [Discovery Path](#discovery-path)
- [Credibility Signals](#credibility-signals)
- [Biases](#biases)

## What Industry Blogs Are Good For

- **Production-tested methods** at scales academic papers can't match.
- **Engineering trade-offs** that academic papers omit (latency, cost, infra).
- **Concrete recipes** for adoption (deployment, monitoring, integration).

Limitations: corporate selection bias (trap 7) is severe. Companies publish what works for them and what serves their narrative. Independent corroboration matters more here than for academic papers.

## Source Map

| Source | URL | Best for | Bias to watch |
|--------|-----|----------|---------------|
| Anthropic Research | https://www.anthropic.com/research | LLM safety, interpretability, agents, Claude evals | Promotes Claude capabilities |
| OpenAI Research | https://openai.com/research | Scaling, alignment, agents | Promotes GPT capabilities |
| Google DeepMind | https://deepmind.google/discover/blog/ | RL, scaling, multi-modal, theorem proving | Gemini-leaning |
| Google Research | https://research.google/blog/ | ML, systems, IR, accessibility, fairness | Broad; less product-promotional |
| Meta AI Research | https://ai.meta.com/research/ | Open-weights, vision, agents, embeddings | Open-source forward, Llama-promoting |
| Microsoft Research | https://www.microsoft.com/en-us/research/blog/ | Systems, ML, HCI, dev tools | Azure / Copilot leaning |
| Apple ML Research | https://machinelearning.apple.com/ | On-device ML, privacy, speech, vision | Apple-Silicon-favoring |
| Hugging Face Blog | https://huggingface.co/blog | Applied recipes, integrations, tutorials | Open-source promotional |
| Distill (archive) | https://distill.pub/ | Visual ML explanations | On hiatus; archive only |

## Discovery Path

1. **Pick relevant labs** for your topic (e.g., for LLM agents: Anthropic + DeepMind + Meta + curator coverage).
2. **Walk recent posts** by date or RSS feed.
3. **Filter by topic** in the title/intro.
4. **For each candidate**, identify whether the post is:
   - A research result with ablations and benchmarks — usable as a research paper would be
   - An engineering write-up with deployment lessons — usable as a system-design pattern
   - A product announcement with capabilities claims — usable only as discovery, not evidence
5. **Check for the underlying paper** if the blog references one. The paper is often where evidence lives; the blog is the trailer.

## Discovery Tips

- **Look for "Lessons we learned" or "What didn't work" posts** — high-signal, rare.
- **Engineering-team blogs** (e.g., "Engineering at OpenAI", "Anthropic Engineering") often contain more applicable patterns than the research blog itself.
- **Annual retrospectives** (e.g., "2025 in review") can surface methods you missed.
- **Author-focused tag pages** when an individual researcher or engineer posts consistently strong material — track them.

## Credibility Signals

- **Linked paper or technical report** — strong signal. Without one, the post is marketing.
- **Numbers with confidence intervals** — companies that report variability are doing real measurement.
- **Failure modes discussed** — companies that publish limitations are publishing research, not marketing.
- **Open-weights / open-code release** — turns the post into a falsifiable claim.
- **Acknowledgement of related work** — research blogs that cite competitors' methods are more trustworthy than those that don't.

## Biases

- **Selection bias (trap 7).** Only successes get published. Companies sit on failures.
- **Capability-marketing framing.** "Our model can do X" is product positioning; "method M improves Y by Z%" is research. Distinguish.
- **Internal-tooling assumptions.** Methods may depend on internal datasets, internal infra, or internal models — apply trap 11 (`proprietary-component`) routinely.
- **Anniversaries and PR cycles.** Big posts cluster around conferences and product launches; not all of them carry new content.
- **Author availability.** Industry researchers move; broken author tag pages are common.
