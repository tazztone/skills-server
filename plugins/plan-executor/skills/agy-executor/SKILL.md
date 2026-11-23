---
name: agy-executor
description: 'Use when a /plan artifact is approved (Proceed or [Approved] plan.md) in a non-Orchestrator session to select models/topology (inline, single @executor, or parallel workspace:"share" swarm) before running.'
---

# Antigravity Plan Executor

Select **orchestrator** and **execution mode/model** in one `ask_question` call on `/plan` approval, skip redundant delegation when native `planexecute` (`exit_plan_mode` / `[plan review]`) is active, execute inline or via `/swarm` (`@executor` or parallel `workspace:"share"` fan-out), and review/land the final diff on the orchestrator.

## 1. Select Models and Wait

Skip this skill if native `planexecute` (`exit_plan_mode` tool or `[plan review]`) is active, or if the approval message already names `inline`, a target model, or explicit `swarm` parameters.

1. Call `swarm{action:"models", all:true}` first to inspect **all** served dropdown models and live quota (`quota_remaining > 0%` or `quota_note` indicating AI credits). Never rely on `suggested` alone; never pick internal/`-tiered` IDs outside the `swarm` catalog.
2. Classify the approved plan and call `ask_question` **once** (never pick defaults, edit files, or spawn workers before the user answers):
   - **Single-stream plan** (sequential or tightly coupled edits) — **2 questions**:
     - **Q1 — Orchestrator**: `(Recommended) Keep current model`, followed by non-exhausted `high`/`xhigh`/flagship models (e.g., `gemini-4-hydrogen-high`, `gemini-4-hydrogen-xhigh`, `gemini-4-carbon-*`, `gemini-4-neon-*`, `claude-opus-5-5-*`).
     - **Q2 — Execution**: `Inline (current session)` + non-exhausted `low`/`medium`/fast models for single `@executor` (e.g., `gemini-4-hydrogen-low`, `gemini-4-hydrogen-medium`, `claude-sonnet-5-5-*`, `gemini-3.8-flash-*`). Put `(Recommended)` on `Inline` for tiny/1-file plans, or on the top `low`/`medium` `@executor` for multi-file/heavy-edit plans.
   - **Multi-workstream plan** (2+ genuinely disjoint file groups or subsystems) — **3 questions**:
     - **Q1 — Orchestrator**: `(Recommended) Keep current model`, followed by non-exhausted `high`/`xhigh`/flagship models.
     - **Q2 — Topology**: `(Recommended) Parallel Swarm (<N> workers on workspace:"share")`, `Single @executor`, `Inline (current session)`.
     - **Q3 — Worker Model**: non-exhausted `low`/`medium`/fast models (ignored if Q2 = `Inline`).

## 2. Execute

### Inline
- Do **not** start a swarm or call `swarm{action:"model"}` (`swarm{action:"model"}` rejects when no swarm is active).
- If Q1 picked a different orchestrator model, instruct the user to switch via `/model` (or `Orchestrator` mode) and confirm, or proceed on the current model.
- Implement, verify, and commit directly.

### Single `@executor`
1. Optionally set `swarm{action:"title", title:"<short plan title>"}`.
2. Pick context mode:
   - Pass `fork:"coordinator"` with `workspace:"inherit"` **only** on short/focused planning sessions that already hold the target files in context.
   - Omit `fork` (start fresh) after heavy research sessions to avoid bloating worker input tokens; include exact plan path, workspace root, qualified symbols, file paths, call chains, and `check_index_coverage` findings in `brief`.
3. Spawn one worker (`name:"executor"`, `model:"<worker-model>"`, `workspace:"inherit"`). Never spawn `narrator` or `monitor` workers.
4. If Q1 changed the coordinator model, switch in-place **after** `add` via `swarm{action:"model", model:"<orchestrator-model>"}`.
5. **End the turn** (`post_message`, `read_board`, and `swarm_wait` unlock on Turn 2).
   - **Self-switch wakeup**: switching the coordinator's own model on Turn 1 immediately triggers Turn 2 with `"You switched to the model ... Continue coordinating"`. On that wakeup turn, **do not re-brief** — call `swarm_wait{since: <brief_seq>}` using the `#N` returned by `add`.

### Parallel `/swarm` Fan-out
1. Set `swarm{action:"title", title:"<short plan title>"}` (echo `open_board` if returned).
2. **Always omit `fork`** so workers start fresh with narrow, disjoint file ownership.
3. Spawn disjoint workers on `workspace:"share"` pinned to `<worker-model>`: use `swarm{action:"add", name:"exec", tasks:[...], model:"<worker-model>", workspace:"share", brief:"..."}` when one shared brief applies, or separate `exec-<area>` workers when briefs differ. Never spawn `narrator` or `monitor`.
4. If Q1 changed the coordinator model, switch via `swarm{action:"model", model:"<orchestrator-model>"}` after `add`, then handle the Turn-2 self-wakeup by calling `swarm_wait{since: <brief_seq>}` without re-briefing.

### Required `brief` Rules
Include in every worker `brief`:
1. Read the approved plan artifact verbatim before editing; use absolute paths (and touch only your assigned slice in parallel runs).
2. Follow workspace `AGENTS.md` / `GEMINI.md` (code style, phase commits, doc updates).
3. Run slice/plan verification and commit locally (`BypassSandbox: true` only when required, e.g., `.git` commits); never push to a remote unless asked.
4. Post `@coordinator [done]` with: modified files, exact verification output, commit SHAs, and workspace path if using `workspace:"share"`.

## 3. Review, Merge, and Land

1. **Single `@executor` (`workspace:"inherit"`)**: inspect `git status`, `git diff`, and `git log` against every requirement in the approved plan.
2. **Parallel Swarm (`workspace:"share"`)**: **land (merge or cherry-pick) all worker commits into the coordinator workspace BEFORE calling `swarm{action:"kill"}`** (`kill` permanently deletes `share` and `branch` workspaces). Optionally spawn a `verifier` (`workspace:"inherit"`, coordinator/`high` model) or run cross-slice review/tests directly on the coordinator.
3. If review finds gaps or failures, bounce exact issues to the owning worker in **two separate steps** (confirm `{"status":"posted","seq":N}` before waiting — never batch `post_message` and `swarm_wait`):
   - Step A: `post_message{text: "@<worker> ..."}`
   - Step B (next step): `swarm_wait{since: N}`
4. Once verified and landed, kill all workers (`swarm{action:"kill", name:"..."}`) and report verified results.

## 4. Recovery & Diagnostics

- **Server restart** (`stopped` in `swarm{action:"status"}`): revive via `post_message{text:"@<worker> resume"}`.
- **Quota exhausted**:
  1. Check `swarm{action:"status"}` — `swarm{action:"model"}` **requires worker state `waiting`** (revive `stopped` first; wait if `working`).
  2. Run `swarm{action:"models", all:true}` and switch via `swarm{action:"model", name:"<worker>", model:"..."}` to a model in a **different quota bucket/family** (e.g., switching `gemini-4-hydrogen-medium` → `gemini-4-hydrogen-low` does not bypass an exhausted `Gemini 4 Hydrogen` bucket; switch across families or ask via `ask_question`).
- **Telemetry verification**: confirm actual executed models via `"model"` on `PLANNER_RESPONSE` entries in `<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl`.
