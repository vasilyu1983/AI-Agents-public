# Synthetic Data Generation Reference

Canonical source: [ai-data-curation-pretraining/SKILL.md](../SKILL.md)

## Table of Contents

- [Augmentation vs Synthesis](#augmentation-vs-synthesis)
- [When to Use Synthetic Data](#when-to-use-synthetic-data)
- [Rule-Based Synthesis (Faker, Chance)](#rule-based-synthesis-faker-chance)
- [Phi / Textbooks Are All You Need Recipe](#phi--textbooks-are-all-you-need-recipe)
- [Cosmopedia: Synthetic Textbooks at Scale](#cosmopedia-synthetic-textbooks-at-scale)
- [Self-Instruct](#self-instruct)
- [Evol-Instruct](#evol-instruct)
- [Nemotron / Distillation + Rejection Sampling](#nemotron--distillation--rejection-sampling)
- [Rephrasing the Web — WRAP and Nemotron-CC](#rephrasing-the-web--wrap-and-nemotron-cc)
- [Verifier-Gated Generation](#verifier-gated-generation)
- [Mixing Synthetic with Web Data](#mixing-synthetic-with-web-data)
- [Collapse Traps](#collapse-traps)
- [Licensing Constraints](#licensing-constraints)

---

## Augmentation vs Synthesis

Two different operations, often conflated (distinction per Chip Huyen, *AI Engineering*, O'Reilly 2025):

- **Data augmentation** creates new examples *from existing real data* — paraphrasing/rephrasing (WRAP is augmentation at corpus scale), back-translation, perturbing tokens or fields, reformatting the same content for multiple audiences (the Cosmopedia style-diversity trick applied to real seeds). The real datum anchors correctness; augmentation buys coverage and robustness around it.
- **Data synthesis** generates examples *from scratch* to mimic the properties of real data — model-generated textbooks (Phi, Cosmopedia), self-generated instructions (Self-Instruct), or rule-based fake records (next section). Nothing anchors correctness except your generator and your verifier gate.

The practical consequence: augmented data inherits the license, PII exposure, and contamination status of its source — scrub and decontaminate the *source* first. Synthesized data has no source lineage to lean on, so the verifier gate (below) carries the entire quality burden.

## When to Use Synthetic Data

Synthetic data addresses gaps that web crawls cannot fill:
- **Domain scarcity**: math reasoning, code, scientific derivations are underrepresented in CommonCrawl.
- **Format control**: step-by-step reasoning, structured textbooks, dialogue — difficult to find at scale in natural web text.
- **Quality ceiling**: web text quality is noisy; synthetic data from a strong generator can have higher average quality on a target skill.

Compare any synthetic-only proposal with a provenance-checked natural-data baseline; monitor diversity, rare-knowledge retention, and target-task scores at the intended token horizon.

---

## Rule-Based Synthesis (Faker, Chance)

Not all synthesis needs a model. Procedural generators can produce reproducible structured test records without sending source data to a model. Generated names and identifiers can coincide with real ones; they do not anonymize source records by themselves:

- **Faker** — Python [`faker`](https://faker.readthedocs.io/) and JS [`@faker-js/faker`](https://fakerjs.dev/): locale-aware fake names, addresses, emails, companies, dates, financial fields. Seedable for reproducibility.
- **Chance** — [chancejs.com](https://chancejs.com/): JS random generator for primitives, people, locations, times; lighter than Faker, same role.
- Same family: language-specific ports (Bogus for .NET — already used in this repo's `qa-testing-nunit` templates) and schema-driven tabular tools.

**Where they fit in an ML pipeline** (vs model-based generation above):

| Use | Rule-based (Faker/Chance) | Model-based (Phi/Self-Instruct-class) |
| --- | --- | --- |
| Synthetic stand-ins for scrubbed names/emails | Useful after the original PII has been removed and the replacement fields have been checked | Can regenerate memorized PII; verify outputs |
| Structured/tabular records for format-following fine-tuning (JSON extraction, form parsing, NER on synthetic invoices) | ✅ generates the *fields*; pair with templates or an LLM for the surrounding text | Wraps the records in natural language |
| Test fixtures and pipeline smoke tests at every curation stage | ✅ | ❌ |
| Reasoning, prose, dialogue, domain knowledge | ❌ no semantics, only formats | ✅ this file's main subject |

**The trap**: rule-based records have uniform, unrealistic *distributions* (Faker's names are flat samples, real names are Zipfian; field correlations are absent). Fine for format training and scrubbing; wrong for anything where the model should learn realistic distributions. Model collapse doesn't apply, but distribution mismatch does — validate on real held-out data.

---

## Phi / Textbooks Are All You Need Recipe

**Paper**: arXiv 2306.11644 (Microsoft Research, 2023)

**Core insight**: 1.3B parameters trained on ~1.3B tokens of synthetic "textbook-quality" Python content outperforms 13B models trained on natural web data on HumanEval and MBPP.

**Generation recipe**:
1. Prompt GPT-3.5 or GPT-4 with: "Write a self-contained, educational section of a Python textbook covering [topic]. Use clear explanations, worked examples, and exercises."
2. Diversify topics: draw from a curriculum covering data structures, algorithms, I/O, OOP, error handling.
3. Deduplicate generated outputs (MinHash at 0.5 threshold — synthetic outputs cluster more than web).
4. Quality filter: retain only outputs where the code examples pass a syntax check and unit tests pass.

**Scale**: Phi-1 used 6B tokens of synthetic textbooks + 1B tokens of filtered web code. Phi-1.5 extended to natural language textbooks using the same recipe.

---

## Cosmopedia: Synthetic Textbooks at Scale

**Source**: HuggingFace blog, 2024. Model: Mixtral-8x7B-Instruct.

**Scale**: 30B tokens across 100M files (Cosmopedia v2).

**Recipe**:
1. Seed topics from web data: extract representative topics from Wikipedia titles, Stanford ENCYC, OpenStax textbooks, and educational websites.
2. Vary style per prompt: "Write a textbook section for a 10-year-old", "Write a university-level lecture transcript", "Write a story that teaches this concept".
3. Generate with Mixtral-8x7B-Instruct at temperature 0.9 for diversity.
4. Post-filter with an edu-score classifier (DistilBERT trained on human labels of educational quality).

**Key finding**: style diversity (multiple audience levels and formats) significantly improves downstream benchmark scores vs. single-style generation. Entropy of output vocabulary was higher with diverse prompts.

**Decontaminate separately**: synthetic outputs from a model trained on CommonCrawl may reproduce benchmark content. Run n-gram decontamination on Cosmopedia data independently.

---

## Self-Instruct

**Paper**: arXiv 2212.10560 (Wang et al., 2022)

**Goal**: generate instruction-following data from a model without human annotation, using a small seed set.

**Algorithm**:
1. Start with 175 seed tasks (human-written instruction + input + output triples).
2. Sample 8 tasks from the pool.
3. Prompt the model: "Here are 8 task examples. Generate 20 new, diverse tasks."
4. Filter generated tasks: remove tasks where ROUGE-L similarity with any existing task exceeds 0.7 (diversity gate).
5. For each accepted task, prompt the model to generate inputs and outputs.
6. Filter outputs: remove outputs where the model refused, produced empty answers, or where input = output.
7. Add accepted examples to the pool; iterate.

**Scale**: original paper reached 52K instructions with GPT-3 as generator.

**For pretraining**: Self-Instruct generates instruction-following format data. Mix into a pretraining corpus at low proportions (1–5%) to improve instruction following without dominating the distribution.

---

## Evol-Instruct

**Paper**: arXiv 2304.12244 (Xu et al., WizardLM 2023)

**Goal**: increase difficulty and diversity of instruction data by iterative rewriting.

**Evolution operations**:
- `add_constraints`: "Add a constraint that the solution must use no built-in sort functions."
- `deepen`: "Make the task require deeper knowledge of [topic]."
- `concretize`: "Replace the abstract requirement with a specific domain example."
- `increase_reasoning`: "Add a step requiring multi-step logical deduction."
- `breadth_evolution`: generate a sibling task in a different domain with similar complexity.

**Algorithm**:
1. Start with seed instructions (can be Self-Instruct output or human-written).
2. For each instruction, sample one evolution operation.
3. Prompt the generator model with the evolution operation + original instruction.
4. Evolver answer: generate a response to the evolved instruction.
5. Eliminate failures: remove if the evolved instruction is unchanged, has an answer that is too short (< 1 sentence), or if the response contains "I cannot" refusals.
6. Iterate: use evolved instructions as seeds for next round.

**For pretraining**: Evol-Instruct data increases the density of complex reasoning examples. Most useful for code and math domains. Keep rounds ≤ 3 to avoid distribution collapse toward a narrow difficulty band.

---

## Nemotron / Distillation + Rejection Sampling

**Distillation** (knowledge distillation at data level): use a large teacher model (GPT-4, Claude, Llama-3-70B) to generate high-quality outputs for given inputs. Train the student on teacher outputs.

**Rejection sampling**: generate N responses from a model; keep only those that pass a verifier or quality check.

```
For each prompt p:
  Generate N=32 responses from generator model
  Score each response with verifier / reward model
  Keep top-k responses (or all with score ≥ threshold)
  Add accepted (p, response) pairs to training set
```

**Nemotron recipe** (NVIDIA, 2024): use a reward model trained on human preference data to score synthetic outputs; filter to top quartile; iterate.

**Key constraint**: check the generator model's current terms of service or licence before using its outputs in a training corpus; commercial providers commonly restrict training competing models on outputs.

---

## Rephrasing the Web — WRAP and Nemotron-CC

A distinct paradigm from "generate from scratch": instead of synthesizing new documents or discarding low-quality pages, **rewrite existing web pages** into higher-quality form. This keeps the factual grounding and diversity of real web data while lifting style and density.

**WRAP** (arXiv 2401.16380): prompt an instruct model to rephrase each web document into a target style — "like Wikipedia", "in question-answer format", "for a child", "in clear English". Training on a mix of original + rephrased text yields ~3x pretraining speedup at fixed compute and improves perplexity across domains. Generate multiple styles per document to add format diversity.

**Nemotron-CC** (arXiv 2412.02595): scales rephrasing to full CommonCrawl to solve the **token-yield problem** — DCLM/edu-style filters discard ~90% of tokens, which starves multi-trillion-token runs. Nemotron-CC combines a classifier *ensemble* (averaging several quality scorers to reduce single-classifier bias) with synthetic rephrasing of mid- and low-quality pages, producing 6.3T high-quality tokens. Models trained on it beat Llama-3.1-8B-class baselines on MMLU at matched scale.

**Decontaminate rephrased data too**: the rephraser is itself a web-trained model and can inject memorized benchmark content. Apply the same n-gram decontamination as for generated-from-scratch synthetic data.

**When to reach for rephrasing vs. filtering**: filter first; rephrase the pages filtering would otherwise drop, when token budget is the binding constraint. Do not rephrase already-high-quality text — you add cost and a collapse-risk vector for no quality gain.

---

## Verifier-Gated Generation

Unfiltered synthetic data degrades pretraining quality — the generator produces plausible-sounding but factually incorrect or incoherent content at non-negligible rates.

**Verifier types by domain**:

| Domain | Verifier | How it gates |
|--------|----------|-------------|
| Code | Unit tests, syntax checker | Execute code; accept if tests pass |
| Math | Symbolic solver (SymPy), checker model | Verify final answer numerically |
| Factual | Retrieval-augmented fact check | Cross-reference claim against trusted corpus |
| General quality | Reward model / edu-score classifier | Score ≥ threshold |

**Protocol**:
1. Generate N=8–32 responses per prompt.
2. Run verifier on all N.
3. Accept if at least one response passes; use the passing response(s).
4. If zero pass, discard the prompt — do not include failing examples.

**Threshold setting**: calibrate on a held-out labeled set. Do not use the acceptance rate as a quality signal without calibration — a low acceptance rate may mean the verifier is too strict or the prompts are miscalibrated.

---

## Mixing Synthetic with Web Data

Start with a diverse, provenance-checked natural corpus, then vary one synthetic share at a time in the ablation. The useful proportion depends on task mix, generator quality, verifier, and training horizon; fixed recipe percentages do not transfer reliably.

**Ablation discipline**: change only the synthetic proportion between runs (one variable per run). Measure eval delta on domain-specific benchmarks (coding: HumanEval; math: GSM8K, MATH; general: ARC, HellaSwag).

---

## Collapse Traps

### Model Collapse

Training iteratively on model outputs without fresh human data narrows the output distribution. The model loses tail capabilities and rare knowledge. Entropy of generated text decreases over iterations. Canonical reference: Shumailov et al., "AI models collapse when trained on recursively generated data," *Nature* 631:755–759 (2024), DOI 10.1038/s41586-024-07566-y.

**Mitigation**: retain a natural-data baseline, verify generated examples, and measure diversity and rare-knowledge retention across generations. Do not assume that a fixed natural/synthetic ratio alone prevents collapse.

**Refinement — collapse depends on ratio, style and verification, not synthetic data per se**:
- A scaling-law study on mixed natural/synthetic corpora (arXiv 2510.01631) found that moderate synthetic ratios (~1/3 high-quality rephrased-synthetic to ~2/3 natural web) *reduced* irreducible loss with no collapse signature — complicating the earlier "any recursion collapses" reading of Shumailov et al. — while also reporting collapse patterns for pure textbook-style synthetic data. The kind of synthetic data matters, not only the ratio.
- "Escaping Model Collapse via Synthetic Data Verification" (ICLR 2026 workshop) shows that external verification — a stronger model, a human rater, or a task-specific verifier scoring generated data before it enters the training set — prevents collapse even under fully recursive retraining, where mixing with a fixed ratio of real data alone does not.
- **Practical takeaway**: don't treat "mix in real data" as a sufficient safeguard on its own. Combine it with the verifier-gating protocol above (unit tests / symbolic checkers / reward models), and re-run the collapse diagnostics (distinct-n, entropy) each generation, not just once.

### Diversity Collapse

Heavy quality filtering of synthetic data removes stylistically unusual but valid outputs. After 2–3 rounds of Evol-Instruct, outputs cluster in a narrow difficulty band.

**Detection**: measure distinct-1, distinct-2 (unique unigrams and bigrams as a fraction of total), and output length distribution across the synthetic dataset. Compare to the seed distribution.

### Generator Contamination

A model trained on CommonCrawl has likely seen evaluation benchmarks. Its synthetic outputs may reproduce benchmark content verbatim or near-verbatim.

**Mitigation**: decontaminate synthetic data independently, using the same n-gram matching procedure as web data. Log every match with the source benchmark.

---

## Licensing Constraints

**Lookup step, per generator, before generation starts:** read the provider's current terms of service or the open-weight model's licence, and record (a) whether outputs may train another model, (b) any competing-model, size or user-count threshold, (c) attribution or naming duties, and (d) the version or date you read. A restriction on (a) or (b) blocks public release of the corpus; (c) goes into the datasheet. Do not keep a per-vendor table here: terms change.

Re-check the terms before each public release; the version you read at generation time is what the datasheet records.
