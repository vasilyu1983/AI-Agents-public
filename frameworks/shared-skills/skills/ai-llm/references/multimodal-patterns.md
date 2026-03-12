# Multimodal LLM Patterns

> Operational reference for working with vision, audio, and document understanding capabilities of LLMs — cost optimization, prompt patterns, preprocessing pipelines, and multimodal RAG architectures.

**Freshness anchor:** January 2026 — covers GPT-4o vision, Claude 3.5 Sonnet vision, Gemini 2.0 Flash/Pro multimodal, Whisper v3, and multimodal embedding models (Nomic, Voyage).

---

## Modality Selection Quick Reference

| Task | Best Modality | Recommended Model | Cost Tier |
|---|---|---|---|
| Image description | Vision | GPT-4o, Claude 3.5 Sonnet | $$ |
| OCR from clean text | Vision or text extraction | Gemini 2.0 Flash (cheapest) | $ |
| Table extraction from image | Vision + JSON mode | GPT-4o structured outputs | $$ |
| Document summarization (PDF) | Text extraction + LLM | PyMuPDF → any LLM | $ |
| Scanned document understanding | Vision | Claude 3.5 Sonnet, GPT-4o | $$ |
| Audio transcription | Speech-to-text | Whisper v3 large, Deepgram Nova-2 | $ |
| Speaker diarization | Specialized | Pyannote + Whisper | $ |
| Video understanding | Frame extraction + vision | Gemini 2.0 (native video) | $$$ |
| Multi-image comparison | Vision (multi-image) | GPT-4o, Gemini 2.0 | $$ |
| Diagram/chart analysis | Vision | Claude 3.5 Sonnet (best accuracy) | $$ |

---

## Vision: Image Token Cost Analysis

### Token Calculation by Provider (January 2026)

| Provider | Model | Pricing Model | Formula |
|---|---|---|---|
| OpenAI | GPT-4o | Tiled: 85 tokens/tile + 170 base | tiles = ceil(w/512) * ceil(h/512) |
| OpenAI | GPT-4o-mini | Same tiling, lower $/token | Same formula, ~60% cheaper |
| Anthropic | Claude 3.5 Sonnet | Proportional to image size | ~1600 tokens for 1568x1568 |
| Anthropic | Claude 3 Haiku | Same scaling, lower cost | Same formula, ~80% cheaper |
| Google | Gemini 2.0 Flash | Fixed: 258 tokens/image | Flat regardless of size |
| Google | Gemini 2.0 Pro | Fixed: 258 tokens/image | Flat regardless of size |

### Cost Optimization Decision Matrix

| Image Type | Optimization | Savings |
|---|---|---|
| Screenshots (UI) | Resize to 1024px wide, JPEG 85% | 40-60% token reduction |
| Photos | Resize to 768px max dimension | 50-70% token reduction |
| Documents | Crop margins, increase contrast | 20-30% token reduction |
| Diagrams | No resize needed (usually small) | Minimal |
| Multi-image batches | Use Gemini Flash (flat rate) | 60-80% vs OpenAI |
| Simple classification | Use `detail: "low"` (OpenAI) | 85 tokens flat |

### Image Preprocessing Pipeline

```python
from PIL import Image
import io
import base64

class ImagePreprocessor:
    MAX_DIMENSION = 1024  # optimal for most vision tasks
    JPEG_QUALITY = 85

    def preprocess(self, image_bytes: bytes, task: str = "general") -> str:
        """Preprocess image for vision LLM, return base64."""
        img = Image.open(io.BytesIO(image_bytes))

        # Convert RGBA to RGB (drop alpha channel)
        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background

        # Resize based on task
        max_dim = self._get_max_dimension(task)
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.LANCZOS)

        # Document-specific: increase contrast
        if task == "document":
            from PIL import ImageEnhance
            img = ImageEnhance.Contrast(img).enhance(1.3)
            img = ImageEnhance.Sharpness(img).enhance(1.2)

        # Encode as JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=self.JPEG_QUALITY)
        return base64.b64encode(buffer.getvalue()).decode()

    def _get_max_dimension(self, task: str) -> int:
        return {
            "classification": 512,
            "general": 1024,
            "document": 1568,
            "detail": 2048,
        }.get(task, 1024)
```

---

## Vision Prompt Patterns

### Pattern 1: Structured Extraction

```
Use when: extracting specific fields from an image (receipts, forms, cards)

Prompt template:
"Analyze this image and extract the following fields as JSON:
- field_1: description of what to extract
- field_2: description of what to extract
Return ONLY valid JSON. If a field is not visible, use null."
```

### Pattern 2: Bounding Box Description

```
Use when: identifying and locating objects in an image

Prompt template:
"Identify all [object_type] in this image. For each, provide:
1. Description
2. Approximate bounding box as [x_min, y_min, x_max, y_max]
   normalized to 0-1000 scale
3. Confidence level (high/medium/low)"
```

### Pattern 3: Comparison Analysis

```
Use when: comparing two or more images

Prompt template:
"Compare Image 1 and Image 2. For each of these dimensions:
- [dimension_1]
- [dimension_2]
- [dimension_3]
State what is the same and what differs. Use a table format."
```

### Pattern 4: Chain-of-Thought Vision

```
Use when: complex visual reasoning, diagram analysis

Prompt template:
"Analyze this diagram step by step:
1. First, identify all components/elements visible
2. Then, describe the relationships/connections between them
3. Finally, answer: [specific question about the diagram]"
```

### Pattern 5: Set-of-Marks for UI

```
Use when: identifying interactive elements in UI screenshots

Implementation:
1. Overlay numbered markers on UI elements using CV
2. Send marked image to vision LLM
3. Prompt: "Element 3 is a button labeled 'Submit'.
   Describe what each numbered element does."
```

---

## Audio: Speech-to-Text Patterns

### STT Provider Comparison

| Provider | Model | WER (English) | Latency | Cost (per hour) | Diarization |
|---|---|---|---|---|---|
| OpenAI | Whisper v3 large | 4.2% | Batch only | $0.006/min | No |
| OpenAI | Whisper v3 turbo | 5.1% | Near real-time | $0.006/min | No |
| Deepgram | Nova-2 | 3.8% | Real-time | $0.0043/min | Yes |
| Google | Chirp 2 | 4.0% | Real-time | $0.016/min | Yes |
| AssemblyAI | Universal-2 | 3.5% | Near real-time | $0.011/min | Yes |
| AWS | Transcribe | 5.5% | Real-time | $0.024/min | Yes |

### Audio Transcription Pipeline

```python
class TranscriptionPipeline:
    def __init__(self, provider="whisper"):
        self.provider = provider

    async def transcribe(self, audio_path: str, options: dict = None) -> dict:
        options = options or {}

        # Step 1: Audio preprocessing
        processed = self._preprocess_audio(audio_path)

        # Step 2: Transcription
        transcript = await self._transcribe(processed, options)

        # Step 3: Post-processing
        if options.get("diarization"):
            transcript = await self._add_diarization(processed, transcript)

        if options.get("summarize"):
            transcript["summary"] = await self._summarize(transcript["text"])

        return transcript

    def _preprocess_audio(self, path: str) -> str:
        """Normalize audio for optimal transcription."""
        # Convert to 16kHz mono WAV (optimal for most STT)
        # Remove silence at start/end
        # Normalize volume
        # Split long files into chunks (< 25MB for Whisper API)
        pass
```

### Audio Preprocessing Checklist

- [ ] Convert to 16kHz sample rate (STT optimal)
- [ ] Convert to mono channel
- [ ] Normalize volume (target -20 dBFS)
- [ ] Remove leading/trailing silence
- [ ] Split files >25MB into overlapping chunks (30s overlap)
- [ ] For noisy audio: apply noise reduction (noisereduce library)
- [ ] For phone audio: apply bandpass filter (300Hz-3400Hz)

---

## Document Understanding Patterns

### PDF Processing Decision Tree

```
PDF file received
│
├── Has text layer? (check with PyMuPDF)
│   ├── YES → Text extraction path
│   │   ├── Simple text → PyMuPDF extract + LLM
│   │   ├── Tables → Camelot/Tabula extraction
│   │   └── Mixed content → Hybrid (text + vision for complex pages)
│   │
│   └── NO → Image path (scanned document)
│       ├── Clean scan → Vision API (page-by-page)
│       ├── Poor quality → Preprocess (deskew, enhance) → Vision API
│       └── Handwritten → Vision API (expect lower accuracy)
│
├── Multi-page? (>5 pages)
│   ├── YES → Page-by-page processing with aggregation
│   │   ├── Map: process each page independently
│   │   └── Reduce: merge results with cross-page dedup
│   │
│   └── NO → Process all pages in single request (if within token limit)
│
└── Need structured extraction?
    ├── YES → Vision + JSON mode / structured outputs
    └── NO → Vision + free-text summarization
```

### PDF Extraction Code

```python
import fitz  # PyMuPDF

class PDFProcessor:
    def __init__(self, vision_client):
        self.vision = vision_client

    def process(self, pdf_path: str, mode: str = "auto") -> dict:
        doc = fitz.open(pdf_path)

        if mode == "auto":
            mode = self._detect_mode(doc)

        if mode == "text":
            return self._text_extraction(doc)
        elif mode == "vision":
            return self._vision_extraction(doc)
        else:  # hybrid
            return self._hybrid_extraction(doc)

    def _detect_mode(self, doc) -> str:
        """Determine if PDF has extractable text."""
        sample_page = doc[0]
        text = sample_page.get_text()

        if len(text.strip()) > 50:
            # Check if tables present
            tables = sample_page.find_tables()
            if tables:
                return "hybrid"
            return "text"
        return "vision"

    def _vision_extraction(self, doc) -> dict:
        results = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=200)  # 200 DPI for good quality
            img_bytes = pix.tobytes("jpeg")

            result = self.vision.analyze(
                image=img_bytes,
                prompt=f"Extract all content from page {page_num + 1}."
            )
            results.append(result)

        return {"pages": results, "total_pages": len(doc)}
```

---

## Multimodal RAG Patterns

### Architecture Options

| Pattern | Use When | Implementation |
|---|---|---|
| Text-only RAG | Documents are text-heavy | Extract text → embed → retrieve → LLM |
| Vision RAG | Documents have charts/images | Store page images → vision embed → retrieve → vision LLM |
| Hybrid RAG | Mix of text and visual content | Both text and image embeddings → fused retrieval |
| Late fusion | Need both modalities at query time | Retrieve text + images separately → combine at LLM |

### Multimodal Embedding Models (January 2026)

| Model | Modalities | Dimensions | Cost |
|---|---|---|---|
| OpenAI text-embedding-3-large | Text only | 3072 | $0.00013/1K tokens |
| Nomic Embed Vision | Text + Image | 768 | Self-hosted |
| Voyage Multimodal 3 | Text + Image | 1024 | $0.00018/1K tokens |
| Google Multimodal Embeddings | Text + Image | 1408 | $0.00005/1K tokens |
| Cohere Embed v3 | Text only | 1024 | $0.0001/1K tokens |

### Multimodal RAG Pipeline

```python
class MultimodalRAG:
    def __init__(self, text_embedder, image_embedder, vector_store, vision_llm):
        self.text_embedder = text_embedder
        self.image_embedder = image_embedder
        self.store = vector_store
        self.llm = vision_llm

    async def ingest(self, document):
        """Index both text and images from a document."""
        # Extract and embed text chunks
        for chunk in document.text_chunks:
            embedding = await self.text_embedder.embed(chunk.text)
            await self.store.upsert(
                id=chunk.id,
                embedding=embedding,
                metadata={"type": "text", "content": chunk.text, "page": chunk.page}
            )

        # Extract and embed images/figures
        for image in document.images:
            embedding = await self.image_embedder.embed(image.bytes)
            await self.store.upsert(
                id=image.id,
                embedding=embedding,
                metadata={"type": "image", "page": image.page, "caption": image.caption}
            )

    async def query(self, question: str, top_k: int = 5):
        """Retrieve multimodal context and generate answer."""
        query_embedding = await self.text_embedder.embed(question)
        results = await self.store.search(query_embedding, top_k=top_k)

        # Build multimodal context
        context_parts = []
        images = []
        for result in results:
            if result.metadata["type"] == "text":
                context_parts.append(result.metadata["content"])
            else:
                images.append(result.metadata)

        # Generate with vision LLM
        return await self.llm.generate(
            text_context="\n".join(context_parts),
            images=images,
            question=question
        )
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| Sending full-resolution images | Wastes tokens, no quality gain | Resize to model's optimal resolution |
| Using vision for text-heavy PDFs | 10x more expensive than text extraction | Check for text layer first |
| Transcribing audio without preprocessing | Higher error rate, worse accuracy | Normalize volume, resample to 16kHz |
| Single embedding model for text+images | Poor cross-modal retrieval | Use dedicated multimodal embeddings |
| Processing 100-page PDF in one request | Context overflow, hallucination | Page-by-page with map-reduce |
| Ignoring image token costs | Surprise $100+ bills | Calculate cost before processing |
| Using vision for simple OCR | Overkill, expensive | Use Tesseract for clean text |
| No caching for repeated image analysis | Redundant API calls | Cache results by image hash |

---

## Cross-References

- `structured-output-patterns.md` — extracting structured data from vision output
- `model-migration-guide.md` — vision capability differences across providers
- `../ai-agents/references/voice-multimodal-agents.md` — voice + vision agent pipelines
- `../ai-llm-inference/references/cost-optimization-patterns.md` — cost management for multimodal
- `../ai-prompt-engineering/references/multimodal-prompt-patterns.md` — prompt templates for vision/audio
