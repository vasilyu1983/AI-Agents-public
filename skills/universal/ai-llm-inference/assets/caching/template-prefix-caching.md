# Prefix and Prompt Caching Template

Caches repeated prefixes or prompts to reduce compute pressure.

---

## 1. Cache Types

### Prefix Cache

- Cache prefill for repeated prompt beginnings  
- Great for many users sharing similar instructions  

### Response Cache (Semantic)

- Cache full responses for identical or semantically close queries  

---

## 2. Cache Config

cache:
enabled: true
type: "prefix"
max_entries: 5000
eviction: "lru"

---

## 3. Cache Keys

- Hash of normalized prompt prefix  
- Model version  
- Context window settings  

---

## 4. Validation Checklist

- [ ] Prefix detection correct  
- [ ] No stale cache entries  
- [ ] Cache hit-rate tracked
