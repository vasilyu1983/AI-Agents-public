# Basic RAG Pipeline Template

*Purpose: Scaffold a minimal, vendor-neutral Retrieval-Augmented Generation pipeline for document search, grounding, or FAQ systems. Start here before adding reranking, routing, or graph retrieval.*

---

## When to Use

Use this template when:

- The system needs current or private knowledge not present in the base model
- A simple retrieval layer is enough for the first production version
- You need a baseline that can be evaluated before adding more complexity

---

## Structure

This template has 4 main sections:

1. **Document preparation** - load, clean, chunk, and label source material
2. **Embedding and indexing** - convert chunks into vectors and store them
3. **Retrieval** - fetch the most relevant chunks for a query
4. **Grounded generation** - answer from retrieved evidence and cite it

---

# TEMPLATE STARTS HERE

## 1. Document Preparation

- Load documents from the chosen corpus
- Normalize formatting and remove obvious duplicates
- Split into chunks sized for your corpus and question style
- Store metadata: source id, title, section, timestamp, ACL tags

## 2. Embedding and Indexing

**Pseudo-code:**

```python
documents = load_documents()
chunks = chunk_documents(documents, chunk_size=512, overlap=64)

embedding_model = make_embedding_model(
    provider="your_provider",
    model="your_current_embedding_model"
)

vector_store = make_vector_store(kind="qdrant")  # or pgvector, Pinecone, Chroma, etc.
vector_store.add_documents(chunks, embedding_model=embedding_model)
```

## 3. Retrieval

**Query-time process:**

- Receive the user question
- Apply filters if the corpus is partitioned by tenant, team, time, or permission
- Retrieve top-k candidate chunks with the same embedding model family used at index time
- Return chunk text plus metadata needed for citation

**Pseudo-code:**

```python
question = "What is the warranty policy?"

retrieved = vector_store.similarity_search(
    question,
    k=4,
    filters={"visibility": "customer_facing"}
)
```

## 4. Grounded Generation

**Prompt template:**

```text
You must answer using only the provided context.
If the answer is missing, say what is missing.
When possible, cite the source ids you used.

Context:
{retrieved_chunks}

Question: {user_question}

Answer:
```

**Generation rules:**

- Keep the answer tied to retrieved evidence
- Return citations or source ids with factual claims
- Fail clearly when evidence is absent instead of filling gaps from prior knowledge

---

# COMPLETE EXAMPLE

```python
documents = load_documents("docs/**/*.md")
chunks = chunk_documents(documents, chunk_size=512, overlap=64)

embedding_model = make_embedding_model(
    provider="your_provider",
    model="your_current_embedding_model"
)

vector_store = make_vector_store(kind="qdrant")
vector_store.add_documents(chunks, embedding_model=embedding_model)

question = "What is the warranty policy?"
retrieved = vector_store.similarity_search(question, k=4)

context = "\n\n".join(
    f"[{chunk.metadata['source_id']}] {chunk.page_content}"
    for chunk in retrieved
)

prompt = f"""
You must answer using only the provided context.
If the answer is missing, say what is missing.
When possible, cite the source ids you used.

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

- [ ] Chunking approach documented and tested on real questions
- [ ] Embedding model is versioned and consistent between indexing and query-time retrieval
- [ ] Metadata supports citation, filtering, and access control
- [ ] Retrieval is evaluated on a small gold set before shipping
- [ ] Prompt requires grounded answers and explicit "missing evidence" behavior
- [ ] Output logs capture retrieval ids and final answer for debugging and evals

---

*For hybrid retrieval and reranking, see [template-advanced-rag.md](template-advanced-rag.md). For evaluation guidance, see [../../references/eval-patterns.md](../../references/eval-patterns.md).*
