---
name: agy-executor
description: 'Use when a /plan artifact is approved (Proceed or [Approved] plan.md) in a non-Orchestrator session before editing files or spawning workers.'
---

# Antigravity Plan Executor

Select orchestrator and execution mode/model via `ask_question` on `/plan` approval, defer when native `planexecute` (`exit_plan_mode` / `[plan review]`) is active, execute inline or via `/swarm`, and review/land diffs on coordinator.

> **Foundational Gate Principle**: Executing edits, picking default models, or dispatching workers before `ask_question` completes violates this skill.

## When NOT to Use
- Native `planexecute` active (`exit_plan_mode` or `[plan review]`).
- User approval specifies `inline`, target model, or `swarm`.

## 1. Select Models and Wait

1. Call `swarm{action:"models", all:true}` to check dropdown models and live quota (`quota_remaining > 0%`). Never pick unlisted IDs.
2. If `low`/`medium` models are exhausted, omit empty worker options and offer `Inline` or cross-family alternatives.
3. Classify plan files and call `ask_question` **once**:
   - **Single-stream plan** (1 file or coupled edits) — **2 questions**:
     - **Q1 — Orchestrator**: `(Recommended) Keep current model`, plus available `high`/`xhigh` models.
     - **Q2 — Execution**: `Inline (current session)` + available `low`/`medium` models. Recommend `Inline` for 1-file plans; recommend top `low`/`medium` `@executor` for 2+ files.
   - **Multi-workstream plan** (2+ disjoint file groups) — **3 questions**:
     - **Q1 — Orchestrator**: `(Recommended) Keep current model`, plus available `high`/`xhigh` models.
     - **Q2 — Topology**: `(Recommended) Parallel Swarm (<N> workers on workspace:"share")`, `Single @executor`, `Inline (current session)`.
     - **Q3 — Worker Model**: available `low`/`medium` models (ignored if Q2 = `Inline`).

## 2. Execute

### Inline
Do not call `swarm`. If Q1 changed model, prompt user to switch via `/model`. Implement, verify, commit directly.

### Single `@executor`
1. Set `swarm{action:"title", title:"<plan title>"}`.
2. Pass `fork:"coordinator"` (`workspace:"inherit"`) **only** when target files were read directly and `0` broad search dumps occurred; otherwise omit `fork`.
3. Spawn: `swarm{action:"add", name:"executor", model:"<worker-model>", workspace:"inherit", brief:"..."}`. Never spawn `narrator` or `monitor`.
4. Switch coordinator model if Q1 changed: `swarm{action:"model", model:"<orchestrator-model>"}`.
5. On Turn-2 self-switch wakeup, **do not re-brief**; call `swarm_wait{since: <brief_seq>}`.

### Parallel `/swarm` Fan-out
1. Set `swarm{action:"title", title:"<plan title>"}`.
2. Omit `fork`. Spawn disjoint workers on `workspace:"share"`: `swarm{action:"add", name:"exec", tasks:[...], model:"<worker-model>", workspace:"share", brief:"..."}` (or separate `exec-<area>`). Never spawn `narrator` or `monitor`.
3. Switch coordinator model if Q1 changed; wait without re-briefing.

### Required `brief` Contract
Every worker `brief` must follow this structure:
```json
{
  "action": "add",
  "name": "executor",
  "model": "gemini-3.8-flash-medium",
  "workspace": "inherit",
  "brief": "Plan: /path/to/plan.md\nScope: edit only <files>\nVerify & Commit: run <tests>; commit locally with git commit -m '...' (BypassSandbox: true only for .git); do not push\nReport: post @coordinator [done] with modified files, verification output, commit SHAs"
}
```

## 3. Review, Merge, and Land

1. **Single `@executor`**: inspect `git status`, `git diff`, and `git log` against plan requirements.
2. **Parallel Swarm**: **land (merge/cherry-pick) all worker commits into coordinator workspace BEFORE calling `swarm{action:"kill"}`** (`kill` deletes `share` workspaces).
3. Kill workers individually: `tasks:[...]` spawns `exec-1..exec-N`; call `swarm{action:"kill", name:"exec-1"}`, etc.
4. Gaps: post and wait in two separate steps:
   - Step A: `post_message{text: "@<worker> fix <issue>"}`
   - Step B: `swarm_wait{since: N}`

## 4. Recovery & Diagnostics

- **Stopped worker**: revive via `post_message{text:"@<worker> resume"}`.
- **Quota exhausted**: ensure worker is `waiting`, then switch via `swarm{action:"model", name:"<worker>", model:"..."}` across quota families.

## Common Mistakes

| Mistake | Correction |
|---|---|
| Editing immediately on approval | Call `swarm{action:"models", all:true}` and `ask_question` first. |
| Calling `swarm{action:"kill"}` before merging | Land commits first; `kill` deletes `workspace:"share"`. |
| Killing `exec` after `tasks:[...]` | Kill each member by numbered name (`exec-1..exec-N`). |
| Re-briefing on self-switch wakeup | Do not re-send tasks. Call `swarm_wait{since: brief_seq}`. |
| Switching to same model family on quota error | Switch across provider/model families. |

## Red Flags - STOP

- "User said hurry/no chatter, so I will skip asking questions."
- "Small 3-line tweak, so I will edit directly."
- "I will kill workers now and pull commits later."
- "Re-briefing worker because coordinator model switched."
