# smart-slidesk Design

Date: 2026-05-08

## Goal

Create a reusable Codex skill named `smart-slidesk` in `.agents/skills/smart-slidesk`.
The skill helps create, maintain, review, and amend SliDesk slide decks while preserving
the user's presentation structure and authorial intent.

The primary mode is deck authoring for an explicit deck. New deck creation is supported
by using the existing `slidesk_template` directory as the scaffold.

## Source Conventions

- `.agents/skills` is a symlink to the user's shared skills directory.
- Shell commands in this repo must use `rtk`.
- A deck name must be explicit and must match a direct child directory of the repo root.
- New decks are created at the repo root because they rely on root-relative shared files.
- New decks are created from `slidesk_template`.
- The user's generic SliDesk convention includes a root-level `common/` directory.
- New decks preserve the template's `common -> ../common` link.

## SliDesk Deck Rules

- `main.sdf` is scaffold-only.
- Never add slides to `main.sdf`.
- Slides always live in `<deck>/slides/*.sdf`.
- `main.sdf` should keep scaffold wiring such as styles and `!include(slides)`.
- Slide ordering follows alphabetical file order, so file names must preserve intended
  presentation order.
- Existing `//@` timing comments are user-owned knowledge and must be preserved exactly
  unless the user explicitly asks to change them.
- New chapter slides should propose a placeholder checkpoint: `//@ < TBD`.
- Every slide introduced by `##` must have a speaker notes block.
- Speaker notes use `/* ... */`.
- If no useful note content is known, use `To Be Defined`.
- `To Be Defined` is allowed anywhere inside speaker notes.
- Unicode, French accents, and emoji are allowed and encouraged in deck content.

## Language And Style

- Preserve the existing deck language and voice when editing.
- Default to French for new decks or unclear language context.
- Apply "show, don't tell": slides should be visual, sparse, and presenter-friendly.
- Put nuance, transitions, caveats, examples, and delivery guidance in speaker notes.
- Humor, memes, and visual relief are welcome when they serve the talk.
- Avoid text-only meme slides unless the user specifically asks for a draft placeholder.

## Explicit Phases

The skill must require agents to state the active phase before acting.

### Technical Pass

Purpose: structural and deterministic validation.

Checks include:

- deck structure exists: `<deck>/main.sdf`, `<deck>/.env`, `<deck>/slides/`
- `main.sdf` contains no slide headings
- `main.sdf` keeps `!include(slides)`
- slide files are under `<deck>/slides/*.sdf`
- each slide boundary is a `##` heading, including class-only forms such as
  `## .[chapter]` and `## .[full-image]`
- visible slide titles or subtitles may follow as `# ...`
- every `##` slide has a following `/* ... */` speaker notes block before the next
  `##` or end of file
- local `!image(...)` paths exist
- external URLs are allowed
- balanced speaker-note comment blocks
- no accidental `////` comment on active includes
- ordering conventions are preserved
- `To Be Defined` notes are allowed
- existing `//@` timing comments are preserved

Technical findings must be concise, deterministic, and cite file paths.

### Narrative Pass

Purpose: literary and editorial review, not technical validation.

Review:

- story arc and chapter flow
- rhythm and density
- tension, release, and visual breathing room
- transitions between sections
- slide economy and "show, don't tell"
- speaker-note usefulness
- audience fit, vocabulary, humor, and meme opportunities
- timing comments as user-owned checkpoints, not as arbitrary editable text

The narrative pass produces findings and proposed changes first. It must not edit the
deck until the user confirms.

### Authoring Pass

Purpose: create, add, amend, or reorganize slides after the deck and requested change are
explicit.

Rules:

- read the whole text deck before editing; slide deck size is not a concern
- do not load binary/media assets into context unless needed
- never edit `main.sdf` to add slides
- preserve raw HTML exactly unless the user explicitly confirms a change to that block
- treat slide body and speaker notes as separate editable regions
- when asked to edit notes, change only `/* ... */` blocks unless slide content is also requested
- prefer existing local assets under `<deck>/assets` or `common/assets`
- generate or download images only with explicit user direction
- use SliDesk `!image(...)` for simple images
- use raw HTML only when layout requires it and after confirmation when modifying existing HTML
- after edits, run the checker script

Mixed requests such as "review this deck and fix issues" should run Technical pass first,
Narrative pass second, then wait for confirmation before Authoring pass edits unless the
user explicitly authorized immediate technical fixes.

## New Deck Workflow

When the user asks for a new deck:

1. Require an explicit deck directory name.
2. Create `<repo-root>/<deck-name>/` from `slidesk_template`.
3. Keep scaffold structure intact.
4. Set `.env` `TITLE=<deck-name>`.
5. Keep `main.sdf` scaffold-only.
6. Use `slides/*.sdf` for all slides.
7. Run the checker script after creation.

## Slide File Ordering

- Choose file names automatically when useful.
- Preserve existing numeric prefix style.
- Prefer gaps such as `25-new-topic.sdf` between `20-foo.sdf` and `30-bar.sdf`.
- When appending before `99-speaker.sdf`, use the next available prefix below `99`.
- Do not renumber by default.
- If renumbering would improve clarity, propose it with concrete consequences before doing it.
- Sorting order matters more than numeric aesthetics because it controls presentation order.

## V1 Slide Patterns

The v1 skill includes a small pattern reference, not a full template library.

Patterns:

- chapter
- content
- full-image
- meme or full-image-with-caption
- quote
- two-column
- speaker
- closing or resources

Agents should prefer existing deck examples and classes first, then use these patterns.
Detailed snippets belong in `references/patterns.md`, not in the main `SKILL.md`.

## Checker Script

The skill includes `scripts/check_deck.py`.

Requirements:

- accept a deck directory path
- default to concise human-readable output
- support `--json` for machine-readable automation
- exit non-zero on errors
- distinguish warnings from errors
- error on missing local `!image(...)` paths
- allow external image URLs
- allow `To Be Defined` anywhere in speaker notes
- account for `## .[chapter]`, `## .[full-image]`, and `#` subtitles after `##`
- report file paths and actionable messages

After any Authoring pass, agents must run:

```bash
rtk python3 .agents/skills/smart-slidesk/scripts/check_deck.py <deck>
```

If the skill is installed elsewhere, agents should use the equivalent installed script path.

## Skill Structure

```text
.agents/skills/smart-slidesk/
  SKILL.md
  agents/openai.yaml
  references/patterns.md
  scripts/check_deck.py
```

`SKILL.md` should stay procedural and compact. Pattern snippets go in
`references/patterns.md`. Deterministic validation goes in `scripts/check_deck.py`.

## Reporting Format

Use concise, deterministic reports:

```text
Phase: <Technical pass | Narrative pass | Authoring pass>
Findings:
- ...
Proposed Changes:
- ...
Validation:
- ...
```

Technical findings cite paths. Narrative findings cite slide titles, sections, and paths
when useful, but remain explicitly editorial.

## Future Iterations

- A richer template library may become a later iteration or a separate skill.
- Additional SliDesk-specific automation can be added after the first checker script proves useful.
- Visual asset generation can be expanded, but remains explicit opt-in.

## Success Criteria

- Future agents reliably avoid adding slides to `main.sdf`.
- Future agents preserve timing comments and raw HTML unless explicitly authorized to change them.
- Existing decks can be technically checked without starting a SliDesk server.
- New decks are created from `slidesk_template` at the repo root.
- Authoring produces sparse visual slides with speaker notes for every slide.
- Technical and narrative passes remain visibly distinct.
