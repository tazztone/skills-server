## Plan Execution Delegation

Applies only to `/plan` artifact approvals (`Proceed` or `[Approved] plan.md`):
- **Coordinator**: Do not edit implementation files, pick a default model, or spawn workers on your own. Load `agy-executor` to query available models, ask the user which model to use (or `Inline`) via `ask_question`, and execute accordingly. (Skip asking only if the approval message already names a target model or `inline`.)
- **Worker Execution**: An `@executor` worker receiving a delegated plan brief executes it directly without re-asking or delegating.
