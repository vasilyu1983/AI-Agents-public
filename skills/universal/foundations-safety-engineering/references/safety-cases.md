# Safety cases for AI and software systems

A safety case is a structured argument, backed by evidence, that a system is acceptably safe for a stated use in a stated context. It links a top claim to sub-claims and evidence. It records its assumptions, and it records the objections it has answered. It does not certify the system. Deciding that the residual risk is acceptable stays with the named authority (see [assurance and boundaries](assurance-and-boundaries.md)).

## Structure

- **CAE (Claims–Arguments–Evidence).** A claim is supported by an argument, and the argument rests on evidence or on sub-claims. Goemans et al. (arXiv:2411.08088) use CAE to build a frontier-AI "cyber inability" template: risk models → proxy tasks → evaluation settings → results. They present it as a proof of concept.
- **GSN (Goal Structuring Notation).** A graphical notation. Its core elements are Goal, Strategy, Solution (the evidence), Context, Assumption and Justification. The GSN Community Standard is maintained by the Safety-Critical Systems Club (SCSC) Assurance Case Working Group; cite the current version from the SCSC site. Use GSN when reviewers need a diagram. CAE and GSN express the same argument shape.
- **Defeaters (Assurance 2.0).** Bloomfield and Rushby (arXiv:2004.10474) call for explicit identification of defeaters and counterevidence, rather than only confirming evidence. Give each defeater an ID and a status: open, eliminated with its evidence, or accepted as residual. A case with no recorded defeaters has not been challenged yet. That does not make it strong.

## Frontier-AI argument families

Clymer et al. (arXiv:2403.10462) discuss four categories of argument, in the paper's words:

1. **Total inability** to cause a catastrophe.
2. **Sufficiently strong control measures.**
3. **Trustworthiness despite capability** to cause harm.
4. **Deference to credible AI advisors.** The paper frames this one as prospective: "if AI systems become much more powerful". Do not present it as available today.

The paper also outlines how arguments from several categories can be combined.

Choose the family that the evidence can actually support. An inability claim rests on capability elicitation. If the elicitation is weak, the claim is weak. When capability is present, move to a control argument. Do not stretch an inability argument over it.

**One sketched control case.** Korbak et al. (arXiv:2501.17315) sketch a single control safety case. The subject is a hypothetical LLM agent deployed inside an AI company, and the hazard is data exfiltration. The case uses evidence from a red-team control evaluation, and it "hinges on" three claims:

1. The red team adequately elicits the model's capability to exfiltrate data.
2. The control measures remain at least as effective in deployment.
3. The developers conservatively extrapolate from the evaluation to deployment.

These are the claims of that sketched case. They are not a general requirement for every control argument. They are still useful as a starting defeater list for any case built on red-team evaluations.

## Building one

1. State the top claim with its scope: the system version, the deployment context, the losses covered and the period.
2. Break it down by hazard, reusing the STPA IDs: H → SC → evidence. For an agent, the [worked STPA](agent-stpa-payments.md) traceability table is the evidence layer.
3. Tag each evidence item with its claim-ladder level (analyzed, implemented, verified or observed) and the artifact version it covers.
4. Add defeaters. Useful prompts: evaluation conditions differ from deployment; a component was updated after testing; the monitor and the model share a blind spot; the human reviewer is overloaded; a tool path bypasses the guard.
5. Name the residual risk, its owner, and what triggers a review.

## Failure modes

- Evidence tied to a model, prompt or tool set that is no longer deployed.
- "No incidents so far" offered as evidence without the exposure and the detection capability behind it.
- Arguments written only to confirm, with no defeater search.
- A claim broader than its evidence: "safe" when the evidence supports "safe against H1–H3 in context C".

**When not to use.** A reversible, low-impact feature with no external authority asking for an argument needs only the traceability worksheet. Build a full case when a decision-maker must accept residual risk explicitly, or when a regulator or customer requires an argued case.
