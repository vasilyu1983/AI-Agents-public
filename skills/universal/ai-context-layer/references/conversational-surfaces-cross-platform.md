# Natural Conversational Surfaces — Cross-Platform Composition

How to ship a conversational experience that feels like talking to a real person, across **iOS / Android / web browser / messaging bots (Telegram, Discord, WhatsApp, Slack) / voice / backend API**, with or without an on-device model. The composition skeleton is identical across platforms; only the *composer* changes.

This reference is platform-neutral. For the iOS-specific deep dive (Apple Foundation Models, `@Generable`, sqlite-vec on-device), see [`software-ios-ai-engine/references/composition-with-rag-context-vector.md`](../../software-ios-ai-engine/references/composition-with-rag-context-vector.md).

## Contents

- [The Universal Composition Skeleton](#the-universal-composition-skeleton)
- [The Composer Matrix](#the-composer-matrix)
- [Three Generic Domain Scenarios, Across Platforms](#three-generic-domain-scenarios-across-platforms)
- [ASCII Flow — A Single Turn, End to End](#ascii-flow--a-single-turn-end-to-end)
- [ASCII Flow — Composer Fallback Chain per Platform](#ascii-flow--composer-fallback-chain-per-platform)
- [ASCII Flow — Three Scenarios Mapped to Skill Chain](#ascii-flow--three-scenarios-mapped-to-skill-chain)
- [ASCII Flow — Cross-Surface Signal Propagation](#ascii-flow--cross-surface-signal-propagation)
- [ASCII Flow — EvidenceBundle Schema Mirroring per Language](#ascii-flow--evidencebundle-schema-mirroring-per-language)
- [Per-Platform Composer Notes](#per-platform-composer-notes)
- [Cross-Platform Patterns](#cross-platform-patterns)
- [Anti-Patterns Specific to Cross-Platform Composition](#anti-patterns-specific-to-cross-platform-composition)
- [Verification Gate for Cross-Platform Conversational Builds](#verification-gate-for-cross-platform-conversational-builds)
- [Sources](#sources)

## The Universal Composition Skeleton

```
                                                ┌─── COMPOSER (per platform) ───┐
                                                │                               │
ai-vector-brain ──┐                             │  iOS      → software-ios-ai-engine
   (corpus build) │                             │  Android  → on-device LLM + sentence bank
                  │   ┌── ai-context-layer ──┐  │  Web      → cloud LLM | Chrome built-in AI | WebLLM
ai-rag ───────────┼──►│  EvidenceBundle      │──┤  Bot      → ai-bot-builder (Telegram/Discord/WA/Slack)
   (retrieval)    │   │  + per-user state    │  │  Voice    → ai-voice-bots (STT/TTS pipeline)
                  │   └──────────────────────┘  │  Backend  → cloud LLM via ai-prompt-engineering
                  │                             │                               │
                  └──── Tier 0 router ──────────┴──────────► answer ◄───────────┘
                       (intent + slots +
                        safety, deterministic)
```

**Load-bearing invariants — same for every platform:**

1. **One typed `EvidenceBundle` struct** flows from Tier 0 into every composer. Platform-specific composers all read the same shape.
2. **One shared answer contract** `{ answer, grounding, followUps[], safetyBoundary, composerUsed }`. UI reads the type, not the engine.
3. **Tier 0 is deterministic and platform-neutral.** Intent classification, slot extraction, safety gating, archetype selection run in your common language (Swift, Kotlin, TypeScript, Python) without an LLM.
4. **Refusal-on-no-evidence is enforced at the bundle layer**, not the composer. If `bundle.anchorCount < 2`, the composer renders a warm onboarding message — never invents.
5. **Naturalness comes from composition, not from the model.** Feel-acknowledgment + 2–3 concrete personal anchors + cross-session memory outweigh model quality.

## The Composer Matrix

Every platform supports at least two composer modes: **with model** (best voice) and **without model** (deterministic, auditable, free). Most products ship both with a fallback chain.

| Platform | Composer A — with on-device model | Composer B — sentence bank / templated | Composer C — retrieval stitch | Composer D — cloud LLM (explicit) |
|---|---|---|---|---|
| **iOS** | Apple Foundation Models (iOS 26+, capable devices) via `@Generable` + `LanguageModelSession` | Hand-curated fragments keyed by (archetype, anchor, mood) | sqlite-vec / ObjectBox + archetype wrappers | OpenAI / Anthropic / Google APIs |
| **Android** | Gemini Nano via AICore / ML Kit GenAI APIs (Pixel 8+, select OEMs) | Same fragment pattern as iOS | ObjectBox Android / sqlite-vec JNI + wrappers | Same cloud APIs |
| **Web browser** | Chrome built-in AI (`window.ai` — Prompt API, Summarizer, Writer, Rewriter) on Chrome 127+ desktop; **or** WebLLM / transformers.js in-browser inference | TS fragment dictionary keyed by archetype | client-side `sqlite-vec` over WASM, or hosted vector store via API | OpenAI / Anthropic / Google streaming APIs |
| **Telegram / Discord / WhatsApp / Slack bot** | rare — run model on server (no on-device) | Python/TS fragment dictionary | server-side vector store + wrappers | cloud LLM via `ai-bot-builder` LangGraph pattern |
| **Voice (telephony, smart speaker)** | rare — latency budget kills on-device | pre-recorded / TTS-rendered fragments | server retrieval + TTS, with cache | cloud LLM with streaming + RA13 voice-tier split |
| **Backend / headless API** | n/a (no surface) | template engine | server retrieval + wrappers | cloud LLM via `ai-prompt-engineering` |

**Picking the composer chain per platform:**

- If the product promises **offline / privacy / no-quota**, the primary composer must be on-device (A) or deterministic (B/C). Cloud (D) is explicit opt-in only.
- If the product promises **highest voice quality** and is online-first, primary is D with B/C as fallback when budget exhausted or unavailable.
- For **regulated domains** (tax, medical, legal, compliance), composer never owns the truth — composer narrates, deterministic tool computes. Same on every platform.

## Three Generic Domain Scenarios, Across Platforms

### Scenario 1 — Consumer reflection / daily check-in companion

**Shape:** consumer app with a personal-knowledge surface (mood, journal, profile-derived facts), light multi-turn, stable interpretation corpus (a few thousand chunks), strong privacy/offline promise.

| Platform | Path with model | Path without model |
|---|---|---|
| **iOS** | Foundation Models `LanguageModelSession` + on-device sqlite-vec mirror | sentence bank (Composer B) + sqlite-vec retrieval stitch (Composer C); rotation window prevents repetition |
| **Android** | Gemini Nano via ML Kit GenAI + ObjectBox vector index | same fragment + retrieval-stitch pattern, Kotlin |
| **Web** | Chrome `window.ai` Prompt API for the answer, indexed-DB-backed `sqlite-vec` (WASM) for retrieval | server-rendered template + server-side vector lookup; React renders the typed answer |
| **Telegram bot** | server-side cloud LLM (Composer D) with persona instructions and tool-calling, LangGraph for memory | Python sentence bank + server vector retrieval, sent via `python-telegram-bot` |
| **Voice** | cloud LLM with streaming and RA13 voice-tier split (foreground hot cache + background vector retrieval) | pre-rendered TTS fragments + cached top-k; longer pauses acceptable on this surface |

Same `ReflectionAnswer` typed result on every platform. Same Tier-0 archetype detection. Cross-surface signal (mood from journaling on iOS feeding the Telegram bot answer) flows through ai-context-layer.

### Scenario 2 — Regulated-domain copilot (tax, medical, legal, compliance)

**Shape:** numeric or regulatory accuracy is load-bearing; wrong answers carry real cost; corpus is volatile (laws change, rates change).

| Platform | Path with model | Path without model |
|---|---|---|
| **iOS** | Foundation Models as **narrator only**, with tool-calling to a deterministic Swift compute engine | Composer B renders the same computed result through templated prose |
| **Android** | Gemini Nano as narrator + Kotlin compute engine via ML Kit function-calling | Composer B with Kotlin templates |
| **Web** | cloud LLM (Claude/GPT) as narrator with **server-side tool-calling** to a deterministic API; Composer B fallback when quota hit | TS template engine over the deterministic API result; no LLM |
| **Telegram bot** | LangGraph: deterministic compute node → narration node (cloud LLM) → response; persona keeps voice warm | rule-engine compute → Python sentence bank → Telegram message |
| **Voice** | streaming cloud LLM narrating the computed result; pre-cache the most common compute outcomes for low latency | pre-rendered TTS fragments for top-N outcomes; deterministic fallback to "I can't tell from your data" |

**Pattern that holds across every platform here:** the model never owns numbers or rules. It owns *empathy with the explanation*. Tool-calling (Apple FM tools, Gemini Nano function-calling, OpenAI tools, LangGraph nodes) is the bridge. **Authority-weighted retrieval** (regulation > guidance > commentary) from `ai-rag` is the safety net. **Refusal-on-no-evidence** is the floor.

### Scenario 3 — Multi-turn emotional companion (journaling, coaching, wellbeing)

**Shape:** long multi-turn sessions, emotional surface, recurring themes across days/weeks. Naturalness *across sessions* matters more than naturalness *within a turn*.

| Platform | Path with model | Path without model |
|---|---|---|
| **iOS** | `LanguageModelSession` persists across the conversation; recurring themes from P14 consolidator inject as context; Tier-0 safety intercepts before FM | Composer C primary (retrieval stitch over symbol/theme corpus on-device), reflective archetype wrappers vary by mood; same safety routing |
| **Android** | Gemini Nano session + ObjectBox; recurring-themes derived memory from background WorkManager job | Sentence bank + ObjectBox retrieval; reflective wrappers in Kotlin |
| **Web** | Chrome built-in AI Prompt API session; IndexedDB-backed memory; `transformers.js` for embeddings if doing the consolidator in-browser | server-side: LangChain / LangGraph short-term + long-term memory (InMemorySaver + InMemoryStore), no LLM in the consolidator — just embeddings + clustering |
| **Telegram bot** | LangGraph + **Mem0** for long-term memory ([vendor-recommended pattern](https://mem0.ai/blog/agentic-rag-chatbot-with-memory)); cloud LLM narrates with persona; recurring themes recalled via memory search node | LangGraph with deterministic nodes only: theme matcher → template selector → Python sentence bank; works fully without LLM credits |
| **Voice** | not recommended as primary surface — voice + emotional + multi-turn is the hardest naturalness problem; if shipped, use cloud LLM with the RA13 voice tier and pre-warmed memory | not recommended without LLM — too easy to break the emotional register |

**Pattern that holds:** continuity comes from `ai-context-layer` (recurring-theme memory + P14 sleep-time consolidation), **not** from the composer. The composer just renders. Replacing the model with sentence-bank-over-retrieval downgrades voice fluidity, **not** relational continuity. Many production teams find Composer B/C with strong theme memory already produces good perceived empathy.

## ASCII Flow — A Single Turn, End to End

How one user turn flows from input to rendered prose on any platform.

```
                user input (text, voice, button)
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  Tier 0  (deterministic, no LLM)    │
        │  ┌───────────────────────────────┐  │
        │  │ 1. Safety / crisis pattern?   │──┼──── yes ──► static safety copy + helplines
        │  │ 2. Archetype detection         │  │             (composer is NOT called)
        │  │ 3. Slot extraction             │  │
        │  │ 4. Locale resolution           │  │
        │  └───────────────────────────────┘  │
        └─────────────┬───────────────────────┘
                      │ intent + slots + safety=clear
                      ▼
        ┌─────────────────────────────────────┐
        │  Bundle assembler (ai-context-layer)│
        │  reads from:                        │
        │   ▸ operational truth (SQL / APIs)  │
        │   ▸ derived memory (user store)     │
        │   ▸ retrieval (ai-rag → ai-vector-brain)
        │   ▸ cross-surface signals (shared)  │
        │  writes: EvidenceBundle (typed)     │
        └─────────────┬───────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────────┐
        │  anchorCount(bundle) ≥ 2 ?          │── no ──► warm onboarding / data-gap CTA
        └─────────────┬───────────────────────┘          (composer is NOT called)
                      │ yes
                      ▼
        ┌─────────────────────────────────────┐
        │  Composer dispatch  (per platform)  │
        │                                     │
        │   on-device model available?        │
        │      │                              │
        │      ├── yes ─► Composer A          │   ◄── iOS: FM | Android: Nano
        │      │           │                  │       Web: window.ai | rest: cloud LLM
        │      │           │ post-process     │
        │      │           ▼                  │
        │      │        anchors ok?           │── no ──┐
        │      │           │ yes              │        │
        │      │           ▼ ───────────────► │        │
        │      │                              │        │
        │      └── no ──► Composer B (sentence bank)   │
        │                  or  Composer C (retrieval) ◄┘
        │                  │                  │
        │                  ▼ ───────────────► │
        └─────────────────┬───────────────────┘
                          │ typed { answer, grounding, anchors[], composerUsed }
                          ▼
        ┌─────────────────────────────────────┐
        │  Universal post-processor           │
        │   ▸ anchor whitelist (P9)           │
        │   ▸ word-count trim                 │
        │   ▸ forbidden-phrase filter         │
        │   ▸ grounding-line extractor        │
        └─────────────┬───────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────────┐
        │  Persist row + emit trace           │── trace: {archetype, composerUsed,
        │  Render in platform UI              │           anchorCount, wordCount,
        └─────────────────────────────────────┘           latencyMs, fallbackReason?}
```

## ASCII Flow — Composer Fallback Chain per Platform

```
iOS                          Android                       Web (browser)
───                          ───────                       ─────────────
SystemLanguageModel          AICore.isAvailable()?         'ai' in window && window.ai.canCreateTextSession()?
  .availability                │                              │
   .available?                 │                              │
    │                          │                              │
  yes│no                     yes│no                          yes│no
    │ │                        │ │                            │ │
    ▼ │                        ▼ │                            ▼ │
  Apple FM                  Gemini Nano                 Chrome window.ai
  @Generable                ML Kit GenAI                Prompt / Summarizer
    │                          │                            │
    │ post-proc fails?         │ post-proc fails?           │ post-proc fails?
    ▼ yes                      ▼ yes                        ▼ yes
  Composer B                Composer B                  WebLLM (transformers.js)
  sentence bank             sentence bank                  │ fails / not loaded?
    │                          │                            ▼
    │ thin bundle?             │ thin bundle?             Composer B (TS templates)
    ▼ yes                      ▼ yes                        │
  Composer C                Composer C                      │ thin bundle?
  sqlite-vec stitch         ObjectBox stitch                ▼ yes
    │                          │                          Composer C (server vector)
    │ still no answer?         │ still no answer?           │
    ▼                          ▼                            ▼
  Cloud LLM (D)             Cloud LLM (D)               Cloud LLM (D)
  EXPLICIT opt-in           EXPLICIT opt-in             EXPLICIT opt-in

Telegram / Discord / WhatsApp / Slack bot       Voice (telephony / smart speaker)
─────────────────────────────────────────       ─────────────────────────────────
[no on-device tier — server-side only]         Latency budget < 300 ms ─► RA13 hot/cold
                                                    │
LangGraph + Mem0  ◄── common baseline           Foreground hot cache         Background cold tier
    │                                           (last-N turns, sub-ms)       (vector recall, P14)
    │ LLM quota exhausted?                          │                              │
    ▼ yes                                           └──────── streams ─────────────┘
Composer B (Python templates)                         │
    │                                                 ▼
    │ thin bundle?                                  Composer (cloud LLM streaming)
    ▼                                                 │ network fails?
Composer C (server retrieval + wrappers)              ▼ yes
                                                    Pre-rendered TTS fragments (B)
```

## ASCII Flow — Three Scenarios Mapped to Skill Chain

```
SCENARIO 1 — Consumer reflection / daily check-in
──────────────────────────────────────────────────
                     ┌─ ai-vector-brain ─┐
                     │  stable corpus    │
                     │  server pgvector  │
                     │  on-device mirror │
                     │  (sqlite-vec /    │
                     │   ObjectBox /     │
                     │   IndexedDB WASM) │
                     └────────┬──────────┘
                              ▼
                     ┌─ ai-rag ──────────┐
                     │  hybrid FTS+vec   │
                     │  archetype filter │
                     │  P21 wrappers     │
                     └────────┬──────────┘
                              ▼
                     ┌─ ai-context-layer ┐
                     │  profile, mood,   │
                     │  cross-surface    │
                     │  signals (P14)    │
                     └────────┬──────────┘
                              │  EvidenceBundle
                              ▼
                     ┌─ composer  (platform) ┐
                     │  A: on-device model   │
                     │  C: retrieval stitch  │
                     │  B: sentence bank     │
                     └────────┬──────────────┘
                              ▼
                          warm prose
                       (40–70 words, feel-first,
                        2–3 personal anchors)

SCENARIO 2 — Regulated-domain copilot  ──  MODEL NARRATES, CODE COMPUTES
─────────────────────────────────────────────────────────────────────────
   user question
        │
        ▼
   Tier 0 ──► EvidenceBundle (entity, computedState, history)
        │                          │
        │                          │  composer
        │                          ▼
        │     ┌─────────────────────────────────────────┐
        │     │  model session with tools               │
        │     │                                         │
        │     │      ┌──────────────────────────┐       │
        │     │      │ computeImpact(args)      │◄──────┼─── deterministic engine
        │     │      │  ↳ tax / dose / clause   │       │    (Swift / Kotlin / TS / Python)
        │     │      └──────────┬───────────────┘       │    NO MODEL involved
        │     │                 │ typed result          │
        │     │                 ▼                       │
        │     │      model narrates result              │
        │     │      with provenance citation           │
        │     └─────────────────────────────────────────┘
        │                          │
        ▼                          ▼
   refusal if         "About £842 more this quarter,
   confidence <        mostly because July invoices pushed
   threshold           you to higher-rate band. (SAIM2110,
                       effective 2026-04-06)"

       Composer B fallback emits the SAME computed result
       through templated prose — equally accurate, less warm.


SCENARIO 3 — Multi-turn emotional companion  ── CONTINUITY IS A CONTEXT-LAYER PROBLEM
──────────────────────────────────────────────────────────────────────────────────────
   Day 1, Sun:    Day 2, Mon:    Day 3, Tue:
   turn ──►Tier0  turn ──►Tier0  turn ──►Tier0
            │              │              │
            ▼              ▼              ▼
       composer       composer       composer
            │              │              │
            ▼              ▼              ▼
       persisted      persisted      persisted
       row            row            row
            │              │              │
            └──────┬───────┴──────┬───────┘
                   ▼              ▼
            ┌── P14 sleep-time consolidator (background) ──┐
            │  ▸ dedupe duplicate themes                   │
            │  ▸ resolve contradictions                    │
            │  ▸ rewrite relative→absolute dates           │
            │  ▸ cluster recurring themes per user         │
            └──────────────────┬───────────────────────────┘
                               ▼
                     recurring-themes memory
                     (per-user, P22 isolated)
                               │
                               ▼  ◄── injected as compact summary
                     Day 4 turn's bundle             into instructions, NOT raw
                               │                     prompt-stuffed
                               ▼
                          composer
                               │
                               ▼
                "Last Sunday you wrote about boundaries.
                 The dream feels like it sits in the same
                 territory — [chunk_excerpt(boundary, jungian)]."

   Composer A (on-device model) or C (retrieval stitch) — either reads the SAME
   recurring-themes memory. Continuity is the bundle, not the model.
```

## ASCII Flow — Cross-Surface Signal Propagation

How a mood logged on iOS reaches the Telegram bot ten minutes later.

```
   iOS app (journaling)         Telegram bot (server)        Web (dashboard)
   ──────────────────────       ─────────────────────        ───────────────
   user logs mood = "low"               │                            │
        │                               │                            │
        │ writes signal                 │                            │
        ▼                               │                            │
   ┌──────────────────────────────────────────────────────────────────────┐
   │            Shared signal store  (Postgres / memory service)           │
   │   {user_id, kind=mood, value="low", source=ios.journal, ts=...}       │
   │   ACL: per-user; retention: 90d; provenance: required                 │
   └──────────────────────────────────────────────────────────────────────┘
        ▲                               │                            ▲
        │                               │                            │
   bundle filler reads             bundle filler reads          bundle filler reads
   on next iOS chat turn           on next Telegram turn        on next web turn
        │                               │                            │
        ▼                               ▼                            ▼
   feel-ack opener:                feel-ack opener:             dashboard surface
   "Sounds heavy today.            "Sounds heavy today.         tone shifts to
   Your progressed Moon..."        Want to talk about it?"      gentler copy

   Pattern: surfaces READ from the shared store; only the LOGGING surface
   writes that signal. Never duplicate signal-extraction logic per surface.
```

## ASCII Flow — EvidenceBundle Schema Mirroring per Language

```
                  ┌──────── EvidenceBundle (canonical schema) ────────┐
                  │                                                   │
                  │  profile:        Profile                          │
                  │  derivedFacts:   DerivedFacts                     │
                  │  recentSignals:  Signal[]                         │
                  │  todayDerived:   TodayDerived?                    │
                  │  lastMood:       Mood?                            │
                  │  archetype:      Archetype                        │
                  │  retrieval:      RetrievedChunk[]                 │
                  │  provenance:     ProvenanceRef[]                  │
                  │  locale:         Locale                           │
                  │  safetyBoundary: SafetyBoundary                   │
                  │  confidence:     Float  // anchors + retrieval    │
                  └──────────────────┬────────────────────────────────┘
                                     │ mirror per language
                                     │ via codegen or hand
        ┌──────────────┬─────────────┼─────────────┬──────────────┐
        ▼              ▼             ▼             ▼              ▼
     Swift           Kotlin       TypeScript     Python         JSON Schema
     struct          data class   interface      Pydantic       (contract test
     (iOS)           (Android)    (web / bot)    (server bot)    cross-language)

   Rule: schema changes go through one PR that updates every mirror
   AND ships a fixture into the cross-language contract test.
   Drift = invisible bugs in grounding and refusal across surfaces.
```

## Per-Platform Composer Notes

### iOS — `software-ios-ai-engine`

Full depth in [`composition-with-rag-context-vector.md`](../../software-ios-ai-engine/references/composition-with-rag-context-vector.md). Key choices: `SystemLanguageModel.default.availability` gating, `@Generable` typed outputs, sqlite-vec for on-device corpus mirror with `content_hash` parity to server.

### Android — `software-android-native`

[Gemini Nano via AICore](https://developer.android.com/ai/gemini-nano) ([ML Kit GenAI APIs](https://developers.google.com/ml-kit/genai)) is the closest equivalent to Apple FM: on-device, privacy-preserving, no cost per request. **Device availability is narrow and changes by release** — check the current supported-device list; ML Kit GenAI exposes summarization, proofreading, rewriting out-of-the-box. For broader Android coverage, deterministic Composer B is the floor. ObjectBox ships first-class Kotlin bindings for on-device HNSW vector search.

### Web browser — `software-frontend`

Three composer tiers in browser:

1. **Chrome built-in AI** ([`window.ai` Prompt API](https://developer.chrome.com/docs/ai/built-in)) — Gemini Nano runs in-browser; Prompt / Summarizer / Writer / Rewriter / Translator / Proofreader APIs. Check the current Chrome version and flag requirements before relying on it; no per-request cost. Limited to Chrome — Safari, Firefox, mobile browsers fall back.
2. **WebLLM / transformers.js** — open-weight models in-browser via WebGPU. Higher install cost (model download), works in any modern browser, full client-side.
3. **Cloud LLM streaming** — OpenAI / Anthropic / Google streaming APIs with `EventSource` or `fetch` streams; React renders snapshot-style updates. Most flexible; costs and privacy tradeoffs apply.

Storage on-device for retrieval: IndexedDB-backed `sqlite-vec` via WASM, or hosted vector via API.

### Messaging bots — `ai-bot-builder`

Telegram / Discord / WhatsApp / Slack are **server-side**; there is no "on-device" path. The composer is whichever LLM you connect server-side. A common stack: **LangGraph + Mem0** for memory ([reference implementation](https://jamwithai.substack.com/p/agentic-rag-with-langgraph-and-telegram)). Five LangGraph memory types apply: short-term (`MessagesState + InMemorySaver + stable thread_id`) and long-term (`InMemoryStore + get_store()` across thread_ids).

To avoid lock-in to a single LLM, expose a `Composer` Protocol that has both an LLM implementation and a fragment-bank implementation; the bot framework reads the typed result either way.

### Voice — `ai-voice-bots`

The turn-latency budget is a hard constraint; measure it on your own audio pipeline. **Apply RA13 from `ai-context-layer`** ([reference-architectures.md](reference-architectures.md)): split memory into a foreground "Fast Talker" hot tier (per-user in-process cache) and a background "Slow Thinker" cold tier (vector recall + pre-fetch). Composer is typically cloud LLM with streaming, because on-device voice + multi-turn is still rough. Composer B (pre-rendered TTS fragments + cached top-k) is a working fallback for narrow domains.

### Voice and realtime memory

Scenario defaults: [memory-scenario-playbooks](memory-scenario-playbooks.md#9-voice--realtime). The memory rules that differ from chat:

- **Latency budget is a design input.** Write the per-turn budget down before choosing the memory path, then allocate it across ASR end-pointing, memory lookup, model first token, and TTS. Any memory step that cannot fit runs off the hot path. Do not copy a published millisecond figure; measure yours.
- **Hot set preloaded at session start.** Load the caller's profile, open items, and last-call summary from the authenticated session metadata before the media session connects (LiveKit documents loading user data before `ctx.connect()`), so the first turn never waits on memory.
- **Inject, don't call.** Retrieve inside the turn-completed hook and inject into the turn context, rather than giving the model a memory tool; LiveKit documents that this avoids the extra round-trips of tool calls.
- **Prefetch in the background.** A background worker predicts likely next topics and fills a per-user cache that the foreground turn reads only from; VoiceAgentRAG (arXiv 2603.02206, abstract) describes this fast-reader / slow-prefetcher split and reports lower retrieval latency on its own setup.
- **Async writes after the turn.** Memory writes never block speech: queue them after the turn and apply them off the hot path. A fact the caller said a few turns ago may not be queryable yet, so keep the live transcript in context for the current call.
- **Write-after-call consolidation.** At call end, consolidate the transcript into facts with ASR confidence attached; low-confidence or consequential facts (amounts, dates, names) are stored as unconfirmed claims or confirmed aloud before the call ends. A correction ("no, fifteen, not fifty") supersedes the misheard fact (P4) instead of adding a second one.
- **Never cache operational truth.** Balances and order status are read live (P1) even on voice; a stale value read aloud is the classic voice-memory failure. When a live lookup is unavoidable, play an acknowledgement rather than stalling.

### Backend / headless — `software-backend`

No user-facing surface; the composer's "answer" is consumed by another system. The bundle + composer pattern still applies — the backend is just one more consumer of `EvidenceBundle`. Composer is typically cloud LLM via `ai-prompt-engineering` for prompt design and `ai-llm-inference` for latency/cost tuning.

## Cross-Platform Patterns

### Pattern — Same bundle, one composer per platform, fallback chain inside

The `EvidenceBundle` Swift struct on iOS, Kotlin data class on Android, TypeScript interface in browser/Node, Pydantic model in Python is the *same schema* across the codebase. The bundle filler (Tier 0) can be shared logic if you ship a small WASM or rules engine; otherwise it's mirrored per language. The composer fallback chain (A → B → C → refusal) lives inside each platform's composer module.

### Pattern — Model owns voice, tools own truth

Holds on every platform with tool-calling:

- iOS: Foundation Models `Tool` protocol.
- Android: ML Kit GenAI function-calling.
- Web/Server: OpenAI tools, Anthropic tools, Google function-calling, LangGraph nodes.

For numbers, regulations, status, or anything the user could check independently — code computes, model narrates.

### Pattern — On-device model is an upgrade, not a requirement

Ship deterministic Composer B (sentence bank) on every platform first. It works on every device, every browser, every channel. Layer on-device model (Apple FM on iOS, Gemini Nano on Android, `window.ai` on Chrome) as a voice-quality upgrade with a feature flag and a remote kill switch. Layer cloud LLM as explicit opt-in for "Deeper answer" CTA. The fallback chain is `model → sentence bank → retrieval stitch → refusal`, in that order.

### Pattern — Persona lives in instructions, not in prompts per turn

Whether using Apple FM, Gemini Nano, Chrome `window.ai`, or cloud LLM: the persona / voice contract / safety rules go in the **session-level instructions** (or system prompt) and stay constant. Per-turn prompts only carry the bundle + the user's message. This keeps token budget low and behavior consistent.

### Pattern — Cross-surface signal flow

A user mood logged on the iOS journaling surface should be available to the Telegram bot ten minutes later. This is `ai-context-layer` Stance #9 — cross-surface signal flow. Mechanism: write signals to a shared store (Postgres, a memory service, or `ai-context-layer` RA1 reference); each surface's bundle filler reads from the same store. Don't duplicate signal logic per surface.

### Pattern — Persistence parity

Every UI-visible field (`answerSource`, `grounding`, `anchors`, `composerUsed`) must be persisted inside the stored row, not just in the HTTP envelope. Same rule on every platform. Integration test: no successful compose has `answerSource IS NULL`.

## Anti-Patterns Specific to Cross-Platform Composition

- **One composer per surface duplicates Tier-0 routing logic.** Centralize archetype detection, slot extraction, and safety gating in one cross-language contract; only the *render* differs.
- **Different output contracts per surface.** iOS returns `{answer, source}`, web returns a string, Telegram returns prose with embedded markdown. UI/analytics/eval grow surface-specific branches. Lock the typed contract once.
- **Letting each surface ship its own grounding/refusal logic.** Refusal-on-no-evidence belongs to the bundle layer (`ai-rag` grounding contract), not per-surface composers.
- **Cloud LLM as silent fallback.** If a local-first or "no-quota" promise exists, cloud must be explicit. Tier-2 upgrade is a visible user CTA, never a hidden chain.
- **Shipping voice + multi-turn + emotional on the first release.** That's the hardest naturalness problem on any platform. Start with a non-voice channel.
- **Embedding-model split between server and on-device.** Different embedding models on each side mean citations don't resolve. Pin model name + version on every row; mirror identically.
- **Telegram bot with no memory.** LangGraph short-term `MessagesState` + long-term `InMemoryStore` is the minimum baseline. Without memory, every turn feels like a stranger.

## Verification Gate for Cross-Platform Conversational Builds

Before shipping:

- The `EvidenceBundle` schema is documented once and mirrored per language (Swift / Kotlin / TS / Python).
- Tier-0 archetype detection + safety gating runs **before** any composer, on every platform.
- Refusal threshold from `ai-rag` is enforced identically across composers.
- On platforms with an on-device model option (iOS / Android / Chrome web), the deterministic Composer B path is also fully wired and tested — model failure must not break the surface.
- The cloud LLM tier (D), if shipped, is gated behind an explicit user CTA, not a silent fallback.
- Cross-surface signals flow through one shared store; per-surface signal logic is not duplicated.
- Bot platforms (Telegram/Discord/WhatsApp/Slack) have LangGraph short-term + long-term memory wired before launch.
- Voice surface has RA13 hot/cold tier split if latency budget is sub-second.
- Persistence parity: every UI-visible composer-output field is also persisted inside the row.
- An integration test exercises each platform's "no model available" path (offline iOS, no-AICore Android, non-Chrome browser, LLM-quota-exhausted bot) and renders a real answer.

## Sources

- Apple — [Foundation Models documentation](https://developer.apple.com/documentation/FoundationModels) and [WWDC25 Deep Dive](https://developer.apple.com/videos/play/wwdc2025/301/)
- [Android Gemini Nano docs](https://developer.android.com/ai/gemini-nano), [ML Kit GenAI APIs](https://developers.google.com/ml-kit/genai), [Gemma 4 in AICore Developer Preview (April 2026)](https://android-developers.googleblog.com/2026/04/AI-Core-Developer-Preview.html)
- [Chrome built-in AI](https://developer.chrome.com/docs/ai/built-in) (Prompt, Summarizer, Writer, Rewriter, Translator, Proofreader APIs)
- [Agentic RAG with LangGraph & Telegram](https://jamwithai.substack.com/p/agentic-rag-with-langgraph-and-telegram)
- [LangGraph + Mem0 for long-term agent memory](https://mem0.ai/blog/agentic-rag-chatbot-with-memory)
- [DigitalOcean — LangGraph + Mem0 integration](https://www.digitalocean.com/community/tutorials/langgraph-mem0-integration-long-term-ai-memory)
- [sqlite-vec](https://github.com/asg017/sqlite-vec), [sqlite-rag](https://github.com/sqliteai/sqlite-rag), [ObjectBox iOS](https://objectbox.io/swift-ios-on-device-vector-database-aka-semantic-index/)
- [NVIDIA PersonaPlex — full-duplex conversational AI](https://research.nvidia.com/labs/adlr/personaplex/)
- [CHI 2026 — Breakdowns in Conversational AI](https://dl.acm.org/doi/10.1145/3772318.3791186)
