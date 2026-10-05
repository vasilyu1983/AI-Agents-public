# Multimodal LLM Patterns

> Operational reference for working with vision, audio, and document understanding capabilities of LLMs — cost optimization, prompt patterns, preprocessing pipelines, and multimodal RAG architectures.

This legacy reference is outside the adaptation scope. For an image or audio workload, choose a candidate model, then use that model's current modality docs and token counter to price a representative sample before committing to preprocessing settings.

## Table of Contents

- [Modality Selection Quick Reference](#modality-selection-quick-reference)
- [Vision: Image Token Cost Analysis](#vision-image-token-cost-analysis)
- [Vision Prompt Patterns](#vision-prompt-patterns)
- [Audio: Speech-to-Text Patterns](#audio-speech-to-text-patterns)
- [Document Understanding Patterns](#document-understanding-patterns)
- [Multimodal RAG Patterns](#multimodal-rag-patterns)
- [Anti-Patterns](#anti-patterns)

---

## Modality Selection Quick Reference

Model classes, not model names: provider lineups rotate, so look up the current tier names in provider docs before committing a stack.

| Task | Best Modality | Recommended Model Class | Cost Tier |
|---|---|---|---|
| Image description | Vision | Balanced/value tier (e.g. a provider's mid tier) | $$ |
| OCR from clean text | Vision or text extraction | Cheapest available flash/lite-class model | $ |
| Table extraction from image | Vision + JSON mode | OpenAI structured-outputs-capable tier | $$ |
| Document summarization (PDF) | Text extraction + LLM | PyMuPDF → any LLM | $ |
| Scanned document understanding | Vision | Balanced tier (Claude Sonnet class, OpenAI mid tier) | $$ |
| Audio transcription | Speech-to-text | Whisper-class or diarization-capable STT provider | $ |
| Speaker diarization | Specialized | Dedicated diarization model + STT | $ |
| Video understanding | Frame extraction + vision | Native-video-capable frontier model (verify current support) | $$$ |
| Multi-image comparison | Vision (multi-image) | Flash/balanced tier with multi-image support | $$ |
| Diagram/chart analysis | Vision | Premium tier (Claude Opus class or equivalent) | $$ |

> Naming note: avoid pinning specific dated model IDs (e.g. a specific GPT or Claude point release) in this table — provider model families rotate every few months. Look up current names in provider docs before quoting one in a design doc.

---

## Vision: Image Token Cost Analysis

### Token Calculation by Provider

Image tokenization depends on the exact model, image dimensions, resolution setting, and sometimes tiling. Read the selected model's image-input docs and pricing page, then count tokens for sample images at each proposed resolution. Start with the [OpenAI image guide](https://platform.openai.com/docs/guides/images-vision), [Anthropic vision guide](https://docs.anthropic.com/en/docs/build-with-claude/vision), or [Google image-understanding guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/image-understanding) as applicable. Google's documented image tokens differ by model generation and media-resolution setting, so a blanket flat-rate rule is unsafe.

### Cost Optimization Decision Matrix

| Image Type | Candidate optimization | Check before adoption |
|---|---|---|
| Screenshots and photos | Resize or compress | Compare token use and task accuracy on a sample |
| Documents | Crop margins or improve contrast | Preserve small text and verify extraction quality |
| Diagrams | Keep labels readable | Test whether resizing loses relationships |
| Multi-image batches | Compare supported model tiers | Count actual image tokens and total request cost |
| Simple classification | Try a lower image-detail setting where supported | Check the selected model's detail levels and accuracy |

### Image Preprocessing Pipeline

```python
from PIL import Image
import io
import base64

class ImagePreprocessor:
    MAX_DIMENSION = 1024  # illustrative setting; choose from the model's image guidance
    JPEG_QUALITY = 85  # illustrative compression setting; measure quality and cost

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

Compare STT providers on your own audio, not on published WER: accent, domain vocabulary, and noise move WER more than the vendor choice. Record per candidate:

| Criterion | What to measure |
|---|---|
| WER on your audio | Transcribe a labelled sample from real traffic; score WER per slice (accent, noise, domain terms) |
| Latency mode | Batch vs streaming; time-to-first-partial for live use |
| Diarization | Native, add-on, or separate model |
| Cost | Per-minute rate from the provider pricing page on the day you decide; record the date |
| Data handling | Retention, training-on-customer-audio opt-out, region |

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

- [ ] Convert to a sample rate supported by the selected STT model
- [ ] Convert to mono channel
- [ ] Normalize volume only if the selected STT model benefits on a sample
- [ ] Remove leading/trailing silence
- [ ] Split files that exceed the selected provider's current size or duration limit; test overlap against lost words at boundaries
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

### Multimodal Embedding Models

Select a model that embeds both the query and the indexed modality into compatible vectors. Confirm its current supported modalities, dimensions, and pricing in the model card before choosing the index schema; dimensions and model lineups change. Record the model ID and dimension with the index so a later model change triggers re-embedding or a separate index.

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
| Sending full-resolution images without checking the model's image policy | May waste tokens or lose useful detail after automatic resizing | Compare token use and accuracy at candidate resolutions |
| Using vision for text-heavy PDFs without comparing extraction | Can cost more than text extraction | Check the text layer and compare representative pages |
| Assuming one audio preprocessing preset suits every STT model | Can degrade transcription | Test provider-supported formats on representative audio |
| Mixing incompatible text and image embeddings in one index | Cross-modal similarity is undefined | Use a shared embedding space or separate indexes with fusion |
| Processing 100-page PDF in one request | Context overflow, hallucination | Page-by-page with map-reduce |
| Ignoring image token costs | Unbudgeted spend | Calculate cost before processing |
| Using vision for simple OCR | Overkill, expensive | Use Tesseract for clean text |
| No caching for repeated image analysis | Redundant API calls | Cache results by image hash |

---

## Cross-References

- `../../ai-prompt-engineering/references/core-patterns.md` — schema design for extracting structured data from vision output
- `../../ai-mlops/references/model-provider-migration.md` — capability differences when migrating providers
- `../../ai-agents/references/voice-multimodal-agents.md` — voice + vision agent pipelines
- `../../ai-llm-inference/references/cost-optimization-patterns.md` — cost management for multimodal
- `../../ai-prompt-engineering/references/multimodal-prompt-patterns.md` — prompt templates for vision/audio
