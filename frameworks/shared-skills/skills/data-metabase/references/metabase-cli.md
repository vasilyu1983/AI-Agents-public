# Metabase CLI reference

Two distinct command-line surfaces. Don't confuse them.

## 1. `mb` — the API client CLI (content automation)

npm-installed tool that reads/writes Metabase content (questions, dashboards, collections,
transforms) over the REST API. Built for scripting and AI agents. Requires **Metabase v58+**
and an **API key**; some features (e.g. Remote Sync) need Pro/Enterprise.
Docs: https://www.metabase.com/docs/latest/installation-and-operation/metabase-cli

```bash
npm install -g @metabase/cli

mb auth login --url https://metabase.example.com   # prompts for API key (or $METABASE_API_KEY)
mb auth login --profile prod --url https://prod.example.com   # named profiles for multiple instances
mb auth list
mb auth status
mb logout
mb --help
```

The built-in **MCP server** (v60+) is usually the preferred path for conversational/agent
content work (OAuth, per-user permissions, no API key to manage) — see [agent-api.md](agent-api.md)
and the MCP rows in `SKILL.md`. Reach for `mb` only when you need an API-key/service-account
flow or scripted bulk content ops outside an MCP session.

## 2. JAR commands — server administration

Run against the Metabase server jar; for operators, not for content automation.
Docs: https://www.metabase.com/docs/latest/installation-and-operation/commands

```bash
java -jar metabase.jar <command>
```

| Command | Purpose |
|---------|---------|
| `help` | list valid commands |
| `version` | Metabase + system version |
| `migrate up\|force\|down\|down-force\|print\|release-locks` | run/inspect app-DB migrations |
| `reset-password <email>` | reset a user's password |
| `load-from-h2` | migrate H2 app-DB → MySQL/Postgres (env-configured) |
| `dump-to-h2` | dump app-DB → H2 (`-k/--keep-existing`, `-p/--dump-plaintext`) |
| `environment-variables-documentation` | markdown of env vars |
| `config-template` | YAML config template with defaults |
| `api-documentation` | generate HTML/JSON API docs |
| `command-documentation` | markdown of all CLI commands |
| `rotate-encryption-key` | rotate `MB_ENCRYPTION_SECRET_KEY` (new key 16+ chars) |
| `remove-encryption` | decrypt app-DB |
| `seed-entity-ids` / `drop-entity-ids` | manage serialization entity IDs |
| `export` / `import` | **Enterprise** serialization to/from a directory (`-c` collection, `-C` no-collections, `-S` no-settings, `-D` no-data-model, `-f` include-field-values, `-s` include-db-secrets) |
| `driver-methods` / `generate-openapi-spec` | developer utilities |

`migrate`, `reset-password`, encryption, and serialization commands change server state —
run only with operator authorization and a backup of the application database.
