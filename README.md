# wechat-mp

**WeChat Official Account** skill for AI agents: write a solid article locally, optionally compose with kedoupi suite peers for images and Feishu notify, optionally push a **draft**.

| Package | Repo | Install |
| --- | --- | --- |
| `wechat-mp` | [kedoupi/wechat-mp-skill](https://github.com/kedoupi/wechat-mp-skill) | `npx skills add kedoupi/wechat-mp-skill` |

Part of the [kedoupi/skills](https://github.com/kedoupi/skills) suite: **standalone or combined**.

Chinese guide: [README.zh-CN.md](./README.zh-CN.md)

## What you can do (pick your level)

| Level | Goal | Credentials? |
| --- | --- | --- |
| **A — Write** | Local `article.md` + quality flow | No |
| **B — Package** | Article + cover (tzai-image) + `preview.html` | No appid; tzai key only if you generate images |
| **C — Draft** | Push to WeChat **draft box** (not mass-send) | Yes: appid + secret |

| Use case | Install |
| --- | --- |
| Write 公众号 article only | `wechat-mp-skill` |
| Write + cover images | + [tzai-image-skill](https://github.com/kedoupi/tzai-image-skill) |
| + Feishu notify | + [lark-push-skill](https://github.com/kedoupi/lark-push-skill) |
| + WeChat draft box | `wechat-mp init` with appid/secret |

## Install

```bash
npx skills add kedoupi/wechat-mp-skill
# or globally for all agents:
npx skills add kedoupi/wechat-mp-skill -g --all
```

Requires **python3** for preview / draft helpers.

### After install (copy-paste)

`npx skills add` only installs code — **no secrets, no style**. Run:

```bash
SK=~/.agents/skills/wechat-mp

# Always safe — checklist + setup hints
bash $SK/scripts/wechat-mp doctor

# Optional account voice (no appid) → ~/.config/kedoupi/wechat-mp/style.yaml
bash $SK/scripts/wechat-mp init-style

# Optional — only when you want draft/upload:
bash $SK/scripts/wechat-mp init \
  --appid 'wx_YOUR_APPID' \
  --secret 'YOUR_APPSECRET'
# If official API is IP-blocked, also pass:
#   --api-base 'https://YOUR_PROXY_HOST'
# → ~/.config/kedoupi/wechat-mp/config.env  (chmod 600)
```

**Do not** put secrets only inside `~/.agents/skills/wechat-mp/` (wiped by `npx skills update`).  
**Do not** put app secrets in `~/.zshrc` for this skill — prefer `init`.

## Agent usage

Say things like:

- 「写一篇关于 … 的公众号」→ local `article.md` (mode A)
- 「完整制作一篇公众号」→ article + cover (if tzai-image present) + `preview.html` (mode B)
- 「推到草稿箱」→ draft API after confirm (mode C)

## First article (CLI)

Run from your **content project root** so history stays in-repo under `./wechat-mp-out/`:

```bash
SK=~/.agents/skills/wechat-mp

bash $SK/scripts/wechat-mp doctor
bash $SK/scripts/wechat-mp new-out --title "My topic"
# edit ./wechat-mp-out/<slug>/article.md  (agent usually writes this)
bash $SK/scripts/wechat-mp preview --dir ./wechat-mp-out/<slug>
bash $SK/scripts/wechat-mp list-out

# Draft only after init + cover image:
bash $SK/scripts/wechat-mp draft --dir ./wechat-mp-out/<slug> --dry-run
# real push (needs confirm / credentials + cover):
# bash $SK/scripts/wechat-mp draft --dir ./wechat-mp-out/<slug>
```

### Preview expectations

`preview.html` is a **structure check** (headings, lists, code, footnotes) with inline styles. It is **not** a pixel-perfect clone of the WeChat editor.

### Safety

| Action | Default |
| --- | --- |
| Local article | On |
| Paid image gen | Off (needs tzai + explicit request) |
| Feishu notify | Off |
| WeChat draft | Off; **no mass-send** |
| `--dry-run` | Never calls WeChat |

## Configuration

### Credentials (draft only)

| Variable | Meaning |
| --- | --- |
| `WECHAT_MP_APPID` | Official Account appid |
| `WECHAT_MP_SECRET` | App secret |
| `WECHAT_MP_AUTHOR` | Optional default author on drafts |
| `WECHAT_MP_API_BASE` | Optional API host (IP-whitelist proxy) |
| `WECHAT_MP_CONFIG` | Optional explicit env file path |

Recommended file (default for `init`):

```text
~/.config/kedoupi/wechat-mp/config.env
```

### Account voice (`style.yaml`)

```bash
bash ~/.agents/skills/wechat-mp/scripts/wechat-mp init-style
# → ~/.config/kedoupi/wechat-mp/style.yaml
```

| Field | Purpose |
| --- | --- |
| `positioning` | One-line audience / account pitch |
| `topics` | Topic boundaries |
| `voice` | `clear-judgment` (default) · `warm-practical` · `sharp-brief` |
| `taboo` | Hard “do not invent” rules |
| `aigc_disclosure` | `ask` · `always` · `never` |

Inspect:

```bash
bash ~/.agents/skills/wechat-mp/scripts/wechat-mp which-config
bash ~/.agents/skills/wechat-mp/scripts/wechat-mp doctor
```

## Output layout (per content project)

```text
<your-project>/
  wechat-mp-out/            # project-local history (list-out reads this)
    README.md
    <slug>/
      manifest.json         # suite handoff + status
      brief.md
      article.md
      cover.png             # required for real draft
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
