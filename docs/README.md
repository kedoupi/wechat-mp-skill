# Documentation

Human-facing docs for **wechat-mp-skill**. Not part of the installable package.

## Layout

```text
docs/
└── README.md         # this index + golden-path notes
```

No curated `screenshots/` yet. End-user demos are **user project outputs** under
`<project>/wechat-mp-out/` (not under the skill package).

## Separation (incubator contract)

| Tree | Role |
| --- | --- |
| `skills/wechat-mp/` | Installable package |
| `docs/` | Guides + demo notes |
| `tests/` | Offline `run.sh` + fixtures |
| `artifacts/` | Reserved for skill-repo live dumps (none yet) |

**User article outputs** stay in the content project (`wechat-mp-out/`), never in `skills/` or the incubator root.

See parent incubator `schema/skill-repo.md` § docs / tests / artifacts.

## Golden-path demo

Offline fixture used by tests:

- `tests/fixtures/sample.md` — short 公众号-style sample for `preview` / `md2html`

End-user install + config lives in the root [README](../README.md) / [中文](../README.zh-CN.md)
(`doctor` → optional `init-style` → optional `init` for draft).

Manual golden path (after install):

```bash
OUT=$(bash skills/wechat-mp/scripts/wechat-mp new-out --title "Demo" --base /tmp/wechat-mp-demo)
cp tests/fixtures/sample.md "$OUT/article.md"
bash skills/wechat-mp/scripts/wechat-mp preview --dir "$OUT"
open "$OUT/preview.html"   # macOS
```

Optional cover: generate with `tzai-image` into `$OUT/cover.png`, then `draft --dry-run`.
