---
name: agentic-engineering
version: 1.2.0
description: >-
  Agentic engineering workflow: evidence-driven, production-grade, with risk
  tiers, context architecture, verification gates, and completion contracts
  for codebases of any scale. Use for product specifications, technical docs,
  architecture, implementation, tests, CI/CD quality gates, agent evaluations,
  memory files, code review, debugging, and remediation planning.
---

# Agentic Engineering

## Mission & Operational Modes

Build the factory that builds the software. Treat generated output as a hypothesis until it is verified. Optimize for user value, correctness, security, operability, and ease of change—not code volume, novelty, or a persuasive demo.

Use this skill whenever a task affects product behavior, an engineering artifact, a repository, an agent workflow, or a production decision.

**Conductor mode:** Real-time, synchronous pairing — exploratory debugging and prototyping with the developer in the loop. Keep context narrow; iterate on a single focus area.

**Orchestrator mode:** Asynchronous, high-level task delegation across multiple files and agents. Decompose into sub-tasks before proceeding.

## Operating Principles

1. **Specify before changing.** Establish the problem, users, constraints, non-goals, acceptance criteria, and evidence of success before implementation.
2. **Inspect before assuming.** Read the relevant local conventions, architecture, interfaces, tests, deployment paths, and prior decisions. Prioritize live filesystem search and Language Server Protocol (LSP) integrations over pre-indexed RAG to obtain real-time, exact symbol definitions and references.
3. **Make the smallest coherent change.** Prefer existing patterns and stable dependencies. Add abstraction, a service, a dependency, a workflow, or a framework only when it solves a demonstrated requirement that simpler code cannot.
4. **Use deterministic checks for deterministic claims.** Compilation, types, linting, schemas, unit/integration/contract tests, security scans, and deployment checks are gates—not suggestions.
5. **Evaluate judgment separately.** Use rubrics and, where appropriate, independent LM judges for ambiguity, relevance, completeness, policy compliance, UX quality, and agent trajectory.
6. **Preserve traceability.** Link requirement → design decision → implementation → verification → release evidence. Record important assumptions and decisions where future agents and humans can find them.
7. **Fail safely.** Bound permissions, protect secrets and personal data, make irreversible operations explicit, and provide rollback/recovery paths.
8. **Escalate meaningful uncertainty.** Ask one focused question or present bounded options when ambiguity materially changes scope, risk, or architecture. Otherwise state the assumption and proceed.
9. **Assume the 80% gap.** AI gets the first 80% right; the remaining 20% — edge cases, error handling, subtle correctness — is where judgment matters. Before completion, actively seek counterexamples, hidden coupling, security/privacy issues, operational failure modes, and unnecessary complexity.
10. **Stop when the acceptance criteria are met.** Do not refactor unrelated code, broaden scope, or build speculative flexibility.
11. **Route by cost.** In multi-agent environments, delegate deterministic sub-tasks (formatting, unit tests, linters) to smaller or cheaper models.

## Risk Levels

Classify work before acting. Apply the highest relevant level.

| Level | Examples | Minimum controls |
|---|---|---|
| Low | Docs, isolated formatting, internal prototype | Clear acceptance criteria; targeted validation; review changed output |
| Medium | Feature work, refactor, data transformation, public API change | Written plan; automated tests; compatibility/error-path checks; rollout note |
| High | Auth, payments, PII, security controls, migrations, production infrastructure | Design review; threat/failure analysis; least privilege; staging/canary; rollback; explicit human approval before release |
| Critical | Destructive production action, regulated/safety-critical domain | Do not execute autonomously; require named owner approval, runbook, audit record, and reversible or rehearsed procedure |

When risk is unclear, treat it as the next higher level.

## Context Management

Keep context lean, especially in large repositories:

- **Scope searches to the target module.** Prefer focused file reads and symbol lookups over repo-wide searches. When subagent tools are available, delegate broad exploration to read-only subagents to keep search logs out of the main context window; otherwise use scoped file queries.
- **Run build/test at module scope.** Execute build and test commands within the target directory to avoid flooding context with repo-wide output.
- **Read nested AGENTS.md files.** Check for subdirectory-level `AGENTS.md` with module-specific rules in addition to the root file. See [Artifact Standards](references/artifact-standards.md) for structure guidance.
- **Lean on hooks when available.** If the harness provides event-driven hooks (post-edit linting, pre-commit checks), rely on them rather than manually re-running checks.

## Workflow

Scale to the task. Apply only the steps warranted by the risk level:

| Risk | Minimum steps |
|---|---|
| Low | 1 → 4 → 5 |
| Medium | 1 → 2 → 3 → 4 → 5 → 7 |
| High / Critical | All steps, in order |

### 1. Frame the Task

Create or update a concise task record before implementation:

```md
# <Task title>

## Problem and outcome
- User/business problem:
- Desired observable outcome:
- In scope:
- Explicit non-goals:

## Constraints
- Compatibility, performance, security, privacy, reliability, cost, and timeline constraints:
- Existing conventions and interfaces to preserve:

## Acceptance criteria
- [ ] Given <context>, when <action>, then <observable result>
- [ ] Failure/edge case: <behavior>
- [ ] Verification: <test, command, metric, or review>

## Assumptions and open questions
- Assumption — rationale — impact if false

## Risk and rollout
- Risk level:
- Rollout, observability, rollback, and owner:
```

Requirements must be testable. Replace vague language such as "fast," "secure," "user-friendly," or "done" with measurable limits, scenarios, or explicit review criteria.

If requirements conflict, surface the conflict; do not silently choose one.

Identify the operational mode: **conductor** (synchronous, exploratory) or **orchestrator** (async, delegatable). Orchestrator tasks should be decomposed into sub-tasks at this stage.

> **Completion criterion:** Task record exists with testable acceptance criteria, explicit risk level, and no unresolved requirement conflicts. Operational mode identified.

### 2. Discover Context

Audit context across six categories:

| Category | What to collect |
|---|---|
| **Instructions** | Repository `AGENTS.md`, contribution rules, style/language conventions, system prompts |
| **Knowledge** | Architecture decision records, product decisions, incidents, runbooks, deployment config |
| **Memory** | Session logs, project state, existing skills/memory files |
| **Examples** | Reference implementations, existing patterns, call sites |
| **Tools** | API schemas, CLI definitions, CI workflows, feature flags |
| **Guardrails** | SLOs, permissions, data classification, security constraints, operational ownership |

Verify the repository has an `AGENTS.md` at root. If missing, create it or invoke the `create-agentsmd` skill before proceeding.

In large repositories, scope searches to the target module (see Context Management).

Summarize findings in a compact working brief. Distinguish **observed facts**, **inferences**, and **assumptions**. Load deep reference material only when it is relevant.

> **Completion criterion:** Working brief covers all six context categories, distinguishing observed facts from inferences and assumptions. Root `AGENTS.md` verified present.

### 3. Design Proportionately

For anything beyond a trivial, localized change, write a plan that includes:

- The chosen approach and why it fits existing architecture.
- Alternatives considered and why they were rejected.
- Components/interfaces/data-flow affected.
- Compatibility and migration strategy.
- Failure behavior, retries/timeouts/idempotency where applicable.
- Security, privacy, performance, reliability, observability, and cost implications.
- Test strategy, CI gates, rollout, rollback, and ownership.

Use a lightweight ADR when the decision is hard to reverse, crosses boundaries, changes a public contract, introduces a dependency, or creates significant operational cost.

**Architecture guardrails**

- Favor a simple, cohesive module over premature layers, plugins, event buses, microservices, or generic frameworks.
- Use established repository patterns unless they fail a stated requirement.
- Design interfaces around real callers and stable domain concepts, not possible future use cases.
- Keep boundaries explicit: ownership, inputs/outputs, error semantics, authentication/authorization, and data lifecycle.
- If a proposed abstraction has one use, no concrete second use, and adds indirection, do not add it.
- For distributed or async work, define delivery guarantees, deduplication/idempotency, ordering assumptions, timeouts, retry bounds, dead-letter behavior, and observability.
- Prefer open interoperability standards for tool and delegation interfaces over proprietary protocols.

> **Completion criterion:** Plan covers approach, alternatives, affected components, failure behavior, test strategy, and rollout. ADR filed if decision is hard to reverse.

### 4. Implement in Small, Verifiable Increments

1. Make the smallest vertical slice that proves the main behavior.
2. Add or update tests with the change; do not defer them to a final cleanup pass.
3. Run focused checks after each meaningful increment.
4. Inspect the diff for accidental scope, generated noise, secrets, dead code, and changed contracts.
5. Refactor only when it makes the completed change clearer, safer, or cheaper to maintain.

Follow these implementation rules:

- Validate inputs at boundaries; return actionable, safe errors.
- Preserve backward compatibility by default; version or migrate intentionally when breaking it.
- Use parameterized queries and safe encoding; never log secrets, credentials, tokens, or sensitive payloads.
- Set explicit timeouts, cancellation, resource limits, and bounded retries for external I/O.
- Make write operations idempotent when retries or duplicate delivery are possible.
- Add structured logs, metrics, traces, health signals, and alerts proportional to operational risk.
- Pin or verify dependencies according to repository policy; confirm packages, APIs, and commands exist before using them.
- Keep configuration typed/validated where the stack supports it; document defaults and safe failure modes.

> **Completion criterion:** Each increment passes its focused checks. Diff verified clean of accidental scope, secrets, dead code, and changed contracts.

### 5. Verify in Layers

Build an evidence matrix. A task is not complete merely because code compiles or an agent says it is correct.

| Claim | Preferred evidence | Gate |
|---|---|---|
| Behavior matches requirements | Acceptance, unit, integration, and end-to-end tests | Required |
| Edge cases and invariants hold | Boundary cases, property/fuzz tests, negative tests | Required when applicable |
| Interfaces remain compatible | Contract tests, schema checks, consumer tests, migration rehearsal | Required for public/shared contracts |
| Code is structurally sound | Format, lint, type/static analysis, build | Required |
| Change is secure | Secret scan, dependency/SCA scan, SAST, threat review, permission review | Risk-based; mandatory for high risk |
| System is operable | Load/performance checks, telemetry assertion, runbook/rollback rehearsal | Risk-based |
| Agent output is high quality | Rubric evaluation and calibrated independent LM judge | Required for agent-facing or subjective artifacts |
| Agent acted responsibly | Tool/trajectory policy checks, permission and audit checks | Required for autonomous actions |

Test behavior rather than implementation detail. Include happy paths, invalid input, empty/missing data, limits, permission failures, dependency failures, retries/timeouts, concurrency, and regression cases relevant to the change.

Do not claim a check passed unless it was actually run and its result observed. Report skipped checks, why they were skipped, and the residual risk.

> **Completion criterion:** Evidence matrix complete. No claim of passing without observed result. Skipped checks documented with residual risk.

### 6. Gate CI/CD

Express quality requirements as executable gates wherever possible. Suggested pipeline order:

1. Reproducible dependency install and build.
2. Formatting, linting, type/static analysis, and generated-file drift checks.
3. Unit and component tests with deterministic fixtures.
4. Integration/contract tests against ephemeral or controlled dependencies.
5. Security checks: secrets, dependency vulnerabilities/licenses, SAST, infrastructure/configuration scanning as applicable.
6. Agent evaluations: task success, rubric/LM-judge score, trajectory/policy checks, regression suite.
7. Package/artifact provenance, signing, SBOM, and deploy manifest checks where supported.
8. Staging verification, smoke tests, telemetry/health checks, and progressive delivery gates.
9. Production promotion only after required approvals and rollback readiness for the risk level.

CI must fail closed on mandatory gates. Make flaky checks visible and fix/quarantine them with an owner and expiry; never normalize rerunning CI until green.

> **Completion criterion:** All mandatory gates pass closed. Flaky checks quarantined with owner and expiry.

### 7. Review and Critique

Perform a structured review before presenting or merging:

```md
## Self-review
- Requirement coverage: Which acceptance criterion does each changed area satisfy?
- Correctness: What counterexample would break this?
- Architecture: Is there a simpler design consistent with the repository?
- Compatibility: Who/what could be a consumer that now breaks?
- Security/privacy: What data, authority, or trust boundary changed?
- Reliability: How does it fail, recover, retry, and alert?
- Operations: How will an on-call engineer detect, diagnose, and roll back it?
- Tests: Which failure mode is still untested, and why?
- Scope: What was intentionally left out?
```

For high-risk or cross-cutting changes, assign a separate critic pass that did not author the solution. The critic must try to falsify the design and return concrete findings with severity, evidence, and a recommended fix—not generic praise.

> **Completion criterion:** Every self-review question addressed. High-risk changes have an independent critic pass with concrete, severity-tagged findings.

### 8. Release and Learn

For releaseable work, provide:

- Change summary and affected users/systems.
- Exact verification evidence and any checks not run.
- Migration/rollout plan, feature flag or progressive exposure if appropriate.
- Dashboards, alerts, key health metrics, and expected baseline.
- Rollback procedure, data recovery steps, and owner.
- Known limitations, follow-up issues, and expiry dates for temporary measures.

After incidents, failed evaluations, regressions, or repeated agent mistakes: identify the failed assumption or missing control; add the smallest durable fix to the spec, test suite, policy, tool constraint, memory, or CI gate; then add a regression check.

> **Completion criterion:** Change summary, verification evidence, rollout plan, rollback procedure, and open items documented.

## Artifact Standards

Detailed standards for product specs, technical docs, memory files, agent evaluations, and architecture reviews are in [`references/artifact-standards.md`](references/artifact-standards.md).

## Self-Diagnosis Protocol

Structured diagnosis protocol for failed tests, builds, deployments, evaluations, or user outcomes is in [`references/self-diagnosis.md`](references/self-diagnosis.md).

## Completion Contract

Before declaring work complete, provide:

1. **What changed** — concise, user-relevant summary.
2. **Why this design** — key trade-offs and why simpler/more complex options were not selected.
3. **Evidence** — commands/tests/evaluations run and their observed results.
4. **Risk and operations** — compatibility, security, rollout/rollback, and monitoring implications.
5. **Open items** — skipped verification, assumptions, limitations, and explicitly scoped follow-ups.

A task is complete only when acceptance criteria have evidence, required gates pass, residual risk is explicit and accepted at the appropriate level, and the resulting artifact is maintainable by someone who did not create it.
