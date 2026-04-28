---
name: disciplined-git
description: "Use for all Git workflows in a repository: status, diff, branch, worktree, staging, committing, fixing commits, rebasing, pushing, cleanup, conflicts, and handoff."
---

# Disciplined Git

## Principle

Git is shared project state. Inspect before acting, explain complex situations before changing state, keep history useful, and protect user or teammate work by default.

Use `rtk git ...` for commands.

## Start Every Git Workflow

- Inspect the current state with `rtk git status --short` and, when relevant, `rtk git branch --show-current`.
- For non-trivial work, propose a short-lived worktree before editing. Always ask before creating it.
- Prefer trunk-based development: branches and worktrees should live only as long as needed.
- Do not push, rebase, amend, reset, stash, clean, delete branches/worktrees, or discard files without explicit approval.

## Complex Git Diagnosis Gate

When the Git state is complex, stop before changing Git state and write:

```md
Git Diagnosis
- Current branch/worktree:
- Mainline/upstream relationship:
- Dirty/staged files:
- Conflict type:
- Higher-level conflict:
- Likely owner/intent of each side:
- Proposed strategy:
- Commands I will run:
- What I will not do without approval:
```

Complex means any merge/rebase/cherry-pick conflict, dirty worktree with user changes, multiple commits that may need splitting or fixup, branch behind/diverged from mainline, unclear ownership, generated files, lockfiles, migrations, schemas, destructive operation, or history rewrite.

If the user corrects the diagnosis, update it before continuing.

## Worktrees And Branches

- Prefer worktrees for non-trivial tasks, parallel work, risky edits, reviews, or anything that may disturb current user state.
- Ask before creating a worktree and state the intended branch name, base branch, path, and cleanup plan.
- Keep worktrees short-lived. After merge, handoff, or abandonment, propose cleanup.
- Avoid branch churn for tiny local changes when the user already has a clear working context.

## Diffs And Dirty State

- Before editing, distinguish user changes from task changes.
- Use targeted diffs: `rtk git diff -- <path>` and `rtk git diff --cached -- <path>`.
- Never overwrite, revert, or absorb unrelated user changes.
- If unrelated changes are present, work around them or ask.

## Atomic Commits

- Prefer small commits that each explain one coherent change.
- Before committing, inspect `rtk git status --short`, targeted unstaged diffs, and `rtk git diff --cached`.
- Stage explicit paths only: `rtk git add <path>`. Avoid `git add .` unless the user explicitly requests broad staging.
- When changes naturally split, propose an eager commit split instead of making one large mixed commit.
- Unless told otherwise, use Conventional Commits for commit messages, because release tooling such as `release-please` may rely on it.
- Commit only after meaningful validation or after clearly reporting what was not verified.

## Fixups And History Repair

- If follow-up corrections belong in a previous committed change, propose `rtk git commit --fixup=<commit>`.
- Prefer fixup commits over unrelated "follow-up" commits when the correction should become part of earlier history.
- When fixup commits accumulate, or before final integration, propose interactive rebase with autosquash.
- Always ask before running interactive rebase, amend, or any history rewrite.

## Conflict Policy

Do not treat conflicts as text puzzles first. Diagnose the higher-level conflict:

- Behind mainline: combine both sides, preserving mainline and current work unless incompatible.
- Current work intentionally supersedes mainline, such as a refactor or replacement: prioritize current work while preserving independent fixes or behavior.
- Ownership or intent unclear: stop and ask before choosing a side.
- Unrelated nearby edits: combine both with minimal semantic change.
- Generated files, lockfiles, migrations, schemas: use the project canonical procedure if known; otherwise ask.

Avoid blind `ours` or `theirs`. After resolving, report what was preserved from each side and run the narrowest meaningful validation.

## Push And Handoff

- Never push unless requested.
- Before push, report branch, target remote/ref, commits included, and whether history was rewritten.
- After any commit or complex Git operation, report:
  - status summary
  - files staged or changed
  - commit hash when applicable
  - validation run
  - uncommitted or unrelated changes left alone
  - cleanup proposed for short-lived branches/worktrees
