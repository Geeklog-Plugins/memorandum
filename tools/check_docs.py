#!/usr/bin/env python3
"""Validate local Markdown references in the Memorandum (stdlib only)."""
from __future__ import annotations

import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"(?<!!)\[[^\]]*\]\((<?[^)\s>]+>?)")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
EXPLICIT_ANCHOR = re.compile(r'<a\s+(?:[^>]*?\s)?(?:id|name)=[\x22\x27]([^\x22\x27]+)', re.I)

def visible_markdown(text):
    """Exclude fenced code, which can contain illustrative paths."""
    lines, fenced, marker = [], False, ""
    for line in text.splitlines():
        m = re.match(r"^\s*(\x60{3,}|~{3,})", line)
        if m:
            if not fenced:
                fenced, marker = True, m.group(1)[0]
            elif m.group(1)[0] == marker:
                fenced = False
            continue
        if not fenced:
            lines.append(line)
    return lines

def slug(text):
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[\x60*_~]", "", text)
    text = unicodedata.normalize("NFKC", text).casefold()
    text = re.sub(r"[^\w\- ]", "", text)
    return re.sub(r"\s+", "-", text.strip())

def anchors(path):
    seen, out = Counter(), set()
    for line in visible_markdown(path.read_text(encoding="utf-8")):
        m = HEADING.match(line)
        if m:
            name = slug(m.group(1))
            if name:
                count = seen[name]
                out.add(name if count == 0 else f"{name}-{count}")
                seen[name] += 1
        out.update(EXPLICIT_ANCHOR.findall(line))
    return out

def main():
    problems = []
    docs = list(ROOT.rglob("*.md"))
    for doc in docs:
        for lineno, line in enumerate(visible_markdown(doc.read_text(encoding="utf-8")), 1):
            for match in LINK.finditer(line):
                uri = match.group(1).strip("<>")
                if uri.startswith(("http:", "https:", "mailto:", "tel:", "data:")):
                    continue
                path_part, _, fragment = uri.partition("#")
                if not path_part and not fragment:
                    continue
                target = (doc.parent / unquote(path_part)).resolve() if path_part else doc
                if not target.is_relative_to(ROOT.resolve()):
                    problems.append(f"{doc.relative_to(ROOT)}:{lineno}: link escapes repository: {uri}")
                    continue
                if target.is_dir():
                    target = target / "README.md"
                if not target.is_file():
                    problems.append(f"{doc.relative_to(ROOT)}:{lineno}: missing file: {uri}")
                elif fragment and target.suffix.lower() == ".md":
                    anchor = unquote(fragment).lower()
                    if anchor not in anchors(target):
                        problems.append(f"{doc.relative_to(ROOT)}:{lineno}: missing anchor: {uri}")
    if problems:
        print("\n".join(problems))
        print(f"FAILED: {len(problems)} invalid local references")
        return 1
    print(f"OK: local Markdown links and anchors checked in {len(docs)} files")
    return 0

if __name__ == "__main__":
    sys.exit(main())
