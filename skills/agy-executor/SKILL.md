---
name: agy-executor
description: 'Delegate execution of an approved implementation plan to a Gemini 4 Hydrogen (Low) swarm worker, then verify and commit on the parent model. Use whenever a plan is approved (e.g., after /plan or clicking Proceed).'
---

# Antigravity Plan Executor (`HIGH` Plan -> `Hydrogen Low` Execute)

Delegate implementation of an approved plan to a `gemini-4-hydrogen-low` (`Gemini 4 Hydrogen (Low)`) `swarm` worker, keep it alive through full verification so `LOW` fixes any failures, then commit and clean up on the parent (`HIGH`) model.

> **Why `swarm` instead of `invoke_subagent`:** Custom `agents/*.md` definitions and `invoke_subagent` only accept generic `modelTier` values (`inherit`, `flash_lite`, `flash`, `pro`) and reject specific model IDs such as `gemini-4-hydrogen-low`. `swarm{action:"add", model:"gemini-4-hydrogen-low"}` pins the exact model.

## 1. Prepare Handoff Context

Gather before dispatching:
- **Plan target**: absolute path to the approved plan artifact (or exact approved steps if inline).
- **Workspace root**: active workspace directory.
- **Codebase context**: qualified symbols, paths, call chains, and `check_index_coverage` findings already gathered during planning (workers start fresh and may lack MCP tools).

## 2. Dispatch Execution (`gemini-4-hydrogen-low`)

Call `swarm{action:"add"}` directly (skip `swarm{action:"models"}`) and **end your turn** so the worker's `@coordinator` post wakes you (`post_message`, `read_board`, and `swarm_wait` unlock on the next turn):

```text
swarm{
  action: "add",
  name: "executor",
  model: "gemini-4-hydrogen-low",
  workspace: "inherit",
  brief: "..."
}
```

Do not load `native_swarm` (no narrator/monitor needed for single-worker execution) unless the plan explicitly requires parallel workers.

The `brief` must instruct `@executor` to:
1. Read the approved plan artifact verbatim before editing.
2. Follow workspace `GEMINI.md` / `AGENTS.md` rules (code style, phase commits, doc updates).
3. Avoid batching 3+ `edit_file` calls targeting the same file in one turn (apply sequentially or use `write_file` when rewriting multiple sections).
4. Stay inside the sandbox: run sandbox-safe checks (`ruff`, `vitest`, unit tests) and **never** attempt `BypassSandbox: true` (background workers cannot prompt for sandbox approval); list any `BypassSandbox: true` commands needed (DB setup, `chmod +x`, `git commit`) for `@coordinator`.
5. Post `@coordinator` when done with: exact modified file paths, symbols, commands run, test output, and remaining `BypassSandbox` steps (or blockers).

## 3. Board Messaging Guardrails (Deadlock Prevention)

- `post_message` parameter is **`text`** (not `Message`): `post_message{text: "@executor ..."}`.
- **Never call `swarm_wait` in the same tool batch as `post_message`.** If `post_message` fails validation while `swarm_wait` runs, both agents deadlock asleep. Always:
  1. Call `post_message{text: "..."}` alone.
  2. Confirm `{"status":"posted", "seq":N}` in the tool result.
  3. Call `swarm_wait{since: N}` on the **next** step.

## 4. Verify, Bounce Fixes to `LOW`, and Finalize (`HIGH`)

`waiting` workers cost zero tokens — **keep `@executor` alive until all checks pass.**

1. Inspect `git status` and `git diff` against every item in the approved plan.
2. Run any `BypassSandbox: true` prerequisites/gates (e.g., DB reset/migrations, full integration/release suite) that `@executor` could not run in sandbox.
3. **If tests fail or non-trivial fixes (>5 lines) are needed**: post the exact failure output and required fixes back to `@executor` via `post_message{text:"@executor ..."}` so **`LOW` implements the fixes**, rather than rewriting files on `HIGH`. Repeat until clean.
4. Run final `git commit` steps (if `BypassSandbox: true` is needed for `.git`).
5. **Only after all checks and commits pass**, kill the worker: `swarm{action:"kill", name:"executor"}`.
6. Write `walkthrough.md` (if in `/plan` mode) and report verified results to the user.

## 5. Recovery

- **Server restart** (`stopped` in `swarm{action:"status"}`): post `@executor resume` via `post_message{text:"@executor resume"}` to revive it.
- **Worker quota exhausted**: switch model without losing state via `swarm{action:"model", name:"executor", model:"gemini-4-hydrogen-medium"}` (or `"gemini-3.8-flash-low"`).

## Optional Always-On Rule (`AGENTS.md` / `GEMINI.md`)

To enforce automatic delegation on every plan approval without needing to invoke the skill manually, add this to your global or project `AGENTS.md` / `GEMINI.md`:

```markdown
## Plan Execution Delegation

When the user approves a plan (e.g., `/plan` approval or `Proceed`), the planning/coordinator agent must not edit implementation files or run execution commands inline unless the user explicitly asks to execute inline. Load the `agy-executor` skill to delegate implementation to `gemini-4-hydrogen-low`, then review and verify the result. (An executor worker receiving a delegated plan brief executes it directly.)
```
