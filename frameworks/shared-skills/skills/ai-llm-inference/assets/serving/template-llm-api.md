# LLM API Template

A production-ready API for LLM inference.

---

## 1. Endpoint

POST /v1/generate

---

## 2. Request Body

{
"prompt": "<text>",
"max_tokens": 256,
"temperature": 0.4,
"top_p": 0.9,
"model": "<model_id>"
}

---

## 3. Response Body

{
"output": "<generated_text>",
"model_version": "<vX.Y>",
"tokens": {
"input": <count>,
"output": <count>
},
"latency_ms": <value>
}

---

## 4. Reliability Mechanisms

- Timeout  
- Circuit breaker  
- Request batching  
- Static/dynamic routing  

---

## 5. Observability

- Log request_id  
- Track token usage  
- Emit latency histograms  

---

## 6. Security

- API key required  
- Rate limiting  
- Input sanitization  
