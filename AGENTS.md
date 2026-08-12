# AGENTS.md — wechat-mp

Source of truth for agents editing this product skill.

## Purpose

WeChat Official Account (**公众号**) skill in the kedoupi suite:

- **Owns:** writing quality rails, output `manifest.json`, MD→WeChat HTML, draft/upload API  
- **Does not own:** image generation (`tzai-image`), Feishu send (`lark-push`)  
- **Compose:** soft-detect peers; degrade; never vendor their code  

## Layout

```text
skills/wechat-mp/
  SKILL.md
  config.example.env          # WeChat credentials only
  scripts/wechat-mp           # bash CLI
  scripts/lib/md2html.py
  scripts/lib/wechat_api.py
  references/                 # brief, frameworks, review, compose, constraints
  templates/                  # article + style.example
tests/run.sh
```

## Conventions

- Version SoT: `skills/wechat-mp/SKILL.md` → `metadata.version`  
- Durable WeChat config: `<skills-parent>/.skill-data/wechat-mp/config.env`  
- Durable style (no appid): same dir `style.yaml` via `init-style`  
- `--dry-run` must stay offline  
- CLI option values may start with `-`  
- No secrets in the package; no mass-publish APIs  
- Bump version on behavior change  
- **Article outputs** (`wechat-mp-out/`, previews, covers) are **user content**, not package or incubator tree. Default `--base ./wechat-mp-out` is relative to the **writer's CWD** (a content project). Never write run outputs into `kedoupi/skills` monorepo root or into `skills/wechat-mp/` package paths.  

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
