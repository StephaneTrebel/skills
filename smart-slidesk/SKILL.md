---
name: smart-slidesk
description: Use when creating, reviewing, editing, validating, or maintaining SliDesk slide decks, especially decks with main.sdf, slides/*.sdf, speaker notes, timing comments, local assets, templates, or narrative review needs.
---

# smart-slidesk

## Core Rules

- Always state the active phase before acting: `Phase: Technical pass`, `Phase: Narrative pass`, or `Phase: Authoring pass`.
- The user must explicitly name the deck. The deck name maps to a direct child directory of the current repo.
- Read the whole text deck before authoring or narrative review. Deck size is not a concern; media assets are not loaded unless needed.
- `main.sdf` is scaffold-only. Never add slides to it.
- Slides live in `<deck>/slides/*.sdf`; file sort order is presentation order.
- Preserve existing `//@` timing comments exactly unless the user explicitly asks to change them.
- Every `##` slide must have a `/* ... */` speaker notes block. Use `To Be Defined` when no note content is known.
- Preserve raw HTML exactly unless the user explicitly confirms a change to that block, or the request directly targets that exact block.
- Prefer local assets under `<deck>/assets` or `common/assets`. Generate or download images only when explicitly asked.
- Default to French for new decks or unclear language; otherwise preserve the deck language and voice.
- Emoji and visual humor are allowed. Follow "show, don't tell": sparse visual slides, richer speaker notes.

## Phase Selection

Use `Technical pass` for deterministic checks: structure, includes, notes, image paths, ordering, and scaffold rules.

Use `Narrative pass` for editorial review: story arc, rhythm, density, transitions, slide economy, audience fit, humor, and meme opportunities. Narrative findings are proposals, not technical failures. Do not edit after a narrative pass until the user confirms.

Use `Authoring pass` for creating a deck, adding slides, amending slides, reorganizing files, or changing speaker notes after the deck and requested change are explicit.

Mixed requests such as "review this deck and fix issues" run Technical pass first, Narrative pass second, then wait for confirmation before Authoring pass edits unless the user explicitly authorized immediate technical fixes.

## Technical Pass

Run the checker whenever possible:

```bash
rtk python3 .agents/skills/smart-slidesk/scripts/check_deck.py <deck>
```

If this skill is installed elsewhere, use the equivalent installed script path.

The checker covers:

- `<deck>/main.sdf`, `<deck>/.env`, and `<deck>/slides/` existence
- `main.sdf` contains no `##` slides and keeps active `!include(slides)`
- slide files live in `slides/*.sdf`
- `##` slide boundaries, including class-only headings like `## .[chapter]` and `## .[full-image]`
- optional visible title/subtitle lines such as `# Bienvenue`
- speaker notes before the next `##` or end of file
- balanced `/* ... */` note blocks
- missing local `!image(...)` paths as errors
- external image URLs as allowed
- commented-out includes such as `//// !include(...)` as warnings
- ordering warnings when numeric prefixes are absent or duplicated

Report format:

```text
Phase: Technical pass
Findings:
- <path>:<line> <message>
Proposed Changes:
- <only when edits are needed>
Validation:
- <checker command and result>
```

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
2. Read `main.sdf`, `.env`, and every text file under `slides/*.sdf`.
3. Preserve `main.sdf` as scaffold-only.
4. Identify existing classes, tone, assets, timing comments, and raw HTML.

When adding slides:

- Use existing deck examples and classes first.
- Use the patterns in `references/patterns.md` only when local examples do not fit.
- Same-section slides may be appended to the relevant existing `.sdf` file.
- New chapters or major sections may get a new numbered file.
- Do not renumber by default.
- If renumbering would improve clarity, propose it first with concrete consequences.
- For new chapter checkpoints, propose `//@ < TBD`; do not invent real timing.

When editing speaker notes:

- Treat slide body and `/* ... */` notes as separate regions.
- If the user asks for notes, change only notes unless slide content is also requested.
- Every slide keeps a notes block, even full-image and meme slides.

When using images:

- Prefer existing local assets.
- Use SliDesk `!image(path, alt, width, height, styles, caption)` for simple images.
- Use raw HTML only when layout requires it.
- Avoid text-only meme placeholders unless the user asks for a draft placeholder.

After edits:

1. Run the checker.
2. Report changed files, validation command, errors, warnings, and anything not verified.

## New Deck Workflow

When creating a deck:

1. Require an explicit deck directory name.
2. Create `<repo-root>/<deck-name>/` from `slidesk_template`.
3. Keep the scaffold intact, including `common -> ../common`.
4. Set `.env` `TITLE=<deck-name>`.
5. Keep `main.sdf` scaffold-only.
6. Write all slides in `slides/*.sdf`.
7. Run the checker.

## File Ordering

- Preserve existing numeric prefix style.
- Prefer gaps such as `25-new-topic.sdf` between `20-foo.sdf` and `30-bar.sdf`.
- When appending before `99-speaker.sdf`, use the next available prefix below `99`.
- Sorting order matters more than numeric aesthetics because it controls presentation order.
- Never silently renumber. Explain consequences before changing existing filenames.

## References

- Read `references/patterns.md` when adding slide patterns or when local examples are insufficient.
- Official SliDesk syntax reference: https://slidesk.github.io/slidesk-doc/docs/syntax/intro/
- Images: https://slidesk.github.io/slidesk-doc/docs/syntax/Image/
- Includes: https://slidesk.github.io/slidesk-doc/docs/syntax/Include/
- Templates: https://slidesk.github.io/slidesk-doc/docs/templates/intro/
