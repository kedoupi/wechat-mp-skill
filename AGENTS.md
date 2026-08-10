# AGENTS.md

Guidance for AI coding agents working on the `wechat-mp` skill.

This skill is scaffolded from the incubator template. Cross-skill conventions live in
the incubator docs (`schema/skill-repo.md`, root `AGENTS.md`) when working inside the
local Skills workspace; they are **not** published as part of this skill repo.

When **creating or editing skills inside the incubator**, agents should follow the
project meta skill `.agents/skills/skill-incubator/` (not shipped in this package).

This file is the **source of truth** for agents in this skill repo. If `CLAUDE.md`
exists, it should only point here.

## Purpose

[One-line description.]

## Layout

```text
skills/
  wechat-mp/        # skill package (discovered by skills CLI)
    SKILL.md           # required skill definition (version source of truth)
    config.example.env
    scripts/           # executable helpers
    templates/         # optional body templates
tests/
  run.sh               # offline self-test
```

## Editing rules

- Keep `SKILL.md` under ~500 lines; put long references in separate files.
- Do not hardcode private credentials or team-specific identifiers.
- Scripts must resolve their own directory with `pwd -P` so symlink installs work.
- Minimize runtime dependencies.
- Bump `metadata.version` in `SKILL.md` when behavior changes.
- `--dry-run` must stay offline / side-effect free.
- CLI values may start with `-` (markdown lists).

## Local validation

```bash
bash tests/run.sh
npx skills add ./ --list
bash skills/wechat-mp/scripts/wechat-mp --help
```
