# smart-slidesk Modernization Design

Date: 2026-05-10

Status: Draft for user review

Supersedes: `docs/superpowers/specs/2026-05-08-smart-slidesk-design.md`

## Goal

Update the `smart-slidesk` skill for the current SliDesk standard:

- `slidesk.toml` replaces `.env`.
- `main.md` replaces `main.sdf`.
- ordered `slides/*.md` files replace ordered `slides/*.sdf` files.
- `main.md` remains scaffold-only and includes slide files.
- legacy `.sdf` decks are not migrated or structurally checked automatically.

The skill should remain useful for creating, reviewing, editing, validating, and
maintaining SliDesk decks, but its default and maintained standard is now
Markdown plus `slidesk.toml`.

## Sources Checked

- Current public SliDesk documentation base: `https://slidesk.github.io/slidesk/`
- Upstream docs source:
  - `docs/configuration/index.md`
  - `docs/syntax/index.md`
  - `docs/syntax/include.md`
  - `docs/syntax/image.md`
  - `docs/syntax/speaker-notes.md`
  - `docs/syntax/comment.md`
  - `docs/usage/index.md`
  - `docs/usage/how-to.md`
  - `docs/usage/commands/create.md`
  - `docs/usage/commands/present.md`
  - `docs/usage/commands/save.md`

Relevant confirmed documentation facts:

- SliDesk uses Markdown syntax for slides.
- `## ` defines a new slide.
- A talk needs `main.sdf` or `main.md`; this skill standardizes on `main.md`.
- SliDesk uses `slidesk.toml` for presentation configuration.
- `slidesk.toml` values are readable as `++KEY++`.
- Directory includes default to `sdf`, so Markdown directory includes must specify
  `md`: `!include(slides, md)`.
- Speaker notes use `/*` and `*/`.
- SliDesk line comments use `////`.
- Images use `!image(path, alternative text, width, height, additional styles, addCaption)`.

## Approach

Three approaches were considered:

1. Current standard only: reject all legacy decks.
2. Dual standard: fully validate and maintain both Markdown and SDF formats.
3. Current standard with legacy warning: validate Markdown-standard decks, warn on
   legacy decks, and allow legacy authoring as-is without deterministic legacy checks.

Chosen approach: option 3.

This keeps the skill aligned with current SliDesk while avoiding a forced migration
or a second maintained validator for `.sdf` decks. When legacy decks are encountered,
the skill should mention that they are outdated and offer conversion only if the user
asks. It must not migrate silently.

## Current Standard

A current-standard deck uses:

```text
<deck>/
  slidesk.toml
  main.md
  slides/
    10-cover.md
  assets/
```

Required configuration:

```toml
[slidesk]
TITLE = "<deck title>"
WIDTH = 1920
```

Required `main.md` default:

```md
!include(slides, md)
```

Required initial slide for new decks:

```md
## .[cover]

# <Deck Title>

/*
To Be Defined
*/
```

## Skill Behavior

The skill keeps the existing phases:

- `Technical pass`
- `Narrative pass`
- `Authoring pass`

Every technical pass reports a format line before findings:

```text
Format: current Markdown standard
```

or:

```text
Format: legacy SDF deck; current standard is slidesk.toml + main.md + slides/*.md
```

Mixed requests such as "review and fix this deck" still run the technical pass first,
then the narrative pass, and wait before editorial edits unless the user explicitly
authorized edits.

The skill defaults to French for new decks or unclear language, preserves the existing
deck language and voice, allows emoji and visual humor when useful, and preserves
timing comments and raw HTML unless explicitly instructed otherwise.

## New Deck Workflow

For a new deck, the skill should:

1. Require an explicit deck directory name.
2. Scaffold the new standard directly; do not depend on `slidesk_template`.
3. Create `slidesk.toml` with `[slidesk]`, `TITLE`, and `WIDTH = 1920`.
4. Create minimal scaffold-only `main.md` with `!include(slides, md)`.
5. Create `slides/10-cover.md` with a cover slide and `To Be Defined` notes.
6. Create `assets/`.
7. Run `check_deck.py`.

Do not create a `common -> ../common` symlink by default. Preserve existing shared
asset structures when editing an existing deck.

## Existing Deck Workflow

For an existing current-standard deck:

- Edit only `.md` slide files for new slide work.
- Use `slidesk.toml` for configuration.
- Never edit `.env`.
- Treat stray `.env`, `main.sdf`, or `slides/*.sdf` as deprecated artifacts.
- Error if `main.md` includes `sdf`; warn if unused `.sdf` files are present.

For an existing legacy deck:

- Mention that it uses legacy `.sdf` or `.env` conventions.
- Explain that the current standard is `slidesk.toml`, `main.md`, and `slides/*.md`.
- Offer conversion only as an optional path if the user asks.
- Do not run a migration phase.
- Do not migrate silently.
- Work on the deck as-is when the user wants that.
- Keep compact legacy authoring guidance in `SKILL.md`.
- Do not maintain legacy examples in `references/patterns.md`.
- Run the checker after edits only to surface the format warning; clearly state that
  legacy content was not structurally checked.

## Checker Design

The checker remains `scripts/check_deck.py` and remains dependency-free Python
standard library.

It should validate current-standard Markdown decks. It should not structurally
validate legacy `.sdf` decks.

Auto-detection:

- Current standard if `main.md`, `slidesk.toml`, or `slides/*.md` exists.
- Legacy if only `main.sdf`, `.env`, or `slides/*.sdf` exists.
- Mixed if current-standard and legacy artifacts coexist.

Human output includes:

```text
Format: <message>
Findings:
- ERROR: <path>:<line> <message>
- WARNING: <path>:<line> <message>
Summary: <n> error(s), <n> warning(s)
```

JSON output includes:

- `ok`: true when there are no errors.
- `format`
- `is_current_standard`
- `format_message`
- `include_mode`: `directory`, `individual`, `mixed`, or `missing`
- `errors`
- `warnings`
- `findings`

Legacy-only decks should exit success with warnings:

- format message says the deck is legacy.
- warning says legacy SDF content is not checked by the current-standard validator.
- warning says the user should ask for conversion to Markdown plus `slidesk.toml` if
  they want the deck brought current.

## Current-Standard Checks

Configuration:

- `slidesk.toml` is mandatory.
- `slidesk.toml` must be UTF-8 and valid TOML.
- `[slidesk]` table is mandatory.
- uppercase `TITLE` is mandatory and must be a string.
- `WIDTH`, `PORT`, `TRANSITION`, and `TELNET_PORT` should warn if not integers.
- `HTTPS` and `WATCH` should warn if not booleans.
- `DOMAIN`, `KEY`, `CERT`, and `PASSPHRASE` should warn if not strings.
- Unknown keys should not warn.

Entrypoint:

- `main.md` is mandatory.
- `main.md` must be UTF-8.
- `main.md` is scaffold-only.
- `main.md` must not contain `##` slide headings.
- `main.md` must not contain `# Deck Title` or other visible slide content.
- Allowed `main.md` content is includes, timing comments, SliDesk comments, and blank lines.
- The default include is `!include(slides, md)`.
- Individual Markdown includes are allowed with warnings.
- Mixed directory and individual includes should warn strongly.
- Missing all active Markdown includes is an error.
- Active includes should be checked for path existence.
- Includes outside `slides/` should warn as outside the house convention.
- Commented-out includes with `////` should warn.
- `!include(slides)` should error in current-standard decks because directory includes
  default to `sdf`; for Markdown decks the required directory include is explicit
  `!include(slides, md)`.

Slides:

- `slides/` is mandatory.
- Empty `slides/` is a warning.
- `slides/*.md` files are validated even if `main.md` has include errors.
- `.md` is the house extension; `.markdown` should warn as non-standard or unincluded.
- Every `slides/*.md` file is a slide source; `README.md`, `_draft.md`, and `.scratch.md`
  should not be silently ignored.
- Numeric prefixes are recommended but not mandatory.
- Missing numeric prefixes warn.
- Duplicate numeric prefixes warn.
- File sort order controls presentation order when using directory include.
- Include order controls presentation order when using individual includes.

Slide parsing:

- `##` is the only slide boundary.
- `#`, `###`, and deeper headings are content within the current slide.
- Class-only headings such as `## .[cover]` are valid slide boundaries.
- Initial content before the first `##` is allowed as the first slide, but if it has
  visible content, it must also have a speaker notes block.
- Ignore `##` inside fenced code blocks.
- Ignore speaker-note markers inside fenced code blocks.
- Every slide segment must have a `/* ... */` speaker notes block.
- New authored notes should use line-isolated markers.
- Existing inline `/* note */` blocks are accepted but should warn as style issues.
- `To Be Defined` is sufficient note content.
- Warn when visible content appears after `*/` before the next slide.

Timing comments:

- Preserve `//@` timing comments exactly.
- Allow timing comments in both `main.md` and slide files.
- Prefer chapter or section timing checkpoints in `main.md`.
- Lightly validate only obvious malformed timing markers, such as `//@` with no body.

Interpolation:

- Preserve `++KEY++` interpolation.
- Warn if an obvious literal interpolation key is not present under `[slidesk]`.
- Check interpolation references in both `main.md` and `slides/*.md`.
- Missing interpolation keys are warnings only because plugins or runtime values may
  provide them.

Images and media:

- Validate SliDesk `!image(...)` paths.
- Validate Markdown image syntax such as `![alt](assets/foo.png)`.
- Validate obvious raw HTML image tags such as `<img src="assets/foo.png">`.
- Resolve local asset paths relative to the deck directory.
- Do not validate ordinary Markdown links.
- Allow `http`, `https`, and `data` image URLs without network checking.
- Warn on dynamic/interpolated paths such as `++KEY++` or `$...`.
- Error on missing local referenced media.
- Only validate referenced assets; do not report unused assets.

Legacy and mixed artifacts:

- `.env` in an otherwise current deck is a warning.
- `main.sdf` in an otherwise current deck is a warning.
- `slides/*.sdf` in an otherwise current deck is a warning if not included.
- `slides/*.sdf` becomes an error if `main.md` includes `sdf`.
- Legacy-only decks are not structurally checked and exit success with warnings.

## Pattern Reference

`references/patterns.md` should be current-standard only:

- Markdown fences, not `sdf` fences.
- `slides/*.md` examples.
- `assets/...` image paths.
- `/* ... */` speaker notes.
- no maintained `.sdf` pattern snippets.

Agents should prefer existing deck examples and classes before using reference patterns.

## Documentation Links In Skill

`SKILL.md` should point to the current docs base:

```text
https://slidesk.github.io/slidesk/
```

If syntax or configuration behavior is uncertain, agents should check the current docs
or upstream docs source before inventing syntax.

Do not keep stale `slidesk-doc` links in the skill.

## Verification Plan

Implementation verification should use focused command checks rather than introducing
a full test framework unless a test harness appears in the repo.

Required focused checks:

- current Markdown deck succeeds.
- missing `slidesk.toml` errors.
- missing `main.md` errors.
- `main.md` with slide content errors.
- `main.md` with `!include(slides)` reports the explicit-MD include issue.
- empty `slides/` warns but remains `ok`.
- legacy-only deck exits success with warnings and says it was not structurally checked.
- mixed current plus stray legacy artifacts warns.
- current deck with `main.md` including `sdf` errors.
- missing local `!image(...)` errors.
- missing Markdown image errors.
- missing raw HTML `<img src>` errors.
- external image URLs pass without network checks.
- fenced code blocks do not create false slide or note findings.
- inline note blocks warn but pass.
- missing notes error.
- `++KEY++` with no TOML key warns.
- JSON output includes `format`, `is_current_standard`, `format_message`, and `include_mode`.

## Out Of Scope

- No conversion helper script in this update.
- No automatic migration.
- No forced migration gate.
- No legacy SDF structural validation.
- No unused asset detection.
- No ordinary Markdown link validation.
- No external network validation for images or links.
- No full SliDesk include resolver for content outside direct `slides/*.md`.

## Decision Log

1. Should the skill switch from `.sdf` and `.env` to Markdown plus `slidesk.toml`?
   Answer: Yes. The old convention is forgone for the new standard.

2. Should new decks use one Markdown file or multiple ordered Markdown files?
   Answer: Multiple ordered `.md` files, matching the old modular `.sdf` workflow.

3. Should new decks keep a scaffold-only `main.md` entrypoint?
   Answer: Yes. Use `main.md` as scaffold-only entrypoint.

4. Should `slidesk.toml` be mandatory?
   Answer: Yes. It replaces `.env` and is required for valid current-standard decks.

5. How should old `.env`, `main.sdf`, and `slides/*.sdf` artifacts be treated?
   Answer: They are old-standard artifacts. Later decisions refined this to warnings,
   not blocking migration checks.

6. Should there be an explicit migration workflow?
   Answer: Initially yes, but this was superseded by later decisions: no migration pass.

7. Should ordinary work auto-run migration for old decks?
   Answer: No. Never migrate silently.

8. If the user refuses migration, should legacy authoring still be allowed?
   Answer: Yes. Full legacy authoring is allowed.

9. Should the checker support both standard and legacy modes?
   Answer: Auto-detect mode, but later refined to current-standard checking only.

10. Should the checker require `--allow-legacy`?
    Answer: Initially considered yes, then superseded. No legacy gate or flag.

11. Should old-standard artifacts be checker warnings or prose only?
    Answer: Checker warnings.

12. Should authoring preserve an existing deck's current format?
    Answer: Yes. Preserve `.md` for current decks and `.sdf` for legacy decks.

13. Should every Markdown slide still require speaker notes?
    Answer: Yes.

14. Should the checker allow first-slide content before the first `##`?
    Answer: Yes, but it still needs notes if it has visible content.

15. Should `main.md` allow title or scaffold content before includes?
    Answer: It should be scaffold-only.

16. Should scaffold-only violations in `main.md` be hard errors?
    Answer: Yes.

17. Should `main.md` require `!include(slides, md)`?
    Answer: Yes for the default directory include, because directory includes default to `sdf`.

18. Should `slidesk.toml` validation enforce required keys?
    Answer: Yes. Require `[slidesk]` and `TITLE`.

19. What should default `slidesk.toml` contain?
    Answer: `[slidesk]`, `TITLE`, and `WIDTH = 1920`.

20. Should `++KEY++` interpolation remain supported?
    Answer: Yes.

21. Should interpolation be checked in both `main.md` and slides?
    Answer: Yes.

22. Should ordered slide files keep numeric-prefix conventions?
    Answer: Yes.

23. Should new-standard decks allow mixed `.md` and `.sdf` includes?
    Answer: No for normal authoring. Mixed format is a warning or error depending on impact.

24. Should `!image(...)` validation continue?
    Answer: Yes, updated for `slidesk.toml`.

25. Should Markdown image syntax be validated?
    Answer: Yes.

26. Should raw HTML `<img>` tags be validated?
    Answer: Yes, conservatively.

27. Should raw HTML preservation remain strict?
    Answer: Yes.

28. Should phases be kept or renamed?
    Answer: Keep `Technical pass`, `Narrative pass`, and `Authoring pass`.

29. Should mixed review-and-fix requests still do technical then narrative pass?
    Answer: Yes.

30. Should documentation links point to the new docs?
    Answer: Yes. Use `https://slidesk.github.io/slidesk/` and remove stale links.

31. Should new decks stop relying on `slidesk_template`?
    Answer: Yes. Scaffold the new standard directly.

32. Should new decks create `common -> ../common`?
    Answer: No by default.

33. Should new scaffolds create an initial slide?
    Answer: Yes. Create `slides/10-cover.md`.

34. What should the first slide look like?
    Answer: `## .[cover]`, `# <Deck Title>`, and `To Be Defined` notes.

35. Should pattern snippets switch to Markdown fences?
    Answer: Yes.

36. Should frontmatter mention legacy `.sdf` support?
    Answer: Yes, secondary to current Markdown-standard support.

37. Should the checker keep the name `check_deck.py`?
    Answer: Yes.

38. Should the checker expose `--format`?
    Answer: No. Use auto-detection.

39. In mixed decks with `main.md` and `main.sdf`, which format wins?
    Answer: Current standard wins; legacy artifacts are warnings unless included.

40. Should `.env` be a warning or error in a current deck?
    Answer: Warning.

41. Should missing `slidesk.toml` error?
    Answer: Yes.

42. Should missing `slides/` error?
    Answer: Yes.

43. Should empty `slides/` error or warn?
    Answer: Warn.

44. Should slide files without numeric prefixes warn?
    Answer: Yes.

45. Should duplicate numeric prefixes warn?
    Answer: Yes.

46. Should deprecated format findings appear before structural errors?
    Answer: Yes, through a format/status section.

47. Should human checker output include `Format:`?
    Answer: Yes.

48. Should JSON output include format metadata?
    Answer: Yes.

49. Should `ok` be true for legacy/deprecation warnings only?
    Answer: Yes. `ok` means no errors.

50. Should skill technical reports mirror the checker `Format:` line?
    Answer: Yes.

51. Should `##` remain the only slide boundary marker?
    Answer: Yes.

52. Should `##` inside fenced code blocks be ignored?
    Answer: Yes.

53. Should note markers inside fenced code blocks be ignored?
    Answer: Yes.

54. Should line-isolated note markers be required?
    Answer: New authored Markdown should use them; inline blocks pass with style warnings.

55. Should notes need non-placeholder content?
    Answer: No. `To Be Defined` is sufficient.

56. Should visible content after notes warn?
    Answer: Yes.

57. Should timing comments remain user-owned?
    Answer: Yes. Preserve exactly unless explicitly changed.

58. Should timing comments be allowed in `main.md` and slide files?
    Answer: Yes.

59. Should timing comment syntax be validated?
    Answer: Light validation only.

60. Should raw `!include(...)` paths be validated?
    Answer: Yes.

61. Should the checker recursively validate included files outside `slides/`?
    Answer: No. Check existence and warn outside convention.

62. Should `slides/*.md` validate even if `main.md` include is wrong?
    Answer: Yes.

63. Should `README.md` in `slides/` be allowed?
    Answer: Warn, because it may be included.

64. Should hidden or draft Markdown files in `slides/` be ignored?
    Answer: No.

65. Should authored slide files use `.md`, not `.markdown`?
    Answer: Yes.

66. Should the checker inspect unused assets?
    Answer: No. Only referenced assets.

67. Should local asset paths resolve relative to deck root or slide file?
    Answer: Deck root only.

68. Should external image URLs be allowed without network checking?
    Answer: Yes.

69. Should ordinary Markdown links be validated?
    Answer: No. Only media paths.

70. Should the skill default to French?
    Answer: Yes.

71. Should the default notes placeholder be `A definir` or `To Be Defined`?
    Answer: Keep `To Be Defined`.

72. Should emoji and visual humor remain allowed?
    Answer: Yes.

73. Should the checker stay standard-library only?
    Answer: Yes.

74. Should `slidesk.toml` keys be case-sensitive with uppercase `TITLE`?
    Answer: Yes.

75. Should unknown `[slidesk]` keys warn?
    Answer: No.

76. Should documented key types be checked?
    Answer: Lightly. Error for invalid `TITLE`; warn for surprising common key types.

77. Should all text deck files be UTF-8?
    Answer: Yes.

78. Should no `main.md` be an error even if `slidesk.toml` and slides exist?
    Answer: Yes.

79. Should a deck with valid `main.md`, `slidesk.toml`, and no slide files be `ok`?
    Answer: Yes, with warnings.

80. Should current deck plus unused `slides/*.sdf` be `ok`?
    Answer: Yes, with warnings, unless `sdf` is included.

81. Should current-standard authoring avoid `.sdf` files?
    Answer: Yes.

82. Should current-standard authoring ever edit `.env`?
    Answer: No.

83. Should the skill offer conversion when legacy files are detected?
    Answer: Yes, softly, and only if the user asks.

84. Should conversion be a helper script or guidance?
    Answer: Guidance only.

85. Should `check_deck.py` still validate legacy `.sdf` decks?
    Answer: No. Warn that they are not checked and suggest asking for conversion first.

86. Should legacy-only decks exit success with warnings?
    Answer: Yes.

87. Should the checker run after legacy edits?
    Answer: Yes, but validation must state legacy content was not structurally checked.

88. Should `SKILL.md` retain legacy authoring rules?
    Answer: Yes, compactly.

89. Should `.sdf` pattern snippets remain?
    Answer: No.

90. Should agents check current docs when uncertain?
    Answer: Yes.

91. Should this update create a new dated spec?
    Answer: Yes.

92. Should the old plan stay historical and a new plan be created later?
    Answer: Yes.

93. Should implementation add tests or focused command checks?
    Answer: Focused command checks.

94. Should `main.md` allow `# Deck Title`?
    Answer: No. Title lives in `slidesk.toml` and visible cover slide.

95. What exact content should new `main.md` use?
    Answer: `!include(slides, md)`.

96. Should individual slide file includes be allowed?
    Answer: Yes, with warnings; directory include remains the house default.

97. If using individual includes, what controls presentation order?
    Answer: Include order in `main.md`, not file sort order.

98. Should checker report include mode in JSON?
    Answer: Yes.

99. Should directory and individual includes be mixed?
    Answer: Warn strongly; avoid mixing.

100. Should individual includes without directory include still be `ok`?
     Answer: Yes, with warnings.

101. Should individual includes outside `slides/` be allowed?
     Answer: Yes with warning-level deviation; check existence but do not validate content
     outside direct `slides/*.md`.
