---
name: create-agentsmd
description: Generate a minimal, high-signal AGENTS.md file at the repository root.
disable-model-invocation: true
---

# Create a High-Signal AGENTS.md (Static Context)

Use this skill to create a minimal, non-redundant `AGENTS.md` at the root of the repository (or subproject roots in monorepos). `AGENTS.md` acts as **Static Context** (always loaded by the agent), so keeping it extremely concise is critical to avoid high token burn and context noise.

## Implementation Steps

1. **Audit Project Configuration**
   - Read the project layout, configurations, package files (`package.json`, `Cargo.toml`, etc.), `README.md`, scripts, and CI workflows.
   - **Completion Criterion**: Compile a list of the tech stack, default commands, and existing documentation.

2. **Extract Candidate Instructions & Guardrails**
   - Identify candidate instructions for agents (e.g., custom test commands, seed databases, PR title schemas) and **Guardrails** (rules specifying what the agent must *never* do).
   - Apply the **Three-Condition Filter** to each candidate.
   - **Completion Criterion**: Eliminate any candidates that do not meet all three filter conditions.

3. **Verify Candidate Commands**
   - Execute every command surviving the filter inside the workspace to confirm they run without errors.
   - **Completion Criterion**: Every command compiles, runs, or executes successfully in the terminal.

4. **Write AGENTS.md**
   - Write the filtered instructions into `/AGENTS.md` using the template format.
   - **Completion Criterion**: The file exists at the root, contains only commands or strict rules with no prose rationale, and has fewer than 10 bullet points.

---

## Reference: The Three-Condition Filter

Only include an instruction in `AGENTS.md` if **all three** conditions are true:
1. **Uninferable**: An agent cannot infer it by reading the codebase or standard tooling defaults.
2. **Critical**: Getting it wrong causes a build, test, runtime, or security failure (or is a strict guardrail).
3. **Undocumented**: It is not already written in an existing file (e.g., `README.md`, `package.json` scripts, `Makefile`, or CI config).

### Push to Dynamic Context
If a workflow, instruction, or set of commands is complex, verbose, or procedural, do NOT add it to `AGENTS.md`. Instead, recommend pushing it to **Dynamic Context** (e.g., as a custom agent skill or external script in the `.agents/skills` folder) to keep the static context footprint low.

### Exclude List (No-Ops)
Do **not** include:
- Standard package manager commands (e.g., `npm install`, `go test`, `pytest`).
- Rationale or explanations of *why* steps are needed.
- Generic coding guidelines (e.g., "write clean code" or "write unit tests").
- High-level architecture overviews already in the `README.md`.

---

## Reference: Structure Template

```markdown
## [Category, e.g., Testing / Database Setup]

- [Brief instruction/command]
- [Brief instruction/command]
```
