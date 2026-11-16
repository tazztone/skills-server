# Plan Executor (`plan-executor`)

Antigravity plugin that delegates execution of approved plans to a Gemini 4 Hydrogen (Low) subagent, followed by parent verification and retrospective, or executes inline when explicitly requested.

## Components

- **Rule** (`rules/AGENTS.md`): Defines dual approval modes:
  - **Delegated Mode (Default)**: Triggered on "Proceed", `[Approved] plan.md`, or "use executor". Delegates implementation to `gemini-4-hydrogen-low` via `agy-executor`.
  - **Direct Inline Mode**: Triggered on "execute inline", "implement directly", or "no swarm". Executes directly on the current model without swarm delegation.
- **Skills** (`skills/`):
  - `agy-executor`: Multi-phase delegation, review bouncing, and commit workflow.
  - `agy-retrospective`: Session audit, `walkthrough.md`, and `SUGGESTIONS.md` maintenance.

## Workflow

1. User or coordinator creates plan (`plan.md`).
2. Coordinator presents plan with dual approval options (Proceed vs execute inline).
3. If approved via Proceed, coordinator delegates to `@executor` on `gemini-4-hydrogen-low`.
4. If approved inline, coordinator implements directly.
5. Coordinator verifies result, commits phases, and runs `agy-retrospective`.
