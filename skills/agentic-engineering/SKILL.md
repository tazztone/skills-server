---
name: agentic-engineering
description: Evidence-driven engineering workflow with progressive quality gates and completion contracts.
disable-model-invocation: true
---

# Agentic Engineering

Evidence-driven engineering workflow. Treat generated output as a hypothesis until verified by deterministic checks and observable evidence.

Read the reference guides when needed:
- [`references/templates.md`](references/templates.md) — Task record, self-review, and release handoff templates.
- [`references/artifact-standards.md`](references/artifact-standards.md) — Standards for specs, technical docs, memory files, and evaluations.
- [`references/self-diagnosis.md`](references/self-diagnosis.md) — Structured diagnosis loop and finding format for test/build failures.

---

## Risk Levels & Step Selection

Classify work before acting. Apply the highest relevant risk level to select the required workflow steps:

| Level | Examples | Required Steps |
|---|---|---|
| **Low** | Docs, isolated formatting, internal prototypes | 1 → 4 → 5 |
| **Medium** | Feature work, refactoring, data transformations, API changes | 1 → 2 → 3 → 4 → 5 → 6 |
| **High** | Auth, payments, migrations, security controls, shared infra | All steps, in order + critic review |
| **Critical** | Destructive production operations, safety-critical domains | All steps + explicit human sign-off before execution |

When risk is unclear, treat it as the next higher level.

---

## Workflow Steps

### 1. Frame & Scope

Establish observable boundaries before modifying code:
- Define the user/system problem, observable desired outcome, in-scope items, and explicit non-goals.
- Specify testable acceptance criteria in Given/When/Then format. Replace subjective qualifiers ("fast", "secure", "clean") with measurable bounds.
- Record constraints, critical assumptions, and the determined risk level.
- For Medium, High, or Critical tasks, use the Task Record Template in [`references/templates.md`](references/templates.md).

> **Completion criterion:** Task boundaries and testable acceptance criteria recorded with an assigned risk level. No unresolved conflicting requirements remain.

### 2. Discover Context

Audit relevant project context before designing:
- **Local conventions:** Module-level patterns, coding styles, and repository `AGENTS.md` / `RULES.md`.
- **Interfaces & boundaries:** Upstream callers, downstream dependencies, data schemas, and domain invariants.
- **Existing tests:** Test fixtures, test suites, and expected coverage patterns.
- **Scope discipline:** Keep exploration focused on the target module. Run build and test commands within target directory scopes rather than repository-wide.

> **Completion criterion:** Working context established with observed conventions, affected interfaces, and existing tests identified.

### 3. Design Proportionately

Scale design investment to the risk level:
- Propose the smallest coherent design that solves the stated requirement using existing repository patterns.
- Inline single-use logic; extract abstractions only when multiple concrete callers or demonstrated requirements exist.
- Detail failure behavior, error semantics, timeouts, retries, and idempotency for external or asynchronous I/O.
- Record a lightweight Architectural Decision Record (ADR) whenever a choice is hard to reverse, alters a public contract, or adds an external dependency.

> **Completion criterion:** Design approach, failure paths, and test strategy documented. ADR recorded if the decision is hard to reverse.

### 4. Implement Incrementally

Execute the design in small, verifiable slices:
1. **Vertical slices:** Build the smallest functional increment that proves the core behavior first.
2. **Defend against the 80% gap:** Direct attention to the subtle 20%—boundary validation, error handling, retries, and contract invariants where generated code commonly fails.
3. **Co-located tests:** Write or update unit and integration tests alongside implementation increments rather than in a deferred cleanup pass.
4. **Clean diffs:** Inspect changes regularly for unintended scope creep, dead code, or modified public contracts. Keep modifications strictly contained to what the acceptance criteria require.

> **Completion criterion:** Each increment builds cleanly and passes its local unit/type checks with no unrelated files modified.

### 5. Verify in Layers

Collect observable evidence across multiple quality gates:

| Gate | Preferred Evidence | Applicability |
|---|---|---|
| **Syntax & Types** | Compiler output, type checker (`tsc`, `mypy`, etc.), static analysis | Mandatory |
| **Code Style** | Project linters and formatters | Mandatory |
| **Behavioral Tests** | Unit, integration, regression, and end-to-end test suites | Mandatory |
| **Boundary Invariants** | Edge cases, schema checks, contract tests, negative input handling | Medium / High risk |
| **Security & Safety** | Secret scans, dependency vulnerability checks, permission bounds | High / Critical risk |

Claim checks passed only when the execution command and output are directly observed in session. Report any skipped checks alongside their residual risk.

If any check fails, do not blindly retry code modifications. Follow the 7-step loop in [`references/self-diagnosis.md`](references/self-diagnosis.md) (isolate boundary → test competing hypotheses → fix root cause).

> **Completion criterion:** Deterministic checks executed with all observed results passing, or skipped checks documented with rationale and residual risk.

### 6. Review & Completion Contract

Conduct a final review against acceptance criteria before presenting work:
- Review changes using the Structured Self-Review Template in [`references/templates.md`](references/templates.md).
- **Falsification pass:** Actively attempt to break the solution with boundary inputs, missing dependencies, or invalid states before presenting. Mandatory for High and Critical tasks.
- Provide the final **Completion Contract**:
  1. **What changed:** Concise summary of changes.
  2. **Design rationale:** Why this approach was selected over alternatives.
  3. **Verification evidence:** Exact commands run and observed outputs.
  4. **Operational notes:** Rollout, rollback, and observability considerations.
  5. **Open items & limitations:** Explicit follow-ups, skipped checks, and remaining assumptions.

> **Completion criterion:** Self-review completed against acceptance criteria and final completion contract delivered with observed verification evidence.
