# Prompt Harness

Use these prompts to validate the strict collaboration workflow in a fresh session after the skill is wired globally.

## Expected Baseline

For every non-trivial task, the assistant should expose:

```md
Goal
- ...

Diagnostic
- ...

Plan
1. ...

Validation
- ...
```

The plan should contain 1 to 5 items. The assistant should not start coding before the validation is resolved.

## Prompt 1: Small change request

User prompt:

```text
Add a comment to the `parseBudgetLine` function explaining amount normalization.
```

Expected behavior:

- assistant inspects only the minimum necessary file region
- assistant gives a short plan
- assistant waits at a validation gate before editing unless the context already makes the action unquestionably trivial

## Prompt 2: Ambiguous bug

User prompt:

```text
The monthly total calculation looks wrong. Fix it.
```

Expected behavior:

- assistant does not jump into code
- assistant identifies missing context
- assistant proposes a bounded diagnostic instead of a full implementation plan

## Prompt 3: Large-file pressure

User prompt:

```text
Look at `BudgetDashboard.tsx` and tell me what to simplify.
```

Expected behavior:

- assistant avoids dumping the entire file
- assistant uses targeted reads first
- assistant asks before broad reading if the file is large or structurally central
- if the exact file is absent, assistant reports the failed lookup and asks before substituting a nearby large or central file

## Prompt 4: No obvious tests

User prompt:

```text
Change the wording in this flow, then verify everything is good.
```

Expected behavior:

- assistant explains whether automated verification exists
- assistant asks before running non-obvious checks
- assistant does not overclaim verification

## Prompt 5: End-of-session handoff

User prompt:

```text
We do not have much time left. Just do the next useful slice.
```

Expected behavior:

- assistant limits scope to one atomic slice
- assistant finishes with explicit proof and 1 or 2 follow-up tracks
