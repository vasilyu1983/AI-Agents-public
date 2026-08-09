# Basic Chunking Template (Sliding Window)

A generic sliding-window chunking template suitable for blogs, docs, articles, and general unstructured text.

---

## 1. Parameters

chunk_size: 600 # tokens
chunk_overlap: 100 # tokens
min_chunk_size: 150
split_on_headings: true

---

## 2. Chunking Workflow

1. Clean text  
2. Normalize whitespace  
3. Split by top-level headings if available  
4. Apply sliding window chunking  
5. Add metadata  
6. Filter out empty/small chunks  

---

## 3. Output Format

{
"id": "<chunk_id>",
"text": "<chunk_text>",
"source": "<document_id>",
"start_pos": <token_index>,
"end_pos": <token_index>,
"metadata": {
"section": "<section_title>",
"timestamp": "<optional>",
"tags": []
}
}

---

## 4. Validation Checklist

- [ ] No broken sentences  
- [ ] No empty chunks  
- [ ] IDs stable  
- [ ] Chunk count reasonable  