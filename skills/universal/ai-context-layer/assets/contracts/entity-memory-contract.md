# Entity And Memory Contract

## EntityProfile

- `id`
- `entity_type`
- `owner_scope`
- `source_of_truth`
- `updated_at`
- `acl_tags`

## LearnedMemory

- `id`
- `entity_id`
- `entity_type`
- `memory_type`
- `value`
- `source`
- `source_episode_id` — stable pointer to the raw input (conversation turn, document, event) the fact was derived from; enables "trace sources" and reverification when the fact is challenged
- `confidence`
- `created_at`
- `updated_at`
- `valid_from` / `valid_to` — validity window: when the fact became true in the world and (if applicable) when it stopped being true
- `invalidated_at` — distinct from `expires_at`: set when the fact is **superseded by newer evidence** (non-destructive), not because of a TTL rollover
- `expires_at` — TTL-based lifetime, independent of supersession
- `owner_scope`
- `inferred`

Bi-temporal note: `valid_from`/`valid_to` are *fact* time; `created_at`/`invalidated_at` are *system* time. They diverge whenever a fact is learned or corrected retroactively. Preserve both — it's the only way to answer "what did we know on date X" vs "what was true on date X" without overwriting history.
