# Artifact Standards

Reference for the [agentic-engineering](../SKILL.md) skill — standards for product specs, technical docs, memory files, agent evaluations, and architecture reviews.

## Product Specifications

Write product specs that are executable by people and agents:

- Problem, target user, context, desired outcome, and non-goals.
- User journeys and acceptance scenarios in Given/When/Then form.
- Functional behavior, edge/failure cases, and explicit policy decisions.
- Non-functional requirements with thresholds: performance, availability, accessibility, privacy, security, localization, and cost where relevant.
- Analytics/telemetry, rollout, support/operations implications, dependencies, and decision owner.

Do not prescribe implementation unless it is a real constraint. Flag ambiguity instead of concealing it in prose.

## Technical Documentation

Keep docs close to the source of truth and update them with behavior changes. Explain purpose, prerequisites, interfaces, normal and failure behavior, examples, security/data handling, configuration, operational procedures, and how claims can be verified.

Prefer runnable examples and links to canonical schemas, code, or commands. Remove or correct stale docs in the same change when discovered.

## Memory Files

Memory is a curated, versioned operating manual—not a transcript.

Store stable, high-value facts: architecture boundaries, domain invariants, conventions, commands, deployment/recovery procedures, ownership, important decisions, and recurring failure patterns. Each entry should state scope, source/evidence, date, owner where relevant, and an expiry/review trigger when it may age.

Do not store secrets, personal data, lengthy logs, unverified claims, ephemeral task chatter, or duplicated documentation. When memory conflicts with code, tests, or a newer authoritative source, flag and resolve the conflict; do not perpetuate it.

**Layered AGENTS.md:** Keep root `AGENTS.md` minimal — architecture pointers and non-negotiable gotchas only. Place modular, additive `AGENTS.md` files inside subdirectories for module-specific rules, and execute build/test commands within the target directory scope rather than root.

## Agent Evaluations and LM Judges

Define an evaluation set before optimizing prompts or workflows:

- Representative normal cases, adversarial/edge cases, regressions, and out-of-distribution cases.
- A scoring rubric with observable anchors, weights, pass thresholds, and disqualifying failures.
- Deterministic assertions for facts, schemas, safety, tool permissions, and side effects.
- Independent judge prompts that quote the rubric, require evidence, separate "insufficient evidence" from failure, and return structured scores plus rationale.
- Calibration against human-reviewed examples; periodically measure judge agreement and investigate drift.

Use pairwise comparison or multiple independent judges for subjective outputs when the decision is important. Treat judge scores as signals, not ground truth; route borderline, high-impact, or safety-sensitive outcomes to human review.

## Architecture Reviews

Review architecture by asking:

- Does it satisfy the current requirement with fewer moving parts?
- Are ownership, boundaries, contracts, data classification, and trust boundaries explicit?
- What are the likely failure modes, blast radius, dependencies, and recovery paths?
- Are consistency, availability, latency, cost, and operability trade-offs documented?
- Can it be tested locally and observed in production?
- What decision would be hard or costly to reverse, and is it recorded?

Output a decision, rationale, alternatives, risks, required controls, and review date—not just observations.
