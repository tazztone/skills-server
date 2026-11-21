# Plan Executor (`plan-executor`)

Antigravity plugin that prompts for a target execution model on `/plan` approval, then either runs inline or delegates implementation, verification, and commits to a `@executor` swarm worker followed by coordinator diff review.

## Components

- **Rule** (`rules/AGENTS.md`): Triggers on `/plan` artifact approvals (`Proceed` or `[Approved] plan.md`) to load `agy-executor` (skipping prompt only if user already named a model or `inline`).
- **Skill** (`skills/agy-executor/SKILL.md`): Live model lookup (`swarm{action:"models"}`), `ask_question` selection, `@executor` delegation/bouncing, and final diff review.

## Workflow

1. Coordinator presents `/plan` artifact (`plan.md`).
2. User approves (`Proceed` or `[Approved] plan.md`).
3. Coordinator calls `swarm{action:"models"}` and `ask_question` with live models + `Inline (current model)`, then waits for user choice.
4. If `Inline`, coordinator implements, verifies, and commits directly.
5. If a model is chosen, coordinator dispatches `@executor` via `swarm{action:"add"}`, worker implements/verifies/commits, and coordinator reviews final diff and kills worker.
