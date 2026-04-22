#!/usr/bin/env python3
"""Convert Mintlify MDX docs to standard Markdown for MkDocs.

Handles:
  - <Note>, <Tip>, <Warning>, <Info>  →  MkDocs admonitions
  - <CardGroup> / <Card>              →  Markdown link list
  - <Tabs> / <Tab>                    →  pymdownx.tabbed syntax
  - Internal /docs/xxx links          →  relative .md links
  - Strips .mdx frontmatter quirks
"""

import os
import re
import shutil
from pathlib import Path

SRC_DIR = Path("docs")
DST_DIR = Path("site_src")

# ---------------------------------------------------------------------------
# Component converters
# ---------------------------------------------------------------------------

_ADMONITIONS = {
    "Note": "note",
    "Tip": "tip",
    "Warning": "warning",
    "Info": "info",
}


def _convert_admonitions(text: str) -> str:
    for tag, kind in _ADMONITIONS.items():

        def _replace(m: re.Match, kind: str = kind) -> str:
            inner = m.group(1).strip()
            lines = inner.split("\n")
            indented = "\n".join(
                ("    " + line) if line.strip() else "" for line in lines
            )
            return f"!!! {kind}\n{indented}\n"

        text = re.sub(
            rf"<{tag}>(.*?)</{tag}>",
            _replace,
            text,
            flags=re.DOTALL,
        )
    return text


def _convert_cards(text: str) -> str:
    """<CardGroup> / <Card> → plain link list."""
    text = re.sub(r"<CardGroup[^>]*>", "", text)
    text = re.sub(r"</CardGroup>", "", text)

    def _card(m: re.Match) -> str:
        title = m.group(1)
        href = (m.group(2) or "").strip()
        body = (m.group(3) or "").strip()
        # Convert absolute /docs/xxx paths to relative xxx.md
        if href and not href.startswith("http"):
            href = re.sub(r"^/docs/", "", href)
            href = href + ".md"
        desc = f" — {body}" if body else ""
        link = f"[{title}]({href})" if href else title
        return f"- **{link}**{desc}\n"

    text = re.sub(
        r'<Card\s[^>]*title="([^"]*)"[^>]*(?:href="([^"]*)")?[^>]*>\s*(.*?)\s*</Card>',
        _card,
        text,
        flags=re.DOTALL,
    )
    # Fallback: cards with href before title
    text = re.sub(
        r'<Card\s[^>]*href="([^"]*)"[^>]*title="([^"]*)"[^>]*>\s*(.*?)\s*</Card>',
        lambda m: (
            f"- **[{m.group(2)}]({re.sub(r'^/docs/', '', m.group(1)) + '.md'})** — {m.group(3).strip()}\n"
        ),
        text,
        flags=re.DOTALL,
    )
    return text


def _convert_tabs(text: str) -> str:
    """<Tabs> / <Tab title="X"> → pymdownx.tabbed."""
    text = re.sub(r"<Tabs>\s*", "", text)
    text = re.sub(r"</Tabs>", "", text)

    def _tab(m: re.Match) -> str:
        title = m.group(1)
        inner = m.group(2)
        # Indent content by 4 spaces
        indented = "\n".join(
            ("    " + line) if line else "" for line in inner.strip().split("\n")
        )
        return f'\n=== "{title}"\n{indented}\n'

    text = re.sub(
        r'<Tab title="([^"]*)">(.*?)</Tab>',
        _tab,
        text,
        flags=re.DOTALL,
    )
    return text


def _fix_internal_links(text: str, src_rel: Path) -> str:
    """Convert absolute /docs/xxx links to relative .md links.

    Computes the correct relative path from the source file's directory
    so MkDocs resolves cross-directory links correctly.
    """
    src_dir = src_rel.parent  # e.g. Path("tools") for tools/requirement-yogi.md

    def _rewrite(m: re.Match) -> str:
        path = m.group(1)  # e.g. "guides/requirement-yogi-search"
        anchor = m.group(2) or ""
        # Strip leading /docs/
        path = re.sub(r"^/docs/", "", path)
        target = Path(path + ".md")  # e.g. guides/requirement-yogi-search.md
        # Compute relative path from src_dir to target
        try:
            rel = Path(os.path.relpath(target, src_dir))
        except ValueError:
            rel = target
        # Normalise Windows backslashes
        rel_str = str(rel).replace("\\", "/")
        return f"]({rel_str}{anchor})"

    # [text](/docs/path#anchor) → [text](relative/path.md#anchor)
    text = re.sub(r"\]\(/docs/([^)#]+)(#[^)]*)?\)", _rewrite, text)
    return text


def convert(text: str, src_rel: Path = Path(".")) -> str:
    text = _convert_admonitions(text)
    text = _convert_cards(text)
    text = _convert_tabs(text)
    text = _fix_internal_links(text, src_rel)
    # Collapse runs of 3+ blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


# ---------------------------------------------------------------------------
# File walker
# ---------------------------------------------------------------------------


def build() -> None:
    if DST_DIR.exists():
        shutil.rmtree(DST_DIR)
    DST_DIR.mkdir(parents=True)

    copied = converted = 0

    for src in SRC_DIR.rglob("*"):
        rel = src.relative_to(SRC_DIR)

        # Skip Mintlify override YAML files and hidden dirs
        if any(part.startswith("_") for part in rel.parts):
            continue
        if src.is_dir():
            (DST_DIR / rel).mkdir(parents=True, exist_ok=True)
            continue

        if src.suffix == ".mdx":
            dst = DST_DIR / rel.with_suffix(".md")
            dst.parent.mkdir(parents=True, exist_ok=True)
            raw = src.read_text(encoding="utf-8")
            # Pass the destination relative path so link rewriting is depth-aware
            dst_rel = dst.relative_to(DST_DIR)
            dst.write_text(convert(raw, dst_rel), encoding="utf-8")
            converted += 1
        elif src.suffix in {".md", ".svg", ".png", ".jpg", ".gif"}:
            dst = DST_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1

    print(f"Converted {converted} MDX files, copied {copied} assets -> {DST_DIR}/")


if __name__ == "__main__":
    build()
