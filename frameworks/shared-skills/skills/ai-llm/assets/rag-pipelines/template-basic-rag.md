# Basic RAG Pipeline Template

*Purpose: Instantly scaffold a minimal, working Retrieval-Augmented Generation (RAG) pipeline for document search, QA, or LLM grounding—usable in LangChain, LlamaIndex, or similar frameworks.*

---

## When to Use

Use this template when:

- You need a fast, reliable RAG implementation for internal KB, FAQ, or doc search
- LLM must ground answers in external data
- Simple, single-language, text-only use case (expand for advanced/hybrid needs)

---

## Structure

This template has 4 main sections:

1. **Chunking** – split source docs for retrieval
2. **Embedding** – convert chunks to vector space
3. **Retrieval** – retrieve top-k similar chunks at query time
4. **Prompt Assembly & Generation** – compose context and generate grounded answer

---

# TEMPLATE STARTS HERE

## 1. Chunking

**Script/Process:**

- Load docs (markdown, PDF, etc)
- Split into chunks (e.g., 400–600 tokens each, 50–100 token overlap)
- Save chunk metadata: source, position, doc ID

## 2. Embedding

**Code Example (Python/LangChain):**

```python
from langchain.embeddings import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
vector_store = Chroma()  # or Pinecone, Qdrant, etc.
vector_store.add_documents(chunks, embeddings)
```

## 3. Retrieval

**Query-Time Process:**

- User submits question
- Embed question (same model)
- Retrieve top-k (e.g., k=4) similar chunks from vector DB

## 4. Prompt Assembly & Generation

**Prompt Template:**

```
You must answer based only on the provided context. If the answer is not found, say "Not found."

Context:
{retrieved_chunks}

Question: {user_question}

Answer:
```

**Generation:**

- Send assembled prompt to LLM (Claude, GPT-4, Gemini, etc)
- Return answer (optionally: highlight source or chunk citations)

---

# COMPLETE EXAMPLE

**Python (Pseudo-code using LangChain):**

```python
# 1. Chunking
docs = load_docs("docs/*.md")
chunks = chunk_docs(docs, chunk_size=512, overlap=64)

# 2. Embedding + Indexing
embeddings = OpenAIEmbeddings()
vector_store = Chroma()
vector_store.add_documents(chunks, embeddings)

# 3. Retrieval at query time
question = "What is the warranty policy?"
q_embedding = embeddings.embed_query(question)
retrieved = vector_store.similarity_search(q_embedding, k=4)

# 4. Prompt Assembly
context = "\n\n".join([c['content'] for c in retrieved])
prompt = f"""
You must answer based only on the provided context. If the answer is not found, say "Not found."

Context:
{context}

Question: {question}

Answer:
"""
answer = call_llm(prompt)
print(answer)
```

---

## Quality Checklist

Before finalizing:

- [ ] All docs chunked, deduped, overlap set (50–100 tokens)
- [ ] Embedding model consistent (same for indexing/query)
- [ ] Vector DB indexed, queryable, low-latency (<1s)
- [ ] Retrieval recall tested (>85% for key questions)
- [ ] Prompt instructs LLM to answer only from context, fallback “Not found”
- [ ] Outputs logged for eval/debug

---

*For advanced/hybrid, see [template-advanced-rag.md]. For evaluation, see [references/eval-patterns.md].*
