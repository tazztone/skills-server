---
name: agentic-engineering
description: Transition from casual vibe coding to disciplined agentic engineering.
disable-model-invocation: true
---

# Agentic Engineering

Use this skill to guide the transition from casual **vibe coding** (ad-hoc prompting without systematic checks) to **agentic engineering** (disciplined development using models within structured constraints, feedback loops, and verification gates).

## Step-by-Step Workflow

1. **Decompose & Design Intent**
   - Do not implement logic immediately. Stop and ask the user for or help them draft a formal specification and architecture document.
   - Break down large tasks into vertical, independently verifiable slices.
   - Identify the **80% Problem** boundaries: Explicitly question the user on edge cases, error handling, and integration points before writing code.
   - Write unit and integration test cases first (Red-Green-Refactor).
   - **Completion Criterion**: The project contains a clear written specification and at least one failing test representing the target behavior.

2. **Establish the Harness**
   - Verify the project has an `AGENTS.md` file at the root. If missing, invoke the `create-agentsmd` skill to generate it.
   - Check that sandboxed execution tools, compilers, and test suites are fully configured and accessible via tools.
   - Propose setup of tracing or logging if the project is deploying an autonomous agent.
   - **Completion Criterion**: The linter/test command executes successfully via run_command, showing failing test results.

3. **Prune and Optimize Context**
   - Audit current active context. Remove files or text segments that are not directly relevant to the target task.
   - Identify **Static Context** (always loaded rules like `AGENTS.md`) and keep it minimal. Push large references or APIs to **Dynamic Context** (loaded on-demand as external references or separate skills).
   - Suggest routing simpler sub-tasks (e.g. unit tests, format updates) to smaller, cheaper models if possible.
   - **Completion Criterion**: The active prompt contains only the files and high-signal instructions required for the immediate step.

4. **Run the Factory Flywheel**
   - Execute the development loop: Generate code -> Run tests/linter -> Read errors -> Correct code -> Repeat.
   - If output is non-deterministic (e.g. UI layout, natural language responses), write and run an evaluation script or checklist.
   - Block completion of the task if any tests or evaluation gates are failing.
   - **Completion Criterion**: The linter, test suite, and evaluation checks pass successfully on all generated code.

5. **Perform Code Review & QA**
   - Audit all edited lines for:
     - **Hallucinated dependencies**: Verify imports match actual packages.
     - **Swallowed errors**: Ensure try/catch blocks do not silence errors.
     - **Correctness gaps**: Check logic paths for edge cases.
   - Reject overly clever or complex code. Prioritize maintainability.
   - **Completion Criterion**: Code is fully reviewed, and a walkthrough of changes is generated.

---

## Reference: Key Concepts

- **Harness**: The scaffolding wrapped around a raw model (including rules, tools, sandboxes, hooks, and observability) that turns it into an agent.
- **Factory**: The system that builds the software (specs + agents + test gates + feedback loops).
- **Static Context**: Always-loaded files (e.g. system prompts, rule files). Keep this small to avoid token burn.
- **Dynamic Context**: Loaded on-demand (e.g. skill files, RAG results). Use this for large references.
- **Orchestrator Mode**: Operating at a high level by defining goals, managing agents, and checking outputs, as opposed to **Conductor Mode** (watching the model write code line-by-line).

---

## Source
- Based on the google paper: *The New SDLC With Vibe Coding: From ad-hoc prompting to Agentic Engineering*
