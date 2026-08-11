#!/usr/bin/env python3
"""Markdown → WeChat-oriented inline-style HTML (stdlib only).

Preview helper — not a pixel-perfect WeChat editor clone. Goal: readable
structure for authors before paste / draft upload.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# Default theme: clean editorial, mobile-first
DEFAULT_STYLES = {
    "body": "margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;font-size:16px;line-height:1.75;color:#1f2328;background:#ffffff;",
    "h1": "margin:1.4em 0 0.6em;font-size:22px;font-weight:700;line-height:1.35;color:#0f172a;",
    "h2": "margin:1.5em 0 0.55em;font-size:18px;font-weight:700;line-height:1.4;color:#0f172a;border-left:3px solid #0d9488;padding-left:10px;",
    "h3": "margin:1.2em 0 0.45em;font-size:16px;font-weight:600;line-height:1.4;color:#334155;",
    "p": "margin:0.75em 0;font-size:16px;line-height:1.75;color:#1f2328;letter-spacing:0.01em;",
    "blockquote": "margin:1em 0;padding:10px 14px;border-left:3px solid #94a3b8;background:#f8fafc;color:#475569;font-size:15px;",
    "code": "font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;background:#f1f5f9;padding:1px 5px;border-radius:3px;color:#0f172a;",
    "pre": "margin:1em 0;padding:12px 14px;background:#0f172a;color:#e2e8f0;border-radius:6px;overflow-x:auto;font-size:13px;line-height:1.55;white-space:pre-wrap;word-break:break-word;",
    "pre_code": "font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;background:transparent;color:#e2e8f0;padding:0;",
    "ul_item": "margin:0.35em 0 0.35em 0.2em;padding-left:0.4em;font-size:16px;line-height:1.7;color:#1f2328;",
    "ol_item": "margin:0.35em 0 0.35em 0.2em;padding-left:0.4em;font-size:16px;line-height:1.7;color:#1f2328;",
    "img": "max-width:100%;height:auto;display:block;margin:1em auto;border-radius:4px;",
    "hr": "border:none;border-top:1px solid #e2e8f0;margin:1.5em 0;",
    "a": "color:#0d9488;text-decoration:underline;",
    "strong": "font-weight:700;color:#0f172a;",
    "em": "font-style:italic;",
    "footnote": "margin-top:1.5em;padding-top:0.75em;border-top:1px solid #e2e8f0;font-size:13px;color:#64748b;line-height:1.6;",
    "section_list": "margin:0.6em 0;",
}


@dataclass
class ConvertResult:
    html: str
    title: str
    digest: str
    images: list[str] = field(default_factory=list)


def _inline(text: str, styles: dict[str, str], footnotes: list[tuple[str, str]]) -> str:
    """Apply inline markdown: images, links, code, bold, italic."""
    # Escape first, then restore intentional markup via placeholders
    text = html.escape(text, quote=False)

    # Inline code
    def code_sub(m: re.Match[str]) -> str:
        return f'<code style="{styles["code"]}">{m.group(1)}</code>'

    text = re.sub(r"`([^`]+)`", code_sub, text)

    # Images ![alt](src)
    images_found: list[str] = []

    def img_sub(m: re.Match[str]) -> str:
        alt, src = m.group(1), m.group(2)
        images_found.append(html.unescape(src))
        return (
            f'<img src="{src}" alt="{alt}" style="{styles["img"]}" />'
        )

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img_sub, text)

    # Links [text](url) → keep visible + footnote (WeChat blocks most external taps)
    def link_sub(m: re.Match[str]) -> str:
        label, url = m.group(1), m.group(2)
        footnotes.append((html.unescape(label), html.unescape(url)))
        n = len(footnotes)
        return (
            f'<span style="{styles["a"]}">{label}</span>'
            f'<sup style="font-size:11px;color:#94a3b8;">[{n}]</sup>'
        )

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_sub, text)

    # Bold ** ** then italic * *
    text = re.sub(
        r"\*\*(.+?)\*\*",
        lambda m: f'<strong style="{styles["strong"]}">{m.group(1)}</strong>',
        text,
    )
    text = re.sub(
        r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)",
        lambda m: f'<em style="{styles["em"]}">{m.group(1)}</em>',
        text,
    )
    return text


def convert(markdown_text: str, styles: dict[str, str] | None = None) -> ConvertResult:
    styles = {**DEFAULT_STYLES, **(styles or {})}
    lines = markdown_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    images: list[str] = []
    footnotes: list[tuple[str, str]] = []
    title = ""
    i = 0
    in_code = False
    code_buf: list[str] = []
    list_buf: list[tuple[str, str]] = []  # (type, content) type=ul|ol

    def flush_list() -> None:
        nonlocal list_buf
        if not list_buf:
            return
        parts = [f'<section style="{styles["section_list"]}">']
        for idx, (kind, content) in enumerate(list_buf, start=1):
            inline_html = _inline(content, styles, footnotes)
            # capture images from inline side-effect via regex on original
            for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", content):
                images.append(m.group(2))
            bullet = "•" if kind == "ul" else f"{idx}."
            st = styles["ul_item"] if kind == "ul" else styles["ol_item"]
            parts.append(
                f'<p style="{st}"><span style="color:#0d9488;font-weight:600;margin-right:6px;">{bullet}</span>{inline_html}</p>'
            )
        parts.append("</section>")
        out.append("".join(parts))
        list_buf = []

    def flush_code() -> None:
        nonlocal code_buf, in_code
        if not in_code:
            return
        body = html.escape("\n".join(code_buf), quote=False)
        out.append(
            f'<pre style="{styles["pre"]}"><code style="{styles["pre_code"]}">{body}</code></pre>'
        )
        code_buf = []
        in_code = False

    while i < len(lines):
        line = lines[i]
        if in_code:
            if line.strip().startswith("```"):
                flush_code()
            else:
                code_buf.append(line)
            i += 1
            continue

        if line.strip().startswith("```"):
            flush_list()
            in_code = True
            code_buf = []
            i += 1
            continue

        if re.match(r"^---+\s*$", line.strip()) or re.match(r"^\*\*\*+\s*$", line.strip()):
            flush_list()
            out.append(f'<hr style="{styles["hr"]}" />')
            i += 1
            continue

        hm = re.match(r"^(#{1,3})\s+(.+)$", line)
        if hm:
            flush_list()
            level = len(hm.group(1))
            raw = hm.group(2).strip()
            if level == 1 and not title:
                title = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", "", raw).strip() or raw
            for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", raw):
                images.append(m.group(2))
            tag = f"h{level}"
            st = styles[tag]
            out.append(f'<{tag} style="{st}">{_inline(raw, styles, footnotes)}</{tag}>')
            i += 1
            continue

        if line.startswith("> "):
            flush_list()
            quote_lines = []
            while i < len(lines) and lines[i].startswith("> "):
                quote_lines.append(lines[i][2:])
                i += 1
            q = _inline(" ".join(quote_lines), styles, footnotes)
            out.append(f'<blockquote style="{styles["blockquote"]}">{q}</blockquote>')
            continue

        ulm = re.match(r"^[-*+]\s+(.+)$", line)
        if ulm:
            list_buf.append(("ul", ulm.group(1)))
            i += 1
            # continue collecting
            while i < len(lines):
                m2 = re.match(r"^[-*+]\s+(.+)$", lines[i])
                if m2:
                    list_buf.append(("ul", m2.group(1)))
                    i += 1
                else:
                    break
            flush_list()
            continue

        olm = re.match(r"^\d+\.\s+(.+)$", line)
        if olm:
            list_buf.append(("ol", olm.group(1)))
            i += 1
            while i < len(lines):
                m2 = re.match(r"^\d+\.\s+(.+)$", lines[i])
                if m2:
                    list_buf.append(("ol", m2.group(1)))
                    i += 1
                else:
                    break
            flush_list()
            continue

        if not line.strip():
            flush_list()
            i += 1
            continue

        # paragraph (merge consecutive non-empty plain lines)
        flush_list()
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,3}\s|```|[-*+]\s|\d+\.\s|>\s|---+\s*$)", lines[i]
        ):
            para.append(lines[i])
            i += 1
        raw_p = " ".join(p.strip() for p in para)
        for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", raw_p):
            images.append(m.group(2))
        out.append(f'<p style="{styles["p"]}">{_inline(raw_p, styles, footnotes)}</p>')

    flush_list()
    flush_code()

    if footnotes:
        items = []
        for n, (label, url) in enumerate(footnotes, start=1):
            items.append(f"[{n}] {html.escape(label)}: {html.escape(url)}")
        out.append(
            f'<p style="{styles["footnote"]}">{"<br/>".join(items)}</p>'
        )

    body = "\n".join(out)
    # digest: plain text first ~60 chars (WeChat digest soft limit ~120 bytes)
    plain = re.sub(r"<[^>]+>", "", body)
    plain = html.unescape(plain)
    plain = re.sub(r"\s+", " ", plain).strip()
    if not title:
        title = plain[:30] if plain else "Untitled"
    digest = plain[:80] if plain else ""

    # de-dupe images preserving order
    seen: set[str] = set()
    uniq_images: list[str] = []
    for img in images:
        if img not in seen:
            seen.add(img)
            uniq_images.append(img)

    wrapped = (
        f'<section style="{styles["body"]}">\n{body}\n</section>'
    )
    return ConvertResult(html=wrapped, title=title, digest=digest, images=uniq_images)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Markdown to WeChat-oriented HTML")
    p.add_argument("input", nargs="?", help="Markdown file (default: stdin)")
    p.add_argument("-o", "--output", help="Write HTML to file")
    p.add_argument("--title-out", help="Write extracted title to file")
    p.add_argument("--digest-out", help="Write digest to file")
    p.add_argument("--images-out", help="Write image paths (one per line)")
    p.add_argument("--meta-json", help="Write {title,digest,images} JSON")
    args = p.parse_args(argv)

    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    result = convert(text)

    if args.output:
        Path(args.output).write_text(result.html, encoding="utf-8")
    else:
        sys.stdout.write(result.html)
        if not result.html.endswith("\n"):
            sys.stdout.write("\n")

    if args.title_out:
        Path(args.title_out).write_text(result.title, encoding="utf-8")
    if args.digest_out:
        Path(args.digest_out).write_text(result.digest, encoding="utf-8")
    if args.images_out:
        Path(args.images_out).write_text(
            "\n".join(result.images) + ("\n" if result.images else ""),
            encoding="utf-8",
        )
    if args.meta_json:
        import json

        Path(args.meta_json).write_text(
            json.dumps(
                {
                    "title": result.title,
                    "digest": result.digest,
                    "images": result.images,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
