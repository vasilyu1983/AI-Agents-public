# Voice Quality Pre-Launch Checklist

Complete this checklist before launching a voice bot to production.

## Audio Quality

- [ ] **STT accuracy** — WER measured on representative sample, within target (< [X]%)
- [ ] **TTS naturalness** — Voice sounds natural, no artifacts, appropriate pace
- [ ] **Audio clarity** — No echo, no clipping, no background noise injection
- [ ] **Volume levels** — Bot audio volume matches typical phone call levels
- [ ] **Silence handling** — No awkward silences > 1s during processing (use filler or acknowledgment)

## Conversation Quality

- [ ] **Turn-taking** — Bot doesn't cut off user, user can interrupt bot (barge-in)
- [ ] **VAD accuracy** — End-of-speech detected correctly (not too early, not too late)
- [ ] **Barge-in** — When user speaks during bot response, bot stops and listens
- [ ] **Background noise** — Bot handles typical phone noise (car, office, street)
- [ ] **Accents and dialects** — STT tested with expected user demographics

## Latency

- [ ] **Total turn latency** — p90 < 700ms measured under load
- [ ] **No perceptible delay** — Conversation feels natural (compare to human-to-human call)
- [ ] **Load tested** — Latency measured at expected peak concurrent calls
- [ ] **Degradation plan** — Known behavior when latency exceeds budget

## Reliability

- [ ] **Connection recovery** — Pipeline reconnects after brief network interruption
- [ ] **Provider failover** — Fallback STT/TTS if primary provider is down
- [ ] **Graceful degradation** — If pipeline fails, user is routed to human or voicemail
- [ ] **No hung calls** — Calls are terminated cleanly on error (no infinite silence)
- [ ] **Concurrent call limit** — Tested at maximum expected concurrent calls

## Telephony

- [ ] **DTMF works** — Keypad input detected correctly alongside voice
- [ ] **Hold/transfer** — Transfer to human agent works with context
- [ ] **Caller ID** — Correct caller ID displayed for outbound calls
- [ ] **Number format** — International numbers handled correctly
- [ ] **Call recording** — Working and consent-compliant (if applicable)

## Monitoring

- [ ] **Latency dashboards** — Per-component and total latency visible
- [ ] **Quality metrics** — MOS estimates, WER sampling, call completion rate tracked
- [ ] **Error alerting** — Alerts for: high error rate, latency spikes, provider outages
- [ ] **Call logging** — Transcripts and metadata stored for review
- [ ] **Cost tracking** — Per-call cost monitored (telephony + STT + LLM + TTS)
