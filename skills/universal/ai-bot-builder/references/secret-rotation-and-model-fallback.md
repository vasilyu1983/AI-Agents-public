# Secret Rotation and Model Fallback

Use this reference when an always-on bot or voice agent must survive provider key rotation, provider outages, and model deprecations without dropping in-flight sessions or paging on-call at 3am.

Pair with [`production-deployment.md`](production-deployment.md), [`stateful-rollout-and-blue-green.md`](stateful-rollout-and-blue-green.md), and [`../../ai-voice-bots/references/production-deployment.md`](../../ai-voice-bots/references/production-deployment.md).

## Table of Contents

- [The Two Problems](#the-two-problems)
- [Secret Lifecycle](#secret-lifecycle)
- [Rotation Without Downtime](#rotation-without-downtime)
- [Secret Stores Compared](#secret-stores-compared)
- [Hot Reload Patterns](#hot-reload-patterns)
- [Multi-Provider Fallback Chain](#multi-provider-fallback-chain)
- [Capability Equivalence Matrix](#capability-equivalence-matrix)
- [Detecting Provider Degradation](#detecting-provider-degradation)
- [Model Deprecation Handling](#model-deprecation-handling)
- [Region Failover](#region-failover)
- [Auditing and Compliance](#auditing-and-compliance)
- [Pre-Production Checklist](#pre-production-checklist)
- [Common Failure Modes](#common-failure-modes)
- [Cross-References](#cross-references)

## The Two Problems

1. **Secret rotation**: provider API keys must be rotated periodically (security policy, leak response, vendor mandates). Naive rotation drops in-flight requests.
2. **Provider outage / degradation**: LLM providers have outages. Lasting 5–60 minutes is common; multi-hour incidents happen 2–4 times a year per provider. A bot that depends on one provider goes silent.

Both are solved by the same architectural pattern: **the provider layer is replaceable at runtime**.

## Secret Lifecycle

A provider secret moves through these states:

```text
created → active → rotating → retired → deleted
```

| State | Behaviour |
|---|---|
| **created** | Generated, not yet used |
| **active** | Used for new requests |
| **rotating** | Two secrets accepted; new requests use the newer one; old still valid |
| **retired** | Not used for new requests; can be revoked safely |
| **deleted** | Removed from secret store |

Rotation cadence in May 2026:

- Anthropic / OpenAI / Google production keys: every 90 days
- Compromise-response rotation: immediate
- Departing engineer: immediate
- Twilio / Telnyx (voice carriers): every 180 days

## Rotation Without Downtime

The pattern: **two-key window**. Both old and new keys are valid simultaneously for the duration of the rotation.

```text
T-0           T+1m           T+30m          T+60m
│             │              │              │
└─old active──┴─old + new────┴─new active───┴─old deleted
              ▲              ▲              ▲
              issue new      switch         revoke
              (both valid)   default        old
```

Implementation:

```python
class RotatingKeyClient:
    def __init__(self, secret_store):
        self.store = secret_store
        self.refresh_interval = 60  # seconds
        self._cache = {"primary": None, "secondary": None, "ts": 0}

    async def get_key(self) -> str:
        now = time.time()
        if now - self._cache["ts"] > self.refresh_interval:
            self._cache["primary"] = await self.store.get("anthropic_primary")
            self._cache["secondary"] = await self.store.get("anthropic_secondary")
            self._cache["ts"] = now
        return self._cache["primary"]

    async def call_with_failover(self, request):
        for key_name in ["primary", "secondary"]:
            try:
                return await call_anthropic(request, key=self._cache[key_name])
            except AuthError:
                continue  # try next key
        raise AuthError("all keys failed")
```

Operator workflow:

1. Issue new key in provider dashboard.
2. Write new key to secret store as `anthropic_primary`. Move old key to `anthropic_secondary`.
3. Wait for refresh interval × 2 (cache propagation).
4. Verify health metrics stable.
5. Revoke old key at provider.
6. Delete `anthropic_secondary` after 24h grace.

The total rotation takes minutes, not hours, with zero session loss.

## Secret Stores Compared

| Store | Hot reload | Audit | Best for |
|---|---|---|---|
| **HashiCorp Vault** | Yes (lease + watch) | Built-in | Enterprise, multi-cloud |
| **AWS Secrets Manager** | Yes (cached client) | CloudTrail | AWS stacks |
| **GCP Secret Manager** | Yes (Pub/Sub on rotation) | Cloud Audit Logs | GCP stacks |
| **Azure Key Vault** | Yes (event grid) | Azure Monitor | Azure stacks |
| **Doppler / Infisical / 1Password** | Webhook + SDK | Built-in | Cross-cloud, smaller teams |
| **Kubernetes Secrets** | No (requires pod restart unless via Reflector / External Secrets Operator) | k8s audit log | Bottom-tier only; use External Secrets to bridge |
| **Env vars** | No | None | Dev only |

If you cannot rotate without restarting pods, you are not in production. Move to a real secret store before going 24/7.

## Hot Reload Patterns

Three options, in preference order:

### Option 1 — TTL-based refresh

Client caches the secret with a short TTL (30–120 seconds) and refetches when stale. Simplest, lowest risk.

```python
class TTLSecret:
    def __init__(self, store, name, ttl=60):
        self.store, self.name, self.ttl = store, name, ttl
        self._value, self._fetched = None, 0

    async def value(self) -> str:
        if time.time() - self._fetched > self.ttl:
            self._value = await self.store.get(self.name)
            self._fetched = time.time()
        return self._value
```

### Option 2 — Push-based invalidation

Secret store sends an event (Pub/Sub, webhook, Vault watch) when the secret rotates. Pod invalidates cache on receipt.

```python
async def on_rotation_event(event):
    if event.secret_name == "anthropic_primary":
        secret_cache.invalidate("anthropic_primary")
        await secret_cache.refresh("anthropic_primary")
        log.info("rotated anthropic primary", new_version=event.version)
```

### Option 3 — Sidecar agent

Vault Agent / External Secrets Operator runs alongside the app pod, writes the current secret to a file the app watches. Decouples app from secret-store SDK.

```yaml
# k8s External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
spec:
  refreshInterval: 60s
  target:
    name: anthropic-keys
  data:
  - secretKey: ANTHROPIC_API_KEY_PRIMARY
    remoteRef:
      key: production/anthropic/primary
  - secretKey: ANTHROPIC_API_KEY_SECONDARY
    remoteRef:
      key: production/anthropic/secondary
```

App reads files via `fsnotify` or polls. Rotation never touches the app's secret-store credentials.

## Multi-Provider Fallback Chain

Provider outage handling: route through a fallback chain when the primary provider degrades.

```text
LLM request
   │
   ▼
┌──────────────────┐
│ Primary:         │ ── 5xx, timeout, rate-limited?
│  vendor A model  │
└────────┬─────────┘
         │ fail
         ▼
┌──────────────────┐
│ Fallback 1:      │ ── same error class?
│  same model via  │
│  a second host   │
└────────┬─────────┘
         │ fail
         ▼
┌──────────────────┐
│ Fallback 2:      │ ── same error class?
│  vendor B model  │
│  (capability     │
│   matched)       │
└────────┬─────────┘
         │ fail
         ▼
┌──────────────────┐
│ Degraded mode:   │
│  cached response │
│  / "try later"   │
└──────────────────┘
```

Rules:

- **Provider re-routing is per request, not per session.** Don't switch a session mid-conversation if you can help it; switch each request individually.
- **Same model across providers if possible.** The same model through a second host (for example, a cloud provider's model marketplace) behaves more like the direct API than a different vendor's model does.
- **Capability-matched fallback for the worst case.** When the model differs, mark the response as degraded.
- **Never silently degrade for safety-critical features.** A bot grounded in your KB should not fall back to a model that won't honor that grounding.

Implementation:

```python
class FailoverLLM:
    def __init__(self, chain: list[Provider]):
        self.chain = chain

    async def complete(self, request: Request) -> Response:
        last_error = None
        for provider in self.chain:
            try:
                if provider.circuit_breaker_open():
                    continue
                resp = await provider.call(request)
                if resp.ok:
                    return resp
                provider.record_failure()
            except (TimeoutError, ProviderError) as e:
                last_error = e
                provider.record_failure()
                continue
        raise AllProvidersDown(last_error)
```

Each provider tracks its own circuit breaker (open after N failures, half-open after cooldown). The chain skips open providers without trying them, saving latency.

## Capability Equivalence Matrix

Maintain a matrix of which features map across providers. Diverge at your peril.

| Capability | Anthropic | OpenAI | Bedrock (Anthropic) | Vertex (Anthropic) | GCP Gemini | Notes |
|---|---|---|---|---|---|---|
| Tool use | Yes | Yes | Yes | Yes | Yes | Schema differs; normalize before send |
| Streaming | SSE | SSE | SSE | SSE | SSE | Wrap in common interface |
| Vision | Yes | Yes | Yes | Yes | Yes | |
| Long context | 200k+ | 200k+ | Provider-cap | Provider-cap | 2M+ | Note: Gemini is the long-context outlier |
| Cache hits | Yes (prompt cache) | Yes | Yes (Bedrock prompt cache) | Yes | Limited | Cache key is provider-specific |
| Native function call schema | Anthropic JSON | OpenAI JSON | Anthropic JSON | Anthropic JSON | Vertex JSON | Differ; normalize |
| Refusal style | Polite explanation | Brief | Polite | Polite | Brief | Affects user perception |
| Cost | Provider pricing page | Provider pricing page | Model rate + Bedrock terms | Model rate + Vertex terms | Provider pricing page | Look up per-1M input/output rates for each fallback target on the day you configure the chain; the decision it feeds is whether a fallback hop changes cost enough to need its own budget alert. Flagship list prices have moved materially within a single year, so never carry a remembered number. |

For voice (STT/TTS), maintain a parallel matrix; Deepgram ↔ Whisper ↔ Anthropic Native, ElevenLabs ↔ Cartesia ↔ OpenAI TTS.

## Detecting Provider Degradation

Don't trust "the provider's status page" alone. Detect locally:

| Signal | Trigger | Action |
|---|---|---|
| Error rate spike | 5xx > 5% over 60s | Open circuit; route to fallback |
| Latency spike | p99 > 2x baseline over 5m | Warn; consider partial failover |
| 429 burst | rate-limit hits > 10/min | Backoff; throttle inputs |
| Specific error class | "model not available" | Immediate failover; alert engineering |
| Output regression | online eval drop > 10% | Pin to prior version or fallback |

Wire to a single "provider health" dashboard with one row per provider × region × model.

## Model Deprecation Handling

Providers deprecate models with notice (typically 6–12 months). Plan for this from day one.

Process:

1. Receive deprecation notice → file ticket with sunset date
2. Identify all uses of the deprecated model (search prompts, configs, hooks)
3. Pick replacement (vendor recommendation, or evaluate alternative)
4. Run eval suite against replacement
5. Canary the replacement (cohort, 1% → 100% over 14 days)
6. Update default; keep old as fallback for 30 days
7. Remove old model code path

Common pitfall: model deprecations that hit before you've finished migration. Always pin the exact model version string in config (e.g. an explicit dated/versioned ID from the provider's current model list), never a floating alias like `-latest` or `-default` — floating aliases mean your bot's behavior can change underneath you with no code change and no changelog entry.

## Region Failover

Multi-region deployment of an always-on bot needs region-aware secrets and provider routing.

```python
def provider_for_region(region: str) -> str:
    return {
        "us-east-1": "anthropic-direct",
        "eu-west-1": "bedrock-eu",  # data residency
        "ap-southeast-1": "bedrock-ap",
    }[region]
```

Rules:

- Secrets per region, not global
- Provider chain per region (US bot might fail over to GCP US; EU bot might not be allowed to)
- Region failover separate from provider failover; both must work

## Auditing and Compliance

Every secret operation must be auditable:

- Who issued / rotated / revoked
- When (UTC)
- From which IP
- What rotation type (scheduled, ad-hoc, compromise response)
- Old version → new version

Vault, AWS Secrets Manager, GCP Secret Manager produce this natively. Pipe to your audit log retention store.

For regulated firms (FCA, HIPAA, PCI):

- Quarterly access review of who has secret-store admin rights
- Annual penetration test that includes secret-store probing
- Documented incident response for suspected key compromise

## Pre-Production Checklist

- [ ] Production secrets in a real secret store (not env vars, not k8s Secret raw)
- [ ] Hot reload mechanism in place (TTL, push, or sidecar)
- [ ] Two-key window tested with a rehearsal rotation
- [ ] Provider fallback chain with at least one alternative per critical provider
- [ ] Capability equivalence matrix documented and kept current
- [ ] Circuit breaker per provider, tuned thresholds
- [ ] Local degradation detection wired to circuit breaker
- [ ] Model versions pinned (no `latest` aliases)
- [ ] Deprecation watch process documented
- [ ] Region failover tested if multi-region
- [ ] Audit logs piped to retention store
- [ ] Compromise-response runbook
- [ ] Game-day exercise: pull primary provider, verify graceful failover

## Common Failure Modes

| Failure | Symptom | Mitigation |
|---|---|---|
| **Restart-on-rotation** | Pods cycle every 90 days; sessions drop | Hot reload secret pattern |
| **Single-provider lock-in** | Provider outage = bot offline | Fallback chain |
| **`latest` model alias** | Silent quality change | Pin specific version |
| **Cache key collision across providers** | Wrong response served | Include provider in cache key |
| **Mid-session provider switch** | Tone or behavior shifts | Switch per request, not per session |
| **Untested fallback** | Fallback broken when needed | Game-day exercises |
| **Provider outage masked as our bug** | Pages on-call for upstream issue | Local provider health detection |
| **Slow deprecation migration** | Last-minute panic | Track deprecations as engineering work |
| **Region misrouting after failover** | Data residency violation | Per-region fallback chains |
| **Compromised key not revoked fast enough** | Bill spike, data exfiltration | Compromise-response runbook + automation |

## Cross-References

- [`production-deployment.md`](production-deployment.md) — base serving stack
- [`stateful-rollout-and-blue-green.md`](stateful-rollout-and-blue-green.md) — rollout strategy
- [`testing-and-production.md`](testing-and-production.md) — eval gates
- [`../../ai-voice-bots/references/production-deployment.md`](../../ai-voice-bots/references/production-deployment.md) — voice provider failover
- [`../../ai-agents/references/24-7-operating-model.md`](../../ai-agents/references/24-7-operating-model.md) — SLOs and oncall
- [`../../ai-agents/references/evaluation-and-observability.md`](../../ai-agents/references/evaluation-and-observability.md) — health detection
- [`../../ai-coding-agents-provider-runtime/SKILL.md`](../../ai-coding-agents-provider-runtime/SKILL.md) — provider abstraction patterns
- [`../../ai-llm-inference/SKILL.md`](../../ai-llm-inference/SKILL.md) — inference cost and capability tradeoffs
- [`../../software-security-appsec/SKILL.md`](../../software-security-appsec/SKILL.md) — secret hygiene
