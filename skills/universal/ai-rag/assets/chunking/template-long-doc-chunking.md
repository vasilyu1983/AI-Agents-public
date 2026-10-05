# Long Document Chunking Template (Hierarchical)

Use for manuals, books, legal docs, and structured multi-section content.

---

## 1. Parameters

max_section_length: 1200 # tokens
subsection_overlap: 150
preserve_headings: true

---

## 2. Workflow

1. Split by major section headings  
2. Inside each section:
   - Apply sliding-window chunking  
   - Maintain parent/child structure  

3. Add hierarchical metadata:
   - section  
   - subsection  
   - page number  

---

## 3. Output Format

{
"id": "<chunk_id>",
"text": "<chunk>",
"source": "<document_id>",
"metadata": {
"section": "<heading>",
"subsection": "<subheading>",
"page": <page_number>
}
}
