## Plan Execution Delegation

When the user approves a plan (e.g., `/plan` approval or `Proceed`), the planning/coordinator agent must not edit implementation files or run execution commands inline unless the user explicitly asks to execute inline. Load the `agy-executor` skill to delegate implementation to `gemini-4-hydrogen-low`, then review and verify the result. (An executor worker receiving a delegated plan brief executes it directly.)
