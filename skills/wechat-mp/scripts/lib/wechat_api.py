#!/usr/bin/env python3
"""WeChat Official Account API helpers (stdlib only).

APIs used:
  - GET  cgi-bin/token
  - POST cgi-bin/media/uploadimg          (in-article images → url)
  - POST cgi-bin/material/add_material    (cover → media_id)
  - POST cgi-bin/draft/add                (create draft)

Never logs full secrets. dry-run is handled by the bash CLI (no network).
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Default WeChat API host. Override when IP whitelist requires a proxy:
#   export WECHAT_MP_API_BASE=https://your-proxy.example
#   # or suite default:
#   export KDP_WECHAT_PROXY=https://your-proxy.example
def _api_base() -> str:
    raw = (
        os.environ.get("WECHAT_MP_API_BASE")
        or os.environ.get("KDP_WECHAT_PROXY")
        or "https://api.weixin.qq.com"
    ).strip().rstrip("/")
    return raw or "https://api.weixin.qq.com"


API_BASE = _api_base()  # evaluated at import; re-read via _api_base() in callers if needed
TIMEOUT = 30

# Simple process-local token cache: appid → (token, expires_at)
_TOKEN_CACHE: dict[str, tuple[str, float]] = {}

_IMG_SRC_RE = re.compile(
    r"""(<img\b[^>]*?\bsrc=(["']))([^"']+)(\2)""",
    re.IGNORECASE,
)


def _mask(s: str) -> str:
    if not s or len(s) <= 8:
        return "****"
    return f"{s[:4]}…{s[-4:]}"


def _http_json(
    method: str,
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> dict:
    req = urllib.request.Request(url, data=data, method=method)
    # Cloudflare / some proxies block the default Python-urllib User-Agent.
    req.add_header(
        "User-Agent",
        "wechat-mp/0.1 (+https://github.com/kedoupi/wechat-mp-skill)",
    )
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"HTTP {e.code}: {raw[:300]}") from exc
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e}") from e
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON: {raw[:300]}") from exc


def get_access_token(appid: str, secret: str, *, force: bool = False) -> str:
    now = time.time()
    if not force and appid in _TOKEN_CACHE:
        token, exp = _TOKEN_CACHE[appid]
        if now < exp:
            return token

    qs = urllib.parse.urlencode(
        {
            "grant_type": "client_credential",
            "appid": appid,
            "secret": secret,
        }
    )
    data = _http_json("GET", f"{_api_base()}/cgi-bin/token?{qs}")
    if "access_token" not in data:
        err = data.get("errcode", "?")
        msg = data.get("errmsg", "unknown")
        raise RuntimeError(f"token failed: errcode={err} errmsg={msg}")
    token = data["access_token"]
    expires_in = int(data.get("expires_in", 7200))
    _TOKEN_CACHE[appid] = (token, now + expires_in - 300)
    return token


def upload_image(access_token: str, image_path: str) -> str:
    """Upload image for article body. Returns WeChat CDN url."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(image_path)
    content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    boundary = f"----WechatMpBoundary{int(time.time())}"
    file_bytes = path.read_bytes()
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="media"; filename="{path.name}"\r\n'
                f"Content-Type: {content_type}\r\n\r\n"
            ).encode(),
            file_bytes,
            f"\r\n--{boundary}--\r\n".encode(),
        ]
    )
    url = f"{_api_base()}/cgi-bin/media/uploadimg?access_token={urllib.parse.quote(access_token)}"
    data = _http_json(
        "POST",
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    if "url" not in data:
        raise RuntimeError(
            f"uploadimg failed: errcode={data.get('errcode')} errmsg={data.get('errmsg')}"
        )
    return data["url"]


def upload_thumb(access_token: str, image_path: str) -> str:
    """Upload permanent image material (cover). Returns media_id."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(image_path)
    content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    boundary = f"----WechatMpBoundary{int(time.time())}"
    file_bytes = path.read_bytes()
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="media"; filename="{path.name}"\r\n'
                f"Content-Type: {content_type}\r\n\r\n"
            ).encode(),
            file_bytes,
            f"\r\n--{boundary}--\r\n".encode(),
        ]
    )
    qs = urllib.parse.urlencode({"access_token": access_token, "type": "image"})
    url = f"{_api_base()}/cgi-bin/material/add_material?{qs}"
    data = _http_json(
        "POST",
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    if "media_id" not in data:
        raise RuntimeError(
            f"add_material failed: errcode={data.get('errcode')} errmsg={data.get('errmsg')}"
        )
    return data["media_id"]


def _is_remote_url(src: str) -> bool:
    s = src.strip().lower()
    return (
        s.startswith("http://")
        or s.startswith("https://")
        or s.startswith("//")
        or s.startswith("data:")
    )


def _resolve_local_image(src: str, base: Path) -> Path:
    """Resolve a local image path and require it to stay under base_dir."""
    p = Path(src)
    if not p.is_absolute():
        p = (base / p).resolve()
    else:
        p = p.resolve()
    try:
        p.relative_to(base.resolve())
    except ValueError as exc:
        raise ValueError(f"body image escapes base dir: {src}") from exc
    return p


def list_local_image_srcs(html: str, base_dir: str | Path | None = None) -> list[str]:
    """Return local image paths referenced by <img src=…> (resolved when possible)."""
    base = Path(base_dir) if base_dir else Path.cwd()
    found: list[str] = []
    seen: set[str] = set()
    for m in _IMG_SRC_RE.finditer(html):
        src = html_lib.unescape(m.group(3).strip())
        if not src or _is_remote_url(src):
            continue
        try:
            p = _resolve_local_image(src, base)
        except ValueError:
            continue
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        found.append(key)
    return found


def rewrite_local_images(
    access_token: str,
    html: str,
    *,
    base_dir: str | Path | None = None,
) -> tuple[str, list[tuple[str, str]]]:
    """Upload local <img src> files via uploadimg and rewrite to CDN urls.

    Returns (new_html, [(local_path, cdn_url), ...]).
    Missing local files raise FileNotFoundError.
    Remote / data: urls are left unchanged.
    Paths must resolve under base_dir (no .. escape).
    """
    base = Path(base_dir) if base_dir else Path.cwd()
    cache: dict[str, str] = {}  # resolved local path → cdn
    mappings: list[tuple[str, str]] = []

    def repl(m: re.Match[str]) -> str:
        prefix, _quote, src_raw, suffix = m.group(1), m.group(2), m.group(3), m.group(4)
        src = html_lib.unescape(src_raw.strip())
        if not src or _is_remote_url(src):
            return m.group(0)
        p = _resolve_local_image(src, base)
        key = str(p)
        if key not in cache:
            if not p.is_file():
                raise FileNotFoundError(
                    f"body image not found: {src} (resolved {p})"
                )
            cdn = upload_image(access_token, key)
            cache[key] = cdn
            mappings.append((key, cdn))
        # CDN urls are ascii; escape quotes defensively
        return f"{prefix}{html_lib.escape(cache[key], quote=True)}{suffix}"

    new_html = _IMG_SRC_RE.sub(repl, html)
    return new_html, mappings


def create_draft(
    access_token: str,
    *,
    title: str,
    html: str,
    digest: str,
    thumb_media_id: str,
    author: str = "",
) -> str:
    if not thumb_media_id:
        raise ValueError("thumb_media_id (cover) is required for draft/add")
    article = {
        "title": title,
        "author": author or "",
        "digest": digest or "",
        "content": html,
        "thumb_media_id": thumb_media_id,
        "show_cover_pic": 0,
    }
    payload = {"articles": [article]}
    # ensure_ascii=False is mandatory for Chinese titles/content
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    url = f"{_api_base()}/cgi-bin/draft/add?access_token={urllib.parse.quote(access_token)}"
    data = _http_json(
        "POST",
        url,
        data=raw,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    errcode = data.get("errcode", 0)
    if errcode not in (0, None) and "media_id" not in data:
        raise RuntimeError(
            f"draft/add failed: errcode={errcode} errmsg={data.get('errmsg')}"
        )
    if "media_id" not in data:
        raise RuntimeError(f"draft/add missing media_id: {data}")
    return data["media_id"]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="WeChat MP API helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("token", help="Fetch access_token")
    t.add_argument("--appid", required=True)
    t.add_argument("--secret", required=True)
    t.add_argument("--force", action="store_true")

    ui = sub.add_parser("upload-image", help="Upload body image → url")
    ui.add_argument("--appid", required=True)
    ui.add_argument("--secret", required=True)
    ui.add_argument("--file", required=True)

    ut = sub.add_parser("upload-thumb", help="Upload cover → media_id")
    ut.add_argument("--appid", required=True)
    ut.add_argument("--secret", required=True)
    ut.add_argument("--file", required=True)

    d = sub.add_parser("draft", help="Create draft")
    d.add_argument("--appid", required=True)
    d.add_argument("--secret", required=True)
    d.add_argument("--title", required=True)
    d.add_argument("--html-file", required=True)
    d.add_argument("--digest", default="")
    d.add_argument("--thumb-media-id", required=True)
    d.add_argument("--author", default="")
    d.add_argument(
        "--base-dir",
        default="",
        help="Resolve relative body image paths; upload via uploadimg before draft/add",
    )

    li = sub.add_parser(
        "list-local-images",
        help="List local <img src> paths in HTML (offline; for dry-run)",
    )
    li.add_argument("--html-file", required=True)
    li.add_argument("--base-dir", default="")

    args = p.parse_args(argv)

    try:
        if args.cmd == "token":
            token = get_access_token(args.appid, args.secret, force=args.force)
            print(token)
            return 0
        if args.cmd == "upload-image":
            token = get_access_token(args.appid, args.secret)
            print(upload_image(token, args.file))
            return 0
        if args.cmd == "upload-thumb":
            token = get_access_token(args.appid, args.secret)
            print(upload_thumb(token, args.file))
            return 0
        if args.cmd == "list-local-images":
            html_body = Path(args.html_file).read_text(encoding="utf-8")
            base = args.base_dir or None
            for path in list_local_image_srcs(html_body, base):
                print(path)
            return 0
        if args.cmd == "draft":
            token = get_access_token(args.appid, args.secret)
            html_body = Path(args.html_file).read_text(encoding="utf-8")
            base = args.base_dir or str(Path(args.html_file).resolve().parent)
            html_body, mappings = rewrite_local_images(
                token, html_body, base_dir=base
            )
            for local, cdn in mappings:
                print(f"uploaded_body_image\t{local}\t{cdn}", file=sys.stderr)
            mid = create_draft(
                token,
                title=args.title,
                html=html_body,
                digest=args.digest,
                thumb_media_id=args.thumb_media_id,
                author=args.author,
            )
            print(mid)
            return 0
    except Exception as e:  # noqa: BLE001 — CLI boundary
        print(f"Error: {e}", file=sys.stderr)
        print(
            f"(appid={_mask(getattr(args, 'appid', '') or '')})",
            file=sys.stderr,
        )
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
