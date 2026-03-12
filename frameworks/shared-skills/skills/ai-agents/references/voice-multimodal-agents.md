# Voice and Multimodal Agents

> Operational reference for building voice agents (phone IVR, smart assistants, real-time speech) and multimodal agents (vision+action, document understanding) — latency budgets, turn-taking, modality integration, and production deployment.

**Freshness anchor:** January 2026 — covers OpenAI Realtime API, Anthropic tool use with vision, Gemini 2.0 multimodal, Deepgram Nova-2, ElevenLabs Turbo v2.5.

---

## Modality Selection Decision Tree

```
What is the agent's primary input?
│
├── Voice (speech)
│   ├── Real-time conversation (phone/assistant)?
│   │   ├── YES → Real-Time Voice Pipeline
│   │   │   ├── Latency budget: TTFB <300ms
│   │   │   ├── Use: WebSocket streaming STT→LLM→TTS
│   │   │   └── Providers: OpenAI Realtime, Deepgram+LLM+ElevenLabs
│   │   └── NO → Async voice processing?
│   │       ├── Voicemail/recording analysis → Batch STT + LLM
│   │       └── Voice note summarization → Whisper + LLM
│   │
│   └── Smart assistant (Alexa/Google)?
│       ├── Use: Platform SDK + webhook backend
│       ├── Latency budget: <8s total response
│       └── Constraints: Platform-specific SSML, intent routing
│
├── Vision (images/video)
│   ├── Single image understanding?
│   │   ├── Use: GPT-4V / Claude Vision / Gemini Vision
│   │   ├── Cost: ~85 tokens per 512x512 tile (OpenAI)
│   │   └── Preprocessing: resize, crop ROI, compress
│   │
│   ├── Document understanding (PDF/forms)?
│   │   ├── Structured data → Vision + JSON mode
│   │   ├── Table extraction → Vision + schema prompt
│   │   └── Multi-page → Page-by-page with aggregation
│   │
│   └── Video analysis?
│       ├── Frame sampling → Extract key frames + vision LLM
│       ├── Real-time → Not cost-effective with current models
│       └── Use: Gemini 2.0 (native video) or frame extraction
│
└── Multi-modal (combined)
    ├── Vision + Action (UI agents) → Screenshot + tool use loop
    ├── Voice + Vision → Speech input + image context + speech output
    └── Document + Conversation → RAG with vision-extracted content
```

---

## Voice Agent Latency Budgets

| Component | Target Latency | Maximum | Notes |
|---|---|---|---|
| Speech-to-Text (STT) | <150ms | 300ms | Streaming STT preferred |
| Endpoint detection (VAD) | <200ms | 400ms | Silero VAD or WebRTC VAD |
| LLM inference (TTFT) | <200ms | 500ms | Use streaming, small models for simple turns |
| Text-to-Speech (TTS) | <150ms | 300ms | Streaming TTS with chunked delivery |
| **Total turn latency** | **<700ms** | **1500ms** | User perceives >1.5s as laggy |
| Network round-trip | <50ms | 100ms | Edge deployment preferred |

### Latency Optimization Checklist

- [ ] Use streaming STT (not batch transcription)
- [ ] Implement Voice Activity Detection (VAD) for accurate endpoint detection
- [ ] Stream LLM output token-by-token to TTS
- [ ] Use TTS with streaming support (ElevenLabs, Deepgram Aura, PlayHT)
- [ ] Deploy inference at edge or in same region as user
- [ ] Pre-warm TTS connections (keep WebSocket alive)
- [ ] Cache common responses (greetings, confirmations)
- [ ] Use smaller models for simple routing/classification turns
- [ ] Implement speculative generation for predictable responses

---

## Turn-Taking Patterns

### Pattern 1: VAD-Based Turn Detection

```
Use when: open-ended conversation, user speaks freely
Pipeline: Audio → VAD → silence threshold → process utterance

Configuration:
- Silence threshold: 500-800ms (adjust per use case)
- Min speech duration: 200ms (filter noise)
- Max speech duration: 30s (prevent runaway capture)
```

### Pattern 2: Barge-In Support

```
Use when: IVR systems, long TTS responses user may interrupt
Pipeline: Monitor user audio DURING TTS playback

Implementation:
- Detect user speech onset during TTS
- Immediately stop TTS playback
- Capture user utterance
- Process interruption as new input
- Anti-pattern: requiring user to wait for full TTS completion
```

### Pattern 3: Push-to-Talk

```
Use when: noisy environments, walkie-talkie style apps
Pipeline: Button press → capture → button release → process

Advantages:
- No VAD false positives
- Clear turn boundaries
- Works in high-noise environments
Disadvantages:
- Less natural interaction
- Requires UI element
```

### Pattern 4: Backchannel Signals

```
Use when: building natural conversational agents
Implementation:
- Detect pause mid-utterance (300-500ms)
- Generate short acknowledgment ("mm-hmm", "I see")
- Do NOT trigger full processing — just backchannel
- Resume listening for continued speech
```

---

## Real-Time Voice Pipeline Architecture

```
┌─────────┐    WebSocket    ┌──────────────┐
│  Client  │ ◄────────────► │  Voice Gateway│
│ (Phone/  │   audio chunks │              │
│  Browser)│                └──────┬───────┘
└─────────┘                       │
                                  ▼
                          ┌───────────────┐
                          │  STT Engine   │
                          │  (Deepgram/   │
                          │   Whisper)    │
                          └──────┬────────┘
                                 │ text
                                 ▼
                          ┌───────────────┐
                          │  Agent Core   │
                          │  (LLM + Tools)│
                          └──────┬────────┘
                                 │ text (streaming)
                                 ▼
                          ┌───────────────┐
                          │  TTS Engine   │
                          │  (ElevenLabs/ │
                          │   Deepgram)   │
                          └──────┬────────┘
                                 │ audio chunks
                                 ▼
                          Back to Client
```

### Pipeline Integration Code

```python
import asyncio

class VoicePipeline:
    def __init__(self, stt, llm, tts):
        self.stt = stt
        self.llm = llm
        self.tts = tts
        self.is_speaking = False

    async def process_turn(self, audio_stream):
        # Step 1: STT (streaming)
        transcript = ""
        async for partial in self.stt.transcribe_stream(audio_stream):
            transcript = partial.text

        if not transcript.strip():
            return  # silence, no action

        # Step 2: LLM (streaming) → TTS (streaming)
        self.is_speaking = True
        tts_stream = self.tts.create_stream()

        buffer = ""
        async for token in self.llm.generate_stream(transcript):
            buffer += token
            # Flush to TTS at sentence boundaries
            if buffer.rstrip().endswith((".", "!", "?", ":")):
                await tts_stream.send_text(buffer)
                buffer = ""

        if buffer:
            await tts_stream.send_text(buffer)

        await tts_stream.finish()
        self.is_speaking = False
```

---

## Vision Agent Patterns

### Image Token Cost Reference (January 2026)

| Provider | Model | Cost per Image | Token Calculation |
|---|---|---|---|
| OpenAI | GPT-4o | ~85 tokens per 512x512 tile | Tiles = ceil(width/512) * ceil(height/512) |
| OpenAI | GPT-4o-mini | Same tiling, lower $/token | More cost-effective for simple vision |
| Anthropic | Claude 3.5 Sonnet | ~1600 tokens per 1568x1568 | Scales with image size |
| Google | Gemini 2.0 Flash | 258 tokens per image | Flat rate, cost-effective |

### Image Preprocessing Checklist

- [ ] Resize to model's optimal resolution (avoid sending 4K images)
- [ ] Crop to region of interest when possible
- [ ] Compress JPEG to 85% quality (minimal quality loss, significant size reduction)
- [ ] Convert PNG screenshots to JPEG (unless transparency needed)
- [ ] For documents: increase contrast, deskew, remove margins
- [ ] For multi-image: limit to 5-10 images per request (cost control)
- [ ] Encode as base64 or use pre-signed URLs (provider-dependent)

### Vision Grounding Patterns

| Pattern | Use When | Implementation |
|---|---|---|
| Bounding box overlay | Need to identify specific regions | Draw numbered boxes, reference by number in prompt |
| Grid overlay | Need spatial precision | Overlay labeled grid, use grid coordinates |
| Set-of-marks | UI element identification | Number each interactive element |
| Cropped regions | Focus on specific area | Send cropped sub-image instead of full image |
| Multi-angle | 3D object understanding | Send 2-4 views of same object |

---

## Document Understanding Pipeline

### Decision Matrix

| Document Type | Best Approach | Fallback |
|---|---|---|
| Clean PDF with text layer | Text extraction (PyMuPDF) + LLM | Vision API on rendered pages |
| Scanned PDF / image-only | Vision API (page-by-page) | OCR (Tesseract) + LLM |
| Forms with checkboxes | Vision API with schema prompt | Specialized form OCR |
| Tables | Vision API + JSON mode output | Camelot/Tabula extraction + LLM |
| Handwritten notes | Vision API | Not reliable for production |
| Multi-page reports | Page-by-page vision + aggregation | Extract text + chunk + RAG |

### Multi-Page Processing

```python
async def process_document(pages: list[bytes], schema: dict) -> dict:
    results = []

    for i, page_image in enumerate(pages):
        result = await vision_llm.analyze(
            image=page_image,
            prompt=f"""Extract data from page {i+1} of {len(pages)}.
Output JSON matching this schema: {json.dumps(schema)}
If a field spans multiple pages, include partial data with
"continues_on_next_page": true""",
            response_format={"type": "json_object"}
        )
        results.append(result)

    # Aggregate cross-page data
    return merge_page_results(results, schema)
```

---

## Modality-Specific Guardrails

| Modality | Guardrail | Implementation |
|---|---|---|
| Voice | Profanity filter on STT output | Word list + regex before LLM |
| Voice | PII detection in transcripts | NER model on STT output |
| Voice | Silence timeout | Disconnect after 30s silence |
| Voice | Max turn duration | Hard cut at 60s recording |
| Vision | NSFW image detection | Pre-screen with safety classifier |
| Vision | PII in images (IDs, cards) | Blur detection + warning |
| Vision | Image size limits | Reject >20MB, resize >4096px |
| Document | Malicious file detection | Scan uploads before processing |
| Document | Page count limits | Cap at 50 pages per request |
| Multimodal | Cross-modal consistency | Verify vision output matches text context |

---

## Smart Assistant Integration (Alexa/Google)

### Platform Comparison

| Feature | Alexa Skills Kit | Google Actions | Apple Shortcuts |
|---|---|---|---|
| Max response time | 8 seconds | 5 seconds | N/A (local) |
| Audio streaming | Yes (AudioPlayer) | Yes (Media) | Limited |
| Visual cards | Yes (APL) | Yes (Canvas) | No |
| Account linking | OAuth 2.0 | OAuth 2.0 | N/A |
| Proactive events | Yes (limited) | Yes (limited) | No |
| SSML support | Full | Full | No |
| LLM integration | Webhook to your backend | Webhook to your backend | Shortcuts actions |

### Response Time Budget (8s Alexa limit)

| Phase | Budget | Strategy |
|---|---|---|
| Intent routing | <100ms | Local classification |
| Context retrieval | <500ms | Pre-cached user state |
| LLM generation | <2000ms | Small model or cached response |
| Response formatting | <100ms | Template-based SSML |
| Network overhead | ~300ms | Edge deployment |
| **Buffer** | **~5000ms** | Safety margin for retries |

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| Batch STT for real-time voice | >2s latency, unusable | Streaming STT with partial results |
| Fixed silence threshold for all users | Fast speakers cut off, slow speakers wait | Adaptive VAD or per-user tuning |
| Sending full-res images to vision API | Expensive, slow, often unnecessary | Resize and crop before sending |
| Processing entire PDF as one image | Context overflow, poor accuracy | Page-by-page with aggregation |
| No barge-in support | Users forced to wait for long responses | Monitor audio during TTS playback |
| Ignoring TTS voice quality for brand | Generic voice feels impersonal | Select/clone voice matching brand |
| Hard-coding SSML | Brittle, unmaintainable | Template SSML with variable substitution |
| No fallback for STT errors | Misheard words cause wrong actions | Confirm critical actions before executing |

---

## Cross-References

- `agent-debugging-patterns.md` — debugging voice/multimodal agent failures
- `guardrails-implementation.md` — guardrail layers for voice/vision input
- `../ai-llm/references/multimodal-patterns.md` — LLM-level multimodal capabilities
- `../ai-llm-inference/references/streaming-patterns.md` — streaming infrastructure for voice
- `../ai-prompt-engineering/references/multimodal-prompt-patterns.md` — prompting for vision/audio
