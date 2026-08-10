#!/usr/bin/env bash
# Offline self-test scaffold. Extend when implementing the skill.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
# After new-skill.sh, package name matches repo folder name.
NAME="$(basename "$ROOT")"
BIN="${ROOT}/skills/${NAME}/scripts/${NAME}"

if [[ ! -x "$BIN" ]]; then
  # Template checkout before rename
  if [[ -x "${ROOT}/skills/wechat-mp/scripts/wechat-mp" ]]; then
    BIN="${ROOT}/skills/wechat-mp/scripts/wechat-mp"
  else
    echo "Helper not found under skills/*/scripts/" >&2
    exit 1
  fi
fi

echo "== syntax =="
bash -n "$BIN"
echo "  PASS  bash -n"

echo "== help / version =="
"$BIN" --help >/dev/null
"$BIN" --version
echo "  PASS  help/version"

echo "== dry-run (requires init or -- empty path) =="
# Use local init into package for isolated test
"$BIN" init --target local --chat-id oc_test --force >/dev/null
out="$("$BIN" --dry-run --title "T" --body "- hello" 2>/dev/null || true)"
# dry-run prints body on stdout
printf '%s\n' "$out" | grep -q 'hello'
rm -f "${ROOT}/skills/"*/config.local.env 2>/dev/null || true
echo "  PASS  dry-run"

echo "All template smoke tests passed."
