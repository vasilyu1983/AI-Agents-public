# API Design Patterns for ML, LLM & RAG Services

A set of operational patterns for building reliable inference APIs.

---

## 1. Input Schema Design

### Best Practices

- Use strict JSON schemas
- Reject unknown fields
- Validate types and ranges
- Document required vs optional parameters

**Checklist – Input Validation**

- [ ] JSON schema defined
- [ ] Range constraints enforced
- [ ] Error messages actionable

---

## 2. Output Schema Design

Include:

- Prediction
- Confidence / scores
- Model version
- Timestamp
- Optional explanations or metadata

### Example

{
"prediction": "approved",
"score": 0.82,
"model_version": "v44",
"time": "2025-03-01T13:55:00Z"
}

---

## 3. API Reliability Patterns

### Pattern 1: Timeouts & Retries

- Enforce request timeout
- Use retry with exponential backoff for downstream dependencies

### Pattern 2: Circuit Breakers

- Open circuit if failures spike
- Protects system from cascading failures

### Pattern 3: Rate Limiting

- Per-user or global QPS limit
- Prevents abuse & overload

---

## 4. Feature Enrichment Patterns

### 1. Pre-request enrichment

- Attach metadata (geo, user profile)
- Validate feature availability

### 2. Real-time feature lookup

- Feature store or fast DB lookup (Redis)

### 3. Post-processing

- Threshold application
- Safety filters (for LLM)

---

## 5. Logging & Observability Requirements

Include:

- request_id  
- user_id (hashed)  
- latency  
- model_version  
- input anomalies  

### Never log

- Raw personally identifiable information  
- Sensitive text without sanitization  

---

## 6. SLO / SLA Definitions

### Recommended SLOs

- Latency: P95 < 200–500 ms
- Availability: > 99%
- Error rate: < 0.1%

---

## 7. API Checklist

- [ ] Request/response schemas stable
- [ ] Validation in place
- [ ] Error handling consistent
- [ ] Logging safe (no PII)
- [ ] Rate limiting + timeouts enabled
