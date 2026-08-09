# Voice Safety & Compliance

**Purpose**: Compliance requirements for voice bots — call recording consent, PCI, TCPA, GDPR, voice biometrics, PII in transcripts, and jurisdiction-specific checklists.

No legal advice. Implementation guidance and compliance checklists only. Consult legal counsel for binding compliance decisions.

---
## Table of Contents

- [Call Recording Consent](#call-recording-consent)
- [Consent Models](#consent-models)
- [US State Requirements](#us-state-requirements)
- [International Requirements](#international-requirements)
- [Disclosure Language Templates](#disclosure-language-templates)
- [Implementation Pattern](#implementation-pattern)
- [PCI Compliance in Voice](#pci-compliance-in-voice)
- [PCI DSS Requirements for Voice](#pci-dss-requirements-for-voice)
- [Pause-and-Resume Pattern](#pause-and-resume-pattern)
- [DTMF-Only Payment Pattern](#dtmf-only-payment-pattern)
- [TCPA Compliance (Outbound)](#tcpa-compliance-outbound)
- [TCPA Core Requirements](#tcpa-core-requirements)
- [Calling Hours](#calling-hours)
- [Consent Management](#consent-management)
- [TCPA Compliance Checklist](#tcpa-compliance-checklist)
- [GDPR Voice Data](#gdpr-voice-data)
- [GDPR Requirements for Voice](#gdpr-requirements-for-voice)
- [Right to Deletion](#right-to-deletion)
- [Data Retention Policy](#data-retention-policy)
- [Voice Biometric Consent](#voice-biometric-consent)
- [When Voice Biometrics Apply](#when-voice-biometrics-apply)
- [Consent Requirements by Jurisdiction](#consent-requirements-by-jurisdiction)
- [PII in Transcripts](#pii-in-transcripts)
- [PII Categories in Voice Data](#pii-categories-in-voice-data)
- [Real-Time PII Redaction](#real-time-pii-redaction)
- [Post-Processing PII Redaction](#post-processing-pii-redaction)
- [Storage Policies](#storage-policies)
- [Compliance Checklist by Jurisdiction](#compliance-checklist-by-jurisdiction)
- [United States](#united-states)
- [European Union (GDPR)](#european-union-gdpr)
- [United Kingdom](#united-kingdom)
- [Australia](#australia)
- [Canada](#canada)
- [Incident Response for Voice Data Breaches](#incident-response-for-voice-data-breaches)
- [Voice Data Breach Scenarios](#voice-data-breach-scenarios)
- [Incident Response Playbook](#incident-response-playbook)
- [Related References](#related-references)

---

## Call Recording Consent

### Consent Models

| Model | Rule | Jurisdictions |
|-------|------|---------------|
| **One-party consent** | Only one party (you) needs to consent to record | Most US states, UK |
| **Two-party / all-party consent** | All parties must consent before recording | CA, FL, IL, PA, WA + others; EU (GDPR) |
| **No consent needed** | Recording permitted without consent | Rare; some B2B contexts |

**Default posture**: Always announce recording and get consent. This satisfies all jurisdictions and builds trust.

### US State Requirements

**Two-party consent states (as of March 2026):**
California, Connecticut, Florida, Illinois, Maryland, Massachusetts, Michigan, Montana, Nevada, New Hampshire, Oregon, Pennsylvania, Washington.

**One-party consent**: All other US states and federal law (federal allows one-party).

**Interstate calls**: When calling across state lines, apply the stricter standard. If either party is in a two-party state, get both-party consent.

### International Requirements

| Country/Region | Consent Model | Notes |
|---------------|---------------|-------|
| **EU/EEA** | Explicit consent (GDPR) | Must have legal basis; consent or legitimate interest |
| **UK** | One-party (with disclosure) | Must inform the other party recording is happening |
| **Canada** | One-party (federal) | Some provinces require all-party |
| **Australia** | All-party in most states | QLD/VIC/TAS/WA require all-party consent |
| **India** | No specific law | Best practice: disclose |

### Disclosure Language Templates

**Pre-call announcement (default — satisfies all jurisdictions):**
```
"This call may be recorded for quality assurance and training purposes.
By continuing, you consent to recording.
If you do not wish to be recorded, please let us know."
```

**Shortened version (for known one-party states):**
```
"This call may be recorded for quality and training purposes."
```

**Explicit opt-in (for strict GDPR compliance):**
```
"We'd like to record this call to improve our service.
Press 1 to consent to recording, or press 2 to continue without recording."
```

### Implementation Pattern

```python
from enum import Enum

class RecordingConsent(Enum):
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    NOT_REQUIRED = "not_required"

class ConsentManager:
    """Manage recording consent based on jurisdiction."""

    TWO_PARTY_US_STATES = {
        "CA", "CT", "FL", "IL", "MD", "MA", "MI", "MT",
        "NV", "NH", "OR", "PA", "WA",
    }

    def __init__(self, default_consent_mode: str = "always_ask"):
        self.default_consent_mode = default_consent_mode
        self.consent_status = RecordingConsent.PENDING

    def requires_explicit_consent(self, caller_state: str | None, caller_country: str = "US") -> bool:
        """Determine if explicit consent is needed."""
        if self.default_consent_mode == "always_ask":
            return True
        if caller_country in ("EU", "EEA", "AU"):
            return True
        if caller_country == "US" and caller_state in self.TWO_PARTY_US_STATES:
            return True
        return False

    def grant_consent(self):
        self.consent_status = RecordingConsent.GRANTED

    def deny_consent(self):
        self.consent_status = RecordingConsent.DENIED

    @property
    def can_record(self) -> bool:
        return self.consent_status == RecordingConsent.GRANTED
```

---

## PCI Compliance in Voice

### PCI DSS Requirements for Voice

When handling payment card data over the phone, these PCI DSS requirements apply:

| Requirement | Rule | Implementation |
|------------|------|----------------|
| **Never store full card numbers in recordings** | PCI DSS 3.2 | Pause recording during payment |
| **Never store CVV/CVC in any form** | PCI DSS 3.2 | Never ask for CVV by voice; use DTMF |
| **Mask card numbers in transcripts** | PCI DSS 3.4 | Real-time PII redaction |
| **Encrypt transmission** | PCI DSS 4.1 | TLS for all audio streams |
| **Restrict access to recordings** | PCI DSS 7.1 | Role-based access control |

### Pause-and-Resume Pattern

```python
class PCIRecordingController:
    """Pause call recording during payment card capture."""

    def __init__(self, recording_client):
        self.recording_client = recording_client
        self._is_paused = False

    async def enter_payment_mode(self, call_id: str):
        """Pause recording before collecting payment data."""
        if not self._is_paused:
            await self.recording_client.pause(call_id)
            self._is_paused = True

    async def exit_payment_mode(self, call_id: str):
        """Resume recording after payment data collection."""
        if self._is_paused:
            await self.recording_client.resume(call_id)
            self._is_paused = False

# Twilio-specific implementation
from twilio.rest import Client

async def pause_twilio_recording(account_sid: str, auth_token: str, call_sid: str, recording_sid: str):
    client = Client(account_sid, auth_token)
    client.calls(call_sid).recordings(recording_sid).update(status="paused")

async def resume_twilio_recording(account_sid: str, auth_token: str, call_sid: str, recording_sid: str):
    client = Client(account_sid, auth_token)
    client.calls(call_sid).recordings(recording_sid).update(status="in-progress")
```

### DTMF-Only Payment Pattern

Never collect card numbers via voice. Use DTMF tones instead — they can be masked in recordings.

```python
async def collect_card_via_dtmf(
    dtmf_queue: asyncio.Queue,
    tts_client,
    audio_output,
    recording_controller,
    call_id: str,
) -> str | None:
    """Collect credit card number via DTMF tones (not voice)."""

    # Pause recording
    await recording_controller.enter_payment_mode(call_id)

    prompt = (
        "For security, please enter your card number using your phone keypad. "
        "Press pound when finished."
    )
    async for chunk in tts_client.synthesize_stream(prompt):
        await audio_output.put(chunk)

    # Collect digits
    digits = ""
    while True:
        try:
            digit = await asyncio.wait_for(dtmf_queue.get(), timeout=15.0)
            if digit == "#":
                break
            digits += digit
        except asyncio.TimeoutError:
            await recording_controller.exit_payment_mode(call_id)
            return None

    # Resume recording
    await recording_controller.exit_payment_mode(call_id)

    # Validate card number (basic Luhn check)
    if len(digits) >= 13 and len(digits) <= 19:
        return digits
    return None
```

---

## TCPA Compliance (Outbound)

### TCPA Core Requirements

The Telephone Consumer Protection Act (TCPA) governs outbound calling in the US. Violations carry penalties of $500-$1,500 per call.

| Requirement | Rule | Penalty |
|------------|------|---------|
| **Prior express consent** | Must have consent before auto-dialing or using prerecorded messages | $500/violation |
| **Do-Not-Call list** | Must check national DNC registry + internal DNC list | $500/violation |
| **Calling hours** | No calls before 8 AM or after 9 PM (callee's local time) | $500/violation |
| **Caller ID** | Must transmit accurate caller ID | $500/violation |
| **Opt-out mechanism** | Must honor opt-out requests immediately | $1,500/violation (willful) |
| **Written consent for marketing** | Prior express written consent for telemarketing autodial/prerecorded | $1,500/violation (willful) |

### Calling Hours

```python
from datetime import datetime, time
import pytz

class TCPACallingHours:
    """Enforce TCPA calling hours: 8 AM - 9 PM callee's local time."""

    EARLIEST = time(8, 0)
    LATEST = time(21, 0)

    # State-specific overrides (some states are stricter)
    STATE_OVERRIDES = {
        "OR": (time(9, 0), time(20, 0)),   # Oregon: 9 AM - 8 PM
        "WA": (time(8, 0), time(20, 0)),   # Washington: 8 AM - 8 PM
    }

    def can_call(self, callee_timezone: str, callee_state: str | None = None) -> bool:
        """Check if it's currently within TCPA calling hours."""
        tz = pytz.timezone(callee_timezone)
        local_now = datetime.now(tz).time()

        earliest, latest = self.EARLIEST, self.LATEST
        if callee_state and callee_state in self.STATE_OVERRIDES:
            earliest, latest = self.STATE_OVERRIDES[callee_state]

        return earliest <= local_now <= latest

    def next_available_window(self, callee_timezone: str) -> datetime:
        """Return the next time we can call this number."""
        tz = pytz.timezone(callee_timezone)
        now = datetime.now(tz)
        local_time = now.time()

        if local_time < self.EARLIEST:
            return now.replace(hour=8, minute=0, second=0, microsecond=0)
        elif local_time > self.LATEST:
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=8, minute=0, second=0, microsecond=0)
        return now  # Currently callable
```

### Consent Management

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TCPAConsent:
    phone_number: str
    consent_type: str  # "express", "express_written", "none"
    consent_date: datetime
    consent_source: str  # "web_form", "verbal", "sms_opt_in"
    consent_text: str    # Exact language the user agreed to
    revoked: bool = False
    revoked_date: datetime | None = None

class ConsentStore:
    """Track TCPA consent for outbound calling."""

    def __init__(self):
        self._consents: dict[str, TCPAConsent] = {}

    def has_consent(self, phone_number: str, call_type: str = "informational") -> bool:
        """Check if we have valid consent to call this number."""
        consent = self._consents.get(phone_number)
        if consent is None or consent.revoked:
            return False
        if call_type == "marketing" and consent.consent_type != "express_written":
            return False  # Marketing requires express written consent
        return True

    def revoke(self, phone_number: str):
        """Immediately honor opt-out request."""
        consent = self._consents.get(phone_number)
        if consent:
            consent.revoked = True
            consent.revoked_date = datetime.utcnow()
```

### TCPA Compliance Checklist

Before launching any outbound dialing campaign:

- [ ] Verify prior express consent for every number (written consent for marketing)
- [ ] Scrub against national DNC registry (updated within 31 days)
- [ ] Scrub against internal DNC list (updated in real-time)
- [ ] Enforce calling hours (8 AM - 9 PM callee's local time)
- [ ] Transmit accurate caller ID
- [ ] Provide opt-out mechanism in every call ("Press 2 to be removed from our list")
- [ ] Honor opt-out requests within 30 days (best practice: immediately)
- [ ] Log consent records with date, source, and exact consent language
- [ ] Record all calls (with consent) for dispute evidence
- [ ] Review state-specific regulations (some states are stricter than federal TCPA)

---

## GDPR Voice Data

### GDPR Requirements for Voice

Voice recordings and transcripts are personal data under GDPR. These requirements apply:

| Requirement | Implementation |
|------------|----------------|
| **Lawful basis** | Consent (Art. 6(1)(a)) or legitimate interest (Art. 6(1)(f)) |
| **Purpose limitation** | Only use recordings for stated purpose (quality, training) |
| **Data minimization** | Don't record more than necessary; delete when purpose is fulfilled |
| **Storage limitation** | Define and enforce retention periods |
| **Right to access** | Provide recording/transcript on request (within 30 days) |
| **Right to erasure** | Delete recording/transcript on request (within 30 days) |
| **Right to object** | Allow users to object to recording at any point |
| **Data protection impact assessment** | Required if processing voice data at scale |

### Right to Deletion

```python
import os
from pathlib import Path

class VoiceDataDeletion:
    """Handle GDPR deletion requests for voice data."""

    def __init__(self, recordings_dir: str, transcripts_dir: str, db_client):
        self.recordings_dir = Path(recordings_dir)
        self.transcripts_dir = Path(transcripts_dir)
        self.db = db_client

    async def delete_caller_data(self, caller_id: str) -> dict:
        """Delete all voice data for a caller. Returns deletion summary."""
        deleted = {"recordings": 0, "transcripts": 0, "metadata": 0}

        # Delete recordings
        for recording in self.recordings_dir.glob(f"*{caller_id}*"):
            recording.unlink()
            deleted["recordings"] += 1

        # Delete transcripts
        for transcript in self.transcripts_dir.glob(f"*{caller_id}*"):
            transcript.unlink()
            deleted["transcripts"] += 1

        # Delete database records
        count = await self.db.delete_call_records(caller_id=caller_id)
        deleted["metadata"] = count

        # Log deletion (without PII — log only that deletion occurred)
        log_deletion_event(caller_id_hash=hash(caller_id), counts=deleted)

        return deleted
```

### Data Retention Policy

| Data Type | Default Retention | Rationale |
|-----------|------------------|-----------|
| Call recordings | 90 days | Quality review period |
| Transcripts | 90 days | Same as recordings |
| Call metadata (no PII) | 2 years | Analytics and reporting |
| Consent records | 7 years | Legal evidence retention |
| PII in CRM | Until deletion requested | Active customer relationship |

---

## Voice Biometric Consent

### When Voice Biometrics Apply

Voice biometrics apply when your system creates or stores a "voiceprint" — a mathematical representation of a person's voice used for identification or verification.

**This applies if you:**
- Use voice to verify caller identity ("speak your passphrase")
- Create speaker embeddings for caller identification
- Use voice similarity to match callers across sessions

**This does NOT apply if you:**
- Simply transcribe speech (STT) without creating biometric templates
- Use VAD (voice activity detection) without speaker identification

### Consent Requirements by Jurisdiction

| Jurisdiction | Law | Requirement |
|-------------|-----|-------------|
| **Illinois** | BIPA | Written consent before creating voiceprint. Disclose purpose and retention. $1,000-5,000 per violation. |
| **Texas** | CUBI | Informed consent required. No private right of action (state AG enforces). |
| **Washington** | Biometric law | Notice required. Consent for commercial purposes. |
| **EU** | GDPR Art. 9 | Explicit consent required for biometric data processing. |
| **UK** | UK GDPR | Same as EU — explicit consent for biometric processing. |

**Default**: Do not create voiceprints without explicit opt-in consent. If you do not need biometric identification, avoid storing any voice embeddings.

---

## PII in Transcripts

### PII Categories in Voice Data

| PII Type | Example in Speech | Risk Level | Redaction Priority |
|----------|------------------|------------|-------------------|
| **Credit card number** | "My card is 4111 1111 1111 1111" | Critical | Immediate |
| **SSN** | "My social is 123-45-6789" | Critical | Immediate |
| **Account number** | "Account number 98765432" | High | Before storage |
| **Date of birth** | "I was born on March 15, 1990" | High | Before storage |
| **Full name** | "My name is John Smith" | Medium | Optional |
| **Address** | "I live at 123 Main Street" | Medium | Before storage |
| **Phone number** | "Call me at 555-0123" | Medium | Before long-term storage |
| **Email** | "My email is john at example dot com" | Medium | Before long-term storage |

### Real-Time PII Redaction

```python
import re

class TranscriptRedactor:
    """Redact PII from STT transcripts in real-time."""

    PATTERNS = {
        "credit_card": re.compile(
            r"\b(?:\d[ -]*?){13,19}\b"
        ),
        "ssn": re.compile(
            r"\b\d{3}[-. ]?\d{2}[-. ]?\d{4}\b"
        ),
        "phone": re.compile(
            r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b"
        ),
        "email": re.compile(
            r"\b[\w.+-]+\s*(?:at|@)\s*[\w.-]+\s*(?:dot|\.)\s*\w+\b",
            re.IGNORECASE,
        ),
        "dob": re.compile(
            r"\b(?:born|birthday|date of birth|dob)\b.*?\b\d{1,2}[-/. ]\d{1,2}[-/. ]\d{2,4}\b",
            re.IGNORECASE,
        ),
    }

    REPLACEMENTS = {
        "credit_card": "[CARD_REDACTED]",
        "ssn": "[SSN_REDACTED]",
        "phone": "[PHONE_REDACTED]",
        "email": "[EMAIL_REDACTED]",
        "dob": "[DOB_REDACTED]",
    }

    def redact(self, text: str) -> tuple[str, list[str]]:
        """Redact PII from text. Returns (redacted_text, list_of_redacted_types)."""
        redacted_types = []
        for pii_type, pattern in self.PATTERNS.items():
            if pattern.search(text):
                text = pattern.sub(self.REPLACEMENTS[pii_type], text)
                redacted_types.append(pii_type)
        return text, redacted_types
```

### Post-Processing PII Redaction

For recordings (audio), use provider PII redaction features:

| Provider | Feature | How |
|----------|---------|-----|
| **Deepgram** | Redact PII in transcripts | `redact=["pci", "ssn", "numbers"]` parameter |
| **AssemblyAI** | PII Redaction | `redact_pii=True`, `redact_pii_audio=True` for audio redaction |
| **Azure** | Content filtering | Built-in PII detection and masking |

For audio-level redaction (beeping out PII in recordings), use post-processing:
1. Run transcript with PII detection to get timestamps of PII segments
2. Replace those audio segments with silence or a beep tone
3. Store only the redacted recording

### Storage Policies

| Data | Encryption | Access Control | Retention | PII Redacted |
|------|-----------|----------------|-----------|-------------|
| Live audio stream | TLS in transit | Pipeline only | Not stored | N/A |
| Call recordings | AES-256 at rest | Role-based (support leads) | 90 days | Optional |
| Transcripts (raw) | AES-256 at rest | Role-based | 30 days | No |
| Transcripts (redacted) | AES-256 at rest | Role-based | 90 days | Yes |
| Call metadata | AES-256 at rest | Analytics team | 2 years | Yes (no PII) |
| Consent records | AES-256 at rest | Legal/compliance | 7 years | Minimal PII |

---

## Compliance Checklist by Jurisdiction

### United States

- [ ] **Recording consent**: Announce recording at start of every call
- [ ] **Two-party states**: Get explicit consent when caller is in CA, FL, IL, PA, WA, etc.
- [ ] **TCPA (outbound)**: Prior express consent, DNC scrub, calling hours 8AM-9PM local
- [ ] **TCPA (marketing)**: Prior express written consent for marketing autodial/prerecorded
- [ ] **PCI DSS**: Pause recording during card collection, never store CVV
- [ ] **HIPAA (healthcare)**: BAA with providers, encrypt PHI, access controls
- [ ] **BIPA (Illinois)**: Written consent before creating voiceprints
- [ ] **CCPA (California)**: Right to know, right to delete voice data
- [ ] **ADA**: Provide alternative channels for hearing-impaired callers

### European Union (GDPR)

- [ ] **Lawful basis**: Document lawful basis for processing voice data (consent or legitimate interest)
- [ ] **Explicit consent**: Get explicit consent before recording, with easy opt-out
- [ ] **Privacy notice**: Inform callers of data controller, purpose, retention, rights
- [ ] **DPIA**: Complete Data Protection Impact Assessment for voice processing at scale
- [ ] **Right to access**: Provide recording/transcript within 30 days on request
- [ ] **Right to erasure**: Delete all voice data within 30 days on request
- [ ] **Data minimization**: Only collect voice data necessary for stated purpose
- [ ] **Cross-border transfers**: Standard Contractual Clauses if data leaves EEA
- [ ] **Biometric consent**: Explicit consent if creating voiceprints (Art. 9)

### United Kingdom

- [ ] **UK GDPR + DPA 2018**: Same as EU GDPR requirements above
- [ ] **ICO registration**: Register as data controller with ICO
- [ ] **Recording disclosure**: Inform caller that recording is in progress
- [ ] **Ofcom rules**: Comply with calling regulations for outbound
- [ ] **PCI DSS**: Same as US requirements

### Australia

- [ ] **Privacy Act 1988**: Comply with Australian Privacy Principles (APPs)
- [ ] **State recording laws**: All-party consent in QLD, VIC, TAS, WA
- [ ] **Do Not Call Register**: Check DNCR before outbound calls
- [ ] **Spam Act 2003**: Consent required for commercial calls
- [ ] **Calling hours**: Mon-Fri 9AM-8PM, Sat 9AM-5PM, no Sun/public holidays

### Canada

- [ ] **PIPEDA**: Consent for collection, use, disclosure of personal information
- [ ] **CASL**: Consent for commercial electronic messages (includes some voice)
- [ ] **CRTC Telecom Rules**: National DNCL check, calling hours
- [ ] **Provincial laws**: Quebec, Alberta, BC have additional privacy legislation
- [ ] **Recording**: Federal one-party consent, some provinces stricter

---

## Incident Response for Voice Data Breaches

### Voice Data Breach Scenarios

| Scenario | Severity | Data at Risk |
|----------|----------|-------------|
| Recording storage compromised | Critical | All call recordings with PII |
| STT transcript database leaked | High | All transcribed conversations |
| Voiceprint database leaked | Critical | Biometric data (irreplaceable) |
| WebSocket stream intercepted | High | Live audio (real-time PII) |
| Unauthorized access to call logs | Medium | Metadata, phone numbers |
| Third-party provider breach | High | Depends on data shared |

### Incident Response Playbook

**Phase 1: Contain (0-4 hours)**
1. Identify scope: which recordings/transcripts/data were exposed
2. Revoke compromised credentials and API keys
3. Isolate affected systems (disable access to recording storage)
4. Preserve evidence (don't delete logs)

**Phase 2: Assess (4-24 hours)**
1. Determine what PII was in the exposed data
2. Identify affected individuals (callers whose data was exposed)
3. Assess whether data was actually accessed or just exposed
4. Determine if biometric data (voiceprints) was involved

**Phase 3: Notify (24-72 hours)**

| Jurisdiction | Notification Deadline | Who to Notify |
|-------------|----------------------|---------------|
| US (varies by state) | 30-60 days (CA: 72 hours for biometric) | Affected individuals + state AG |
| EU (GDPR) | 72 hours to DPA; without undue delay to individuals | Data Protection Authority + affected individuals |
| UK | 72 hours to ICO | ICO + affected individuals |
| Australia | 30 days | OAIC + affected individuals |
| Canada | As soon as feasible | OPC + affected individuals |

**Phase 4: Remediate**
1. Patch the vulnerability that caused the breach
2. Rotate all API keys and access credentials
3. If voiceprints were leaked, notify all affected users and invalidate voiceprints
4. Review and tighten access controls
5. Conduct post-incident review
6. Update incident response plan based on learnings

---

## Related References

- [telephony-platform-selection.md](telephony-platform-selection.md) — Platform compliance certifications
- [ivr-design.md](ivr-design.md) — TCPA compliance for outbound dialing
- [voice-quality-metrics.md](voice-quality-metrics.md) — Call recording for quality monitoring
- [voice-pipeline-architecture.md](voice-pipeline-architecture.md) — Where PII flows through the pipeline
