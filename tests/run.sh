#!/usr/bin/env bash
# Offline self-test for wechat-mp. No network.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
BIN="${ROOT}/skills/wechat-mp/scripts/wechat-mp"
MD2HTML="${ROOT}/skills/wechat-mp/scripts/lib/md2html.py"
API="${ROOT}/skills/wechat-mp/scripts/lib/wechat_api.py"
FIX="${ROOT}/tests/fixtures/sample.md"
PASS=0
FAIL=0
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

assert_contains() {
  local name="$1" needle="$2" haystack="$3"
  if [[ "$haystack" == *"$needle"* ]]; then
    echo "  PASS  $name"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $name (missing: $needle)"
    echo "        got: ${haystack:0:240}"
    FAIL=$((FAIL + 1))
  fi
}

assert_not_contains() {
  local name="$1" needle="$2" haystack="$3"
  if [[ "$haystack" != *"$needle"* ]]; then
    echo "  PASS  $name"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $name (unexpected: $needle)"
    FAIL=$((FAIL + 1))
  fi
}

assert_exit() {
  local name="$1" expected="$2"
  shift 2
  set +e
  "$@" >"$TMP/cmd.out" 2>"$TMP/cmd.err"
  local code=$?
  set -e
  if [[ "$code" -eq "$expected" ]]; then
    echo "  PASS  $name (exit $code)"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $name (exit $code, expected $expected)"
    echo "        stderr: $(head -c 300 "$TMP/cmd.err" 2>/dev/null || true)"
    FAIL=$((FAIL + 1))
  fi
}

echo "== syntax =="
bash -n "$BIN"
python3 -m py_compile "$MD2HTML" "$API"
echo "  PASS  bash -n / py_compile"
PASS=$((PASS + 1))

echo "== version / help =="
ver="$("$BIN" version)"
assert_contains "version" "wechat-mp v0.2.1" "$ver"
"$BIN" --help >"$TMP/help"
assert_contains "help draft" "draft" "$(cat "$TMP/help")"
assert_contains "help dry-run" "dry-run" "$(cat "$TMP/help")"

echo "== doctor =="
set +e
doc="$("$BIN" doctor 2>&1)"
doc_code=$?
set -e
assert_contains "doctor header" "wechat-mp doctor" "$doc"
assert_contains "doctor python" "python3" "$doc"
# python3 present → expect 0
if [[ "$doc_code" -eq 0 ]]; then
  echo "  PASS  doctor exit 0"
  PASS=$((PASS + 1))
else
  echo "  FAIL  doctor exit $doc_code"
  FAIL=$((FAIL + 1))
fi

echo "== new-out + manifest =="
out_dir="$("$BIN" new-out --base "$TMP/out" --title "Sample Topic" --slug sample-topic)"
assert_contains "new-out path" "sample-topic" "$out_dir"
[[ -f "$out_dir/manifest.json" ]]
assert_contains "manifest skill" "wechat-mp" "$(cat "$out_dir/manifest.json")"
assert_contains "manifest status pending" '"article": "pending"' "$(cat "$out_dir/manifest.json")"
[[ -d "$out_dir/figures" ]]
echo "  PASS  figures dir"
PASS=$((PASS + 1))

# Chinese title → slugify empty → article-TIMESTAMP under base
zh_dir="$("$BIN" new-out --base "$TMP/out" --title "公众号写作指南")"
if [[ -d "$zh_dir" && -f "$zh_dir/manifest.json" ]]; then
  echo "  PASS  chinese title new-out dir"
  PASS=$((PASS + 1))
else
  echo "  FAIL  chinese title new-out dir"
  FAIL=$((FAIL + 1))
fi
assert_contains "chinese title in manifest" "公众号写作指南" "$(cat "$zh_dir/manifest.json")"

echo "== manifest-set =="
"$BIN" manifest-set --dir "$out_dir" --status article=done --title "Sample Topic" >/dev/null
assert_contains "manifest article done" '"article": "done"' "$(cat "$out_dir/manifest.json")"
assert_contains "manifest title set" "Sample Topic" "$(cat "$out_dir/manifest.json")"

echo "== md2html / preview =="
cp "$FIX" "$out_dir/article.md"
"$BIN" preview --dir "$out_dir" >"$TMP/prev_meta"
[[ -f "$out_dir/preview.html" ]]
html="$(cat "$out_dir/preview.html")"
assert_contains "html section" "<section" "$html"
assert_contains "html h1 or h2" "Agent Skill" "$html"
assert_contains "inline style" "style=" "$html"
assert_contains "blockquote" "blockquote" "$html"
assert_contains "preview status" '"preview": "done"' "$(cat "$out_dir/manifest.json")"

# Chinese + list + meta
python3 "$MD2HTML" "$FIX" -o "$TMP/t.html" --meta-json "$TMP/meta.json"
meta="$(cat "$TMP/meta.json")"
assert_contains "meta title" "Agent Skill" "$meta"
# ensure_ascii=False: Chinese characters stay as UTF-8, not \uXXXX
assert_contains "meta chinese utf8" "公众号" "$meta"
assert_not_contains "meta no unicode escape title" '\\u' "$meta"

# Links become footnotes (WeChat blocks external taps)
cat >"$TMP/links.md" <<'MD'
# Link test

See [docs](https://example.com/path) for more.
MD
python3 "$MD2HTML" "$TMP/links.md" -o "$TMP/links.html"
assert_contains "link footnote" "[1]" "$(cat "$TMP/links.html")"
assert_contains "link url in footnote" "example.com" "$(cat "$TMP/links.html")"

# Body image local path tracking
cat >"$TMP/img.md" <<'MD'
# Img

![alt](figures/demo.png)
MD
python3 "$MD2HTML" "$TMP/img.md" --meta-json "$TMP/imgmeta.json" -o "$TMP/img.html"
assert_contains "img in meta" "figures/demo.png" "$(cat "$TMP/imgmeta.json")"
assert_contains "img tag" 'src="figures/demo.png"' "$(cat "$TMP/img.html")"

# list-local-images offline helper
echo '<section><img src="figures/demo.png" /><img src="https://cdn.example/a.png" /></section>' >"$TMP/mix.html"
locals="$(python3 "$API" list-local-images --html-file "$TMP/mix.html" --base-dir "$TMP")"
assert_contains "list local only" "demo.png" "$locals"
assert_not_contains "list skip remote" "cdn.example" "$locals"

echo "== draft dry-run =="
# fake cover file for dry-run path existence optional — dry-run allows missing cover file
: >"$out_dir/cover.png"
# body figure referenced in article
mkdir -p "$out_dir/figures"
: >"$out_dir/figures/demo.png"
cat >"$out_dir/article.md" <<'MD'
# Sample

Body with ![fig](figures/demo.png).
MD
err_out="$("$BIN" draft --dir "$out_dir" --dry-run 2>&1)"
assert_contains "dry-run flag" "[dry-run]" "$err_out"
assert_contains "dry-run no network" "no network" "$err_out"
assert_contains "dry-run would body images" "upload body images" "$err_out"
assert_contains "dry-run lists body image" "body_image=" "$err_out"

# dry-run without credentials still OK
err_nocred="$(env -u WECHAT_MP_APPID -u WECHAT_MP_SECRET -u WECHAT_MP_CONFIG \
  "$BIN" draft --dir "$out_dir" --dry-run 2>&1)"
assert_contains "dry-run no creds ok" "[dry-run]" "$err_nocred"

echo "== upload dry-run =="
uerr="$("$BIN" upload-image --file "$out_dir/cover.png" --dry-run 2>&1)"
assert_contains "upload dry-run" "[dry-run]" "$uerr"
terr="$("$BIN" upload-thumb --file "$out_dir/cover.png" --dry-run 2>&1)"
assert_contains "upload-thumb dry-run" "[dry-run]" "$terr"
tokerr="$("$BIN" token --dry-run 2>&1)"
assert_contains "token dry-run" "[dry-run]" "$tokerr"

echo "== draft guards (offline, no network) =="
# Isolate HOME so a developer machine ~/.config/kedoupi/wechat-mp cannot leak
# creds into offline guards. On macOS env, flags (-u) must precede name=value.
_EMPTY_HOME="$TMP/empty-home-draft"
mkdir -p "$_EMPTY_HOME"
_unset_creds=(
  env
  -u WECHAT_MP_APPID -u WECHAT_MP_SECRET -u WECHAT_MP_CONFIG
  -u KDP_WECHAT_APPID -u KDP_WECHAT_APPSECRET -u KDP_WECHAT_PROXY -u WECHAT_MP_API_BASE
  "HOME=$_EMPTY_HOME"
)
rm -f "$out_dir/cover.png"
assert_exit "draft no cover" 2 "${_unset_creds[@]}" \
  "$BIN" draft --dir "$out_dir"
: >"$out_dir/cover.png"
# credentials missing → exit 2 before network
assert_exit "draft no credentials" 2 "${_unset_creds[@]}" \
  "$BIN" draft --dir "$out_dir"

echo "== empty option rejected =="
assert_exit "empty --title new-out" 2 "$BIN" new-out --title ""
assert_exit "unknown command" 2 "$BIN" not-a-command

echo "== CLI values may start with dash =="
# require_val must accept markdown-list-style titles
dash_dir="$("$BIN" new-out --base "$TMP/out" --title "- leading dash title" --slug dash-title)"
assert_contains "dash title path" "dash-title" "$dash_dir"
assert_contains "dash title manifest" "leading dash" "$(cat "$dash_dir/manifest.json")"

echo "== which-config masks secrets =="
# Isolated HOME + explicit env only (no host kedoupi file overriding values)
_WC_HOME="$TMP/empty-home-which-config"
mkdir -p "$_WC_HOME"
wc_out="$(
  HOME="$_WC_HOME" \
  WECHAT_MP_APPID=wxabcdef12345678 WECHAT_MP_SECRET=supersecretvalue \
    "$BIN" which-config 2>&1
)"
assert_contains "which-config header" "Skill root" "$wc_out"
assert_contains "which-config appid masked" "wxab" "$wc_out"
assert_not_contains "which-config no full secret" "supersecretvalue" "$wc_out"
assert_contains "which-config secret masked" "****" "$wc_out"

echo "== suite command =="
suite="$("$BIN" suite 2>&1)"
assert_contains "suite header" "suite visibility" "$suite"
assert_contains "suite tzai line" "tzai-image" "$suite"
assert_contains "suite lark line" "lark-push" "$suite"

echo "== list-out project history =="
# empty base
empty_list="$("$BIN" list-out --base "$TMP/empty-history" 2>&1)"
assert_contains "list-out empty" "No history yet" "$empty_list"
# after new-out, history lists the slug
hist_base="$TMP/proj/wechat-mp-out"
mkdir -p "$TMP/proj"
h1="$("$BIN" new-out --base "$hist_base" --title "History One" --slug history-one)"
h2="$("$BIN" new-out --base "$hist_base" --title "History Two" --slug history-two)"
[[ -f "$hist_base/README.md" ]]
echo "  PASS  history base README"
PASS=$((PASS + 1))
listed="$("$BIN" list-out --base "$hist_base" 2>&1)"
assert_contains "list-out count" "count=2" "$listed"
assert_contains "list-out slug" "history-one" "$listed"
assert_contains "list-out title" "History Two" "$listed"
jlist="$("$BIN" list-out --base "$hist_base" --json)"
assert_contains "list-out json slug" "history-two" "$jlist"


echo "== api base / alias offline =="
# list-local-images stays offline; _api_base only reads env
base="$(WECHAT_MP_API_BASE=https://proxy.example python3 -c "import importlib.util; from pathlib import Path; p=Path('$API'); spec=importlib.util.spec_from_file_location('w', p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(m._api_base())")"
assert_contains "api base env" "proxy.example" "$base"


echo "== kedoupi config migrate =="
# Isolate HOME so we never touch the developer machine layout in assertions
FAKE_HOME="$TMP/fake-home"
mkdir -p "$FAKE_HOME/.agents/skills/.skill-data/wechat-mp"
printf '%s\n' 'WECHAT_MP_APPID=wxTESTAPPID123456' 'WECHAT_MP_SECRET=testsecretvalue12' >"$FAKE_HOME/.agents/skills/.skill-data/wechat-mp/config.env"
chmod 600 "$FAKE_HOME/.agents/skills/.skill-data/wechat-mp/config.env"
mig="$(HOME="$FAKE_HOME" "$BIN" which-config 2>&1)"
assert_contains "migrate creates kedoupi path" ".config/kedoupi/wechat-mp/config.env" "$mig"
assert_contains "migrate recommended exists" "[exists" "$mig"
[[ -f "$FAKE_HOME/.config/kedoupi/wechat-mp/config.env" ]]
echo "  PASS  kedoupi file on disk"
PASS=$((PASS + 1))
assert_contains "migrate appid masked" "WECHAT_MP_APPID=" "$(HOME="$FAKE_HOME" "$BIN" which-config 2>&1)"
assert_not_contains "migrate no raw secret" "testsecretvalue12" "$(HOME="$FAKE_HOME" "$BIN" which-config 2>&1)"


echo "== doctor setup hints =="
FAKE_HOME2="$TMP/fake-home-doctor"
mkdir -p "$FAKE_HOME2"
doc="$(HOME="$FAKE_HOME2" "$BIN" doctor 2>&1)"
assert_contains "doctor setup header" "After install" "$doc"
assert_contains "doctor setup init cmd" "wechat-mp init" "$doc"

echo "== package layout =="
for f in \
  "$ROOT/skills/wechat-mp/SKILL.md" \
  "$ROOT/skills/wechat-mp/config.example.env" \
  "$ROOT/skills/wechat-mp/references/wechat-constraints.md" \
  "$ROOT/skills/wechat-mp/references/article-brief.md" \
  "$ROOT/skills/wechat-mp/templates/article.md" \
  "$ROOT/skills/wechat-mp/templates/style.example.yaml" \
  "$ROOT/README.md" \
  "$ROOT/README.zh-CN.md" \
  "$ROOT/AGENTS.md"
do
  if [[ -f "$f" ]]; then
    :
  else
    echo "  FAIL  missing $f"
    FAIL=$((FAIL + 1))
  fi
done
echo "  PASS  package layout files"
PASS=$((PASS + 1))

echo
if [[ "$FAIL" -gt 0 ]]; then
  echo "FAILED: $FAIL  passed: $PASS"
  exit 1
fi
echo "All tests passed ($PASS)."
