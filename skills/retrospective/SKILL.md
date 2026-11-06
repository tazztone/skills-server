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
2. Write the response to `<parent-artifact-dir>/scratch/retrospective.md` using `write_file` (`Path` and `Content` only, omitting `ArtifactMetadata`), where `<parent-artifact-dir>` is the resolved absolute path to `<appDataDir>/brain/<conversation-id>`.

- **Completion criterion:** Every session roadblock and candidate improvement is printed to the user and written to `<parent-artifact-dir>/scratch/retrospective.md`.

## 2. Ground, Plan, and Critique (Isolated Subagent)

Dispatch a fresh-context subagent (`TypeName="self"`, `Role="Grounded Planner"`) with `<parent-artifact-dir>` interpolated as a literal absolute path so planning runs with a 0-token baseline. Wait for the subagent notification before proceeding.

```python
invoke_subagent(
    Role="Grounded Planner",
    TypeName="self",
    Prompt="""
Read `<parent-artifact-dir>/scratch/retrospective.md`.
Confine all file operations to `<parent-artifact-dir>/scratch/followup_plan.md` (`Path` and `Content`/`Target`/`Replacement` only); leave repository files untouched.

## Pass 1: Triage, Ground, and Draft Plan
Answer and execute:
> "verify/ground the previous findings in `<parent-artifact-dir>/scratch/retrospective.md`.
> how to best adress them? write a plan."

1. Inspect `git status`, `git diff`, source files, docs, and tests to audit every finding against actual workspace state.
2. Triage each finding as **grounded** (backed by exact `file:line` or command output) or **discarded** (false positive, already resolved, or out-of-scope noise).
3. Draft a phased implementation plan (`1 phase = 1 commit`, including doc/spec updates and verification commands per phase) for grounded findings only, and write it to `<parent-artifact-dir>/scratch/followup_plan.md` using `write_file`.

- **Completion criterion:** Every finding in `retrospective.md` is classified as grounded or discarded, and grounded tasks are written to `<parent-artifact-dir>/scratch/followup_plan.md`.

## Pass 2: Critique and Refine Plan
Answer and execute:
> "verify/ground, critique and refine the plan
> what would u change or improve still? are you happy with the plan? update it as you see fit."

1. Challenge protocol fallbacks, failure modes, edge cases, state invariants, and test coverage in `<parent-artifact-dir>/scratch/followup_plan.md` against project docs and code.
2. Apply refinements in place on `<parent-artifact-dir>/scratch/followup_plan.md` using `edit_file`.
3. Return the triage summary (grounded vs. discarded items) and Pass 2 critique refinements to the parent agent.

- **Completion criterion:** `<parent-artifact-dir>/scratch/followup_plan.md` is refined in place via `edit_file` and the triage + critique summary is returned to the parent agent.
"""
)
```

- **Completion criterion:** Subagent completes both passes, updates `<parent-artifact-dir>/scratch/followup_plan.md`, and returns the triage and critique summary.

## 3. Promote Artifact and Handoff (Main Thread)

1. Read `<parent-artifact-dir>/scratch/followup_plan.md` and promote it to `<parent-artifact-dir>/followup_plan.md` via `write_file` with `ArtifactMetadata` (`UserFacing: true`, `RequestFeedback: true`, `Summary: "<concise summary of grounded follow-up phases>"`).
2. Present the [`followup_plan.md`](file://<parent-artifact-dir>/followup_plan.md) link, grounded vs. discarded triage highlights, and Pass 2 refinements to the user. Wait for explicit approval before executing Phase 1.

- **Completion criterion:** `<parent-artifact-dir>/followup_plan.md` is created in the main thread with `RequestFeedback: true` and presented to the user with no repository files modified.
