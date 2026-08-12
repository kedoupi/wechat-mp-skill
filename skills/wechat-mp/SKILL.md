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
  version: "0.2.1"
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

## Onboarding (install ≠ configure)

**Do not** ask for `appid`/`secret` just because the skill was installed or the
user said “写一篇公众号”. Mode A (local article) works with zero WeChat config.

| When | Agent action |
| --- | --- |
| Write / preview only | Proceed; no secrets |
| User wants **draft box** and config missing | Explain why + paste `init` block below; offer dry-run / local-only degrade |
| User wants cover / notify | Soft-detect peers; if missing keys there, use those skills’ `init` hints |
| User asks “装好了吗 / doctor” | Run `doctor` (prints copy-paste setup when draft config missing) |

Copy-paste (writes `~/.config/kedoupi/wechat-mp/config.env` — **not** shell rc):

```bash
bash <skill-dir>/scripts/wechat-mp init \
  --appid 'wx_YOUR_APPID' \
  --secret 'YOUR_APPSECRET'
# optional IP-whitelist proxy:
#   --api-base 'https://YOUR_PROXY_HOST'

bash <skill-dir>/scripts/wechat-mp init-style   # optional account voice
bash <skill-dir>/scripts/wechat-mp doctor
```

If the user pastes appid/secret in chat, generate the same `init` command (or run
it with their approval). Never invent credentials; never put secrets only inside
the skill package.

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

**Output home = the content project**, not the skill install path and not the
`kedoupi/skills` incubator monorepo.

```text
<your-project>/                 # cd here (user's writing / product repo)
  wechat-mp-out/                # project-local history (commit if you want)
    <slug-a>/ brief.md article.md …
    <slug-b>/ …
```

1. **CWD** = the project the user is writing in (or pass `--base <project>/wechat-mp-out`).  
2. `wechat-mp list-out` — load prior titles/briefs as **history** (tone, repeated topics, avoid duplicate angles).  
3. Read durable / example style if present.  
4. `wechat-mp new-out --title "…"` → `$OUT` under `./wechat-mp-out/<slug>` (default `--base ./wechat-mp-out`).  
5. Read and apply:
   - `references/article-brief.md` → write `$OUT/brief.md`
   - `references/frameworks.md` → pick one framework
6. Draft body → self-review with `references/editorial-review.md`  
7. Only on **pass**: write `$OUT/article.md`  
8. `manifest-set --dir "$OUT" --status article=done --title "…"`  
9. Deliver paths. **Stop** unless user asked for images/draft/notify.

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
# from the content project root:
bash <skill-dir>/scripts/wechat-mp doctor
bash <skill-dir>/scripts/wechat-mp list-out          # project history
bash <skill-dir>/scripts/wechat-mp new-out --title "主题"
bash <skill-dir>/scripts/wechat-mp preview --dir ./wechat-mp-out/<slug>
bash <skill-dir>/scripts/wechat-mp draft --dir ./wechat-mp-out/<slug> --dry-run
bash <skill-dir>/scripts/wechat-mp --help
```

## Output contract (per content project)

```text
<project>/wechat-mp-out/          # history root (stays with the project)
  README.md                       # auto-created once
  <slug>/
    manifest.json                 # suite handoff + status
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
