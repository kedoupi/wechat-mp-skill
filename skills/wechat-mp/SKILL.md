---
name: wechat-mp
description: Use when the user asks to ... [trigger description that tells agents when to invoke this skill]
metadata:
  author: kedoupi
  version: "0.1.0"
  requires:
    bins: []
---

# wechat-mp

[One paragraph: what this skill does, default behavior, key constraints.]

## Prerequisites

```bash
# Verify required CLI / auth
# <cli> auth status --verify
```

## Locating the helper

```bash
# Common install locations:
#   Canonical / symlink source: ~/.agents/skills/wechat-mp/
#   Claude:  ~/.claude/skills/wechat-mp/
#   Codex:   ~/.codex/skills/wechat-mp/
#   Project: ./.agents/skills/wechat-mp/
```

Scripts resolve their real path with `pwd -P` so symlink installs share one config.

## Config

One-time after install (if this skill needs durable config):

```bash
bash <skill-dir>/scripts/wechat-mp init --chat-id <id>
```

Config is stored **outside** the skill package (survives `npx skills update`).
See incubator schema: durable path is `<skills-parent>/.skill-data/wechat-mp/config.env`.

Inspect:

```bash
bash <skill-dir>/scripts/wechat-mp config-path
bash <skill-dir>/scripts/wechat-mp which-config
```

## Safety

[Describe what agents must confirm before taking real action.]

If the user runs the helper script directly, that invocation is the approval.
For previews, use `--dry-run` (must stay offline / side-effect free).

## Usage

```bash
# Preview (local only)
bash <skill-dir>/scripts/wechat-mp --dry-run --title "Example" --body "- item"

# Real action
bash <skill-dir>/scripts/wechat-mp --title "Hello" --body "World"
```

## Key CLI options

```text
--title <text>
--body <text>     # may start with '-'
--dry-run         # local preview only
```

Full reference: `bash <skill-dir>/scripts/wechat-mp --help`.
