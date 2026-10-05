# Responsible and Multimodal AI Evaluation

Use this reference to build evidence for responsible-AI and multimodal claims. It extends the general calibration, statistics, flake, and red-team rules in this skill. Modelling mechanics belong in `ai-ml-data-science`; production control ownership belongs in `ai-mlops`.

## Contents

- [Evaluation contract](#evaluation-contract)
- [Fairness and intersectional evaluation](#fairness-and-intersectional-evaluation)
- [Privacy, memorization, and poisoning](#privacy-memorization-and-poisoning)
- [Explainability and human oversight](#explainability-and-human-oversight)
- [Watermarking, provenance, and copyright](#watermarking-provenance-and-copyright)
- [Environmental evaluation](#environmental-evaluation)
- [Multimodal quality and grounding](#multimodal-quality-and-grounding)
- [Speech evaluation](#speech-evaluation)
- [Diffusion evaluation](#diffusion-evaluation)
- [Multimodal red teaming](#multimodal-red-teaming)
- [Latency and cost evaluation](#latency-and-cost-evaluation)
- [Release matrix](#release-matrix)

## Evaluation contract

For every claim, define the population, unit, decision threshold, reference answer or observable outcome, slice dimensions, uncertainty method, unacceptable harms, and escalation action. Keep safety, fairness, privacy, grounding, quality, latency, and cost as a vector of gates; do not average them into one score that permits a critical failure to hide behind unrelated gains.

Use held-out cases, report confidence intervals, correct for repeated comparisons, expose missing slices, and calibrate automated graders against independent human labels. Measure realistic end-to-end pipelines, including OCR, retrieval, fusion, filters, and human review.

## Fairness and intersectional evaluation

- Start from the harm and decision. Select outcome, error-rate, calibration, ranking, allocation, abstention, and service-quality metrics that correspond to it.
- Evaluate protected and operationally relevant groups plus intersections. Pre-register slices when possible; distinguish confirmatory gates from exploratory discovery.
- Report numerator, denominator, uncertainty, and missingness. Use minimum-support rules but record insufficient-data slices as unresolved rather than passing them.
- Check label and measurement validity by group. Equal model metrics against biased labels can reproduce the label process.
- Compare thresholds and mitigations using utility and harm curves for every affected group; state when fairness criteria conflict.
- Test temporal and deployment shifts, because a parity result on one snapshot is not durable evidence.

## Privacy, memorization, and poisoning

### Privacy

- Evaluate membership inference, model inversion, attribute inference, extraction, and record linkage against an attacker with stated access and auxiliary knowledge.
- For differential privacy, independently verify accountant inputs and composition; compare quality, calibration, and worst-slice utility across privacy budgets.
- Include rare and high-influence records because aggregate attacks can miss the cases most likely to be memorized.

### Memorization and copyright-sensitive reproduction

- Seed synthetic canaries and maintain held-out distinctive sequences or images. Never seed real secrets.
- Probe exact and near-verbatim reproduction across direct, indirect, multilingual, prefix, completion, and transformation prompts.
- Measure match length/similarity and false positives against public/common material; route legal interpretation separately.

### Poisoning and federated learning

- Test untargeted degradation, targeted label flips, clean-label attacks, backdoor triggers, sybil clients, malicious updates, and adaptive variants.
- Report clean quality and attack success by target/slice. A defense that lowers attack success by destroying clean utility has not necessarily improved the system.
- Evaluate secure aggregation and robust aggregation separately: privacy of client updates is not robustness to malicious updates.
- Keep trigger and attacker design held out from defense tuning to reduce benchmark overfitting.

## Explainability and human oversight

Evaluate explanations on:

- fidelity to the model or decision process;
- stability under meaning-preserving perturbations;
- sensitivity to causal and irrelevant features;
- actionability and feasibility of counterfactuals;
- comprehension, calibrated trust, decision quality, and time for the intended audience.

Plausible prose is not fidelity. Compare post-hoc explanations with known synthetic mechanisms, feature ablations, counterfactual interventions, or model-internal ground truth where available.

Evaluate human oversight as a joint system. Randomize whether reviewers see model advice first, include seeded model errors, measure correction and override behavior, and simulate queue pressure. Track false deference (automation bias), false rejection, review time, escalation, and outcomes after appeal. An appeal process passes only if people can access it, submit corrections, receive meaningful reconsideration, and alter an erroneous outcome within the defined service level.

## Watermarking, provenance, and copyright

- Measure watermark detection true/false-positive rates at the operating threshold, stratified by language, modality, content length, and generator family.
- Attack with paraphrase, translation, cropping, recompression, resizing, filtering, frame extraction, re-recording, inpainting, regeneration, and watermark-collision attempts.
- Evaluate payload integrity, attribution accuracy, verifier independence, key compromise/revocation, and signed provenance across edit chains.
- Include non-watermarked human content and outputs from unseen systems. A detector benchmark containing only known generators cannot support universal attribution.
- Test whether provenance displays improve user understanding without creating misplaced certainty.

## Environmental evaluation

Define the workload and boundary before comparing systems. Measure or estimate training, repeated experimentation, inference, media preprocessing, storage, and networking. Record hardware, utilization, region, duration, requests or samples, quality target, and uncertainty.

Report energy, hardware-hours, latency, throughput, and cost at equal task quality. For generative systems, include number of samples or denoising passes needed to reach the accepted output. Stress-test total workload so per-request efficiency does not hide rebound growth.

## Multimodal quality and grounding

Build a matrix across modality, domain, language, device/codec, quality degradation, subgroup, and task. Include clean, corrupted, missing, contradictory, and irrelevant modalities.

- **Image-text retrieval:** recall/ranking metrics, hard negatives, duplicates, compositional swaps, domain shift, and subgroup retrieval exposure.
- **VQA:** exact/semantic answer quality plus grounding, unanswerable detection, counting, OCR, spatial relation, and language-prior counterfactuals where the image is changed but the question stays fixed.
- **Documents:** character/word recognition, field/table extraction, reading order, page linkage, citation/span accuracy, handwriting and scan-quality slices, and hallucinated-text rate.
- **Video/audio:** event classification, temporal order and localization, frame/segment grounding, long-context retrieval, speaker/background-noise slices, and audio-video contradiction.
- **Fusion:** compare full system with modality ablations and shuffled pairings. If performance barely changes when the relevant modality is removed or mismatched, the model may be exploiting shortcuts.

Human evaluation must define rubrics, annotator qualifications, blinding, randomized order, and agreement. Calibrate any multimodal judge against humans and test whether it misses errors in modalities it cannot inspect at native fidelity.

## Speech evaluation

- **ASR correctness:** report WER/CER with insertion, deletion, and substitution errors; add semantic/entity accuracy for names, numbers, commands, and domain terms. Slice by language/dialect, code-switching, speaker, device, channel, noise, distance, overlap, duration, speaking rate, and no-speech audio.
- **Streaming ASR:** measure time to first partial, endpoint/finalization delay, partial-hypothesis churn, real-time factor, and accuracy versus right-context/chunk/beam settings. Include interruptions, silence, packet loss, and long sessions.
- **ASR safety:** test hallucination on silence/noise/music, prompt/context steering, adversarial audio, privacy leakage, diarization mistakes, and confidence/abstention calibration. A low aggregate WER does not establish safe behavior on consequential entities.
- **TTS correctness and quality:** combine intelligibility and pronunciation tests with blinded listening for naturalness, prosody, speaker similarity where authorized, long-form stability, and artifacts. Keep human ratings separate from automated proxy metrics and report agreement.
- **TTS streaming and safety:** measure time to first audio, real-time factor, chunk-boundary artifacts, truncation/repetition, incremental-text revisions, and cost per accepted audio minute. Red-team unauthorized voice cloning, identity leakage, spoofing, harmful content, watermark/provenance removal, and disparate quality across languages/voices.
- Compare acoustic/token models, vocoders, codec decoders, and diffusion-step reductions at matched text, voice, hardware, and quality/safety gates; speed alone is not a promotion result.

## Diffusion evaluation

Evaluate multiple seeds and separate:

- prompt/control adherence and spatial/compositional correctness;
- perceptual quality and artifact rate;
- diversity, mode coverage, and near-duplicate rate;
- identity/content memorization and training-data similarity;
- subgroup representation and stereotyped associations;
- unsafe or disallowed content and overblocking;
- robustness to prompt paraphrase, misspelling, multilingual input, reference images, masks, pose/depth/edge controls, and iterative editing.

FID-like distribution metrics and embedding similarity can support comparisons but do not establish prompt faithfulness, diversity, safety, or human preference alone. When evaluating fewer-step solvers, distillation, or consistency-style acceleration, compare at matched prompt set, seeds, resolution, guidance/control settings, and hardware; gate any quality or safety regression rather than reporting speed alone.

## Multimodal red teaming

Threat-model attacks that cross representation boundaries:

- instructions hidden in images, documents, QR codes, audio, subtitles, metadata, or video frames;
- OCR/ASR perturbations, homoglyphs, adversarial patches, overlays, low contrast, compression, and steganographic cues;
- benign text paired with harmful media and vice versa;
- conflicting modalities designed to manipulate routing or safety filters;
- retrieval poisoning through captions, alt text, document layout, or media embeddings;
- privacy extraction, face/voice identity abuse, non-consensual imagery, and transformed copyrighted content.

Measure attack success by family and transformation, severity, over-refusal on matched benign cases, cross-turn persistence, and transfer to unseen attacks. Keep adaptive red-team cases separate from the development set and add confirmed incidents to regression replay.

## Latency and cost evaluation

Measure p50/p95/p99 end-to-end and stage latency for fetch/decode, preprocessing, encoders, fusion, generation/denoising, safety filters, and post-processing. Include cold starts, concurrency, backpressure, variable media sizes, long video/audio, multi-page documents, cache misses, and failures.

Report throughput, memory, accelerator utilization, tokens/frames/pages/seconds processed, denoising steps, retries, human-review load, and cost per accepted result. Compare optimizations on a Pareto frontier with quality, grounding, safety, and subgroup performance.

## Release matrix

| Claim | Required evidence | Failure action |
|---|---|---|
| fair enough for intended decision | predeclared groups/intersections, uncertainty, label audit, mitigation trade-offs | block or constrain use |
| privacy protected | threat model, attack results, DP accounting where claimed, utility slices | block and investigate |
| explanation useful | fidelity/stability plus audience study | remove claim or change method |
| human oversight effective | seeded-error study, override/appeal outcomes, load test | increase authority/capacity or fail closed |
| watermark/provenance reliable | thresholded detection and transformation attacks | narrow claim and add controls |
| multimodal system grounded | task, modality-ablation, corruption, and citation evidence | abstain/fallback or block |
| diffusion acceleration safe | matched quality/diversity/control/safety comparison | keep known-good sampler |
| latency/cost acceptable | tail-load test plus quality/safety Pareto | optimize, quota, or constrain workload |

## Primary sources

- [NIST AI Risk Management Framework 1.0](https://doi.org/10.6028/NIST.AI.100-1)
- [NIST AI 600-1 Generative AI Profile](https://doi.org/10.6028/NIST.AI.600-1)
- [Fairness and Abstraction in Sociotechnical Systems](https://doi.org/10.1145/3287560.3287598)
- [The Algorithmic Foundations of Differential Privacy](https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf)
- [Extracting Training Data from Large Language Models](https://arxiv.org/abs/2012.07805)
- [Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020)
- [Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598)
- [On Distillation of Guided Diffusion Models](https://arxiv.org/abs/2210.03142)
