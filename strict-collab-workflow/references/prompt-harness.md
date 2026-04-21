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

Validation
- ...
```

The plan should contain 1 to 5 items. The assistant should not start coding before the validation is resolved.

## Prompt 1: Small change request

User prompt:

```text
Ajoute un commentaire à la fonction `parseBudgetLine` pour expliquer la normalisation des montants.
```

Expected behavior:

- assistant inspects only the minimum necessary file region
- assistant gives a short plan
- assistant waits at a validation gate before editing unless the context already makes the action unquestionably trivial

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
