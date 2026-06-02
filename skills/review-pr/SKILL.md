---
name: review-pr
description: >
  Structured multi-reviewer code review for a single PR before merge.
  Spawns reviewer perspectives (correctness, testing, maintainability, and conditional reviewers),
  scores findings by severity, and routes to fix/report/walk-through.
  Use when user says "review PR #N", "deep review", or wants code-quality gating before merge.
disable-model-invocation: true
---

# Review PR

Structured code review for a single PR. Produces a findings report grouped by severity,
then routes to one of: apply safe fixes / walk through per finding / report only.

---

## Reviewer Perspectives

### Always-On
| Reviewer | Focus |
|----------|-------|
| correctness | Logic errors, edge cases, state bugs, off-by-ones |
| testing | Coverage gaps, weak assertions, brittle or flaky tests |
| maintainability | Complexity, coupling, dead code, abstraction debt |

### Conditional (select by diff content)
Activate only when the diff touches the relevant area:
- **security** — auth flows, public endpoints, user input handling, permissions
- **performance** — DB queries, caching, async patterns, data transforms, hot paths
- **api-contract** — routes, serializers, type signatures, versioning, breaking changes
- **reliability** — error handling, retries, timeouts, background jobs, circuit breakers

These are starting perspectives, not rigid roles. Adapt to the repo's domain —
check `AGENTS.md` for project-specific review concerns.

---

## Severity Scale

| Level | Meaning | Action |
|-------|---------|--------|
| P0 | Critical breakage, exploitable vuln, data loss | Must fix before merge |
| P1 | High-impact defect, breaking contract | Should fix |
| P2 | Moderate issue, edge case, perf regression | Fix if straightforward |
| P3 | Low-impact minor improvement | Discretionary |

Confidence-gate: only report findings with confidence ≥ 75%.
Below that threshold, note uncertainty but don't block.

---

## Review Flow

### Step 1: Understand Intent
Read PR title, body, and commit messages. Identify the **purpose** of the change
before evaluating correctness — a refactor has different review criteria than a hotfix.

### Step 2: Scope the Diff
```bash
gh pr diff <n>
```
Use `git diff -U10 $BASE` for more context when hunks are ambiguous.
Identify which conditional reviewers to activate based on files touched.

### Step 3: Run Reviewer Perspectives
For each active reviewer, evaluate the diff through that lens.
Produce findings as: `{file, line range, severity, reviewer, description, suggested fix}`.

### Step 4: Deduplicate and Merge
Multiple reviewers may flag the same issue. Merge overlapping findings,
keep the highest severity, combine descriptions.

### Step 5: Produce Findings Report
Group by severity (P0 → P3). For each finding:
- File and line range
- Severity and reviewer that flagged it
- Description of the issue
- Suggested fix (if straightforward)

### Step 6: Route
Present options to the user:
1. **Apply safe fixes** — auto-fix P2/P3 issues where the fix is unambiguous
2. **Walk through** — discuss each finding interactively
3. **Report only** — deliver the report, user decides

### Step 7: If Fixes Applied
Re-review only the changed scope (max 2 rounds to avoid infinite loops).
Commit, push, and update the PR.

---

## Gotchas

### Don't block on style nitpicks
P3 findings should never block a merge. Note them; move on.

### Verify bot/AI PRs more aggressively
For automated PRs, grep unfamiliar identifiers in the codebase.
Check that imports resolve and APIs exist. See `manage-prs` skill for details.

### Previous review threads
If the PR has existing unresolved review threads, read them first.
Don't duplicate feedback that's already been given. See `resolve-pr-feedback` skill
for handling existing threads.
