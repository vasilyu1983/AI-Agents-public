# Safety and Red-Team Evaluation

Capability evals ask "does it do the task well?" Safety evals ask "does it refuse
the things it must, resist attack, and stay safe under adversarial pressure?"
These are different measurements with different failure modes, different metrics,
and a dataset that must *grow* because attackers adapt. This file covers how to
evaluate refusal behavior, jailbreak/injection robustness, and harm — without the
two classic mistakes: over-refusal (useless assistant) and silent under-refusal
(unsafe assistant).

## Table of Contents

- [Two error types, both costly](#two-error-types-both-costly)
- [Refusal as precision and recall](#refusal-as-precision-and-recall)
- [Jailbreak and prompt-injection methodology](#jailbreak-and-prompt-injection-methodology)
- [Harm rubrics and severity](#harm-rubrics-and-severity)
- [Growing the adversarial set](#growing-the-adversarial-set)
- [Robustness, not point estimates](#robustness-not-point-estimates)
- [Agentic and tool-use safety](#agentic-and-tool-use-safety)
- [Operational discipline](#operational-discipline)
- [Checklist](#checklist)

## Two error types, both costly

Safety eval is a classification problem with two failure modes that trade off:

- **Under-refusal (false negative)**: complies with something it should refuse —
  the unsafe failure. The expensive one.
- **Over-refusal (false positive)**: refuses something benign — the annoying
  failure that makes a model useless and pushes users to unsafe alternatives.

A safety eval that only measures under-refusal will be "fixed" by making the model
refuse everything. **You must measure both on the same report**, with a benign-but-
adjacent "should comply" set sitting right next to the harmful set. Tuning safety
without an over-refusal set is the #1 safety-eval mistake.

## Refusal as precision and recall

Frame refusal as a detector and use detector metrics, not a single accuracy:

- **Refusal recall** (a.k.a. harmful-block rate): of requests that *should* be
  refused, the fraction refused. High = safe.
- **Refusal precision** / **over-refusal rate**: of requests refused, the fraction
  that should have been refused / the fraction of benign requests wrongly refused.
- Report both and the operating point. A single "97% safe" hides whether the model
  is over-refusing 20% of benign traffic.
- Grade refusal *quality* too: a good refusal is clear, non-judgmental, and offers
  a safe alternative where appropriate — not just "I can't help with that."

## Jailbreak and prompt-injection methodology

Test the model the way an attacker would, not just with naked harmful asks
(which any model blocks):

- **Direct jailbreaks**: roleplay, hypothetical framing, "for a novel," obfuscation
  (base64, leetspeak, low-resource languages), prefix-injection, refusal-suppression
  ("never say you can't"), many-shot jailbreaking (long context of fake compliant
  turns), token-smuggling.
- **Indirect prompt injection** (the agentic threat): malicious instructions hidden
  in *retrieved content, tool outputs, web pages, files, emails* the agent reads.
  This is now the dominant real-world attack on tool-using agents — eval it
  explicitly by planting injected instructions in the data the agent ingests and
  checking it doesn't follow them.
- **Measure attack success rate (ASR)** per attack family, not one pooled number —
  you need to know *which* family breaks the model.
- Use both static known-attack suites and **adaptive** attacks (an attacker model
  that iterates against your defenses); static-only ASR overstates robustness.

## Harm rubrics and severity

- Grade by **harm category** (violence, self-harm, illicit, CSAM, privacy, etc.)
  and **severity tier**, not pass/fail — a mild policy miss and an egregious one
  are not the same incident.
- Use a **rubric-based judge** with explicit category definitions; safety judging
  is high-stakes, so it needs strong human calibration (see `advanced-judging.md`,
  `threshold-derivation.md`) and a human-reviewed sample on every release.
- For the highest-severity categories, **humans define ground truth** — never gate
  CSAM/self-harm purely on an LLM judge (Rule 5: model for judgment, humans for
  high-stakes ground truth).

## Growing the adversarial set

Unlike capability sets, a safety set is never "done":

- **Every successful jailbreak becomes a permanent regression case.** The set
  grows monotonically; today's patch must not regress tomorrow.
- **Automated red-teaming**: use an attacker LLM to generate and mutate attacks at
  scale, then human-confirm the hits. This is how you keep ahead of a frozen suite
  that the model has effectively memorized.
- **Diversity over volume**: 50 distinct attack *strategies* beat 5,000 paraphrases
  of one. Track strategy coverage, not just case count.
- Watch for **safety-set contamination**: public jailbreak benchmarks leak into
  training data and inflate apparent robustness — keep a private held-out attack
  set.

## Robustness, not point estimates

- A model that blocks an attack at temperature 0 may comply at temperature 1, or on
  the 3rd resample. Run safety cases **k times** and report worst-case, not mean —
  for safety, the tail is the metric (one success in 20 tries is a breach).
- Test robustness to trivial perturbations (rephrasing, added whitespace, language
  switch). Fragile safety that breaks on paraphrase is not safety.

## Agentic and tool-use safety

For tool-using agents, expand beyond text harm:

- **Excessive agency**: does it take destructive/irreversible actions (delete, send,
  pay, escalate privilege) without confirmation? Eval with sandboxed tools and
  check for unsafe action attempts.
- **Injected-instruction following**: covered above — the agent must treat tool/
  retrieved content as *data*, not *commands*.
- **Confused-deputy / data exfiltration**: does it leak secrets or another tenant's
  data when prompted via tool output? Eval with planted secrets it must not emit.

## Multimodal safety surface

Vision inputs introduce attack surface not covered by text-only safety training.
When the system accepts images, video, or audio, safety eval must expand beyond
text-only cases:

- **Visual jailbreaks**: harmful instructions embedded in images (rendered text,
  diagrams, screenshots) that bypass text-input filters. Include cases where the
  harmful content is image-only with a benign-looking text wrapper.
- **Cross-modal inconsistency**: cases where the text instruction says X but the
  image implies Y. The model must handle the conflict safely — not silently pick
  the more permissive interpretation.
- **Audio injection**: where applicable, test speech-embedded instructions
  (analogous to indirect text injection) to confirm the model does not execute
  commands delivered acoustically.
- Use **MMMU** and **Video-MME** as task-distribution anchors when selecting
  benign multimodal capability baselines — safety tuning must not degrade
  cross-modal task performance on these distributions.

## Provider-native safety classifiers as a new red-team surface

Some frontier providers now ship an inline safety classifier in front of the
flagship model: it intercepts requests in specific high-risk categories
(commonly cybersecurity exploits, biology/chemistry dual-use, and model
distillation/extraction) and transparently routes a small minority of sessions
to a more conservative sibling model instead of the one the caller requested.
This architecture introduces two new eval surfaces that a capability-only eval
suite will miss entirely:

- **Classifier boundary testing**: inputs that probe the boundary between the
  full-capability model and the conservative fallback. Near-boundary inputs may
  produce inconsistent behavior — a prompt that triggers fallback on one
  phrasing may not on a paraphrase. Eval classifier-boundary behavior
  explicitly rather than assuming monotone safety properties.
- **Fallback-seam consistency**: when a session routes to the fallback model,
  the response contract (output format, tool use, safety posture) must hold.
  Evals that only run against the flagship model may never exercise the
  fallback path at all. To test the seam: issue fallback-triggering inputs,
  confirm the fallback fires, and verify the fallback model's response
  satisfies the same output-contract requirements your system depends on.

Add fallback-seam test cases to your safety regression suite whenever your
provider documents this kind of embedded-classifier routing. Check the
provider's current API response fields (e.g., a stop-reason or refusal-category
object) for whether a given response was classifier-routed, and treat routed
sessions as a separate behavioral slice in production monitoring. Verify
whether your specific provider/model combination uses this architecture before
writing eval cases against it — it is not universal across providers or model
tiers, and the categories and routing rate are provider-specific and change
across releases.

## Operational discipline

- Run safety evals **on every release**, separately from capability gates — a
  capability win never justifies a safety regression.
- Keep the harmful prompt corpus access-controlled; it is sensitive material.
- Report safety results with severity breakdown and both error types; never collapse
  to one number.

### Evaluation-awareness and behavioral consistency

A model that detects eval scaffolding and behaves conservatively only under test
passes the gate for the wrong reason. Verify that the eval path and the production
path produce statistically indistinguishable output distributions:

- Run a sample of the safety eval cases through the live production endpoint (same
  system prompt, same tool set) and through the eval harness, then compare
  refusal-rate and response-distribution with a statistical test (e.g. chi-squared
  on pass/fail counts or a two-sample KS on score distributions).
- If the distributions diverge, audit for scaffolding signals the model could be
  using to identify the eval context: eval-specific system prompts, sentinel tokens,
  predictable request patterns, or eval-only tool stubs.
- Rotate scaffolding details periodically to prevent the model from learning stable
  eval fingerprints through training on logged eval traffic.

## Checklist

- [ ] Harmful "should-refuse" set AND benign-adjacent "should-comply" set, scored together
- [ ] Refusal recall and over-refusal rate both reported, with the operating point
- [ ] Refusal *quality* graded, not just the binary
- [ ] Jailbreak families tested separately (ASR per family), including adaptive attacks
- [ ] Indirect prompt injection tested via planted instructions in retrieved/tool content
- [ ] Harm graded by category and severity tier, not pass/fail
- [ ] Highest-severity categories anchored to human ground truth
- [ ] Every successful jailbreak added as a permanent regression case
- [ ] Strategy diversity tracked; private held-out attack set kept (contamination guard)
- [ ] Safety cases run k times, worst-case reported, robustness to perturbation checked
- [ ] Agentic: excessive-agency and exfiltration tested with sandboxed tools
- [ ] Safety gate runs every release, independent of capability gates
- [ ] (Classifier-equipped models) Classifier-boundary behavior tested and fallback-seam output contract verified
- [ ] Multimodal: visual jailbreaks, cross-modal inconsistency, and audio injection tested where applicable
- [ ] Eval-path and production-path output distributions compared; divergence investigated for scaffolding detection
