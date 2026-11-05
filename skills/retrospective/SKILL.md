---
name: retrospective
description: Summarize session roadblocks and improvements, then dispatch an isolated subagent to ground, draft, and critique a follow-up plan.
disable-model-invocation: true
---

# Retrospective

Reflect on session friction while full context is hot, then hand off to a 0-token subagent to ground findings against the codebase, draft a follow-up plan, and self-critique it.

## 1. Extract Retrospective (Main Thread)

Answer this exact prompt using current session memory:

> "saw any other issues or room for improvement during this session? what should we work on still ?
> summarize roadblocks/friction encountered during this session."

1. Output the response directly to the user (`### Roadblocks & Friction Encountered` and `### Room for Improvement & Recommended Next Tasks`).
2. Save the response to `<appDataDir>/brain/<conversation-id>/scratch/retrospective.md`.

- **Completion criterion:** Every session roadblock and candidate improvement is printed to the user and written to `<appDataDir>/brain/<conversation-id>/scratch/retrospective.md`.

## 2. Ground, Plan, and Critique (Isolated Subagent)

Dispatch a fresh-context subagent (`TypeName="self"`, `Role="Grounded Planner"`) so planning runs with a 0-token baseline instead of session history. Wait for the subagent notification before proceeding.

```python
invoke_subagent(
    Role="Grounded Planner",
    TypeName="self",
    Prompt="""
Read `<appDataDir>/brain/<conversation-id>/scratch/retrospective.md`.

## Pass 1: Ground and Draft Plan
Answer and execute:
> "verify/ground the previous findings:
> <contents of retrospective.md>
> how to best adress them? write a plan."

1. Inspect `git status`, `git diff`, source files, docs, and tests to verify every finding against actual workspace state.
2. Create an implementation plan artifact (`<appDataDir>/brain/<conversation-id>/followup_plan.md`) with `ArtifactMetadata` (`UserFacing: true`, `RequestFeedback: true`).
3. Do not edit repository files.

- **Completion criterion:** Every claim in `retrospective.md` is verified against the codebase and captured in `followup_plan.md`.

## Pass 2: Critique and Refine Plan
Answer and execute:
> "verify/ground, critique and refine the plan
> what would u change or improve still? are you happy with the plan? update it as you see fit."

1. Challenge protocol fallbacks, failure modes, edge cases, state invariants, and test coverage against project docs and code.
2. Edit `followup_plan.md` in place with the refinements.
3. Return the artifact path, grounded decisions, and critique refinements made in Pass 2.

- **Completion criterion:** `followup_plan.md` is updated with every edge-case refinement and returned to the parent agent.
"""
)
```

- **Completion criterion:** Subagent completes both passes and returns the refined `followup_plan.md` artifact path and summary.

## 3. Handoff

Present the finalized plan artifact link, grounded highlights, and critique refinements to the user. Wait for explicit confirmation before executing Phase 1.

- **Completion criterion:** Finalized plan artifact and summary presented to the user with no repository files modified.
