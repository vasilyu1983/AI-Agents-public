# Responsible AI: Modelling Mechanics

Use this reference to reason about responsible-AI failure mechanisms during data preparation, modelling, and model handoff. It explains what can go wrong and what a credible technical response looks like. Production control ownership belongs in `ai-mlops`; measurement and red-team design belongs in `ai-evals`.

## Contents

- [Start with the decision and harm model](#start-with-the-decision-and-harm-model)
- [Fairness and intersectionality](#fairness-and-intersectionality)
- [Differential privacy and the privacy-utility trade-off](#differential-privacy-and-the-privacy-utility-trade-off)
- [Interpretability and explanation](#interpretability-and-explanation)
- [Poisoning and federated learning](#poisoning-and-federated-learning)
- [Re-identification and memorization](#re-identification-and-memorization)
- [Watermarking and provenance](#watermarking-and-provenance)
- [Human oversight, automation bias, and appeals](#human-oversight-automation-bias-and-appeals)
- [Copyright and training-data governance](#copyright-and-training-data-governance)
- [Environmental trade-offs](#environmental-trade-offs)
- [Handoff checklist](#handoff-checklist)

## Start with the decision and harm model

Responsible AI is not a single metric. Define the system boundary, affected people, decision, recourse path, and plausible harms before selecting a fairness metric or explanation tool. Separate model error from allocation, interaction, representational, privacy, security, and environmental harms. Record who benefits, who bears error, and which harms cannot be repaired after deployment.

NIST AI RMF treats fairness, privacy, explainability, human oversight, appeal, and environmental impact as lifecycle concerns. Use that structure as a control map, not as evidence that a particular model is safe.

## Fairness and intersectionality

- Choose the fairness definition from the decision context. Demographic parity, equalized odds, equal opportunity, calibration, and individual fairness encode different—and sometimes incompatible—normative choices.
- Report outcome and error metrics per relevant group, then inspect intersections such as age by gender by disability. Good performance on each marginal group does not imply good performance at their intersections.
- Use confidence intervals and minimum-support rules. Small slices should be flagged as uncertain, not silently dropped or presented as stable.
- Investigate the pipeline: label validity, sampling, missingness, measurement error, proxy features, threshold choice, and feedback loops. Removing protected attributes does not remove correlated proxies.
- Compare mitigation points: pre-processing (sampling/reweighting), in-processing (constraints or robust objectives), and post-processing (group-aware thresholds where lawful and appropriate). Measure utility and harm changes for every affected slice.

Do not announce a model as “fair” from one parity score. State which definition was tested, for whom, on what data, and which trade-offs remain.

## Differential privacy and the privacy-utility trade-off

Differential privacy bounds how much an output distribution can change when one person's record is added or removed. The privacy budget is expressed through epsilon and delta under an explicit adjacency definition; smaller epsilon is stronger protection, but the operational meaning depends on the mechanism, sampling, composition, and threat model.

- Clip per-example contributions before adding calibrated noise; otherwise one record can dominate sensitivity.
- Account for privacy loss across repeated queries or training steps. Never report a per-step budget as the end-to-end guarantee.
- Keep the accountant, adjacency definition, clipping norm, sampling assumptions, and final budget with the model artifact.
- Evaluate privacy and utility together: overall quality, worst-slice quality, calibration, rare-class recall, and membership/inversion attacks. Noise can harm minority or rare groups disproportionately.
- Distinguish central DP, local DP, and federated learning. Federated learning keeps raw data distributed; it is not, by itself, a differential-privacy guarantee.

## Interpretability and explanation

Interpretability is the degree to which a person can understand the model's mechanism; explainability often refers to post-hoc accounts of a prediction or model behavior. A sparse linear model may be intrinsically interpretable. SHAP, LIME, saliency maps, counterfactuals, and generated rationales are explanations with assumptions and failure modes.

- Match the explanation to its audience and decision: developer debugging, operator action, subject notification, audit, or scientific understanding.
- Test fidelity, stability under small perturbations, sensitivity to irrelevant features, and usefulness to the intended user.
- Do not treat attention weights or fluent chain-of-thought as faithful causal explanations.
- Use counterfactual explanations only with feasibility and actionability constraints; do not recommend immutable or harmful changes.
- Prefer a simpler, auditable model where the decision risk demands faithful reasoning and the utility trade-off is acceptable.

## Poisoning and federated learning

Data poisoning changes training data to degrade availability, create targeted errors, or install a backdoor. In federated learning, malicious or compromised clients can submit model updates rather than raw examples.

- Threat-model label flips, clean-label attacks, backdoors, sybil clients, model-replacement attacks, and poisoned foundation-model or dataset dependencies.
- Preserve provenance and immutable dataset versions; validate new contributors and quarantine anomalous batches.
- In federated settings, bound client updates, use robust aggregation where its assumptions fit, monitor update similarity and influence, and test targeted triggers after aggregation.
- Secure aggregation protects individual updates from the server but can reduce visibility into malicious updates. It does not solve poisoning; combine privacy and robustness controls deliberately.
- Test adaptive attackers. A static anomaly threshold is evidence against only the attacks it was designed to catch.

## Re-identification and memorization

Removing names is not anonymization. Quasi-identifiers can link a released or logged dataset back to people, and high-dimensional or rare records are especially vulnerable. Models can also memorize and reproduce training examples.

- Minimize collection and retention; separate direct identifiers; generalize, suppress, or synthesize only after a documented threat model.
- Test linkage against realistic auxiliary data, membership inference, model inversion, and extraction of rare or canary strings.
- Deduplicate training corpora and restrict verbatim high-risk content, but do not claim deduplication eliminates memorization.
- Treat embeddings, gradients, checkpoints, prompts, and logs as potentially sensitive artifacts.
- Avoid claiming “anonymous” from k-anonymity or a single attack result; state the attacker knowledge and residual risk.

## Watermarking and provenance

Watermarks can be embedded in model outputs or model parameters; provenance systems can cryptographically bind content metadata and edit history. Neither is a universal detector of AI-generated content.

- Define the purpose: disclosure, ownership evidence, leak tracing, or platform policy enforcement.
- Measure detection power, false positives, quality impact, robustness to paraphrase/crop/compression/editing, and accessibility across languages or modalities.
- Keep key management and verifier independence in scope.
- Combine watermarking with signed provenance, access controls, logging, and policy. Treat missing watermark evidence as inconclusive because transformations may remove it.

## Human oversight, automation bias, and appeals

A nominal human in the loop is not an effective control. Automation bias makes reviewers over-trust machine suggestions, especially under time pressure or when uncertainty is hidden.

- Give reviewers enough time, authority, independent evidence, and a clear override path.
- Show calibrated uncertainty and known limitations without anchoring the reviewer on a confident default.
- Measure override rates, error detection, review latency, disagreement outcomes, and whether reviewers merely rubber-stamp outputs.
- Design escalation and fallback for low-confidence, novel, conflicting, or high-impact cases.
- Give affected people notice, understandable reasons, correction channels, and meaningful human reconsideration. Feed appeal outcomes back into slice analysis and error review.

## Copyright and training-data governance

Copyright, privacy, license, and contractual permissions are separate questions. Public availability is not permission for every training or output use.

- Track source, license, consent or lawful basis where relevant, collection method, intended use, retention, and removal requests.
- Deduplicate and detect near-verbatim memorization; evaluate long-tail prompts that elicit distinctive passages or images.
- Separate factual similarity from substantial reproduction and route legal conclusions to qualified counsel.
- Maintain provenance through fine-tuning and synthetic-data generation. Synthetic data can reproduce source material or encode the generating model's bias.

## Environmental trade-offs

Measure the full lifecycle: data processing, training experiments, hyperparameter search, inference volume, storage, networking, hardware manufacture, and retirement. FLOPs or parameter count alone are not environmental-impact measures.

- Compare candidates at equal quality and workload using energy, hardware time, latency, and cost alongside task metrics.
- Report workload, region, hardware, utilization, measurement method, and uncertainty when estimating energy or emissions.
- Reduce impact through smaller baselines, transfer learning, efficient architectures, bounded search, batching, caching, quantization/distillation where quality permits, and workload-aware scheduling.
- Check rebound effects: cheaper inference can increase total use enough to erase per-request savings.

## Handoff checklist

- Decision, affected groups, harm model, and prohibited uses are documented.
- Fairness definitions, intersectional slices, uncertainty, and residual disparities are reported.
- Privacy mechanism, attack model, accountant, and utility impact are reproducible.
- Explanations are tested for fidelity, stability, and audience usefulness.
- Poisoning, re-identification, memorization, and provenance threats have explicit tests.
- Human override and appeal workflows have owners and measurable outcomes.
- Data rights, copyright questions, and environmental measurements are recorded with assumptions.

## Primary sources

- [NIST AI Risk Management Framework 1.0](https://doi.org/10.6028/NIST.AI.100-1)
- [Fairness and Abstraction in Sociotechnical Systems](https://doi.org/10.1145/3287560.3287598)
- [The Algorithmic Foundations of Differential Privacy](https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf)
- [Why Should I Trust You? (LIME)](https://arxiv.org/abs/1602.04938)
- [A Unified Approach to Interpreting Model Predictions (SHAP)](https://arxiv.org/abs/1705.07874)
- [Deep Leakage from Gradients](https://arxiv.org/abs/1906.08935)
- [Certified Robustness to Adversarial Examples with Differential Privacy](https://arxiv.org/abs/1802.03471)
- [Extracting Training Data from Large Language Models](https://arxiv.org/abs/2012.07805)
- [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993)
