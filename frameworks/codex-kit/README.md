# Codex Kit — Skills

**Status**: PRODUCTION-READY
**Version**: 2.1
**Last Updated**: 2025-12-20
**Skills Source**: `frameworks/shared-skills/` (shared with Claude Code Kit)

## Overview

Codex Kit provides a Codex-native Agent Skills library you can copy into any repository. Skills are defined by `SKILL.md` files and follow the Agent Skills specification. Codex loads skills natively; no router prompts or Claude-specific bridges are required.

**NEW in v2.1**: Skills now maintained in shared source. Run `./frameworks/sync-skills.sh` to sync from `shared-skills/`.

## Contents

```
frameworks/codex-kit/
├── README.md
├── docs/                         # Codex skills documentation (user + author guides)
├── framework/
│   ├── README.md                 # Codex skills guide
│   └── sync-skills.sh            # Wrapper for ./frameworks/sync-skills.sh
```

## Quick Start

Copy the skills to a Codex skills location:

```
mkdir -p .codex/skills
cp -R frameworks/shared-skills/skills/* .codex/skills/
```

Or keep `frameworks/shared-skills/skills/` as the source of truth and sync into both workspaces:

```
./frameworks/sync-skills.sh
```

Codex discovers skills automatically. For the full guide, see `frameworks/codex-kit/framework/README.md`.

If you use Claude Code in the same repo, copy the same skills to `.claude/skills/` as well.
