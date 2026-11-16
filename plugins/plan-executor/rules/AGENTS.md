## Plan Execution Delegation

When presenting a plan artifact (`plan.md`) for approval, note both approval paths: click **Proceed** for low-cost swarm execution (`gemini-4-hydrogen-low`), or reply **"execute inline"** to implement directly on the current model without swarm.

When a plan is approved:
- **Delegated Mode (Default)**: When user clicks "Proceed", sends `[Approved] plan.md`, or says "use executor", coordinator must not edit implementation files or run execution commands inline. Load `agy-executor` skill to delegate implementation to `gemini-4-hydrogen-low` via swarm, then review and verify the result.
- **Direct Inline Mode**: When user explicitly requests inline execution (e.g., "execute inline", "implement directly", "no swarm", "approve inline", or "inline"), skip swarm delegation and implement all phases directly on the current model.
- **Worker Execution**: An executor worker receiving a delegated plan brief executes it directly.
