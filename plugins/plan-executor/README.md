# Plan Executor (`plan-executor`)

Antigravity (`agy`) plugin that adds model-split execution and parallel `/swarm` fan-out on `/plan` approvals in non-Orchestrator sessions while cleanly deferring to native `Orchestrator` / `planexecute` when active.

## Native `Orchestrator` vs. `plan-executor`

- **Native `Orchestrator` (`planexecute`) active** (`exit_plan_mode` tool or `[plan review]` handoff): `plan-executor` skips prompting so native single-stream `Planner -> Executor -> Reviewer` model switching runs uninterrupted in one warm conversation.
- **Standard session (or multi-workstream plan)**: `plan-executor` queries `swarm{action:"models", all:true}`, asks once via `ask_question` for orchestrator (`high`/`xhigh`) and execution mode/model (`Inline`, single `@executor`, or parallel `workspace:"share"` `/swarm` on `low`/`medium`), and manages review/landing on the coordinator.

## Components

- **Rule** (`rules/AGENTS.md`): Triggers on `/plan` artifact approvals (`Proceed` or `[Approved] plan.md`) unless native `planexecute` is active or the approval already specifies `inline`, a target model, or `swarm`. Keeps spawned workers (`@executor`, `@exec-*`, `@verifier`) executing directly without re-asking.
- **Skill** (`skills/agy-executor/SKILL.md`): Full-catalog lookup (`swarm{action:"models", all:true}`), adaptive 2-vs-3 question `ask_question`, bounded `fork:"coordinator"` vs. fresh parallel `workspace:"share"` fan-out, Turn-2 self-wakeup handling after `swarm{action:"model"}`, merge-before-`kill` landing, and cross-family quota switching.

## Workflow

1. Coordinator presents `/plan` artifact (`plan.md`).
2. User approves (`Proceed` or `[Approved] plan.md`).
3. Coordinator calls `swarm{action:"models", all:true}` and one `ask_question` (2 questions for single-stream plans; 3 questions for disjoint multi-workstream plans), then waits.
4. **If `Inline`**: Coordinator implements, verifies, and commits directly without calling `swarm`.
5. **If Single `@executor`**: Coordinator spawns `@executor` (`workspace:"inherit"`, using `fork:"coordinator"` only when target files were read directly and `0` broad search dumps occurred), switches coordinator via `swarm{action:"model"}` if Q1 changed (handling Turn-2 auto-wakeup via `swarm_wait`), reviews final diff, and kills worker.
6. **If Parallel `/swarm`**: Coordinator spawns disjoint fresh workers (`workspace:"share"`), merges worker commits back and runs cross-slice verification before killing each worker individually (`exec-1..exec-N`).
