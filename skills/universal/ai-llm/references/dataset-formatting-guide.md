# Dataset Formatting Guide (Instruction, Chat, Transformation)

Templates and rules for building clean, consistent datasets for SFT and instruction tuning.

## Table of Contents

- [1. Instruction Format (Recommended)](#1-instruction-format-recommended)
- [2. Chat Format (Multi-Turn)](#2-chat-format-multi-turn)
- [3. Transformation Format (Simple I/O)](#3-transformation-format-simple-io)
- [4. Dataset Hygiene Rules](#4-dataset-hygiene-rules)
- [5. SFT Loss Masking and Collate Mechanics](#5-sft-loss-masking-and-collate-mechanics) (incl. chat-turn masking and packing)
- [6. Formatting Deliverables Checklist](#6-formatting-deliverables-checklist)

---

## 1. Instruction Format (Recommended)

Each example:

{
"instruction": "<what user wants>",
"input": "<optional context>",
"output": "<ideal response>"
}

**Rules**

- Use empty string for missing inputs  
- Keep outputs concise  
- Avoid multi-step reasoning unless required  

---

## 2. Chat Format (Multi-Turn)

{
"messages": [
{"role": "system", "content": "<policy/role>"},
{"role": "user", "content": "<query>"},
{"role": "assistant", "content": "<ideal reply>"}
]
}

**Rules**

- No overlapping roles  
- Ensure each conversation is self-contained  
- Avoid leaking system prompts in assistant outputs  

---

## 3. Transformation Format (Simple I/O)

{
"input": "<raw text>",
"output": "<transformed text>"
}

Use for:

- Rewriting  
- Summarization  
- Classification  
- Extraction  

---

## 4. Dataset Hygiene Rules

### A. No Leakage

- Do not include system prompts in model outputs  
- Do not include personal info  
- Remove timestamps or IDs that encode answers  

### B. Deduplication

- Remove near-duplicate samples  
- Deduplicate across categories  

### C. Quality Enforcement

- Each output = ideal model response  
- Avoid ambiguous tasks  
- Avoid mixed languages unless intentional  

---

## 5. SFT Loss Masking and Collate Mechanics

Formatting the JSON is only half of dataset preparation. The other half is what the
collate function does to the *targets* before they reach the loss. This section covers
the mechanics for supervised fine-tuning; `ai-pretraining` delegates SFT formatting
here.

### A. `ignore_index=-100`

PyTorch's cross entropy defaults to `cross_entropy(..., ignore_index=-100)`, meaning any
target position labeled `-100` is skipped entirely in the loss. Raschka demonstrates
this directly: computing the loss over two examples, then adding a third whose target is
`-100`, produces an identical loss value — the extra entry contributes nothing.

This is the mechanism behind every masking decision below. Replace a target token ID
with `-100` and that position stops affecting training.

### B. Mask Padding, Keep the First EOS

Batches are padded to equal length with the end-of-text token. Those padding tokens
should not train the model, so in the *targets* they are replaced with `-100`.

**Keep one end-of-text token unmasked in the targets.** Raschka is explicit that the
initial end-of-text token in each target sequence stays as its real ID while the
*additional* padding tokens are masked. The reason is functional: the model has to learn
to emit an end-of-text token, since that is the signal that a response is complete. Mask
all of them and the model never learns to stop.

Concretely, a target sequence ends like `[..., 4, 50256, -100, -100]` — real tokens,
then one live EOS, then masked padding.

### C. Per-Batch Dynamic Padding

Padding is applied inside the collate function, per batch, to the longest sequence in
*that* batch — not globally to the longest sequence in the dataset. This keeps wasted
compute proportional to within-batch length variance rather than to the dataset's worst
case.

A production collate function typically carries:

- `pad_token_id` — the token used to pad inputs
- `ignore_index=-100` — the value written into targets for masked positions
- `allowed_max_length` — an optional truncation cap applied to both inputs and targets
  after padding, so a single long example cannot blow up the batch

Sort or bucket examples by length before batching if length variance is high; dynamic
padding only helps when the batch is reasonably homogeneous.

### D. Contested: Masking Instruction Tokens

Beyond padding, it is **common** to also mask the target token IDs corresponding to the
instruction and input sections, so the loss is computed only over the response. The
stated rationale is that this trains the model to focus on generating accurate responses
rather than memorizing instructions, which can help reduce overfitting.

**This is contested, not settled.** Raschka notes that researchers are divided on
whether masking instructions is universally beneficial during instruction fine-tuning,
and cites Shi et al., "Instruction Tuning With Loss Over Instructions"
(<https://arxiv.org/abs/2405.14394>, 2024), which reports conditions where *not* masking
the instructions benefits model performance. Raschka's own worked example does not apply
instruction masking, leaving it as an exercise.

Direction only — no magnitude is claimed here, and none should be inferred. Practical
handling:

- Do not treat instruction masking as a default best practice.
- Treat it as a hyperparameter: run it both ways on your own eval set if the choice is
  load-bearing.
- Padding masking is *not* contested — always mask padding, always keep the first EOS.

Source: Sebastian Raschka, *Build a Large Language Model (From Scratch)* (Manning,
2024), Ch. 7.

### E. Chat SFT: Loss on Assistant Turns; Packing Stays Inside Examples

- **Multi-turn chat SFT: compute loss on assistant tokens only.** System, user, and
  tool-result turns are context, not behavior to imitate — mask them to `-100`, keep
  each assistant turn's end-of-turn token live. Render the mask from the *same chat
  template* the model will be served with, then decode one masked example and eyeball
  which spans are live before launching the run. (Section D's contested question is the
  narrower one: whether a single-turn *instruction* also carries loss.)
- **Packing must not cross example boundaries.** When several examples are packed into
  one sequence, each token may attend only within its own example (per-example position
  IDs / varlen attention, not one causal mask over the whole pack), and the last token of
  one example must not be trained to predict the first token of the next. Check your
  trainer's packing mode does both; if it cannot, disable packing rather than train on
  cross-example attention.

---

## 6. Formatting Deliverables Checklist

- [ ] JSONL validated with `jq`  
- [ ] UTF-8 encoded  
- [ ] No trailing commas  
- [ ] Uniform field names  
- [ ] Balanced sample distribution  
- [ ] Full dataset documented in README  
