"""Anthropic LLM adapter — `LLMClient` Protocol.

Thin wrapper around the official `anthropic` SDK. Lazy-imported so the
core package stays usable without the dep installed.

Two reasons this lives in the kit even though the kit is provider-neutral:
1. The Phase 4 eval suites need *some* real LLM to be meaningful.
2. It documents the minimum surface a provider adapter must implement.

Add an OpenAI / Google / local adapter the same way — implement
`complete` and `count_tokens`, lazy-import the SDK, keep the rest.
"""

from __future__ import annotations

import os
from typing import Any


class AnthropicLLM:
    """Satisfies the `LLMClient` Protocol against Anthropic's API.

    Defaults to a fast, cheap model so eval suites stay affordable. Override
    via the constructor for production wiring.

    The default is a tier alias, not a dated snapshot: aliases keep resolving to
    the current snapshot of that tier, so this adapter does not start 404-ing
    when a snapshot is retired. Pin a dated snapshot at the call site if you
    need byte-reproducible output.
    """

    def __init__(
        self,
        *,
        model: str = "claude-haiku-4-5",
        api_key: str | None = None,
        client: Any = None,
        temperature: float = 0.0,
    ) -> None:
        self._model = model
        self._temperature = temperature
        if client is not None:
            self._client = client
        else:
            from anthropic import Anthropic  # lazy
            self._client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    def complete(
        self,
        *,
        system: str,
        messages: list[dict[str, str]],
        max_tokens: int,
    ) -> str:
        resp = self._client.messages.create(
            model=self._model,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
            temperature=self._temperature,
        )
        # Newer SDKs return a list of content blocks; old ones a single string.
        try:
            return "".join(
                block.text for block in resp.content if getattr(block, "type", None) == "text"
            )
        except (AttributeError, TypeError):
            return str(getattr(resp, "completion", resp))

    def count_tokens(self, text: str) -> int:
        """Best-effort token count.

        The Anthropic SDK exposes a token-count endpoint that round-trips to
        the API. We avoid that on the hot path because every `compress` call
        would otherwise hit the network. The local approximation (~4 chars
        per token) is good enough for budget checks; for billing-grade
        accuracy, swap in `client.beta.messages.count_tokens(...)` and
        cache the result.
        """
        return max(1, len(text) // 4)
