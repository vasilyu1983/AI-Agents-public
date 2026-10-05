# Eval Dataset Construction: Questions, Ideal Answers, and the Tuning Loop

How to build the (question, ideal-answer) set an eval runs against, get the
system's own answers, compare them, and iterate the dataset itself. This is the
upstream half of evaluation — the grading half lives in `llm-judge-bias.md`,
`threshold-derivation.md`, and `flake-and-reproducibility.md`.

ai-evals owns eval *method*. Statistical sizing lives in
[eval-statistics.md](eval-statistics.md#paired-binary-sizing-mcnemar) and
agreement (kappa) bands in [threshold-derivation.md](threshold-derivation.md#measure-judge-human-agreement);
those are the only versions to cite. For worked composition procedures — task
distribution tables, stratified sampling, difficulty binning, dataset versioning,
bias audits — see the companion [eval-dataset-design.md](eval-dataset-design.md).
This file owns sourcing, ideal-answer authoring, and the run→compare→tune loop.

## Table of Contents

- [The loop in one picture](#the-loop-in-one-picture)
- [Step 1: Source the questions](#step-1-source-the-questions)
- [Step 2: Author the ideal answers](#step-2-author-the-ideal-answers)
- [Step 3: Get the system's answers](#step-3-get-the-systems-answers)
- [Step 4: Compare ideal vs actual](#step-4-compare-ideal-vs-actual)
- [Step 5: Tune — but tune the right thing](#step-5-tune--but-tune-the-right-thing)
- [Building the robustness slice by perturbing memorized instances](#building-the-robustness-slice-by-perturbing-memorized-instances)
- [Record schema](#record-schema)
- [Known traps](#known-traps)
- [Checklist](#checklist)

## The loop in one picture

```text
source questions  ->  author ideal answers  ->  run system  ->  compare
      ^                                                            |
      |                                                            v
      +--------- tune (dataset? prompt? system? threshold?) <------+
```

The single most common mistake is conflating the legs: a low score can mean the
*system* is wrong, the *ideal answer* is wrong, the *grader* is wrong, or the
*question* is ambiguous. Step 4 must attribute the failure before Step 5 acts.

## Step 1: Source the questions

Do not invent questions from imagination — they drift toward what the system
already handles. Source from where real difficulty lives:

| Source | Why it matters | Watch out for |
|--------|----------------|---------------|
| **Production logs / traces** | Real distribution, real phrasing, real edge cases | PII; must de-identify before it becomes an eval set |
| **Support tickets / chat transcripts** | Captures what users actually struggle with | Survivorship bias toward complaints |
| **Failed runs / incident reports** | Every past failure should become a regression case | Don't only collect failures — you'll lose the happy-path baseline |
| **Subject-matter experts** | Coverage of important-but-rare cases users haven't hit yet | Experts over-index on hard cases; balance with easy ones |
| **Adversarial / red-team authoring** | Stress boundaries, injection, refusal, unanswerable | Keep proportional; not the whole set |

Rules:

- **Mirror production proportions, then over-sample rare high-impact slices.**
  See qa-agent-testing for the proportion table and stratified sampling.
- **Every fixed bug becomes a question.** The regression slice is built from
  real failures, not synthesized ones.
- **Include unanswerable / refusal questions.** A dataset with no
  "correct answer is 'I don't know'" cases cannot measure hallucination.
- **Synthetic questions are a supplement, not the base.** Cap synthetic at a
  minority of the set and flag them in metadata; an all-synthetic set measures
  the generator, not your users. (HF synthetic-testset tooling and the ai-rag
  `generate_synthetic_rag_testset.py` scaffold are starting points, not the set.)

## Step 2: Author the ideal answers

There are two valid targets — pick per question type, and never blur them:

- **Reference answer** (exact/near-exact expected output). Use for factual QA,
  extraction, classification, structured output. Grading = match / similarity.
- **Rubric** (criteria the answer must satisfy). Use for open-ended, multi-valid
  answers (explanations, summaries, advice). Grading = criteria checklist, often
  LLM-judged. Store the criteria, not one "golden" prose answer, so a correct
  answer phrased differently still passes.

Authoring discipline:

- **Author the ideal answer from the same context the system gets** — for RAG,
  from the retrieved/allowed evidence, not from the author's own knowledge.
  Otherwise you grade the system against information it could never have.
- **Capture acceptable variants.** For reference answers, list valid alternates
  (`"acceptable_answers": [...]`) so phrasing differences aren't false failures.
- **Two independent authors + adjudication** for anything that will gate
  releases; track agreement against the kappa bands in
  `threshold-derivation.md`. A single author's
  "ideal" is one opinion.
- **An LLM may *draft* ideal answers; a human must *approve* them** for the
  golden set. LLM-authored-and-LLM-graded with no human anchor is a closed loop
  that drifts toward the model's own style (self-preference). Use the LLM for the
  large dynamic set; keep a human-anchored golden subset as ground truth.
- **Write down *why* the ideal answer is ideal** (the failing requirement it
  encodes). A test that can't say what reverting would break is a weak test
  (see flake-and-reproducibility.md, Rule 9 in coding-behavior).

## Step 3: Get the system's answers

- Run the **actual system under test** (same prompt, model, tools, retrieval,
  decoding params), not a simplified stand-in — otherwise the comparison is
  against a system you won't ship.
- **Pin and record** model version, prompt version, seed, and decoding params
  with each run; they are part of the measurement (flake-and-reproducibility.md).
- For stochastic systems, run each question **k times** and keep all k, not just
  one — variance is signal, and single runs produce flaky verdicts.
- Capture the **full trace** (retrieved evidence, tool calls), not just the final
  text, so Step 4 can attribute failures to retrieval vs generation vs tools.

## Step 4: Compare ideal vs actual

Layer the comparison cheapest-first (see threshold-derivation.md gate design):

1. **Deterministic check** — exact/normalized match, schema validity, required
   citations present, refusal-when-expected. Cheap, no calibration, runs always.
2. **Similarity** — for reference answers where wording varies (embedding or
   token overlap), with a tuned threshold.
3. **LLM-as-judge against the rubric** — for open-ended answers; apply every
   judge-bias control (different judge model, both orderings, behavior-pinned
   rubric, structured verdict). See llm-judge-bias.md.

**Attribute every failure before acting:**

| Symptom | Likely cause | Where to look |
|---------|--------------|---------------|
| System answer correct but scored fail | grader/ideal-answer wrong | rubric, acceptable_answers, judge prompt |
| Verdict flips across k runs | noisy grader or genuine system variability | regrade frozen outputs to locate the variability; retain real system failures (flake doc) |
| Right info missing from answer | retrieval/tool failure, not generation | trace evidence vs ideal's required evidence |
| Confident wrong answer | system hallucination | this is a real regression — keep it |
| Many fails on one slice | dataset slice too hard, or real weakness | compare slice pass-rate to its historical floor |

## Step 5: Tune — but tune the right thing

Step 4's attribution tells you *which knob*. In order of preference:

- **Fix the dataset** when the ideal answer was wrong, the question was
  ambiguous, or acceptable variants were missing. This is expected and frequent
  early on — bump the dataset version (minor for label fixes, major for schema
  changes; see qa-agent-testing versioning).
- **Fix the grader/threshold** when correct answers fail or wrong answers pass —
  recalibrate against the human-labeled set; never move the threshold *after*
  seeing results just to pass (threshold-on-the-fly is gaming).
- **Fix the system** (prompt, retrieval, model, tools) when the failure is real.
  This is the only tuning that should be gated; re-run the *frozen* dataset
  before/after so the delta is attributable to the system change alone.
- **Repair broken graders** after regrading frozen outputs locates the defect; report any quarantine and coverage gap, and mark a broken blocking grader inconclusive. Keep genuine stochastic system failures in reliability counts.

Discipline that keeps the loop honest:

- **Freeze the golden set during system tuning.** If you edit the dataset and the
  system in the same iteration, you can't attribute the score change to either.
- **Never tune the system on the golden set you gate with.** That's testset
  leakage — hold out the gating set; iterate on a separate dev split
  (flake-and-reproducibility.md).
- **Empirically calibrate difficulty** by running the system k times and binning
  by pass-rate/variance (qa-agent-testing has the procedure) — labels authors
  guess are often wrong.

## Building the robustness slice by perturbing memorized instances

Step 1 sources questions from where real difficulty lives. This section covers a
slice you cannot source that way, because the cases do not exist yet: variants of
problems the model has already memorized. Sourcing alone will not produce them —
production logs contain the *canonical* phrasings, which are exactly the ones the
model handles.

The framing here is **François Chollet's attributed analysis**, from Chollet &
Watson, *Deep Learning with Python*, 3rd ed. (Manning, 2026), ch. 19 §§19.1.1–19.1.3
(pp. 565–570). It is a specific and contested position on what LLMs are doing, not
a consensus view — cite it as his argument. It is worth carrying anyway because
the *eval-design* consequence holds regardless of whether you accept his account
of the mechanism.

His three failure modes, and what each implies for a case set:

**1. Non-adaptation to novelty.** Chollet's claim is that a trained model is a
static "interpolative database" whose parameters are frozen after training, so it
excels at "recognizing or generating patterns highly similar to those encountered
during training" and is "inherently poor at adaptation." The sharp version, quoted:
"An LLM's ability to solve a given problem has nothing to do with problem
complexity, and everything to do with familiarity — they will break their teeth on
any sufficiently novel problem, no matter how simple."

*Eval consequence:* difficulty labels that rank cases by intrinsic complexity are
measuring the wrong axis. Stratify by **familiarity** — how likely this exact shape
appeared in training — separately from complexity. A trivially easy but unfamiliar
case belongs in the hard slice.

**2. Oversensitivity to phrasing.** Chollet reports that "innocuous prompt
modifications, such as changing place and people's names in a text paragraph or
variable names in a block of code, can significantly degrade LLM performance." Two
worked instances he gives:

- The "Alice in Wonderland" riddle — "Alice has N brothers and she also has M
  sisters. How many sisters does Alice's brother have?" (answer M + 1). Asking it
  "with values commonly found in online instances of the riddle (like N = 3 and
  M = 2) will generally result in the correct answer, but try tweaking the values
  of M and N, and you will quickly get incorrect answers." He cites Nezhurina et
  al., "Alice in Wonderland: Simple Tasks Showing Complete Reasoning Breakdown in
  State-Of-the-Art Large Language Models" (`arXiv:2406.02061`).
- Monty Hall variants, where models "tend to always output the canonical answer to
  the puzzle… regardless of whether it makes sense in context."

He also notes these specific prompts "were patched later on by special-casing
them," and that "even already patched prompts will still fail if you make small
changes to them" — which is the reason a *fixed* published probe is close to
worthless as a gate.

*Eval consequence:* this is the actionable core. **Build the robustness slice by
perturbing memorized instances**, not by writing fresh hard questions. Take a case
the system passes, then vary the surface while holding the required reasoning
fixed: swap the numeric values, rename the people/places/variables, invert a
premise so the canonical memorized answer becomes wrong, reorder clauses,
substitute synonyms ("rewrite" for "rephrase"). Author the ideal answer from the
*perturbed* problem — the trap is copying the canonical answer forward. A pass on
the canonical form paired with a fail on a meaning-preserving perturbation is the
finding; report the pair, not the aggregate.

**3. No generalizable discrete programs.** Chollet's third mode is that memorized
programs "often don't generalize well… especially true for programs that encode
any kind of discrete logic." His example is character-level addition: a Transformer
trained on hundreds of thousands of digit pairs reaches "very high accuracy. Very
high, but not 100%," and for state-of-the-art LLMs not hardcoded to shell out to
code, "they only have about 70% accuracy — quite underwhelming." Note the hedge in
his own phrasing ("about"); do not harden it. He adds that "their accuracy is
strongly dependent on which digits are being added, with more common digits
leading to higher accuracy."

*Eval consequence:* for any task with discrete/algorithmic structure, a single
aggregate accuracy hides the shape of the failure. Slice by the *operand* — which
digits, which value ranges, which input lengths — because performance varies by
how common the specific values are, not by how hard the operation is. And check
whether a passing case is passing because the system delegated to a tool; a
tool-backed pass and a parametric pass are different capabilities and should be
labeled differently in the record.

**Scope note:** this is *model* brittleness. Brittleness in the **judge** —
position, verbosity, self-preference, rubric-wording sensitivity — is a different
failure and lives in `llm-judge-bias.md`. Adversarial
*safety* perturbation (jailbreak paraphrase, injection) lives in
`safety-redteam-eval.md`. This section is about capability cases only.

## Record schema

A portable per-case record that supports every step above:

```json
{
  "id": "qa_0042",
  "question": "What is the refund window for digital goods?",
  "context": "[evidence the system is allowed to use, if grounded]",
  "ideal": {
    "type": "reference | rubric",
    "reference_answer": "14 days from purchase.",
    "acceptable_answers": ["two weeks from purchase"],
    "rubric": ["states 14-day window", "cites policy section", "no extra claims"],
    "why_ideal": "encodes the policy fact users most often get wrong"
  },
  "expected_behavior": { "must_cite": true, "refuse_if_unanswerable": false },
  "metadata": {
    "slice": "policy", "difficulty": "easy", "source": "support_tickets_2026q1",
    "is_synthetic": false, "authors": ["a1", "a2"], "version": "1.2.0",
    "perturbation_of": null, "perturbation_kind": null, "familiarity": "canonical"
  }
}
```

For a robustness-slice case, `perturbation_of` carries the id of the canonical
case it was derived from, `perturbation_kind` names the surface change
(`values` | `entity-names` | `premise-inverted` | `clause-order` | `synonyms`),
and `familiarity` flips to `perturbed` — so the canonical/perturbed pair can be
scored together rather than averaged apart.

Run output stores `actual_answer`, `trace`, `run_params` (model/prompt/seed),
and per-layer `verdicts` so Step 4 attribution is possible.

## Multimodal case construction

When eval cases involve image or audio context, additional construction discipline
applies:

- **Store the image or audio asset with the case record**, not just a URL — URLs
  rot and the visual ground truth must be reproducible at eval time. Reference the
  asset path or inline the content in the record schema.
- **Graders that strip formatting before judging cannot strip images.** Do not
  pass multimodal cases through a text-normalization pipeline that silently drops
  the non-text modality; confirm the grader receives the full context.
- **Ideal answers must reference the visual ground truth** explicitly (e.g.,
  "the chart shows a peak at week 3" rather than "the answer is week 3") so the
  rubric can be verified against the asset independently of the model's output.
- Flag each case with `"modality": ["text", "image"]` (or the relevant set) in the
  metadata so multimodal cases can be sliced and analyzed separately from text-only
  cases.

## Known traps

- Authoring ideal answers from author knowledge instead of the system's allowed
  context — grades against unreachable information
- All-synthetic datasets — measure the generator, not users
- LLM authors and LLM grades with no human anchor — drifts to model self-preference
- Editing dataset and system in the same iteration — failures unattributable
- Tuning the system on the gating set — testset leakage, inflated scores
- One ideal "golden" prose answer for open-ended questions — penalizes valid
  rephrasings; use a rubric + acceptable variants instead
- A dataset with no unanswerable cases — cannot measure hallucination/refusal
- Only canonical phrasings of known problems — measures familiarity, not
  capability; add perturbed variants of cases the system already passes
- Copying the canonical ideal answer onto a perturbed case — the perturbation
  usually changes the correct answer, and this silently grades against the old one
- Averaging canonical and perturbed cases into one accuracy — hides the
  pass-then-fail pair that is the actual finding

## Checklist

- [ ] Questions sourced from production/tickets/failures/SMEs, not imagination
- [ ] Production proportions mirrored; rare high-impact slices over-sampled
- [ ] Every past bug added as a regression question
- [ ] Unanswerable/refusal cases included
- [ ] Robustness slice built by perturbing cases the system already passes, with
      ideal answers re-authored from the perturbed problem and canonical/perturbed
      pairs reported together
- [ ] Ideal answers authored from the system's allowed context
- [ ] Reference vs rubric chosen per question type; acceptable variants captured
- [ ] Golden subset human-approved (LLM may draft, human signs off)
- [ ] System run with pinned/recorded model/prompt/seed; full trace captured
- [ ] Comparison layered (deterministic → similarity → judge) with bias controls
- [ ] Each failure attributed (system vs ideal vs grader vs question) before tuning
- [ ] Golden set frozen during system tuning; dev split separate from gate set
- [ ] Dataset versioned on every change
