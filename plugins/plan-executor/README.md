# Plan Executor (`plan-executor`)

Antigravity plugin that prompts for **orchestrator** (`high`/`xhigh` or keep current) and **executor** (`low`/`medium` or `Inline`) models on `/plan` approval, switches the coordinator in-place if changed, runs inline or delegates implementation/tests/commits to `@executor`, and reviews the final diff.

## Components

- **Rule** (`rules/AGENTS.md`): Triggers on `/plan` artifact approvals (`Proceed` or `[Approved] plan.md`) to load `agy-executor` (skipping prompt only if user already named a target model or `inline`).
- **Skill** (`skills/agy-executor/SKILL.md`): Live model lookup (`swarm{action:"models"}`), two-question `ask_question` selection, coordinator `swarm{action:"model"}` switching, `@executor` delegation/bouncing, and final diff review.

## Workflow

1. Coordinator presents `/plan` artifact (`plan.md`).
2. User approves (`Proceed` or `[Approved] plan.md`).
3. Coordinator calls `swarm{action:"models"}` and one `ask_question` with Q1 (Orchestrator: keep current or `high`/`xhigh`) and Q2 (Executor: `low`/`medium` or `Inline`), then waits.
4. If `Inline`, coordinator implements, verifies, and commits directly (switching model if requested and supported).
5. If an executor model is chosen, coordinator spawns `@executor` via `swarm{action:"add"}`, switches coordinator via `swarm{action:"model"}` if changed, worker implements/verifies/commits, and coordinator reviews final diff and kills worker.
