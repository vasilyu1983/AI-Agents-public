# Synthetic Data Generation Reference

Canonical source: [ai-data-curation-pretraining/SKILL.md](../SKILL.md)

## Table of Contents

- [When to Use Synthetic Data](#when-to-use-synthetic-data)
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

## When to Use Synthetic Data

Synthetic data addresses gaps that web crawls cannot fill:
- **Domain scarcity**: math reasoning, code, scientific derivations are underrepresented in CommonCrawl.
- **Format control**: step-by-step reasoning, structured textbooks, dialogue — difficult to find at scale in natural web text.
- **Quality ceiling**: web text quality is noisy; synthetic data from a strong generator can have higher average quality on a target skill.

Synthetic data is **not** a replacement for diverse web data. It should always be mixed with human-sourced text.

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

**Key constraint**: check the generator model's terms of service before using its outputs in a training corpus. GPT-4 and Claude explicitly prohibit using outputs to train competing models.

---

## Rephrasing the Web — WRAP and Nemotron-CC

A distinct paradigm from "generate from scratch": instead of synthesizing new documents or discarding low-quality pages, **rewrite existing web pages** into higher-quality form. This keeps the factual grounding and diversity of real web data while lifting style and density.

**WRAP** (arXiv 2401.16380): prompt an instruct model to rephrase each web document into a target style — "like Wikipedia", "in question-answer format", "for a child", "in clear English". Training on a mix of original + rephrased text yields ~3x pretraining speedup at fixed compute and improves perplexity across domains. Generate multiple styles per document to add format diversity.

**Nemotron-CC** (arXiv 2412.02595): scales rephrasing to full CommonCrawl to solve the **token-yield problem** — DCLM/edu-style filters discard ~90% of tokens, which starves multi-trillion-token runs. Nemotron-CC combines a classifier *ensemble* (averaging several quality scorers to reduce single-classifier bias) with synthetic rephrasing of mid- and low-quality pages, producing 6.3T high-quality tokens. Models trained on it beat Llama-3.1-8B-class baselines on MMLU at matched scale.

**Decontaminate rephrased data too**: the rephraser is itself a web-trained model and can inject memorized benchmark content. Apply the same 13-gram decontamination as for generated-from-scratch synthetic data.

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

Synthetic data should supplement, not replace, diverse web data.

**Recommended proportions** (domain-dependent; tune via ablations):
- Web (filtered): 70–85%
- Books / academic: 5–15%
- Code: 5–10%
- Synthetic textbooks / instruction: 2–10%
- Math: 1–5%

**Ablation discipline**: change only the synthetic proportion between runs (one variable per run). Measure eval delta on domain-specific benchmarks (coding: HumanEval; math: GSM8K, MATH; general: ARC, HellaSwag).

---

## Collapse Traps

### Model Collapse

Training iteratively on model outputs without fresh human data narrows the output distribution. The model loses tail capabilities and rare knowledge. Entropy of generated text decreases over iterations. Canonical reference: Shumailov et al., "AI models collapse when trained on recursively generated data," *Nature* 631:755–759 (2024), DOI 10.1038/s41586-024-07566-y.

**Mitigation**: always mix human-sourced data. Never train a new generation entirely on previous-generation synthetic outputs.

**2025–2026 refinement — collapse is a function of ratio and verification, not synthetic data per se**:
- A scaling-law study on mixed natural/synthetic corpora (arXiv 2510.01631, Oct 2025) found that moderate synthetic ratios (~1/3 high-quality rephrased-synthetic to ~2/3 natural web) *reduced* irreducible loss with no collapse signature — complicating the earlier "any recursion collapses" reading of Shumailov et al.
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

| Generator | ToS restriction on using outputs for training |
|-----------|----------------------------------------------|
| GPT-4 / GPT-4o | Prohibited for training competing models |
| Claude (Anthropic) | Prohibited for training models competing with Anthropic |
| Llama 3 (Meta) | Permitted for models < 700B parameters; attribution required |
| Mixtral (Mistral) | Apache 2.0; outputs are unrestricted |
| Gemma (Google) | Permitted; usage policy applies |

Verify against current ToS before using any generator's outputs in a publicly released corpus. ToS terms change.
