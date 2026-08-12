---
name: wechat-mp
description: >
  Use when the user wants to write a WeChat Official Account (微信公众号) article,
  推文, 草稿箱 draft, or WeChat-oriented markdown→HTML preview/排版 for 公众号.
  Modes: write a solid local article (default), optional cover via tzai-image suite peer,
  optional draft push, optional lark-push notify. Triggers: 公众号, 微信推文, 写一篇公众号,
  草稿箱, 微信排版, wechat mp, official account article.
  Not for: pure image generation only (use tzai-image / tzai-wechat), pure Feishu/Lark
  chat messages (use lark-push), Xiaohongshu posts, generic blogs without 公众号 intent.
metadata:
  author: kedoupi
  version: "0.1.2"
  requires:
    bins: ["python3"]
---

# WeChat MP (`wechat-mp`)

Kedoupi suite skill for **WeChat Official Account content**: write a good article locally,
optionally compose with **`tzai-image`** (cover) and **`lark-push`** (notify), optionally
push a **draft** when credentials and explicit user permission exist.

**Single-install value:** article quality rails + local preview.  
**No WeChat appid required** for modes A/B (write / full local make).

## Suite rules

| Skill | Role |
| --- | --- |
| **This skill** | Writing quality, output dir + `manifest.json`, MD→HTML, WeChat draft API |
| **`tzai-image`** | Images only (soft peer) |
| **`lark-push`** | Feishu messages only (soft peer) |

Do **not** reimplement image APIs or Feishu send inside this skill. Soft-detect peers; degrade.

## Prerequisites

```bash
bash <skill-dir>/scripts/wechat-mp doctor
```

| Need | Required for |
| --- | --- |
| **python3** | preview / draft helpers |
| **WeChat appid/secret** | draft / upload only |
| **tzai-image** (optional) | generated cover |
| **lark-push** (optional) | completion notify |

```bash
# Optional WeChat API (draft)
bash <skill-dir>/scripts/wechat-mp init --appid wx… --secret …

# Optional account voice (no appid)
bash <skill-dir>/scripts/wechat-mp init-style
```

## Locating the helper

```text
~/.agents/skills/wechat-mp/scripts/wechat-mp
# also: ~/.claude|~/.codex|~/.grok|~/.cursor/skills/wechat-mp/
```

## Safety (defaults)

| Action | Default | Allow when |
| --- | --- | --- |
| Write local article | on | 「写一篇公众号」 |
| Paid image gen | **off** | 「配图 / 完整制作」 or clear approval |
| Feishu notify | **off** | explicit 通知 + lark configured |
| WeChat draft | **off** | 「推草稿箱」 + init credentials |

- User running the CLI counts as approval for that invocation.  
- **No mass-send / freepublish** in this skill.  
- No cover → do not pretend draft succeeded.  
- `--dry-run` never touches the network.

## Modes

### A — 写一篇（default）

1. Read `templates/style.example.yaml` path or durable style if present.  
2. `wechat-mp new-out --title "…" --base ./wechat-mp-out` → `$OUT`  
   Use a **content workspace** CWD (or explicit `--base` under the user's writing project).  
   Do **not** create `wechat-mp-out` inside the `kedoupi/skills` incubator monorepo root.  
3. Read and apply:
   - `references/article-brief.md` → write `$OUT/brief.md`
   - `references/frameworks.md` → pick one framework
4. Draft body → self-review with `references/editorial-review.md`  
5. Only on **pass**: write `$OUT/article.md`  
6. `manifest-set --dir "$OUT" --status article=done --title "…"`  
7. Deliver paths. **Stop** unless user asked for images/draft/notify.

Typical length: ~1200–2500 Chinese characters unless brief says otherwise.

### B — 完整制作（local）

After A is sealed:

1. Read `references/compose-with-suite.md`  
2. If tzai-image found: generate **one** cover → `$OUT/cover.png` (kind `wechat` or `cover`). Optional 0–3 figures under `$OUT/figures/`.  
3. If tzai missing: write cover prompt file; still keep article.  
4. `wechat-mp preview --dir "$OUT"`  
5. Update manifest `visual` / `preview`. **Still not a draft push.**

### C — 推草稿箱

Only if user clearly asked this turn:

```bash
bash <skill-dir>/scripts/wechat-mp draft --dir "$OUT"
# or offline:
bash <skill-dir>/scripts/wechat-mp draft --dir "$OUT" --dry-run
```

Requires cover file + `init` credentials. Local body images in HTML are uploaded
via `uploadimg` and rewritten to CDN URLs before `draft/add`. See
`references/wechat-constraints.md`.

### D — 飞书通知（optional）

If user asked and lark-push is available, send a short notice with title + `$OUT` + optional `draft_media_id`. Skip if missing.

## CLI quick ref

```bash
bash <skill-dir>/scripts/wechat-mp doctor
bash <skill-dir>/scripts/wechat-mp suite
bash <skill-dir>/scripts/wechat-mp new-out --title "主题"
bash <skill-dir>/scripts/wechat-mp preview --dir ./wechat-mp-out/<slug>
bash <skill-dir>/scripts/wechat-mp draft --dir ./wechat-mp-out/<slug> --dry-run
bash <skill-dir>/scripts/wechat-mp --help
```

## Output contract

```text
wechat-mp-out/<slug>/
  manifest.json    # suite handoff
  brief.md
  article.md
  cover.png
  figures/
  preview.html
```

## Troubleshooting

1. `doctor` — fix `[FAIL]` lines  
2. Draft errors — check appid permissions; cover present; Chinese JSON (helper uses `ensure_ascii=False`)  
3. No cover gen — install tzai-image; writing still valid  
4. `which-config` — confirm durable credentials path  
