# Assurance and boundaries

An assurance argument connects a bounded claim to assumptions, supporting evidence, and unresolved objections. Record separately:

- **Analyzed:** a plausible scenario and constraint were identified.
- **Implemented:** a named artifact implements the constraint.
- **Verified:** a test or model check exercises the stated property under declared conditions.
- **Observed:** field evidence supports the claim for a defined exposure window.

These levels are not substitutes. A simulation is not deployment evidence, a model check applies to its model, and absence of observed accidents does not establish negligible risk without exposure and detection information.

For each constraint state mechanism, responsible owner, verification method, evidence version, result, and residual limitation. Review changes in operating modes, feedback paths, dependencies, or authority allocation. Use failure analyses from reliability where appropriate, but do not infer interaction safety from component reliability alone.

Do not fabricate likelihood rankings when only scenarios exist. Qualitative priorities need explicit rationale such as severity, exposure, detectability, reversibility, and uncertainty. Acceptance of residual risk belongs to the system's named authority; an analysis report cannot certify safety or regulatory compliance. Before choosing controls, record severity and reversibility, the accepting authority, and the residual hazards; the usual framing is ALARP ("as low as reasonably practicable", the principle behind IEC 61508 and UK practice). Defence in depth does not multiply: Swiss-cheese layers share failure causes (same model, same prompt channel), so count a layer as independent only with evidence that its failures are uncorrelated; the Swiss-cheese model is a communication aid, not a probability model (Larouzee & Le Coze 2020, Safety Science 126; abstract-level source). When an LLM drafts the STPA, a human freezes the losses and hazards first.

The workflow should produce a useful bounded artifact even when evidence is incomplete. Identify missing inputs or evidence precisely; do not require ritual confirmation or block unrelated authorized work.

For argument structure (CAE/GSN, defeaters, frontier-AI argument families), see [safety cases](safety-cases.md).
