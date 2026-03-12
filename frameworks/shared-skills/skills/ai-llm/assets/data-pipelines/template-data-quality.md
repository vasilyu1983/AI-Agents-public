# Data Quality Pipeline Template

*Purpose: Copy-paste scaffold for constructing data pipelines that ensure clean, deduplicated, relevant, and safe training/evaluation data for LLMs, RAG, or agentic systems.*

---

## When to Use

Use this template when:

- Preparing training, fine-tuning, or RAG data for any LLM or agent system
- You need to guarantee data freshness, consistency, deduplication, and PII safety
- You must pass production LLMOps or compliance review for data quality

---

## Structure

This template has 5 sections:

1. **Ingestion** – load raw data from all sources
2. **Filtering & Deduplication** – remove junk, deduplicate, basic cleaning
3. **PII & Safety Scanning** – detect and remove personally identifiable info or toxic content
4. **Labeling & Metadata** – assign tags, data splits, version, and source info
5. **Validation & Audit** – test data pipeline, sample review, and version audit

---

# TEMPLATE STARTS HERE

**Pipeline Scaffold:**

```
1. Ingestion
   - Load data from all required sources (docs, web, PDFs, code, etc)
   - Track source and collection date for each file or row

2. Filtering & Deduplication
   - Remove empty or near-duplicate records (use hashes or similarity)
   - Strip boilerplate, ads, footers, legal disclaimers
   - Normalize encoding and line endings

3. PII & Safety Scanning
   - Scan and redact emails, phone numbers, credit cards, names, locations, etc.
   - Use toxicity filter or blocklist to remove unsafe/abusive content
   - Document all PII redactions/removals

4. Labeling & Metadata
   - Assign split: train/valid/test or pretrain/finetune/eval
   - Add language, domain, or topic tags
   - Store version, source, and pipeline config for every output batch

5. Validation & Audit
   - Sample rows for human review (spot-check data, PII, toxic content)
   - Log pass/fail, run regression on pipeline after edits
   - Archive all data pipeline configs for reproducibility
```

---

# COMPLETE EXAMPLE

**Pythonic pseudo-code (pipeline script):**

```python
# 1. Ingest
docs = load_files("raw_data/", recursive=True)
docs = [{**doc, "source": src, "date": today()} for doc, src in docs]

# 2. Filter & Dedup
docs = filter_empty(docs)
docs = deduplicate_by_hash(docs)
docs = strip_boilerplate(docs)

# 3. PII & Safety Scan
docs = redact_pii(docs)
docs = remove_toxic_content(docs)

# 4. Label/Metadata
for doc in docs:
    doc['split'] = assign_split(doc)
    doc['lang'] = detect_language(doc['content'])
    doc['pipeline_ver'] = "v1.0"
    doc['source'] = doc['source']

# 5. Validate/Audit
sample = random_sample(docs, 0.01)
human_review(sample)
log_pipeline_version("v1.0", pipeline_config)
```

---

## Quality Checklist

Before finalizing:

- [ ] All data sources logged, dates and source tracked
- [ ] Deduplication and filtering scripts run, verified (no near-duplicate rows)
- [ ] PII scan/removal complete and logged
- [ ] Toxic/abusive content filter applied
- [ ] Each row labeled with split, language, version, and source
- [ ] Manual review spot-checks at least 1% of data
- [ ] Pipeline config, audit logs, and version archived for reproducibility

---

*For RAG/Retrieval, see [template-basic-rag.md] or [template-advanced-rag.md]. For deployment or agentic QA, see other templates and [references/llmops-best-practices.md].*
