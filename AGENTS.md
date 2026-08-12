# AGENTS.md — wechat-mp

Source of truth for agents editing this product skill.

## Purpose

WeChat Official Account (**公众号**) skill in the kedoupi suite:

- **Owns:** writing quality rails, output `manifest.json`, MD→WeChat HTML, draft/upload API  
- **Does not own:** image generation (`tzai-image`), Feishu send (`lark-push`)  
- **Compose:** soft-detect peers; degrade; never vendor their code  

## Layout

```text
skills/wechat-mp/             # installable package
  SKILL.md
  config.example.env
  scripts/wechat-mp
  scripts/lib/
  references/
  templates/
docs/
  README.md                   # guides + golden-path demo notes
tests/
  README.md
  run.sh
  fixtures/
artifacts/                    # optional future skill-repo live dumps (none yet)
```

**docs / tests / artifacts:** incubator separation applies.  
**User articles** live under the content project `wechat-mp-out/`, not in this repo.

## Conventions

- Version SoT: `skills/wechat-mp/SKILL.md` → `metadata.version`  
- **Config (recommended):** `~/.config/kedoupi/wechat-mp/config.env` (+ `style.yaml`)  
- Legacy still read / one-shot migrate: `.skill-data/wechat-mp/`, `~/.config/wechat-mp/`  
- Public keys only: `WECHAT_MP_*` — never edit the user's shell rc for secrets  

- `--dry-run` must stay offline  
- CLI option values may start with `-`  
- No secrets in the package; no mass-publish APIs  
- Bump version on behavior change  
- **Article outputs** live under the **content project**: `<project>/wechat-mp-out/<slug>/`. That folder is intentional history for the next session (`list-out`). Default `--base ./wechat-mp-out` is CWD-relative — agents must `cd` to (or pass) the user's project, **not** the skill install path and **not** `kedoupi/skills` incubator root.  

## Suite discipline

1. Single responsibility  
2. Standalone install must write useful articles  
3. Composition via paths + `manifest.json`, not hard imports  
4. Separate keys: `WECHAT_MP_*` / `TZAI_*` / lark config  

## Validation

```bash
bash tests/run.sh
npx skills add ./ --list
bash skills/wechat-mp/scripts/wechat-mp doctor
```

## Incubator

When this repo is a submodule of `kedoupi/skills`, also follow parent `AGENTS.md` and update the parent **README catalog** on version/public changes.
