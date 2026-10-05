"""Postgres-backed EpisodeLog.

Append-only by contract. The adapter exposes no update or delete method
because the audit spine must remain whole — if you "fix" an episode you
have just lied to every memory that points at it.
"""

from __future__ import annotations

import json
from typing import Any
from uuid import uuid4


class PostgresEpisodeLog:
    """Satisfies the `EpisodeLog` Protocol.

    Caller passes a psycopg connection (sync). The adapter does not own
    pooling — wire it up at the application layer with `psycopg_pool`.
    """

    def __init__(self, conn: Any) -> None:
        self._conn = conn

    def append(self, *, episode: dict[str, Any]) -> str:
        eid = episode.get("id") or f"ep_{uuid4().hex[:16]}"
        owner_scope = episode.get("owner_scope")
        if not owner_scope:
            raise ValueError("episode.owner_scope is required (A10)")
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO episode_log (id, episode, owner_scope)
                VALUES (%s, %s::jsonb, %s::jsonb)
                """,
                (eid, json.dumps(episode), json.dumps(owner_scope)),
            )
        self._conn.commit()
        return eid

    def get(self, episode_id: str) -> dict[str, Any] | None:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT episode FROM episode_log WHERE id = %s",
                (episode_id,),
            )
            row = cur.fetchone()
        return row[0] if row else None
