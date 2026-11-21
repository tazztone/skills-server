---
name: agy-executor
description: 'Use when a /plan artifact is approved (Proceed or [Approved] plan.md) to select execution models before running.'
---

# Antigravity Plan Executor

Ask the user for **orchestrator** (`high`/`xhigh` or keep current) and **executor** (`low`/`medium` or `Inline`) models in one `ask_question` call, delegate implementation, verification, and commits to `@executor` when a worker model is chosen, and review the final diff on the orchestrator.

## 1. Select Models and Wait

Unless the approval message already names a target model or `inline`:

1. Call `swarm{action:"models"}` first to inspect live non-exhausted models (`quota_remaining > 0%`).
2. Call `ask_question` once with two questions (`questions` array) and wait before any edits or `swarm` dispatch:
   - **Q1 — Orchestrator**: `(Recommended) Keep current model`, followed by non-exhausted `high` / `xhigh` models (include flagship tierless models such as Opus in this bucket).
   - **Q2 — Executor**: non-exhausted `low` / `medium` models (include fast/mid tierless models such as Flash/Sonnet in this bucket), plus `Inline (run on orchestrator)`.
   - Never pick default models, edit files, or spawn `@executor` before the user answers.

## 2. Execute

- **If `Inline`**:
  - If a different Orchestrator model was chosen, attempt `swarm{action:"model", model:"<orchestrator-model>"}`; if `swarm` rejects because no swarm is active, ask the user to switch model manually or confirm running on the current model.
  - Implement, verify, and commit the approved plan directly on the orchestrator (do not start a swarm).
- **If an Executor model was chosen** (or approval named a single target model, keeping current model as orchestrator):
  1. Gather the absolute plan path, workspace root, and relevant codebase context (qualified symbols, file paths, call chains, and `check_index_coverage` findings if indexed — workers start fresh without parent context).
  2. Spawn one worker pinned to the chosen executor model:

```text
swarm{
  action: "add",
  name: "executor",
  model: "<executor-model>",
  workspace: "inherit",
  brief: "..."
}
```

  3. If a different Orchestrator model was chosen, switch the coordinator in-place (`swarm{action:"model", model:"<orchestrator-model>"}`).
  4. **End the turn** (`post_message`, `read_board`, and `swarm_wait` unlock on the next turn).

Include these 4 rules in `brief`:
1. Read the approved plan artifact verbatim before editing; use absolute paths.
2. Follow workspace `GEMINI.md` / `AGENTS.md` (code style, phase commits, doc updates).
3. Run all verification/tests and phase `git commit`s directly (`BypassSandbox: true` only when required, e.g., `.git` commits).
4. Post `@coordinator [done]` when finished with: modified files, exact test/verification output, and commit SHAs.

## 3. Review and Land

1. Inspect `git status`, `git diff`, and `git log` against every requirement in the approved plan.
2. If review finds gaps or failures, bounce exact issues back to `@executor` in **two separate steps** (confirm `{"status":"posted","seq":N}` before waiting — never batch `post_message` and `swarm_wait`):
   - Step A: `post_message{text: "@executor ..."}`
   - Step B (next step): `swarm_wait{since: N}`
3. Once verified, kill the worker (`swarm{action:"kill", name:"executor"}`) and report verified results.

## Recovery

- **Server restart** (`stopped` in `swarm{action:"status"}`): revive via `post_message{text:"@executor resume"}`.
- **Quota exhausted**: check `swarm{action:"models"}` and switch the worker via `swarm{action:"model", name:"executor", model:"..."}` (or ask the user via `ask_question` if unsure).
