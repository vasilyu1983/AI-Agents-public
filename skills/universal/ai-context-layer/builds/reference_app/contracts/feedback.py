from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class FeedbackOutcome:
    """Backend feedback record. Updates derived memory only — never operational
    truth (A2 in reverse)."""

    id: str
    entity_id: str
    entity_type: str
    source_type: str
    """e.g. 'inline_reaction', 'support_correction', 'eval_label'."""

    source_id: str
    outcome_type: str
    """e.g. 'memory_confirmed', 'memory_corrected', 'response_off'."""

    status: str
    """'pending' | 'applied' | 'rejected'."""

    impact_score: float
    details: dict[str, Any]
    measured_at: datetime
    owner_scope: dict[str, str]


@dataclass(slots=True)
class InlineReactionFeedback:
    """Lightweight per-response reaction tied to a specific bundle.

    The `context_bundle_id` is the correlation key — it lets the backend
    update the confidence of the exact memories that informed the response,
    not just track an aggregate satisfaction score."""

    context_bundle_id: str
    reaction: str
    """Use 2-3 options, not 5-star scales. 'resonated' | 'neutral' | 'off'."""

    surface: str
    timestamp: datetime
    actor: dict[str, str] = field(default_factory=dict)
