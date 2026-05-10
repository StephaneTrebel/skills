# smart-slidesk Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update `smart-slidesk` from legacy SDF/.env assumptions to the current SliDesk Markdown plus `slidesk.toml` standard.

**Architecture:** Keep procedural instructions in `SKILL.md`, reusable Markdown examples in `references/patterns.md`, UI metadata in `agents/openai.yaml`, and deterministic current-standard validation in `scripts/check_deck.py`. The checker auto-detects current, legacy-only, and mixed decks, but structurally validates only current-standard Markdown decks.

**Tech Stack:** Codex skill markdown, YAML metadata, Python 3 standard library, SliDesk Markdown decks, focused command checks. Do not commit; the user explicitly requested uncommitted changes.

---

### Task 1: Establish Checker RED Baseline

**Files:**
- Read: `smart-slidesk/scripts/check_deck.py`
- Temporary: `/tmp/smart-slidesk-modernization-red`

- [x] Create temporary current-standard, legacy-only, and invalid Markdown fixture decks under `/tmp`.
- [x] Run the current checker against those fixtures.
- [x] Confirm the current checker fails the new-standard deck and lacks the required format metadata.

### Task 2: Implement Current-Standard Checker

**Files:**
- Modify: `smart-slidesk/scripts/check_deck.py`

- [x] Replace SDF-first structure checks with auto-detected current/legacy/mixed format metadata.
- [x] Add `slidesk.toml` parsing and light type validation with `tomllib`.
- [x] Validate scaffold-only `main.md`, active includes, include mode, and include path existence.
- [x] Validate `slides/*.md` ordering, slide boundaries, notes, fenced code handling, timing comments, interpolation, and visible content after notes.
- [x] Validate referenced media in `!image(...)`, Markdown image syntax, and raw HTML `<img src="...">`.
- [x] Keep legacy-only decks successful with warnings and no structural legacy validation.
- [x] Add JSON fields: `format`, `is_current_standard`, `format_message`, and `include_mode`.

### Task 3: Verify Checker Behavior

**Files:**
- Execute: `smart-slidesk/scripts/check_deck.py`

- [x] Run focused fixture checks for current success, missing config, bad `main.md`, empty slides, legacy-only warning, mixed artifacts, `sdf` include error, missing image paths, fenced code handling, inline notes, missing notes, interpolation warnings, and JSON metadata.
- [x] Run Python syntax check.

### Task 4: Update Skill Instructions And Resources

**Files:**
- Modify: `smart-slidesk/SKILL.md`
- Modify: `smart-slidesk/references/patterns.md`
- Modify: `smart-slidesk/agents/openai.yaml`

- [x] Rewrite `SKILL.md` around `slidesk.toml`, `main.md`, and ordered `slides/*.md`.
- [x] Keep compact legacy authoring guidance, but state legacy decks are not structurally checked.
- [x] Remove stale `slidesk-doc` links and point to `https://slidesk.github.io/slidesk/`.
- [x] Convert pattern snippets from `sdf` fences to `md` fences.
- [x] Update metadata to mention Markdown decks and legacy support.

### Task 5: Final Verification

**Files:**
- Execute: `smart-slidesk/scripts/check_deck.py`
- Execute: skill validation when available

- [x] Run the full focused checker verification again.
- [x] Run syntax/whitespace checks on changed files.
- [x] Validate skill frontmatter/metadata if the local validator is available.
- [x] Inspect git diff and status.
- [x] Do not commit.
