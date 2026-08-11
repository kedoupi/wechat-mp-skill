# Compose with kedoupi suite

`wechat-mp` is one service in the suite. **Soft peers** — never hard-require their code.

## Peer ownership

| Skill | Owns | Does not own |
| --- | --- | --- |
| `wechat-mp` | 公众号写作质量、MD→HTML、微信草稿 | 生图、飞书发送 |
| `tzai-image` | 文生图 / kinds | 公众号文案与 draft API |
| `lark-push` | 飞书消息 | 生图、微信凭证 |

## Detect peers

```bash
for c in \
  "$HOME/.agents/skills/tzai-image/scripts/tzai-image" \
  "$HOME/.claude/skills/tzai-image/scripts/tzai-image" \
  "$HOME/.grok/skills/tzai-image/scripts/tzai-image" \
  "$HOME/.codex/skills/tzai-image/scripts/tzai-image"
do
  [ -x "$c" ] && TZAI="$c" && break
done

for c in \
  "$HOME/.agents/skills/lark-push/scripts/lark-push" \
  "$HOME/.claude/skills/lark-push/scripts/lark-push" \
  "$HOME/.grok/skills/lark-push/scripts/lark-push"
do
  [ -x "$c" ] && LARK="$c" && break
done
```

Or: `bash <wechat-mp>/scripts/wechat-mp suite`

## Handoff: `manifest.json`

Output dir (from `wechat-mp new-out`):

```text
wechat-mp-out/<slug>/
  manifest.json
  brief.md
  article.md
  cover.png          # after visual
  figures/
  preview.html
```

Update status after each step:

```bash
bash scripts/wechat-mp manifest-set --dir "$OUT" --status article=done --title "标题"
bash scripts/wechat-mp manifest-set --dir "$OUT" --status visual=done
```

## Mode B — cover via tzai-image

If `$TZAI` exists and user asked 配图/完整制作:

```bash
bash "$TZAI" wechat \
  --prompt "<文章主题与情绪，短句>" \
  --image "$OUT/cover.png"
# or: cover --type conceptual …
```

Cost guardrails: **1 cover**, **0–3** body figures. Failures → keep article; write prompts to `cover-prompt.txt` if needed.

If `$TZAI` missing:

```text
提示用户: npx skills add kedoupi/tzai-image-skill -g --all
仍交付 article.md；可附封面提示词。
```

## Mode D — notify via lark-push

Only if user asked 飞书通知 and `$LARK` works:

```bash
bash "$LARK" --kind notice --title "公众号成稿：${TITLE}" --body "- path: ${OUT}
- draft: ${MEDIA_ID:-local only}"
```

If missing: skip notify; do not fail the article.

## Recipes

1. **Write only:** `npx skills add kedoupi/wechat-mp-skill`  
2. **Write + visual:** + `tzai-image-skill`  
3. **Full:** + `lark-push-skill` + `wechat-mp init` for drafts  
