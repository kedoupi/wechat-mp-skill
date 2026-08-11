# Demo fixture notes

Offline fixture used by tests:

- `tests/fixtures/sample.md` — short 公众号-style sample for `preview` / `md2html`

Manual golden path (after install):

```bash
OUT=$(bash skills/wechat-mp/scripts/wechat-mp new-out --title "Demo" --base /tmp/wechat-mp-demo)
cp tests/fixtures/sample.md "$OUT/article.md"
bash skills/wechat-mp/scripts/wechat-mp preview --dir "$OUT"
open "$OUT/preview.html"   # macOS
```

Optional cover: generate with `tzai-image` into `$OUT/cover.png`, then `draft --dry-run`.
