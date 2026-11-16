# Plan Executor (`plan-executor`)

Antigravity plugin that delegates execution of approved plans to a Gemini 4 Hydrogen (Low) subagent, followed by parent verification and retrospective.

## Components

- **Rule** (`rules/AGENTS.md`): Instructs the coordinator/planning agent to delegate approved plans using the `agy-executor` skill rather than editing files inline.
- **Skills** (`skills/`):
  - `agy-executor` (symlinked from `../../skills/agy-executor`)
  - `agy-retrospective` (symlinked from `../../skills/agy-retrospective`)

## Workflow

1. User approves a plan.
2. Coordinator loads `agy-executor` and delegates execution to `gemini-4-hydrogen-low`.
3. Coordinator verifies the result and runs `agy-retrospective` if needed.
