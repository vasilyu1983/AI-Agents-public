# Multimodal Prompt Patterns

> Operational reference for prompting with vision, audio, and document inputs — image description patterns, bounding box prompts, OCR+LLM workflows, audio transcription instructions, document extraction, multi-image comparison, and video frame analysis.

**Freshness anchor:** January 2026 — covers GPT-4o vision prompting, Claude 3.5 Sonnet vision, Gemini 2.0 multimodal, Whisper v3 prompt conditioning, and document AI patterns.

---

## Pattern Selection Quick Reference

| Task | Pattern | Model Recommendation | Cost |
|---|---|---|---|
| Describe an image | General description | Any vision model | $ |
| Extract text from image | OCR prompt | Gemini Flash (cheapest) | $ |
| Extract structured data from image | Schema extraction | GPT-4o structured | $$ |
| Compare two images | Side-by-side comparison | GPT-4o or Claude | $$ |
| Analyze UI screenshot | Set-of-marks + action | Claude or GPT-4o | $$ |
| Transcribe audio | STT + formatting prompt | Whisper + LLM | $ |
| Extract data from PDF | Document extraction | Vision per page | $$ |
| Parse tables from images | Table schema prompt | GPT-4o structured | $$ |
| Analyze video | Frame sampling + vision | Gemini (native) | $$$ |
| Identify objects with locations | Bounding box prompt | GPT-4o | $$ |

---

## Vision Prompt Patterns

### Pattern 1: General Image Description

```
Use when: need a natural language description of image content
Quality tip: be specific about what aspects to describe

PROMPT:
Describe this image in detail. Focus on:
1. Main subject(s) and their appearance
2. Setting/background
3. Colors, lighting, and mood
4. Any text visible in the image
5. Notable details or unusual elements

Be factual. Do not speculate about things not visible in the image.
```

### Pattern 2: Structured Data Extraction

```
Use when: extracting specific fields from an image (receipt, business card, form)

PROMPT:
Extract the following information from this image. Return JSON only.

Schema:
{
  "vendor_name": "string",
  "date": "YYYY-MM-DD",
  "items": [{"name": "string", "quantity": "number", "price": "number"}],
  "subtotal": "number",
  "tax": "number",
  "total": "number",
  "payment_method": "string or null"
}

Rules:
- If a field is not visible or legible, use null
- For prices, use numeric values (no currency symbols)
- For dates, convert to ISO format
- If text is partially obscured, note "[unclear]" in the value
```

### Pattern 3: Bounding Box / Region Identification

```
Use when: need to locate objects within an image

PROMPT:
Identify all [TARGET_OBJECTS] in this image. For each one, provide:

1. Label: what the object is
2. Bounding box: [x_min, y_min, x_max, y_max] as percentages (0-100)
   where (0,0) is top-left and (100,100) is bottom-right
3. Confidence: high, medium, or low
4. Description: brief description of the specific instance

Return as a JSON array. Example:
[
  {
    "label": "car",
    "bbox": [10, 30, 45, 80],
    "confidence": "high",
    "description": "Red sedan, front-facing"
  }
]
```

### Pattern 4: OCR + Understanding

```
Use when: need both text extraction AND comprehension

PROMPT:
This image contains a [DOCUMENT_TYPE]. Perform the following:

Step 1: Extract all visible text exactly as written
Step 2: Identify the document structure (headers, sections, lists)
Step 3: Answer these specific questions based on the content:
- [Question 1]
- [Question 2]
- [Question 3]

For Step 1, preserve original formatting including line breaks.
For Step 3, cite the specific text that supports each answer.
```

### Pattern 5: Set-of-Marks for UI

```
Use when: identifying and describing interactive UI elements

PREPROCESSING STEP:
1. Overlay numbered circles/rectangles on each interactive element
2. Use a consistent color (e.g., red) with white number labels
3. Number elements left-to-right, top-to-bottom

PROMPT:
This is a screenshot of [APPLICATION_NAME] with numbered markers on
interactive elements.

For each numbered element, provide:
1. Element number
2. Element type (button, link, input field, dropdown, checkbox, etc.)
3. Label/text on the element
4. Likely action when clicked/activated
5. Current state (enabled/disabled, checked/unchecked, etc.)

Return as a structured list.
```

### Pattern 6: Multi-Image Comparison

```
Use when: comparing 2+ images for differences, quality, or content

PROMPT:
I'm providing [N] images for comparison.

For each of these dimensions, compare all images:

| Dimension | Image 1 | Image 2 | ... |
|-----------|---------|---------|-----|
| [Dim 1]   |         |         |     |
| [Dim 2]   |         |         |     |

Dimensions to compare:
- [Dimension 1]: [what to evaluate]
- [Dimension 2]: [what to evaluate]
- [Dimension 3]: [what to evaluate]

After the comparison table, provide:
- Key differences summary
- Recommendation (if applicable)
```

---

## Document Understanding Prompts

### Pattern 7: Table Extraction

```
Use when: extracting tabular data from images or PDFs

PROMPT:
This image contains a table. Extract its complete contents.

Output format:
{
  "headers": ["col1", "col2", ...],
  "rows": [
    ["val1", "val2", ...],
    ...
  ],
  "notes": "any footnotes or annotations visible"
}

Rules:
- Preserve exact cell values (numbers, text, symbols)
- For merged cells, repeat the value in each position
- For empty cells, use ""
- If a cell contains multiple lines, join with " | "
- If the table spans multiple pages, note "continues on next page"
```

### Pattern 8: Form Understanding

```
Use when: extracting filled form data

PROMPT:
This image shows a completed form. Extract all field-value pairs as JSON.
Include: field_label, field_type (text|checkbox|radio|signature|date),
value, and confidence (high|medium|low).
- Checkboxes: true if checked, false if unchecked
- Handwritten text: best interpretation with [handwritten] tag
- Illegible fields: "[illegible]" with confidence: "low"
```

### Pattern 9: Multi-Page Document Processing

```
Use when: processing a document across multiple pages

PAGE-LEVEL PROMPT:
This is page [N] of [TOTAL] of a [DOCUMENT_TYPE].

Extract:
1. All text content with structure preserved
2. Any tables (in structured format)
3. Any figures/charts (described)
4. References to other pages ("see page X", "continued from...")

Mark any content that:
- Continues from a previous page: [CONTINUED]
- Continues on the next page: [CONTINUES]

AGGREGATION PROMPT:
I'm providing extracted content from [N] pages of a [DOCUMENT_TYPE].
Merge the content into a single coherent document:
1. Join split paragraphs across pages
2. Merge split tables
3. Resolve cross-page references
4. Remove duplicate headers/footers
5. Maintain document structure (sections, numbering)
```

---

## Audio Prompt Patterns

### Pattern 10: Whisper Prompt Conditioning

```
Use when: transcribing audio with domain-specific terminology

# Whisper API with prompt conditioning
response = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    prompt="Terms: Kubernetes, PostgreSQL, Redis, NGINX, gRPC, OAuth 2.0",
    language="en",
    response_format="verbose_json",
    timestamp_granularities=["segment", "word"]
)

TERMINOLOGY PROMPT TIPS:
- List domain-specific terms that Whisper might misrecognize
- Include proper nouns (company names, product names)
- Include acronyms with correct casing
- Keep prompt under 224 tokens
- Do NOT include instructions — only vocabulary hints
```

### Pattern 11: Transcript Post-Processing

```
Use when: cleaning and structuring raw transcription output

PROMPT:
Below is a raw audio transcription. Clean and structure it:

Raw transcript:
"""
[RAW_TRANSCRIPT]
"""

Tasks:
1. Fix obvious transcription errors (homophone mistakes, etc.)
2. Add proper punctuation and capitalization
3. Break into paragraphs at topic changes
4. If multiple speakers are detected, label as Speaker 1, Speaker 2, etc.
5. Remove filler words (um, uh, like, you know) unless they convey meaning
6. Flag any sections that seem garbled: [UNCLEAR: approximate text]

Output the cleaned transcript. Preserve the original meaning exactly.
Do not add, summarize, or interpret — only clean the formatting.
```

### Pattern 12: Speaker Diarization Post-Processing

```
Use when: formatting diarized transcripts into readable format

PROMPT:
Below is a diarized transcript with speaker labels and timestamps.
Format it into a clean meeting transcript.

Raw input:
"""
[SPEAKER_0 00:00:05] welcome everyone to today's standup
[SPEAKER_1 00:00:08] hey good morning
[SPEAKER_0 00:00:10] let's start with updates john what do you have
"""

Tasks:
1. Replace SPEAKER_N with actual names if identifiable from context
   (otherwise keep Speaker 1, Speaker 2, etc.)
2. Format timestamps as [MM:SS]
3. Combine consecutive segments from same speaker
4. Add paragraph breaks at topic transitions
5. Generate a brief summary of key discussion points at the end
```

---

## Video Frame Analysis

### Frame Sampling Strategy

| Video Type | Sampling Rate | Rationale |
|---|---|---|
| Static presentation/slides | 1 frame per slide change | Detect transitions |
| Interview/talking head | 1 frame per 30 seconds | Minimal visual change |
| Product demo | 1 frame per 5 seconds | UI changes frequently |
| Security footage | 1 frame per second (motion-triggered) | Only analyze when activity detected |
| Sports/action | 2-5 frames per second | Fast-moving content |

### Video Analysis Prompt

```
Use when: analyzing video content through sampled frames

PROMPT:
I'm providing [N] frames sampled from a [VIDEO_TYPE] video.
Frames are in chronological order, [X] seconds apart.

For each frame, briefly note:
- Frame number and approximate timestamp
- Key visual content
- Changes from previous frame

After analyzing all frames, provide:
1. Overall video summary
2. Key events/transitions timeline
3. [SPECIFIC_QUESTION about the video content]

Focus on what is visually evident. Do not speculate about
audio content or off-screen events.
```

### Frame Extraction Notes

- Use OpenCV (`cv2.VideoCapture`) to extract frames at intervals
- Resize frames to 1024px wide (16:9) for cost efficiency
- Encode as JPEG 85% quality, base64 for API submission
- For Gemini 2.0: pass video file directly (native video support)
- For other providers: extract 10-20 key frames max per video

---

## Prompt Engineering Tips by Modality

### Vision-Specific Tips

| Tip | Why | Example |
|---|---|---|
| Specify output format upfront | Prevents narrative responses | "Return JSON only" |
| Reference image regions explicitly | Guides attention | "In the top-right corner..." |
| Use chain-of-thought for complex images | Improves accuracy | "First identify all elements, then..." |
| Set confidence expectations | Gets honest uncertainty | "If unsure, say 'uncertain'" |
| Provide schema for extraction | Consistent output | JSON schema in prompt |
| Limit to what's visible | Prevents hallucination | "Only describe what is visible" |

### Audio-Specific Tips

| Tip | Why | Example |
|---|---|---|
| Provide domain vocabulary | Reduces misrecognition | "Terms: Kubernetes, Redis" |
| Specify language | Avoids detection errors | `language="en"` |
| Use verbose_json format | Gets timestamps + segments | `response_format="verbose_json"` |
| Pre-process noisy audio | Improves accuracy | Noise reduction before STT |
| Handle long audio in chunks | API limits + quality | Split at 10-min segments with overlap |

### Document-Specific Tips

| Tip | Why | Example |
|---|---|---|
| Render at 200+ DPI | Ensures text is legible | `page.get_pixmap(dpi=200)` |
| Process page by page | Context window limits | Map-reduce over pages |
| Increase image contrast | Better OCR accuracy | `ImageEnhance.Contrast(img).enhance(1.3)` |
| Provide document type context | Guides extraction | "This is an invoice" |
| Specify expected fields | Focused extraction | "Extract: vendor, date, total" |

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| "Describe this image" with no specificity | Vague, verbose output | List specific aspects to describe |
| Sending 4K images for simple classification | Wastes tokens | Resize to 512px for classification |
| No output format specification | Inconsistent responses | Always specify JSON, table, or list format |
| Asking about audio content in vision prompt | Model cannot hear | Use STT for audio, vision for images |
| Processing all PDF pages in one request | Context overflow | Page-by-page with aggregation |
| No error handling for "I cannot see" responses | Silent failures | Check for refusal patterns in output |
| Using same prompt across all vision models | Models have different strengths | Adapt prompt to model (XML for Claude, etc.) |
| Extracting text from clean PDFs via vision | 10x more expensive | Check for text layer first, use PyMuPDF |

---

## Cross-References

- `prompt-testing-ci-cd.md` — testing multimodal prompts
- `prompt-security-defense.md` — security for multimodal inputs
- `../ai-llm/references/multimodal-patterns.md` — LLM-level multimodal capabilities and costs
- `../ai-llm/references/structured-output-patterns.md` — structured extraction from vision
- `../ai-agents/references/voice-multimodal-agents.md` — voice + vision agent patterns
