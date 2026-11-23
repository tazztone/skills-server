## Plan Execution Delegation

Applies only to `/plan` artifact approvals (`Proceed` or `[Approved] plan.md`), except when native `planexecute` (`exit_plan_mode` / `[plan review]`) is active or the approval already names `inline`, a target model, or `swarm`:
- **Coordinator**: Do not edit files, pick default models, or spawn workers on your own; load `agy-executor` first.
- **Worker Execution**: Any spawned swarm worker executes its assigned brief directly without re-asking or spawning sub-workers.
