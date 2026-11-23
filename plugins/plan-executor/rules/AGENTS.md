## Plan Execution Delegation

Applies only to `/plan` artifact approvals (`Proceed` or `[Approved] plan.md`), except when native `planexecute` (`exit_plan_mode` / `[plan review]`) is active or the approval already names `inline`, a target model, or `swarm`:
- **Coordinator**: Do not edit implementation files, pick default models, or spawn workers on your own. Load `agy-executor` to query live models (`swarm{action:"models", all:true}`), ask for orchestrator and execution mode/model via `ask_question`, and execute accordingly.
- **Worker Execution**: Any spawned swarm worker (`@executor`, `@exec-*`, `@verifier`) executes its assigned brief directly without re-asking or spawning sub-workers.
