---
name: strict-collab-workflow
description: >
  Enforce a strict collaboration workflow for future sessions: inspect minimally before coding,
  present a visible Goal/Diagnostic/Plan/Validation structure, keep plans to 1-5 steps, use rtk for shell
  commands, avoid broad reads of large or central files without approval, and finish each execution
  slice with explicit proof and next-step handoff.
---

Use this workflow as the default operating mode unless the user explicitly overrides it.

## Goals

- maximize execution reliability
- reduce token waste
- keep iterations atomic
- make continuation easy when a session stops

## Default Structure

Before any non-trivial code change, respond with:

```md
Goal
- ...

Diagnostic
- ...

Plan
1. ...

Validation
- Waiting for validation / go-ahead
```

The plan must contain 1 to 5 steps.

## Diagnostic Rules

- inspect the minimum useful context first
- do not change code during diagnostic
- prefer targeted inspection over broad reading
- when reading partially, state the file and the slice inspected

Treat a file as large when:

- it is over 400 lines, or
- it is structurally central or sensitive even below that threshold

Examples of structurally central or sensitive files:

- root configuration
- `AGENTS.md`
- a pivot component or service
- generated files
- files mixing several responsibilities

For large or structurally central files:

- prefer targeted reads first
- ask before broad reading or large dumps

## Validation Rules

Wait for user validation before implementation by default.

Proceed without revalidation only when all of the following are true:

- request is explicitly executable
- target is clear
- change is low-risk and local
- verification path is clear
- operating rules are already fully established by context or `AGENTS.md`

If any doubt remains, ask instead of inferring.

Once the operating frame is 100% clear, do not keep asking the same confirmation repeatedly.

## Execution Rules

- keep work to one coherent slice
- avoid bundling unrelated edits
- stop after the agreed slice
- do not silently expand scope

## Token Rules

- every shell command must use `rtk`
- prefer `rtk rg`, bounded `rtk sed -n`, and other targeted commands
- avoid long command output unless it has real signal
- avoid reading an entire large file when a narrow query is enough
- summarize instead of dumping raw output

## Proof Rules

After each execution slice, report:

```md
Result
- ...

Proof
- Tests run: ...
- Bootstrap/prerequisites: ...
- Not verified: ...

Next
- Next action: ...
- Later options: ...
```

When no clear automated verification exists:

- say so explicitly
- ask before running non-obvious checks
- do not overclaim validation
- if a verification path is clearly documented in context or `AGENTS.md`, use it without redundant re-asking

## Validation

Use `references/prompt-harness.md` to verify the workflow in a fresh session on a real project.
