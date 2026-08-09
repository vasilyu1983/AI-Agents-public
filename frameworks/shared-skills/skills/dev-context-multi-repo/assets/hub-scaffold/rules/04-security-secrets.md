# Rule 04 — Security & Secrets

> **Stub.** Replace with your own security policy. Illustrative scaffolding.

Non-negotiable security constraints for agents touching the portfolio or
this hub.

## What goes here (replace)

- Never commit secrets, credentials, tokens, private keys, or connection
  strings — into source repos *or* into hub markdown/profiles/graphs.
- Never reproduce a discovered secret into a report or chat answer; record
  only its location and that it must be rotated.
- Treat scan output that includes secrets as restricted; redact before it
  enters the compiled layer.
- Where to report a discovered exposure (named owner / channel).

Pair with `rules/02-data-handling.md` for the data-classification labels
the compiled layer must carry.
