# Code Chunking Template (Function/Class Aware)

Chunk code by logical boundaries rather than fixed token sizes.

---

## 1. Parameters

chunk_type: "code"
min_block_size: 30
max_block_size: 200
language: "<python/js/java/etc>"

---

## 2. Chunking Rules

- Split by:
  - Function definitions
  - Class definitions
  - Top-level blocks
- Maintain indentation context
- Add file path metadata
- Avoid breaking functions across chunks

---

## 3. Output Format

{
"id": "<chunk_id>",
"text": "<code_block>",
"source_file": "<path/to/file>",
"function": "<function_name>",
"language": "<lang>"
}

---

## 4. Checklist

- [ ] Syntax-preserving  
- [ ] Blocks not split mid-function  
- [ ] Language metadata applied  
