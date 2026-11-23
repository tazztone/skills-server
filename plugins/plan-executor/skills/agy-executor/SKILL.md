---
name: agy-executor
description: 'Use when a /plan artifact is approved (Proceed or [Approved] plan.md) in a non-Orchestrator session before editing files or spawning workers.'
---

# Antigravity Plan Executor

> **Gate Rule**: Editing files, picking default models, or spawning workers before `ask_question` completes violates this skill.

## 1. Select Models and Wait

1. Call `swarm{action:"models", all:true}` and keep models with `quota_remaining > 0%`. Never use unlisted IDs.
2. Ask **once** via `ask_question`:
   - **Q1 — Orchestrator**: `(Recommended) Keep current model`, plus available `high`/`xhigh` models.
   - **Q2 — Execution**:
     - *1 stream / coupled edits*: `Inline (current session)` + available `low`/`medium` models (recommend `Inline` for `1 file`; top `low`/`medium` `@executor` for `2+ files`).
     - *2+ disjoint file groups*: `(Recommended) Parallel Swarm (workspace:"share")`, `Single @executor`, `Inline (current session)`.
   - **Q3 — Worker Model** *(2+ disjoint groups only)*: available `low`/`medium` models (ignored if Q2 = `Inline`).

## 2. Execute

- **Inline**: Do not call `swarm`. If Q1 changed model, tell user to switch via `/model`. Implement, verify, commit directly.
- **Single `@executor`**: Spawn `swarm{action:"add", name:"executor", model:"<worker-model>", workspace:"inherit", brief:...}`. Pass `fork:"coordinator"` only if target files were read directly with `0` broad search dumps; otherwise omit.
- **Parallel `/swarm`**: Omit `fork`; spawn disjoint `workspace:"share"` workers (`tasks:[...]` on `name:"exec"`, or `exec-<area>`).
- **Coordinator switch**: If Q1 changed model, call `swarm{action:"model", model:"<orchestrator-model>"}` after `add`. On Turn-2 self-wakeup, call `swarm_wait{since: <brief_seq>}` — do **not** re-brief.

Required `brief` slots:
```text
Plan: /abs/path/to/plan.md
Scope: edit only <files/slice>
Verify & commit: <test command>; follow workspace commit rules
Report: @coordinator [done] with modified files, check output, commit SHAs[, share path]
```

## 3. Review, Land, and Kill

1. **Single `@executor`**: inspect `git status`, `git diff`, and `git log`.
2. **Parallel `/swarm`**: merge/cherry-pick all worker commits into coordinator workspace and run cross-slice checks **before** `swarm{action:"kill"}` (kills delete `share` workspaces).
3. **Gaps**: `post_message` → confirm `seq` → `swarm_wait{since: N}` on next step (never batch).
4. **Cleanup**: kill workers individually (`exec-1..exec-N` when `tasks:[...]` was used).

## Gotchas

- `swarm{action:"models"}` without `all:true` omits non-suggested models.
- Same-family models share quota buckets (switching `hydrogen-medium` → `hydrogen-low` stays exhausted; switch across families).
