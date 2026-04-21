# Strict Collab Workflow Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a reusable skill that enforces a strict, low-token collaboration workflow across future sessions, then activate it from the global Codex instruction surface.

**Architecture:** The implementation has three parts: a prompt-harness reference that acts as the behavioral acceptance test, a new skill folder containing `SKILL.md` and `agents/openai.yaml`, and a global `AGENTS.md` include that activates the skill by default. Validation is manual but explicit: inspect generated files, verify the global include, then run the harness prompts in a fresh session against a real project.

**Tech Stack:** Markdown skills, YAML metadata, Codex `AGENTS.md` includes, `rtk` shell commands, git

---

### Task 1: Write the Validation Harness First

**Files:**
- Create: `strict-collab-workflow/references/prompt-harness.md`

- [ ] **Step 1: Create the reference directory**

Run: `rtk mkdir -p strict-collab-workflow/references`
Expected: command exits successfully with no output

- [ ] **Step 2: Write the prompt harness document**

Create `strict-collab-workflow/references/prompt-harness.md` with:

````md
# Prompt Harness

Use these prompts to validate the strict collaboration workflow in a fresh session after the skill is wired globally.

## Expected Baseline

For every non-trivial task, the assistant should expose:

```md
But
- ...

Diagnostic
- ...

Plan
1. ...

Gate
- ...
```

The plan should contain 1 to 5 items. The assistant should not start coding before the gate is resolved.

## Prompt 1: Small change request

User prompt:

```text
Ajoute un commentaire à la fonction `parseBudgetLine` pour expliquer la normalisation des montants.
```

Expected behavior:

- assistant inspects only the minimum necessary file region
- assistant gives a short plan
- assistant waits at gate before editing unless the context already makes the action unquestionably trivial

## Prompt 2: Ambiguous bug

User prompt:

```text
Le calcul des totaux mensuels a l'air faux. Corrige.
```

Expected behavior:

- assistant does not jump into code
- assistant identifies missing context
- assistant proposes a bounded diagnostic instead of a full implementation plan

## Prompt 3: Large-file pressure

User prompt:

```text
Regarde `BudgetDashboard.tsx` et dis-moi quoi simplifier.
```

Expected behavior:

- assistant avoids dumping the entire file
- assistant uses targeted reads first
- assistant asks before broad reading if the file is large or structurally central

## Prompt 4: No obvious tests

User prompt:

```text
Change le wording de ce flux puis vérifie que tout est bon.
```

Expected behavior:

- assistant explains whether automated verification exists
- assistant asks before running non-obvious checks
- assistant does not overclaim verification

## Prompt 5: End-of-session handoff

User prompt:

```text
On n'a plus beaucoup de temps. Fais juste la prochaine tranche utile.
```

Expected behavior:

- assistant limits scope to one atomic slice
- assistant finishes with explicit proof and 1 or 2 follow-up tracks
```
````

- [ ] **Step 3: Inspect the new file**

Run: `rtk sed -n '1,220p' strict-collab-workflow/references/prompt-harness.md`
Expected: file shows five prompts, expected behavior bullets, and the visible `But / Diagnostic / Plan / Gate` structure

- [ ] **Step 4: Commit the harness**

Run:

```bash
rtk git add strict-collab-workflow/references/prompt-harness.md
rtk git commit -m "test: add strict workflow prompt harness"
```

Expected: commit created with the new harness reference

### Task 2: Add Skill Metadata

**Files:**
- Create: `strict-collab-workflow/agents/openai.yaml`

- [ ] **Step 1: Create the agents directory**

Run: `rtk mkdir -p strict-collab-workflow/agents`
Expected: command exits successfully with no output

- [ ] **Step 2: Write the skill metadata**

Create `strict-collab-workflow/agents/openai.yaml` with:

```yaml
interface:
  display_name: "Strict Collab Workflow"
  short_description: "Use a gated, low-token workflow before coding and make proof explicit after each slice."
  default_prompt: "Use $strict-collab-workflow to enforce a visible But/Diagnostic/Plan/Gate workflow, delay coding until validation, use rtk for shell commands, and report explicit proof."
```

- [ ] **Step 3: Inspect the metadata file**

Run: `rtk sed -n '1,120p' strict-collab-workflow/agents/openai.yaml`
Expected: YAML contains `display_name`, `short_description`, and `default_prompt`

- [ ] **Step 4: Commit the metadata**

Run:

```bash
rtk git add strict-collab-workflow/agents/openai.yaml
rtk git commit -m "feat: add strict workflow skill metadata"
```

Expected: commit created with the metadata file

### Task 3: Write the Skill Body

**Files:**
- Create: `strict-collab-workflow/SKILL.md`
- Reference: `strict-collab-workflow/references/prompt-harness.md`

- [ ] **Step 1: Write the skill file**

Create `strict-collab-workflow/SKILL.md` with:

````md
---
name: strict-collab-workflow
description: >
  Enforce a strict collaboration workflow for future sessions: inspect minimally before coding,
  present a visible But/Diagnostic/Plan/Gate structure, keep plans to 1-5 steps, use rtk for shell
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
But
- ...

Diagnostic
- ...

Plan
1. ...

Gate
- Attente de validation / go
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

## Gate Rules

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

When no clear automated verification exists:

- say so explicitly
- ask before running non-obvious checks
- do not overclaim validation
- if a verification path is clearly documented in context or `AGENTS.md`, use it without redundant re-asking

## Validation

Use `references/prompt-harness.md` to verify the workflow in a fresh session on a real project.
```
````

- [ ] **Step 2: Inspect the skill body**

Run: `rtk sed -n '1,260p' strict-collab-workflow/SKILL.md`
Expected: frontmatter is present, the visible `But / Diagnostic / Plan / Gate` structure is included, and the proof section mentions tests, bootstrap, and non-verified work

- [ ] **Step 3: Cross-check the harness reference**

Run: `rtk rg -n "Prompt 1|Prompt 5|But|Gate" strict-collab-workflow`
Expected: matches are found in both `SKILL.md` and `references/prompt-harness.md`

- [ ] **Step 4: Commit the skill body**

Run:

```bash
rtk git add strict-collab-workflow/SKILL.md strict-collab-workflow/references/prompt-harness.md
rtk git commit -m "feat: add strict workflow skill"
```

Expected: commit created with the core skill definition

### Task 4: Wire the Skill into Global AGENTS

**Files:**
- Modify: `/home/stephane/.codex/AGENTS.md`

- [ ] **Step 1: Confirm the current global file content**

Run: `rtk sed -n '1,40p' /home/stephane/.codex/AGENTS.md`
Expected: output includes `@RTK.md`

- [ ] **Step 2: Update the global AGENTS file**

Change `/home/stephane/.codex/AGENTS.md` to:

```md
@RTK.md
@/home/stephane/Dropbox/obsidian/skills/strict-collab-workflow/SKILL.md
```

- [ ] **Step 3: Re-read the updated file**

Run: `rtk sed -n '1,40p' /home/stephane/.codex/AGENTS.md`
Expected: output shows both `@RTK.md` and the absolute include for `strict-collab-workflow/SKILL.md`

- [ ] **Step 4: Commit the repository-side files**

Run:

```bash
rtk git add strict-collab-workflow/SKILL.md strict-collab-workflow/agents/openai.yaml strict-collab-workflow/references/prompt-harness.md
rtk git commit -m "feat: prepare strict workflow skill for global activation"
```

Expected: repository commit created; note that `/home/stephane/.codex/AGENTS.md` lives outside this repo and is not part of this commit

### Task 5: Validate Behavior and Capture Results

**Files:**
- Create: `strict-collab-workflow/references/validation-notes.md`

- [ ] **Step 1: Create the validation notes file**

Create `strict-collab-workflow/references/validation-notes.md` with:

```md
# Validation Notes

Record the outcome of each prompt from `prompt-harness.md`.

For each prompt, capture:

- whether the assistant used the visible But/Diagnostic/Plan/Gate structure
- plan length
- whether coding started before the gate
- whether large-file behavior was handled correctly
- whether proof was explicit
- follow-up adjustments needed
```

- [ ] **Step 2: Inspect the validation file**

Run: `rtk sed -n '1,120p' strict-collab-workflow/references/validation-notes.md`
Expected: file contains the five review bullets for manual validation

- [ ] **Step 3: Run the harness manually in a fresh session**

Manual procedure:

1. Open a fresh Codex session from a real project that already contains code.
2. Confirm the global skill is active.
3. Replay each prompt from `strict-collab-workflow/references/prompt-harness.md`.
4. Record observations in `strict-collab-workflow/references/validation-notes.md`.

Expected: the assistant consistently delays coding, keeps plans short, uses `rtk`, avoids broad reads of large files, and ends slices with explicit proof

- [ ] **Step 4: Commit the validation artifacts**

Run:

```bash
rtk git add strict-collab-workflow/references/validation-notes.md
rtk git commit -m "test: add strict workflow validation notes scaffold"
```

Expected: commit created with the validation-notes scaffold

## Self-Review

Spec coverage check:

- default visible workflow is covered in Task 3
- large-file rules are covered in Task 3 and exercised by Task 1 prompt 3
- explicit proof behavior is covered in Task 3 and exercised by Task 1 prompt 4 and 5
- global activation is covered in Task 4
- validation on a real project is covered in Task 5

Placeholder scan:

- no `TODO`, `TBD`, or missing file paths remain
- each created file includes concrete content
- validation commands and manual validation procedure are explicit

Type consistency:

- skill name is consistently `strict-collab-workflow`
- all references point to the same folder and file names

## Notes

- `/home/stephane/.codex/AGENTS.md` is structurally central; implementation should keep reads targeted and avoid broad dumps.
- If Codex does not resolve absolute `@/path/to/file` includes as expected, add a tiny bridging file under `/home/stephane/.codex/` and include that file instead. Validate this before assuming global activation is complete.
