# Plan Executor (`plan-executor`)

Antigravity (`agy`) plugin that defers to native `Orchestrator` / `planexecute` when active, or offers 1-click `Inline` vs live-quota **Coordinator + Worker** `/swarm` presets (`Argon High`, `Neon High`, or `Current` -> `Hydrogen` / `3.8 Flash` / `Sonnet`) with `Custom Swarm` fallback and vanilla `/swarm` execution.

## Native `Orchestrator` vs. `plan-executor`

- **Native `Orchestrator` (`planexecute`) active** (`exit_plan_mode` tool or `[plan review]` handoff): `plan-executor` skips prompting so native single-stream `Planner -> Executor -> Reviewer` runs uninterrupted.
- **Standard session**: `plan-executor` calls `swarm{action:"models", all:true}` (`quota_remaining > 0%`, excluding `gemini-pro-orchestrator-*` to avoid nested `planexecute`), shows 1-click Q1 presets with live `%`, and hands Swarm execution off to vanilla `/swarm`.

## Components

- **Rule** (`rules/AGENTS.md`): Triggers on `/plan` artifact approvals (`Proceed` or `[Approved] plan.md`) unless native `planexecute` is active or the approval already specifies `inline`, a target model, or `swarm`. Keeps spawned workers executing directly without re-asking.
- **Skill** (`skills/agy-executor/SKILL.md`): Live quota check (`swarm{action:"models", all:true}`), 1-click Q1 `Inline` + Argon/Neon/Current presets, `Custom Swarm` fallback (`Hydrogen`, `3.8 Flash`, `Sonnet` `low` -> `high`), vanilla `/swarm` handoff, and Turn-2 Coordinator self-wakeup handling.

## Workflow

1. Coordinator presents `/plan` artifact (`plan.md`).
2. User approves (`Proceed` or `[Approved] plan.md`).
3. Coordinator calls `swarm{action:"models", all:true}` and asks **Q1** once: `(Recommended) Inline (current session)`, cross-pool presets (`Argon High -> Hydrogen Low/Med`, `Argon High -> 3.8 Flash Med`, `Argon High -> Sonnet Med`, `Neon High -> Hydrogen Low`, `Current -> Hydrogen Low/Med`), or `Custom Swarm`.
4. **If `Inline`**: Coordinator implements, verifies, and commits directly without calling `swarm`.
5. **If `Swarm`** (or `Custom Swarm` after Q2): Coordinator hands execution off to vanilla `/swarm` pinned to the chosen worker model with the plan path; if Coordinator model changed, calls `swarm{action:"model"}` after `add`, handles Turn-2 self-wakeup via `swarm_wait{since: <brief_seq>}` without re-briefing, and reviews final diffs before killing workers.
