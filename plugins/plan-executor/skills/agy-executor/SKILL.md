---
name: agy-executor
description: 'Delegate an approved plan to a gemini-4-hydrogen-low swarm worker, then verify and commit on the parent model. Trigger on plan approval (/plan, Proceed).'
---

# Antigravity Plan Executor

Execute approved plans on `gemini-4-hydrogen-low` (`LOW`) while keeping review, unsandboxed gates, and commits on the parent (`HIGH`) model.

## 1. Prepare Handoff

Collect before spawning:
- **Plan target**: absolute path to the approved plan artifact (or exact approved steps).
- **Workspace root**: absolute active repository path (pass absolute paths in `brief` so file tools succeed on turn 1).
- **Codebase context**: qualified symbols, paths, call chains, and `check_index_coverage` findings already gathered (workers start fresh and may lack MCP tools).

- **Completion criterion:** Plan path, workspace root, and codebase pointers ready.

## 2. Dispatch `@executor`

Spawn one worker pinned to `gemini-4-hydrogen-low` (`swarm{action:"add"}` directly), then **end the turn** so the worker's `@coordinator` post wakes you (`post_message`, `read_board`, and `swarm_wait` unlock next turn):

```text
swarm{
  action: "add",
  name: "executor",
  model: "gemini-4-hydrogen-low",
  workspace: "inherit",
  brief: "..."
}
```

Include these 5 rules in `brief`:
1. Read the approved plan artifact verbatim before editing.
2. Follow workspace `GEMINI.md` / `AGENTS.md` (code style, phase commits, doc updates).
3. Use absolute paths in `read_file`/`edit_file`/`write_file`; apply at most 2 `edit_file` calls per file per turn (sequence further edits or use `write_file`).
4. Stay sandboxed: iterate on targeted single-file tests first (`WaitMsBeforeAsync: 10000`), end your turn while waiting on background tasks instead of calling `swarm_wait`, run the full sandbox-safe suite once before reporting, and list unsandboxed commands (DB setup, `chmod +x`, `git commit`) for `@coordinator` instead of passing `BypassSandbox: true`.
5. Post `@coordinator` when done with: modified files, symbols, commands run, exact test results, remaining unsandboxed steps, and factual coding friction/gotchas or codebase issues noticed (or `None`; update if bounced for fixes).

- **Completion criterion:** `executor` spawned on `gemini-4-hydrogen-low` and turn ended to await `#2`.

## 3. Verify, Bounce Fixes to `LOW`, and Land

Keep `@executor` parked (`waiting` costs 0 tokens) until every gate and commit passes:

1. Inspect `git status` and `git diff` against every item in the approved plan.
2. Run unsandboxed prerequisites and full gates (`BypassSandbox: true` if required).
3. If tests fail or non-trivial fixes (>5 lines) are needed, send exact failures back to `@executor` in **two separate steps** (confirm `{"status":"posted","seq":N}` before waiting — never batch `post_message` and `swarm_wait`):
   - Step A: `post_message{text: "@executor ..."}` (parameter is `text`).
   - Step B (next step): `swarm_wait{since: N}`.
4. Repeat 1–3 until green, then run final `git commit` steps on `HIGH`.
5. Kill the worker (`swarm{action:"kill", name:"executor"}`), write `walkthrough.md` (if in `/plan` mode), load and run `agy-retrospective` (if available) to filter worker friction + coordinator/gate friction, and report verified results.

- **Completion criterion:** All gates pass after the final edit, planned commits are landed, `@executor` is killed, `walkthrough.md` is written if in `/plan`, and `agy-retrospective` (if available) has run.

## Recovery

- **Server restart** (`stopped` in `swarm{action:"status"}`): revive with `post_message{text:"@executor resume"}`.
- **Worker quota exhausted**: switch model in-place via `swarm{action:"model", name:"executor", model:"gemini-4-hydrogen-medium"}` (or `"gemini-3.8-flash-low"`).
