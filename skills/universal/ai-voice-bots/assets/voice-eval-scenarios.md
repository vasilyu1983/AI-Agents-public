# Voice Agent Eval Scenarios

Use this template to define end-to-end voice-agent evals before launch or vendor migration. Prefer real audio replays when available; use synthetic calls only to fill coverage gaps.

## Scenario Set

| Scenario | Caller goal | Stressor | Expected outcome | Pass criteria |
|----------|-------------|----------|------------------|---------------|
| Happy path | Resolve a common request | Normal handset audio | Task completed without transfer | Correct answer, p90 turn latency within budget |
| Barge-in | Interrupt the bot mid-response | User speaks over TTS | Bot stops speaking and handles interruption | Bot audio stops within 350ms of speech onset |
| Noisy caller | Complete the same request | Office, street, car, or speakerphone noise | Bot asks concise clarification or succeeds | No hallucinated confirmation; no repeated dead air |
| Accent/dialect | Complete the same request | Representative caller demographics | Bot recognizes key entities | Critical fields correct or DTMF fallback offered |
| Tool failure | Lookup or booking action fails | Timeout or provider error | Bot explains and offers fallback/transfer | No silent failure; no irreversible action |
| Compliance gate | Payment, identity, or consent step | Sensitive data present | Bot follows policy and logging rules | Recording/redaction/confirmation behavior correct |
| Human transfer | Caller asks for an agent | Escalation intent | Warm transfer with context | Handoff payload contains intent, summary, and blockers |
| Long call | Multi-turn troubleshooting | 10+ minutes or many corrections | State remains coherent | No lost task state; recovery after correction |

## Metrics

Track these per scenario and by caller cohort:

- Task completion or correct transfer
- First-audio latency, p90/p99 turn latency, and barge-in stop latency
- Speech recognition failures on critical fields
- User repetition rate and clarification count
- Tool-call success, timeout, and rollback behavior
- Policy violations: consent, retention, PII, PCI, TCPA, or jurisdiction-specific gates
- Audio experience score: clipping, overlap, silence, unnatural pacing

## Eval Harness Shape

```json
{
  "scenario_id": "barge_in_order_status",
  "caller_profile": "mobile_noisy_us",
  "input_audio": "fixtures/barge_in_order_status.wav",
  "expected": {
    "outcome": "resolved",
    "must_include": ["order status"],
    "must_not_include": ["payment card"],
    "max_turn_latency_p90_ms": 700,
    "max_barge_in_stop_ms": 350
  },
  "judges": ["deterministic_assertions", "transcript_llm_judge", "audio_experience_judge"]
}
```

## Launch Gate

- Run at least one happy-path, one interruption, one noisy-audio, one tool-failure, and one compliance scenario for every production flow.
- Use at least 50 calls per high-risk scenario before launch; use more when measuring conversion or containment.
- Do not accept a vendor or model change based only on MOS/WER. Include whole-call task success and turn-taking experience.
