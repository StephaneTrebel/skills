# smart-slidesk Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the reusable `smart-slidesk` skill for SliDesk deck authoring, review, and deterministic validation.

**Architecture:** Keep procedural instructions in `SKILL.md`, reusable slide examples in `references/patterns.md`, UI metadata in `agents/openai.yaml`, and deterministic validation in `scripts/check_deck.py`. The checker is standalone Python and accepts a deck directory path.

**Tech Stack:** Codex skill markdown, YAML metadata, Python 3 standard library, SliDesk `.sdf` decks.

---

### Task 1: Skill Instructions

**Files:**
- Create: `.agents/skills/smart-slidesk/SKILL.md`

- [x] Write `SKILL.md` with frontmatter, explicit Technical/Narrative/Authoring phases, deck rules, new-deck workflow, ordering rules, protected raw HTML guidance, and required checker usage.

### Task 2: Pattern Reference And Metadata

**Files:**
- Create: `.agents/skills/smart-slidesk/references/patterns.md`
- Create: `.agents/skills/smart-slidesk/agents/openai.yaml`

- [x] Add concise SliDesk snippets for chapter, content, full-image, meme/image, quote, two-column, speaker, and closing/resources slides.
- [x] Add UI metadata with display name, short description, and default prompt.

### Task 3: Checker Script

**Files:**
- Create: `.agents/skills/smart-slidesk/scripts/check_deck.py`

- [x] Write a Python checker that validates deck structure, `main.sdf` scaffold rules, slide note blocks, local image paths, include comments, ordering warnings, and JSON output.
- [x] Ensure missing local image paths are errors and external URLs are allowed.

### Task 4: Verification

**Files:**
- Read: `.agents/skills/smart-slidesk/SKILL.md`
- Execute: `.agents/skills/smart-slidesk/scripts/check_deck.py`

- [x] Run syntax checks for the Python script.
- [x] Run the checker against `slidesk_template`.
- [x] Run focused temporary-deck checks for missing notes, missing images, JSON output, and valid class-only headings.
- [x] Inspect git status and targeted diffs.
