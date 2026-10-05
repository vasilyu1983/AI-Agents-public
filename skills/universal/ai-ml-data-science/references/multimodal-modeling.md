# Multimodal Modelling Mechanics

Use this reference for general multimodal model design and interview-grade reasoning. It covers representation, fusion, training, adaptation, and diffusion mechanics. Production controls belong in `ai-mlops`; evaluation and red teaming belong in `ai-evals`.

## Contents

- [Representations and objectives](#representations-and-objectives)
- [CLIP and SigLIP-style contrastive training](#clip-and-siglip-style-contrastive-training)
- [Fusion choices](#fusion-choices)
- [Task architectures](#task-architectures)
- [Speech recognition and synthesis](#speech-recognition-and-synthesis)
- [Diffusion generation and control](#diffusion-generation-and-control)
- [Fine-tuning and adaptation](#fine-tuning-and-adaptation)
- [Latency and cost](#latency-and-cost)
- [Design checklist](#design-checklist)

## Representations and objectives

A multimodal system must decide where modalities meet and what objective aligns them. Image, audio, video, document layout, and text encoders produce sequences at different rates and information densities. Alignment losses make representations comparable; generative or task losses teach conditional prediction. The objective should match the product behavior rather than assume one shared embedding solves every task.

## CLIP and SigLIP-style contrastive training

CLIP uses separate image and text encoders, normalized embeddings, and a learned temperature. Within a batch, matched image-text pairs are positives and other pairs act as negatives; symmetric cross-entropy trains image-to-text and text-to-image retrieval. This supports zero-shot classification by comparing image embeddings with prompt-derived class embeddings.

SigLIP replaces the batchwise softmax normalized across in-batch image-text pairs with independent sigmoid classification over each pair. The distinction matters operationally: softmax contrastive learning couples every pair through the batch denominator, while the pairwise sigmoid objective does not require that global normalization.

For both:

- Caption and image quality, duplicates, false negatives, sampling balance, and batch construction can dominate architectural gains.
- Zero-shot transfer depends on prompt formulation and domain shift; validate on the actual domain.
- Retrieval alignment does not imply grounding, compositional reasoning, counting, OCR reliability, or suitability for sensitive classification.
- Measure demographic and cultural slices because web-scale paired data carries representation and association biases.

## Fusion choices

| Pattern | Mechanism | Strength | Main cost or risk |
|---|---|---|---|
| Early fusion | concatenate/project modality tokens before shared processing | rich cross-modal interaction | quadratic token cost and sensitivity to alignment/noise |
| Late fusion | encode each modality independently, combine scores or pooled features | modular, cacheable, handles missing modalities | weak fine-grained interaction |
| Cross-attention / intermediate fusion | one modality attends to another at selected layers | balances interaction and modularity | more complex serving and ablation |

Choose from the dependency in the task. Fine spatial grounding, temporal causality, and document layout usually need token-level interaction. Retrieval and candidate ranking often benefit from dual encoders because each side can be indexed or cached. Design missing-modality behavior explicitly rather than substituting zero tensors without testing.

## Task architectures

### Visual question answering

VQA combines visual tokens with question tokens, then predicts an answer or generates text. A credible system needs grounding tests, OCR/counting/spatial-relation slices, answerability detection, and protection against language priors that let the model guess without using the image.

### Documents

Document AI must preserve text, two-dimensional layout, reading order, tables, handwriting, and page relationships. OCR-first pipelines are modular but propagate recognition errors; vision-language approaches may reason jointly but can hallucinate text. Keep coordinates and source spans so answers can be verified against the page.

### Video

Video adds temporal sampling, motion, event ordering, audio synchronization, and a large token budget. Sparse frame sampling may miss short events; dense sampling raises latency and memory. Evaluate temporal order, event localization, long-context retrieval, and performance across motion and shot-change regimes—not only static-frame recognition.

## Speech recognition and synthesis

Speech systems map between a variable-rate acoustic signal and linguistic or acoustic-token sequences. Keep the modelling question separate from microphone capture, voice activity detection, diarization, normalization, transport, playback, and policy controls; those surrounding stages often dominate production failure.

### Automatic speech recognition (ASR)

A Whisper-style system converts audio to a log-Mel spectrogram, encodes the acoustic frames with a Transformer encoder, then autoregressively decodes text tokens while conditioning on task and language tokens. The encoder-decoder formulation can support multilingual transcription, translation, timestamps, and contextual decoding, but autoregressive decoding adds sequential latency and can hallucinate plausible text when audio is absent, noisy, clipped, or out of domain.

Contrast the main alignment families:

- **CTC:** predicts frame-level labels plus a blank symbol and sums over monotonic alignments. It enables parallel token scoring and simple decoding, but its conditional-independence assumption limits direct modelling of output dependencies; an external or fused language model is often useful.
- **RNN-T / transducer:** combines an acoustic encoder, a prediction network over prior non-blank outputs, and a joint network. It learns monotonic alignment while modelling label history and supports low-latency streaming, at the cost of more complex training and beam search.
- **Attention encoder-decoder:** attends over encoded audio and models rich output dependencies. It is natural for sequence-to-sequence multitask systems such as Whisper, but unconstrained attention and autoregressive decoding need explicit chunking, timestamp, and no-speech controls for streaming or long recordings.

Interview trade-offs should include word/character error patterns rather than one aggregate score: accents and dialects, code-switching, rare names, domain vocabulary, overlapping speakers, background noise, far-field audio, punctuation, timestamps, and no-speech hallucination. Streaming adds an accuracy/latency trade-off through chunk size, right context, endpointing, partial-hypothesis revision, and decoder beam width.

### Text-to-speech (TTS)

A modern TTS pipeline usually has two learned stages:

1. A text or phoneme encoder plus an acoustic/token model predicts a mel spectrogram, neural audio codec tokens, or another intermediate representation. Autoregressive models such as Tacotron-style systems model duration implicitly with attention; non-autoregressive duration-informed models generate in parallel; diffusion or flow-based acoustic models iteratively refine a sample and trade steps for latency and quality.
2. A neural vocoder converts the acoustic representation to waveform samples. Autoregressive waveform models can be high quality but sequential; parallel convolutional, adversarial, flow, or diffusion vocoders reduce latency with different artifact, stability, and compute trade-offs. Codec-language-model systems may instead predict discrete audio tokens decoded by a codec.

Evaluate intelligibility, pronunciation, prosody, speaker similarity where authorized, naturalness, long-form stability, and artifacts across language, voice, device, and text slices. Production design must cover time-to-first-audio, real-time factor, chunk boundaries, incremental text, pronunciation dictionaries, caching, voice consent, cloning abuse, watermark/provenance limits, and fallback when synthesis misses its latency budget.

### Ownership boundaries

- Stay in `ai-ml-data-science` for ASR/TTS objectives, alignment families, acoustic/token models, vocoders, diffusion mechanics, and adaptation choices.
- Route deployment, media validation, streaming capacity, voice consent enforcement, provenance, monitoring, and incidents to `ai-mlops` and its responsible/multimodal operations reference.
- Route WER/CER and slice design, human listening tests, hallucination, speaker/privacy, spoofing, red-team, latency, and cost gates to `ai-evals` and its responsible/multimodal evaluation reference.
- Route conversational turn-taking, telephony, interruption, and end-to-end bot experience to `ai-voice-bots`.

## Diffusion generation and control

Diffusion models learn to reverse a gradual noising process. Sampling starts from noise and repeatedly applies a denoiser or score estimate. Latent diffusion performs this process in a compressed latent space to reduce compute.

- Classifier-free guidance combines conditional and unconditional predictions. Increasing guidance can improve prompt adherence or perceived fidelity while reducing diversity or causing artifacts; tune the trade-off on the deployment distribution.
- Control signals may include text, masks, edges, depth, pose, layout, reference images, or other modalities. Test whether the model follows the control rather than merely producing a plausible sample.
- Diversity is not captured by one attractive output. Evaluate multiple seeds, mode coverage, near-duplicates, subgroup representation, and prompt sensitivity.
- Sampling acceleration includes fewer-step solvers, progressive distillation, consistency-style training, latent-space operation, caching, and smaller backbones. Each changes the quality/latency frontier and must be re-evaluated for control adherence and safety.

## Fine-tuning and adaptation

- Linear probes or adapters test whether the pretrained representation already contains the signal.
- Parameter-efficient adaptation reduces trainable state but does not eliminate overfitting, forgetting, bias amplification, or deployment complexity.
- Contrastive fine-tuning needs carefully constructed positives and hard negatives; false negatives can damage semantic neighborhoods.
- Instruction tuning for vision-language models needs grounded examples, explicit unanswerable cases, and resistance to text-only shortcuts.
- Diffusion adaptation should check identity leakage, memorization, style overfitting, composition, diversity, and behavior outside the narrow training prompt set.
- Keep a frozen baseline and held-out domain, safety, and memorization sets. Training loss is not a release criterion.

## Latency and cost

Break latency into media loading/decoding, preprocessing, modality encoders, token projection/fusion, autoregressive decoding or diffusion steps, post-processing, and queueing. Track input resolution, frames, audio duration, visual-token count, output length, denoising steps, batch size, cache hit rate, and hardware utilization.

Common levers include adaptive resolution/frame sampling, region selection, cached embeddings, dual-encoder retrieval before cross-encoder reranking, token pruning, batching, quantization, distillation, speculative decoding where supported, and early exit. Report quality and safety by slice after every optimization; media compression and token pruning can preferentially erase small text, brief events, or accessibility cues.

## Design checklist

- State the modalities, task, alignment objective, fusion point, and missing-modality behavior.
- Identify where spatial, temporal, OCR, audio, or layout grounding is required.
- Define domain, subgroup, adversarial, and unanswerable slices before tuning.
- Keep provenance from output claims to media regions, timestamps, or document spans where the use case needs verification.
- Measure quality, diversity, grounding, safety, latency, memory, throughput, and cost together.

## Primary sources

- [Learning Transferable Visual Models From Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020)
- [Sigmoid Loss for Language Image Pre-Training (SigLIP)](https://arxiv.org/abs/2303.15343)
- [ViLBERT: Pretraining Task-Agnostic Visiolinguistic Representations](https://arxiv.org/abs/1908.02265)
- [LayoutLM: Pre-training of Text and Layout for Document Image Understanding](https://arxiv.org/abs/1912.13318)
- [An Image is Worth 16x16 Words](https://arxiv.org/abs/2010.11929)
- [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752)
- [Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598)
- [On Distillation of Guided Diffusion Models](https://arxiv.org/abs/2210.03142)
- [Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)](https://arxiv.org/abs/2212.04356)
- [Connectionist Temporal Classification](https://www.cs.toronto.edu/~graves/icml_2006.pdf)
- [Sequence Transduction with Recurrent Neural Networks](https://arxiv.org/abs/1211.3711)
- [Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram Predictions (Tacotron 2)](https://arxiv.org/abs/1712.05884)
- [WaveNet: A Generative Model for Raw Audio](https://arxiv.org/abs/1609.03499)
- [Grad-TTS: A Diffusion Probabilistic Model for Text-to-Speech](https://arxiv.org/abs/2105.06337)
