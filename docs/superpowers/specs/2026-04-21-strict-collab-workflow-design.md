# Strict Collab Workflow Design

## Goal

Define a default collaboration workflow for future Codex sessions that improves execution reliability first, reduces token waste second, and leaves a clean next-step handoff when a session stops midstream.

## Problems To Solve

- Codex starts coding too early before enough context is gathered.
- Planning is often too detailed for the scope of the task.
- Iterations are not consistently atomic, which makes review and continuation harder.
- Command and file-reading habits can waste tokens.
- Verification is often under-specified when a project does not already expose an obvious test path.

## Default Workflow

Every non-trivial task follows this visible structure before code changes:

```md
But
- ...

Diagnostic
- ...

Plan
1. ...
2. ...

Gate
- Attente de validation / go
```

### Phase 0: But

Codex briefly restates:

- the requested outcome
- the relevant constraint
- the primary execution risk

### Phase 1: Diagnostic

Codex gathers the minimum context required before acting.

Rules:

- no code changes during diagnostic
- no broad dump of large files without explicit user approval
- prefer targeted inspection over exploratory reading
- when reading partially, state the file and the slice inspected

Definition of a large file:

- small: 200 lines or fewer
- medium: 201 to 400 lines
- large: more than 400 lines
- very large: more than 800 lines

Size is not the only criterion. A file should also be treated as large when it is structurally central or sensitive even below 400 lines, for example:

- root configuration
- `AGENTS.md`
- a pivot component or service
- generated files
- files mixing several responsibilities

For large or structurally central files, Codex must prefer targeted reads first and ask before broad reading.

### Phase 2: Plan

Codex proposes an actionable plan with 1 to 5 steps.

Rules:

- no oversized implementation plan for a small task
- steps must be operational, not abstract
- plan should reflect the next atomic slice, not the whole universe of possible work

### Phase 3: Gate

Codex waits for user validation before implementation by default.

Codex may proceed without revalidation only when all of the following are true:

- the request is explicitly executable
- the target is clear
- the change is low-risk and local
- the verification path is clear
- the working rules are already fully established by context or `AGENTS.md`

If any doubt remains, Codex asks instead of inferring.

### Phase 4: Atomic Execution

Once validated, Codex performs one coherent slice of work.

Rules:

- keep scope narrow
- avoid bundling unrelated edits
- stop after the agreed slice rather than silently rolling into the next one

### Phase 5: Explicit Proof

After each execution slice, Codex reports:

- what changed
- which automated checks exist
- which exact checks were run
- which bootstrap or prerequisites were required
- what remains unverified
- the single next action
- one or two possible follow-up tracks if the session ends here

Default behavior when no clear automated verification exists:

- do not improvise broad verification without approval
- ask before running non-obvious checks
- if a verification path is clearly documented in context or `AGENTS.md`, use it without redundant re-asking

## Token Discipline

The workflow must reduce token usage without reducing rigor.

Rules:

- all shell commands must use `rtk`
- prefer targeted commands such as `rtk rg` and bounded `rtk sed -n`
- avoid long command output unless it provides real signal
- avoid reading entire large files when a narrow query is enough
- prefer concise summaries over raw dumps

## User-Facing Response Format

The workflow is always explicit rather than implicit.

During execution:

```md
Action en cours
- ...

Constat
- ...
```

After execution:

```md
Résultat
- ...

Preuve
- Tests lancés: ...
- Bootstrap/prérequis: ...
- Non vérifié: ...

Suite
- Prochaine action: ...
- Pistes ensuite: ...
```

## Decision Rules

Codex must stop and ask before proceeding when:

- context is insufficient
- a large or structurally central file would need broad reading
- the change likely spans multiple files in a non-trivial way
- the command or test cost is unclear
- multiple reasonable implementation options exist

Codex should avoid repeated confirmation requests once the operating frame is fully clear.

## Scope

This workflow is intended to apply to all future sessions by default, not only to a single project.

The skill should therefore be:

- written as a general collaboration skill
- referenced from the user's global instruction surface
- still invocable directly as a fallback

## Validation Strategy

The skill should be validated on a real project with a small prompt harness.

Recommended harness:

- 3 to 5 prompts
- include one simple task
- include one ambiguous task
- include one case where Codex would normally start coding too early
- compare observed behavior against expected gate, plan size, and proof format

## Non-Goals

- encoding a personal writing style beyond what the workflow requires
- forcing long plans for small tasks
- mandating automated verification where the project does not define one
- replacing project-specific instructions from `AGENTS.md`

## Open Integration Work

Implementation still needs to define:

- final skill name
- exact global integration point
- whether extra reference files are needed for examples or test prompts
