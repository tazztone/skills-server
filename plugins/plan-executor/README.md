# Plan Executor (`plan-executor`)

Antigravity (`agy`) plugin that defers to native `Orchestrator` (`planexecute`), or on `/plan` approvals offers 1-click `Inline` vs **Coordinator + Worker** `<swarm>` presets with lazy quota checks and `Custom Swarm` fallback.

## When to Use vs. Native `Orchestrator`

- **Skip `plan-executor` (use `/model -> Orchestrator`)** for single-stream `Planner -> Hydrogen` work: native `Orchestrator` already supports `Neon`/`Carbon`/`Argon`/`Opus 5.5` planners + `Hydrogen` executor + `Effort` sliders inside `/model` (`Tab`/`Shift+Tab`, `←`/`→`), keeps warm context, and costs `0` plugin tokens.
- **Use `plan-executor`** when you stay on a regular model day-to-day (no forced `Plan mode` lock on quick edits) and want:
  1. **Non-Hydrogen workers** (`Sonnet 5.5`, `3.8 Flash`) — `Orchestrator` locks `executors` to `gemini-4-hydrogen`.
  2. **Parallel isolated workers** (`workspace:"share"` / `"branch"`) and optional verifier workers.
  3. **Per-plan 1-click choice** (`Inline` vs `Neon`/`Argon`/`Current` Swarm) + mid-run quota switching (`swarm{action:"model"}`).

## The 3 "Plan" Mechanisms in `agy`

| Mechanism | Trigger | Scope / Behavior | `plan-executor` fires? |
|---|---|---|---|
| **`/plan`** | `/plan <task>` in chat | Creates `implementation_plan.md` + `Proceed` button | **Yes** (unless `Orchestrator`) |
| **`Shift+Tab` → `plan`** | Prompt `Shift+Tab` (`--mode plan`) | Sticky read-only permission mode (`default`/`accept-edits`/`auto`/`plan`); never switches models, no auto-artifact | **Yes** only if `/plan` artifact is approved |
| **`Orchestrator`** (`planexecute`) | `/model` → `Orchestrator` | Auto-switches `Planner` (`Plan mode is on`) ↔ `Executor` (`exit_plan_mode` / `[plan review]`) even in `auto` | **No** (defers cleanly) |

## Components & Workflow (`v2.5.0`)

- **[rules/AGENTS.md](./rules/AGENTS.md)** (`32` words): Gates `/plan` approvals (`Proceed` or `[Approved] plan.md`) unless inside a swarm worker, native `planexecute`, or explicit `inline`/model/`swarm`.
- **[skills/agy-executor/SKILL.md](./skills/agy-executor/SKILL.md)**:
  1. Calls `ask_question` once with short labels (no pre-call to `swarm{action:"models"}`): `(Recommended) Inline`, `Neon Med -> H2 Low/Med`, `Neon High/XHigh -> H2 Med`, `Neon Med -> Sonnet Med`, `Argon High -> H2 Low`, `Current -> H2 Low/Med`, or `Custom Swarm`.
  2. **`Inline`**: Works directly (never calls `swarm`).
  3. **`Swarm`**: Calls `swarm{action:"add", model:"<worker>"}` directly with the plan path (never `gemini-pro-orchestrator*` for Coordinator or Worker). Calls `swarm{action:"models", all:true}` lazily only for `Custom Swarm` or quota rejections. If Coordinator != active model, calls `swarm{action:"model"}` **after** `add` and answers Turn-2 self-wakeup with `swarm_wait{since:<brief_seq>}`.

---

## `agy` Routing, Quota & `<swarm>` Reference (`agy` `1.5.14`)

| Pool | Observed Models (`swarm{action:"models", all:true}`) | Reset |
|---|---|---|
| `GEMINI MODELS` | `gemini-4-hydrogen-*`, `gemini-4-neon-*`, `gemini-4-carbon-*`, `gemini-3.8-flash-*`, `gemini-pro-orchestrator` (`Carbon`), `gemini-pro-orchestrator-neon` | Shared 5h + Weekly |
| `GEMINI 4 ARGON` | `gemini-4-argon-low/medium/high`, `gemini-pro-orchestrator-argon` (planner leg) | Separate Weekly |
| Claude / 3P | `claude-opus-5-5-*`, `claude-sonnet-5-5-*`, `gpt-oss-120b-medium` | Separate multi-day |

- **Catalog notes**: `gemini-4-hydrogen-low/medium/high/xhigh` (`M463`/`M462`/`M461`/`M464`) share `1,048,576` context / `65,536` output; `-tiered-*` aliases are `invoke_subagent`-only (`flash_lite`/`flash`/`pro`), not in `swarm`.
- **Why `gemini-pro-orchestrator*` is excluded in Swarm**: `planexecute.NewGateHook` locks bare `gemini-pro-orchestrator` (`Carbon`), `-argon`, and `-neon` into read-only `Plan mode` (`exit_plan_mode` / `[plan review]`), conflicting with Swarm edits.
- **`nativeswarm` quirks**: Always pass `all:true` to `models`; `model` requires an active swarm (after `add`) and only switches `waiting` workers; `kill` permanently deletes `share`/`branch` workspaces (merge first).
- **Verify actual model used**: Check `"model"` on `PLANNER_RESPONSE` entries in `~/.gemini/antigravity-cli/brain/<conversation-id>/.system_generated/logs/transcript.jsonl`.
