# Plan Executor (`plan-executor`)

Antigravity (`agy`) plugin that gates `/plan` approvals in non-Orchestrator sessions on `Inline` vs `Swarm`, lets vanilla `/swarm` execute on a chosen worker model while keeping the current model as Coordinator, and reviews final diffs.

## Native `Orchestrator` vs. `plan-executor`

- **Native `Orchestrator` (`planexecute`) active** (`exit_plan_mode` tool or `[plan review]` handoff): `plan-executor` skips prompting so native single-stream `Planner -> Executor -> Reviewer` runs uninterrupted.
- **Standard session**: `plan-executor` asks `Inline` vs `Swarm` first (zero model queries on `Inline`), and if `Swarm` is chosen, asks **Worker Model** (`Hydrogen`, `3.8 Flash`, `Sonnet`, `low` -> `high`) and hands execution off to vanilla `/swarm`.

## Components

- **Rule** (`rules/AGENTS.md`): Triggers on `/plan` artifact approvals (`Proceed` or `[Approved] plan.md`) unless native `planexecute` is active or the approval already specifies `inline`, a target model, or `swarm`. Keeps spawned workers executing directly without re-asking.
- **Skill** (`skills/agy-executor/SKILL.md`): Two-step `Inline` vs `Swarm` gate, `swarm{action:"models", all:true}` worker-model lookup (`Hydrogen`, `3.8 Flash`, `Sonnet`, `low` -> `high`), vanilla `/swarm` handoff keeping Coordinator model unchanged, and Coordinator diff review.

## Workflow

1. Coordinator presents `/plan` artifact (`plan.md`).
2. User approves (`Proceed` or `[Approved] plan.md`).
3. Coordinator asks **Q1**: `(Recommended) Inline (current session)` vs `Swarm`.
4. **If `Inline`**: Coordinator implements, verifies, and commits directly without calling `swarm`.
5. **If `Swarm`**: Coordinator calls `swarm{action:"models", all:true}`, asks **Q2** for Worker Model (`Hydrogen`, `3.8 Flash`, `Sonnet`, `low` -> `high`), keeps current session model as Coordinator, hands execution off to vanilla `/swarm` with the plan path, and reviews final diffs/commits before killing workers.
