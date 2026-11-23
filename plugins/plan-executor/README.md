# Plan Executor (`plan-executor`)

Antigravity (`agy`) plugin that defers to native `Orchestrator` / `planexecute` when active, or offers 1-click `Inline` vs live-quota **Coordinator + Worker** `/swarm` presets (`Argon High`, `Neon High`, or `Current` -> `Hydrogen` / `3.8 Flash` / `Sonnet`) with `Custom Swarm` fallback and vanilla `/swarm` execution.

## Native `Orchestrator` vs. `plan-executor`

- **Native `Orchestrator` (`planexecute`) active** (`exit_plan_mode` tool or `[plan review]` handoff): `plan-executor` skips prompting so native single-stream `Planner -> Executor -> Reviewer` runs uninterrupted.
- **Standard session**: `plan-executor` calls `swarm{action:"models", all:true}` (`quota_remaining > 0%`, excluding `gemini-pro-orchestrator-*`), shows 1-click Q1 presets with live `%`, and hands Swarm execution off to vanilla `/swarm`.
- **Why custom orchestration was stripped (`v2.2.0` -> `v2.4.0`)**: Vanilla `agy` already owns parallel topology, `workspace:"share"`, `fork`, `post_message` / `swarm_wait`, and `kill`. Keeping [SKILL.md](./skills/agy-executor/SKILL.md) focused solely on the mode/preset gate eliminates duplication and context bloat.

## Components

- **Rule** (`rules/AGENTS.md`): Triggers on `/plan` artifact approvals (`Proceed` or `[Approved] plan.md`) unless native `planexecute` is active or the approval already specifies `inline`, a target model, or `swarm`. Keeps spawned workers executing directly without re-asking.
- **Skill** (`skills/agy-executor/SKILL.md`): Live quota check (`swarm{action:"models", all:true}`), 1-click Q1 `Inline` + Argon/Neon/Current presets, `Custom Swarm` fallback (`Hydrogen`, `3.8 Flash`, `Sonnet` `low` -> `high`), vanilla `/swarm` handoff, and Turn-2 Coordinator self-wakeup handling.

## Workflow

1. Coordinator presents `/plan` artifact (`plan.md`).
2. User approves (`Proceed` or `[Approved] plan.md`).
3. Coordinator calls `swarm{action:"models", all:true}` and asks **Q1** once: `(Recommended) Inline (current session)`, cross-pool presets (`Argon High -> Hydrogen Low/Med`, `Argon High -> 3.8 Flash Med`, `Argon High -> Sonnet Med`, `Neon High -> Hydrogen Low`, `Current -> Hydrogen Low/Med`), or `Custom Swarm`.
4. **If `Inline`**: Coordinator implements, verifies, and commits directly without calling `swarm`.
5. **If `Swarm`** (or `Custom Swarm` after Q2): Coordinator hands execution off to vanilla `/swarm` pinned to the chosen worker model with the plan path; if Coordinator model changed, calls `swarm{action:"model"}` after `add`, handles Turn-2 self-wakeup via `swarm_wait{since: <brief_seq>}` without re-briefing, and reviews final diffs before killing workers.

---

## `agy` Routing, Quota & `/swarm` Reference (`agy` `1.5.14`)

Empirical notes from inspecting `agy` `1.5.14` and live `swarm{action:"models", all:true}` responses:

### Model Catalog & `Gemini 4 Hydrogen`

- **Dropdown vs. Tiered aliases**: `FetchAvailableModelsResponse` separates `models`, `agent_model_sorts` (interactive `/model` picker + `swarm`), and `tiered_model_ids` (`flash_lite`, `flash`, `pro` for `invoke_subagent` `Model` aliases). `-tiered-high` / `-tiered-xhigh` do not appear in the `swarm` dropdown, and no `-low-tiered` or `-medium-tiered` variants exist.
- **`Gemini 4 Hydrogen` limits & thinking levels**: `gemini-4-hydrogen-low` (`THINKING_LEVEL_LOW=1`, `M463`), `-medium` (`2`, `M462`), `-high` (`3`, `M461`), and `-xhigh` (`7`, `M464`) all share `MaxTokens = 1,048,576` and `MaxOutputTokens = 65,536`.

### Quota Pools & Cross-Pool Strategy

Models in the same pool share quota and reset windows; changing effort (`low` -> `xhigh`) within a pool draws from the same bucket:

| Pool | Models Observed | Reset Pattern |
|---|---|---|
| `GEMINI MODELS` (5h + Weekly) | `gemini-4-hydrogen-*`, `gemini-4-neon-*`, `gemini-3.8-flash-*`, `gemini-pro-orchestrator-neon` | Shared 5-hour sliding reset |
| `GEMINI 4 ARGON` (Weekly) | `gemini-4-argon-low/medium/high`, `gemini-pro-orchestrator-g1-pro` (planner leg) | Separate weekly sliding reset |
| Claude / 3P | `claude-opus-5-5-*`, `claude-sonnet-5-5-*`, `gpt-oss-120b-medium` (legacy `4.6` separate) | Separate multi-day reset |

- **Optimal cross-pool split**: Pair `gemini-4-argon-high` (Coordinator, weekly `GEMINI 4 ARGON` pool) with `gemini-4-hydrogen-low`/`medium`, `gemini-3.8-flash-medium`, or `claude-sonnet-5-5-medium` (Workers) so coordinator review does not drain the worker pool.

### Why `gemini-pro-orchestrator-*` Is Excluded From Swarm Presets

- `codeassistclient.synthesizeOrchestratorModels` wires `gemini-pro-orchestrator` (`M667`, `plan-execute-config`) to delegate internally to `gemini-flash-worker-agy` (`M669` -> `M432` Hydrogen).
- `planexecute.NewGateHook` locks those models into read-only `Plan mode` (`exit_plan_mode` / `enter_plan_mode`), refusing workspace edits until handoff and interrupting for review (`A plan review is due...`).
- Using `gemini-4-argon-high` or `gemini-4-neon-high` as Swarm Coordinator avoids `Plan mode` locks while keeping the same planning family. To use standalone `Orchestrator (Neon)` outside Swarm, run `agy --model gemini-pro-orchestrator-neon` or highlight `Orchestrator` in `/model` and cycle `Planner` with `←`/`→` or `Tab`.

### `nativeswarm` Behavior & Telemetry Verification

- `swarm{action:"models"}` without `all:true` returns only `suggested` models; always pass `all:true` to inspect all served models and live `quota_remaining`.
- `swarm{action:"model"}` rejects without an active swarm (`Inline` path must never call it), requires calling **after** `swarm{action:"add"}`, only switches `waiting` workers (revive `stopped` first; wait if `working`), and auto-wakes the Coordinator on Turn 2 (`selfModelSwitchNotice`: answer with `swarm_wait{since: <brief_seq>}`, do not re-brief).
- `tasks:[...]` creates `<name>-1..-<k>`; `swarm{action:"kill"}` takes individual worker names and permanently deletes `share`/`branch` workspaces, so merge commits before `kill`.
- **Empirical model verification**: Inspect `"model"` on `PLANNER_RESPONSE` entries in `~/.gemini/antigravity-cli/brain/<conversation-id>/.system_generated/logs/transcript.jsonl`.
