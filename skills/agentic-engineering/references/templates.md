# Templates

Reference templates for the [agentic-engineering](../SKILL.md) skill.

## 1. Task Record Template

Use during **Step 1 (Frame & Scope)** for Medium, High, or Critical risk tasks:

```md
# <Task Title>

## Problem & Desired Outcome
- Problem statement: <User or technical problem>
- Desired observable outcome: <Observable state change>
- In scope: <Explicit boundary of this change>
- Non-goals: <Explicitly excluded work>

## Constraints
- Existing conventions and interfaces to preserve:
- Security, performance, compatibility, or operational constraints:

## Acceptance Criteria
- [ ] Given <context>, when <action>, then <observable result>
- [ ] Edge / failure case: <behavior>
- [ ] Verification: <test, command, or observable check>

## Assumptions & Open Questions
- Assumption: <what is assumed> — Rationale: <why> — Risk if false: <impact>

## Risk & Rollout
- Risk level: Low | Medium | High | Critical
- Verification & Rollback path: <how to verify and revert if needed>
```

---

## 2. Structured Self-Review Template

Use during **Step 6 (Review & Completion Contract)** before presenting final work:

```md
## Self-Review
- Requirement coverage: Which acceptance criteria does each changed area satisfy?
- Correctness: What counterexample or boundary condition could break this?
- Architecture: Is there a simpler design consistent with existing repository patterns?
- Compatibility: What existing callers, configs, or contracts could break?
- Security & Data: What data, authority, or trust boundary changed?
- Operations & Failure: How does this fail, recover, log, and alert under stress?
- Unverified Areas: Which failure mode or edge case remains untested, and why?
- Scope Hygiene: Was any unrelated code refactored or modified?
```

---

## 3. Release & Handoff Summary Template

Use for releasable packages, cross-team handoffs, or PR descriptions:

```md
## Summary of Changes
- <High-level user-relevant summary of changes>

## Verification Evidence
- [x] Static checks: <linters, typecheckers, build output>
- [x] Automated tests: <unit, integration, or end-to-end tests run and results>
- [ ] Skipped checks / residual risk: <any check not run, rationale, and remaining risk>

## Operational & Rollout Notes
- Migration / rollout steps:
- Rollback procedure:
- Monitoring / key telemetry signals:
- Open follow-ups / limitations:
```
