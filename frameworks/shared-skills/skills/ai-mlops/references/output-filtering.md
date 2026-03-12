# Model Output Filtering

Operational patterns for filtering and validating LLM/ML model outputs to prevent unsafe, harmful, or policy-violating content from reaching users.

---

## Overview

Output filtering is the **last line of defense** before content reaches users. Even with strong input guardrails and safety alignment, models can still produce:

- NSFW or explicit content
- Violence or hate speech
- PII leakage (SSN, credit cards, API keys)
- Harmful instructions (weapons, drugs, self-harm)
- Jailbreak attempts that succeeded
- Hallucinated or ungrounded claims

This guide covers **multi-layer output filtering** using classifiers, rules, LLM-based post-filters, and scoring thresholds.

---

## Defense Layers

### Layer 1: Classifier Gate

**Use safety classifiers to detect unsafe content before serving:**

```python
from transformers import pipeline

class SafetyClassifier:
    def __init__(self):
        # Load pre-trained safety classifier
        self.classifier = pipeline(
            "text-classification",
            model="microsoft/deberta-large-mnli",
            device=0
        )

        # Safety categories
        self.unsafe_categories = [
            "nsfw",
            "violence",
            "hate_speech",
            "self_harm",
            "dangerous_instructions"
        ]

    def classify(self, text: str) -> dict:
        """Classify text across safety categories."""
        results = {}

        for category in self.unsafe_categories:
            # Zero-shot classification
            result = self.classifier(
                text,
                candidate_labels=[category, "safe"]
            )

            # Extract score for unsafe category
            unsafe_score = [
                r["score"] for r in result
                if r["label"] == category
            ][0]

            results[category] = unsafe_score

        return results

    def is_safe(self, text: str, threshold: float = 0.8) -> bool:
        """Return True if text is safe, False otherwise."""
        scores = self.classify(text)

        for category, score in scores.items():
            if score > threshold:
                logger.warning(f"Unsafe content detected: {category} ({score:.2f})")
                return False

        return True
```

**Example usage:**
```python
safety = SafetyClassifier()

response = llm.generate(prompt)

if not safety.is_safe(response):
    response = "I cannot provide that information."
```

**Specialized classifiers:**
- **OpenAI Moderation API** - NSFW, hate, violence, self-harm
- **Perspective API** - Toxicity, profanity, identity attacks
- **Azure Content Safety** - Multi-category safety scoring
- **Llama Guard 2** - Policy-based content moderation

**Checklist:**
- [ ] Safety classifier deployed (OpenAI Moderation, Perspective, Azure)
- [ ] Multiple safety categories covered (NSFW, hate, violence, PII)
- [ ] Threshold configured (typically 0.8 for high precision)
- [ ] Unsafe outputs blocked before serving

---

### Layer 2: Rule-Based Filtering

**Regex and pattern-based filters for specific unsafe content:**

```python
import re

class RuleBasedFilter:
    def __init__(self):
        # Patterns for PII
        self.pii_patterns = {
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "api_key": r'\b[A-Za-z0-9]{32,}\b'  # Generic API key pattern
        }

        # Slurs and hate speech (use curated lists)
        self.banned_words = self.load_banned_words()

    def load_banned_words(self) -> set:
        """Load list of banned words from file."""
        with open("banned_words.txt") as f:
            return set(line.strip().lower() for line in f)

    def contains_pii(self, text: str) -> bool:
        """Check if text contains PII."""
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, text):
                logger.warning(f"PII detected: {pii_type}")
                return True
        return False

    def contains_banned_words(self, text: str) -> bool:
        """Check if text contains banned words."""
        text_lower = text.lower()
        for word in self.banned_words:
            if word in text_lower:
                logger.warning(f"Banned word detected: {word}")
                return True
        return False

    def is_safe(self, text: str) -> bool:
        """Return True if text passes all rule checks."""
        if self.contains_pii(text):
            return False
        if self.contains_banned_words(text):
            return False
        return True
```

**Metadata-based rules:**
```python
def check_metadata_rules(response: str, metadata: dict) -> bool:
    """Apply metadata-based filtering rules."""

    # Block responses from certain sources
    blocked_sources = ["untrusted.com", "spam.com"]
    if metadata.get("source") in blocked_sources:
        return False

    # Block old content (>2 years)
    from datetime import datetime, timedelta
    timestamp = datetime.fromisoformat(metadata.get("timestamp", "1970-01-01"))
    if datetime.now() - timestamp > timedelta(days=730):
        return False

    return True
```

**Checklist:**
- [ ] PII regex patterns configured (SSN, credit cards, emails, phones)
- [ ] Banned words list loaded and maintained
- [ ] API key and secret detection active
- [ ] Metadata-based rules enforced

---

### Layer 3: LLM-Based Post-Filter or Rewriter

**Use a lightweight LLM to rewrite or decline unsafe content:**

```python
class LLMPostFilter:
    def __init__(self):
        self.filter_llm = LLM(model="gpt-3.5-turbo")

    def rewrite_if_unsafe(self, response: str) -> str:
        """Use LLM to detect and rewrite unsafe content."""
        prompt = f"""
You are a safety filter. Review the following response and determine if it contains:
- NSFW content
- Hate speech or violence
- PII (SSN, credit cards, emails)
- Harmful instructions

If unsafe, rewrite it to be safe. If safe, return "SAFE".

Response:
{response}

Your output:
"""
        result = self.filter_llm.generate(prompt)

        if result.strip() == "SAFE":
            return response
        else:
            logger.info("Response rewritten by LLM filter")
            return result

    def should_decline(self, response: str) -> bool:
        """Use LLM to determine if response should be declined."""
        prompt = f"""
Is the following response unsafe or harmful? Answer YES or NO.

Response:
{response}

Answer:
"""
        result = self.filter_llm.generate(prompt).strip().upper()
        return result == "YES"
```

**When to use:**
- Borderline cases where classifiers are uncertain
- Rephrasing unsafe content to safe alternatives
- Handling context-dependent safety (what's safe in one context may not be in another)

**Checklist:**
- [ ] LLM post-filter configured for borderline cases
- [ ] Rewriting prompt tested and validated
- [ ] Decline threshold configured
- [ ] Logging for post-filter decisions

---

### Layer 4: Scoring & Thresholds

**Combine multiple signals into a safety score:**

```python
class SafetyScorer:
    def __init__(self):
        self.classifier = SafetyClassifier()
        self.rule_filter = RuleBasedFilter()
        self.llm_filter = LLMPostFilter()

    def compute_safety_score(self, text: str) -> float:
        """Compute composite safety score (0.0 = unsafe, 1.0 = safe)."""
        scores = []

        # Classifier score
        classifier_results = self.classifier.classify(text)
        classifier_safe = all(score < 0.8 for score in classifier_results.values())
        scores.append(1.0 if classifier_safe else 0.0)

        # Rule-based score
        rule_safe = self.rule_filter.is_safe(text)
        scores.append(1.0 if rule_safe else 0.0)

        # LLM filter score (optional, slower)
        # llm_safe = not self.llm_filter.should_decline(text)
        # scores.append(1.0 if llm_safe else 0.0)

        # Weighted average
        return sum(scores) / len(scores)

    def should_serve(self, text: str, threshold: float = 0.9) -> bool:
        """Return True if safety score exceeds threshold."""
        score = self.compute_safety_score(text)

        if score < threshold:
            logger.warning(f"Low safety score: {score:.2f}")
            return False

        return True
```

**Escalation for low confidence:**
```python
def serve_with_escalation(response: str, scorer: SafetyScorer) -> str:
    """Serve response or escalate to human review."""
    score = scorer.compute_safety_score(response)

    if score >= 0.9:
        # High confidence: safe
        return response
    elif score >= 0.7:
        # Medium confidence: escalate to human review
        logger.info("Escalating to human review")
        enqueue_for_review(response)
        return "Your request is being reviewed. Please check back later."
    else:
        # Low confidence: block
        return "I cannot provide that information."
```

**Checklist:**
- [ ] Composite safety score implemented
- [ ] Threshold configured (typically 0.9 for production)
- [ ] Escalation path for borderline cases
- [ ] Logging and monitoring active

---

## Output Filtering Checklist

**Classifier Gate:**
- [ ] Safety classifier deployed (OpenAI, Perspective, Azure, Llama Guard)
- [ ] Multiple categories covered (NSFW, hate, violence, self-harm, PII)
- [ ] Threshold configured and tested
- [ ] Unsafe outputs blocked before serving

**Rule-Based Filtering:**
- [ ] PII detection regex patterns configured
- [ ] Banned words list loaded and maintained
- [ ] API key and secret detection active
- [ ] Metadata-based rules enforced

**LLM Post-Filter:**
- [ ] LLM rewriter configured for borderline cases
- [ ] Decline logic tested
- [ ] Rewriting prompt validated
- [ ] Logging for post-filter decisions

**Scoring & Thresholds:**
- [ ] Composite safety score implemented
- [ ] Threshold set (0.9 recommended for production)
- [ ] Escalation path configured for medium-confidence cases
- [ ] Monitoring and alerting active

**Operational:**
- [ ] All unsafe outputs logged with category and score
- [ ] Human review queue established for escalations
- [ ] False positive rate monitored (<1% target)
- [ ] Filter performance reviewed weekly

---

## Real-World Example: Multi-Layer Output Filter

```python
class ProductionOutputFilter:
    def __init__(self):
        self.safety_classifier = SafetyClassifier()
        self.rule_filter = RuleBasedFilter()
        self.llm_rewriter = LLMPostFilter()
        self.scorer = SafetyScorer()

    def filter_response(self, response: str) -> str:
        """Multi-layer output filtering pipeline."""

        # Layer 1: Classifier gate
        if not self.safety_classifier.is_safe(response, threshold=0.8):
            logger.warning("Blocked by safety classifier")
            return self.refusal_message("safety")

        # Layer 2: Rule-based filtering
        if not self.rule_filter.is_safe(response):
            logger.warning("Blocked by rule filter (PII or banned words)")
            return self.refusal_message("policy")

        # Layer 3: LLM rewriter for borderline cases
        safety_score = self.scorer.compute_safety_score(response)

        if 0.7 <= safety_score < 0.9:
            logger.info("Rewriting borderline response")
            response = self.llm_rewriter.rewrite_if_unsafe(response)

        # Layer 4: Final scoring
        if not self.scorer.should_serve(response, threshold=0.9):
            logger.warning("Blocked by final safety score")
            return self.refusal_message("safety")

        # All checks passed
        return response

    def refusal_message(self, reason: str) -> str:
        """Generate refusal message based on reason."""
        templates = {
            "safety": "I cannot provide that information as it may be unsafe.",
            "policy": "I cannot assist with that request due to policy restrictions.",
            "pii": "I cannot share personal information."
        }
        return templates.get(reason, "I cannot help with that request.")
```

---

## Related Patterns

- **[Jailbreak Defense](jailbreak-defense.md)** - Preventing safety bypass attempts
- **[Privacy Protection](privacy-protection.md)** - PII detection and redaction
- **[RAG Security](rag-security.md)** - Grounding validation for RAG outputs
- **[Safety Evaluation](safety-evaluation.md)** - Testing output filters with adversarial prompts
