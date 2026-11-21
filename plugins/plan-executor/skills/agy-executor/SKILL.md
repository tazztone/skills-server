---
name: agy-executor
description: 'Use when a /plan artifact is approved (Proceed or [Approved] plan.md) to select an execution model and run inline or via swarm.'
---

# Antigravity Plan Executor

Ask the user which model should execute an approved `/plan` (or run inline), delegate implementation, verification, and commits to `@executor` when a swarm model is chosen, and review the final diff on the coordinator.

## 1. Select Model and Wait

Unless the approval message already names a target model or `inline`:

1. Call `swarm{action:"models"}` first to inspect live non-exhausted models and remaining quota.
2. Call `ask_question` presenting available models plus `Inline (current model)` and wait for the answer before any edits or `swarm` dispatch.
   - Never pick a default model, edit files, or spawn `@executor` before the user answers.

## 2. Execute

- **If `Inline`**: implement, verify, and commit the approved plan directly on the current model (do not start a swarm).
- **If a model was chosen**:
  1. Gather the absolute plan path, workspace root, and relevant codebase context (qualified symbols, file paths, call chains, and `check_index_coverage` findings if indexed — workers start fresh without parent context).
  2. Spawn one worker pinned to the chosen model, then **end the turn** (`post_message`, `read_board`, and `swarm_wait` unlock on the next turn):

```text
swarm{
  action: "add",
  name: "executor",
  model: "<chosen-model>",
  workspace: "inherit",
  brief: "..."
}
```

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
