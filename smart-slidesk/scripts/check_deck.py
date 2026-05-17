#!/usr/bin/env python3
"""Deterministic checks for current-standard SliDesk decks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback.
    tomllib = None  # type: ignore[assignment]


SLIDE_HEADING_RE = re.compile(r"^\s*##(?!#)(?:\s|$)")
INCLUDE_RE = re.compile(r"!include\(([^)]*)\)")
SLIDESK_IMAGE_RE = re.compile(r"!image\(([^)]*)\)")
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*]\(([^)\s]+)(?:\s+[^)]*)?\)")
HTML_IMAGE_RE = re.compile(r"<img\b[^>]*\bsrc\s*=\s*([\"'])(.*?)\1", re.IGNORECASE)
INTERPOLATION_RE = re.compile(r"\+\+([A-Za-z_][A-Za-z0-9_]*)\+\+")
NUMERIC_MD_PREFIX_RE = re.compile(r"^(\d+)[-_].+\.md$")
CUSTOM_ASSET_RE = re.compile(r"^(add_styles|add_scripts)\s*:\s*(.+)$")

CURRENT_STANDARD = "slidesk.toml + main.md + slides/*.md"


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


@dataclass
class CheckResult:
    findings: list[Finding]
    format: str
    is_current_standard: bool
    format_message: str
    include_mode: str = "missing"

    @property
    def errors(self) -> list[Finding]:
        return [item for item in self.findings if item.level == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [item for item in self.findings if item.level == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "format": self.format,
            "is_current_standard": self.is_current_standard,
            "format_message": self.format_message,
            "include_mode": self.include_mode,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "findings": [item.as_dict() for item in self.findings],
        }


@dataclass
class IncludeSummary:
    mode: str
    includes_sdf: bool
    main_text: str


@dataclass
class NoteAnalysis:
    blocks: list[tuple[int, int]]
    note_lines: set[int]


def add(findings: list[Finding], level: str, path: Path | str, line: int | None, message: str) -> None:
    findings.append(Finding(level, str(path), line, message))


def read_text(path: Path, findings: list[Finding]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        add(findings, "error", path, None, "file is not valid UTF-8 text")
    except OSError as exc:
        add(findings, "error", path, None, f"cannot read file: {exc}")
    return None


def split_args(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    quote: str | None = None
    for char in value:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char == ",":
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    parts.append("".join(current).strip())
    return parts


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def first_image_arg(args: str) -> str:
    parts = split_args(args)
    return strip_quotes(parts[0]) if parts else ""


def is_external_path(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "data"}


def is_dynamic_path(value: str) -> bool:
    return "++" in value or value.startswith("$") or "${" in value


def normalize_media_path(value: str) -> str:
    value = strip_quotes(value).strip()
    if len(value) >= 2 and value[0] == "<" and value[-1] == ">":
        value = value[1:-1].strip()
    return value


def local_path_without_query(value: str) -> str:
    return value.split("#", 1)[0].split("?", 1)[0]


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def markdown_files(slides_dir: Path) -> list[Path]:
    if not slides_dir.exists() or not slides_dir.is_dir():
        return []
    return sorted(path for path in slides_dir.iterdir() if path.is_file() and path.suffix == ".md")


def extension_files(slides_dir: Path, suffix: str) -> list[Path]:
    if not slides_dir.exists() or not slides_dir.is_dir():
        return []
    return sorted(path for path in slides_dir.iterdir() if path.is_file() and path.suffix == suffix)


def detect_format(deck_dir: Path) -> tuple[str, str, bool]:
    slides_dir = deck_dir / "slides"
    has_current = (
        (deck_dir / "main.md").exists()
        or (deck_dir / "slidesk.toml").exists()
        or bool(markdown_files(slides_dir))
    )
    has_legacy = (
        (deck_dir / "main.sdf").exists()
        or (deck_dir / ".env").exists()
        or bool(extension_files(slides_dir, ".sdf"))
    )

    if has_current and has_legacy:
        return (
            "mixed",
            f"current Markdown standard with legacy artifacts; current standard is {CURRENT_STANDARD}",
            False,
        )
    if has_current:
        return ("current", "current Markdown standard", True)
    if has_legacy:
        return (
            "legacy",
            f"legacy SDF deck; current standard is {CURRENT_STANDARD}",
            False,
        )
    return (
        "unknown",
        f"no SliDesk deck format detected; current standard is {CURRENT_STANDARD}",
        False,
    )


def add_legacy_artifact_warnings(deck_dir: Path, findings: list[Finding]) -> None:
    env_path = deck_dir / ".env"
    main_sdf = deck_dir / "main.sdf"
    if env_path.exists():
        add(findings, "warning", env_path, None, ".env is deprecated; use slidesk.toml for current-standard decks")
    if main_sdf.exists():
        add(findings, "warning", main_sdf, None, "main.sdf is a legacy artifact; use scaffold-only main.md")


def check_toml(deck_dir: Path, findings: list[Finding]) -> set[str]:
    toml_path = deck_dir / "slidesk.toml"
    if not toml_path.exists():
        add(findings, "error", toml_path, None, "missing slidesk.toml")
        return set()
    if not toml_path.is_file():
        add(findings, "error", toml_path, None, "slidesk.toml is not a file")
        return set()

    text = read_text(toml_path, findings)
    if text is None:
        return set()
    if tomllib is None:
        add(findings, "error", toml_path, None, "Python tomllib is unavailable; Python 3.11+ is required")
        return set()

    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        add(findings, "error", toml_path, None, f"slidesk.toml is invalid TOML: {exc}")
        return set()

    slidesk = data.get("slidesk")
    if not isinstance(slidesk, dict):
        add(findings, "error", toml_path, None, "slidesk.toml must contain a [slidesk] table")
        return set()

    keys = {str(key) for key in slidesk}
    title = slidesk.get("TITLE")
    if not isinstance(title, str):
        add(findings, "error", toml_path, None, "[slidesk].TITLE is required and must be a string")

    int_keys = {"WIDTH", "PORT", "TRANSITION", "TELNET_PORT"}
    bool_keys = {"HTTPS", "WATCH"}
    string_keys = {"DOMAIN", "KEY", "CERT", "PASSPHRASE"}

    for key in sorted(int_keys & keys):
        if not isinstance(slidesk[key], int) or isinstance(slidesk[key], bool):
            add(findings, "warning", toml_path, None, f"[slidesk].{key} should be an integer")
    for key in sorted(bool_keys & keys):
        if not isinstance(slidesk[key], bool):
            add(findings, "warning", toml_path, None, f"[slidesk].{key} should be a boolean")
    for key in sorted(string_keys & keys):
        if not isinstance(slidesk[key], str):
            add(findings, "warning", toml_path, None, f"[slidesk].{key} should be a string")

    return keys


def parse_include(raw_args: str) -> tuple[str, list[str]]:
    parts = split_args(raw_args)
    if not parts:
        return "", []
    include_path = strip_quotes(parts[0])
    extensions = [strip_quotes(part).lstrip(".").lower() for part in parts[1:] if strip_quotes(part)]
    return include_path, extensions


def check_include_path(
    deck_dir: Path,
    main_path: Path,
    line_no: int,
    include_path: str,
    findings: list[Finding],
) -> Path | None:
    if not include_path:
        add(findings, "error", main_path, line_no, "!include(...) is missing its path")
        return None
    if is_dynamic_path(include_path):
        add(findings, "warning", main_path, line_no, f"dynamic include path not checked: {include_path}")
        return None
    candidate = Path(include_path)
    resolved = candidate if candidate.is_absolute() else deck_dir / candidate
    if not resolved.exists():
        add(findings, "error", main_path, line_no, f"included path does not exist: {include_path}")
    return resolved


def check_custom_asset_paths(
    deck_dir: Path,
    main_path: Path,
    line_no: int,
    raw_value: str,
    findings: list[Finding],
) -> None:
    for raw_path in raw_value.split(","):
        value = normalize_media_path(raw_path)
        if not value:
            continue
        if is_external_path(value) or is_dynamic_path(value):
            continue
        candidate = local_path_without_query(value)
        resolved = deck_dir / candidate
        if not resolved.exists():
            add(findings, "warning", main_path, line_no, f"custom asset path does not exist: {value}")


def check_main_md(deck_dir: Path, findings: list[Finding]) -> IncludeSummary:
    main_path = deck_dir / "main.md"
    if not main_path.exists():
        add(findings, "error", main_path, None, "missing main.md")
        return IncludeSummary("missing", False, "")
    if not main_path.is_file():
        add(findings, "error", main_path, None, "main.md is not a file")
        return IncludeSummary("missing", False, "")

    text = read_text(main_path, findings)
    if text is None:
        return IncludeSummary("missing", False, "")

    directory_includes = 0
    individual_includes = 0
    includes_sdf = False
    in_slidesk_comment: int | None = None
    saw_customisation_container = False

    nonblank_lines = [(line_no, line.strip()) for line_no, line in enumerate(text.splitlines(), 1) if line.strip()]
    if not nonblank_lines or nonblank_lines[0][1] != "/::":
        line_no = nonblank_lines[0][0] if nonblank_lines else None
        add(
            findings,
            "error",
            main_path,
            line_no,
            "main.md must start with the SliDesk customisation container: /:: ... ::/",
        )

    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        if in_slidesk_comment is not None:
            custom_asset_match = CUSTOM_ASSET_RE.match(stripped)
            if custom_asset_match:
                check_custom_asset_paths(deck_dir, main_path, line_no, custom_asset_match.group(2), findings)
            if stripped == "::/":
                in_slidesk_comment = None
            continue
        if stripped == "/::":
            saw_customisation_container = True
            in_slidesk_comment = line_no
            continue
        if stripped.startswith("////"):
            if "!include(" in stripped:
                add(findings, "warning", main_path, line_no, "include is commented out with ////; verify this is intentional")
            continue
        if stripped.startswith("//@"):
            if not stripped[3:].strip():
                add(findings, "warning", main_path, line_no, "timing comment starts with //@ but has no body")
            continue
        if SLIDE_HEADING_RE.match(line):
            add(findings, "error", main_path, line_no, "main.md is scaffold-only and must not contain ## slides")
            continue

        include_match = INCLUDE_RE.fullmatch(stripped)
        if include_match:
            include_path, extensions = parse_include(include_match.group(1))
            resolved = check_include_path(deck_dir, main_path, line_no, include_path, findings)
            normalized = include_path.rstrip("/")
            suffix = Path(include_path).suffix.lower()
            has_sdf = "sdf" in extensions or suffix == ".sdf"

            if has_sdf:
                includes_sdf = True
                add(findings, "error", main_path, line_no, "current-standard main.md must not include sdf content")

            if normalized == "slides" and not extensions:
                add(findings, "error", main_path, line_no, "use !include(slides, md); directory includes default to sdf")
            elif normalized == "slides" and "md" in extensions:
                directory_includes += 1
            elif suffix == ".md":
                individual_includes += 1
                if resolved and not is_relative_to(resolved.resolve(), (deck_dir / "slides").resolve()):
                    add(findings, "warning", main_path, line_no, "individual Markdown include is outside slides/")
            elif "md" in extensions:
                directory_includes += 1
                if normalized != "slides":
                    add(findings, "warning", main_path, line_no, "Markdown directory include is outside the house-standard slides/ directory")
            else:
                add(findings, "warning", main_path, line_no, "include does not explicitly include Markdown slides")
            continue

        if "!include(" in stripped:
            add(findings, "error", main_path, line_no, "main.md include lines must contain only one !include(...) directive")
            continue

        add(findings, "error", main_path, line_no, "main.md is scaffold-only; move visible slide content to slides/*.md")

    if in_slidesk_comment is not None:
        add(findings, "error", main_path, in_slidesk_comment, "SliDesk customisation container starts with /:: but is not closed with ::/")
    if not saw_customisation_container:
        add(findings, "error", main_path, None, "main.md must contain a top-level SliDesk customisation container")

    if directory_includes and individual_includes:
        add(findings, "warning", main_path, None, "main.md mixes directory and individual Markdown includes; choose one ordering model")
        mode = "mixed"
    elif directory_includes:
        mode = "directory"
    elif individual_includes:
        add(findings, "warning", main_path, None, "individual Markdown includes are allowed, but the house default is !include(slides, md)")
        mode = "individual"
    else:
        add(findings, "error", main_path, None, "main.md must include Markdown slides with !include(slides, md) or individual .md includes")
        mode = "missing"

    return IncludeSummary(mode, includes_sdf, text)


def check_ordering(slide_files: list[Path], findings: list[Finding]) -> None:
    seen: dict[str, Path] = {}
    numeric_count = 0
    for path in slide_files:
        match = NUMERIC_MD_PREFIX_RE.match(path.name)
        if not match:
            add(findings, "warning", path, None, "slide filename has no numeric prefix; verify ordering is intentional")
            continue
        numeric_count += 1
        prefix = match.group(1)
        if prefix in seen:
            add(findings, "warning", path, None, f"duplicate numeric prefix also used by {seen[prefix]}")
        else:
            seen[prefix] = path
    if slide_files and numeric_count == 0:
        add(findings, "warning", slide_files[0].parent, None, "no slide files use numeric prefixes; ordering still controls presentation")


def fenced_line_mask(lines: list[str]) -> list[bool]:
    mask: list[bool] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in lines:
        stripped = line.lstrip()
        if not in_fence and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence_char = stripped[0]
            fence_len = len(stripped) - len(stripped.lstrip(fence_char))
            in_fence = True
            mask.append(True)
            continue
        if in_fence:
            mask.append(True)
            if stripped.startswith(fence_char * fence_len):
                in_fence = False
            continue
        mask.append(False)
    return mask


def analyze_notes(path: Path, lines: list[str], fenced: list[bool], findings: list[Finding]) -> NoteAnalysis:
    open_idx: int | None = None
    blocks: list[tuple[int, int]] = []
    warned_style_lines: set[int] = set()

    for idx, line in enumerate(lines):
        if fenced[idx]:
            continue
        search_from = 0
        while True:
            start = line.find("/*", search_from)
            end = line.find("*/", search_from)
            if start == -1 and end == -1:
                break
            if end != -1 and (start == -1 or end < start):
                if line.strip() != "*/" and idx not in warned_style_lines:
                    add(findings, "warning", path, idx + 1, "speaker-note markers should be on their own lines")
                    warned_style_lines.add(idx)
                if open_idx is None:
                    add(findings, "error", path, idx + 1, "closing speaker-note marker without opening /*")
                else:
                    blocks.append((open_idx, idx))
                    open_idx = None
                search_from = end + 2
                continue
            if start != -1:
                if line.strip() != "/*" and idx not in warned_style_lines:
                    add(findings, "warning", path, idx + 1, "speaker-note markers should be on their own lines")
                    warned_style_lines.add(idx)
                if open_idx is not None:
                    add(findings, "error", path, idx + 1, f"nested speaker-note marker before closing block opened on line {open_idx + 1}")
                open_idx = idx
                search_from = start + 2

    if open_idx is not None:
        add(findings, "error", path, open_idx + 1, "speaker-note block is not closed")

    note_lines: set[int] = set()
    for start, end in blocks:
        note_lines.update(range(start, end + 1))
    return NoteAnalysis(blocks, note_lines)


def is_visible_content_line(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith("////") and not stripped.startswith("//@")


def first_visible_line(
    lines: list[str],
    fenced: list[bool],
    note_lines: set[int],
    start: int,
    end: int,
) -> int | None:
    for idx in range(start, end):
        if fenced[idx] or idx in note_lines:
            continue
        if is_visible_content_line(lines[idx]):
            return idx
    return None


def segment_has_notes(blocks: list[tuple[int, int]], start: int, end: int) -> bool:
    return any(block_start >= start and block_end < end for block_start, block_end in blocks)


def warn_visible_content_after_notes(
    path: Path,
    lines: list[str],
    fenced: list[bool],
    analysis: NoteAnalysis,
    start: int,
    end: int,
    findings: list[Finding],
) -> None:
    segment_blocks = [(block_start, block_end) for block_start, block_end in analysis.blocks if block_start >= start and block_end < end]
    if not segment_blocks:
        return
    last_note_end = max(block_end for _, block_end in segment_blocks)
    visible_idx = first_visible_line(lines, fenced, analysis.note_lines, last_note_end + 1, end)
    if visible_idx is not None:
        add(findings, "warning", path, visible_idx + 1, "visible slide content appears after the speaker-notes block")


def validate_media_path(
    deck_dir: Path,
    source_path: Path,
    line_no: int,
    kind: str,
    raw_path: str,
    findings: list[Finding],
) -> None:
    media_path = normalize_media_path(raw_path)
    if not media_path:
        add(findings, "error", source_path, line_no, f"{kind} is missing its path")
        return
    if media_path.startswith("#"):
        return
    if is_external_path(media_path):
        return
    if is_dynamic_path(media_path):
        add(findings, "warning", source_path, line_no, f"dynamic media path not checked: {media_path}")
        return
    local_path = local_path_without_query(media_path)
    if not local_path:
        return
    candidate = Path(local_path)
    resolved = candidate if candidate.is_absolute() else deck_dir / candidate
    if not resolved.exists():
        add(findings, "error", source_path, line_no, f"local {kind} path does not exist: {media_path}")


def check_media_references(deck_dir: Path, path: Path, lines: list[str], fenced: list[bool], findings: list[Finding]) -> None:
    for idx, line in enumerate(lines):
        if fenced[idx]:
            continue
        line_no = idx + 1
        for match in SLIDESK_IMAGE_RE.finditer(line):
            validate_media_path(deck_dir, path, line_no, "!image(...)", first_image_arg(match.group(1)), findings)
        for match in MARKDOWN_IMAGE_RE.finditer(line):
            validate_media_path(deck_dir, path, line_no, "Markdown image", match.group(1), findings)
        for match in HTML_IMAGE_RE.finditer(line):
            validate_media_path(deck_dir, path, line_no, "HTML image", match.group(2), findings)


def check_timing_comments(path: Path, lines: list[str], fenced: list[bool], findings: list[Finding]) -> None:
    for idx, line in enumerate(lines):
        if fenced[idx]:
            continue
        stripped = line.strip()
        if stripped.startswith("//@") and not stripped[3:].strip():
            add(findings, "warning", path, idx + 1, "timing comment starts with //@ but has no body")


def check_commented_includes(path: Path, lines: list[str], fenced: list[bool], findings: list[Finding]) -> None:
    for idx, line in enumerate(lines):
        if fenced[idx]:
            continue
        stripped = line.strip()
        if stripped.startswith("////") and "!include(" in stripped:
            add(findings, "warning", path, idx + 1, "include is commented out with ////; verify this is intentional")


def check_interpolations(path: Path, text: str, slidesk_keys: set[str], findings: list[Finding]) -> None:
    lines = text.splitlines()
    fenced = fenced_line_mask(lines)
    for idx, line in enumerate(lines):
        if fenced[idx]:
            continue
        for match in INTERPOLATION_RE.finditer(line):
            key = match.group(1)
            if key not in slidesk_keys:
                add(findings, "warning", path, idx + 1, f"interpolation ++{key}++ has no matching [slidesk] key")


def check_slide_file(deck_dir: Path, path: Path, text: str, slidesk_keys: set[str], findings: list[Finding]) -> None:
    lines = text.splitlines()
    fenced = fenced_line_mask(lines)
    analysis = analyze_notes(path, lines, fenced, findings)
    heading_indices = [idx for idx, line in enumerate(lines) if not fenced[idx] and SLIDE_HEADING_RE.match(line)]

    segments: list[tuple[int, int, int]] = []
    if heading_indices:
        initial_visible = first_visible_line(lines, fenced, analysis.note_lines, 0, heading_indices[0])
        if initial_visible is not None:
            segments.append((0, heading_indices[0], initial_visible))
        for index, heading_idx in enumerate(heading_indices):
            next_heading = heading_indices[index + 1] if index + 1 < len(heading_indices) else len(lines)
            segments.append((heading_idx, next_heading, heading_idx))
    else:
        visible = first_visible_line(lines, fenced, analysis.note_lines, 0, len(lines))
        if visible is not None:
            segments.append((0, len(lines), visible))

    for start, end, report_idx in segments:
        if not segment_has_notes(analysis.blocks, start, end):
            add(findings, "error", path, report_idx + 1, "slide is missing a /* ... */ speaker notes block before the next slide")
        else:
            warn_visible_content_after_notes(path, lines, fenced, analysis, start, end, findings)

    check_timing_comments(path, lines, fenced, findings)
    check_commented_includes(path, lines, fenced, findings)
    check_media_references(deck_dir, path, lines, fenced, findings)
    check_interpolations(path, text, slidesk_keys, findings)


def check_slides_dir(deck_dir: Path, includes_sdf: bool, slidesk_keys: set[str], findings: list[Finding]) -> None:
    slides_dir = deck_dir / "slides"
    if not slides_dir.exists():
        add(findings, "error", slides_dir, None, "missing slides directory")
        return
    if not slides_dir.is_dir():
        add(findings, "error", slides_dir, None, "slides path is not a directory")
        return

    md_files = markdown_files(slides_dir)
    markdown_extension_files = extension_files(slides_dir, ".markdown")
    sdf_files = extension_files(slides_dir, ".sdf")

    if not md_files:
        add(findings, "warning", slides_dir, None, "slides directory contains no .md files")
    for path in markdown_extension_files:
        add(findings, "warning", path, None, ".markdown is not the house slide extension; use .md")
    for path in sdf_files:
        if includes_sdf:
            add(findings, "error", path, None, "current-standard decks must not include .sdf slide files")
        else:
            add(findings, "warning", path, None, "legacy .sdf slide file is not included by !include(slides, md)")

    check_ordering(md_files, findings)
    for path in md_files:
        text = read_text(path, findings)
        if text is not None:
            check_slide_file(deck_dir, path, text, slidesk_keys, findings)


def check_current_standard(deck_dir: Path, findings: list[Finding]) -> str:
    slidesk_keys = check_toml(deck_dir, findings)
    include_summary = check_main_md(deck_dir, findings)
    if include_summary.main_text:
        check_interpolations(deck_dir / "main.md", include_summary.main_text, slidesk_keys, findings)
    check_slides_dir(deck_dir, include_summary.includes_sdf, slidesk_keys, findings)
    return include_summary.mode


def check_deck(deck_dir: Path) -> CheckResult:
    findings: list[Finding] = []
    deck_dir = deck_dir.resolve()

    if not deck_dir.exists():
        add(findings, "error", deck_dir, None, "deck directory does not exist")
        return CheckResult(findings, "missing", False, f"deck does not exist; current standard is {CURRENT_STANDARD}")
    if not deck_dir.is_dir():
        add(findings, "error", deck_dir, None, "deck path is not a directory")
        return CheckResult(findings, "invalid", False, f"deck path is not a directory; current standard is {CURRENT_STANDARD}")

    deck_format, format_message, is_current_standard = detect_format(deck_dir)

    if deck_format == "legacy":
        add(findings, "warning", deck_dir, None, f"legacy SDF deck detected; current standard is {CURRENT_STANDARD}")
        add(findings, "warning", deck_dir, None, "legacy SDF content was not structurally checked; ask for conversion to Markdown plus slidesk.toml first")
        return CheckResult(findings, deck_format, is_current_standard, format_message)

    if deck_format == "mixed":
        add_legacy_artifact_warnings(deck_dir, findings)

    include_mode = check_current_standard(deck_dir, findings)
    return CheckResult(findings, deck_format, is_current_standard, format_message, include_mode)


def print_human(result: CheckResult) -> None:
    print(f"Format: {result.format_message}")
    print("Findings:")
    if not result.findings:
        print("- OK: no issues found")
    else:
        for item in result.findings:
            location = item.path if item.line is None else f"{item.path}:{item.line}"
            print(f"- {item.level.upper()}: {location}: {item.message}")
    print(f"Summary: {len(result.errors)} error(s), {len(result.warnings)} warning(s)")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check a current-standard SliDesk Markdown deck without starting a SliDesk server.")
    parser.add_argument("deck", help="Path to the deck directory")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    result = check_deck(Path(args.deck))
    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    else:
        print_human(result)

    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
