# ML/LLM API Service Template

A complete template for building a production ML/LLM inference API.

---

## 1. API Overview

**Endpoint:** /v1/predict  
**Method:** POST  
**Input Format:** JSON  
**Response Type:** Deterministic (JSON)  
**SLO:** P95 < <ms>  

---

## 2. Request Schema

{
"features": {
"<field_1>": <value>,
"<field_2>": <value>,
...
},
"metadata": {
"request_id": "<uuid>"
}
}

**Validation Rules**

- Reject unknown fields  
- Enforce dtype constraints  
- Validate ranges  

---

## 3. Response Schema

{
"prediction": <value>,
"confidence": <score>,
"model_version": "<vX.Y>",
"timestamp": "<ISO-8601>"
}

---

## 4. API Logic Flow

1. Validate JSON schema  
2. Sanitize input (PII removal if needed)  
3. Retrieve features (online feature store or payload)  
4. Load model (version-pinned)  
5. Run inference  
6. Package response  
7. Log metadata  

---

## 5. Reliability Patterns

- Timeout per request (<threshold ms)  
- Retry rules for DB / feature store  
- Circuit breaker around external services  
- Strict rate limiting (global + per-IP)  

---

## 6. Observability

Log:

- request_id  
- model_version  
- latency_ms  
- error_state  

Metrics:

- P50/P95/P99 latencies  
- Inference success rate  
- Throughput (req/s)  

---

## 7. Deployment Details

- Container image: <URI>  
- Resource requests: <CPU/GPU/Memory>  
- Autoscaling rules: <config>  

---

## 8. Testing

- Unit tests for schema  
- Integration tests for feature fetch  
- Load test before promotion  
