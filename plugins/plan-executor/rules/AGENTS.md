## Plan Execution Delegation

On `/plan` approval (`Proceed` or `[Approved] plan.md`), if not a swarm worker, native `planexecute` (`exit_plan_mode`/`[plan review]`), or explicit `inline`/model/`swarm`: do not edit or spawn directly; load `agy-executor` first.
