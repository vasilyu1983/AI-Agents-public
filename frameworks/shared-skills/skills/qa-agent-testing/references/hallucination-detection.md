# Hallucination Detection

Methods for detecting, measuring, and preventing AI agent hallucinations across factual accuracy, faithfulness, and fabrication dimensions.

---

## Contents

- [Hallucination Taxonomy](#hallucination-taxonomy)
- [Detection Methods](#detection-methods)
- [Grounding Verification](#grounding-verification)
- [Measurement Metrics](#measurement-metrics)
- [Automated Detection Pipelines](#automated-detection-pipelines)
- [LLM-as-Judge for Hallucination](#llm-as-judge-for-hallucination)
- [Dataset Design for Benchmarking](#dataset-design-for-benchmarking)
- [Known Failure Patterns](#known-failure-patterns)
- [Production Monitoring](#production-monitoring)
- [Detection Checklist](#detection-checklist)
- [Related Resources](#related-resources)

---

## Hallucination Taxonomy

| Type | Definition | Example | Detection Difficulty |
|------|-----------|---------|---------------------|
| Factual hallucination | States incorrect real-world facts | "Python was created in 2001" (actually 1991) | Medium - verifiable against sources |
| Faithfulness hallucination | Contradicts provided context/documents | Summary includes claims absent from source text | Medium - compare against source |
| Fabrication | Invents entities, citations, or data | "According to Smith et al. (2023)..." (paper does not exist) | Hard - requires existence verification |
| Intrinsic hallucination | Contradicts the source material | "Revenue grew 20%" when source says "declined 5%" | Medium - entailment check |
| Extrinsic hallucination | Adds unsupported information | Includes plausible but ungrounded statistics | Hard - absence proof |
| Reasoning hallucination | Logical steps are invalid | Correct premises but wrong conclusion | Hard - requires logic verification |

### Severity Levels

```text
CRITICAL:  Medical, legal, financial facts wrong
           - Incorrect drug dosages, case citations, tax rates
HIGH:      Fabricated sources or data presented as factual
           - Non-existent papers, fake statistics
MEDIUM:    Unfaithful summary or context distortion
           - Paraphrase changes meaning
LOW:       Minor factual imprecision
           - Approximate dates, rounded numbers
INFO:      Hedged or qualified uncertain claims
           - "Approximately", "as of my last update"
```

---

## Detection Methods

### Method 1: Reference-Based Detection

Compare agent output against a known-correct reference.

```python
from typing import NamedTuple

class FactCheck(NamedTuple):
    claim: str
    reference: str
    is_supported: bool
    confidence: float

def reference_based_check(
    output: str,
    reference_text: str,
    claim_extractor,
    entailment_model,
) -> list[FactCheck]:
    """Check each claim in output against reference material."""
    claims = claim_extractor.extract(output)
    results = []

    for claim in claims:
        entailment = entailment_model.check(
            premise=reference_text,
            hypothesis=claim,
        )
        results.append(FactCheck(
            claim=claim,
            reference=reference_text[:200],
            is_supported=entailment.label == "entailment",
            confidence=entailment.score,
        ))
    return results
```

### Method 2: Reference-Free Detection

Detect hallucinations without ground truth using self-consistency.

```python
def self_consistency_check(agent_client, query: str, n_samples: int = 5):
    """
    Generate multiple responses and check for contradictions.
    Inconsistent claims across samples indicate hallucination risk.
    """
    responses = []
    for i in range(n_samples):
        response = agent_client.send_message(
            query, temperature=0.7, seed=i
        )
        responses.append(response.text)

    # Extract claims from each response
    all_claims = [extract_claims(r) for r in responses]

    # Find claims that appear in fewer than majority of responses
    claim_frequency = {}
    for claims in all_claims:
        for claim in claims:
            normalized = normalize_claim(claim)
            claim_frequency[normalized] = claim_frequency.get(normalized, 0) + 1

    inconsistent = [
        claim for claim, count in claim_frequency.items()
        if count < n_samples * 0.6  # Appears in fewer than 60% of samples
    ]
    return {
        "consistent_claims": len(claim_frequency) - len(inconsistent),
        "inconsistent_claims": len(inconsistent),
        "hallucination_risk": len(inconsistent) / max(len(claim_frequency), 1),
        "flagged": inconsistent,
    }
```

### Method 3: Entailment-Based Detection

```python
from transformers import pipeline

nli_model = pipeline(
    "text-classification",
    model="microsoft/deberta-v2-xlarge-mnli",
)

def entailment_check(premise: str, hypothesis: str) -> dict:
    """
    Check if premise entails, contradicts, or is neutral to hypothesis.
    """
    result = nli_model(f"{premise} [SEP] {hypothesis}")[0]
    return {
        "label": result["label"],       # entailment, contradiction, neutral
        "score": result["score"],
        "is_hallucination": result["label"] == "contradiction",
    }

# Usage: check if agent output is faithful to source
source = "Company revenue was $50M, down 5% from last year."
output_claim = "Revenue grew by 5% to reach $50M."
result = entailment_check(source, output_claim)
# result: {"label": "contradiction", "score": 0.97, "is_hallucination": True}
```

---

## Grounding Verification

### Citation Accuracy Testing

```python
def verify_citations(output: str, available_sources: list[dict]) -> dict:
    """Verify that citations in agent output are accurate."""
    citations = extract_citations(output)
    results = {
        "total_citations": len(citations),
        "verified": 0,
        "fabricated": 0,
        "misattributed": 0,
        "details": [],
    }

    for citation in citations:
        # Check if cited source exists
        source = find_source(citation.reference, available_sources)
        if source is None:
            results["fabricated"] += 1
            results["details"].append({
                "citation": citation.text,
                "status": "FABRICATED",
                "reason": "Source does not exist in available materials",
            })
            continue

        # Check if claim matches source content
        entailment = entailment_check(
            premise=source["content"],
            hypothesis=citation.claim,
        )
        if entailment["is_hallucination"]:
            results["misattributed"] += 1
            results["details"].append({
                "citation": citation.text,
                "status": "MISATTRIBUTED",
                "reason": "Claim contradicts the cited source",
            })
        else:
            results["verified"] += 1
            results["details"].append({
                "citation": citation.text,
                "status": "VERIFIED",
            })

    return results
```

### Source Attribution Matrix

| Attribution Type | What to Verify | Test Approach |
|-----------------|----------------|---------------|
| Direct quote | Exact text exists in source | String matching |
| Paraphrase | Meaning preserved from source | Entailment model |
| Statistic | Number matches source data | Numeric extraction + comparison |
| Named entity | Person/org/place exists and is correct | Entity lookup |
| URL/link | URL is valid and content matches claim | HTTP check + content compare |
| Date/time | Temporal claim is accurate | Date extraction + validation |

---

## Measurement Metrics

### Core Metrics

| Metric | Formula | Target | Use Case |
|--------|---------|--------|----------|
| Hallucination Rate | Hallucinated claims / Total claims | < 5% | Overall quality |
| Factual Accuracy Score | Correct facts / Total factual claims | > 95% | Fact-critical domains |
| Faithfulness Score | Supported claims / Total claims (given context) | > 90% | RAG systems |
| Citation Precision | Correct citations / Total citations | > 95% | Research tasks |
| Fabrication Rate | Fabricated entities / Total entities mentioned | < 2% | Any generation |

### Computing Hallucination Rate

```python
def compute_hallucination_rate(
    eval_results: list[dict],
) -> dict:
    """Compute hallucination metrics from evaluation results."""
    total_claims = 0
    hallucinated_claims = 0
    by_category = {}

    for result in eval_results:
        for claim in result["claims"]:
            total_claims += 1
            category = claim["type"]
            by_category.setdefault(category, {"total": 0, "hallucinated": 0})
            by_category[category]["total"] += 1

            if not claim["is_supported"]:
                hallucinated_claims += 1
                by_category[category]["hallucinated"] += 1

    overall_rate = hallucinated_claims / max(total_claims, 1)
    category_rates = {
        cat: d["hallucinated"] / max(d["total"], 1)
        for cat, d in by_category.items()
    }

    return {
        "overall_hallucination_rate": round(overall_rate, 4),
        "total_claims_evaluated": total_claims,
        "hallucinated_claims": hallucinated_claims,
        "by_category": category_rates,
        "passes_threshold": overall_rate < 0.05,
    }
```

---

## Automated Detection Pipelines

### End-to-End Detection Pipeline

```python
from dataclasses import dataclass, field

@dataclass
class HallucinationReport:
    query: str
    agent_response: str
    claims: list[dict] = field(default_factory=list)
    hallucination_rate: float = 0.0
    flagged_claims: list[str] = field(default_factory=list)

class HallucinationDetector:
    def __init__(self, claim_extractor, entailment_model, fact_checker):
        self.claim_extractor = claim_extractor
        self.entailment_model = entailment_model
        self.fact_checker = fact_checker

    def evaluate(
        self, query: str, response: str, context: str = None
    ) -> HallucinationReport:
        """Full hallucination evaluation pipeline."""
        report = HallucinationReport(query=query, agent_response=response)

        # Step 1: Extract atomic claims
        claims = self.claim_extractor.extract(response)

        # Step 2: Check each claim
        for claim in claims:
            result = {"text": claim, "checks": []}

            # Faithfulness check (if context provided)
            if context:
                entailment = self.entailment_model.check(context, claim)
                result["checks"].append({
                    "type": "faithfulness",
                    "supported": entailment.label == "entailment",
                    "score": entailment.score,
                })

            # Factual check (external knowledge)
            fact_result = self.fact_checker.verify(claim)
            result["checks"].append({
                "type": "factual",
                "supported": fact_result.is_correct,
                "score": fact_result.confidence,
            })

            is_hallucinated = any(
                not c["supported"] and c["score"] > 0.8
                for c in result["checks"]
            )
            result["is_hallucinated"] = is_hallucinated
            report.claims.append(result)

            if is_hallucinated:
                report.flagged_claims.append(claim)

        total = len(report.claims)
        flagged = len(report.flagged_claims)
        report.hallucination_rate = flagged / max(total, 1)
        return report
```

### CI Integration

```bash
#!/bin/bash
# run_hallucination_eval.sh - CI pipeline step

set -euo pipefail

EVAL_DATASET="tests/eval/hallucination_golden_set.jsonl"
THRESHOLD=0.05
OUTPUT="reports/hallucination_eval.json"

echo "Running hallucination evaluation..."
python -m eval.hallucination_detector \
    --dataset "$EVAL_DATASET" \
    --output "$OUTPUT" \
    --threshold "$THRESHOLD"

# Parse results
RATE=$(jq -r '.overall_hallucination_rate' "$OUTPUT")
PASSES=$(jq -r '.passes_threshold' "$OUTPUT")

echo "Hallucination rate: $RATE (threshold: $THRESHOLD)"

if [ "$PASSES" != "true" ]; then
    echo "FAIL: Hallucination rate exceeds threshold"
    jq '.flagged_claims' "$OUTPUT"
    exit 1
fi

echo "PASS: Hallucination rate within acceptable range"
```

---

## LLM-as-Judge for Hallucination

### Judge Prompt Template

```python
HALLUCINATION_JUDGE_PROMPT = """You are a hallucination detection judge.

Given:
- CONTEXT: The source material provided to the agent
- QUERY: The user's question
- RESPONSE: The agent's response

Evaluate each factual claim in RESPONSE for:
1. SUPPORTED - Claim is directly supported by CONTEXT
2. NOT_SUPPORTED - Claim cannot be verified from CONTEXT (but may be true)
3. CONTRADICTED - Claim directly contradicts CONTEXT

Output format (JSON):
{{
  "claims": [
    {{
      "claim": "<extracted claim>",
      "verdict": "SUPPORTED|NOT_SUPPORTED|CONTRADICTED",
      "evidence": "<quote from context or 'no evidence found'>",
      "reasoning": "<brief explanation>"
    }}
  ],
  "summary": {{
    "total_claims": <int>,
    "supported": <int>,
    "not_supported": <int>,
    "contradicted": <int>,
    "faithfulness_score": <float 0-1>
  }}
}}

CONTEXT:
{context}

QUERY:
{query}

RESPONSE:
{response}
"""

def llm_judge_hallucination(
    judge_client, context: str, query: str, response: str
) -> dict:
    """Use an LLM judge to evaluate hallucination."""
    prompt = HALLUCINATION_JUDGE_PROMPT.format(
        context=context, query=query, response=response
    )
    result = judge_client.generate(prompt, temperature=0.0)
    return json.loads(result.text)
```

### Judge Calibration

| Judge Configuration | Precision | Recall | Cost | Speed |
|--------------------|-----------|--------|------|-------|
| GPT-4 single pass | 0.85 | 0.78 | High | Slow |
| GPT-4 with chain-of-thought | 0.91 | 0.83 | High | Slow |
| Claude 3.5 Sonnet | 0.87 | 0.81 | Medium | Medium |
| Panel of 3 judges (majority vote) | 0.93 | 0.85 | 3x | 3x |
| NLI model + LLM judge ensemble | 0.94 | 0.88 | Medium | Medium |

**Recommendation:** Use NLI model for cheap first-pass filtering, then LLM judge for ambiguous cases.

---

## Dataset Design for Benchmarking

### Golden Set Structure

```json
{
  "id": "halluc_eval_042",
  "query": "What was Apple's revenue in Q3 2024?",
  "context": "Apple reported Q3 2024 revenue of $85.8 billion...",
  "reference_answer": "Apple's Q3 2024 revenue was $85.8 billion.",
  "claims": [
    {
      "text": "Apple's Q3 2024 revenue was $85.8 billion",
      "is_supported": true,
      "type": "factual"
    }
  ],
  "known_hallucination_traps": [
    "Confusing Q3 with Q2 ($81.8B)",
    "Using 2023 Q3 figure ($81.8B) instead of 2024",
    "Fabricating growth percentage"
  ],
  "difficulty": "medium",
  "domain": "finance"
}
```

### Dataset Composition

| Category | Percentage | Purpose |
|----------|-----------|---------|
| Factual questions with clear answers | 30% | Baseline accuracy |
| Summarization with source text | 25% | Faithfulness testing |
| Questions requiring "I don't know" | 15% | Abstention calibration |
| Adversarial (designed to trigger hallucination) | 15% | Stress testing |
| Multi-hop reasoning | 10% | Reasoning hallucination |
| Citation-required tasks | 5% | Attribution accuracy |

---

## Known Failure Patterns

### Pattern 1: Confident Fabrication

```text
TRIGGER: Agent asked about obscure topic with sparse training data
SYMPTOM: Fluent, confident response with entirely fabricated details
EXAMPLE: "The 1987 Lisbon Protocol on marine conservation established..."
         (No such protocol exists)
DETECTION: Entity existence verification
MITIGATION: Calibrate confidence, train to say "I'm not sure"
```

### Pattern 2: Numeric Drift

```text
TRIGGER: Agent paraphrases text containing numbers
SYMPTOM: Numbers slightly altered (rounding, transposition)
EXAMPLE: Source says "23.7%" → Agent says "27.3%"
DETECTION: Numeric extraction and comparison
MITIGATION: Instruct to quote numbers exactly from source
```

### Pattern 3: Temporal Confusion

```text
TRIGGER: Multiple time periods discussed in context
SYMPTOM: Attributes data from one period to another
EXAMPLE: "2024 revenue" using 2023 figures
DETECTION: Temporal entity extraction + cross-reference
MITIGATION: Explicit date anchoring in prompts
```

### Pattern 4: Source Blending

```text
TRIGGER: Multiple documents in RAG context
SYMPTOM: Combines facts from different sources into false composite
EXAMPLE: Merges Company A's revenue with Company B's growth rate
DETECTION: Per-source faithfulness checking
MITIGATION: Source-aware retrieval, attribution requirements
```

---

## Production Monitoring

### Key Signals to Track

- [ ] Hallucination rate by query category (dashboard metric)
- [ ] Citation verification failure rate (weekly trend)
- [ ] Self-consistency score distribution (anomaly detection)
- [ ] User-reported inaccuracy rate (feedback loop)
- [ ] Abstention rate -- too low may indicate overconfidence

### Alerting Thresholds

```python
HALLUCINATION_ALERTS = {
    "overall_rate": {"warn": 0.05, "critical": 0.10},
    "fabrication_rate": {"warn": 0.02, "critical": 0.05},
    "citation_failure_rate": {"warn": 0.05, "critical": 0.15},
    "confidence_without_source": {"warn": 0.10, "critical": 0.20},
}
```

---

## Detection Checklist

- [ ] Hallucination taxonomy defined for your domain
- [ ] Reference-based detection implemented for RAG outputs
- [ ] Self-consistency checks running for open-ended queries
- [ ] Entailment model integrated for faithfulness scoring
- [ ] LLM judge configured and calibrated against human labels
- [ ] Golden evaluation dataset created (100+ examples minimum)
- [ ] Metrics computed: hallucination rate, faithfulness score, citation precision
- [ ] CI pipeline runs hallucination eval on model/prompt changes
- [ ] Production monitoring tracks hallucination rate trends
- [ ] Known failure patterns documented and tested for
- [ ] Abstention behavior calibrated (agent says "I don't know" when appropriate)

---

## Related Resources

- **[prompt-injection-testing.md](prompt-injection-testing.md)** - Security testing for adversarial inputs
- **[scoring-rubric.md](scoring-rubric.md)** - Rubric design for evaluation
- **[llm-judge-limitations.md](llm-judge-limitations.md)** - Known limitations of LLM-as-judge
- **[test-case-design.md](test-case-design.md)** - Designing evaluation test cases
- **[eval-dataset-design.md](eval-dataset-design.md)** - Building representative eval datasets
- **[SKILL.md](../SKILL.md)** - QA Agent Testing skill overview
