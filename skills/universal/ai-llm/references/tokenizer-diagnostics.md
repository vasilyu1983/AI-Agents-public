# Tokenizer Diagnostics

Debugging discipline for production tokenizer failures. When an LLM misbehaves on
only a *subset* of inputs, inspect how those inputs tokenize before you touch the
prompt, the retrieval layer, or the model choice.

This file is the **debugging** counterpart to
[ai-pretraining: bpe-tokenizer](../../ai-pretraining/references/bpe-tokenizer.md),
which covers *building* a BPE tokenizer — merge rules, vocabulary construction,
training-corpus choice. Read that one when you are creating a tokenizer; read this
one when an existing tokenizer is already hurting you in production.

## Table of Contents

- [The Operational Heuristic](#the-operational-heuristic)
- [Evaluating a Tokenizer: Fertility and Parity](#evaluating-a-tokenizer-fertility-and-parity)
- [Failure Mode 1: Glitch / Undertrained Tokens](#failure-mode-1-glitch--undertrained-tokens)
- [Failure Mode 2: Domain-Mismatch Compression Penalty](#failure-mode-2-domain-mismatch-compression-penalty)
- [Failure Mode 3: Number Tokenization and Arithmetic](#failure-mode-3-number-tokenization-and-arithmetic)
- [Failure Mode 4: Subword Brittleness to Typos](#failure-mode-4-subword-brittleness-to-typos)
- [Diagnostic Checklist](#diagnostic-checklist)

---

## The Operational Heuristic

Pai's rule, and the reason this file exists: **when a model misbehaves on only some
inputs, tokenize those inputs and look at the output first.** Tokenization is cheap to
inspect and sits upstream of everything else. A subset-specific failure — one language,
one customer's product SKUs, one document type, one numeric format — is far more
often a tokenization artifact than a reasoning failure.

Concretely, before escalating:

1. Take the failing inputs and the passing inputs.
2. Tokenize both with the *exact* tokenizer the deployed model uses.
3. Compare token counts per word (fertility) and eyeball the segmentation.
4. If the failing set fragments noticeably worse, you have found the layer to fix.

The model examples below are **mechanism demonstrations**, not claims about any
current model. They illustrate *how* a tokenizer failure presents; verify behavior
against whatever model you actually deploy.

---

## Evaluating a Tokenizer: Fertility and Parity

Two standard metrics, both cheap to compute on your own corpus:

**Fertility** — average number of tokens needed to represent a dataset, calculated as
tokens divided by words. Higher fertility means lower compression power. A tokenizer
achieves higher compression by being trained on larger datasets during the vocabulary
generation phase.

**Parity** — how fairly a tokenizer treats two languages, calculated as the ratio of
tokens needed to represent the same data in one language versus the other. Many models
advertise multilingual support while their tokenizer was trained on an English-centric
corpus, so a non-English sentence may need several times more tokens than the English
equivalent (Petrov et al.). Parity is a direct cost and context-budget issue, not just a
fairness one: the same content costs more tokens and consumes more of the window.

**The compression → downstream-performance link is disputed.** Goldman et al. report
that higher compression leads to better downstream performance; Schmidt et al. dispute
this in their experiments. Treat compression as a *cost and coverage* metric you can
measure directly, and do not assume improving it will improve task accuracy. Direction
of the disagreement only — do not attach magnitudes to either side.

Practical use: compute fertility on your own domain corpus for each candidate model's
tokenizer before committing. This is one of the few pre-deployment checks that requires
no inference calls.

---

## Failure Mode 1: Glitch / Undertrained Tokens

Tokenization algorithms can leave tokens in a vocabulary whose referent has effectively
vanished from the pretraining data. Pai's worked case: the token
**"SolidMagiGoldkarp"** — representing a now-deleted Reddit user, one of the site's most
active posters because of his quest to count to infinity — was a token in the GPT-2
tokenizer vocabulary. The same tokenizer was reused for GPT-3 models, but the
pretraining dataset had changed and did not include many or any references to it. So a
token existed with no signal in the pretraining data to learn from, which produced
anomalous behavior. Such tokens are called **glitch tokens** or **undertrained tokens**.

The mechanism generalizes beyond that one string, and is the thing to remember:

- A tokenizer is often frozen and reused across model generations.
- The pretraining corpus is *not* frozen across those generations.
- Any token whose supporting data drops out becomes a near-random embedding.

Why it matters operationally: if user input or retrieved documents can contain rare
strings — usernames, SKUs, ticket IDs, scraped artifacts — those may land on
undertrained tokens and produce behavior that looks like a jailbreak or a hallucination
but is an embedding artifact.

**Token etymology** as a diagnostic habit: enumerate the rare tokens in your model's
vocabulary and trace their origins. Beyond curiosity, knowing where rare tokens came
from tells you about the characteristics of the pretraining dataset — useful when you
are choosing between models for a domain.

---

## Failure Mode 2: Domain-Mismatch Compression Penalty

If you run a general-purpose tokenizer over domain-specific data — healthcare, finance,
law, biomedical — the compression ratio drops, because domain words have no tokens of
their own and get split into multiple pieces.

Pai's worked example. The sentence *"The addition of CAR-T cells and antisense
oligonucleotides drove down incidence rates."* under the FLAN-T5 tokenizer splits as:

```text
['▁The', '▁addition', '▁of', '▁C', 'AR', '-', ' T', '▁cells', '▁and', '▁anti', ' s',
' ense', '▁', ' oli', ' gon', ' u', ' cle', ' o', ' t', ' ides', '▁drove', '▁down',
'▁incidence', '▁rates', ' .', '</s>']
```

Read the fragments: `oligonucleotides` is shattered into the seven word-pieces
`oli / gon / u / cle / o / t / ides` (plus a standalone `▁` word-boundary marker),
`antisense` into `anti / s / ense`, and `CAR-T` into `C / AR / - / T`. Three domain
terms consume roughly a dozen tokens.

Consequences, in order of how often they bite:

- **Context budget.** Domain documents cost materially more tokens than their word count
  suggests. Budget from a measured fertility number, not from a words × 1.3 rule.
- **Cost.** Same multiplier, applied to every call.
- **Representation quality.** The model never sees the domain term as a unit, so it has
  no single embedding for the concept.

The fix, and its cost, are in
[fine-tuning-recipes.md](fine-tuning-recipes.md) under Tokenizer/Encoding: adding domain
tokens to the vocabulary is cheap; giving them *learned representations* is not.

A related design point worth knowing: purpose-built domain models sometimes ship
domain-specific tokens and tokenization rules rather than relying on a general
vocabulary. GALACTICA (Meta) introduced markers such as `[START_REF]`/`[END_REF]` for
citations, `<WORK>` for internal working memory used in reasoning and code generation,
and `[START_SMILES]`/`[START_DNA]`/`[START_AMINO]` with their closing counterparts for
molecular, DNA, and amino-acid sequences. If your domain has structured spans, this is
the pattern to imitate.

---

## Failure Mode 3: Number Tokenization and Arithmetic

Numbers are a recurring, under-diagnosed arithmetic failure source. A general BPE
vocabulary contains multi-digit chunks that occur frequently in text, so a number is
segmented by *corpus frequency*, not by place value. A number like `937` may tokenize as
`9` + `37` — an arbitrary split that carries no positional meaning. Two numbers of the
same magnitude can segment completely differently, so the model cannot rely on a stable
digit-position representation.

This is why arithmetic errors are often not reasoning errors: the model never received
the digits in a form where column alignment is recoverable.

Known mitigations:

- **Digit-per-token tokenization** — assign each digit in a number its own token. This is
  the approach GALACTICA took, and variants of it appear in later models.
- **Consistent right-to-left grouping** — some tokenizers group digits in fixed-size
  chunks from the right, preserving place value.
- **Do the arithmetic outside the model** — for anything where correctness matters, call
  a calculator tool rather than tuning tokenization. This is the production answer;
  tokenizer fixes are for model builders.

Diagnostic: if your failures cluster on numeric inputs, tokenize a sample of the failing
numbers before assuming the model "can't do math."

---

## Failure Mode 4: Subword Brittleness to Typos

Subword tokenization is brittle to small perturbations in a specific way: a single typo
can re-segment a word entirely. A correctly spelled word may be one token while its
misspelling fragments into several unrelated pieces, so the input the model sees is not
a slightly-noisy version of the original — it is a structurally different sequence.

Where this actually shows up: large models absorb this fairly well, because they have
seen enough noisy text during pretraining to recover the intent from fragmented
subwords. Smaller BERT-class encoders, trained on less data and with less capacity to
generalize over segmentation noise, degrade noticeably on typo-heavy input. This
matters when picking the model tier for user-generated text — search queries, support
tickets, chat — where typos are the norm rather than the exception.

Do not read this as "big models are typo-proof." Read it as: **tolerance to segmentation
noise scales with model capability**, so a pipeline validated on clean text may fail
when moved to a smaller model or to noisier input, and typo robustness deserves its own
eval slice.

---

## Diagnostic Checklist

Run this when an LLM fails on a subset of inputs:

- [ ] Tokenized the failing inputs with the deployed model's exact tokenizer
- [ ] Compared fertility (tokens/word) on failing vs passing inputs
- [ ] Computed parity if more than one language is involved
- [ ] Measured fertility on the domain corpus, not on generic English
- [ ] Checked whether failing inputs contain rare strings that may hit undertrained tokens
- [ ] Checked numeric inputs for arbitrary digit splits
- [ ] Added a typo-robustness slice to the eval set if inputs are user-generated
- [ ] Re-costed the context budget from measured fertility, not a words × constant rule
- [ ] Decided whether the fix is vocabulary extension (see
      [fine-tuning-recipes.md](fine-tuning-recipes.md)), a different model, or an
      external tool

---

## Sources

- Suhas Pai, *Designing Large Language Model Applications* (O'Reilly, 2025), Ch. 3 —
  glitch/undertrained tokens, fertility and parity, the FLAN-T5 domain-fragmentation
  example, GALACTICA domain tokens, vocabulary extension.
- Goldman et al. and Schmidt et al. — the disputed compression → downstream-performance
  link, cited by Pai. Direction only; no magnitudes claimed here.
- Petrov et al. — cross-language tokenization disparity, cited by Pai.
