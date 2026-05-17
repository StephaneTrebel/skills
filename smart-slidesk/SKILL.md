---
name: smart-slidesk
description: Use when creating, reviewing, editing, validating, or maintaining SliDesk Markdown decks with slidesk.toml, main.md, ordered slides/*.md, speaker notes, timing comments, local assets, or narrative review needs; also when legacy .sdf decks are encountered.
---

# smart-slidesk

## Core Rules

- Always state the active phase before acting: `Phase: Technical pass`, `Phase: Narrative pass`, or `Phase: Authoring pass`.
- The user must explicitly name the deck. The deck name maps to a direct child directory of the current repo.
- Current standard is `<deck>/slidesk.toml`, scaffold-only `<deck>/main.md` with the required SliDesk customisation container, and ordered `<deck>/slides/*.md`.
- New decks always use the current standard. Do not create `.env`, `main.sdf`, `slides/*.sdf`, or `common -> ../common` for new decks.
- Existing current-standard decks stay Markdown-only. Never edit `.env` or create `.sdf` files in them.
- Existing legacy decks may be authored as-is, but mention they are legacy and that deterministic structural checking only covers the current Markdown standard.
- Read the whole text deck before authoring or narrative review. For current decks, read `slidesk.toml`, `main.md`, and `slides/*.md`; for legacy decks, read `.env`, `main.sdf`, and `slides/*.sdf`.
- Preserve existing `//@` timing comments exactly unless the user explicitly asks to change them.
- Every slide must have a `/* ... */` speaker notes block. Use `To Be Defined` when no note content is known.
- Preserve raw HTML exactly unless the user explicitly confirms a change to that block, or the request directly targets that exact block.
- Prefer local assets under `<deck>/assets` or `common/assets`. Generate or download images only when explicitly asked.
- Default to French for new decks or unclear language; otherwise preserve the deck language and voice.
- Emoji and visual humor are allowed. Follow "show, don't tell": sparse visual slides, richer speaker notes.

## Phase Selection

Use `Technical pass` for deterministic checks: format status, config, entrypoint, includes, notes, image paths, ordering, and scaffold rules.

Use `Narrative pass` for editorial review: story arc, rhythm, density, transitions, slide economy, audience fit, humor, and meme opportunities. Narrative findings are proposals, not technical failures. Do not edit after a narrative pass until the user confirms.

Use `Authoring pass` for creating a deck, adding slides, amending slides, reorganizing files, or changing speaker notes after the deck and requested change are explicit.

Mixed requests such as "review this deck and fix issues" run Technical pass first, Narrative pass second, then wait for confirmation before Authoring pass edits unless the user explicitly authorized immediate technical fixes.

## Technical Pass

Run the checker whenever possible:

```bash
rtk python3 .agents/skills/smart-slidesk/scripts/check_deck.py <deck>
```

If this skill is installed elsewhere, use the equivalent installed script path.

The checker validates current-standard Markdown decks and reports legacy decks without structurally checking their `.sdf` content. It covers:

- format status: current, mixed, legacy, unknown, missing, or invalid
- mandatory `slidesk.toml`, `[slidesk]`, and uppercase string `TITLE`
- light type checks for common `slidesk.toml` keys
- scaffold-only `main.md`, including the required top-level `/: ... ::/` customisation container before includes
- active Markdown includes, with `!include(slides, md)` as the house default
- `add_styles` and `add_scripts` entries in the customisation container, with local asset path checks when possible
- include path existence and `include_mode` metadata
- ordered `slides/*.md`, numeric-prefix warnings, and duplicate-prefix warnings
- `##` slide boundaries, including class-only headings such as `## .[cover]`
- first-slide content before the first `##`, when present
- speaker notes before the next `##` or end of file
- balanced `/* ... */` note blocks, ignoring fenced code blocks
- local paths in `!image(...)`, Markdown images, and raw HTML `<img src="...">`
- `++KEY++` interpolation warnings when no matching `[slidesk]` key exists
- commented-out includes such as `//// !include(...)` as warnings
- deprecated `.env`, `main.sdf`, and `slides/*.sdf` artifacts as warnings unless `main.md` includes `sdf`, which is an error

Report format:

```text
Phase: Technical pass
Format: <checker format line>
Findings:
- <path>:<line> <message>
Proposed Changes:
- <only when edits are needed>
Validation:
- <checker command and result>
```

For legacy decks, say that the deck uses legacy SDF/.env conventions, the current standard is `slidesk.toml + main.md + slides/*.md`, and legacy content was not structurally checked. Offer conversion only if the user asks; do not block ordinary work.

## Narrative Pass

Separate editorial judgment from technical validation. A narrative pass reviews:

- story arc and chapter flow
- rhythm, density, and breathing room
- tension/release, visual pauses, demos, quotes, recaps, and meme opportunities
- transitions between sections
- whether slides show instead of tell
- whether notes support delivery instead of repeating visible text
- audience fit, vocabulary, and humor
- timing comments as user-owned checkpoints

Do not edit during a narrative pass. Produce concise findings and proposed changes first.

Report format:

```text
Phase: Narrative pass
Findings:
- <slide title or section, with file path when useful>
Proposed Changes:
- <specific editorial proposal>
Validation:
- Editorial pass only; no technical checker result unless also run.
```

## Authoring Pass

Before editing:

1. Confirm the explicit deck directory exists.
2. Detect whether the deck is current-standard, mixed, or legacy.
3. Read all text deck files for that format.
4. Identify existing classes, include mode, tone, assets, timing comments, and raw HTML.

Current-standard authoring rules:

- Before creating or changing `main.md`, ask the user whether custom CSS or custom scripts should be loaded. If yes, write them into the top customisation container with comma-separated `add_styles` and/or `add_scripts` entries; prefer local files under `<deck>/assets` or `common/assets`.
- Keep `main.md` scaffold-only. It must start with the SliDesk customisation container before the first include. Use an empty container when no custom assets are needed:

```md
/::
::/

!include(slides, md)
```

- With custom CSS or scripts:

```md
/::
add_styles: assets/custom.css
add_scripts: assets/custom.js
::/

!include(slides, md)
```

- It should normally contain only that customisation container, `!include(slides, md)`, timing comments, SliDesk comments, and blank lines.
- Slides live in `slides/*.md`.
- If `main.md` uses `!include(slides, md)`, file sort order controls presentation order.
- If `main.md` uses individual Markdown includes, include order in `main.md` controls presentation order.
- Prefer `!include(slides, md)` for new decks and new scaffolds.
- Use `slidesk.toml` for configuration. Require `[slidesk]`, `TITLE`, and `WIDTH = 1920` for new decks.
- Preserve `++KEY++` interpolation and add missing keys only when the user asks or the authoring change requires them.

Legacy authoring rules:

- Mention once that the deck is legacy and structurally unchecked by the current checker.
- Work as-is unless the user explicitly asks for conversion.
- Preserve `main.sdf` as scaffold-only and keep legacy slide content in `slides/*.sdf`.
- Preserve `.env` when editing legacy config.
- Prefer copying patterns from the existing legacy deck rather than from `references/patterns.md`.

When adding slides:

- Use existing deck examples and classes first.
- Use `references/patterns.md` only when local examples do not fit.
- Same-section slides may be appended to the relevant existing slide file.
- New chapters or major sections may get a new numbered file.
- Do not renumber by default.
- If renumbering would improve clarity, propose it first with concrete consequences.
- For new chapter checkpoints, propose `//@ < TBD`; do not invent real timing.

When editing speaker notes:

- Treat slide body and `/* ... */` notes as separate regions.
- If the user asks for notes, change only notes unless slide content is also requested.
- Every slide keeps a notes block, even full-image and meme slides.
- New authored note markers should be line-isolated:

```md
/*
To Be Defined
*/
```

When using images:

- Prefer existing local assets.
- Use SliDesk `!image(path, alt, width, height, styles, caption)` for simple images.
- Markdown image syntax is allowed when it is a better fit.
- Use raw HTML only when layout requires it.
- Avoid text-only meme placeholders unless the user asks for a draft placeholder.

After edits:

1. Run the checker.
2. Report changed files, validation command, errors, warnings, and anything not verified.
3. For legacy decks, explicitly state that legacy content was not structurally checked.

## New Deck Workflow

When creating a deck:

1. Require an explicit deck directory name.
2. Create `<repo-root>/<deck-name>/` directly; do not use `slidesk_template`.
3. Create `<deck>/slidesk.toml`:

```toml
[slidesk]
TITLE = "<deck title>"
WIDTH = 1920
```

4. Ask whether custom CSS or custom scripts should be loaded. Create scaffold-only `<deck>/main.md`; use an empty customisation container when none are requested:

```md
/::
::/

!include(slides, md)
```

5. If custom assets are requested, populate the container with comma-separated paths:

```md
/::
add_styles: assets/custom.css
add_scripts: assets/custom.js
::/

!include(slides, md)
```

6. Create `<deck>/slides/10-cover.md`:

```md
## .[cover]

# <Deck Title>

/*
To Be Defined
*/
```

7. Create `<deck>/assets/`.
8. Run the checker.

## Optional Conversion Guidance

Only convert a legacy deck when the user explicitly asks. There is no automatic migration pass and no conversion helper script.

Recommended conversion steps:

1. Convert `.env` values into `[slidesk]` keys in `slidesk.toml`.
2. Rename `main.sdf` to `main.md`.
3. Change directory includes to `!include(slides, md)`.
4. Rename `slides/*.sdf` to `slides/*.md`.
5. Remove stale `.env` and `.sdf` files after confirming the conversion.
6. Run the checker and resolve current-standard findings.

## File Ordering

- Preserve existing numeric prefix style.
- Prefer gaps such as `25-new-topic.md` between `20-foo.md` and `30-bar.md`.
- When appending before `99-speaker.md`, use the next available prefix below `99`.
- Sorting order matters more than numeric aesthetics when using directory includes.
- Include order matters more than filename order when using individual includes.
- Never silently renumber. Explain consequences before changing existing filenames.

## References

- Read `references/patterns.md` when adding slide patterns or when local examples are insufficient.
- Current SliDesk documentation: https://slidesk.github.io/slidesk/
- SliDesk customisation container docs: https://slidesk.github.io/slidesk/customisation/
- If SliDesk syntax or configuration behavior is uncertain, check the current docs or upstream docs source before inventing syntax.
