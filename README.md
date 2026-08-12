# wechat-mp

**WeChat Official Account** skill for AI agents: write a solid article locally, optionally compose with kedoupi suite peers for images and Feishu notify, optionally push a **draft**.

| Package | Repo | Install |
| --- | --- | --- |
| `wechat-mp` | [kedoupi/wechat-mp-skill](https://github.com/kedoupi/wechat-mp-skill) | `npx skills add kedoupi/wechat-mp-skill` |

Part of the [kedoupi/skills](https://github.com/kedoupi/skills) suite: **standalone or combined**.

| Use case | Install |
| --- | --- |
| Write 公众号 article only | `wechat-mp-skill` |
| Write + cover images | + [tzai-image-skill](https://github.com/kedoupi/tzai-image-skill) |
| + Feishu notify | + [lark-push-skill](https://github.com/kedoupi/lark-push-skill) |
| + WeChat draft box | `wechat-mp init` with appid/secret |

Chinese guide: [README.zh-CN.md](./README.zh-CN.md)

## Install

```bash
npx skills add kedoupi/wechat-mp-skill
# or globally for all agents:
npx skills add kedoupi/wechat-mp-skill -g --all
```

Requires **python3** for preview / draft helpers. **No WeChat credentials** needed to write or preview.

### After install (copy-paste)

The skills CLI does not run package hooks — run these yourself (or ask your agent):

```bash
SK=~/.agents/skills/wechat-mp

# Always safe: environment checklist (prints setup hints if draft config missing)
bash $SK/scripts/wechat-mp doctor

# Optional — only when you want WeChat draft/upload:
bash $SK/scripts/wechat-mp init \
  --appid 'wx_YOUR_APPID' \
  --secret 'YOUR_APPSECRET'
# → ~/.config/kedoupi/wechat-mp/config.env
```

## Agent usage

Say things like:

- 「写一篇关于 … 的公众号」→ local `article.md` (mode A)
- 「完整制作一篇公众号」→ article + cover (if tzai-image present) + `preview.html` (mode B)
- 「推到草稿箱」→ draft API after confirm (mode C)

## CLI

```bash
SK=~/.agents/skills/wechat-mp   # or your install path

# From your *content project* root (so history stays in-repo):
bash $SK/scripts/wechat-mp doctor
bash $SK/scripts/wechat-mp list-out       # prior articles in ./wechat-mp-out
bash $SK/scripts/wechat-mp suite          # soft peers
bash $SK/scripts/wechat-mp new-out --title "My topic"
bash $SK/scripts/wechat-mp preview --dir ./wechat-mp-out/<slug>
bash $SK/scripts/wechat-mp draft --dir ./wechat-mp-out/<slug> --dry-run

# Optional WeChat API credentials (draft only)
bash $SK/scripts/wechat-mp init --appid wx… --secret …
bash $SK/scripts/wechat-mp init-style     # account voice, no appid
```

### Preview expectations

`preview.html` is a **structure check** (headings, lists, code, footnotes) with inline styles. It is **not** a pixel-perfect clone of the WeChat editor.

### Safety

- Default: local article only  
- No mass-publish  
- `--dry-run` never calls WeChat  
- Cover required for real draft  

## Output layout (per content project)

`wechat-mp-out/` is **project-local writing history**: next time you open the same project, `list-out` and prior `brief.md` / `article.md` are available as continuity.

```text
<your-project>/
  wechat-mp-out/
    README.md
    <slug>/
      manifest.json   # suite handoff + status
      brief.md
      article.md
      cover.png
      figures/
      preview.html
```

## Related kedoupi skills

- [tzai-image](https://github.com/kedoupi/tzai-image-skill) — image generation (`wechat` / `cover` kinds)
- [lark-push](https://github.com/kedoupi/lark-push-skill) — Feishu / Lark notifications

## License

MIT

## Inspired by

Community tools such as [WeWrite](https://github.com/imraywang/wewrite) explored full content pipelines for 公众号. This project is a **separate** kedoupi suite skill (compose with tzai-image / lark-push; not a fork).
