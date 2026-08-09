# Mechanism: Rate Limiting and Token Bucket

**Sources**: Tanenbaum & Wetherall, *Computer Networks* 5th ed., Ch. 5 (2010). Varghese, G. (2004), *Network Algorithmics*, Ch. 4. Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 7. Turner (1986), "New directions in communications," IEEE Communications Magazine.

## Definition

**Rate limiting** is admission control: enforcing a maximum throughput to protect a resource from overload. The **token bucket** is the canonical algorithm — it allows controlled bursting while enforcing a long-run average rate.

**Token Bucket algorithm**:

```
State: bucket_tokens (current tokens), bucket_capacity (maximum tokens)
Parameters: fill_rate r (tokens/second), capacity b (burst size)

On each time step dt:
  bucket_tokens = min(bucket_capacity, bucket_tokens + r·dt)

On each request of size s:
  if bucket_tokens >= s:
    bucket_tokens -= s
    admit request
  else:
    reject (or queue) request
```

**Leaky Bucket** variant: enforces a strictly constant output rate regardless of burst. Output drains at a fixed rate; input fills a finite queue. If queue is full, packets are dropped.

```
Leaky Bucket vs. Token Bucket:
  Token Bucket: admits bursts up to capacity b; smooths long-run average to r
  Leaky Bucket: smooths output strictly to r; no bursting allowed
```

**Relationship to control theory**: The token bucket is a discrete integrator with saturation. The fill rate `r` is the "setpoint" for average throughput. The bucket level is the integrator state. Overflow is analogous to actuator saturation.

## When to Use

- Protecting a downstream API or service from overload.
- Admitting requests at a controlled rate while allowing short bursts.
- LLM API calls per minute: fill rate = RPM limit; burst = short spike accommodation.
- Agent tool-call rate limiting: tokens per step; refill per time window.
- Retry backoff: treat retry budget as a token bucket; exhausted → fail open.
- Database connection pool admission.

**Choose Token Bucket when**: bursty traffic is expected and tolerable up to a limit.
**Choose Leaky Bucket when**: downstream requires strictly smooth input (e.g., video streaming, payment processor with no burst tolerance).

## Inputs

| Input | Description |
|-------|-------------|
| Fill rate `r` | Tokens added per second (= desired average throughput) |
| Bucket capacity `b` | Maximum burst size in tokens |
| Request cost `s` | Tokens consumed per request (usually 1; can vary by request type) |
| Arrival pattern | Bursty or smooth traffic |

## Outputs

| Output | Description |
|--------|-------------|
| Admission decision | Admit or reject/queue the incoming request |
| Bucket level | Current token count (remaining burst capacity) |
| Wait time | If queuing: how long until tokens are available |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Burst rejection at startup | Bucket starts empty | Initialize bucket to capacity on startup |
| Retry storm after rejection | Rejected requests all retry immediately | Add jitter to retry delay; use exponential backoff |
| Rate too conservative | r set too low for actual workload | Profile actual request rate; tune r to 90th percentile sustained rate |
| Rate too permissive | r too high; downstream still overloaded | Add backpressure signal ([10-circuit-breaker-backpressure.md](10-circuit-breaker-backpressure.md)); reduce r |
| Bucket refills while system is recovering | Fill continues during circuit-open period | Pause token fill when circuit breaker is OPEN |
| Request weighting ignored | All requests cost 1 token regardless of load | Use cost-based tokens (e.g., weight by expected compute cost) |

## Worked Example: LLM API Rate Limiting

**Problem**: LLM API allows 60 requests/minute (1 req/sec). Agent workflow makes burst calls for parallel tool use — up to 5 simultaneous calls.

```
Token Bucket configuration:
  r = 1 token/second    (60 req/min average rate)
  b = 5 tokens          (burst capacity for parallel calls)

Startup: bucket = 5 tokens (full).

t=0: parallel tool calls = 5 → consume 5 tokens → bucket = 0
t=1: bucket refills to 1 → 1 sequential call allowed
t=2: bucket = 2 → 2 parallel calls allowed
...
t=5: bucket = 5 → parallel burst allowed again

Without token bucket: 10 parallel calls at t=0 → API rate limit error (429) → retry storm.
With token bucket: admits 5 now, queues remainder → no 429 errors.
```

**Retry with jitter**:
```python
def retry_delay(attempt):
    base = 1.0  # seconds
    cap = 60.0
    return min(cap, base * 2**attempt) + random.uniform(0, 1)
```

## Sources

- Turner (1986), IEEE Communications Magazine 24(10):2-9.
- Varghese (2004), *Network Algorithmics*, Ch. 4. Morgan Kaufmann.
- Tanenbaum & Wetherall, *Computer Networks*, 5th ed., Ch. 5.
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 7.
