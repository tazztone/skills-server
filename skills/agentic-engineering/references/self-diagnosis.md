# Self-Diagnosis Protocol

Reference for the [agentic-engineering](../SKILL.md) skill — structured diagnosis when a test, build, deployment, evaluation, or user outcome fails.

Do not repeatedly retry blindly.

1. **Capture evidence:** exact failure, inputs, environment, logs/traces, revision, and reproducibility.
2. **Classify:** requirement gap, context/memory gap, design flaw, implementation defect, test/evaluation defect, environment/configuration issue, dependency issue, or operational regression.
3. **Minimize:** isolate a smallest reproducer and identify the first failing boundary.
4. **Form competing hypotheses:** state predicted evidence for each; test the cheapest discriminating hypothesis first.
5. **Fix cause, not symptom:** choose the narrowest durable correction; update spec/design only if the understanding changed.
6. **Verify broadly enough:** run the focused regression plus affected adjacent checks.
7. **Learn:** add a regression test/eval, guardrail, memory entry, or CI rule if it prevents recurrence.

## Structured Finding Format

When critiquing an architecture or proposing a fix, use this format:

```md
Finding: <specific issue>
Severity: blocker | high | medium | low
Evidence: <observed code, test, trace, requirement, or metric>
Impact: <user/business/operational consequence>
Root cause or uncertainty: <why this occurs, or what is unknown>
Options: <smallest safe fix>; <alternative and trade-off>
Recommendation: <chosen option and why>
Verification: <tests, gates, rollout signals>
```

Never present speculation as diagnosis. If evidence is insufficient, say what must be observed next.
