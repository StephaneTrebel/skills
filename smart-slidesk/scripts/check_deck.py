#!/usr/bin/env python3
"""Deterministic checks for SliDesk decks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


SLIDE_HEADING_RE = re.compile(r"^\s*##(?!#)(?:\s|$)")
IMAGE_RE = re.compile(r"!image\(([^)]*)\)")
NUMERIC_PREFIX_RE = re.compile(r"^(\d+)[-_].+\.sdf$")


@dataclass
class Finding:
    level: str
    path: str
    line: int | None
    message: str

    def as_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "level": self.level,
            "path": self.path,
            "message": self.message,
        }
        if self.line is not None:
            data["line"] = self.line
        return data


def add(findings: list[Finding], level: str, path: Path | str, line: int | None, message: str) -> None:
    findings.append(Finding(level, str(path), line, message))


def read_text(path: Path, findings: list[Finding]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        add(findings, "error", path, None, "file is not valid UTF-8 text")
    except OSError as exc:
        add(findings, "error", path, None, f"cannot read file: {exc}")
    return ""


def is_external_path(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "data"}


def is_unchecked_dynamic_path(value: str) -> bool:
    return "++" in value or value.startswith("$")


def first_image_arg(args: str) -> str:
    first = args.split(",", 1)[0].strip()
    if (first.startswith('"') and first.endswith('"')) or (first.startswith("'") and first.endswith("'")):
        first = first[1:-1].strip()
    return first


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check_comment_balance(path: Path, text: str, findings: list[Finding]) -> None:
    open_line: int | None = None
    for line_no, line in enumerate(text.splitlines(), 1):
        search_from = 0
        while True:
            start = line.find("/*", search_from)
            end = line.find("*/", search_from)
            if start == -1 and end == -1:
                break
            if end != -1 and (start == -1 or end < start):
                if open_line is None:
                    add(findings, "error", path, line_no, "closing speaker-note marker without opening /*")
                else:
                    open_line = None
                search_from = end + 2
                continue
            if start != -1:
                if open_line is not None:
                    add(findings, "error", path, line_no, f"nested speaker-note marker before closing block opened on line {open_line}")
                open_line = line_no
                search_from = start + 2
    if open_line is not None:
        add(findings, "error", path, open_line, "speaker-note block is not closed")


def has_notes_block(segment: str) -> bool:
    start = segment.find("/*")
    if start == -1:
        return False
    end = segment.find("*/", start + 2)
    return end != -1


def check_slides_file(path: Path, deck_dir: Path, text: str, findings: list[Finding]) -> None:
    check_comment_balance(path, text, findings)

    lines = text.splitlines()
    heading_lines = [idx for idx, line in enumerate(lines) if SLIDE_HEADING_RE.match(line)]
    if not heading_lines and text.strip():
        add(findings, "warning", path, None, "slide file contains text but no ## slide heading")

    for index, heading_idx in enumerate(heading_lines):
        next_heading_idx = heading_lines[index + 1] if index + 1 < len(heading_lines) else len(lines)
        segment = "\n".join(lines[heading_idx:next_heading_idx])
        if not has_notes_block(segment):
            add(findings, "error", path, heading_idx + 1, "slide is missing a /* ... */ speaker notes block before the next slide")

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("////") and "!include(" in stripped:
            add(findings, "warning", path, line_no, "include is commented out with ////; verify this is intentional")

    for match in IMAGE_RE.finditer(text):
        image_path = first_image_arg(match.group(1))
        line_no = line_for_offset(text, match.start())
        if not image_path:
            add(findings, "error", path, line_no, "!image(...) is missing its mandatory path")
            continue
        if is_external_path(image_path):
            continue
        if is_unchecked_dynamic_path(image_path):
            add(findings, "warning", path, line_no, f"dynamic image path not checked: {image_path}")
            continue
        candidate = Path(image_path)
        resolved = candidate if candidate.is_absolute() else deck_dir / candidate
        if not resolved.exists():
            add(findings, "error", path, line_no, f"local image path does not exist: {image_path}")


def check_main_sdf(deck_dir: Path, main_path: Path, findings: list[Finding]) -> None:
    text = read_text(main_path, findings)
    if not text:
        return
    has_active_slides_include = False
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if SLIDE_HEADING_RE.match(line):
            add(findings, "error", main_path, line_no, "main.sdf is scaffold-only and must not contain ## slides")
        if stripped.startswith("////") and "!include(" in stripped:
            add(findings, "warning", main_path, line_no, "include is commented out with ////; verify this is intentional")
        if not stripped.startswith("////") and re.search(r"!include\(\s*slides\s*\)", stripped):
            has_active_slides_include = True
    if not has_active_slides_include:
        add(findings, "error", main_path, None, "main.sdf must contain active !include(slides)")


def check_ordering(slide_files: list[Path], findings: list[Finding]) -> None:
    seen: dict[str, Path] = {}
    numeric_count = 0
    for path in slide_files:
        match = NUMERIC_PREFIX_RE.match(path.name)
        if not match:
            add(findings, "warning", path, None, "slide filename has no numeric prefix; verify sort order is intentional")
            continue
        numeric_count += 1
        prefix = match.group(1)
        if prefix in seen:
            add(findings, "warning", path, None, f"duplicate numeric prefix also used by {seen[prefix]}")
        else:
            seen[prefix] = path
    if slide_files and numeric_count == 0:
        add(findings, "warning", slide_files[0].parent, None, "no slide files use numeric prefixes; alphabetical order still controls presentation order")


def check_deck(deck_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    deck_dir = deck_dir.resolve()

    if not deck_dir.exists():
        add(findings, "error", deck_dir, None, "deck directory does not exist")
        return findings
    if not deck_dir.is_dir():
        add(findings, "error", deck_dir, None, "deck path is not a directory")
        return findings

    main_path = deck_dir / "main.sdf"
    env_path = deck_dir / ".env"
    slides_dir = deck_dir / "slides"

    if not main_path.exists():
        add(findings, "error", main_path, None, "missing main.sdf")
    if not env_path.exists():
        add(findings, "error", env_path, None, "missing .env")
    if not slides_dir.exists():
        add(findings, "error", slides_dir, None, "missing slides directory")
    elif not slides_dir.is_dir():
        add(findings, "error", slides_dir, None, "slides path is not a directory")

    if main_path.exists():
        check_main_sdf(deck_dir, main_path, findings)

    if slides_dir.exists() and slides_dir.is_dir():
        slide_files = sorted(slides_dir.glob("*.sdf"))
        if not slide_files:
            add(findings, "warning", slides_dir, None, "slides directory contains no .sdf files")
        check_ordering(slide_files, findings)
        for path in slide_files:
            text = read_text(path, findings)
            if text:
                check_slides_file(path, deck_dir, text, findings)

    return findings


def print_human(findings: list[Finding]) -> None:
    errors = [item for item in findings if item.level == "error"]
    warnings = [item for item in findings if item.level == "warning"]
    if not findings:
        print("OK: no issues found")
        return
    for item in findings:
        location = item.path if item.line is None else f"{item.path}:{item.line}"
        print(f"{item.level.upper()}: {location}: {item.message}")
    print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s)")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check a SliDesk deck without starting a SliDesk server.")
    parser.add_argument("deck", help="Path to the deck directory")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    findings = check_deck(Path(args.deck))
    errors = [item for item in findings if item.level == "error"]
    warnings = [item for item in findings if item.level == "warning"]

    if args.json:
        print(json.dumps({
            "ok": not errors,
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": [item.as_dict() for item in findings],
        }, ensure_ascii=False, indent=2))
    else:
        print_human(findings)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
