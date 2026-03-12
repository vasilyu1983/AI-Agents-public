# Model Extraction Defense

Operational patterns for detecting and preventing model extraction attacks where adversaries attempt to steal model capabilities through repeated querying.

---

## Overview

**Model extraction** is an attack where adversaries reconstruct a model's behavior by:

- Querying the model repeatedly with carefully chosen inputs
- Analyzing responses to infer model parameters or decision boundaries
- Building a surrogate model that mimics the original

**Why it matters:**
- Stolen models can be monetized or used competitively
- Extraction enables adversarial attack development
- Proprietary training data or techniques may be exposed

This guide covers **detection, prevention, and mitigation** patterns for model extraction.

---

## Threat Scenarios

### 1. Query-Based Extraction

**Attack:** Adversary sends thousands of queries to map model behavior.

**Example:**
```python
# Adversary's extraction script
for i in range(100000):
    input_sample = generate_strategic_input(i)
    response = api.query(input_sample)
    training_data.append((input_sample, response))

# Train surrogate model
surrogate_model = train_model(training_data)
```

**Impact:** Adversary builds a local copy of your model without training costs.

### 2. Logit/Probability Extraction

**Attack:** If API returns confidence scores or logits, adversary can reconstruct model outputs more accurately.

**Example API response:**
```json
{
  "prediction": "cat",
  "confidence": 0.95,
  "probabilities": {
    "cat": 0.95,
    "dog": 0.03,
    "bird": 0.02
  }
}
```

**Impact:** High-fidelity extraction with fewer queries.

### 3. Gradient/Parameter Probing

**Attack:** If model exposes gradients or parameters (e.g., in federated learning), adversary can directly reconstruct weights.

**Impact:** Perfect model clone.

### 4. Active Learning Extraction

**Attack:** Adversary uses uncertainty sampling to query the most informative inputs.

**Example:**
```python
# Query inputs where model is uncertain
for input in candidate_inputs:
    confidence = api.query(input)["confidence"]
    if confidence < 0.7:  # Low confidence = informative
        training_data.append((input, api.query(input)["prediction"]))
```

**Impact:** Fewer queries needed for high-fidelity extraction.

---

## Detection Patterns

### 1. Rate Limiting

**Limit queries per user/API key:**

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(minutes=window_minutes)
        self.request_log = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit."""
        now = datetime.now()

        # Remove old requests outside window
        self.request_log[user_id] = [
            timestamp for timestamp in self.request_log[user_id]
            if now - timestamp < self.window
        ]

        # Check limit
        if len(self.request_log[user_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False

        # Allow request
        self.request_log[user_id].append(now)
        return True
```

**Rate limit tiers:**
```python
RATE_LIMITS = {
    "free": {"max_requests": 100, "window_minutes": 60},
    "basic": {"max_requests": 1000, "window_minutes": 60},
    "premium": {"max_requests": 10000, "window_minutes": 60}
}
```

**Checklist:**
- [ ] Per-user rate limits configured
- [ ] Rate limits enforced at API gateway
- [ ] Exceeded limits logged and alerted
- [ ] Rate limit bypass attempts detected

---

### 2. Query Similarity Tracking

**Detect repetitive or systematic querying patterns:**

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class QuerySimilarityTracker:
    def __init__(self, similarity_threshold: float = 0.9):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.threshold = similarity_threshold
        self.user_queries = defaultdict(list)

    def track_query(self, user_id: str, query: str) -> bool:
        """Track query and detect high similarity to recent queries."""

        # Embed query
        query_emb = self.model.encode(query)

        # Compare to recent queries
        recent_queries = self.user_queries[user_id][-100:]  # Last 100 queries

        if recent_queries:
            similarities = [
                self.cosine_similarity(query_emb, q_emb)
                for q_emb in recent_queries
            ]

            # Check if high similarity (repetitive querying)
            if max(similarities) > self.threshold:
                logger.warning(f"High query similarity detected for user {user_id}")
                return False  # Suspicious

        # Store query embedding
        self.user_queries[user_id].append(query_emb)
        return True

    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

**Checklist:**
- [ ] Query embeddings tracked per user
- [ ] High similarity patterns detected
- [ ] Suspicious users flagged for review

---

### 3. Repetitive Probing Pattern Detection

**Detect systematic grid searches or parameter sweeps:**

```python
class ProbingDetector:
    def __init__(self):
        self.user_activity = defaultdict(list)

    def detect_probing(self, user_id: str, query: str) -> bool:
        """Detect systematic probing patterns."""

        # Extract numeric parameters from query
        numbers = self.extract_numbers(query)

        # Store activity
        self.user_activity[user_id].append({
            "query": query,
            "numbers": numbers,
            "timestamp": datetime.now()
        })

        # Check for grid search pattern
        recent = self.user_activity[user_id][-50:]  # Last 50 queries

        if len(recent) >= 20:
            # Check if numbers increment systematically
            if self.is_systematic_sequence(recent):
                logger.warning(f"Systematic probing detected for user {user_id}")
                return True

        return False

    def extract_numbers(self, query: str) -> list:
        """Extract numeric values from query."""
        import re
        return [float(n) for n in re.findall(r'\d+\.?\d*', query)]

    def is_systematic_sequence(self, activity: list) -> bool:
        """Check if queries follow systematic pattern (e.g., incrementing values)."""
        numbers_list = [a["numbers"] for a in activity if a["numbers"]]

        if len(numbers_list) < 10:
            return False

        # Check for incrementing pattern
        for i in range(1, len(numbers_list)):
            if numbers_list[i] == numbers_list[i-1]:
                continue  # Skip duplicates
            # More sophisticated checks can be added
            # E.g., checking for arithmetic or geometric progressions

        return True  # Simplified; implement actual logic
```

**Checklist:**
- [ ] Numeric parameter extraction implemented
- [ ] Systematic sequence detection active
- [ ] Grid search patterns flagged

---

### 4. High-Volume Unexplained Activity

**Monitor total query volume per user:**

```python
class VolumeMonitor:
    def __init__(self, daily_threshold: int = 10000):
        self.daily_threshold = daily_threshold
        self.daily_counts = defaultdict(int)

    def check_volume(self, user_id: str) -> bool:
        """Check if user exceeded daily volume threshold."""
        self.daily_counts[user_id] += 1

        if self.daily_counts[user_id] > self.daily_threshold:
            logger.warning(f"High volume activity for user {user_id}: {self.daily_counts[user_id]} queries")
            return False  # Suspicious

        return True

    def reset_daily_counts(self):
        """Reset counts (run daily via cron)."""
        self.daily_counts.clear()
```

**Checklist:**
- [ ] Daily query volume tracked per user
- [ ] High-volume users flagged
- [ ] Volume alerts sent to security team

---

## Prevention Patterns

### 1. Watermarking Outputs

**Embed watermarks in model outputs to trace stolen models:**

```python
import hashlib

class OutputWatermarking:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def watermark(self, response: str, user_id: str) -> str:
        """Embed subtle watermark in response."""

        # Generate watermark based on user_id and secret
        watermark_hash = hashlib.sha256(
            f"{user_id}{self.secret_key}".encode()
        ).hexdigest()[:8]

        # Embed watermark (example: append to metadata or subtle text modification)
        # This is a simplified example; production watermarking is more sophisticated
        watermarked_response = response + f"\n\n<!-- {watermark_hash} -->"

        return watermarked_response

    def detect_watermark(self, response: str) -> str | None:
        """Detect watermark in stolen model output."""
        import re

        match = re.search(r'<!-- ([a-f0-9]{8}) -->', response)
        if match:
            return match.group(1)
        return None
```

**Advanced watermarking:**
- **Text watermarking:** Slight variations in word choice or phrasing
- **Embedding watermarking:** Add imperceptible noise to vector embeddings
- **Timing watermarking:** Subtle latency variations unique to each user

**Checklist:**
- [ ] Watermarking implemented for all outputs
- [ ] Watermark detection tested
- [ ] Watermark registry maintained (user_id → watermark)

---

### 2. Noise or Randomness Injection

**Add slight randomness to outputs to prevent exact reconstruction:**

```python
import random

class NoiseInjector:
    def __init__(self, noise_level: float = 0.01):
        self.noise_level = noise_level

    def add_noise(self, prediction: float) -> float:
        """Add Gaussian noise to prediction."""
        noise = random.gauss(0, self.noise_level)
        return max(0, min(1, prediction + noise))  # Clip to [0, 1]
```

**Benefits:**
- Harder to extract exact model behavior
- Minimal impact on user experience (< 1% noise)

**Tradeoffs:**
- May reduce model accuracy slightly
- Not suitable for deterministic use cases

**Checklist:**
- [ ] Noise injection enabled for non-critical use cases
- [ ] Noise level calibrated (<1% impact on accuracy)
- [ ] Deterministic mode available for trusted users

---

### 3. Throttling + Request Quotas

**Enforce strict quotas per user/API key:**

```python
class QuotaManager:
    def __init__(self):
        self.quotas = {
            "free": {"daily": 100, "monthly": 1000},
            "basic": {"daily": 1000, "monthly": 20000},
            "premium": {"daily": 10000, "monthly": 500000}
        }
        self.usage = defaultdict(lambda: {"daily": 0, "monthly": 0})

    def check_quota(self, user_id: str, tier: str) -> bool:
        """Check if user has remaining quota."""
        usage = self.usage[user_id]
        quota = self.quotas[tier]

        if usage["daily"] >= quota["daily"]:
            logger.warning(f"Daily quota exceeded for user {user_id}")
            return False

        if usage["monthly"] >= quota["monthly"]:
            logger.warning(f"Monthly quota exceeded for user {user_id}")
            return False

        # Increment usage
        usage["daily"] += 1
        usage["monthly"] += 1
        return True
```

**Checklist:**
- [ ] Quota tiers configured (free, basic, premium)
- [ ] Daily and monthly limits enforced
- [ ] Quota exceeded alerts sent

---

### 4. Hide Logits and Confidence Scores

**Avoid exposing detailed model outputs:**

```python
# BAD: Bad: Exposes logits
{
  "prediction": "cat",
  "confidence": 0.95,
  "probabilities": {"cat": 0.95, "dog": 0.03, "bird": 0.02}
}

# GOOD: Good: Only top prediction
{
  "prediction": "cat"
}
```

**Checklist:**
- [ ] Logits and probabilities hidden in production API
- [ ] Only top prediction returned
- [ ] Confidence scores optional (premium tier only)

---

## Model Extraction Defense Checklist

**Detection:**
- [ ] Rate limiting enabled (per user, per API key)
- [ ] Query similarity tracking active
- [ ] Repetitive probing pattern detection implemented
- [ ] High-volume activity monitored and alerted

**Prevention:**
- [ ] Output watermarking deployed
- [ ] Noise injection enabled (calibrated <1% impact)
- [ ] Request quotas enforced (daily, monthly limits)
- [ ] Logits and confidence scores hidden

**Operational:**
- [ ] Extraction attempts logged and analyzed
- [ ] Suspicious users flagged for manual review
- [ ] High-risk traffic requires authentication
- [ ] Monitoring dashboards track extraction indicators
- [ ] Security team alerted on threshold breaches

---

## Real-World Example: Extraction Defense System

```python
class ExtractionDefenseSystem:
    def __init__(self):
        self.rate_limiter = RateLimiter(max_requests=100, window_minutes=60)
        self.similarity_tracker = QuerySimilarityTracker()
        self.probing_detector = ProbingDetector()
        self.volume_monitor = VolumeMonitor(daily_threshold=10000)
        self.watermarker = OutputWatermarking(secret_key="secret")
        self.noise_injector = NoiseInjector(noise_level=0.01)
        self.quota_manager = QuotaManager()

    def serve_request(self, user_id: str, query: str, tier: str) -> dict:
        """Serve request with extraction defenses."""

        # Check quota
        if not self.quota_manager.check_quota(user_id, tier):
            return {"error": "Quota exceeded"}

        # Check rate limit
        if not self.rate_limiter.is_allowed(user_id):
            return {"error": "Rate limit exceeded"}

        # Check query similarity
        if not self.similarity_tracker.track_query(user_id, query):
            logger.warning(f"Suspicious query similarity for user {user_id}")
            # Don't block, but flag for review
            alert_security_team(user_id, "High query similarity")

        # Check for probing
        if self.probing_detector.detect_probing(user_id, query):
            logger.warning(f"Probing detected for user {user_id}")
            alert_security_team(user_id, "Systematic probing")

        # Check volume
        if not self.volume_monitor.check_volume(user_id):
            alert_security_team(user_id, "High volume activity")

        # Generate response
        prediction = model.predict(query)

        # Add noise (for non-premium users)
        if tier != "premium":
            prediction = self.noise_injector.add_noise(prediction)

        # Watermark output
        response = self.watermarker.watermark(str(prediction), user_id)

        # Return only top prediction (no logits)
        return {"prediction": response}
```

---

## Related Patterns

- **[Threat Models](threat-models.md)** - Model extraction in ML/LLM threat taxonomy
- **[Governance Checklists](governance-checklists.md)** - IP protection and compliance
- **[Privacy Protection](privacy-protection.md)** - Watermarking for data provenance
- **[Incident Response](incident-response-playbooks.md)** - Responding to extraction attempts
